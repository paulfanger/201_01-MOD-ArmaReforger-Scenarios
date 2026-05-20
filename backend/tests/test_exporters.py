"""Unit tests for backend exporters.

Tests that all exporter modules produce valid Enfusion Brace-Syntax output.
Run with: backend/.venv/bin/pytest backend/tests/test_exporters.py -v
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.exporters.braces import serialize, emit_class_block, emit_meta_configurations
from backend.exporters.gproj import generate_gproj, CORE_GUID
from backend.exporters.conf import generate_mission_header, generate_conf_meta, generate_ent_meta
from backend.exporters.ent import generate_world_subscene, generate_world_with_layers, WORLD_PATHS
from backend.exporters.layer import generate_layer, generate_managers_layer
from backend.exporters.mint import mint_guid, mint_unique_guid


# ---- braces.py tests --------------------------------------------------------

class TestBraceSerializer:
    def test_simple_dict(self):
        out = serialize({"key": "value"})
        assert 'key "value"' in out

    def test_nested_dict(self):
        out = serialize({"Outer": {"Inner": "data"}})
        assert "Outer {" in out
        assert 'Inner "data"' in out
        assert "}" in out

    def test_list_values(self):
        out = serialize({"Deps": ["A", "B"]})
        assert "Deps {" in out
        assert '"A"' in out
        assert '"B"' in out

    def test_integer_scalar(self):
        out = serialize({"count": 8})
        assert "count 8" in out

    def test_bool_as_int(self):
        out = serialize({"flag": True})
        assert "flag 1" in out
        out2 = serialize({"flag": False})
        assert "flag 0" in out2

    def test_guid_ref_quoted(self):
        out = serialize({"World": "{ABCDEF1234567890}Worlds/Test.ent"})
        assert '"{ABCDEF1234567890}Worlds/Test.ent"' in out

    def test_top_level_must_be_dict(self):
        with pytest.raises(ValueError):
            serialize(["list"])

    def test_emit_class_block(self):
        out = emit_class_block("SCR_MissionHeader", {"m_sName": "Test"})
        assert "SCR_MissionHeader {" in out
        assert 'm_sName "Test"' in out
        assert "}" in out

    def test_meta_configurations(self):
        out = emit_meta_configurations("CONFResourceClass")
        assert "CONFResourceClass PC {}" in out
        assert "XBOX_ONE : PC" in out
        assert "HEADLESS : PC" in out


# ---- gproj.py tests ---------------------------------------------------------

class TestGprojExporter:
    def test_minimal_gproj(self):
        out = generate_gproj("TestMission", "ABCDEF1234567890", "Test Mission")
        assert "GameProject {" in out
        assert f'"{CORE_GUID}"' in out
        assert 'ID "TestMission"' in out
        assert 'TITLE "Test Mission"' in out

    def test_has_core_dependency(self):
        out = generate_gproj("MyAddon", "1234567890ABCDEF", "My Addon")
        assert CORE_GUID in out

    def test_extra_deps(self):
        out = generate_gproj("MyAddon", "1234567890ABCDEF", "My Addon", extra_deps=["DEADBEEF12345678"])
        assert "DEADBEEF12345678" in out
        assert CORE_GUID in out  # core is always first

    def test_guid_format(self):
        """GUID must be wrapped in braces in the GUID field."""
        out = generate_gproj("Test", "ABCDEF1234567890", "Test")
        assert '"{ABCDEF1234567890}"' in out


# ---- conf.py tests ----------------------------------------------------------

class TestConfExporter:
    WORLD_GUID = "ABCDEF1234567890"
    WORLD_PATH = "Worlds/TestMission.ent"

    def test_minimal_conf(self):
        out = generate_mission_header(
            name="Test Mission",
            description="A test",
            world_guid=self.WORLD_GUID,
            world_path=self.WORLD_PATH,
        )
        assert "SCR_MissionHeader {" in out
        assert f'World "{{{self.WORLD_GUID}}}{self.WORLD_PATH}"' in out
        assert 'm_sName "Test Mission"' in out
        assert 'm_sGameMode "Coop"' in out

    def test_disclosure_injected(self):
        out = generate_mission_header(
            name="Test",
            description="A night mission",
            world_guid=self.WORLD_GUID,
            world_path=self.WORLD_PATH,
        )
        assert "AI" in out  # Disclosure auto-appended

    def test_player_count(self):
        out = generate_mission_header(
            name="Test",
            description="X",
            world_guid=self.WORLD_GUID,
            world_path=self.WORLD_PATH,
            player_count=4,
        )
        assert "m_iPlayerCount 4" in out

    def test_time_of_day(self):
        out = generate_mission_header(
            name="Test",
            description="X",
            world_guid=self.WORLD_GUID,
            world_path=self.WORLD_PATH,
            time_hour=2,
            time_minute=30,
        )
        assert "m_iStartingHours 2" in out
        assert "m_iStartingMinutes 30" in out

    def test_conf_meta(self):
        out = generate_conf_meta("ABCDEF1234567890", "Missions/Test.conf")
        assert "MetaFileClass {" in out
        assert "Configurations {" in out
        assert "PC {}" in out
        assert "HEADLESS : PC {}" in out

    def test_ent_meta(self):
        out = generate_ent_meta("ABCDEF1234567890", "Worlds/Test.ent")
        assert "MetaFileClass {" in out
        assert "Configurations {" in out


# ---- ent.py tests -----------------------------------------------------------

class TestEntExporter:
    def test_subscene_everon(self):
        out = generate_world_subscene("everon")
        assert "SubScene {" in out
        assert "Everon.ent" in out

    def test_subscene_unknown_defaults_everon(self):
        out = generate_world_subscene("unknown_map")
        assert "Everon.ent" in out  # fallback

    def test_layer_table(self):
        out = generate_world_with_layers("night-recon", ["gamemode", "AI"])
        assert "Layer night-recon_gamemode" in out
        assert "Index 0" in out
        assert "Layer night-recon_AI" in out
        assert "Index 1" in out

    def test_all_known_maps(self):
        for map_id in ["everon", "eden", "arland", "malden"]:
            out = generate_world_subscene(map_id)
            assert "SubScene {" in out
            assert ".ent" in out


# ---- layer.py tests ---------------------------------------------------------

class TestLayerExporter:
    SAMPLE_GUID = "904EC091C347AEA9"
    SAMPLE_PATH = "Prefabs/MP/Modes/Coop/CoopGameMode.et"

    def test_single_entity(self):
        entities = [{
            "class_name": "SCR_CoopGameMode",
            "instance_name": "CoopGameMode",
            "prefab_guid": self.SAMPLE_GUID,
            "prefab_path": self.SAMPLE_PATH,
        }]
        out = generate_layer(entities)
        assert "SCR_CoopGameMode CoopGameMode" in out
        assert f"{{{self.SAMPLE_GUID}}}" in out
        assert "}" in out

    def test_entity_with_coords(self):
        entities = [{
            "class_name": "SCR_SpawnPoint",
            "instance_name": "SP_US_01",
            "prefab_guid": self.SAMPLE_GUID,
            "prefab_path": "PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et",
            "coords": [263.5, 9.0, 245.0],
        }]
        out = generate_layer(entities)
        assert "coords 263" in out
        assert "SP_US_01" in out

    def test_grouped_entity(self):
        entities = [{
            "$grp": True,
            "class_name": "SCR_AIWaypoint",
            "prefab_guid": self.SAMPLE_GUID,
            "prefab_path": "Prefabs/AI/Waypoints/SCR_AIWaypoint.et",
            "instances": [
                {"name": "WP_01", "coords": [100, 5, 200]},
                {"name": "WP_02", "coords": [150, 5, 250]},
            ]
        }]
        out = generate_layer(entities)
        assert "$grp SCR_AIWaypoint" in out
        assert "WP_01 {" in out
        assert "WP_02 {" in out

    def test_managers_layer(self):
        out = generate_managers_layer()
        # GameMode is in the gamemode layer (prefab), NOT the managers layer
        # Managers layer has: CoopFactionManager (prefab), LoadoutManager, TimeAndWeather (inline)
        assert "CoopFactionManager" in out           # prefab-based FactionManager
        assert "FactionManager" in out               # present in class name SCR_FactionManager
        assert "TimeAndWeatherManagerEntity" in out
        assert "LoadoutManager" in out
        assert "E4075339B4E24E10" in out             # verified CoopFactionManager GUID
        assert 'SCR_FactionManager CoopFactionManager : "' in out  # prefab entity pattern

    def test_managers_layer_no_standalone_gamemode(self):
        """GameMode is a prefab entity in the gamemode layer, never inline in managers."""
        out = generate_managers_layer()
        # Should NOT have a standalone inline "GameMode GameMode {}" block
        # (SCR_CoopGameMode is in its own gamemode.layer)
        lines = out.split("\n")
        standalone_gamemode = any(
            line.startswith("GameMode ") and "GameMode {" in line
            for line in lines
        )
        assert not standalone_gamemode, "GameMode must not appear inline in managers layer"


# ---- mint.py tests ----------------------------------------------------------

class TestGuidMinter:
    def test_mint_guid_format(self):
        guid = mint_guid()
        assert len(guid) == 16
        assert guid == guid.upper()
        assert all(c in "0123456789ABCDEF" for c in guid)

    def test_mint_uniqueness(self):
        guids = [mint_guid() for _ in range(100)]
        assert len(set(guids)) > 90  # statistically near-certain to be unique

    def test_mint_not_in_catalog(self):
        import json
        catalog_path = ROOT / "catalog" / "INDEX.json"
        if catalog_path.exists():
            catalog = json.loads(catalog_path.read_text())
            guid = mint_unique_guid(catalog)
            assert guid not in catalog["guid_to_type"]
        else:
            pytest.skip("Catalog not bootstrapped yet")
