"""Unit tests for backend validators.

Tests schema validator + cross-file consistency validator.
Run with: backend/.venv/bin/pytest backend/tests/test_validators.py -v
"""
import json
import pytest
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.validators.schema import validate_mission_tree, ValidationReport, CORE_GUID
from backend.validators.cross_file import validate_cross_file_consistency


@pytest.fixture
def fake_catalog():
    """Minimal catalog index for testing."""
    return {
        "version": 1,
        "total_assets": 3,
        "core_guid": CORE_GUID,
        "guid_to_type": {
            "ABCDEF1234567890": "gamemode",
            "0987654321FEDCBA": "spawnpoint",
            "FEDCBA0987654321": "faction",
        },
        "by_type": {"gamemode": 1, "spawnpoint": 1, "faction": 1},
        "sources": ["test"],
    }


@pytest.fixture
def valid_output_tree(tmp_path, fake_catalog):
    """Create a valid minimal mission output tree."""
    # addon.gproj with core dep
    (tmp_path / "addon.gproj").write_text(
        f'GameProject {{\n ID "Test"\n GUID "{{ABCDEF1234567890}}"\n'
        f' Dependencies {{\n  "{CORE_GUID}"\n }}\n}}\n'
    )

    missions = tmp_path / "Missions"
    missions.mkdir()
    worlds = tmp_path / "Worlds"
    worlds.mkdir()

    # .conf
    (missions / "TestMission.conf").write_text(
        'SCR_MissionHeader {\n'
        f' World "{{ABCDEF1234567890}}Worlds/TestMission.ent"\n'
        ' m_sName "Test"\n'
        ' m_sGameMode "Coop"\n'
        ' m_iPlayerCount 4\n'
        ' m_sDescription "Test | AI-assisted authoring."\n'
        '}\n'
    )

    # .conf.meta
    (missions / "TestMission.conf.meta").write_text(
        'MetaFileClass {\n'
        f' Name "{{0987654321FEDCBA}}Missions/TestMission.conf"\n'
        '}\n'
    )

    # .ent
    (worlds / "TestMission.ent").write_text(
        'SubScene {\n Parent "worlds/Everon/Everon.ent"\n}\n'
    )

    # .layer
    (worlds / "TestMission_gamemode.layer").write_text(
        f'SCR_CoopGameMode CoopGameMode : "{{ABCDEF1234567890}}Prefabs/Coop.et" {{\n}}\n'
    )

    return tmp_path


class TestSchemaValidator:
    def test_valid_tree_passes(self, valid_output_tree, fake_catalog):
        report = validate_mission_tree(valid_output_tree, fake_catalog)
        assert report.passed, f"Expected pass but got: {[str(e) for e in report.errors]}"

    def test_missing_gproj_fails(self, tmp_path, fake_catalog):
        # Create partial tree without gproj
        (tmp_path / "Missions").mkdir()
        (tmp_path / "Worlds").mkdir()
        report = validate_mission_tree(tmp_path, fake_catalog)
        assert not report.passed
        assert any("addon.gproj" in str(e) for e in report.errors)

    def test_missing_core_dep_fails(self, tmp_path, fake_catalog):
        (tmp_path / "addon.gproj").write_text(
            'GameProject {\n ID "Test"\n Dependencies {\n  "AABBCCDD11223344"\n }\n}\n'
        )
        (tmp_path / "Missions").mkdir()
        (tmp_path / "Worlds").mkdir()
        report = validate_mission_tree(tmp_path, fake_catalog)
        assert not report.passed
        assert any("core" in str(e).lower() for e in report.errors)

    def test_hallucinated_guid_fails(self, tmp_path, fake_catalog):
        (tmp_path / "addon.gproj").write_text(
            f'GameProject {{\n ID "Test"\n Dependencies {{\n  "{CORE_GUID}"\n }}\n}}\n'
        )
        missions = tmp_path / "Missions"
        missions.mkdir()
        worlds = tmp_path / "Worlds"
        worlds.mkdir()
        # Layer with hallucinated GUID
        (worlds / "Test_gamemode.layer").write_text(
            'SCR_CoopGameMode : "{DEADBEEFDEADBEEF}Fake/Path.et" {}\n'
        )
        (missions / "Test.conf").write_text(
            'SCR_MissionHeader {\n'
            f' World "{{ABCDEF1234567890}}Worlds/Test.ent"\n'
            ' m_sName "Test"\n m_sGameMode "Coop"\n m_iPlayerCount 4\n}\n'
        )

        report = validate_mission_tree(tmp_path, fake_catalog)
        assert not report.passed
        assert any("DEADBEEFDEADBEEF" in str(e) for e in report.errors)

    def test_player_count_1_emits_warning(self, tmp_path, fake_catalog):
        """Solo coop (1 player) is valid in Reforger — emits WARNING, not error."""
        (tmp_path / "addon.gproj").write_text(
            f'GameProject {{\n ID "Test"\n Dependencies {{\n  "{CORE_GUID}"\n }}\n}}\n'
        )
        missions = tmp_path / "Missions"
        missions.mkdir()
        (tmp_path / "Worlds").mkdir()
        (missions / "Test.conf").write_text(
            'SCR_MissionHeader {\n'
            f' World "{{ABCDEF1234567890}}Worlds/Test.ent"\n'
            ' m_sName "Test"\n m_sGameMode "Coop"\n m_iPlayerCount 1\n}\n'
        )

        report = validate_mission_tree(tmp_path, fake_catalog, [])
        # 1 player in coop = warning only (solo play is supported), not an error
        assert any("player" in str(w).lower() for w in report.warnings), (
            f"Expected a player-count warning, got none. warnings={report.warnings}"
        )
        # Only error should be the missing ABCDEF1234567890 GUID (not in fake_catalog)
        # Rule 6 must NOT produce an error for count=1
        player_errors = [e for e in report.errors if "player" in str(e).lower()]
        assert not player_errors, f"Rule 6 should not be an error for count=1: {player_errors}"

    def test_player_count_0_fails(self, tmp_path, fake_catalog):
        """player_count=0 is invalid — must produce an error."""
        (tmp_path / "addon.gproj").write_text(
            f'GameProject {{\n ID "Test"\n Dependencies {{\n  "{CORE_GUID}"\n }}\n}}\n'
        )
        missions = tmp_path / "Missions"
        missions.mkdir()
        (tmp_path / "Worlds").mkdir()
        (missions / "Test.conf").write_text(
            'SCR_MissionHeader {\n'
            f' World "{{ABCDEF1234567890}}Worlds/Test.ent"\n'
            ' m_sName "Test"\n m_sGameMode "Coop"\n m_iPlayerCount 0\n}\n'
        )

        report = validate_mission_tree(tmp_path, fake_catalog, [])
        assert not report.passed
        assert any("player" in str(e).lower() for e in report.errors), (
            f"Expected player-count error for count=0. errors={report.errors}"
        )

    def test_embedded_asset_fails(self, valid_output_tree, fake_catalog):
        # Create a .pak file which is not allowed
        (valid_output_tree / "bad.pak").write_text("pak content")
        report = validate_mission_tree(valid_output_tree, fake_catalog)
        assert not report.passed
        assert any("pak" in str(e).lower() or "EULA" in str(e) for e in report.errors)

    def test_mint_log_guids_allowed(self, valid_output_tree, fake_catalog):
        """Locally minted GUIDs should not be flagged as hallucinations."""
        worlds = valid_output_tree / "Worlds"
        minted_guid = "AABB1122CCDD3344"
        (worlds / "Test_extra.layer").write_text(
            f'SomeClass inst : "{{{minted_guid}}}path.et" {{}}\n'
        )
        report = validate_mission_tree(valid_output_tree, fake_catalog, mission_mint_log=[minted_guid])
        # Should pass with mint log containing the GUID
        assert report.passed or not any(minted_guid in str(e) for e in report.errors)

    def test_report_to_dict(self, valid_output_tree, fake_catalog):
        report = validate_mission_tree(valid_output_tree, fake_catalog)
        d = report.to_dict()
        assert "passed" in d
        assert "error_count" in d
        assert "errors" in d
        assert isinstance(d["errors"], list)


class TestCrossFileValidator:
    def test_no_manifest_warns(self, tmp_path):
        report = validate_cross_file_consistency(tmp_path, tmp_path / "output")
        # Should warn, not error
        assert report.passed  # no errors, just warnings about missing manifest

    def test_halt_required_errors(self, tmp_path):
        manifest = {
            "resolved_assets": [],
            "missing_assets": [{"narrative_ref": "MISSING_THING"}],
            "halt_required": True,
            "halt_reason": "asset not found",
        }
        (tmp_path / "asset-manifest.json").write_text(json.dumps(manifest))
        report = validate_cross_file_consistency(tmp_path, tmp_path / "output")
        assert not report.passed
        assert any("halt_required" in str(e) for e in report.errors)

    def test_halt_false_missing_is_warning(self, tmp_path):
        """halt_required=false + missing_assets → warning only, not error."""
        manifest = {
            "resolved_assets": [],
            "missing_assets": [{"narrative_ref": "SOME_ASSET"}],
            "halt_required": False,
            "halt_reason": None,
        }
        (tmp_path / "asset-manifest.json").write_text(json.dumps(manifest))
        report = validate_cross_file_consistency(tmp_path, tmp_path / "output")
        assert report.passed  # no hard errors
        assert len(report.warnings) > 0  # but has warnings
