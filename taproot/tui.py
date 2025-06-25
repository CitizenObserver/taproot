from __future__ import annotations

from datetime import timezone
from typing import Sequence, List, Dict, Any

import humanize
from prompt_toolkit.key_binding import KeyBindings
from InquirerPy import inquirer
from rich.console import Console
from rich.theme import Theme

console = Console(theme=Theme({"header": "bold cyan", "dim": "dim"}))


class _ProfileChange:
    """Sentinel used when the user wants to switch profile."""


PROFILE_CHANGE = _ProfileChange()

COLS = {"name": 25, "age": 16, "state": 10}


def _naturaltime(dt) -> str:
    return humanize.naturaltime(dt.astimezone(timezone.utc))


def _row(inst: Dict[str, Any]) -> str:
    name = inst["name"] if inst["name"] != inst["id"] else f"[dim]{inst['name']}[/dim]"
    age = _naturaltime(inst["launch_time"])
    state = inst["state"]
    return f"{name:<{COLS['name']}} {age:<{COLS['age']}} {state:<{COLS['state']}} {inst['id']}"


def pick_profile(profiles: Sequence[str], default: str | None) -> str:
    console.clear()
    console.print("[header]AWS profile selector (↑↓ move, ⏎ select)[/header]")
    return inquirer.select(
        message="Choose profile:",
        choices=list(profiles),
        default=default,
    ).execute()


def pick_instance(instances, profile):
    console.clear()
    console.print(f"Profile: [bold]{profile}[/bold]   (Tab = change profile)\n")

    choices = [{"name": _row(i), "value": i} for i in instances]

    # ─── Tab key ⇢ switch profile ──────────────────────────────────────────────
    def _exit_tab(event):
        event.app.exit(result=PROFILE_CHANGE)

    kb_map = {
        "toggle": [{"key": "tab", "func": _exit_tab}],
    }

    return inquirer.select(
        message="Choose instance:",
        choices=choices,
        keybindings=kb_map,  # <- pass the mapping, not KeyBindings()
        vi_mode=False,
    ).execute()
