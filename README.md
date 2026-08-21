### 🌐 Multi-Language Support

**English** | [Русский](./translations/ru/README.md)

# GeoAgent

GeoAgent is the AI assistant built into [GeoView](https://github.com/geo-kit/GeoView) to streamline your workflows.

## What it can do

| Tool | What happens |
|---|---|
| `find_reservoir_models` | Lists sub-directories and `.DATA` / `.hdf5` files in one directory. Reads no file contents. |
| `load_model_in_geoview` | Opens a model in GeoView |
| `run_simulation_in_geoview` | Runs simulation using JutulDarcy simulator |
| `prepare_optimization_in_geoview` | Requests and fills in NPV optimization parameters and opens the Optimization tab |

## Privacy

The agent cannot open a shell, execute code, or change a file on your disk. It reads
directory listings, not the contents of a deck. Everything it writes lands in one place,
GeoView's artifact directory, as JSON.

## Getting started

GeoView launches and stops the agent for you, so the install steps live with it:
**[Enabling the chat](https://github.com/geo-kit/GeoView#enabling-the-chat-geoagent)**.

Clone it next to GeoView; that is where GeoView looks by default:

```
your-workspace/
├── GeoView/
└── GeoAgent/
```

Anywhere else works too, as long as `GEOVIEW_AGENT_DIR` points at it.

## Configuration

| Variable | Purpose |
|---|---|
| `GEOAGENT_MODEL` | `provider:model`. Providers: `openai`, `lmstudio`, `ollama`. GeoView sets this from its own flags. |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI or any OpenAI-compatible endpoint. |
| `LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, `LMSTUDIO_MODEL` | LM Studio's local server. |
| `OLLAMA_BASE_URL` | Ollama. |
| `GEOVIEW_RESULT_DIR` | Where to deliver requests. Set by GeoView. |
| `GEOAGENT_MODEL_ROOTS` | Optional allow-list of directories, `os.pathsep` separated. |

See `.env.example` for an example of configuration.

## How it communicates with GeoView

GeoView and the agent are separate processes and pass work through a shared
directory rather than an API. The agent writes a manifest, then publishes a pointer to
it:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json   # what to do, and with what
<GEOVIEW_RESULT_DIR>/results/latest.json            # {"run_id": ...}, written last
```

GeoView checks that pointer once a second and routes the manifest by its `type` field.
Writing the pointer last keeps GeoView from picking up a half-finished request.

For this agent the `type` is always a request — `load_model`, `run_simulation`, or
`optimization_setup`. It never writes results back, because it computes nothing itself.

To add a capability, add a `type` on both sides.

## Development

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/). From this directory:

```bash
uv venv && uv pip install -e . --group dev
pytest
ruff check . && ruff format --check .
```

To work on the agent itself, run it under LangGraph Studio instead of letting GeoView start it.
This is the one case where `GEOVIEW_RESULT_DIR` is yours to set: GeoView normally sets it on the
agent process, and nothing does here, so the publishing tools refuse to act without it:

```bash
export GEOVIEW_RESULT_DIR=/path/to/GeoView/.agent_runtime
langgraph dev --host 127.0.0.1 --port 2024 --no-browser --no-reload --allow-blocking
```

`--allow-blocking` is not optional — the tools make synchronous calls and the dev server aborts
runs without it. `graph.py` is loaded by path from `langgraph.json`, so it must use absolute
imports (`from GeoAgent.configuration import ...`).

## Need more features?

GeoAgent serves as a baseline AI agent for basic workflows.
For advanced capabilities — such as automated code generation and execution based on user prompts — please contact us to request access.
