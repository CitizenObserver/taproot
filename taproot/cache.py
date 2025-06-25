"""MRU cache for last-used profile/instance."""
from __future__ import annotations,unicode_literals
import json,appdirs
from pathlib import Path
d=_CACHE_FILE=Path(appdirs.user_cache_dir("taproot"))/"history.json"

def load():
    try:return json.loads(d.read_text())
    except FileNotFoundError:return {}

def save(p,i):
    d.parent.mkdir(parents=True,exist_ok=True)
    d.write_text(json.dumps({"profile":p,"instance_id":i}))
