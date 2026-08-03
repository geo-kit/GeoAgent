"""Writing artifacts for GeoView.

GeoView and the agent run as separate processes, so they talk through a directory
instead of an API. The agent writes:

    <result_dir>/results/<run_id>/result.json   # manifest for this action
    <result_dir>/results/latest.json            # {"run_id": <run_id>} pointer

GeoView polls ``latest.json`` and, when it changes, reads the manifest and routes it
by its ``type`` field. The pointer is written *last* so a watcher never reads a
half-written run.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from . import configuration


class ArtifactError(RuntimeError):
    "Raised when an artifact cannot be published."


def _new_run_id() -> str:
    return datetime.now().strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:6]


def publish(kind: str, message: str, **payload) -> str:
    """Write a manifest of type ``kind`` and publish it to GeoView.

    Returns the run id. Raises ArtifactError when no result directory is
    configured, so the tool can tell the user instead of writing into the void.
    """
    root = configuration.result_dir()
    if root is None:
        raise ArtifactError(
            "GeoView result directory is not configured (GEOVIEW_RESULT_DIR is unset), "
            "so this action cannot reach GeoView. Start the agent from GeoView with "
            "--agent, or set GEOVIEW_RESULT_DIR when running it standalone."
        )

    results_root = root / "results"
    run_id = _new_run_id()
    run_dir = results_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "status": "ok",
        "error": None,
        "type": kind,
        "message": message,
        "ts": datetime.now().isoformat(timespec="seconds"),
        **payload,
    }
    (run_dir / "result.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Publish the pointer last.
    (results_root / "latest.json").write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    return run_id


def manifest_path(root: Path, run_id: str) -> Path:
    "Path of a published manifest; used by the tests."
    return root / "results" / run_id / "result.json"
