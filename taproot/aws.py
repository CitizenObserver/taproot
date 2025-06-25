from __future__ import annotations

import subprocess
from datetime import timezone
from typing import Iterable

import boto3
import botocore


def list_profiles() -> list[str]:
    """Return configured AWS CLI profiles, defaulting to ['default']."""
    profiles = boto3.session.Session().available_profiles
    return profiles if profiles else ["default"]


def ensure_credentials(profile: str) -> boto3.Session:
    """Validate credentials; perform `aws sso login` once if expired."""
    session = boto3.Session(profile_name=profile)
    sts = session.client("sts")

    def _valid() -> bool:
        try:
            sts.get_caller_identity()
            return True
        except botocore.exceptions.ClientError as exc:
            code = exc.response["Error"]["Code"]
            return code not in {
                "ExpiredToken",
                "InvalidClientTokenId",
                "UnauthorizedException",
            }

    if not _valid():
        subprocess.run(["aws", "sso", "login", "--profile", profile], check=True)
        if not _valid():
            raise RuntimeError(f"SSO login failed for profile '{profile}'")

    return session


def _name_tag(instance: dict) -> str | None:
    """Return the value of the 'Name' tag if present."""
    for tag in instance.get("Tags", []):
        if tag.get("Key") == "Name" and tag.get("Value"):
            return tag["Value"]
    return None


def iter_instances(session: boto3.Session) -> Iterable[dict]:
    """Yield raw EC2 instance dictionaries across all pages."""
    ec2 = session.client("ec2")
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            yield from reservation["Instances"]


def collect_instances(session: boto3.Session) -> list[dict]:
    """Return simplified instance dictionaries for TUI display."""
    items = []
    for inst in iter_instances(session):
        items.append(
            {
                "id": inst["InstanceId"],
                "name": _name_tag(inst) or inst["InstanceId"],
                "state": inst["State"]["Name"],
                "launch_time": inst["LaunchTime"].astimezone(timezone.utc),
            }
        )
    return items
