#!/usr/bin/env python3
"""Entry-point shim — delegates to the sentinel_kql package."""

from sentinel_kql.cli import cli

if __name__ == "__main__":
    cli()
