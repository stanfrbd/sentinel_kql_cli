---
name: sentinel-kql
description: Drive the Sentinel KQL CLI to run hunting queries, list tables, inspect schemas, and export results from Microsoft Sentinel. Use this skill whenever the user wants to hunt in Sentinel, query Log Analytics, list tables, get a table schema, or export KQL results.
---

# Sentinel KQL CLI Skill

You have access to a `sentinel-kql` CLI (installed via `pip install -e .`). It authenticates via `az login` (AzureCliCredential) and queries Microsoft Sentinel / Log Analytics.

## Running commands

```bash
sentinel-kql [GLOBAL OPTIONS] COMMAND [OPTIONS]
```

Use the Bash tool to run commands. Capture stdout for further analysis.

## Global options

| Flag | Env var | Required? | Notes |
|---|---|---|---|
| `--workspace-id` | `SENTINEL_WORKSPACE_ID` | Yes (or resolve from name) | Log Analytics workspace GUID |
| `--workspace` | `SENTINEL_WORKSPACE` | If no workspace-id | Workspace name |
| `--resource-group` | `SENTINEL_RESOURCE_GROUP` | If no workspace-id | Resource group |
| `--subscription` | `SENTINEL_SUBSCRIPTION_ID` | No | Defaults to current az account |
| `--output` / `-o` | — | No | `table` (default), `json`, `csv` |
| `--export` | — | No | File path to write results to |
| `--export-format` | — | No | `json` (default) or `csv` |
| `--no-verify` | `SSL_VERIFY=false` | No | Disable SSL verification (corporate proxy) |

Use `--output json` when you need to parse results programmatically.

## Commands

### `whoami`
Verify identity and workspace.
```bash
sentinel-kql whoami --output json
```

### `tables [--days N]`
List tables with data. Default lookback: 1 day.
```bash
sentinel-kql --output json tables --days 7
```

### `schema TABLE_NAME`
Get column names and types for a table.
```bash
sentinel-kql --output json schema <TABLE>
```

### `query KQL [--days N] [--start DATE] [--end DATE] [--limit N]`
Run an inline KQL query. Default: 1 day lookback, 100-row limit.

`--start` / `--end` accept ISO 8601 dates (`2026-01-01` or `2026-01-01T08:00:00`). When either is set, `--days` is ignored. `--end` defaults to now if omitted.
```bash
sentinel-kql --output json query "T | where ... | summarize ..." --days 7 --limit 0
sentinel-kql --output json query "SecurityEvent" --start 2026-01-01 --end 2026-01-31 --limit 0
sentinel-kql --output json query "SecurityEvent" --start 2026-09-01 --limit 0   # end = now
```

### `query-file FILE [--days N] [--start DATE] [--end DATE] [--limit N]`
Run KQL from a `.kql` file. Same `--start` / `--end` semantics as `query`.
```bash
sentinel-kql --output json query-file hunt.kql --days 30 --limit 0
sentinel-kql --output json query-file hunt.kql --start 2026-01-01 --end 2026-01-31 --limit 0
```

### `saved-searches [--days N] [--start DATE] [--end DATE]`
List workspace functions / saved searches.
```bash
sentinel-kql --output json saved-searches
sentinel-kql --output json saved-searches --start 2026-01-01 --end 2026-09-28
```

## Typical hunting workflow

1. **Verify identity** — run `whoami`
2. **Discover tables** — run `tables --days 7` to see what has data
3. **Inspect schema** — run `schema <table>` before writing a query; note the exact column names
4. **Hunt** — run `query` with your KQL, start with `--limit 100`, widen `--days` as needed or pin a specific range with `--start`/`--end`
5. **Export** — add `--export results.json` or `--export-format csv --export results.csv`

## Worked example — "what did a user visit recently?"

This shows the schema-first approach for any user-activity table.

**Step 1 — find candidate tables** (look for tables with web/network/proxy activity)
```bash
sentinel-kql --output json tables --days 7
# Parse the JSON, grep for keywords: web, proxy, url, http, network, dns
```

**Step 2 — inspect the schema of a promising table**
```bash
sentinel-kql --output json schema <TABLE>
# Identify: user identity column (e.g. SourceUserName, UserPrincipalName, InitiatedBy)
#           destination column  (e.g. DestinationHostName, RequestURL, Url, DestinationDomain)
#           timestamp column    (always TimeGenerated)
```

**Step 3 — hunt**
```bash
sentinel-kql --output table \
  query "<TABLE>
    | where TimeGenerated > ago(8h)
    | where <USER_COL> has '<username>'
    | summarize Visits=count() by <DEST_COL>
    | top 10 by Visits desc" \
  --days 1 --limit 0
```

**Step 4 — export if needed**
```bash
sentinel-kql --output csv --export user_visits.csv \
  query "<TABLE>
    | where TimeGenerated > ago(8h)
    | where <USER_COL> has '<username>'
    | project TimeGenerated, <DEST_COL>, <USER_COL>
    | sort by TimeGenerated desc" \
  --days 1 --limit 0
```

> Always read the schema first — column names differ between tables (Zscaler uses `SourceUserName`/`DestinationHostName`, AAD uses `UserPrincipalName`/`ResourceDisplayName`, etc.).

## Writing KQL for this tool

- Global flags (`--output`, `--export`, `--no-verify`) must come **before** the command name
- `| limit N` is appended automatically unless `--limit 0`; don't add it manually in the KQL
- `--days` / `--start`/`--end` set the API scan boundary (controls cost); use them as the primary time control — don't duplicate with `ago()` at the same window (e.g. `--days 7` + `ago(7d)` is redundant, `--days 1` + `ago(7d)` is wrong — the API wins). `ago()` inside KQL is fine only to **sub-filter within** the scan window (e.g. `--days 1` + `| where TimeGenerated > ago(1h)` to show just the last hour)
- Use `| project` to select only needed columns — avoids truncation in table output
- For aggregations (`summarize`, `top`), always use `--limit 0`

## Error signals

| Exit code | Meaning |
|---|---|
| 0 | Success |
| 1 | Auth failure, workspace not found, or KQL error |

Errors go to stderr; JSON/CSV output is clean stdout — safe to pipe.
