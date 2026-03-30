# QGenda Claude Code Skill

A Claude Code skill and MCP server for querying the QGenda scheduling system. Covers 15 read-only API endpoints including schedules, staff, open shifts, time-off requests, rotations, audit logs, and more.

## What This Does

When you type `/qgenda` in Claude Code (or just ask a scheduling question), Claude gains knowledge of the QGenda REST API and can query your scheduling data on your behalf. It also ships an MCP server for Claude Desktop — see [INSTALL.md](INSTALL.md) for setup.

### Supported queries

| Category | What you can ask |
|----------|-----------------|
| **Schedules** | Who is working today? What's Dr. Smith's schedule next week? |
| **Open shifts** | What shifts need coverage? Are there any unfilled shifts this week? |
| **Staff** | List all staff members. Who has the "Neuro Lite" sub-specialty? |
| **Staff detail** | Show me everything about Dr. Jones (tags, skillset, profiles). |
| **Requests** | Who has requested time off next month? Any pending swap requests? |
| **Rotations** | What rotation is Dr. Smith on? Show rotations for Q1. |
| **Audit log** | Who changed the schedule for last Monday? |
| **Tasks** | What shift types exist? Show task details with profiles. |
| **Facilities** | List all facilities. |
| **Time events** | What time events are logged for today? |
| **Daily cases** | Show daily cases for this week. |
| **Daily config** | List daily configurations. |
| **Rooms** | What rooms are available? |
| **Patient encounters** | Show encounters for a given daily config and date. |

## Prerequisites

1. **uv** (Python package manager):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **QGenda API credentials** — choose one of these methods:

   **Option A: Config file (recommended)**

   Create `~/.qgenda.conf` with your credentials:

   ```ini
   [qgenda]
   company_key = YOUR-COMPANY-KEY
   username = YOUR-API-USERNAME
   password = YOUR-API-PASSWORD
   api_url = https://api.qgenda.com/
   api_version = v2
   ```

   ```bash
   chmod 600 ~/.qgenda.conf
   ```

   The MCP server automatically looks for `~/.qgenda.conf` — no environment variable needed if your file is at that path. For a non-standard location, set:

   ```bash
   export QGENDA_CONF_FILE=/path/to/your/qgenda.conf
   ```

   **Option B: Environment variables**

   Set these three variables instead of using a config file:

   ```bash
   export QGENDA_EMAIL=your-api-username
   export QGENDA_PASSWORD=your-api-password
   export QGENDA_COMPANY_KEY=your-company-key
   ```

   Add any of these to `~/.zshrc` or `~/.bashrc` to make them permanent.

## Quick Start

```bash
cd ~/Maker/claude-qgenda-plugin
uv sync
uv run python scripts/qgenda_query.py staff          # test connection
uv run python scripts/qgenda_query.py staff --format table  # table output
claude                                                # start Claude Code
```

## Project Structure

```text
qgenda_core.py              # Shared logic: qgendapy client, OData, formatting, 15 query functions
server.py                   # MCP server for Claude Desktop (15 tools)
scripts/
  qgenda_query.py           # CLI helper script (15 subcommands)
.claude-plugin/
  plugin.json               # Plugin manifest (name, version, MCP config)
.mcp.json                   # MCP server configuration (referenced by plugin.json)
skills/
  qgenda/                   # Plugin skill directory (canonical location)
    SKILL.md                # Skill definition — teaches Claude the QGenda API
    references/
      api-reference.md      # Comprehensive API endpoint reference
    scripts/                # Symlinks to scripts scoped to the skill
.claude/
  skills/
    qgenda -> ../../skills/qgenda  # Symlink so Claude Code discovers the skill locally
git-hooks/
  pre-commit                # Syncs pyproject.toml version to plugin.json
tests/
  test_core.py              # 37 unit tests
package/
  install.sh                # Self-contained installer for tarball distribution
spec/
  QGenda REST API.pdf       # Original 309-page API specification
justfile                    # deps, test, hooks, install, package
CLAUDE.md                   # Project conventions for Claude
INSTALL.md                  # Setup for Claude Code, Desktop, Docker, packaging
```

> **Why the symlink?** Claude Code discovers project-scoped skills from `.claude/skills/`, but burying the canonical skill files in a hidden directory makes them hard to find when browsing the repo. The symlink at `.claude/skills/qgenda` points to `skills/qgenda/` so the files stay visible at the repo root while still being discoverable during local development. When distributed as a plugin, only `skills/qgenda/` is used.

## Setup

### Claude Code (plugin — recommended)

The plugin includes both the `/qgenda` skill and the MCP server (15 tools). Install once to get everything:

```bash
# Install from GitHub (permanent)
claude plugin marketplace add lancereinsmith/claude-qgenda-plugin
claude plugin install qgenda@claude-qgenda-plugin

# Or load from a local path (per-session, for testing)
claude --plugin-dir /path/to/claude-qgenda-plugin
```

If your credentials are at `~/.qgenda.conf`, the MCP server finds them automatically — no configuration needed.

Verify: `claude plugin list` and `claude mcp list`

### Claude Code (MCP server only — manual)

If you prefer not to use the plugin, you can register the MCP server directly:

```bash
claude mcp add qgenda \
  -e QGENDA_CONF_FILE=~/.qgenda.conf \
  -- uv run --directory ~/Maker/claude-qgenda-plugin mcp run server.py:mcp
```

This gives you the 15 MCP tools but not the `/qgenda` skill.

### Claude Desktop

Claude Desktop does not support plugins. Add the MCP server manually to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "qgenda": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/claude-qgenda-plugin",
        "mcp", "run", "server.py:mcp"
      ],
      "env": {
        "QGENDA_CONF_FILE": "/path/to/.qgenda.conf"
      }
    }
  }
}
```

Then restart Claude Desktop.

### Run locally (for testing)

```bash
uv run python server.py
```

You'll see startup confirmation on stderr:

```
2026-03-18 14:19:52 [qgenda-mcp] QGenda MCP server starting — 15 tools registered
2026-03-18 14:19:52 [qgenda-mcp] Tools: get_schedule, get_staff, get_staff_tags, ...
2026-03-18 14:19:52 [qgenda-mcp] Credentials file: /Users/you/.qgenda.conf
```

### Run with Docker

```bash
docker compose up -d              # Starts on port 8000 (SSE transport)
MCP_PORT=9000 docker compose up -d  # Custom port
```

Credentials are mounted from `~/.qgenda.conf` as a Docker secret. Override with `QGENDA_CONF_FILE=/path/to/conf docker compose up -d`.

See [INSTALL.md](INSTALL.md) for detailed setup instructions.

## How to Use

### Invoke the skill explicitly

Type `/qgenda` in Claude Code followed by your question:

```text
/qgenda Who is working next Monday?
/qgenda Show me Dr. Smith's schedule for January
/qgenda What shifts need coverage this week?
/qgenda Who has requested time off in March?
/qgenda What rotation is Dr. Jones on?
```

### Just ask naturally

The skill's description tells Claude when to auto-invoke. Simply ask scheduling questions:

```text
"Who's on call this weekend?"
"What's my schedule next week?"
"Are there any open shifts I can pick up?"
"Who changed the Friday schedule?"
```

### CLI script

The helper script supports JSON (default), table, and CSV output across all 15 subcommands:

```bash
# Schedules
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --end 2025-01-31
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --includes StaffTags,TaskTags
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --filter "StaffLName eq 'Smith'"

# Open shifts
uv run python scripts/qgenda_query.py openshifts --start 2025-01-01 --end 2025-01-31

# Staff
uv run python scripts/qgenda_query.py staff --format table
uv run python scripts/qgenda_query.py staff-tags --tag-category "Sub Specialty" --tag-name "Neuro Lite"
uv run python scripts/qgenda_query.py staff-detail --staff-id <GUID> --includes Skillset,Tags,Profiles

# Requests, rotations, audit log
uv run python scripts/qgenda_query.py requests --start 2025-01-01 --end 2025-01-31
uv run python scripts/qgenda_query.py rotations --range-start 2025-01-01 --range-end 2025-03-31
uv run python scripts/qgenda_query.py auditlog --start 2025-01-01 --end 2025-01-31

# Tasks with related entities
uv run python scripts/qgenda_query.py tasks --includes Profiles,Tags,TaskShifts

# Daily operations
uv run python scripts/qgenda_query.py dailyconfig
uv run python scripts/qgenda_query.py rooms
uv run python scripts/qgenda_query.py encounters --daily-config-key <GUID> --start 2025-01-01

# Other
uv run python scripts/qgenda_query.py facilities
uv run python scripts/qgenda_query.py timeevent --start 2025-01-01
uv run python scripts/qgenda_query.py dailycase --start 2025-01-01

# Output formats
uv run python scripts/qgenda_query.py staff --format table
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --format csv > schedule.csv
```

## Architecture

### Three-layer design

```text
                  ┌──────────────┐     ┌────────────────────────┐
User ─── Claude ──┤  server.py   │     │ scripts/qgenda_query.py│
                  │ (MCP tools)  │     │ (CLI subcommands)      │
                  └──────┬───────┘     └───────────┬────────────┘
                         │                         │
                         ▼                         ▼
                  ┌─────────────────────────────────────────┐
                  │           qgenda_core.py                │
                  │                                         │
                  │  get_client()     ← qgendapy (auto auth)│
                  │  build_odata()    ← $select/$filter/…   │
                  │  format_response()← json/table/csv      │
                  │  query_*()        ← 15 endpoint funcs   │
                  └──────────┬──────────────────────────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │  QGenda REST API   │
                  │  api.qgenda.com/v2 │
                  └────────────────────┘
```

### How API calls work

All 15 endpoints use `qgendapy` resource methods (e.g., `client.schedule.list()`, `client.staff.get()`, `client.daily.rooms()`). Authentication and token refresh are handled automatically by the library.

### The `includes` parameter

Several QGenda endpoints support an `includes` query parameter that inlines related entities in the response. This is different from OData `$expand` — it's a QGenda-specific feature. Without it, you'd need multiple API calls to get related data (e.g., a staff member's tags, a task's profiles).

Available `includes` values per endpoint:

| Endpoint | `includes` values |
|----------|-------------------|
| Schedule | `StaffTags,TaskTags,LocationTags` |
| Open Shifts | `TaskTags,LocationTags` |
| Tasks | `Profiles,Tags,TaskShifts` |
| Staff Member (by ID) | `Skillset,Tags,Profiles` |
| Daily Cases | `Task,Supervisors,DirectProviders` |
| Patient Encounters | `StandardFields,PatientInformation` |
| Request Limits | `ShiftCredit,StaffLimits` |

## How the Skill Works

1. **SKILL.md** provides Claude with instructions on how to use the helper script, what endpoints are available, how OData filtering works, what `includes` values exist, and how to format results.

2. **api-reference.md** gives Claude detailed API documentation so it can construct the right queries — all parameters, types, required/optional status, and available related entities.

3. **qgenda_core.py** contains all shared logic — qgendapy client, OData building, response formatting, and query functions.

4. **qgenda_query.py** and **server.py** are thin wrappers around the core.

When you ask a question, Claude will:

- Determine the right API endpoint and parameters
- Run the helper script (or write custom Python for complex queries)
- Parse the JSON response
- Present results in a readable format

## Customizing the Skill

### Change what Claude knows

Edit `.claude/skills/qgenda/SKILL.md` to:

- Add practice-specific terminology (e.g., map task names to plain English like "MRI Reading" -> "MRI")
- Add default filters (e.g., always filter to your specific staff group)
- Change the default date behavior
- Add new query patterns

### Add practice-specific context

You can add details about your practice to the SKILL.md. For example:

```markdown
## Practice Context

- Our company has 12 physicians
- Task "BR" means Breast Imaging, "CT1" means CT Reading Room 1
- Dr. Smith's last name in QGenda is "Smith-Jones"
```

### Extend the helper script

Edit `scripts/qgenda_query.py` to add new subcommands or change output formatting. The script delegates to `qgenda_core.py` which handles authentication, caching, and API calls.

### Prevent auto-invocation

If you want the skill to only activate when you explicitly type `/qgenda`, add this to the SKILL.md frontmatter:

```yaml
disable-model-invocation: true
```

## Distribution

### As a plugin (recommended)

This repo is structured as a **Claude Code plugin** with a
`.claude-plugin/plugin.json` manifest, `skills/` directory, and
built-in MCP server. Installing the plugin gives you both the
`/qgenda` skill and the 15 MCP tools in one step.

**Install from GitHub:**

```bash
claude plugin marketplace add lancereinsmith/claude-qgenda-plugin
claude plugin install qgenda@claude-qgenda-plugin
```

**Update to the latest version:**

```bash
claude plugin marketplace update claude-qgenda-plugin   # refresh marketplace cache
claude plugin update qgenda@claude-qgenda-plugin         # update the plugin
```

Restart Claude Code after updating for changes to take effect.

**Test locally:**

```bash
claude --plugin-dir /path/to/claude-qgenda-plugin
```

### Manual install to personal skills

```bash
just install       # copies to ~/.claude/skills/qgenda/
just uninstall     # removes it
```

### As a tarball

For environments without GitHub access:

```bash
just package       # creates dist/qgenda-skill-X.Y.Z.tar.gz
```

Recipient installs with:

```bash
tar xzf qgenda-skill-<version>.tar.gz
cd qgenda-skill && ./install.sh
```

See [INSTALL.md](INSTALL.md) for full details on all distribution methods.

## Running Tests

```bash
just test
# or
uv run python -m pytest tests/ -v
```

42 tests covering: environment validation (config file, env vars, default fallback, partial config), OData builder (including `$expand`), response formatting, client caching, all 15 query functions (with parameter verification), and `includes` parameter forwarding.

## Troubleshooting

| Error | Fix |
|-------|-----|
| "QGenda credentials not configured" | Either place a config file at `~/.qgenda.conf`, set `QGENDA_CONF_FILE` to a custom path, or set `QGENDA_EMAIL`, `QGENDA_PASSWORD`, and `QGENDA_COMPANY_KEY` env vars |
| "Config file not found" | Check the path in your `QGENDA_CONF_FILE` variable |
| "Partial QGenda env config" | You set some but not all of the three env vars (`QGENDA_EMAIL`, `QGENDA_PASSWORD`, `QGENDA_COMPANY_KEY`) — set all three or use a config file instead |
| "ModuleNotFoundError: qgendapy" | Run `uv sync` in the project directory |
| Authentication fails | Verify your username, password, and company_key in qgenda.conf or env vars |
| Claude Desktop doesn't show tools | Check paths in config, restart Desktop, check `~/Library/Logs/Claude/mcp*.log` |
| No data returned | Verify date range (max 100 days with compression, 31 without) and that your API user has access |
