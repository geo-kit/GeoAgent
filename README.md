# GeoAgent

The assistant built into [GeoView](https://github.com/geo-kit/GeoView), the reservoir
model viewer. It answers questions about the model you have open and operates the app
in plain language: finding a deck, opening it, running a simulation, filling in an
optimization run.

GeoAgent computes nothing itself. It drives GeoView, which does the work and shows the
result in its own tabs. That keeps it small: seven dependencies, no Julia, no solver.

## What it can do

| Tool | What happens |
|---|---|
| `find_reservoir_models` | Lists sub-directories and `.DATA` / `.hdf5` files in one directory. Never reads file contents. |
| `load_model_in_geoview` | Opens a model in GeoView. |
| `run_simulation_in_geoview` | Runs GeoView's JutulDarcy simulation of the model already open. Takes no arguments, so it cannot target a different deck than the one on screen. |
| `prepare_optimization_in_geoview` | Fills in GeoView's BHP optimization form and opens the tab. Does not start the run; you press Optimize. |

Questions about the loaded model need no tool at all. GeoView puts a summary of what is
on screen (path, grid, active cells, phases, wells, dates, whether results exist) at the
top of every message.

The optimization tool requires all twelve economic and engineering inputs. That is
deliberate: the agent cannot call it without them, so instead of inventing an oil price
and producing a confident but meaningless NPV, it asks.

## What it deliberately cannot do

No shell commands. No code execution. No editing or deleting files. No reading file
contents. No network calls beyond the model provider. The only thing it writes is a JSON
request in GeoView's own artifact directory.

Set `GEOAGENT_MODEL_ROOTS` to restrict which directories it may browse and open models
from. Unset, it can open any readable model file, the same reach as the path field in
GeoView's own interface.

## Install

Python 3.12+ and [uv](https://docs.astral.sh/uv/). Check out next to GeoView:

```
your-workspace/
├── GeoView/
└── GeoAgent/
```

```bash
uv venv && uv pip install -e . --group dev
```

Then copy `.env.example` to `.env` and fill in the API key for the provider you use.

## Run

Normally you do not start it yourself. GeoView does, and points its chat at it:

```bash
python -m geoview.app --server --port 8080 --agent --agent-provider openai --agent-model gpt-5-mini
```

Standalone, for development against LangGraph Studio:

```bash
langgraph dev --host 127.0.0.1 --port 2024 --no-browser
```

Set `GEOVIEW_RESULT_DIR` to GeoView's `.agent_runtime` directory first, otherwise the
tools have nowhere to deliver their requests and will say so.

## Configuration

Everything is an environment variable; see `.env.example`.

| Variable | Purpose |
|---|---|
| `GEOAGENT_MODEL` | `provider:model`. Providers: `openai`, `lmstudio`, `ollama`. GeoView sets this from its own flags. |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI or any OpenAI-compatible endpoint. |
| `LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, `LMSTUDIO_MODEL` | LM Studio's local server. |
| `OLLAMA_BASE_URL` | Ollama. |
| `GEOVIEW_RESULT_DIR` | Where to deliver requests. Set by GeoView. |
| `GEOAGENT_MODEL_ROOTS` | Optional allow-list of directories, `os.pathsep` separated. |

## How it talks to GeoView

The two run as separate processes, so they share a directory instead of an API. The
agent writes a manifest and then publishes a pointer to it:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json   # what to do, and with what
<GEOVIEW_RESULT_DIR>/results/latest.json            # {"run_id": ...}, written last
```

GeoView polls the pointer once a second and dispatches on the manifest's `type`. The
pointer is written last so a watcher never reads a half-written request. Adding a
capability means a new `type` on both sides; the transport does not change.

## Tests

```bash
pytest
ruff check . && ruff format --check .
```

## GeoAgentPro

GeoAgent operates the application. GeoAgentPro reasons about reservoir engineering: it
writes, runs, lints and repairs JutulDarcy Julia code, retrieves from the JutulDarcy
documentation, runs its own simulations and multi-step autonomous workflows, and works
from a CLI or as an MCP server as well as inside GeoView. It is available separately.
