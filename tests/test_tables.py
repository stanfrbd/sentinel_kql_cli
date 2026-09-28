"""Tests for the tables command."""

import json

from tests.conftest import cli


def test_tables_returns_results():
    result = cli("--output", "json", cmd=["tables", "--days", "1"])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) > 0


def test_tables_has_table_column():
    result = cli("--output", "json", cmd=["tables", "--days", "1"])
    rows = json.loads(result.stdout)
    assert "$table" in rows[0]
