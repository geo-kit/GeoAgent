"""Tests for the tools and the artifact contract.

No network and no model calls: everything here is filesystem-level.
"""

from __future__ import annotations

import json

import pytest

from GeoAgent.tools import (
    find_reservoir_models,
    load_model_in_geoview,
    prepare_optimization_in_geoview,
    run_simulation_in_geoview,
)

VALID_OPTIMIZATION = {
    "oil_price": 400.0,
    "gas_price": 0.1,
    "water_price": 5.0,
    "water_cost": 3.0,
    "gas_cost": 0.05,
    "discount_rate": 10.0,
    "months": 24,
    "max_iterations": 25,
    "bhp_prod_min": 80.0,
    "bhp_prod_max": 250.0,
    "bhp_inj_min": 200.0,
    "bhp_inj_max": 400.0,
}


@pytest.fixture
def result_dir(tmp_path, monkeypatch):
    "Point the agent at a throwaway GeoView result directory."
    target = tmp_path / "runtime"
    monkeypatch.setenv("GEOVIEW_RESULT_DIR", str(target))
    monkeypatch.delenv("GEOAGENT_MODEL_ROOTS", raising=False)
    return target


@pytest.fixture
def deck(tmp_path):
    "A file that looks like a reservoir model."
    path = tmp_path / "models" / "SPE1.DATA"
    path.parent.mkdir(parents=True)
    path.write_text("RUNSPEC\n", encoding="utf-8")
    return path


def published(result_dir):
    "The manifest the pointer currently points at."
    pointer = json.loads((result_dir / "results" / "latest.json").read_text())
    manifest = result_dir / "results" / pointer["run_id"] / "result.json"
    return json.loads(manifest.read_text(encoding="utf-8"))


# ── artifact contract ────────────────────────────────────────────────────────


def test_pointer_is_written_after_the_manifest(result_dir, deck):
    "A watcher must never see a pointer to a half-written run."
    load_model_in_geoview.invoke({"data_file": str(deck)})

    pointer = result_dir / "results" / "latest.json"
    run_id = json.loads(pointer.read_text())["run_id"]
    manifest = result_dir / "results" / run_id / "result.json"
    assert pointer.stat().st_mtime_ns >= manifest.stat().st_mtime_ns


def test_manifest_carries_the_fields_geoview_reads(result_dir, deck):
    load_model_in_geoview.invoke({"data_file": str(deck)})

    manifest = published(result_dir)
    assert manifest["status"] == "ok"
    assert manifest["type"] == "load_model"
    assert manifest["data_file"] == str(deck)
    assert manifest["run_id"] and manifest["message"] and manifest["ts"]


def test_tools_explain_themselves_when_geoview_is_absent(monkeypatch, deck):
    monkeypatch.delenv("GEOVIEW_RESULT_DIR", raising=False)

    answer = load_model_in_geoview.invoke({"data_file": str(deck)})
    assert "GEOVIEW_RESULT_DIR" in answer


# ── load_model_in_geoview ────────────────────────────────────────────────────


def test_load_rejects_a_non_model_file(result_dir, tmp_path):
    note = tmp_path / "notes.txt"
    note.write_text("not a deck", encoding="utf-8")

    answer = load_model_in_geoview.invoke({"data_file": str(note)})
    assert "not a reservoir model" in answer
    assert not (result_dir / "results").exists()


def test_load_rejects_a_missing_file(result_dir, tmp_path):
    answer = load_model_in_geoview.invoke({"data_file": str(tmp_path / "ghost.DATA")})
    assert "not found" in answer.lower()
    assert not (result_dir / "results").exists()


def test_load_respects_the_allow_list(result_dir, deck, tmp_path, monkeypatch):
    monkeypatch.setenv("GEOAGENT_MODEL_ROOTS", str(tmp_path / "elsewhere"))

    answer = load_model_in_geoview.invoke({"data_file": str(deck)})
    assert "outside the directories" in answer
    assert not (result_dir / "results").exists()


# ── find_reservoir_models ────────────────────────────────────────────────────


def test_find_lists_models_and_folders_only(deck, tmp_path):
    (deck.parent / "readme.txt").write_text("ignore me", encoding="utf-8")
    (deck.parent / "cases").mkdir()

    answer = find_reservoir_models.invoke({"directory": str(deck.parent)})
    assert "SPE1.DATA" in answer
    assert "cases" in answer
    assert "readme.txt" not in answer


def test_find_reports_a_missing_directory(tmp_path):
    answer = find_reservoir_models.invoke({"directory": str(tmp_path / "nowhere")})
    assert "not found" in answer.lower()


# ── run_simulation_in_geoview ────────────────────────────────────────────────


def test_simulation_request_is_published(result_dir):
    run_simulation_in_geoview.invoke({})
    assert published(result_dir)["type"] == "run_simulation"


# ── prepare_optimization_in_geoview ──────────────────────────────────────────


def test_optimization_publishes_every_form_field(result_dir):
    prepare_optimization_in_geoview.invoke(dict(VALID_OPTIMIZATION))

    manifest = published(result_dir)
    assert manifest["type"] == "optimization_setup"
    assert manifest["params"] == VALID_OPTIMIZATION


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("bhp_prod_min", 300.0, "bhp_prod_min must be lower than bhp_prod_max"),
        ("bhp_inj_max", 100.0, "bhp_inj_min must be lower than bhp_inj_max"),
        ("discount_rate", 0.0, "discount_rate must be greater than 0"),
        ("months", 0, "months must be a whole number greater than 0"),
    ],
)
def test_optimization_refuses_inconsistent_values(result_dir, field, value, expected):
    params = dict(VALID_OPTIMIZATION)
    params[field] = value

    answer = prepare_optimization_in_geoview.invoke(params)
    assert expected in answer
    assert not (result_dir / "results").exists()
