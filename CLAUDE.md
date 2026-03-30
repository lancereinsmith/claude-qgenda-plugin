# QGenda Claude Skill

## Overview

This project provides a read-only QGenda scheduling integration for Claude through two interfaces:

- **Claude Code Plugin/Skill** — `skills/qgenda/SKILL.md` + `scripts/qgenda_query.py` (plugin structure with `.claude-plugin/plugin.json`)
- **Claude Desktop MCP Server** — `server.py` via FastMCP

Both share core logic in `qgenda_core.py`. The project covers 15 QGenda REST API endpoints spanning schedules, staff, tasks, requests, rotations, audit logs, daily operations, and patient encounters.

## Architecture

```text
qgenda_core.py                      ← Shared: client, OData, formatting, 15 query functions
├── server.py                        ← MCP server (15 tools, thin wrappers over core)
└── scripts/qgenda_query.py          ← CLI script (15 subcommands, thin wrappers with argparse)
```

### How the layers connect

1. **`qgenda_core.py`** contains ALL business logic: client initialization, OData query building, response formatting, and one `query_*()` function per API endpoint. It uses `qgendapy` for all API access — authentication and token refresh are handled automatically.

2. **`server.py`** (MCP) and **`scripts/qgenda_query.py`** (CLI) are thin wrappers — they accept user input, call the matching `core.query_*()` function, and return/print the result. They contain no query logic themselves.

3. All 15 endpoints use `qgendapy` resource methods (e.g., `client.schedule.list()`, `client.staff.get()`, `client.daily.rooms()`).

## Endpoints covered

| # | Endpoint | API Path | Core Function | CLI Command | MCP Tool |
|---|----------|----------|---------------|-------------|----------|
| 1 | Schedule | `GET /schedule` | `query_schedule()` | `schedule` | `get_schedule` |
| 2 | Staff list | `GET /staffmember` | `query_staff()` | `staff` | `get_staff` |
| 3 | Staff with tags | `GET /staffmember` (w/ includes) | `query_staff_with_tags()` | `staff-tags` | `get_staff_tags` |
| 4 | Tasks | `GET /task` | `query_tasks()` | `tasks` | `get_tasks` |
| 5 | Facilities | `GET /facility` | `query_facilities()` | `facilities` | `get_facilities` |
| 6 | Time events | `GET /timeevent` | `query_time_events()` | `timeevent` | `get_time_events` |
| 7 | Daily cases | `GET /dailycase` | `query_daily_cases()` | `dailycase` | `get_daily_cases` |
| 8 | Open shifts | `GET /schedule/openshifts` | `query_open_shifts()` | `openshifts` | `get_open_shifts` |
| 9 | Requests (PTO/swaps) | `GET /request` | `query_requests()` | `requests` | `get_requests` |
| 10 | Rotations | `GET /schedule/rotations` | `query_rotations()` | `rotations` | `get_rotations` |
| 11 | Schedule audit log | `GET /schedule/auditLog` | `query_schedule_audit_log()` | `auditlog` | `get_schedule_audit_log` |
| 12 | Staff member by ID | `GET /staffmember/:id` | `query_staff_member()` | `staff-detail` | `get_staff_member` |
| 13 | Daily configuration | `GET /daily/dailyconfiguration` | `query_daily_configuration()` | `dailyconfig` | `get_daily_configuration` |
| 14 | Rooms | `GET /daily/room` | `query_rooms()` | `rooms` | `get_rooms` |
| 15 | Patient encounters | `GET /daily/patientencounter` | `query_patient_encounters()` | `encounters` | `get_patient_encounters` |

## Key conventions

- Python >=3.11, managed with `uv`
- All API query logic lives in `qgenda_core.py` — server.py and the CLI script are thin wrappers
- Credentials: config file (default `~/.qgenda.conf`, override with `QGENDA_CONF_FILE` env var) or individual env vars (`QGENDA_EMAIL`, `QGENDA_PASSWORD`, `QGENDA_COMPANY_KEY`)
- The `qgendapy` client handles token refresh automatically
- Default `$select` fields are defined in `qgenda_core.DEFAULT_SELECT` to keep responses concise
- Error handling: API/auth failures return human-readable error messages, never raw tracebacks
- Output formats: json (default), table, csv — controlled via `--format` flag in CLI
- Read-only: no POST/PUT/DELETE endpoints are exposed — the skill is safe to use without risk of modifying data

### OData and `includes`

- All endpoints support OData query params: `$select`, `$filter`, `$orderby`, `$expand`
- The `build_odata()` helper constructs these from function arguments
- Several endpoints also support an `includes` query parameter (NOT OData) that returns related entities inline:
  - Schedule: `StaffTags,TaskTags,LocationTags`
  - Open Shifts: `TaskTags,LocationTags`
  - Tasks: `Profiles,Tags,TaskShifts`
  - Staff Member (by ID): `Skillset,Tags,Profiles`
  - Daily Cases: `Task,Supervisors,DirectProviders`
  - Patient Encounters: `StandardFields,PatientInformation`

## Running tests

```bash
uv run python -m pytest tests/
```

42 tests covering: environment validation, OData builder (including `$expand`), response formatting, client caching, all 15 query functions, and `includes` parameter forwarding.

## Development

```bash
uv sync                                          # Install dependencies
uv run python scripts/qgenda_query.py staff      # Test CLI
uv run python scripts/qgenda_query.py --help     # See all 15 subcommands
uv run python server.py                          # Run MCP server (logs tools to stderr on startup)
```

### Registering the MCP server with Claude Code

```bash
claude mcp add qgenda \
  -e QGENDA_CONF_FILE=~/.qgenda.conf \
  -- uv run --directory ~/Maker/claude-qgenda-plugin mcp run server.py:mcp
```

See [INSTALL.md](INSTALL.md) for Claude Desktop configuration and Docker setup.

## File reference

| File | Purpose |
|------|---------|
| `qgenda_core.py` | Shared client, OData builder, formatters, 15 query functions |
| `server.py` | MCP server — 15 `@mcp.tool()` functions wrapping core |
| `scripts/qgenda_query.py` | CLI helper — 15 argparse subcommands wrapping core |
| `.claude-plugin/plugin.json` | Plugin manifest (name, version, MCP config) for Claude Code plugin distribution |
| `.mcp.json` | MCP server configuration (referenced by plugin.json) |
| `git-hooks/pre-commit` | Git hook — syncs pyproject.toml version to plugin.json on commit |
| `skills/qgenda/SKILL.md` | Skill definition (instructions, examples, method reference) — canonical location |
| `skills/qgenda/references/` | API reference docs loaded on demand by the skill |
| `skills/qgenda/scripts/` | Symlinks to `qgenda_query.py` and `qgenda_core.py` scoped to the skill |
| `.claude/skills/qgenda` | Symlink → `skills/qgenda/` so Claude Code discovers the skill locally without burying files in a hidden directory |
| `tests/test_core.py` | 37 unit tests for core logic |
| `justfile` | `install`, `package`, `sync-scripts`, `test` recipes |
| `package/install.sh` | Self-contained install script bundled into distributable tarballs |
| `Dockerfile` | Container image for running the MCP server with SSE transport |
| `docker-compose.yml` | Docker Compose config — mounts credentials as secret, configurable port via `MCP_PORT` |
| `spec/QGenda REST API.pdf` | Original 309-page QGenda API specification (source of truth) |
