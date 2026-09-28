"""Environment loading and Azure config resolution."""

import os
import subprocess
import sys
from pathlib import Path

AZ = "az.cmd" if sys.platform == "win32" else "az"

# Load .env once at import time (siblings of the package root)
_ENV_PATH = Path(__file__).parent.parent / ".env"


def load_env() -> None:
    if not _ENV_PATH.exists():
        return
    for raw in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def get_subscription_id() -> str:
    result = subprocess.run(
        [AZ, "account", "show", "--query", "id", "-o", "tsv"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        from sentinel_kql.output import err_console
        err_console.print("[red]Not logged in. Run `az login` first.[/red]")
        sys.exit(1)
    return result.stdout.strip()


def resolve_workspace_id(subscription: str, resource_group: str, workspace: str) -> str:
    """Return the Log Analytics workspace GUID from its name via az CLI."""
    result = subprocess.run(
        [
            AZ, "monitor", "log-analytics", "workspace", "show",
            "--subscription", subscription,
            "--resource-group", resource_group,
            "--workspace-name", workspace,
            "--query", "customerId",
            "-o", "tsv",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        from sentinel_kql.output import err_console
        err_console.print(f"[red]Could not resolve workspace ID:[/red] {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()
