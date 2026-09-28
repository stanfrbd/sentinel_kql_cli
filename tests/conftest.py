"""Shared fixtures and helpers for the test suite."""

import os
import subprocess
from pathlib import Path

import pytest

# Load .env so SSL_VERIFY (and other vars) are available to the test process
_ENV_PATH = Path(__file__).parent.parent / ".env"
if _ENV_PATH.exists():
    for _line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

CLI = "sentinel-kql"
_NO_VERIFY = ["--no-verify"] if os.environ.get("SSL_VERIFY", "true").lower() == "false" else []


def cli(*global_opts: str, cmd: list[str]) -> subprocess.CompletedProcess:
    args = [CLI] + list(_NO_VERIFY) + list(global_opts) + cmd
    return subprocess.run(args, capture_output=True, text=True)


@pytest.fixture(scope="session")
def first_table() -> str:
    """Return the name of the first table that has data (used across tests)."""
    import json
    result = cli("--output", "json", cmd=["tables", "--days", "1"])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert rows, "No tables returned — is the workspace reachable?"
    return rows[0]["$table"]
