"""QGenda MCP Server — exposes QGenda scheduling data as tools for Claude Desktop."""

import logging
import sys

from mcp.server.fastmcp import FastMCP

import qgenda_core as core

logger = logging.getLogger("qgenda-mcp")

mcp = FastMCP(
    "qgenda",
    instructions=(
        "You are helping a physician query their QGenda scheduling system. "
        "Present schedule data in clean, readable tables. "
        "Default to today's date when no date is specified. "
        "Never expose or log credentials."
    ),
)


@mcp.tool()
def get_schedule(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    """Get schedule entries from QGenda for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to today.
        end_date: End date in YYYY-MM-DD format. Defaults to start_date.
        select: Comma-separated fields to return (e.g. "StartDate,StaffLName,TaskName").
        filter: OData filter expression (e.g. "StaffLName eq 'Smith'").
        orderby: OData sort expression (e.g. "StartDate", "StaffLName desc").
        includes: Comma-separated related entities to include (e.g. "StaffTags,TaskTags,LocationTags").
        expand: OData $expand expression.
    """
    try:
        return core.query_schedule(start_date, end_date, select, filter, orderby, includes=includes, expand=expand)
    except Exception as exc:
        return f"Error querying schedule: {exc}"


@mcp.tool()
def get_staff(
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
) -> str:
    """List staff members / providers from QGenda.

    Args:
        select: Comma-separated fields to return.
        filter: OData filter expression (e.g. "startswith(LastName, 'S')").
        orderby: OData sort expression.
    """
    try:
        return core.query_staff(select, filter, orderby)
    except Exception as exc:
        return f"Error querying staff: {exc}"


@mcp.tool()
def get_staff_tags(
    tag_category: str | None = None,
    tag_name: str | None = None,
) -> str:
    """List staff with their tags (sub-specialties, skill sets, staff types, etc.).

    The standard get_staff tool does NOT return tags. Use this tool when you need
    to look up staff by sub-specialty (e.g. "Neuro Lite"), skill set, or staff type.

    Args:
        tag_category: Optional category filter (e.g. "Sub Specialty", "Primary Specialty",
            "Skill Set", "Staff Type", "Location").
        tag_name: Optional tag name filter (e.g. "Neuro Lite", "MQSA", "Shareholder").
    """
    try:
        return core.query_staff_with_tags(tag_category, tag_name)
    except Exception as exc:
        return f"Error querying staff tags: {exc}"


@mcp.tool()
def get_tasks(
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    """List task definitions (shift types, assignment types) from QGenda.

    Args:
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        includes: Comma-separated related entities (e.g. "Profiles,Tags,TaskShifts").
        expand: OData $expand expression.
    """
    try:
        return core.query_tasks(select, filter, orderby, includes=includes, expand=expand)
    except Exception as exc:
        return f"Error querying tasks: {exc}"


@mcp.tool()
def get_facilities(
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
) -> str:
    """List facilities from QGenda.

    Args:
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
    """
    try:
        return core.query_facilities(select, filter, orderby)
    except Exception as exc:
        return f"Error querying facilities: {exc}"


@mcp.tool()
def get_time_events(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    """Get time events from QGenda.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to today.
        end_date: End date in YYYY-MM-DD format.
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        includes: Comma-separated related entities to include.
        expand: OData $expand expression.
    """
    try:
        return core.query_time_events(start_date, end_date, select, filter, orderby, includes=includes, expand=expand)
    except Exception as exc:
        return f"Error querying time events: {exc}"


@mcp.tool()
def get_daily_cases(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    """Get daily case information from QGenda.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to today.
        end_date: End date in YYYY-MM-DD format.
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        includes: Comma-separated related entities (e.g. "Task,Supervisors,DirectProviders").
        expand: OData $expand expression.
    """
    try:
        return core.query_daily_cases(start_date, end_date, select, filter, orderby, includes=includes, expand=expand)
    except Exception as exc:
        return f"Error querying daily cases: {exc}"


# ---------------------------------------------------------------------------
# New tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_open_shifts(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    """Get open (unfilled) shifts for a date range. Use when the user asks about
    unfilled shifts, available coverage, or shifts that need to be picked up.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to today.
        end_date: End date in YYYY-MM-DD format.
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        includes: Comma-separated related entities (e.g. "TaskTags,LocationTags").
        expand: OData $expand expression.
    """
    try:
        return core.query_open_shifts(start_date, end_date, select, filter, orderby, expand, includes)
    except Exception as exc:
        return f"Error querying open shifts: {exc}"


@mcp.tool()
def get_requests(
    start_date: str | None = None,
    end_date: str | None = None,
    include_removed: bool = False,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
) -> str:
    """Get time-off and swap requests. Use when the user asks about PTO, time-off
    requests, swap requests, or who has requested time off.

    Args:
        start_date: Start date in YYYY-MM-DD format. Defaults to today.
        end_date: End date in YYYY-MM-DD format.
        include_removed: If true, include removed/cancelled requests.
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        expand: OData $expand expression.
    """
    try:
        return core.query_requests(start_date, end_date, include_removed, select, filter, orderby, expand)
    except Exception as exc:
        return f"Error querying requests: {exc}"


@mcp.tool()
def get_rotations(
    range_start_date: str | None = None,
    range_end_date: str | None = None,
    ignore_holiday: bool = False,
    ignore_weekend: bool = False,
    defined_blocks: bool = False,
    range_extension: int | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
) -> str:
    """Get rotation schedules. Use when the user asks about rotations, rotation
    assignments, or what rotation someone is on.

    Args:
        range_start_date: Start date in YYYY-MM-DD format. Defaults to today.
        range_end_date: End date in YYYY-MM-DD format. Defaults to start date.
        ignore_holiday: Ignore holidays when calculating rotations.
        ignore_weekend: Ignore weekends when calculating rotations.
        defined_blocks: Use defined rotation blocks from the UI.
        range_extension: Months (1-13) to extend rotation start/end calculation.
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        expand: OData $expand expression.
    """
    try:
        return core.query_rotations(
            range_start_date, range_end_date, ignore_holiday, ignore_weekend,
            defined_blocks, range_extension, select, filter, orderby, expand,
        )
    except Exception as exc:
        return f"Error querying rotations: {exc}"


@mcp.tool()
def get_schedule_audit_log(
    schedule_start_date: str | None = None,
    schedule_end_date: str | None = None,
    since_modified_timestamp: str | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
) -> str:
    """Get the schedule audit log showing who changed what on the schedule.
    Use when the user asks about schedule changes, who modified a schedule entry,
    or audit history.

    Args:
        schedule_start_date: Start date in YYYY-MM-DD format. Defaults to today.
        schedule_end_date: End date in YYYY-MM-DD format. Defaults to start date.
        since_modified_timestamp: Only return changes after this timestamp (ISO-8601 UTC).
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        expand: OData $expand expression.
    """
    try:
        return core.query_schedule_audit_log(
            schedule_start_date, schedule_end_date, since_modified_timestamp,
            select, filter, orderby, expand,
        )
    except Exception as exc:
        return f"Error querying schedule audit log: {exc}"


@mcp.tool()
def get_staff_member(
    staff_id: str,
    includes: str | None = None,
) -> str:
    """Get a single staff member by ID with full detail including tags, profiles,
    and skillset. Use when you need detailed info about a specific provider.

    Args:
        staff_id: The staff member's StaffKey (GUID).
        includes: Comma-separated related entities (e.g. "Skillset,Tags,Profiles").
    """
    try:
        return core.query_staff_member(staff_id, includes)
    except Exception as exc:
        return f"Error querying staff member: {exc}"


@mcp.tool()
def get_daily_configuration(
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
) -> str:
    """List daily configurations (capacity management setup). Use when the user
    asks about daily configurations or capacity settings.

    Args:
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        expand: OData $expand expression.
    """
    try:
        return core.query_daily_configuration(select, filter, orderby, expand)
    except Exception as exc:
        return f"Error querying daily configuration: {exc}"


@mcp.tool()
def get_rooms(
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
) -> str:
    """List rooms for the company. Use when the user asks about available rooms
    or room configuration.

    Args:
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        expand: OData $expand expression.
    """
    try:
        return core.query_rooms(select, filter, orderby, expand)
    except Exception as exc:
        return f"Error querying rooms: {exc}"


@mcp.tool()
def get_patient_encounters(
    daily_configuration_key: str,
    start_date: str | None = None,
    end_date: str | None = None,
    includes: str | None = None,
    select: str | None = None,
    filter: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
) -> str:
    """Get patient encounter data for a daily configuration and date range.

    Args:
        daily_configuration_key: The daily configuration GUID (required).
        start_date: Start date in YYYY-MM-DD format. Defaults to today.
        end_date: End date in YYYY-MM-DD format.
        includes: Comma-separated related entities (e.g. "StandardFields,PatientInformation").
        select: Comma-separated fields to return.
        filter: OData filter expression.
        orderby: OData sort expression.
        expand: OData $expand expression.
    """
    try:
        return core.query_patient_encounters(
            daily_configuration_key, start_date, end_date, includes,
            select, filter, orderby, expand,
        )
    except Exception as exc:
        return f"Error querying patient encounters: {exc}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="QGenda MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for SSE/HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind for SSE/HTTP transport (default: 127.0.0.1)",
    )
    args = parser.parse_args()

    # Log to stderr so it's visible to the user (stdout is reserved for MCP protocol)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        stream=sys.stderr,
    )
    tool_names = [t.name for t in (mcp._tool_manager.list_tools())]
    logger.info("QGenda MCP server starting — %d tools registered", len(tool_names))
    logger.info("Tools: %s", ", ".join(tool_names))
    logger.info("Transport: %s", args.transport)
    try:
        core.check_env()
        logger.info("Credentials file: %s", core.check_env())
    except RuntimeError as exc:
        logger.warning("Credential check: %s", exc)

    if args.port is not None:
        mcp.settings.port = args.port
    if args.host is not None:
        mcp.settings.host = args.host

    mcp.run(transport=args.transport)
