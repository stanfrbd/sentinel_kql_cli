"""Top-level Click group with shared context."""

import os
import sys

import click

from sentinel_kql.client import make_client
from sentinel_kql.config import load_env, get_subscription_id, resolve_workspace_id
from sentinel_kql.output import err_console
from sentinel_kql.commands.whoami import whoami
from sentinel_kql.commands.tables import tables
from sentinel_kql.commands.schema import schema
from sentinel_kql.commands.query import query, query_file, saved_searches

load_env()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--workspace-id", envvar="SENTINEL_WORKSPACE_ID",
    help="Log Analytics workspace GUID. Falls back to SENTINEL_WORKSPACE_ID env var, "
         "or is resolved from --workspace + --resource-group.",
)
@click.option(
    "--workspace", envvar="SENTINEL_WORKSPACE",
    help="Workspace name (used to resolve --workspace-id if not set).",
)
@click.option(
    "--resource-group", "-g", envvar="SENTINEL_RESOURCE_GROUP",
    help="Azure resource group.",
)
@click.option(
    "--subscription", "-s", envvar="SENTINEL_SUBSCRIPTION_ID",
    help="Azure subscription ID. Defaults to current az account.",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json", "csv"], case_sensitive=False),
    default="table", show_default=True,
    help="Output format.",
)
@click.option("--export", "export_path", default=None, help="Export results to file.")
@click.option(
    "--export-format",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    default="json", show_default=True,
    help="Format for --export.",
)
@click.option(
    "--no-verify", "no_verify", is_flag=True, default=False,
    help="Disable SSL certificate verification (useful behind corporate proxies). Env: SSL_VERIFY=false.",
)
@click.pass_context
def cli(ctx, workspace_id, workspace, resource_group, subscription, output, export_path, export_format, no_verify):
    """Sentinel KQL CLI — query Microsoft Sentinel from the command line.

    Requires `az login` with access to the target Log Analytics workspace.

    \b
    Configuration via .env or environment variables:
      SENTINEL_WORKSPACE_ID      Workspace GUID (fastest — skips auto-resolution)
      SENTINEL_WORKSPACE         Workspace name
      SENTINEL_RESOURCE_GROUP    Resource group
      SENTINEL_SUBSCRIPTION_ID   Subscription ID
      SSL_VERIFY                 Set to false to disable SSL verification
    """
    ctx.ensure_object(dict)

    # SSL_VERIFY=false in env is equivalent to passing --no-verify
    if not no_verify:
        no_verify = os.environ.get("SSL_VERIFY", "true").lower() == "false"

    if not workspace_id:
        if not workspace or not resource_group:
            err_console.print(
                "[red]Provide --workspace-id, or both --workspace and --resource-group "
                "so the ID can be resolved automatically.[/red]"
            )
            sys.exit(1)
        sub = subscription or get_subscription_id()
        workspace_id = resolve_workspace_id(sub, resource_group, workspace)

    ctx.obj["workspace_id"] = workspace_id
    ctx.obj["output"] = output.lower()
    ctx.obj["export_path"] = export_path
    ctx.obj["export_format"] = export_format.lower()
    ctx.obj["client"] = make_client(verify_ssl=not no_verify)


cli.add_command(whoami)
cli.add_command(tables)
cli.add_command(schema)
cli.add_command(query)
cli.add_command(query_file)
cli.add_command(saved_searches)
