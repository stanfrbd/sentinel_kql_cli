# Sentinel KQL CLI

A command-line tool for running KQL hunting queries against Microsoft Sentinel (Log Analytics). Authenticates via `az login` using Microsoft's Azure Identity library.

## Project layout

```
sentinel_kql_cli/
├── sentinel_kql/           # Python package
│   ├── __init__.py
│   ├── cli.py              # Click group + shared context
│   ├── config.py           # .env loading, workspace ID resolution
│   ├── client.py           # Azure Monitor Logs client & query runner
│   ├── output.py           # rich table / JSON / CSV rendering
│   └── commands/
│       ├── whoami.py
│       ├── tables.py
│       ├── schema.py
│       └── query.py        # query, query-file, saved-searches
├── sentinel_kql_cli.py     # thin shim (python sentinel_kql_cli.py …)
├── smoke_test.py
├── pyproject.toml
├── requirements.txt
├── .env                    # local secrets (gitignored)
└── .env.example
```

## Prerequisites

- Python 3.11+
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) — run `az login` before use
- Access to a Microsoft Sentinel / Log Analytics workspace

## Required Azure roles

All operations in this tool are **read-only**. Assign one of the following built-in roles on the Log Analytics workspace (or the resource group / subscription that contains it):

| Role | Scope | What it allows |
|---|---|---|
| **Microsoft Sentinel Reader** | Resource group or workspace | Read Sentinel data, run KQL queries. **Minimum role for this tool.** |
| **Log Analytics Reader** | Workspace | Run KQL queries and read workspace metadata. Equivalent to Sentinel Reader for pure query access. |
| **Microsoft Sentinel Contributor** | Resource group or workspace | Everything above plus managing analytics rules, watchlists, etc. Wider than needed for hunting. |

### Assigning the role (Azure portal)

1. Go to your Log Analytics workspace → **Access control (IAM)**
2. Click **Add role assignment**
3. Select **Microsoft Sentinel Reader**
4. Assign to the user or service principal that will run `az login`

### Assigning via Azure CLI

```bash
az role assignment create \
  --role "Microsoft Sentinel Reader" \
  --assignee "<user-email-or-object-id>" \
  --scope "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>"
```

> **Note:** Role propagation can take a few minutes. If queries fail with a 403 immediately after assignment, wait and retry.

## Installation

```bash
pip install -e .
```

This installs the `sentinel-kql` entry point. Alternatively, install dependencies only and use the shim:

```bash
pip install -r requirements.txt
python sentinel_kql_cli.py …
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```ini
SENTINEL_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SENTINEL_RESOURCE_GROUP=my-resource-group
SENTINEL_WORKSPACE=my-log-analytics-workspace

# Optional — workspace GUID (Properties → Workspace ID in Azure portal).
# Set this to skip the automatic resolution step (faster startup).
SENTINEL_WORKSPACE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## Usage

```
sentinel-kql [OPTIONS] COMMAND [ARGS]…
```

All global flags can also be set via environment variables / `.env`.

```
Options:
  --workspace-id TEXT              Log Analytics workspace GUID
  --workspace TEXT                 Workspace name (resolves --workspace-id if unset)
  -g, --resource-group TEXT        Azure resource group
  -s, --subscription TEXT          Azure subscription ID
  -o, --output [table|json|csv]    Output format  [default: table]
  --export TEXT                    Write results to file
  --export-format [json|csv]       Format for --export  [default: json]
  -h, --help                       Show help
```

### Commands

| Command | Description |
|---|---|
| `whoami` | Show current Azure identity and workspace info |
| `tables [--days N]` | List tables that have data |
| `schema TABLE` | Get column schema of a table |
| `query KQL [--days N] [--start DATE] [--end DATE] [--limit N]` | Run an inline KQL query |
| `query-file FILE [--days N] [--start DATE] [--end DATE] [--limit N]` | Run KQL from a `.kql` file |
| `saved-searches [--days N] [--start DATE] [--end DATE]` | List workspace functions/saved searches |

### Examples

```bash
# Verify identity
sentinel-kql whoami

# List tables active in the last 7 days
sentinel-kql tables --days 7

# Get schema of SigninLogs
sentinel-kql schema SigninLogs

# Inline query — last 24 h, limit 50 rows
sentinel-kql query "SecurityEvent | where EventID == 4625 | summarize count() by Account" \
  --days 1 --limit 50

# Specific date range
sentinel-kql query "SecurityEvent" --start 2026-01-01 --end 2026-01-15

# Start date only — end defaults to now
sentinel-kql query "SecurityEvent" --start 2026-09-01

# JSON output (pipe-friendly)
sentinel-kql --output json query "Heartbeat | limit 5"

# Export to CSV
sentinel-kql --export results.csv --export-format csv \
  query "SigninLogs | where ResultType != 0 | project TimeGenerated, UserPrincipalName, ResultType" \
  --days 7

# Run KQL from a file, last 30 days, no row cap
sentinel-kql query-file hunt.kql --days 30 --limit 0

# Run KQL from a file over a specific date range
sentinel-kql query-file hunt.kql --start 2026-01-01 --end 2026-01-31 --limit 0
```

## LLM skill

A Claude Code skill lives at `.claude/agents/sentinel-kql.md`. It gives an LLM a complete reference for driving this CLI. Load it via `/sentinel-kql` in Claude Code.

## Tests

```bash
pytest
```

12 integration tests in `tests/` cover: identity verification, table listing, schema fetch, inline query, query-file, CSV export, and JSON export. All tests hit the real workspace — no mocks.
