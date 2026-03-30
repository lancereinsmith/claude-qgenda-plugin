# Installation Guide

This project provides a QGenda scheduling integration that works
with both **Claude Code** (CLI) and the **Claude Desktop** app.
It exposes 15 read-only QGenda API endpoints covering schedules,
staff, open shifts, requests, rotations, audit logs, and more.

## Prerequisites

### 1. Install uv (if you don't have it)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone this project

```bash
git clone <repo-url> ~/Maker/claude-qgenda-plugin
cd ~/Maker/claude-qgenda-plugin
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Configure QGenda credentials

Choose one of the following methods:

#### Option A: Config file (recommended)

Create `~/.qgenda.conf` with your credentials:

```bash
touch ~/.qgenda.conf
chmod 600 ~/.qgenda.conf
```

Edit `~/.qgenda.conf`:

```ini
[qgenda]
company_key = YOUR-COMPANY-KEY
username = YOUR-API-USERNAME
password = YOUR-API-PASSWORD
api_url = https://api.qgenda.com/
api_version = v2
```

The MCP server automatically discovers `~/.qgenda.conf` — no
environment variable is needed if your file is at this default path.

For a **non-standard location**, set the path explicitly:

```bash
echo 'export QGENDA_CONF_FILE=/path/to/your/qgenda.conf' >> ~/.zshrc
source ~/.zshrc
```

Or with `direnv`:

```bash
echo 'export QGENDA_CONF_FILE=$HOME/.qgenda.conf' >> .envrc
direnv allow
```

#### Option B: Environment variables

Instead of a config file, set these three variables:

```bash
export QGENDA_EMAIL=your-api-username
export QGENDA_PASSWORD=your-api-password
export QGENDA_COMPANY_KEY=your-company-key
```

Add them to `~/.zshrc` or `~/.bashrc` to make them permanent.
All three must be set — partial configuration will produce an error.

#### Credential priority

When multiple methods are configured, this priority applies:

1. `QGENDA_CONF_FILE` environment variable (explicit path)
2. `QGENDA_EMAIL` + `QGENDA_PASSWORD` + `QGENDA_COMPANY_KEY` env vars
3. `~/.qgenda.conf` (default location, auto-discovered)

### 5. Test the connection

```bash
uv run python scripts/qgenda_query.py staff
```

If this prints JSON with staff data, your credentials are working.

---

## Claude Code (CLI)

The skill is automatically available when you run Claude Code
from this project directory (it reads `.claude/skills/qgenda/`).

### Verify

1. Start Claude Code in this directory:

   ```bash
   cd ~/Maker/claude-qgenda-plugin
   claude
   ```

2. Type `/` and look for `qgenda` in the list
3. Try: `/qgenda Who is working tomorrow?`

### Use from any project — Plugin (recommended)

This repo is structured as a **Claude Code plugin**. The plugin
includes both the `/qgenda` skill and the MCP server (15 tools)
in a single install.

**Install from GitHub (permanent):**

```bash
# Step 1: Add the repo as a plugin marketplace
claude plugin marketplace add lancereinsmith/claude-qgenda-plugin

# Step 2: Install the plugin
claude plugin install qgenda@claude-qgenda-plugin
```

If your credentials are at `~/.qgenda.conf`, the MCP server
finds them automatically — no configuration needed. For a
non-standard path, set `QGENDA_CONF_FILE` in your shell profile.
You can also use environment variables instead of a config file
(see step 4 above).

**Update to the latest version:**

```bash
claude plugin marketplace update claude-qgenda-plugin   # refresh marketplace cache
claude plugin update qgenda@claude-qgenda-plugin         # update the plugin
```

Restart Claude Code after updating for changes to take effect.

**Load from a local path (per-session, for testing):**

```bash
claude --plugin-dir /path/to/claude-qgenda-plugin
```

When installed as a plugin, the skill is namespaced:
`/qgenda:qgenda` (or just `/qgenda` if unambiguous).

> **Note:** Plugins are Claude Code only. Claude Desktop does not
> support plugins — see the MCP Server section below for Desktop setup.

### Use from any project — Manual install

Alternatively, copy the skill to your personal skills directory:

```bash
just install
```

This copies skill files to `~/.claude/skills/qgenda/` and rewrites
script paths to absolute paths. To uninstall: `just uninstall`.

### Install from a tarball (no git clone needed)

If someone gives you a `qgenda-skill-X.Y.Z.tar.gz` file:

```bash
tar xzf qgenda-skill-0.1.1.tar.gz
cd qgenda-skill
./install.sh
```

The install script copies files to `~/.claude/skills/qgenda/`,
rewrites paths, and installs Python dependencies.

---

## Packaging and Distribution

### Plugin distribution (recommended)

This repo is a Claude Code plugin. The plugin structure:

```text
claude-qgenda-plugin/
├── .claude-plugin/
│   └── plugin.json            ← plugin manifest (name, version, MCP config)
├── skills/
│   └── qgenda/
│       ├── SKILL.md           ← skill definition (always loaded)
│       ├── references/
│       │   └── api-reference.md  ← loaded on demand
│       └── scripts/
│           ├── qgenda_query.py   ← executed by Claude when needed
│           └── qgenda_core.py    ← shared core logic
├── .claude/
│   └── skills/
│       └── qgenda -> ../../skills/qgenda  ← symlink for local dev
├── server.py                  ← MCP server (separate from plugin)
└── ...
```

To distribute as a plugin, push to GitHub. Users install with:

```bash
claude plugin marketplace add lancereinsmith/claude-qgenda-plugin
claude plugin install qgenda@claude-qgenda-plugin
```

Or test locally:

```bash
claude --plugin-dir /path/to/claude-qgenda-plugin
```

### Tarball distribution (alternative)

For environments without GitHub access, create a tarball:

```bash
just package
```

This produces `dist/qgenda-skill-X.Y.Z.tar.gz` containing the
skill files and a self-contained install script.


### How to manually package (without just)

If you don't have `just` installed:

```bash
# 1. Sync scripts into the skill directory
cp scripts/qgenda_query.py .claude/skills/qgenda/scripts/
cp qgenda_core.py .claude/skills/qgenda/scripts/

# 2. Create the package directory
mkdir -p dist/qgenda-skill/references dist/qgenda-skill/scripts

# 3. Copy files
cp .claude/skills/qgenda/SKILL.md dist/qgenda-skill/
cp .claude/skills/qgenda/references/api-reference.md dist/qgenda-skill/references/
cp .claude/skills/qgenda/scripts/qgenda_query.py dist/qgenda-skill/scripts/
cp .claude/skills/qgenda/scripts/qgenda_core.py dist/qgenda-skill/scripts/
cp package/install.sh dist/qgenda-skill/
chmod +x dist/qgenda-skill/install.sh

# 4. Create the tarball
cd dist && tar czf qgenda-skill.tar.gz qgenda-skill/

# 5. Clean up
rm -rf dist/qgenda-skill
```

The resulting `dist/qgenda-skill.tar.gz` is the distributable package.

---

## MCP Server

The project includes an MCP server (`server.py`) that exposes all
15 QGenda endpoints as tools. If you installed the plugin above,
the MCP server is already included — no additional setup needed
for Claude Code. Claude Desktop requires manual configuration.

### Running the MCP server locally (for testing)

```bash
cd ~/Maker/claude-qgenda-plugin
uv run python server.py
```

On startup you'll see output like:

```
2026-03-18 14:19:52 [qgenda-mcp] QGenda MCP server starting — 15 tools registered
2026-03-18 14:19:52 [qgenda-mcp] Tools: get_schedule, get_staff, get_staff_tags, ...
2026-03-18 14:19:52 [qgenda-mcp] Credentials file: /Users/you/.qgenda.conf
```

You can also run it via the `mcp` CLI:

```bash
uv run mcp run server.py:mcp
```

> **Note:** MCP servers communicate over stdio. The startup log
> goes to stderr so you can see it, but the server itself will
> appear to "hang" — that's normal, it's waiting for MCP protocol
> messages from a client (Claude Code or Claude Desktop).

### Configure Claude Code to use the MCP server (without plugin)

If you did not install the plugin, you can register the MCP server
manually so its tools are available in every conversation:

```bash
# From the project directory:
claude mcp add qgenda \
  -e QGENDA_CONF_FILE=~/.qgenda.conf \
  -- uv run --directory ~/Maker/claude-qgenda-plugin mcp run server.py:mcp
```

This stores the configuration in your Claude Code settings. To
verify it was added:

```bash
claude mcp list
```

To remove it later:

```bash
claude mcp remove qgenda
```

### Configure Claude Desktop to use the MCP server

1. Open Claude Desktop settings:
   - macOS: **Claude > Settings > Developer > Edit Config**
   - Or edit directly: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the QGenda MCP server to your config:

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

> **Important:** Replace the paths above with your actual paths.
> `--directory` must point to where you cloned this project.
> `QGENDA_CONF_FILE` must point to your credentials file.

3. Restart Claude Desktop (quit and reopen).

### Verify (Claude Desktop)

After restarting, you should see a hammer icon in the Claude
Desktop chat input area. Click it to confirm the QGenda tools
are listed.

Try asking: "Who is working today?" or "Are there any open shifts this week?"

### Available MCP tools

All 15 tools are available in Claude Desktop. Tools that support
it accept `includes` for related entity expansion and standard
OData parameters (`select`, `filter`, `orderby`, `expand`).

**Scheduling:**

| Tool | Description |
|------|-------------|
| `get_schedule` | Schedule entries for a date range (defaults to today) |
| `get_open_shifts` | Open/unfilled shifts needing coverage |
| `get_rotations` | Rotation schedule assignments |
| `get_schedule_audit_log` | Who changed what on the schedule |

**Staff:**

| Tool | Description |
|------|-------------|
| `get_staff` | Staff / provider list |
| `get_staff_tags` | Staff with tags (sub-specialties, skill sets) |
| `get_staff_member` | Single staff member detail (by ID, with skillset/tags/profiles) |

**Requests:**

| Tool | Description |
|------|-------------|
| `get_requests` | Time-off and swap requests |

**Tasks & Facilities:**

| Tool | Description |
|------|-------------|
| `get_tasks` | Task definitions (shift types, with profiles/tags/taskshifts) |
| `get_facilities` | Facility list |

**Time & Cases:**

| Tool | Description |
|------|-------------|
| `get_time_events` | Time event entries |
| `get_daily_cases` | Daily case information |

**Daily Operations (Capacity Management):**

| Tool | Description |
|------|-------------|
| `get_daily_configuration` | Daily configurations (capacity setup) |
| `get_rooms` | Room list for the company |
| `get_patient_encounters` | Patient encounter data for a daily config |

---

## Docker

Run the MCP server in a Docker container with SSE transport.

### Quick start

```bash
docker compose up -d
```

This builds the image and starts the server on port 8000 (SSE transport).
Credentials are mounted as a Docker secret from `~/.qgenda.conf`.

### Custom port

Set `MCP_PORT` in a `.env` file or pass it directly:

```bash
# Via .env file
echo "MCP_PORT=9000" >> .env
docker compose up -d

# Or inline
MCP_PORT=9000 docker compose up -d
```

### Custom credentials path

If your `qgenda.conf` is not at `~/.qgenda.conf`:

```bash
QGENDA_CONF_FILE=/path/to/qgenda.conf docker compose up -d
```

### Connecting to the Docker MCP server

Point Claude Desktop to the SSE endpoint:

```json
{
  "mcpServers": {
    "qgenda": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### View logs

```bash
docker compose logs -f qgenda-mcp
```

### Stop

```bash
docker compose down
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| "QGenda credentials not configured" | Either place a config file at `~/.qgenda.conf`, set `QGENDA_CONF_FILE` to a custom path, or set `QGENDA_EMAIL`, `QGENDA_PASSWORD`, and `QGENDA_COMPANY_KEY` env vars. See step 4 above. |
| "Config file not found" | Check the path in your `QGENDA_CONF_FILE` variable — the file doesn't exist at that location |
| "Partial QGenda env config" | You set some but not all of `QGENDA_EMAIL`, `QGENDA_PASSWORD`, `QGENDA_COMPANY_KEY` — set all three or use a config file instead |
| "ModuleNotFoundError: qgendapy" | Run `uv sync` in the project directory |
| Authentication error | Check credentials in your config file or env vars |
| Claude Desktop doesn't show tools | Check the path in `--directory` is correct, restart Claude Desktop, and check `~/Library/Logs/Claude/mcp*.log` for errors |
| No data returned | Verify your date range (max 100 days with compression, 31 without) and that your API user has access to the requested data |
| "401 Unauthorized" | Credentials may be wrong or expired — update your config file or env vars. Token refresh is automatic. |
