"""Unit tests for the snapshot system.

Tests create/list/load/restore functionality.
Run with: backend/.venv/bin/pytest backend/tests/test_snapshots.py -v
"""
import json
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.snapshots import (
    create_snapshot, list_snapshots, load_snapshot,
    restore_snapshot, snapshot_from_mission_files
)


@pytest.fixture
def mission_dir(tmp_path):
    """Create a minimal mission directory."""
    narrative = {"title": "Test Mission", "factions": {"player": {"id": "US"}}}
    (tmp_path / "narrative.json").write_text(json.dumps(narrative))
    (tmp_path / "current-stage.json").write_text(json.dumps({"stage": 1}))
    return tmp_path


class TestSnapshots:
    def test_create_snapshot(self, mission_dir):
        snap_path = create_snapshot(
            mission_dir, "test_label", stage=1,
            content={"narrative.json": {"title": "Test"}}
        )
        assert snap_path.exists()
        assert snap_path.name == "000_test_label.json"

    def test_list_snapshots(self, mission_dir):
        create_snapshot(mission_dir, "first", stage=1, content={"a": 1})
        create_snapshot(mission_dir, "second", stage=2, content={"b": 2})
        snaps = list_snapshots(mission_dir)
        assert len(snaps) == 2
        assert "000_first.json" in [s.name for s in snaps]
        assert "001_second.json" in [s.name for s in snaps]

    def test_list_empty(self, tmp_path):
        assert list_snapshots(tmp_path) == []

    def test_load_snapshot(self, mission_dir):
        content = {"narrative.json": {"title": "Loaded"}}
        snap_path = create_snapshot(mission_dir, "loadtest", stage=3, content=content)
        loaded = load_snapshot(snap_path)
        assert loaded["label"] == "loadtest"
        assert loaded["stage"] == 3
        assert loaded["content"]["narrative.json"]["title"] == "Loaded"

    def test_snapshot_has_timestamp(self, mission_dir):
        snap_path = create_snapshot(mission_dir, "ts_test", stage=1, content={})
        loaded = load_snapshot(snap_path)
        assert "timestamp" in loaded
        assert "+00:00" in loaded["timestamp"] or "Z" in loaded["timestamp"]  # ISO UTC

    def test_snapshot_diff_added(self, mission_dir):
        snap1 = create_snapshot(mission_dir, "s1", stage=1, content={"a.json": {"x": 1}})
        snap2 = create_snapshot(mission_dir, "s2", stage=2, content={"a.json": {"x": 2}, "b.json": {}})
        loaded2 = load_snapshot(snap2)
        diff = loaded2["diff_from_previous"]
        assert diff.get("a.json", {}).get("change") == "modified"
        assert diff.get("b.json", {}).get("change") == "added"

    def test_restore_snapshot(self, mission_dir):
        # Create snapshot with known content
        content = {"narrative.json": {"title": "Restored Title"}}
        create_snapshot(mission_dir, "restore_test", stage=1, content=content)

        # Overwrite narrative.json
        (mission_dir / "narrative.json").write_text(json.dumps({"title": "Changed"}))

        # Restore
        restored = restore_snapshot(mission_dir, snapshot_index=0)
        assert restored["narrative.json"]["title"] == "Restored Title"

        # Verify file was actually written
        actual = json.loads((mission_dir / "narrative.json").read_text())
        assert actual["title"] == "Restored Title"

    def test_restore_invalid_index_raises(self, mission_dir):
        with pytest.raises(IndexError):
            restore_snapshot(mission_dir, snapshot_index=99)

    def test_snapshot_from_files(self, mission_dir):
        content = snapshot_from_mission_files(mission_dir)
        assert "narrative.json" in content
        assert content["narrative.json"]["title"] == "Test Mission"
        assert "current-stage.json" in content

    def test_safe_label_sanitization(self, mission_dir):
        """Labels with special chars are sanitized for filename safety."""
        snap = create_snapshot(mission_dir, "my label! @#$", stage=1, content={})
        # Should not have dangerous chars in filename
        assert " " not in snap.name
        assert "!" not in snap.name
