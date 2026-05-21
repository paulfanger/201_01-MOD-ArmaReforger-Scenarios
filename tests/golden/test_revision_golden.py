"""
Golden trajectory regression tests for the revisions endpoint.

These tests apply known JSON-Patch operations and verify:
1. Schema validity pre and post
2. Expected delta (key fields changed)
3. Invariants preserved (key fields unchanged)

Run with: pytest tests/golden/test_revision_golden.py -v
"""

import copy
import json
from pathlib import Path

import jsonpatch
import jsonschema
import pytest

REPO_ROOT = Path(__file__).parents[2]
GOLDEN_DIR = Path(__file__).parent
FIXTURES_DIR = REPO_ROOT / "backend" / "tests" / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


NARRATIVE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["title", "factions", "biome", "tone", "pacing"],
    "properties": {
        "title": {"type": "string"},
        "factions": {
            "type": "object",
            "required": ["player", "ai"],
            "properties": {
                "player": {"type": "object", "required": ["id"]},
                "ai": {"type": "object", "required": ["id"]},
            },
        },
        "biome": {"type": "object", "required": ["map_id_ref"]},
        "tone": {"type": "object", "required": ["primary"]},
        "pacing": {"type": "object"},
    },
    "additionalProperties": True,
}


def validate_narrative(data: dict) -> None:
    jsonschema.validate(data, NARRATIVE_SCHEMA)


def get_nested(obj: dict, json_pointer: str):
    """Resolve a simple JSON pointer path (no escaping)."""
    parts = json_pointer.lstrip("/").split("/")
    cur = obj
    for p in parts:
        cur = cur[p]
    return cur


# ---------------------------------------------------------------------------
# Test: baseline narrative validates
# ---------------------------------------------------------------------------

def test_night_recon_baseline_schema():
    """Golden baseline narrative must pass schema validation."""
    narrative = load_json(FIXTURES_DIR / "night_recon_narrative.json")
    validate_narrative(narrative)  # Should not raise


# ---------------------------------------------------------------------------
# Test: revision 01 — tone change
# ---------------------------------------------------------------------------

def test_night_recon_revision_01():
    """Apply revision 01 patch, verify delta + invariants."""
    narrative_path = FIXTURES_DIR / "night_recon_narrative.json"
    revision_path = GOLDEN_DIR / "night_recon_revision_01.json"

    if not narrative_path.exists():
        pytest.skip("Fixture not found")

    narrative = load_json(narrative_path)
    revision = load_json(revision_path)

    # Pre-validate
    validate_narrative(narrative)

    # Apply patch
    patch = jsonpatch.JsonPatch(revision["input_patch"])
    after = patch.apply(copy.deepcopy(narrative))

    # Post-validate
    validate_narrative(after)

    # Check expected delta
    for pointer, expected_value in revision["expected_output_delta"].items():
        actual = get_nested(after, pointer)
        assert actual == expected_value, f"Delta check failed: {pointer}: {actual!r} != {expected_value!r}"

    # Check invariants preserved
    for pointer, expected_value in revision["invariants"].items():
        actual = get_nested(after, pointer.replace(".", "/"))
        assert actual == expected_value, f"Invariant violated: {pointer}: {actual!r} != {expected_value!r}"


# ---------------------------------------------------------------------------
# Test: episodic memory
# ---------------------------------------------------------------------------

def test_episodic_memory_basic():
    """Basic round-trip: log + search."""
    import tempfile
    from pathlib import Path
    from backend.memory.episodic import EpisodicMemory

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_episodic.db"
        mem = EpisodicMemory(db_path)
        mem.log("turn-test-1", "pc", "Validate PASS for night-recon", "validate pass")
        results = mem.search("validate night")
        assert len(results) >= 1
        assert results[0]["episode_id"] == "turn-test-1"
        mem.close()


# ---------------------------------------------------------------------------
# Test: cached_completion import works (no API call)
# ---------------------------------------------------------------------------

def test_llm_module_imports():
    """LLM module imports without error (no live API call)."""
    from backend.llm import SYSTEM_PROMPT_PREFIX, _make_cached_system
    assert "mission-authoring" in SYSTEM_PROMPT_PREFIX
    blocks = _make_cached_system()
    assert blocks[0]["cache_control"]["type"] == "ephemeral"


# ---------------------------------------------------------------------------
# Test: revisions schema validation
# ---------------------------------------------------------------------------

def test_revision_schema_rejects_missing_title():
    """Post-patch schema validation must reject removed required field."""
    import jsonschema
    bad = {"factions": {"player": {"id": "US"}, "ai": {"id": "USSR"}}, "biome": {"map_id_ref": "everon"}, "tone": {"primary": "x"}, "pacing": {}}
    with pytest.raises(jsonschema.ValidationError):
        validate_narrative(bad)
