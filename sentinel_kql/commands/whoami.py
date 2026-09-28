"""whoami command — show current Azure identity and workspace info."""

import json
import subprocess
import sys

import click

from sentinel_kql.config import AZ
from sentinel_kql.output import emit, err_console


@click.command()
@click.pass_context
def whoami(ctx):
    """Show current Azure identity and workspace info."""
    result = subprocess.run([AZ, "account", "show"], capture_output=True, text=True)
    if result.returncode != 0:
        err_console.print("[red]Not logged in. Run `az login`.[/red]")
        sys.exit(1)
    acct = json.loads(result.stdout)
    rows = [
        {"Field": "User",            "Value": acct.get("user", {}).get("name", "")},
        {"Field": "Subscription",    "Value": acct.get("name", "")},
        {"Field": "Subscription ID", "Value": acct.get("id", "")},
        {"Field": "Tenant ID",       "Value": acct.get("tenantId", "")},
        {"Field": "Workspace ID",    "Value": ctx.obj["workspace_id"]},
    ]
    emit(rows, ctx.obj["output"], title="Identity",
         export=ctx.obj["export_path"], export_fmt=ctx.obj["export_format"])
