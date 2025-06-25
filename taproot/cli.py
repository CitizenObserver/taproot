from __future__ import annotations

import subprocess
from typing import Optional

import typer
from rich import print  # purposeful re-export for colourful output

from . import __version__
from .aws import collect_instances, ensure_credentials, list_profiles
from .cache import load as cache_load, save as cache_save
from .tui import pick_instance, pick_profile

app = typer.Typer(
    help="Taproot: quick EC2 Instance Connect via TUI.", add_completion=False
)


@app.command()
def connect(
    profile: Optional[str] = typer.Option(
        None, "-p", "--profile", help="AWS CLI profile name."
    ),
    instance_id: Optional[str] = typer.Option(
        None, "--instance-id", help="Connect directly, skip TUI."
    ),
    user: str = typer.Option("root", "--user", help="OS user for SSH session."),
):
    """Interactive (or headless) EC2 Instance Connect."""
    cache = cache_load()
    profile = profile or pick_profile(list_profiles(), cache.get("profile"))
    session = ensure_credentials(profile)

    if instance_id is None:
        instances = collect_instances(session)
        chosen = pick_instance(instances)
        instance_id = chosen["id"]
    else:
        valid_ids = {i["id"] for i in collect_instances(session)}
        if instance_id not in valid_ids:
            typer.echo(
                f"Instance {instance_id} not found under profile {profile}",
                err=True,
            )
            raise typer.Exit(code=2)

    cache_save(profile, instance_id)
    _ssh(profile, instance_id, user)


def _ssh(profile: str, instance_id: str, user: str) -> None:
    cmd = [
        "aws",
        "ec2-instance-connect",
        "ssh",
        "--instance-id",
        instance_id,
        "--connection-type",
        "eice",
        "--os-user",
        user,
        "--profile",
        profile,
    ]
    print(f"[grey50]$ {' '.join(cmd)}[/grey50]")
    subprocess.run(cmd, check=True)


@app.command()
def version() -> None:
    """Print Taproot version."""
    print(__version__)


if __name__ == "__main__":
    app()
