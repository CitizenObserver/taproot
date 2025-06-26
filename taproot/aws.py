from __future__ import annotations
import subprocess, sys, boto3, botocore
from datetime import timezone
from typing import Iterable, Dict, List


def list_profiles() -> list[str]:
    return boto3.session.Session().available_profiles or ["default"]


def ensure_credentials(profile: str) -> boto3.Session:
    """
    Return a boto3.Session whose credentials are definitely valid.

    If the cached AWS SSO credentials for *profile* are stale, we transparently run
    “aws sso login --profile <profile>” once, then re-check.  This now catches the
    newer TokenRetrievalError that Botocore throws when the token is expired.
    """
    session = boto3.session.Session(profile_name=profile, region_name="us-east-1")
    sts = session.client("sts")

    # Errors that always mean “token/credentials are bad → force a refresh”
    BAD_CODES = {
        "ExpiredToken",
        "InvalidClientTokenId",
        "UnauthorizedException",
    }

    def _valid() -> bool:
        """Return True iff the current credentials are usable."""
        try:
            sts.get_caller_identity()
            return True
        except botocore.exceptions.ClientError as exc:
            # e.g. ExpiredToken from STS
            return exc.response["Error"]["Code"] not in BAD_CODES
        except (
            botocore.exceptions.UnauthorizedSSOTokenError,  # direct SSO failure
            botocore.exceptions.TokenRetrievalError,  # new in botocore.tokens
        ):
            return False

    # First check – if invalid, refresh once
    if not _valid():
        subprocess.run(["aws", "sso", "login", "--profile", profile], check=True)
        if not _valid():
            raise RuntimeError(f"[taproot] AWS SSO login failed (profile: {profile}).")

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
            "private_ip": i.get("PrivateIpAddress") or "",
            "public_ip": i.get("PublicIpAddress") or "",
        }
        for i in iter_instances(session)
    ]
