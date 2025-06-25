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


def naturaltime(dt):
    return humanize.naturaltime(dt.astimezone(timezone.utc))


def pick_profile(profiles: Sequence[str], default: str | None):
    console.print("[header]AWS profile[/header]")
    return inquirer.select(
        message="Choose profile:",
        choices=list(profiles),
        default=default,
    ).execute()


def pick_instance(instances: list[dict]):
    """
    Show a grouped & sortable instance list.

    *   Groups by state (running, stopped, …)
    *   Sorts each group by launch_time DESC
    *   Shows 'Name – 3 h ago (i-abc123)'  (Name is dim if it’s a fallback)
    """
    by_state = defaultdict(list)
    for inst in instances:
        by_state[inst["state"]].append(inst)

    ordered_states = ["running", "stopped", "pending", "terminated"]
    choices = []
    for state in ordered_states:
        group = sorted(by_state.get(state, []), key=itemgetter("launch_time"), reverse=True)
        if not group:
            continue
        choices.append({"name": f"--- {state.upper()} ---", "disabled": ""})
        for inst in group:
            label = _instance_label(inst)
            choices.append({"name": label, "value": inst})

    return inquirer.select(message="Choose instance:", choices=choices).execute()


def _instance_label(inst: dict) -> str:
    time_str = naturaltime(inst["launch_time"])
    name = inst["name"]
    if name == inst["id"]:
        name = f"[dim]{name}[/dim]"
    return f"{name} – {time_str} ({inst['id']})"
