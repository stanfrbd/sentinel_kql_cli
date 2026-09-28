"""Tests for the whoami command."""

import json

from tests.conftest import cli


def test_whoami_returns_identity_fields():
    result = cli("--output", "json", cmd=["whoami"])
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    fields = {r["Field"]: r["Value"] for r in data}
    assert "User" in fields
    assert "Workspace ID" in fields


def test_whoami_workspace_id_is_guid():
    result = cli("--output", "json", cmd=["whoami"])
    data = json.loads(result.stdout)
    fields = {r["Field"]: r["Value"] for r in data}
    assert len(fields["Workspace ID"]) == 36
