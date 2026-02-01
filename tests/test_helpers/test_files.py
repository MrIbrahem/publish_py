"""Tests for helpers.files module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.app_main.helpers.files import _get_rand_id, get_reports_dir, to_do


class TestGetRandId:
    """Tests for _get_rand_id function."""

    def test_returns_consistent_id_within_process(self):
        """Test that the same rand_id is returned within a process."""
        id1 = _get_rand_id()
        id2 = _get_rand_id()
        assert id1 == id2

    def test_returns_8_character_string(self):
        """Test that rand_id is 8 characters long."""
        rand_id = _get_rand_id()
        assert len(rand_id) == 8
        assert isinstance(rand_id, str)


class TestGetReportsDir:
    """Tests for get_reports_dir function."""

    def test_creates_directory_structure(self, monkeypatch):
        """Test that the reports directory structure is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_paths = SimpleNamespace(
                publish_reports_dir=f"{tmpdir}/publish_reports/reports_by_day",
                log_dir=tmpdir,
            )
            mock_settings = SimpleNamespace(paths=mock_paths)
            monkeypatch.setattr("src.app_main.helpers.files.settings", mock_settings)

            reports_dir = get_reports_dir()
            assert reports_dir.exists()
            assert reports_dir.is_dir()

    def test_follows_expected_structure(self, monkeypatch):
        """Test that the directory follows YYYY/MM/DD/rand_id structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_paths = SimpleNamespace(
                publish_reports_dir=f"{tmpdir}/publish_reports/reports_by_day",
                log_dir=tmpdir,
            )
            mock_settings = SimpleNamespace(paths=mock_paths)
            monkeypatch.setattr("src.app_main.helpers.files.settings", mock_settings)

            reports_dir = get_reports_dir()
            now = datetime.now()

            # Check path components
            path_parts = reports_dir.parts
            assert "publish_reports" in path_parts
            assert "reports_by_day" in path_parts
            assert str(now.year) in path_parts
            assert f"{now.month:02d}" in path_parts
            assert f"{now.day:02d}" in path_parts


class TestToDo:
    """Tests for to_do function."""

    def test_writes_to_log_file(self, monkeypatch):
        """Test that to_do writes to the log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_paths = SimpleNamespace(
                log_dir=tmpdir,
                publish_reports_dir=f"{tmpdir}/publish_reports/reports_by_day",
            )
            mock_settings = SimpleNamespace(paths=mock_paths)
            monkeypatch.setattr("src.app_main.helpers.files.settings", mock_settings)

            tab = {"title": "Test Page", "user": "TestUser"}
            to_do(tab, "success")

            # Check log file exists
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = Path(tmpdir) / f"publish_{today}.json"
            assert log_file.exists()

            # Check content
            with open(log_file, "r") as f:
                content = f.read()
                entry = json.loads(content.strip())
                assert entry["title"] == "Test Page"
                assert entry["user"] == "TestUser"
                assert entry["status"] == "success"
                assert "time" in entry
                assert "time_date" in entry

    def test_writes_to_reports_directory(self, monkeypatch):
        """Test that to_do writes to reports_by_day directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_paths = SimpleNamespace(
                log_dir=tmpdir,
                publish_reports_dir=f"{tmpdir}/publish_reports/reports_by_day",
            )
            mock_settings = SimpleNamespace(paths=mock_paths)
            monkeypatch.setattr("src.app_main.helpers.files.settings", mock_settings)

            tab = {"title": "Test Page", "user": "TestUser"}
            to_do(tab, "success")

            # Check reports_by_day file exists
            reports_dir = Path(tmpdir) / "publish_reports" / "reports_by_day"
            assert reports_dir.exists()

            # Find the success.json file
            now = datetime.now()
            year_dir = reports_dir / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
            assert year_dir.exists()

            # Find subdirectory with rand_id
            subdirs = list(year_dir.iterdir())
            assert len(subdirs) >= 1

            success_file = subdirs[0] / "success.json"
            assert success_file.exists()

            with open(success_file, "r") as f:
                data = json.load(f)
                assert data["title"] == "Test Page"
                assert data["status"] == "success"

    def test_adds_timestamp_fields(self, monkeypatch):
        """Test that to_do adds time and time_date fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_paths = SimpleNamespace(
                log_dir=tmpdir,
                publish_reports_dir=f"{tmpdir}/publish_reports/reports_by_day",
            )
            mock_settings = SimpleNamespace(paths=mock_paths)
            monkeypatch.setattr("src.app_main.helpers.files.settings", mock_settings)

            tab = {"title": "Test"}
            to_do(tab, "test")

            today = datetime.now().strftime("%Y-%m-%d")
            log_file = Path(tmpdir) / f"publish_{today}.json"

            with open(log_file, "r") as f:
                entry = json.loads(f.read().strip())
                assert "time" in entry
                assert "time_date" in entry
                assert isinstance(entry["time"], int)
                assert isinstance(entry["time_date"], str)
