from __future__ import annotations

from collections import defaultdict
from datetime import timezone
from operator import itemgetter
from typing import Sequence

import humanize
from InquirerPy import inquirer
from rich.console import Console
from rich.theme import Theme

console = Console(theme=Theme({"header": "bold cyan", "dim": "dim"}))


def _naturaltime(dt) -> str:
    return humanize.naturaltime(dt.astimezone(timezone.utc))


def pick_profile(profiles: Sequence[str], default: str | None) -> str:
    console.print("[header]AWS profile[/header]")
    return inquirer.select(
        message="Choose profile:",
        choices=list(profiles),
        default=default,
    ).execute()


def pick_instance(instances: list[dict]) -> dict:
    """Interactive instance selector grouped by state."""
    grouped = defaultdict(list)
    for inst in instances:
        grouped[inst["state"]].append(inst)

    order = ["running", "stopped", "pending", "terminated"]
    choices = []
    for state in order:
        group = sorted(
            grouped.get(state, []),
            key=itemgetter("launch_time"),
            reverse=True,
        )
        if not group:
            continue
        choices.append({"name": f"--- {state.upper()} ---", "disabled": ""})
        for inst in group:
            label = _label(inst)
            choices.append({"name": label, "value": inst})

    return inquirer.select(message="Choose instance:", choices=choices).execute()


def _label(inst: dict) -> str:
    ago = _naturaltime(inst["launch_time"])
    name = inst["name"]
    if name == inst["id"]:
        name = f"[dim]{name}[/dim]"
    return f"{name} – {ago} ({inst['id']})"
