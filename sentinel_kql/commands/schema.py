"""schema command — get column schema of a table."""

import click

from sentinel_kql.client import run_kql
from sentinel_kql.output import emit


@click.command()
@click.argument("table_name")
@click.pass_context
def schema(ctx, table_name):
    """Get the column schema of TABLE_NAME."""
    kql = f"{table_name} | getschema"
    rows = run_kql(ctx.obj["client"], ctx.obj["workspace_id"], kql, days=90)
    emit(rows, ctx.obj["output"], title=f"Schema — {table_name}",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
