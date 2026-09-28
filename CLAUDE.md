the goal of this project is to create a simple CLI tool that allow someone who is authenticated via `az login` to do some hunting queries via command line and get results.

the tool must have functions like getschema for a table, get list of tables, launch hunting query and so on.

the tool must be usable by a human being so the information displayed must nice, ability to export to json / to csv.

Note: this tool will be used in an LLM skill, so a skill must be available too.

Goal of the tool: since it is difficult to make an MCP out of this, a CLI tool with a skill is better. This will help any analyst to perform hunting queries from the CLI.

use a .env

smoke test everything

fill the requirements.txt

fill the README

use Microsoft auth lib