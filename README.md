# Taproot

A terminal-based TUI to select AWS profiles, perform SSO login, list EC2 instances, and SSH into one with EC2 Instance Connect.

## Features

- AWS SSO login integration
- Profile and instance picker
- EC2 metadata with launch time
- Instant SSH via `ec2-instance-connect`

## Usage

```bash
poetry install
poetry run python -m taproot.main
```