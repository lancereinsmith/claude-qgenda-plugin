# QGenda REST API Reference

## Base URL

`https://api.qgenda.com/v2/`

## Authentication

**Endpoint:** `POST /login`

Request (form-encoded):

- `email` (required) - API account username
- `password` (required) - API account password

Response:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "expires_in": 3600
}
```

All subsequent requests require: `Authorization: bearer <access_token>`

The qgendapy client handles authentication and token refresh automatically.

## Data Format

All data returned from the QGenda REST API is in JSON format. Requests should include `Content-Type: application/json`.

## Compression

The API supports BR and GZip compression via `Accept-Encoding` header. With compression, up to 100 days of data can be requested; without, up to 31 days.

## OData Support

All GET endpoints support OData query parameters:

- `$select` - Comma-separated field names to return
- `$filter` - Filter expression (e.g., `StaffLName eq 'Smith'`, `startswith(StaffLName, 'H')`)
- `$orderby` - Sort expression (e.g., `StartDate`, `StaffLName desc`)
- `$expand` - Expand related entities inline

**NOTE:** OData parameters, operators, and expressions are **case-sensitive**. Property names in expressions must match the exact casing (e.g., `Date` ≠ `date`).

## The `includes` Parameter

Several endpoints support an `includes` query parameter (separate from OData) that returns related entities inline. Pass a comma-separated list of entity names.

| Endpoint | Available `includes` values |
|----------|---------------------------|
| `GET /schedule` | `StaffTags`, `TaskTags`, `LocationTags` |
| `GET /schedule/openshifts` | `TaskTags`, `LocationTags` |
| `GET /task` | `Profiles`, `Tags`, `TaskShifts` |
| `GET /staffmember/:staffId` | `Skillset`, `Tags`, `Profiles` |
| `GET /requestlimit` | `ShiftCredit`, `StaffLimits` |
| `GET /dailycase` | `Task`, `Supervisors`, `DirectProviders` |
| `GET /daily/patientencounter` | `StandardFields`, `PatientInformation` |

## Incremental Sync with `sinceModifiedTimestamp`

For tracking changes over time, several endpoints support `sinceModifiedTimestamp` (ISO-8601 UTC format: `yyyy-MM-ddThh:mm:ssZ`). Recommended pattern:

1. Seed your data by calling the endpoint without `sinceModifiedTimestamp`
2. Take the MAX `LastModifiedDateUTC` from the response
3. On subsequent calls, pass that value as `sinceModifiedTimestamp` to get only changes

Supported on: Schedule, Schedule/AuditLog, Task, PayCode, PayRate

---

## Endpoints

### Schedule

`GET /schedule`

Returns schedule entries within a date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `startDate` | Yes | Date | Start date (M/D/YYYY or MM/DD/YYYY) |
| `endDate` | No | Date | End date. Defaults to startDate |
| `companyKey` | No | GUID | Filter by company |
| `includeDeletes` | No | Boolean | Include deleted entries (IsStruck=true) |
| `sinceModifiedTimestamp` | No | Timestamp | Only entries changed after this time |
| `dateFormat` | No | String | Date format for request fields |
| `includes` | No | String | Related entities (StaffTags,TaskTags,LocationTags) |
| `$select` | No | OData | Fields to return |
| `$filter` | No | OData | Filter expression |
| `$orderby` | No | OData | Sort expression |
| `$expand` | No | OData | Expand expression |

Key response fields: `StartDate`, `StartDateUTC`, `EndDate`, `EndDateUTC`, `StaffFName`, `StaffLName`, `StaffKey`, `TaskName`, `TaskKey`, `CompName`, `CompKey`, `IsStruck`, `LastModifiedDateUTC`

---

### Schedule Audit Log

`GET /schedule/auditLog`

Returns the schedule audit log for a date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `scheduleStartDate` | Yes | Date | Earliest date for audit entries |
| `scheduleEndDate` | Yes | Date | Latest date for audit entries |
| `sinceModifiedTimestamp` | No | Timestamp | Only changes after this time |
| `dateFormat` | No | String | Date format for request fields |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Open Shifts

`GET /schedule/openshifts`

Returns open (unfilled) shifts for a date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `startDate` | Yes | Date | Start date |
| `endDate` | No | Date | End date (max 100 days with compression, 31 without) |
| `companyKey` | No | GUID | Filter by company |
| `dateFormat` | No | String | Date format |
| `includes` | No | String | Related entities (TaskTags,LocationTags) |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Rotations

`GET /schedule/rotations`

Returns rotation schedules for a date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `rangeStartDate` | Yes | Date | Earliest date |
| `rangeEndDate` | Yes | Date | Latest date (max 380 days) |
| `ignoreHoliday` | No | Boolean | Ignore QGenda holidays in rotation calculation |
| `ignoreWeekend` | No | Boolean | Ignore weekends (Fri-Sat or Sat-Sun per company) |
| `definedBlocks` | No | Boolean | Use rotation blocks from UI (Block: Tasks) |
| `rangeExtension` | No | Integer | Months (1-13) to extend start/end calculation (default: 6) |
| `dateFormat` | No | String | Date format |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Request (Time-Off / Swaps)

`GET /request`

Returns requests for a date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `startDate` | Yes | Date | Start date |
| `endDate` | No | Date | End date (max 100 days) |
| `includeRemoved` | No | Boolean | Include removed requests (default: false) |
| `dateFormat` | No | String | Date format |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

### Request/Approved

`GET /request/approved`

Returns approved requests with pagination support via `pageToken`/`syncToken`.

---

### Request Limit

`GET /requestlimit`

Returns request limits viewable by the user.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | No | GUID | Filter by company |
| `startDate` | No | Date | Limits active during this start date |
| `endDate` | No | Date | Limits active during this end date |
| `includes` | No | String | Related entities (ShiftCredit,StaffLimits) |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Staff Member

`GET /staffmember`

Returns provider/staff information. The basic endpoint does NOT return tags — use `includes=Tags` or the `staff-tags` CLI command.

`GET /staffmember/:staffId`

Returns a single staff member by StaffKey with full detail.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `CompanyKey` | Yes | GUID | Company key |
| `includes` | No | String | Related entities (Skillset,Tags,Profiles) |

---

### Task

`GET /task`

Returns all tasks viewable by the user.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `includes` | No | String | Related entities (Profiles,Tags,TaskShifts) |
| `sinceModifiedTimestamp` | No | Timestamp | Only tasks modified after this time |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Facility

`GET /facility`

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Time Event

`GET /timeevent`

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `startDate` | Yes | Date | Start date |
| `companyKey` | Yes | GUID | Company key |
| `endDate` | No | Date | End date |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Daily Case

`GET /dailycase`

Returns daily cases within a date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `startDate` | Yes | Date | Start date |
| `endDate` | No | Date | End date (max 100/31 days with/without compression) |
| `dateFormat` | No | String | Date format |
| `includes` | No | String | Related entities (Task,Supervisors,DirectProviders) |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Daily Configuration

`GET /daily/dailyconfiguration`

Returns daily configurations the user has access to.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

`GET /daily/dailyconfiguration/:dailyConfigurationKey`

Returns a single daily configuration by key.

---

### Room

`GET /daily/room`

Returns rooms for a company.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Room Assignments

`GET /daily/capacityroomassignment`

Returns room assignments for a company and daily configuration.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `dailyConfigurationKey` | Yes | GUID | Daily configuration key |
| `startDate` | Yes | Date | Start date |
| `endDate` | No | Date | End date (defaults to startDate) |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Patient Encounter

`GET /daily/patientencounter`

Returns patient encounters for a daily configuration and date range.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `companyKey` | Yes | GUID | Company key |
| `dailyConfigurationKey` | Yes | GUID | Daily configuration key |
| `startDate` | Yes | Date | Start date |
| `endDate` | No | Date | End date (max 100/31 days with/without compression) |
| `dateFormat` | No | String | Date format |
| `includes` | No | String | Related entities (StandardFields,PatientInformation) |
| `$select/$filter/$orderby/$expand` | No | OData | Standard OData params |

---

### Organization

`GET /organization`

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `OrganizationKey` | Yes | GUID | Organization identifier |

---

## Pagination

Some endpoints support pagination:

- `page` - Page number
- `limit` - Records per page

The `/request/approved` endpoint uses token-based pagination:
- `pageToken` - Token specifying which result page to return
- `syncToken` - Token from previous request's `nextSyncToken` for incremental sync
- `maxResults` - Max items per page (default: 100, max: 100)
