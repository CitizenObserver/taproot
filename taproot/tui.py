from __future__ import annotations
from datetime import timezone
from typing import Sequence, List, Dict, Any
import humanize
from InquirerPy import inquirer
from rich.console import Console
from rich.theme import Theme

console = Console(theme=Theme({"header": "bold cyan", "dim": "dim"}))

# sentinel for profile swap
class _ProfileChange: ...
PROFILE_CHANGE = _ProfileChange()

COLS = {"name": 25, "age": 16, "state": 10}

def _naturaltime(dt): 
    return humanize.naturaltime(dt.astimezone(timezone.utc))

def _row(inst: Dict[str, Any]) -> str:
    name = inst["name"] if inst["name"] != inst["id"] else f"[dim]{inst['name']}[/dim]"
    age  = _naturaltime(inst["launch_time"])
    state= inst["state"]
    return f"{name:<{COLS['name']}} {age:<{COLS['age']}} {state:<{COLS['state']}} {inst['id']}"

def pick_profile(profiles: Sequence[str], default: str | None) -> str:
    console.clear()
    console.print("[header]AWS profile selector (↑↓ to move, ⏎ to select)[/header]")
    return inquirer.select(message="Choose profile:", choices=list(profiles), default=default).execute()

def pick_instance(instances: List[Dict[str, Any]], profile: str):
    console.clear()
    console.print(f"Profile: [bold]{profile}[/bold]   (Tab=change profile)\n")
    choices=[{"name":_row(inst),"value":inst} for inst in instances]
    prompt=inquirer.select(message="Choose instance:", choices=choices, vi_mode=False)
    @prompt.kb.add("tab")
    def _(_ev): 
        prompt.status["answered"]=True
        prompt.status["result"]=PROFILE_CHANGE
        prompt._session.app.exit(result=PROFILE_CHANGE)
    return prompt.execute()
