"""Tests for the schema command."""

import json

import pytest

from tests.conftest import cli


def test_schema_returns_columns(first_table):
    result = cli("--output", "json", cmd=["schema", first_table])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) > 0


def test_schema_has_column_name_field(first_table):
    result = cli("--output", "json", cmd=["schema", first_table])
    rows = json.loads(result.stdout)
    assert "ColumnName" in rows[0]


def test_schema_unknown_table_fails():
    result = cli("--output", "json", cmd=["schema", "TableThatDoesNotExist_XYZ"])
    assert result.returncode != 0
