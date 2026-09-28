"""Tests for query, query-file, and export."""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import cli


def test_query_inline_returns_list(first_table):
    result = cli("--output", "json", cmd=["query", f"{first_table} | limit 3", "--days", "1", "--limit", "3"])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert isinstance(rows, list)


def test_query_respects_limit(first_table):
    result = cli("--output", "json", cmd=["query", first_table, "--days", "1", "--limit", "2"])
    rows = json.loads(result.stdout)
    assert len(rows) <= 2


def test_query_file_executes_kql(first_table, tmp_path):
    kql_file = tmp_path / "test.kql"
    kql_file.write_text(f"{first_table} | limit 3", encoding="utf-8")
    result = cli("--output", "json", cmd=["query-file", str(kql_file), "--days", "1", "--limit", "3"])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert isinstance(rows, list)


def test_export_csv(first_table, tmp_path):
    out = tmp_path / "results.csv"
    result = cli("--export", str(out), "--export-format", "csv",
                 cmd=["query", f"{first_table} | limit 3", "--days", "1", "--limit", "3"])
    assert result.returncode == 0, result.stderr
    assert out.exists() and out.stat().st_size > 0


def test_export_json(first_table, tmp_path):
    out = tmp_path / "results.json"
    result = cli("--export", str(out), "--export-format", "json",
                 cmd=["query", f"{first_table} | limit 3", "--days", "1", "--limit", "3"])
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list)


def test_query_start_end_range(first_table):
    yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    result = cli("--output", "json",
                 cmd=["query", f"{first_table} | limit 3", "--start", yesterday, "--end", today, "--limit", "3"])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert isinstance(rows, list)


def test_query_start_only_defaults_end_to_now(first_table):
    yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    result = cli("--output", "json",
                 cmd=["query", f"{first_table} | limit 3", "--start", yesterday, "--limit", "3"])
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert isinstance(rows, list)


def test_query_invalid_date_fails():
    result = cli("--output", "json",
                 cmd=["query", "SecurityEvent | limit 1", "--start", "not-a-date"])
    assert result.returncode != 0
