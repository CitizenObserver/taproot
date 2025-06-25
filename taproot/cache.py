"""Very small MRU cache for last-used profile / instance."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from appdirs import user_cache_dir

_CACHE_FILE = Path(user_cache_dir("taproot")) / "history.json"


def load() -> dict[str, Any]:
    try:
        return json.loads(_CACHE_FILE.read_text())
    except FileNotFoundError:
        return {}


def save(profile: str, instance_id: str) -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_FILE.write_text(
        json.dumps({"profile": profile, "instance_id": instance_id})
    )
