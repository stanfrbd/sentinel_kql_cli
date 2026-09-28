"""tables command — list all tables with data in the workspace."""

import click

from sentinel_kql.client import run_kql
from sentinel_kql.output import emit, console


@click.command()
@click.option("--days", default=1, show_default=True, help="Lookback window in days.")
@click.pass_context
def tables(ctx, days):
    """List all tables that have data in the workspace."""
    kql = "search * | distinct $table | sort by $table asc"
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, days)
    emit(rows, ctx.obj["output"], title="Tables",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
    if ctx.obj["output"] == "table":
        console.print(f"[dim]{len(rows)} table(s) with data in the last {days} day(s).[/dim]")
