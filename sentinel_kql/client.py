"""Azure Monitor Logs client and query execution."""

import sys
from datetime import timedelta

from azure.identity import AzureCliCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus


def make_client(verify_ssl: bool = True) -> LogsQueryClient:
    credential = AzureCliCredential()
    if not verify_ssl:
        from azure.core.pipeline.transport import RequestsTransport
        return LogsQueryClient(credential, transport=RequestsTransport(connection_verify=False))
    return LogsQueryClient(credential)


def rows_from_response(table) -> list[dict]:
    # table.columns is List[str] in azure-monitor-query >= 2.0
    return [dict(zip(table.columns, row)) for row in table.rows]


def run_kql(client: LogsQueryClient, workspace_id: str, kql: str, timespan) -> list[dict]:
    from sentinel_kql.output import err_console, console

    with console.status("[bold green]Running query…[/bold green]"):
        response = client.query_workspace(
            workspace_id, kql, timespan=timespan
        )

    if response.status == LogsQueryStatus.PARTIAL:
        err_console.print("[yellow]Warning: partial results (query timed out or truncated).[/yellow]")
    elif response.status == LogsQueryStatus.FAILURE:
        err_console.print(f"[red]Query failed:[/red] {response.partial_error}")
        sys.exit(1)

    if not response.tables or len(response.tables[0].rows) == 0:
        return []

    return rows_from_response(response.tables[0])
