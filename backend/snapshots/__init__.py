"""Snapshot system for mission approval gates.

Snapshots are taken automatically by version-keeper at each /approve event.
Stored in missions/{id}/snapshots/{index:03d}_{label}.json
Each snapshot contains: stage, label, timestamp, content (inline copies of all
intermediate files at that point), diff from previous snapshot.

This module provides the core snapshot read/write/diff/restore API.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SNAPSHOT_RE = re.compile(r'^(\d{3})_(.+)\.json$')


def create_snapshot(
    mission_dir: Path,
    label: str,
    stage: int,
    content: dict[str, Any],
) -> Path:
    """Create a new snapshot for the mission at the current stage.

    Args:
        mission_dir: Path to missions/{id}/
        label: human-readable label, e.g. "narrative_approved"
        stage: current pipeline stage number (1-6)
        content: dict of filename -> file_content to snapshot

    Returns:
        Path to written snapshot file.
    """
    snapshots_dir = mission_dir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)

    existing = list_snapshots(mission_dir)
    index = len(existing)

    diff = {}
    if existing:
        prev = load_snapshot(existing[-1])
        prev_content = prev.get("content", {})
        for fname, new_data in content.items():
            if fname not in prev_content:
                diff[fname] = {"change": "added"}
            elif prev_content[fname] != new_data:
                diff[fname] = {"change": "modified"}
    else:
        diff = {fname: {"change": "added"} for fname in content}

    snapshot = {
        "index": index,
        "label": label,
        "stage": stage,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content,
        "diff_from_previous": diff,
    }

    safe_label = re.sub(r'[^\w-]', '_', label)
    path = snapshots_dir / f"{index:03d}_{safe_label}.json"
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return path


def list_snapshots(mission_dir: Path) -> list[Path]:
    """Return sorted list of snapshot file paths."""
    snapshots_dir = mission_dir / "snapshots"
    if not snapshots_dir.exists():
        return []
    snapshots = [
        f for f in snapshots_dir.iterdir()
        if f.is_file() and SNAPSHOT_RE.match(f.name)
    ]
    return sorted(snapshots)


def load_snapshot(snapshot_path: Path) -> dict:
    """Load a snapshot file."""
    return json.loads(snapshot_path.read_text())


def restore_snapshot(
    mission_dir: Path,
    snapshot_index: int,
) -> dict[str, Any]:
    """Restore mission files from snapshot index."""
    snapshots = list_snapshots(mission_dir)
    if snapshot_index >= len(snapshots):
        raise IndexError(f"Snapshot {snapshot_index} not found (have {len(snapshots)})")

    snapshot = load_snapshot(snapshots[snapshot_index])
    content = snapshot.get("content", {})

    for filename, data in content.items():
        target = mission_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, (dict, list)):
            target.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            target.write_text(str(data))

    return content


def snapshot_from_mission_files(mission_dir: Path) -> dict[str, Any]:
    """Build a content dict from current mission files for snapshot creation."""
    content = {}
    for fname in ["narrative.json", "asset-manifest.json", "encounters.json", "current-stage.json"]:
        fp = mission_dir / fname
        if fp.exists():
            try:
                content[fname] = json.loads(fp.read_text())
            except json.JSONDecodeError:
                content[fname] = fp.read_text()
    return content
