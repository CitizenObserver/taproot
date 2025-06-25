# Taproot v0.7 — EC2 Instance Connect TUI

Taproot lets you jump onto any EC2 instance **in seconds**—even in an AWS SSO environment—without memorising IDs or digging through the console.

| Feature                                             | Status |
| --------------------------------------------------- | ------ |
| Profile picker (SSO‑aware)                          | ✅      |
| Instance list (running first, fresh → old)          | ✅      |
| Human‑friendly “launched 3 h ago” times             | ✅      |
| Change profile without restarting                   | ✅      |
| One‑shot `aws ec2-instance-connect ssh …` execution | ✅      |

---

## Installation

### 1 · Via `pipx` (recommended)

```bash
pipx install taproot          # from PyPI once published

# or, from your local checkout (main branch)
pipx install .
```

`pipx` keeps Taproot isolated in its own virtual‑env and drops a global executable called `` in `~/.local/bin`.

### 2 · Via plain `pip`

```bash
pip install --user .
```

---

## Quick start

```bash
taproot connect
# ┌─────────────────────┐
# │ choose AWS profile   │
# └─────────────────────┘

# then …

#  ↩  Change profile
#  app-bluebox        4 m ago   running  i-0abc123
#  job-worker-12      2 h ago   running  i-0def456
#  ─────────────────────────────────────────────────
#  i-0e59…            9 m ago terminated i-0e59…
```

Pick an instance → Taproot spawns `` and you’re inside.

---

## Development workflow

```bash
git clone https://github.com/your-org/taproot.git
cd taproot
poetry install
poetry run taproot connect  # dev run
```

Run the test suite (once you add tests) with:

```bash
pytest -q
```

---

## Releasing

```bash
poetry version patch         # bumps 0.7.0 → 0.7.1
git commit -am "v0.7.1"
git tag v0.7.1
git push --follow-tags
poetry build
poetry publish               # requires PyPI token
```

---

## Security updates

Dependabot is configured (`.github/dependabot.yml`) to open weekly PRs for:

- Python dependencies in `pyproject.toml` / `poetry.lock`
- GitHub Actions versions

Merge them after CI passes to stay current.

---

## License

MIT © 2025 Citizen Observer

