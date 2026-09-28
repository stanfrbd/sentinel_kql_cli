"""Output rendering: rich table, JSON, CSV, and file export."""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


def _serialize(v):
    if isinstance(v, datetime):
        return v.isoformat()
    return v


def _serializable(rows: list[dict]) -> list[dict]:
    return [{k: _serialize(v) for k, v in row.items()} for row in rows]


def print_table(rows: list[dict], title: str | None = None) -> None:
    if not rows:
        console.print(Panel("[yellow]No results returned.[/yellow]", title=title or "Results"))
        return
    t = Table(title=title, show_header=True, header_style="bold cyan", show_lines=False)
    for col in rows[0]:
        t.add_column(col, overflow="fold", max_width=80)
    for row in rows:
        t.add_row(*[str(_serialize(row[c])) if row[c] is not None else "" for c in rows[0]])
    console.print(t)


def print_json(rows: list[dict]) -> None:
    print(json.dumps(_serializable(rows), indent=2, ensure_ascii=False))


def print_csv(rows: list[dict]) -> None:
    if not rows:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for row in rows:
        writer.writerow({k: _serialize(v) for k, v in row.items()})


def export_file(rows: list[dict], path: str, fmt: str) -> None:
    p = Path(path)
    if fmt == "json":
        p.write_text(
            json.dumps(_serializable(rows), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    elif fmt == "csv":
        with p.open("w", newline="", encoding="utf-8") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                for row in rows:
                    writer.writerow({k: _serialize(v) for k, v in row.items()})
    console.print(f"[green]Exported {len(rows)} row(s) -> {p.resolve()}[/green]")


def emit(
    rows: list[dict],
    fmt: str,
    title: str | None = None,
    export: str | None = None,
    export_fmt: str = "json",
) -> None:
    if fmt == "table":
        print_table(rows, title=title)
    elif fmt == "json":
        print_json(rows)
    elif fmt == "csv":
        print_csv(rows)

    if export:
        export_file(rows, export, export_fmt)
