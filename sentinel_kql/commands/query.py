"""query, query-file, and saved-searches commands."""

from pathlib import Path

import click

from sentinel_kql.client import run_kql
from sentinel_kql.output import emit, console


@click.command()
@click.argument("kql_query")
@click.option("--days", default=1, show_default=True, help="Lookback window in days.")
@click.option("--limit", default=100, show_default=True, help="Max rows (0 = no limit).")
@click.pass_context
def query(ctx, kql_query, days, limit):
    """Run an inline KQL query.

    \b
    Example:
      sentinel-kql query "SecurityEvent | where EventID == 4625" --days 7 --limit 50
    """
    kql = kql_query if limit == 0 else f"{kql_query}\n| limit {limit}"
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, days)
    emit(rows, ctx.obj["output"], title="Query Results",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
    if ctx.obj["output"] == "table":
        console.print(f"[dim]{len(rows)} row(s) returned.[/dim]")


@click.command("query-file")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--days", default=1, show_default=True, help="Lookback window in days.")
@click.option("--limit", default=100, show_default=True, help="Max rows (0 = no limit).")
@click.pass_context
def query_file(ctx, file, days, limit):
    """Run a KQL query from FILE.

    \b
    Example:
      sentinel-kql query-file hunt.kql --days 30 --limit 0
    """
    kql = Path(file).read_text(encoding="utf-8").strip()
    if limit > 0:
        kql = f"{kql}\n| limit {limit}"
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, days)
    emit(rows, ctx.obj["output"], title=f"Results — {file}",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
    if ctx.obj["output"] == "table":
        console.print(f"[dim]{len(rows)} row(s) from [italic]{file}[/italic].[/dim]")


@click.command("saved-searches")
@click.option("--days", default=30, show_default=True, help="Lookback window in days.")
@click.pass_context
def saved_searches(ctx, days):
    """List saved searches / functions available in the workspace."""
    kql = "_Functions | project Name, Parameters, Body | sort by Name asc"
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, days)
    emit(rows, ctx.obj["output"], title="Saved Searches / Functions",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
