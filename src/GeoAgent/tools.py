"""Tools available to the agent.

All four are either read-only on the filesystem or write a request into GeoView's
artifact directory. Nothing here executes code, spawns a process, reads file
contents or writes outside that directory.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from . import configuration
from .artifacts import ArtifactError, publish

MODEL_SUFFIXES = (".data", ".hdf5")
MAX_LISTED_ENTRIES = 50


def _outside_allowed_roots(path: Path) -> str:
    "Error message if an allow-list is configured and path falls outside it, else ''."
    roots = configuration.model_roots()
    if not roots:
        return ""
    resolved = path.resolve()
    for root in roots:
        if resolved == root or root in resolved.parents:
            return ""
    listed = ", ".join(str(root) for root in roots)
    return f"'{path}' is outside the directories this agent may use ({listed})."


class FindReservoirModelsInput(BaseModel):
    directory: str = Field(
        description="Absolute path of the directory to inspect, e.g. 'D:/models'."
    )


@tool(
    "find_reservoir_models",
    description=(
        "List the sub-directories and reservoir model files (.DATA, .hdf5) directly "
        "inside a directory. Use it to locate a model when the user names one without "
        "giving a full path, and to explore one level at a time. Never reads file "
        "contents."
    ),
    args_schema=FindReservoirModelsInput,
)
def find_reservoir_models(directory: str) -> str:
    "List reservoir models and sub-directories in one directory."
    path = Path(directory).expanduser()
    if not path.exists():
        return f"Directory not found: {path}"
    if not path.is_dir():
        return f"Not a directory: {path}"
    denied = _outside_allowed_roots(path)
    if denied:
        return denied

    try:
        entries = sorted(path.iterdir(), key=lambda p: p.name.lower())
    except OSError as err:
        return f"Cannot read {path}: {err}"

    folders = [f"[DIR]  {entry}" for entry in entries if entry.is_dir()]
    models = [
        f"[FILE] {entry}"
        for entry in entries
        if entry.is_file() and entry.suffix.lower() in MODEL_SUFFIXES
    ]
    if not folders and not models:
        return f"No reservoir models or sub-directories in {path}."

    lines = models + folders
    truncated = len(lines) > MAX_LISTED_ENTRIES
    listing = "\n".join(lines[:MAX_LISTED_ENTRIES])
    if truncated:
        listing += f"\n... {len(lines) - MAX_LISTED_ENTRIES} more entries not shown."
    return f"Contents of {path}:\n{listing}"


class LoadModelInput(BaseModel):
    data_file: str = Field(
        description="Absolute path of the reservoir model to open, ending in .DATA or .hdf5."
    )


@tool(
    "load_model_in_geoview",
    description=(
        "Open a reservoir model in GeoView. GeoView loads the file and its 3D view "
        "switches to it. Use this when the user asks to open or load a model. Confirm "
        "which file is meant when several could match."
    ),
    args_schema=LoadModelInput,
)
def load_model_in_geoview(data_file: str) -> str:
    "Ask GeoView to open a reservoir model."
    path = Path(data_file).expanduser()
    if path.suffix.lower() not in MODEL_SUFFIXES:
        return (
            f"'{path.name}' is not a reservoir model. GeoView opens "
            f"{' or '.join(MODEL_SUFFIXES)} files."
        )
    if not path.exists():
        return f"File not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"
    denied = _outside_allowed_roots(path)
    if denied:
        return denied

    try:
        publish("load_model", f"Opening {path.name} in GeoView.", data_file=str(path))
    except ArtifactError as err:
        return str(err)
    return (
        f"Asked GeoView to open {path}. Loading a large model takes a few seconds. "
        "GeoView reports the outcome in the chat itself, so do not call this tool again "
        "for the same file."
    )


class NoArguments(BaseModel):
    "Schema for tools that act on whatever GeoView currently has open."


@tool(
    "run_simulation_in_geoview",
    description=(
        "Run a JutulDarcy simulation of the model currently open in GeoView and show "
        "the result in its 3D view. Always operates on the loaded model, so there is "
        "nothing to choose. Requires a model to be loaded first. The first run of a "
        "session can take several minutes while Julia compiles."
    ),
    args_schema=NoArguments,
)
def run_simulation_in_geoview() -> str:
    "Ask GeoView to simulate the loaded model."
    try:
        publish("run_simulation", "Starting a simulation of the loaded model.")
    except ArtifactError as err:
        return str(err)
    return (
        "Simulation requested. GeoView runs it and reports progress and the result in "
        "the chat, so do not start another one while it is running."
    )


class PrepareOptimizationInput(BaseModel):
    """Inputs for GeoView's BHP optimization form.

    Every field is required. These are economic and engineering values that only the
    user can supply; guessing them produces a meaningless NPV. Ask for what is missing.
    """

    oil_price: float = Field(description="Oil price, $/m3.")
    gas_price: float = Field(description="Gas price, $/m3.")
    water_price: float = Field(description="Water production cost, $/m3.")
    water_cost: float = Field(description="Water injection cost, $/m3.")
    gas_cost: float = Field(description="Gas injection cost, $/m3.")
    discount_rate: float = Field(description="Discount rate, percent per year, above 0.")
    months: int = Field(description="Forecast horizon in months, a whole number above 0.")
    max_iterations: int = Field(
        description=(
            "Maximum optimizer iterations, a whole number above 0. GeoView's own default is 25."
        )
    )
    bhp_prod_min: float = Field(
        description="Lower bottom-hole pressure bound for producers, bar, above 0."
    )
    bhp_prod_max: float = Field(
        description="Upper bottom-hole pressure bound for producers, bar, above bhp_prod_min."
    )
    bhp_inj_min: float = Field(
        description="Lower bottom-hole pressure bound for injectors, bar, above 0."
    )
    bhp_inj_max: float = Field(
        description="Upper bottom-hole pressure bound for injectors, bar, above bhp_inj_min."
    )


def _validate_optimization(params: dict) -> str:
    "Mirror of GeoView's own form validation; returns an error message or ''."
    problems = []
    for name in ("discount_rate", "bhp_prod_min", "bhp_prod_max", "bhp_inj_min", "bhp_inj_max"):
        if params[name] <= 0:
            problems.append(f"{name} must be greater than 0 (got {params[name]}).")
    for name in ("months", "max_iterations"):
        value = params[name]
        if value != int(value) or value <= 0:
            problems.append(f"{name} must be a whole number greater than 0 (got {value}).")
    if params["bhp_prod_min"] >= params["bhp_prod_max"]:
        problems.append("bhp_prod_min must be lower than bhp_prod_max.")
    if params["bhp_inj_min"] >= params["bhp_inj_max"]:
        problems.append("bhp_inj_min must be lower than bhp_inj_max.")
    return " ".join(problems)


@tool(
    "prepare_optimization_in_geoview",
    description=(
        "Fill in GeoView's BHP optimization form for the loaded model and open the "
        "Optimization tab, so the user can review the values and press Optimize "
        "themselves. This tool does not start the optimization. Call it only once the "
        "user has given every value. Never invent prices, costs, horizons or pressure "
        "bounds; ask for the ones you are missing."
    ),
    args_schema=PrepareOptimizationInput,
)
def prepare_optimization_in_geoview(
    oil_price: float,
    gas_price: float,
    water_price: float,
    water_cost: float,
    gas_cost: float,
    discount_rate: float,
    months: int,
    max_iterations: int,
    bhp_prod_min: float,
    bhp_prod_max: float,
    bhp_inj_min: float,
    bhp_inj_max: float,
) -> str:
    "Fill GeoView's optimization form without starting the run."
    params = {
        "oil_price": oil_price,
        "gas_price": gas_price,
        "water_price": water_price,
        "water_cost": water_cost,
        "gas_cost": gas_cost,
        "discount_rate": discount_rate,
        "months": months,
        "max_iterations": max_iterations,
        "bhp_prod_min": bhp_prod_min,
        "bhp_prod_max": bhp_prod_max,
        "bhp_inj_min": bhp_inj_min,
        "bhp_inj_max": bhp_inj_max,
    }

    problem = _validate_optimization(params)
    if problem:
        return f"The form was not filled in: {problem} Ask the user for corrected values."

    params["months"] = int(params["months"])
    params["max_iterations"] = int(params["max_iterations"])

    try:
        publish(
            "optimization_setup",
            "Optimization form filled in; waiting for the user to start it.",
            params=params,
        )
    except ArtifactError as err:
        return str(err)
    return (
        "GeoView's Optimization tab is now open with these values filled in. Tell the "
        "user to check them and press Optimize when ready; the run is theirs to start."
    )


TOOLS = [
    find_reservoir_models,
    load_model_in_geoview,
    run_simulation_in_geoview,
    prepare_optimization_in_geoview,
]
