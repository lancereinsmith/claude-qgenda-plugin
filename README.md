# QGenda Claude Code Plugin

A Claude Code plugin for querying the QGenda scheduling system. Covers 15 read-only API endpoints including schedules, staff, open shifts, time-off requests, rotations, audit logs, and more.

## Install

### 1. Get your QGenda API credentials

Create `~/.qgenda.conf`:

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

### 2. Install the plugin

```bash
claude plugin marketplace add lancereinsmith/claude-qgenda-plugin
claude plugin install qgenda@claude-qgenda-plugin
```

That's it. Restart Claude Code and you're ready to go.

### Verify

```bash
claude plugin list    # should show qgenda
claude mcp list       # should show qgenda with 15 tools
```

### Update

```bash
claude plugin marketplace update claude-qgenda-plugin
claude plugin update qgenda@claude-qgenda-plugin
```

Restart Claude Code after updating.

## How to Use

### Invoke the skill explicitly

Type `/qgenda` followed by your question:

```text
/qgenda Who is working next Monday?
/qgenda Show me Dr. Smith's schedule for January
/qgenda What shifts need coverage this week?
/qgenda Who has requested time off in March?
/qgenda What rotation is Dr. Jones on?
```

### Just ask naturally

The skill auto-invokes for scheduling questions:

```text
"Who's on call this weekend?"
"What's my schedule next week?"
"Are there any open shifts I can pick up?"
"Who changed the Friday schedule?"
```

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

## Customizing the Skill

### Add practice-specific context

After installing, you can customize the skill by editing `SKILL.md` in your plugin directory. For example:

```markdown
## Practice Context

- Our company has 12 physicians
- Task "BR" means Breast Imaging, "CT1" means CT Reading Room 1
- Dr. Smith's last name in QGenda is "Smith-Jones"
```

### Prevent auto-invocation

If you want the skill to only activate when you explicitly type `/qgenda`, add this to the SKILL.md frontmatter:

```yaml
disable-model-invocation: true
```

## Alternative credential methods

Instead of a config file, you can use environment variables:

```bash
export QGENDA_EMAIL=your-api-username
export QGENDA_PASSWORD=your-api-password
export QGENDA_COMPANY_KEY=your-company-key
```

For a config file at a non-standard location:

```bash
export QGENDA_CONF_FILE=/path/to/your/qgenda.conf
```

## Alternative setup methods

Most users should use the plugin install above. These alternatives are for specific use cases.

### Claude Code (MCP server only, no skill)

```bash
claude mcp add qgenda \
  -e QGENDA_CONF_FILE=~/.qgenda.conf \
  -- uv run --directory ~/Maker/claude-qgenda-plugin mcp run server.py:mcp
```

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

### Docker

```bash
docker compose up -d              # Starts on port 8000 (SSE transport)
MCP_PORT=9000 docker compose up -d  # Custom port
```

Credentials are mounted from `~/.qgenda.conf` as a Docker secret.

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

See [INSTALL.md](INSTALL.md) for full details on all setup methods.

## Troubleshooting

| Error | Fix |
|-------|-----|
| "QGenda credentials not configured" | Place a config file at `~/.qgenda.conf`, set `QGENDA_CONF_FILE` to a custom path, or set all three env vars |
| "Config file not found" | Check the path in your `QGENDA_CONF_FILE` variable |
| "Partial QGenda env config" | You set some but not all of `QGENDA_EMAIL`, `QGENDA_PASSWORD`, `QGENDA_COMPANY_KEY` |
| "ModuleNotFoundError: qgendapy" | Run `uv sync` in the project directory |
| Authentication fails | Verify credentials in qgenda.conf or env vars |
| Claude Desktop doesn't show tools | Check paths in config, restart Desktop, check `~/Library/Logs/Claude/mcp*.log` |
| No data returned | Verify date range (max 100 days with compression, 31 without) and API user access |

---

## Development

Everything below is for contributors or anyone working on the plugin source code.

### Prerequisites

- **uv** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Python >= 3.11

### Getting started

```bash
cd ~/Maker/claude-qgenda-plugin
uv sync
uv run python scripts/qgenda_query.py staff          # test connection
uv run python scripts/qgenda_query.py staff --format table  # table output
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

### Running tests

```bash
just test
# or
uv run python -m pytest tests/ -v
```

42 tests covering: environment validation (config file, env vars, default fallback, partial config), OData builder (including `$expand`), response formatting, client caching, all 15 query functions (with parameter verification), and `includes` parameter forwarding.

### Architecture

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

All 15 endpoints use `qgendapy` resource methods (e.g., `client.schedule.list()`, `client.staff.get()`, `client.daily.rooms()`). Authentication and token refresh are handled automatically.

### The `includes` parameter

Several QGenda endpoints support an `includes` query parameter that inlines related entities in the response. This is QGenda-specific, not OData.

| Endpoint | `includes` values |
|----------|-------------------|
| Schedule | `StaffTags,TaskTags,LocationTags` |
| Open Shifts | `TaskTags,LocationTags` |
| Tasks | `Profiles,Tags,TaskShifts` |
| Staff Member (by ID) | `Skillset,Tags,Profiles` |
| Daily Cases | `Task,Supervisors,DirectProviders` |
| Patient Encounters | `StandardFields,PatientInformation` |
| Request Limits | `ShiftCredit,StaffLimits` |

### Project structure

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
  test_core.py              # Unit tests
package/
  install.sh                # Self-contained installer for tarball distribution
spec/
  QGenda REST API.pdf       # Original 309-page API specification
justfile                    # deps, test, hooks, install, package
CLAUDE.md                   # Project conventions for Claude
INSTALL.md                  # Setup for Claude Code, Desktop, Docker, packaging
```
