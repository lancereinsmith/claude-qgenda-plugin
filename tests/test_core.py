"""Tests for qgenda_core shared logic."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

import qgenda_core as core


class TestCheckEnv:
    def _clear_qgenda_env(self, monkeypatch):
        """Remove all QGenda env vars."""
        for var in ("QGENDA_CONF_FILE", "QGENDA_EMAIL", "QGENDA_PASSWORD", "QGENDA_COMPANY_KEY"):
            monkeypatch.delenv(var, raising=False)

    def test_no_config_at_all(self, monkeypatch):
        self._clear_qgenda_env(monkeypatch)
        monkeypatch.setattr(os.path, "exists", lambda p: False)
        with pytest.raises(RuntimeError, match="credentials not configured"):
            core.check_env()

    def test_conf_file_missing(self, monkeypatch, tmp_path):
        self._clear_qgenda_env(monkeypatch)
        monkeypatch.setenv("QGENDA_CONF_FILE", str(tmp_path / "nope.conf"))
        with pytest.raises(RuntimeError, match="not found"):
            core.check_env()

    def test_conf_file_valid(self, monkeypatch, tmp_path):
        self._clear_qgenda_env(monkeypatch)
        conf = tmp_path / "qgenda.conf"
        conf.write_text("[qgenda]\n")
        monkeypatch.setenv("QGENDA_CONF_FILE", str(conf))
        assert core.check_env() == str(conf)

    def test_tilde_expansion(self, monkeypatch, tmp_path):
        self._clear_qgenda_env(monkeypatch)
        conf = tmp_path / "qgenda.conf"
        conf.write_text("[qgenda]\n")
        monkeypatch.setenv("QGENDA_CONF_FILE", "~/qgenda.conf")
        monkeypatch.setattr(
            os.path, "expanduser", lambda p: str(conf) if "~" in p else p
        )
        monkeypatch.setattr(os.path, "exists", lambda p: p == str(conf))
        assert core.check_env() == str(conf)

    def test_env_vars_all_set(self, monkeypatch):
        self._clear_qgenda_env(monkeypatch)
        monkeypatch.setenv("QGENDA_EMAIL", "user@example.com")
        monkeypatch.setenv("QGENDA_PASSWORD", "secret")
        monkeypatch.setenv("QGENDA_COMPANY_KEY", "key-123")
        assert core.check_env() is None

    def test_env_vars_partial(self, monkeypatch):
        self._clear_qgenda_env(monkeypatch)
        monkeypatch.setenv("QGENDA_EMAIL", "user@example.com")
        with pytest.raises(RuntimeError, match="Partial QGenda env config"):
            core.check_env()

    def test_conf_file_takes_precedence(self, monkeypatch, tmp_path):
        """When both config file and env vars are set, config file wins."""
        self._clear_qgenda_env(monkeypatch)
        conf = tmp_path / "qgenda.conf"
        conf.write_text("[qgenda]\n")
        monkeypatch.setenv("QGENDA_CONF_FILE", str(conf))
        monkeypatch.setenv("QGENDA_EMAIL", "user@example.com")
        monkeypatch.setenv("QGENDA_PASSWORD", "secret")
        monkeypatch.setenv("QGENDA_COMPANY_KEY", "key-123")
        assert core.check_env() == str(conf)

    def test_empty_conf_file_ignored(self, monkeypatch):
        """Empty QGENDA_CONF_FILE (e.g., blank userConfig) is treated as unset."""
        self._clear_qgenda_env(monkeypatch)
        monkeypatch.setenv("QGENDA_CONF_FILE", "")
        monkeypatch.setenv("QGENDA_EMAIL", "user@example.com")
        monkeypatch.setenv("QGENDA_PASSWORD", "secret")
        monkeypatch.setenv("QGENDA_COMPANY_KEY", "key-123")
        assert core.check_env() is None

    def test_default_conf_file(self, monkeypatch, tmp_path):
        """Falls back to ~/.qgenda.conf when nothing else is configured."""
        self._clear_qgenda_env(monkeypatch)
        default_conf = tmp_path / ".qgenda.conf"
        default_conf.write_text("[qgenda]\n")
        monkeypatch.setattr(
            os.path, "expanduser", lambda p: str(default_conf) if "~" in p else p
        )
        monkeypatch.setattr(os.path, "exists", lambda p: p == str(default_conf))
        assert core.check_env() == str(default_conf)


class TestBuildOdata:
    def test_empty_returns_none(self):
        assert core.build_odata() is None

    def test_explicit_select(self):
        result = core.build_odata(select="FirstName,LastName")
        assert result is not None
        params = result.to_params()
        assert params["$select"] == "FirstName,LastName"

    def test_default_select_for_endpoint(self):
        result = core.build_odata(endpoint="schedule")
        assert result is not None
        params = result.to_params()
        assert params["$select"] == ",".join(core.DEFAULT_SELECT["schedule"])

    def test_explicit_overrides_default(self):
        result = core.build_odata(select="TaskName", endpoint="schedule")
        params = result.to_params()
        assert params["$select"] == "TaskName"

    def test_all_params(self):
        result = core.build_odata(
            select="A,B",
            filter_expr="StaffLName eq 'Smith'",
            orderby="StartDate desc",
        )
        params = result.to_params()
        assert params["$select"] == "A,B"
        assert params["$filter"] == "StaffLName eq 'Smith'"
        assert params["$orderby"] == "StartDate desc"

    def test_unknown_endpoint_no_default(self):
        result = core.build_odata(endpoint="unknown")
        assert result is None

    def test_expand_param(self):
        result = core.build_odata(expand="Tags")
        params = result.to_params()
        assert params["$expand"] == "Tags"

    def test_expand_with_other_params(self):
        result = core.build_odata(
            select="A,B",
            filter_expr="X eq 1",
            orderby="A",
            expand="Tags,Profiles",
        )
        params = result.to_params()
        assert params["$select"] == "A,B"
        assert params["$filter"] == "X eq 1"
        assert params["$orderby"] == "A"
        assert params["$expand"] == "Tags,Profiles"


class TestFormatResponse:
    def test_json_format(self):
        out = core.format_response([{"a": 1}], "json")
        assert json.loads(out) == [{"a": 1}]

    def test_csv_format(self):
        data = [{"Name": "Alice", "Age": "30"}, {"Name": "Bob", "Age": "25"}]
        out = core.format_response(data, "csv")
        assert "Name,Age" in out
        assert "Alice,30" in out
        assert "Bob,25" in out

    def test_table_format(self):
        data = [{"Name": "Alice"}, {"Name": "Bob"}]
        out = core.format_response(data, "table")
        assert "Name" in out
        assert "----" in out
        assert "Alice" in out
        assert "Bob" in out

    def test_empty_list_falls_back_to_json(self):
        out = core.format_response([], "table")
        assert out == "[]"

    def test_non_list_falls_back_to_json(self):
        out = core.format_response({"error": "not found"}, "csv")
        assert "not found" in out


def _mock_response(data):
    """Create a mock QGendaResponse with .data attribute."""
    resp = MagicMock()
    resp.data = data
    return resp


class TestClientCaching:
    def setup_method(self):
        core._client = None

    @patch("qgenda_core.check_env")
    @patch("qgenda_core.QGendaClient")
    def test_caches_client(self, mock_cls, mock_env):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        c1 = core.get_client()
        c2 = core.get_client()

        assert c1 is c2
        assert mock_cls.call_count == 1

    def teardown_method(self):
        core._client = None


class TestQuerySchedule:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.schedule.list.return_value = _mock_response(
            [{"StaffLName": "Smith", "TaskName": "CT"}]
        )
        mock_get_client.return_value = client

        result = core.query_schedule(start_date="2026-03-18")
        data = json.loads(result)
        assert data[0]["StaffLName"] == "Smith"
        client.schedule.list.assert_called_once()

    @patch("qgenda_core.get_client")
    def test_with_includes(self, mock_get_client):
        client = MagicMock()
        client.schedule.list.return_value = _mock_response([])
        mock_get_client.return_value = client

        core.query_schedule(start_date="2026-03-18", includes="StaffTags,TaskTags")
        call_kwargs = client.schedule.list.call_args[1]
        assert call_kwargs["includes"] == "StaffTags,TaskTags"


class TestQueryOpenShifts:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.schedule.open_shifts.return_value = _mock_response(
            [{"ShiftName": "Open CT"}]
        )
        mock_get_client.return_value = client

        result = core.query_open_shifts(start_date="2026-03-18")
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["ShiftName"] == "Open CT"
        client.schedule.open_shifts.assert_called_once()

    @patch("qgenda_core.get_client")
    def test_with_includes(self, mock_get_client):
        client = MagicMock()
        client.schedule.open_shifts.return_value = _mock_response([])
        mock_get_client.return_value = client

        core.query_open_shifts(start_date="2026-03-18", includes="TaskTags,LocationTags")
        call_kwargs = client.schedule.open_shifts.call_args[1]
        assert call_kwargs["includes"] == "TaskTags,LocationTags"


class TestQueryRequests:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.request.list.return_value = _mock_response([{"Type": "PTO"}])
        mock_get_client.return_value = client

        result = core.query_requests(start_date="2026-03-18")
        data = json.loads(result)
        assert data[0]["Type"] == "PTO"

    @patch("qgenda_core.get_client")
    def test_include_removed(self, mock_get_client):
        client = MagicMock()
        client.request.list.return_value = _mock_response([])
        mock_get_client.return_value = client

        core.query_requests(start_date="2026-03-18", include_removed=True)
        call_kwargs = client.request.list.call_args[1]
        assert call_kwargs["include_removed"] is True


class TestQueryRotations:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.schedule.rotations.return_value = _mock_response(
            [{"Rotation": "A"}]
        )
        mock_get_client.return_value = client

        result = core.query_rotations(
            range_start_date="2026-03-01", range_end_date="2026-03-31"
        )
        data = json.loads(result)
        assert data[0]["Rotation"] == "A"

        call_kwargs = client.schedule.rotations.call_args[1]
        assert call_kwargs["range_start_date"] == "2026-03-01"
        assert call_kwargs["range_end_date"] == "2026-03-31"


class TestQueryScheduleAuditLog:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.schedule.audit_log.return_value = _mock_response(
            [{"Action": "Edit"}]
        )
        mock_get_client.return_value = client

        result = core.query_schedule_audit_log(
            schedule_start_date="2026-03-01", schedule_end_date="2026-03-31"
        )
        data = json.loads(result)
        assert data[0]["Action"] == "Edit"

    @patch("qgenda_core.get_client")
    def test_since_modified(self, mock_get_client):
        client = MagicMock()
        client.schedule.audit_log.return_value = _mock_response([])
        mock_get_client.return_value = client

        ts = "2026-03-01T00:00:00Z"
        core.query_schedule_audit_log(
            schedule_start_date="2026-03-01", since_modified_timestamp=ts,
        )
        call_kwargs = client.schedule.audit_log.call_args[1]
        assert call_kwargs["since_modified_timestamp"] == ts


class TestQueryStaffMember:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.staff.get.return_value = _mock_response(
            {"FirstName": "Jane", "LastName": "Doe"}
        )
        mock_get_client.return_value = client

        result = core.query_staff_member("staff-guid-123")
        data = json.loads(result)
        assert data["FirstName"] == "Jane"

        client.staff.get.assert_called_once_with("staff-guid-123", odata=None)


class TestQueryDailyConfiguration:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.daily.configurations.return_value = _mock_response(
            [{"Name": "Config A"}]
        )
        mock_get_client.return_value = client

        result = core.query_daily_configuration()
        data = json.loads(result)
        assert data[0]["Name"] == "Config A"


class TestQueryRooms:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.daily.rooms.return_value = _mock_response(
            [{"RoomName": "Room 1"}]
        )
        mock_get_client.return_value = client

        result = core.query_rooms()
        data = json.loads(result)
        assert data[0]["RoomName"] == "Room 1"


class TestQueryPatientEncounters:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.daily.patient_encounters.return_value = _mock_response(
            [{"PatientFirstName": "John"}]
        )
        mock_get_client.return_value = client

        result = core.query_patient_encounters(
            daily_configuration_key="config-key-123",
            start_date="2026-03-18",
        )
        data = json.loads(result)
        assert data[0]["PatientFirstName"] == "John"

        call_kwargs = client.daily.patient_encounters.call_args[1]
        assert call_kwargs["daily_configuration_key"] == "config-key-123"
        assert call_kwargs["start_date"] == "2026-03-18"

    @patch("qgenda_core.get_client")
    def test_with_includes(self, mock_get_client):
        client = MagicMock()
        client.daily.patient_encounters.return_value = _mock_response([])
        mock_get_client.return_value = client

        core.query_patient_encounters(
            daily_configuration_key="config-key",
            start_date="2026-03-18",
            includes="StandardFields,PatientInformation",
        )
        call_kwargs = client.daily.patient_encounters.call_args[1]
        assert call_kwargs["includes"] == "StandardFields,PatientInformation"


class TestQueryStaff:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.staff.list.return_value = _mock_response(
            [{"FirstName": "Jane", "LastName": "Doe"}]
        )
        mock_get_client.return_value = client

        result = core.query_staff()
        data = json.loads(result)
        assert data[0]["FirstName"] == "Jane"


class TestQueryTasks:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.task.list.return_value = _mock_response(
            [{"TaskName": "CT", "TaskKey": "abc"}]
        )
        mock_get_client.return_value = client

        result = core.query_tasks()
        data = json.loads(result)
        assert data[0]["TaskName"] == "CT"


class TestQueryFacilities:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.facility.list.return_value = _mock_response(
            [{"FacilityName": "Main Hospital"}]
        )
        mock_get_client.return_value = client

        result = core.query_facilities()
        data = json.loads(result)
        assert data[0]["FacilityName"] == "Main Hospital"


class TestQueryTimeEvents:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.time_event.list.return_value = _mock_response(
            [{"StaffLName": "Smith"}]
        )
        mock_get_client.return_value = client

        result = core.query_time_events(start_date="2026-03-18")
        data = json.loads(result)
        assert data[0]["StaffLName"] == "Smith"


class TestQueryDailyCases:
    @patch("qgenda_core.get_client")
    def test_basic_call(self, mock_get_client):
        client = MagicMock()
        client.daily_case.list.return_value = _mock_response(
            [{"TaskName": "CT"}]
        )
        mock_get_client.return_value = client

        result = core.query_daily_cases(start_date="2026-03-18")
        data = json.loads(result)
        assert data[0]["TaskName"] == "CT"
