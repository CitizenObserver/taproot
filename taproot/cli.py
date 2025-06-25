from __future__ import annotations

import subprocess

import typer
from rich import print

from . import __version__
from .aws import list_profiles, ensure_credentials, collect_instances
from .cache import load as cache_load, save as cache_save
from .tui import pick_profile, pick_instance, PROFILE_CHANGE

app = typer.Typer(help="Taproot: EC2 Instance Connect TUI.", add_completion=False)


def _ssh(profile: str, iid: str, user: str = "root") -> None:
    cmd = [
        "aws",
        "ec2-instance-connect",
        "ssh",
        "--instance-id",
        iid,
        "--connection-type",
        "eice",
        "--os-user",
        user,
        "--profile",
        profile,
    ]
    print(f"[grey50]$ {' '.join(cmd)}[/grey50]")
    subprocess.run(cmd, check=True)


def _interactive() -> None:
    cache = cache_load()
    current_profile: str | None = cache.get("profile")

    while True:
        current_profile = pick_profile(list_profiles(), current_profile)
        session = ensure_credentials(current_profile)

        while True:
            instances = collect_instances(session)
            choice = pick_instance(instances, current_profile)

            if choice is PROFILE_CHANGE:
                break  # user pressed Tab

            instance_id = choice["id"]
            cache_save(current_profile, instance_id)
            _ssh(current_profile, instance_id)
            return  # exit after first connection


@app.command()
def connect() -> None:
    """Launch the interactive TUI."""
    _interactive()


@app.command()
def version() -> None:
    """Print version."""
    print(__version__)


if __name__ == "__main__":
    app()
