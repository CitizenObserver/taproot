from __future__ import annotations
import subprocess, boto3, botocore
from datetime import timezone
from typing import Iterable, Dict, List

def list_profiles() -> list[str]:
    return boto3.session.Session().available_profiles or ["default"]

def ensure_credentials(profile: str) -> boto3.Session:
    session = boto3.Session(profile_name=profile)
    sts = session.client("sts")

    def _valid() -> bool:
        try:
            sts.get_caller_identity()
            return True
        except botocore.exceptions.ClientError as exc:
            return exc.response["Error"]["Code"] not in {
                "ExpiredToken", "InvalidClientTokenId", "UnauthorizedException",
            }

    if not _valid():
        subprocess.run(["aws", "sso", "login", "--profile", profile], check=True)
        if not _valid():
            raise RuntimeError(f"SSO login failed for profile '{profile}'")
    return session

def _name_tag(inst: Dict) -> str | None:
    for t in inst.get("Tags", []):
        if t.get("Key") == "Name" and t.get("Value"):
            return t["Value"]
    return None

def iter_instances(session: boto3.Session) -> Iterable[dict]:
    ec2 = session.client("ec2")
    for page in ec2.get_paginator("describe_instances").paginate():
        for r in page["Reservations"]:
            yield from r["Instances"]

def collect_instances(session: boto3.Session) -> List[dict]:
    return [
        {
            "id": i["InstanceId"],
            "name": _name_tag(i) or i["InstanceId"],
            "state": i["State"]["Name"],
            "launch_time": i["LaunchTime"].astimezone(timezone.utc),
        }
        for i in iter_instances(session)
    ]
