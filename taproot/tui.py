from __future__ import annotations
from datetime import timezone
from typing import List, Dict, Any, Sequence
import humanize
from InquirerPy import inquirer
from rich.console import Console
from rich.theme import Theme

console = Console(theme=Theme({"header": "bold cyan", "dim": "dim"}))


class _ProfileChange:
    pass


PROFILE_CHANGE = _ProfileChange()

COLS = {
    "name": 13,
    "age": 14,
    "state": 10,
    "public": 15,
    "private": 15,
}


def _naturaltime(dt):
    return humanize.naturaltime(dt.astimezone(timezone.utc))


def _row(i: Dict[str, Any]) -> str:
    name = i["name"] if i["name"] != i["id"] else f"{i['name']}"
    age = _naturaltime(i["launch_time"])
    pub = i["public_ip"] or "-"
    priv = i["private_ip"] or "-"
    return (
        f"{name:<{COLS['name']}} {age:<{COLS['age']}} {i['state']:<{COLS['state']}} "
        f"{pub:<{COLS['public']}} {priv:<{COLS['private']}} {i['id']}"
    )


def pick_profile(profiles: Sequence[str], default: str | None):
    console.clear()
    console.print("[header]AWS profile selector (↑↓, ⏎)[/header]")
    return inquirer.select(
        message="Choose profile:", choices=list(profiles), default=default
    ).execute()


def pick_instance(instances: List[Dict[str, Any]], profile: str):
    console.clear()
    console.print(f"Profile: [bold]{profile}[/bold]\n")

    running = [j for j in instances if j["state"] == "running"]
    others = [j for j in instances if j["state"] != "running"]
    running.sort(key=lambda x: x["launch_time"], reverse=True)
    others.sort(key=lambda x: x["launch_time"], reverse=True)

    choices = [{"name": "↩  Change profile", "value": PROFILE_CHANGE}]
    choices += [{"name": _row(j), "value": j} for j in running]
    if running and others:
        # Visual spacer must still have a dummy `value` so InquirerPy sees both keys
        choices.append({"name": " ", "value": "__sep__", "disabled": ""})
    choices += [{"name": _row(j), "value": j} for j in others]

    return inquirer.select(
        message="Choose instance:", choices=choices, vi_mode=False
    ).execute()
