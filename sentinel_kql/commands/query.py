"""query, query-file, and saved-searches commands."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import click

from sentinel_kql.client import run_kql
from sentinel_kql.output import emit, console


def _resolve_timespan(days: int, start: str | None, end: str | None):
    """Return a timedelta or (datetime, datetime) tuple for the Azure SDK."""
    if start or end:
        now = datetime.now(tz=timezone.utc)
        try:
            s = datetime.fromisoformat(start).replace(tzinfo=timezone.utc) if start else now - timedelta(days=days)
            e = datetime.fromisoformat(end).replace(tzinfo=timezone.utc) if end else now
        except ValueError as exc:
            raise click.BadParameter(str(exc), param_hint="'--start'/'--end'") from exc
        return (s, e)
    return timedelta(days=days)


@click.command()
@click.argument("kql_query")
@click.option("--days", default=1, show_default=True, help="Lookback window in days (ignored when --start/--end are set).")
@click.option("--start", default=None, metavar="DATE", help="Start of time range (ISO 8601, e.g. 2026-01-01).")
@click.option("--end", default=None, metavar="DATE", help="End of time range (ISO 8601). Defaults to now.")
@click.option("--limit", default=100, show_default=True, help="Max rows (0 = no limit).")
@click.pass_context
def query(ctx, kql_query, days, start, end, limit):
    """Run an inline KQL query.

    \b
    Examples:
      sentinel-kql query "SecurityEvent | where EventID == 4625" --days 7 --limit 50
      sentinel-kql query "SecurityEvent" --start 2026-01-01 --end 2026-01-15
      sentinel-kql query "SecurityEvent" --start 2026-01-01
    """
    kql = kql_query if limit == 0 else f"{kql_query}\n| limit {limit}"
    timespan = _resolve_timespan(days, start, end)
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, timespan)
    emit(rows, ctx.obj["output"], title="Query Results",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
    if ctx.obj["output"] == "table":
        console.print(f"[dim]{len(rows)} row(s) returned.[/dim]")


@click.command("query-file")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--days", default=1, show_default=True, help="Lookback window in days (ignored when --start/--end are set).")
@click.option("--start", default=None, metavar="DATE", help="Start of time range (ISO 8601, e.g. 2026-01-01).")
@click.option("--end", default=None, metavar="DATE", help="End of time range (ISO 8601). Defaults to now.")
@click.option("--limit", default=100, show_default=True, help="Max rows (0 = no limit).")
@click.pass_context
def query_file(ctx, file, days, start, end, limit):
    """Run a KQL query from FILE.

    \b
    Examples:
      sentinel-kql query-file hunt.kql --days 30 --limit 0
      sentinel-kql query-file hunt.kql --start 2026-01-01 --end 2026-01-15
    """
    kql = Path(file).read_text(encoding="utf-8").strip()
    if limit > 0:
        kql = f"{kql}\n| limit {limit}"
    timespan = _resolve_timespan(days, start, end)
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, timespan)
    emit(rows, ctx.obj["output"], title=f"Results — {file}",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
    if ctx.obj["output"] == "table":
        console.print(f"[dim]{len(rows)} row(s) from [italic]{file}[/italic].[/dim]")


@click.command("saved-searches")
@click.option("--days", default=30, show_default=True, help="Lookback window in days (ignored when --start/--end are set).")
@click.option("--start", default=None, metavar="DATE", help="Start of time range (ISO 8601, e.g. 2026-01-01).")
@click.option("--end", default=None, metavar="DATE", help="End of time range (ISO 8601). Defaults to now.")
@click.pass_context
def saved_searches(ctx, days, start, end):
    """List saved searches / functions available in the workspace."""
    kql = "_Functions | project Name, Parameters, Body | sort by Name asc"
    timespan = _resolve_timespan(days, start, end)
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, timespan)
    emit(rows, ctx.obj["output"], title="Saved Searches / Functions",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
