#!/usr/bin/env python3
import boto3
import subprocess
import os
import sys
import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

def list_aws_profiles():
    config_path = os.path.expanduser("~/.aws/config")
    profiles = []
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("[profile "):
                    profile_name = line.split("profile ")[1].split("]")[0]
                    profiles.append(profile_name)
                elif line.startswith("[default]"):
                    profiles.append("default")
    return profiles

def select_profile(profiles):
    print("Select AWS profile:")
    for idx, profile in enumerate(profiles):
        print(f"{idx + 1}. {profile}")
    choice = int(input("Enter number: ")) - 1
    return profiles[choice]

def aws_sso_login(profile):
    subprocess.run(["aws", "sso", "login", "--profile", profile], check=True)

def list_ec2_instances(profile):
    session = boto3.Session(profile_name=profile)
    ec2 = session.client("ec2")

    response = ec2.describe_instances()
    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            launch_time = instance["LaunchTime"]
            state = instance["State"]["Name"]
            name = "N/A"
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
            time_diff = relativedelta(datetime.now(timezone.utc), launch_time)
            time_ago = f"{time_diff.days}d {time_diff.hours}h {time_diff.minutes}m ago"
            instances.append({
                "name": name,
                "id": instance_id,
                "state": state,
                "launched": time_ago
            })
    return instances

def select_instance(instances):
    print("\nSelect EC2 instance:")
    for idx, inst in enumerate(instances):
        print(f"{idx + 1}. [{inst['state']}] {inst['name']} ({inst['id']}) - Launched {inst['launched']}")
    choice = int(input("Enter number: ")) - 1
    return instances[choice]

def connect_to_instance(instance_id, profile):
    cmd = [
        "aws", "ec2-instance-connect", "ssh",
        "--instance-id", instance_id,
        "--connection-type", "eice",
        "--os-user", "root",
        "--profile", profile
    ]
    subprocess.run(cmd)

def main():
    profiles = list_aws_profiles()
    profile = select_profile(profiles)
    aws_sso_login(profile)
    instances = list_ec2_instances(profile)
    instance = select_instance(instances)
    connect_to_instance(instance['id'], profile)

if __name__ == "__main__":
    main()
