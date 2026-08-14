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

## Installation

Requires Python 3.13, [uv](https://docs.astral.sh/uv/), and [GeoView](https://github.com/geo-kit/GeoView).
Clone the GeoAgent repository next to the GeoView:

```
your-workspace/
├── GeoView/
└── GeoAgent/
```

Then install the dependencies:

```bash
uv venv && uv pip install -e . --group dev
```

Then copy `.env.example` to `.env` and fill in the API key for the provider you use.

## Run

Run GeoView wuth `--agent` flag (flags `--agent-provider` and `--agent-model` are optional):

```bash
python -m geoview.app --agent --agent-provider openai --agent-model gpt-5-mini
```

To run the agent itself, use LangGraph Studio:

```bash
langgraph dev --host 127.0.0.1 --port 2024 --no-browser
```

Point `GEOVIEW_RESULT_DIR` at GeoView's `.agent_runtime` directory first. Without it the
tools have nowhere to deliver a request, and they will tell you so.

## Configuration

| Variable | Purpose |
|---|---|
| `GEOAGENT_MODEL` | `provider:model`. Providers: `openai`, `lmstudio`, `ollama`. GeoView sets this from its own flags. |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI or any OpenAI-compatible endpoint. |
| `LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, `LMSTUDIO_MODEL` | LM Studio's local server. |
| `OLLAMA_BASE_URL` | Ollama. |
| `GEOVIEW_RESULT_DIR` | Where to deliver requests. Set by GeoView. |
| `GEOAGENT_MODEL_ROOTS` | Optional allow-list of directories, `os.pathsep` separated. |

See `.env.example` for an example of confirugation.

## How it communicates with GeoView

GeoView and the agent are separate processes and pass work through a shared
directory rather than an API. The agent writes a manifest, then publishes a pointer to
it:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json   # what to do, and with what
<GEOVIEW_RESULT_DIR>/results/latest.json            # {"run_id": ...}, written last
```

GeoView checks that pointer once a second and routes the manifest by its `type` field.
Writing the pointer last keeps GeoView from picking up a half-finished request. To add a
capability, add a `type` on both sides; the transport stays as it is.

## Need more features?

GeoAgent serves as a baseline AI agent for basic workflows. 
For advanced capabilities — such as automated code generation and execution based on user prompts — please contact us to request access.
