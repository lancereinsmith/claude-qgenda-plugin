---
name: qgenda
description: Query QGenda scheduling system for physician schedules, staff info, tasks, and facilities. Use when the user asks about schedules, availability, shifts, who is working, or anything related to QGenda.
argument-hint: query about schedules, availability, staff, etc.
---

You are helping a physician query their QGenda scheduling system. Use the MCP tools (preferred) or the helper script to answer their questions.

## Authentication

Authentication is handled automatically. The MCP server resolves credentials in this order:
1. **`QGENDA_CONF_FILE`** — config file path set via plugin config or environment variable
2. **Environment variables** — `QGENDA_EMAIL`, `QGENDA_PASSWORD`, and `QGENDA_COMPANY_KEY`
3. **Default location** — `~/.qgenda.conf` (auto-discovered)

If the QGenda MCP tools are available, authentication is already working — go straight to answering the user's question. Do not run setup checks or ask about credentials.

Only if a QGenda MCP tool call fails with an authentication or configuration error, ask the user to check their config file path or environment variables.

## Helper Script

A helper script exists at `scripts/qgenda_query.py` in this project. Use it for common operations.
Always run with `uv run` to ensure dependencies are available. Use `--format table` for readable output.

```bash
# Get schedule for a date range
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --end 2025-01-31

# Get schedule with related entities (tags)
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --includes StaffTags,TaskTags

# Get schedule filtered by provider last name
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --filter "StaffLName eq 'Smith'"

# List all staff members
uv run python scripts/qgenda_query.py staff

# List staff with tags (sub-specialties, skill sets)
uv run python scripts/qgenda_query.py staff-tags --tag-category "Sub Specialty" --tag-name "Neuro Lite"

# Get detailed info for a single staff member
uv run python scripts/qgenda_query.py staff-detail --staff-id <GUID> --includes Skillset,Tags,Profiles

# List tasks with related entities
uv run python scripts/qgenda_query.py tasks --includes Profiles,Tags,TaskShifts

# List facilities
uv run python scripts/qgenda_query.py facilities

# Get open (unfilled) shifts
uv run python scripts/qgenda_query.py openshifts --start 2025-01-01 --end 2025-01-31

# Get time-off and swap requests
uv run python scripts/qgenda_query.py requests --start 2025-01-01 --end 2025-01-31

# Get rotation schedules
uv run python scripts/qgenda_query.py rotations --range-start 2025-01-01 --range-end 2025-03-31

# Get schedule audit log (who changed what)
uv run python scripts/qgenda_query.py auditlog --start 2025-01-01 --end 2025-01-31

# List daily configurations
uv run python scripts/qgenda_query.py dailyconfig

# List rooms
uv run python scripts/qgenda_query.py rooms

# Get patient encounters
uv run python scripts/qgenda_query.py encounters --daily-config-key <GUID> --start 2025-01-01

# Output as table or CSV
uv run python scripts/qgenda_query.py staff --format table
uv run python scripts/qgenda_query.py schedule --start 2025-01-01 --format csv
```

## Writing Custom Queries

For queries the helper script doesn't cover, write inline Python using `qgendapy`:

```python
from qgendapy import QGendaClient, OData

client = QGendaClient()
odata = (
    OData()
    .select("StartDate", "EndDate", "StaffFName", "StaffLName", "TaskName")
    .filter("startswith(StaffLName, 'H')")
    .orderby("StartDate")
)
resp = client.schedule.list(start_date="2025-01-01", end_date="2025-01-31", odata=odata)
data = resp.data  # list[dict]
```

## QGenda API Reference

See [references/api-reference.md](references/api-reference.md) for full endpoint documentation.

## Available Client Methods

### Via qgendapy client (all endpoints)

| Method | Required Params | Optional Params | Description |
|--------|----------------|-----------------|-------------|
| `client.schedule.list(start_date)` | `start_date` | `end_date`, `includes`, `odata` | Get schedule entries |
| `client.schedule.open_shifts(start_date)` | `start_date` | `end_date`, `includes`, `odata` | Get open shifts |
| `client.schedule.rotations()` | -- | `range_start_date`, `range_end_date`, `odata` | Get rotations |
| `client.schedule.audit_log()` | -- | `schedule_start_date`, `schedule_end_date`, `odata` | Get audit log |
| `client.staff.list()` | -- | `odata` | Get staff/provider list |
| `client.staff.get(staff_key)` | `staff_key` | `odata` | Get single staff member |
| `client.task.list()` | -- | `odata` | Get task definitions |
| `client.facility.list()` | -- | `odata` | Get facilities |
| `client.time_event.list(start_date)` | `start_date` | `end_date`, `odata` | Get time events |
| `client.daily_case.list(start_date)` | `start_date` | `end_date`, `odata` | Get daily cases |
| `client.request.list(start_date)` | `start_date` | `end_date`, `include_removed`, `odata` | Get requests |
| `client.daily.configurations()` | -- | `odata` | Get daily configurations |
| `client.daily.rooms()` | -- | `odata` | Get rooms |
| `client.daily.patient_encounters()` | -- | `daily_configuration_key`, `start_date`, `includes`, `odata` | Get encounters |

### Via qgenda_core (wrapper functions)

| Function | Key Params | Description |
|----------|-----------|-------------|
| `query_schedule()` | `start_date`, `end_date`, `includes` | Schedule entries |
| `query_staff()` | -- | Staff/provider list |
| `query_staff_with_tags()` | `tag_category`, `tag_name` | Staff with tag data |
| `query_tasks()` | `includes` | Task definitions |
| `query_facilities()` | -- | Facilities |
| `query_time_events()` | `start_date`, `includes` | Time events |
| `query_daily_cases()` | `start_date`, `includes` | Daily cases |
| `query_open_shifts()` | `start_date`, `includes` | Open/unfilled shifts |
| `query_requests()` | `start_date`, `include_removed` | Time-off/swap requests |
| `query_rotations()` | `range_start_date`, `range_end_date` | Rotation schedules |
| `query_schedule_audit_log()` | `schedule_start_date` | Schedule change history |
| `query_staff_member()` | `staff_id`, `includes` | Single staff member detail |
| `query_daily_configuration()` | -- | Daily configurations |
| `query_rooms()` | -- | Rooms |
| `query_patient_encounters()` | `daily_configuration_key`, `start_date` | Patient encounters |

## OData Query Parameters

All GET endpoints support OData filtering via the `OData` builder:

- `$select` - Choose fields: `"StartDate,EndDate,StaffLName"`
- `$filter` - Filter results: `"StaffLName eq 'Smith'"`, `"startswith(StaffLName, 'H')"`
- `$orderby` - Sort: `"StartDate"`, `"StaffLName desc"`
- `$expand` - Expand related entities inline

## The `includes` Parameter

Several endpoints support `includes` to return related entities inline (separate from OData `$expand`):

- **Schedule:** `StaffTags,TaskTags,LocationTags`
- **Open Shifts:** `TaskTags,LocationTags`
- **Tasks:** `Profiles,Tags,TaskShifts`
- **Staff Member (by ID):** `Skillset,Tags,Profiles`
- **Daily Cases:** `Task,Supervisors,DirectProviders`
- **Patient Encounters:** `StandardFields,PatientInformation`

## Common Schedule Fields

`StartDate`, `StartDateUTC`, `EndDate`, `EndDateUTC`, `StaffFName`, `StaffLName`, `TaskName`, `CompName`

## Response Handling

All `qgenda_core.query_*()` functions return formatted strings (JSON, table, or CSV). The underlying `qgendapy` client returns `QGendaResponse` objects with a `.data` attribute containing the raw list/dict.

## Guidelines

- Default to today's date when no date is specified — don't ask the user to confirm
- Present schedule data in a clean, readable table format
- If a query returns too much data, suggest narrowing the date range or adding filters
- Never expose or log credentials
