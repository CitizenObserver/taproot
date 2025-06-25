"""Cache last-used profile/instance."""
import json
from pathlib import Path
from appdirs import user_cache_dir

_cache = Path(user_cache_dir("taproot")) / "history.json"

def load():
    try:
        return json.loads(_cache.read_text())
    except FileNotFoundError:
        return {}

def save(profile: str, iid: str):
    _cache.parent.mkdir(parents=True, exist_ok=True)
    _cache.write_text(json.dumps({"profile": profile, "instance_id": iid}))
