"""Shared QGenda client logic used by both the MCP server and CLI script."""

import json
import os
from datetime import date

from qgendapy import OData, QGendaClient

# Default fields to return for each endpoint when no $select is specified.
DEFAULT_SELECT = {
    "schedule": ["StartDate", "EndDate", "StaffFName", "StaffLName", "TaskName", "CompName"],
    "staff": ["FirstName", "LastName", "Email", "StaffKey"],
    "task": ["TaskName", "TaskKey", "Abbrev"],
    "facility": ["FacilityName", "FacilityKey", "Abbrev"],
    "timeevent": ["StartDate", "EndDate", "StaffFName", "StaffLName", "TaskName"],
    "dailycase": ["StartDate", "EndDate", "StaffFName", "StaffLName", "TaskName"],
}

_client: QGendaClient | None = None


def check_env() -> str | None:
    """Validate QGenda configuration is available.

    Returns the config file path if QGENDA_CONF_FILE is set, or None if
    credentials are provided via individual environment variables
    (QGENDA_EMAIL, QGENDA_PASSWORD, QGENDA_COMPANY_KEY).
    """
    # 1. Explicit config file path
    conf = os.environ.get("QGENDA_CONF_FILE", "").strip()
    if conf:
        conf = os.path.expanduser(conf)
        if not os.path.exists(conf):
            raise RuntimeError(f"Config file not found: {conf}")
        return conf

    # 2. Individual environment variables (qgendapy resolves these directly)
    env_vars = ("QGENDA_EMAIL", "QGENDA_PASSWORD", "QGENDA_COMPANY_KEY")
    present = [v for v in env_vars if os.environ.get(v, "").strip()]
    if present:
        missing = [v for v in env_vars if not os.environ.get(v, "").strip()]
        if missing:
            raise RuntimeError(
                f"Partial QGenda env config: {', '.join(present)} set but "
                f"{', '.join(missing)} missing. Set all three or use QGENDA_CONF_FILE."
            )
        return None

    # 3. Default config file location
    default_conf = os.path.expanduser("~/.qgenda.conf")
    if os.path.exists(default_conf):
        os.environ["QGENDA_CONF_FILE"] = default_conf
        return default_conf

    raise RuntimeError(
        "QGenda credentials not configured. Either set QGENDA_CONF_FILE to "
        "a config file path, or set QGENDA_EMAIL, QGENDA_PASSWORD, and "
        "QGENDA_COMPANY_KEY environment variables."
    )


def get_client() -> QGendaClient:
    """Return a QGendaClient instance. Token refresh is handled automatically."""
    global _client
    if _client is None:
        check_env()
        _client = QGendaClient()
    return _client


def build_odata(
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    endpoint: str | None = None,
) -> OData | None:
    """Build an OData query object. Applies default $select if none provided."""
    odata = OData()
    has_params = False

    if select:
        odata = odata.select(*select.split(","))
        has_params = True
    elif endpoint and endpoint in DEFAULT_SELECT:
        odata = odata.select(*DEFAULT_SELECT[endpoint])
        has_params = True

    if filter_expr:
        odata = odata.filter(filter_expr)
        has_params = True
    if orderby:
        odata = odata.orderby(orderby)
        has_params = True
    if expand:
        odata = odata.expand(expand)
        has_params = True

    return odata if has_params else None


def format_response(data, fmt: str = "json") -> str:
    """Format API response data in the requested format.

    Args:
        data: List or dict from the QGenda API (QGendaResponse.data).
        fmt: "json" for pretty JSON, "csv" for comma-separated, "table" for ASCII table.
    """
    if fmt == "json":
        return json.dumps(data, indent=2, default=str)

    if not isinstance(data, list) or len(data) == 0:
        return json.dumps(data, indent=2, default=str)

    headers = list(data[0].keys())

    if fmt == "csv":
        import csv
        import io

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
        return buf.getvalue()

    if fmt == "table":
        col_widths = {h: len(h) for h in headers}
        for row in data:
            for h in headers:
                col_widths[h] = max(col_widths[h], len(str(row.get(h, ""))))

        def fmt_row(vals: dict) -> str:
            return "  ".join(str(vals.get(h, "")).ljust(col_widths[h]) for h in headers)

        lines = [fmt_row({h: h for h in headers})]
        lines.append("  ".join("-" * col_widths[h] for h in headers))
        for row in data:
            lines.append(fmt_row(row))
        return "\n".join(lines)

    return json.dumps(data, indent=2, default=str)


def today() -> str:
    """Return today's date as YYYY-MM-DD."""
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Query functions — all use qgendapy resource methods
# ---------------------------------------------------------------------------


def query_schedule(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    fmt: str = "json",
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    if not start_date:
        start_date = today()
    if not end_date:
        end_date = start_date
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand, "schedule")
    resp = client.schedule.list(
        start_date=start_date, end_date=end_date,
        includes=includes, odata=odata,
    )
    return format_response(resp.data, fmt)


def query_staff(
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    fmt: str = "json",
) -> str:
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, endpoint="staff")
    resp = client.staff.list(odata=odata)
    return format_response(resp.data, fmt)


def query_staff_with_tags(
    tag_category: str | None = None,
    tag_name: str | None = None,
    fmt: str = "json",
) -> str:
    """Fetch staff with their full tag data (sub-specialties, skill sets, etc.)."""
    client = get_client()
    odata = OData().select("FirstName", "LastName", "StaffKey", "Tags")
    resp = client.staff.list(odata=odata)
    data = resp.data

    # Optionally filter to staff who have a matching tag
    if tag_category or tag_name:
        filtered = []
        for staff in data:
            for cat in staff.get("Tags") or []:
                cat_match = (not tag_category) or cat.get("CategoryName") == tag_category
                if cat_match:
                    for tag in cat.get("Tags") or []:
                        if (not tag_name) or tag.get("Name") == tag_name:
                            filtered.append(staff)
                            break
                    else:
                        continue
                    break
        data = filtered

    # Flatten tags into a readable summary for table/csv output
    results = []
    for staff in data:
        row: dict = {
            "FirstName": staff.get("FirstName", ""),
            "LastName": staff.get("LastName", ""),
            "StaffKey": staff.get("StaffKey", ""),
        }
        for cat in staff.get("Tags") or []:
            cat_name = cat.get("CategoryName", "")
            tag_names = ", ".join(t.get("Name", "") for t in cat.get("Tags") or [])
            row[cat_name] = tag_names
        results.append(row)

    if fmt == "json":
        return json.dumps(results, indent=2)

    if not results:
        return json.dumps([], indent=2)

    # Collect all column headers across all rows
    headers_set: list[str] = []
    seen: set[str] = set()
    for row in results:
        for k in row:
            if k not in seen:
                headers_set.append(k)
                seen.add(k)

    if fmt == "csv":
        import csv
        import io

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=headers_set)
        writer.writeheader()
        writer.writerows(results)
        return buf.getvalue()

    if fmt == "table":
        col_widths = {h: len(h) for h in headers_set}
        for row in results:
            for h in headers_set:
                col_widths[h] = max(col_widths[h], len(str(row.get(h, ""))))

        def fmt_row(vals: dict) -> str:
            return "  ".join(
                str(vals.get(h, "")).ljust(col_widths[h]) for h in headers_set
            )

        lines = [fmt_row({h: h for h in headers_set})]
        lines.append("  ".join("-" * col_widths[h] for h in headers_set))
        for row in results:
            lines.append(fmt_row(row))
        return "\n".join(lines)

    return json.dumps(results, indent=2)


def query_tasks(
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    fmt: str = "json",
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand, "task")
    resp = client.task.list(odata=odata)
    return format_response(resp.data, fmt)


def query_facilities(
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    fmt: str = "json",
) -> str:
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, endpoint="facility")
    resp = client.facility.list(odata=odata)
    return format_response(resp.data, fmt)


def query_time_events(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    fmt: str = "json",
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    if not start_date:
        start_date = today()
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand, "timeevent")
    kwargs: dict = {"start_date": start_date, "odata": odata}
    if end_date:
        kwargs["end_date"] = end_date
    resp = client.time_event.list(**kwargs)
    return format_response(resp.data, fmt)


def query_daily_cases(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    fmt: str = "json",
    includes: str | None = None,
    expand: str | None = None,
) -> str:
    if not start_date:
        start_date = today()
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand, "dailycase")
    kwargs: dict = {"start_date": start_date, "odata": odata}
    if end_date:
        kwargs["end_date"] = end_date
    resp = client.daily_case.list(**kwargs)
    return format_response(resp.data, fmt)


# ---------------------------------------------------------------------------
# Endpoints that previously used _api_get — now use qgendapy resources
# ---------------------------------------------------------------------------


def query_open_shifts(
    start_date: str | None = None,
    end_date: str | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    includes: str | None = None,
    fmt: str = "json",
) -> str:
    """Get open (unfilled) shifts for a date range."""
    if not start_date:
        start_date = today()
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    kwargs: dict = {"start_date": start_date, "odata": odata}
    if end_date:
        kwargs["end_date"] = end_date
    if includes:
        kwargs["includes"] = includes
    resp = client.schedule.open_shifts(**kwargs)
    return format_response(resp.data, fmt)


def query_requests(
    start_date: str | None = None,
    end_date: str | None = None,
    include_removed: bool = False,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    fmt: str = "json",
) -> str:
    """Get time-off and swap requests for a date range."""
    if not start_date:
        start_date = today()
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    resp = client.request.list(
        start_date=start_date, end_date=end_date,
        include_removed=include_removed, odata=odata,
    )
    return format_response(resp.data, fmt)


def query_rotations(
    range_start_date: str | None = None,
    range_end_date: str | None = None,
    ignore_holiday: bool = False,
    ignore_weekend: bool = False,
    defined_blocks: bool = False,
    range_extension: int | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    fmt: str = "json",
) -> str:
    """Get rotation schedules for a date range."""
    if not range_start_date:
        range_start_date = today()
    if not range_end_date:
        range_end_date = range_start_date
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    resp = client.schedule.rotations(
        range_start_date=range_start_date, range_end_date=range_end_date,
        odata=odata,
    )
    return format_response(resp.data, fmt)


def query_schedule_audit_log(
    schedule_start_date: str | None = None,
    schedule_end_date: str | None = None,
    since_modified_timestamp: str | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    fmt: str = "json",
) -> str:
    """Get the schedule audit log for a date range."""
    if not schedule_start_date:
        schedule_start_date = today()
    if not schedule_end_date:
        schedule_end_date = schedule_start_date
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    kwargs: dict = {
        "schedule_start_date": schedule_start_date,
        "schedule_end_date": schedule_end_date,
        "odata": odata,
    }
    if since_modified_timestamp:
        kwargs["since_modified_timestamp"] = since_modified_timestamp
    resp = client.schedule.audit_log(**kwargs)
    return format_response(resp.data, fmt)


def query_staff_member(
    staff_id: str,
    includes: str | None = None,
    fmt: str = "json",
) -> str:
    """Get a single staff member by ID with full detail."""
    client = get_client()
    resp = client.staff.get(staff_id, odata=None)
    return format_response(resp.data, fmt)


def query_daily_configuration(
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    fmt: str = "json",
) -> str:
    """List daily configurations (capacity management)."""
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    resp = client.daily.configurations(odata=odata)
    return format_response(resp.data, fmt)


def query_rooms(
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    fmt: str = "json",
) -> str:
    """List rooms for the company."""
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    resp = client.daily.rooms(odata=odata)
    return format_response(resp.data, fmt)


def query_patient_encounters(
    daily_configuration_key: str,
    start_date: str | None = None,
    end_date: str | None = None,
    includes: str | None = None,
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    expand: str | None = None,
    fmt: str = "json",
) -> str:
    """Get patient encounters for a daily configuration and date range."""
    if not start_date:
        start_date = today()
    client = get_client()
    odata = build_odata(select, filter_expr, orderby, expand)
    kwargs: dict = {
        "daily_configuration_key": daily_configuration_key,
        "start_date": start_date,
        "odata": odata,
    }
    if end_date:
        kwargs["end_date"] = end_date
    if includes:
        kwargs["includes"] = includes
    resp = client.daily.patient_encounters(**kwargs)
    return format_response(resp.data, fmt)
