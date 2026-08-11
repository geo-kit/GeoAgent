"""Configuration.

Everything comes from environment variables; there is no config file and no model
presets. GeoView sets these variables on the agent process when it launches it,
and .env covers standalone runs.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "openai:gpt-5-mini"

SUPPORTED_PROVIDERS = ("openai", "lmstudio", "ollama")


def qualified_model() -> str:
    "The configured provider:model string."
    return os.environ.get("GEOAGENT_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def load_chat_model():
    """Build the chat model from GEOAGENT_MODEL.

    LM Studio speaks the OpenAI protocol, so it reuses ChatOpenAI with its own base
    URL. An unsupported provider fails here with a readable message.
    """
    spec = qualified_model()
    provider, _, model = spec.partition(":")
    provider = provider.strip().lower()
    model = model.strip()

    if not model:
        raise ValueError(
            f"GEOAGENT_MODEL must look like 'provider:model' (got {spec!r}). "
            f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}."
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            base_url=os.environ.get("OPENAI_BASE_URL") or None,
            api_key=os.environ.get("OPENAI_API_KEY"),
            temperature=0,
        )

    if provider == "lmstudio":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.environ.get("LMSTUDIO_MODEL") or model,
            base_url=os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
            api_key=os.environ.get("LMSTUDIO_API_KEY", "lm-studio"),
            temperature=0,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model,
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            temperature=0,
        )

    raise ValueError(
        f"Unsupported model provider {provider!r} in GEOAGENT_MODEL={spec!r}. "
        f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}."
    )


def result_dir() -> Path | None:
    "Directory GeoView watches for artifacts, or None when running detached."
    raw = os.environ.get("GEOVIEW_RESULT_DIR", "").strip()
    return Path(raw) if raw else None


def model_roots() -> list[Path]:
    """Directories the agent may browse and load models from.

    An empty list means no restriction: loading a deck is exactly what the user could
    type into GeoView's own path field. Set GEOAGENT_MODEL_ROOTS to narrow it down.
    """
    raw = os.environ.get("GEOAGENT_MODEL_ROOTS", "").strip()
    if not raw:
        return []
    return [Path(part).resolve() for part in raw.split(os.pathsep) if part.strip()]
