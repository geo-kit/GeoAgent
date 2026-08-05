### 🌐 Multi-Language Support

**English** | [Русский](./translations/ru/README.md)

# GeoAgent

GeoAgent is the chat panel inside [GeoView](https://github.com/geo-kit/GeoView). Ask it
which model is open, point it at a deck somewhere on disk, or tell it to run the
simulation and watch the 3D view fill in.

GeoView does the computing. The agent presses its buttons for you, which is why
installing it pulls seven Python packages and no Julia.

## What it can do

| Tool | What happens |
|---|---|
| `find_reservoir_models` | Lists sub-directories and `.DATA` / `.hdf5` files in one directory. Reads no file contents. |
| `load_model_in_geoview` | Opens a model in GeoView. |
| `run_simulation_in_geoview` | Runs GeoView's JutulDarcy simulation of the model already open. Takes no arguments, so it cannot reach for a deck other than the one on screen. |
| `prepare_optimization_in_geoview` | Fills in GeoView's BHP optimization form and opens the tab. You press Optimize. |

Asking what is loaded costs no tool call. GeoView pastes the current state at the top of
every message you send: file path, grid size, active cells, phases, well names, dates,
and whether a simulation has run yet.

The optimization tool takes twelve economic and engineering values and will not run with
any of them missing. Guess an oil price and you get an NPV that reads as authoritative
and means nothing, so the agent asks you for the numbers.

## Limits

The agent cannot open a shell, execute code, or change a file on your disk. It reads
directory listings, not the contents of a deck. Everything it writes lands in one place,
GeoView's artifact directory, as JSON.

Out of the box it can open any model file you could have typed into GeoView's own path
field. Set `GEOAGENT_MODEL_ROOTS` to keep it inside directories you choose.

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

GeoView starts the agent for you and points its chat at it:

```bash
python -m geoview.app --server --port 8080 --agent --agent-provider openai --agent-model gpt-5-mini
```

To work on the agent itself, run it against LangGraph Studio:

```bash
langgraph dev --host 127.0.0.1 --port 2024 --no-browser
```

Point `GEOVIEW_RESULT_DIR` at GeoView's `.agent_runtime` directory first. Without it the
tools have nowhere to deliver a request, and they will tell you so.

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

GeoView and the agent are separate processes, so they pass work through a shared
directory rather than an API. The agent writes a manifest, then publishes a pointer to
it:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json   # what to do, and with what
<GEOVIEW_RESULT_DIR>/results/latest.json            # {"run_id": ...}, written last
```

GeoView checks that pointer once a second and routes the manifest by its `type` field.
Writing the pointer last keeps GeoView from picking up a half-finished request. To add a
capability, add a `type` on both sides; the transport stays as it is.

## Tests

```bash
pytest
ruff check . && ruff format --check .
```

## GeoAgentPro

GeoAgent operates the application. GeoAgentPro does the engineering: it writes JutulDarcy
code in Julia, runs it, reads the errors and fixes them, and searches the JutulDarcy
documentation on the way. It runs simulations in its own process instead of asking
GeoView for them, and you can drive it from a terminal or as an MCP server. Sold
separately.
