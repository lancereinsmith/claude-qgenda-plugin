#!/usr/bin/env python3
"""Helper script for querying QGenda from Claude Code.

Requires:
  - qgendapy package
  - QGENDA_CONF_FILE environment variable pointing to qgenda.conf

Usage:
  python qgenda_query.py schedule --start 2025-01-01 --end 2025-01-31
  python qgenda_query.py schedule --start 2025-01-01 --filter "StaffLName eq 'Smith'"
  python qgenda_query.py schedule --start 2025-01-01 --includes StaffTags,TaskTags
  python qgenda_query.py staff
  python qgenda_query.py openshifts --start 2025-01-01
  python qgenda_query.py requests --start 2025-01-01 --end 2025-01-31
  python qgenda_query.py rotations --range-start 2025-01-01 --range-end 2025-03-31
  python qgenda_query.py auditlog --start 2025-01-01 --end 2025-01-31
  python qgenda_query.py staff-detail --staff-id <GUID> --includes Skillset,Tags,Profiles
  python qgenda_query.py dailyconfig
  python qgenda_query.py rooms
  python qgenda_query.py encounters --daily-config-key <GUID> --start 2025-01-01
"""

import argparse
import sys
import os

# Allow importing qgenda_core from the project root or the same directory
# (same directory when installed as a packaged skill)
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, ".."))

import qgenda_core as core


def cmd_schedule(args):
    try:
        print(
            core.query_schedule(
                args.start,
                args.end,
                args.select,
                args.filter,
                args.orderby,
                args.format,
                includes=args.includes,
                expand=args.expand,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_staff(args):
    try:
        print(core.query_staff(args.select, args.filter, args.orderby, args.format))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_staff_tags(args):
    try:
        print(
            core.query_staff_with_tags(args.tag_category, args.tag_name, args.format)
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tasks(args):
    try:
        print(
            core.query_tasks(
                args.select, args.filter, args.orderby, args.format,
                includes=args.includes, expand=args.expand,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_facilities(args):
    try:
        print(
            core.query_facilities(args.select, args.filter, args.orderby, args.format)
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_timeevent(args):
    try:
        print(
            core.query_time_events(
                args.start,
                args.end,
                args.select,
                args.filter,
                args.orderby,
                args.format,
                includes=args.includes,
                expand=args.expand,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_dailycase(args):
    try:
        print(
            core.query_daily_cases(
                args.start,
                args.end,
                args.select,
                args.filter,
                args.orderby,
                args.format,
                includes=args.includes,
                expand=args.expand,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_openshifts(args):
    try:
        print(
            core.query_open_shifts(
                args.start, args.end, args.select, args.filter,
                args.orderby, args.expand, args.includes, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_requests(args):
    try:
        print(
            core.query_requests(
                args.start, args.end, args.include_removed,
                args.select, args.filter, args.orderby, args.expand, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_rotations(args):
    try:
        print(
            core.query_rotations(
                args.range_start, args.range_end,
                args.ignore_holiday, args.ignore_weekend,
                args.defined_blocks, args.range_extension,
                args.select, args.filter, args.orderby, args.expand, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_auditlog(args):
    try:
        print(
            core.query_schedule_audit_log(
                args.start, args.end, args.since,
                args.select, args.filter, args.orderby, args.expand, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_staff_detail(args):
    try:
        print(core.query_staff_member(args.staff_id, args.includes, args.format))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_dailyconfig(args):
    try:
        print(
            core.query_daily_configuration(
                args.select, args.filter, args.orderby, args.expand, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_rooms(args):
    try:
        print(
            core.query_rooms(
                args.select, args.filter, args.orderby, args.expand, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_encounters(args):
    try:
        print(
            core.query_patient_encounters(
                args.daily_config_key, args.start, args.end, args.includes,
                args.select, args.filter, args.orderby, args.expand, args.format,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_odata_args(parser):
    """Add common OData and format arguments to a subparser."""
    parser.add_argument("--select", help="OData $select fields (comma-separated)")
    parser.add_argument("--filter", help="OData $filter expression")
    parser.add_argument("--orderby", help="OData $orderby expression")
    parser.add_argument("--expand", help="OData $expand expression")
    parser.add_argument(
        "--format",
        choices=["json", "table", "csv"],
        default="json",
        help="Output format (default: json)",
    )


def add_includes_arg(parser):
    """Add --includes flag for endpoints that support it."""
    parser.add_argument(
        "--includes",
        help="Comma-separated related entities to include in response",
    )


def main():
    parser = argparse.ArgumentParser(description="Query QGenda REST API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Schedule
    p_sched = subparsers.add_parser("schedule", help="Query schedule")
    p_sched.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    p_sched.add_argument("--end", help="End date (YYYY-MM-DD)")
    add_odata_args(p_sched)
    add_includes_arg(p_sched)
    p_sched.set_defaults(func=cmd_schedule)

    # Staff
    p_staff = subparsers.add_parser("staff", help="List staff members")
    add_odata_args(p_staff)
    p_staff.set_defaults(func=cmd_staff)

    # Staff with tags (sub-specialties, skill sets, etc.)
    p_stags = subparsers.add_parser(
        "staff-tags", help="List staff with tags (sub-specialties, skill sets, etc.)"
    )
    p_stags.add_argument(
        "--tag-category",
        help='Tag category to filter (e.g. "Sub Specialty", "Skill Set", "Staff Type")',
    )
    p_stags.add_argument(
        "--tag-name", help='Tag name to filter (e.g. "Neuro Lite", "MQSA")'
    )
    p_stags.add_argument(
        "--format",
        choices=["json", "table", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    p_stags.set_defaults(func=cmd_staff_tags)

    # Tasks
    p_tasks = subparsers.add_parser("tasks", help="List tasks")
    add_odata_args(p_tasks)
    add_includes_arg(p_tasks)
    p_tasks.set_defaults(func=cmd_tasks)

    # Facilities
    p_fac = subparsers.add_parser("facilities", help="List facilities")
    add_odata_args(p_fac)
    p_fac.set_defaults(func=cmd_facilities)

    # Time events
    p_time = subparsers.add_parser("timeevent", help="Query time events")
    p_time.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    p_time.add_argument("--end", help="End date (YYYY-MM-DD)")
    add_odata_args(p_time)
    add_includes_arg(p_time)
    p_time.set_defaults(func=cmd_timeevent)

    # Daily cases
    p_daily = subparsers.add_parser("dailycase", help="Query daily cases")
    p_daily.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    p_daily.add_argument("--end", help="End date (YYYY-MM-DD)")
    add_odata_args(p_daily)
    add_includes_arg(p_daily)
    p_daily.set_defaults(func=cmd_dailycase)

    # --- New subcommands ---

    # Open shifts
    p_open = subparsers.add_parser("openshifts", help="Query open (unfilled) shifts")
    p_open.add_argument("--start", help="Start date (YYYY-MM-DD, defaults to today)")
    p_open.add_argument("--end", help="End date (YYYY-MM-DD)")
    add_odata_args(p_open)
    add_includes_arg(p_open)
    p_open.set_defaults(func=cmd_openshifts)

    # Requests (time-off, swaps)
    p_req = subparsers.add_parser("requests", help="Query time-off and swap requests")
    p_req.add_argument("--start", help="Start date (YYYY-MM-DD, defaults to today)")
    p_req.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_req.add_argument(
        "--include-removed", action="store_true",
        help="Include removed/cancelled requests",
    )
    add_odata_args(p_req)
    p_req.set_defaults(func=cmd_requests)

    # Rotations
    p_rot = subparsers.add_parser("rotations", help="Query rotation schedules")
    p_rot.add_argument("--range-start", help="Range start date (YYYY-MM-DD, defaults to today)")
    p_rot.add_argument("--range-end", help="Range end date (YYYY-MM-DD, defaults to start)")
    p_rot.add_argument("--ignore-holiday", action="store_true", help="Ignore holidays")
    p_rot.add_argument("--ignore-weekend", action="store_true", help="Ignore weekends")
    p_rot.add_argument("--defined-blocks", action="store_true", help="Use defined rotation blocks")
    p_rot.add_argument("--range-extension", type=int, help="Months (1-13) to extend range")
    add_odata_args(p_rot)
    p_rot.set_defaults(func=cmd_rotations)

    # Schedule audit log
    p_audit = subparsers.add_parser("auditlog", help="Query schedule audit log")
    p_audit.add_argument("--start", help="Schedule start date (YYYY-MM-DD, defaults to today)")
    p_audit.add_argument("--end", help="Schedule end date (YYYY-MM-DD, defaults to start)")
    p_audit.add_argument("--since", help="Only changes after this timestamp (ISO-8601 UTC)")
    add_odata_args(p_audit)
    p_audit.set_defaults(func=cmd_auditlog)

    # Staff detail (single staff member by ID)
    p_sd = subparsers.add_parser("staff-detail", help="Get detailed info for a single staff member")
    p_sd.add_argument("--staff-id", required=True, help="Staff member GUID (StaffKey)")
    add_includes_arg(p_sd)
    p_sd.add_argument(
        "--format",
        choices=["json", "table", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    p_sd.set_defaults(func=cmd_staff_detail)

    # Daily configuration
    p_dc = subparsers.add_parser("dailyconfig", help="List daily configurations")
    add_odata_args(p_dc)
    p_dc.set_defaults(func=cmd_dailyconfig)

    # Rooms
    p_rooms = subparsers.add_parser("rooms", help="List rooms")
    add_odata_args(p_rooms)
    p_rooms.set_defaults(func=cmd_rooms)

    # Patient encounters
    p_enc = subparsers.add_parser("encounters", help="Query patient encounters")
    p_enc.add_argument("--daily-config-key", required=True, help="Daily configuration GUID")
    p_enc.add_argument("--start", help="Start date (YYYY-MM-DD, defaults to today)")
    p_enc.add_argument("--end", help="End date (YYYY-MM-DD)")
    add_odata_args(p_enc)
    add_includes_arg(p_enc)
    p_enc.set_defaults(func=cmd_encounters)

    args = parser.parse_args()
    try:
        core.check_env()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
