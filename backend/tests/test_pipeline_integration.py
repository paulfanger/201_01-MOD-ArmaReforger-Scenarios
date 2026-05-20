"""Full pipeline integration tests — all missions, all maps, all edge cases.

Tests the complete Stage 6 pipeline:
  narrative.json + asset-manifest.json + encounters.json
  → generate_mission_tree()
  → validate_mission_tree() + validate_cross_file_consistency()
  → All 13+ output files with correct Reforger Brace-Syntax

Coverage goals:
  - All 3 real missions (night-recon-everon, day-assault-arland, fog-ambush-eden)
  - All 4 maps (everon, eden, arland, malden)
  - All time-of-day configurations
  - Weather: clear, fog_light, fog_heavy, rain, overcast, clear_cold
  - Player count: 1 (solo), 2, 4, 8 (max)
  - Empty encounters (no AI)
  - GUID hallucination detection
  - SphereRadius / m_aWaypoints / $grp syntax in layer output
  - Alias resolution (ENF_Faction_US etc.)
  - Managers layer: CoopFactionManager as prefab entity
  - DISCLOSURE.md APL-ND header
  - Snapshot creation
"""
import json
import re
import shutil
import tempfile
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.scripts.generate_mission import generate_mission_tree
from backend.validators.schema import validate_mission_tree
from backend.validators.cross_file import validate_cross_file_consistency
from backend.catalog.resolver import CatalogResolver
from backend.exporters.layer import (
    generate_layer, generate_managers_layer, generate_trigger_entity,
    generate_environment_layer,
)
from backend.exporters.ent import generate_world_subscene
from backend.exporters.mint import mint_log_list

MISSIONS_DIR = ROOT / "missions"
CATALOG_INDEX_PATH = ROOT / "catalog" / "INDEX.json"

# ---- Helpers ----------------------------------------------------------------

def load_catalog_index() -> dict:
    return json.loads(CATALOG_INDEX_PATH.read_text())


def load_mint_log(mission_dir: Path) -> list[str]:
    """Return all minted GUIDs for this mission as a flat list.

    Uses mint_log_list() from mint.py which handles both legacy flat-list
    format and the new keyed-dict format correctly.
    """
    return mint_log_list(mission_dir)


GUID_RE = re.compile(r'\{([0-9A-F]{16})\}')


def extract_guids_from_file(path: Path) -> set[str]:
    return set(GUID_RE.findall(path.read_text()))


def make_minimal_mission(
    tmp_dir: Path,
    mission_id: str,
    map_id: str = "everon",
    hour: int = 20,
    minute: int = 0,
    weather: str = "clear",
    max_players: int = 4,
    extra_encounters: dict | None = None,
) -> Path:
    """Create a minimal but valid mission directory for testing."""
    mdir = tmp_dir / mission_id
    mdir.mkdir()

    narrative = {
        "title": f"Test: {mission_id}",
        "tagline": "Integration test mission",
        "premise": "Test premise for pipeline validation",
        "factions": {
            "player": {"id": "US", "asset_id_ref": "US_Campaign", "guid": "ADFDBDA163950168"},
            "ai": {"id": "USSR", "asset_id_ref": "USSR_Campaign", "guid": "15B582F8FA0B0940"},
        },
        "biome": {"map_id_ref": map_id},
        "time_of_day": {"hour": hour, "minute": minute},
        "weather": {"preset": weather},
        "player_setup": {"min_players": 1, "max_players": max_players, "cooperative": True},
    }
    (mdir / "narrative.json").write_text(json.dumps(narrative, indent=2))

    asset_manifest = {
        "mission_id": mission_id,
        "stage": 2,
        "resolved_assets": [
            {"narrative_ref": "US_Campaign", "guid": "ADFDBDA163950168",
             "path": "Configs/Factions/US_Campaign.conf", "type": "faction", "role": "player_faction"},
            {"narrative_ref": "USSR_Campaign", "guid": "15B582F8FA0B0940",
             "path": "Configs/Factions/USSR_Campaign.conf", "type": "faction", "role": "ai_faction"},
        ],
        "missing_assets": [],
        "halt_required": False,
        "halt_reason": None,
    }
    (mdir / "asset-manifest.json").write_text(json.dumps(asset_manifest, indent=2))

    encounters = extra_encounters or {
        "spawn_points": [
            {"team": "US", "coords": [300, 10, 200], "angle_y": 90.0,
             "prefab_guid": "CEA2B24051A44525",
             "prefab_path": "PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et"},
        ],
        "ai_groups": [],
        "waypoints": [],
        "tasks": [],
        "triggers": [],
    }
    (mdir / "encounters.json").write_text(json.dumps(encounters, indent=2))

    return mdir


# ============================================================================
# 1. REAL MISSION END-TO-END TESTS
# ============================================================================

class TestRealMissions:
    """Run the full pipeline for all 3 real missions and validate output."""

    @pytest.fixture(autouse=True)
    def catalog_index(self):
        self.catalog = load_catalog_index()

    def _run_and_validate(self, mission_id: str):
        mdir = MISSIONS_DIR / mission_id
        assert mdir.exists(), f"Mission directory missing: {mdir}"

        result = generate_mission_tree(mission_id, mdir, auto_approve=True)

        assert result["status"] == "ok", (
            f"{mission_id}: generate_mission_tree failed\n"
            f"Errors: {result.get('errors')}"
        )
        assert len(result["errors"]) == 0, f"{mission_id}: errors = {result['errors']}"

        output_dir = mdir / "output"
        mint_log = load_mint_log(mdir)

        schema_report = validate_mission_tree(output_dir, self.catalog, mint_log)
        cross_report = validate_cross_file_consistency(mdir, output_dir)

        assert schema_report.passed, (
            f"{mission_id}: schema validation FAILED\n"
            + "\n".join(str(e) for e in schema_report.errors)
        )
        assert cross_report.passed, (
            f"{mission_id}: cross-file validation FAILED\n"
            + "\n".join(str(e) for e in cross_report.errors)
        )

        return result, output_dir

    def test_night_recon_everon_full_pipeline(self):
        result, output_dir = self._run_and_validate("night-recon-everon")
        # Should have at least 10 files (gproj, conf, conf.meta, ent, ent.meta, 7 layers, DISCLOSURE)
        assert len(result["files_written"]) >= 10

    def test_day_assault_arland_full_pipeline(self):
        result, output_dir = self._run_and_validate("day-assault-arland")
        # Arland map
        ent = (output_dir / "Worlds" / "day-assault-arland.ent").read_text()
        assert "Arland" in ent or "arland" in ent.lower()

    def test_fog_ambush_eden_full_pipeline(self):
        result, output_dir = self._run_and_validate("fog-ambush-eden")
        # Eden map
        ent = (output_dir / "Worlds" / "fog-ambush-eden.ent").read_text()
        assert "Eden" in ent or "eden" in ent.lower()
        # fog weather: WeatherPreset should appear
        env = (output_dir / "Worlds" / "fog-ambush-eden_environment.layer").read_text()
        assert "WeatherPreset" in env

    def test_all_real_missions_have_no_hallucinated_guids(self):
        """Every GUID reference in every output file must be in catalog or mint-log."""
        known_guids = set(self.catalog.get("guid_to_type", {}).keys())
        known_guids.add("58D0FB3206B6F859")  # CORE

        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            mdir = MISSIONS_DIR / mission_id
            mint_log = load_mint_log(mdir)
            allowed = known_guids | set(mint_log)

            output_dir = mdir / "output"
            for f in output_dir.rglob("*"):
                if f.is_file() and f.suffix in {".layer", ".ent", ".conf", ".gproj"}:
                    found = extract_guids_from_file(f)
                    bad = found - allowed
                    assert not bad, (
                        f"HALLUCINATED GUID(s) in {mission_id}/{f.name}: {bad}"
                    )

    def test_all_real_missions_have_disclosure_md(self):
        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            output_dir = MISSIONS_DIR / mission_id / "output"
            disclosure = output_dir / "DISCLOSURE.md"
            assert disclosure.exists(), f"{mission_id}: DISCLOSURE.md missing"
            text = disclosure.read_text()
            assert "APL-ND" in text
            assert "AI Usage Disclosure" in text

    def test_all_real_missions_managers_layer_correct(self):
        """Managers layer must have CoopFactionManager as prefab, not inline GameMode."""
        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            output_dir = MISSIONS_DIR / mission_id / "output"
            managers_layer = list((output_dir / "Worlds").glob("*_managers.layer"))
            assert managers_layer, f"{mission_id}: managers layer missing"

            text = managers_layer[0].read_text()
            # CoopFactionManager must be prefab-based
            assert "E4075339B4E24E10" in text, f"{mission_id}: CoopFactionManager GUID missing"
            assert 'SCR_FactionManager CoopFactionManager : "' in text
            # No standalone inline GameMode block
            assert not re.search(r'^GameMode GameMode \{', text, re.MULTILINE), (
                f"{mission_id}: standalone inline 'GameMode GameMode {{' found in managers layer"
            )

    def test_all_real_missions_triggers_use_sphere_radius(self):
        """Triggers must use SphereRadius, never m_fRadius or radius."""
        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            output_dir = MISSIONS_DIR / mission_id / "output"
            triggers = list((output_dir / "Worlds").glob("*_triggers.layer"))
            assert triggers
            text = triggers[0].read_text()
            if "SCR_BaseTriggerEntity" in text:
                assert "SphereRadius" in text, f"{mission_id}: SphereRadius missing in triggers"
                assert "m_fRadius" not in text, f"{mission_id}: wrong field m_fRadius used"
                assert not re.search(r'^\s+radius\s+\d', text, re.MULTILINE), (
                    f"{mission_id}: bare 'radius' field found in triggers"
                )

    def test_all_real_missions_ai_layer_uses_m_aWaypoints(self):
        """AI groups must use m_aWaypoints, waypoints must use $grp pattern."""
        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            output_dir = MISSIONS_DIR / mission_id / "output"
            ai_layers = list((output_dir / "Worlds").glob("*_AI.layer"))
            assert ai_layers
            text = ai_layers[0].read_text()
            if "SCR_AIGroup" in text:
                assert "m_aWaypoints" in text, f"{mission_id}: m_aWaypoints missing"
            if "$grp" in text:
                # $grp pattern: starts with $grp ClassName
                assert re.search(r'^\$grp \w+', text, re.MULTILINE), (
                    f"{mission_id}: malformed $grp pattern"
                )


# ============================================================================
# 2. ALL-MAP TESTS
# ============================================================================

class TestAllMaps:
    """Verify SubScene parent path for all 4 supported maps."""

    MAP_EXPECTED = {
        "everon": "Everon.ent",
        "eden": "Eden.ent",
        "arland": "Arland.ent",
        "malden": "Malden.ent",
    }

    def test_all_maps_subscene(self):
        for map_id, expected_file in self.MAP_EXPECTED.items():
            ent = generate_world_subscene(map_id)
            assert expected_file in ent, (
                f"Map '{map_id}': expected '{expected_file}' in SubScene, got:\n{ent}"
            )

    def test_all_maps_generate_pipeline(self):
        """Run full pipeline for each map variant and confirm no errors."""
        catalog = load_catalog_index()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            for map_id in ["everon", "eden", "arland", "malden"]:
                mdir = make_minimal_mission(tmp_dir, f"test-{map_id}", map_id=map_id)
                result = generate_mission_tree(f"test-{map_id}", mdir, auto_approve=True)

                assert result["status"] == "ok", (
                    f"Map '{map_id}': pipeline failed. Errors: {result['errors']}"
                )
                # Validate
                output_dir = mdir / "output"
                mint_log = load_mint_log(mdir)
                report = validate_mission_tree(output_dir, catalog, mint_log)
                assert report.passed, (
                    f"Map '{map_id}': validation errors:\n"
                    + "\n".join(str(e) for e in report.errors)
                )

                # Check subscene
                ent_path = output_dir / "Worlds" / f"test-{map_id}.ent"
                assert ent_path.exists()
                ent_text = ent_path.read_text()
                expected = self.MAP_EXPECTED[map_id]
                assert expected in ent_text, (
                    f"Map '{map_id}': SubScene doesn't reference '{expected}'"
                )

    def test_unknown_map_falls_back_gracefully(self):
        """Unknown map_id should not crash but use Everon fallback."""
        ent = generate_world_subscene("unknown_planet")
        assert "SubScene" in ent
        assert "Parent" in ent  # Should have some parent reference


# ============================================================================
# 3. WEATHER PRESETS
# ============================================================================

class TestWeatherPresets:
    """All weather presets produce valid environment layers."""

    WEATHER_PRESETS = [
        "clear",
        "fog_light",
        "fog_heavy",
        "rain",
        "overcast",
        "clear_cold",
        "storm",
    ]

    def test_all_weather_presets_generate(self):
        for preset in self.WEATHER_PRESETS:
            layer = generate_environment_layer(time_hour=12, time_minute=0, weather=preset)
            assert "TimeAndWeatherManagerEntity" in layer, f"Preset '{preset}': missing entity"
            assert "m_iDefaultHours 12" in layer, f"Preset '{preset}': hour missing"
            # "clear" should NOT emit WeatherPreset line
            if preset == "clear":
                assert "WeatherPreset" not in layer, "clear preset must not emit WeatherPreset"
            else:
                assert "WeatherPreset" in layer, f"Preset '{preset}': WeatherPreset line missing"
                assert preset in layer, f"Preset '{preset}': preset value missing from output"

    def test_no_hallucinated_guid_in_environment_layer(self):
        """Environment layer uses engine built-in — must have NO GUID references."""
        for preset in self.WEATHER_PRESETS:
            layer = generate_environment_layer(20, 30, preset)
            guids = GUID_RE.findall(layer)
            assert not guids, (
                f"Environment layer for '{preset}' emits GUID(s): {guids} — "
                "TimeAndWeatherManagerEntity is an engine built-in with no prefab GUID"
            )

    def test_weather_pipeline_integration(self):
        """Fog weather in fog-ambush-eden: WeatherPreset appears in output."""
        mdir = MISSIONS_DIR / "fog-ambush-eden"
        result = generate_mission_tree("fog-ambush-eden", mdir, auto_approve=True)
        assert result["status"] == "ok"
        output_dir = mdir / "output"
        env = (output_dir / "Worlds" / "fog-ambush-eden_environment.layer").read_text()
        assert "WeatherPreset" in env
        assert "fog" in env.lower()


# ============================================================================
# 4. PLAYER COUNT EDGE CASES
# ============================================================================

class TestPlayerCounts:
    """Player count min/max boundaries."""

    @pytest.fixture(autouse=True)
    def catalog(self):
        self.catalog = load_catalog_index()

    def _check_player_count_in_output(self, output_dir: Path, expected: int) -> bool:
        conf_files = list((output_dir / "Missions").glob("*.conf"))
        assert conf_files, "No .conf file found"
        text = conf_files[0].read_text()
        # m_iPlayerCount field
        match = re.search(r'm_iPlayerCount\s+(\d+)', text)
        if not match:
            return True  # field not present — default, ok
        return int(match.group(1)) == expected

    def test_solo_player_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            mdir = make_minimal_mission(Path(tmp), "solo-test", max_players=1)
            result = generate_mission_tree("solo-test", mdir, auto_approve=True)
            assert result["status"] == "ok"
            report = validate_mission_tree(mdir / "output", self.catalog, load_mint_log(mdir))
            # Solo (1 player) should be valid
            assert report.passed, f"Solo player validation failed: {report.errors}"

    def test_two_player(self):
        with tempfile.TemporaryDirectory() as tmp:
            mdir = make_minimal_mission(Path(tmp), "duo-test", max_players=2)
            result = generate_mission_tree("duo-test", mdir, auto_approve=True)
            assert result["status"] == "ok"

    def test_max_eight_players(self):
        with tempfile.TemporaryDirectory() as tmp:
            mdir = make_minimal_mission(Path(tmp), "max-test", max_players=8)
            result = generate_mission_tree("max-test", mdir, auto_approve=True)
            assert result["status"] == "ok"
            report = validate_mission_tree(mdir / "output", self.catalog, load_mint_log(mdir))
            assert report.passed


# ============================================================================
# 5. EMPTY ENCOUNTERS EDGE CASES
# ============================================================================

class TestEmptyEncounters:
    """Missions with no AI/waypoints/tasks/triggers must still generate valid output."""

    @pytest.fixture(autouse=True)
    def catalog(self):
        self.catalog = load_catalog_index()

    def test_empty_encounters_no_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_encounters = {
                "spawn_points": [],
                "ai_groups": [],
                "waypoints": [],
                "tasks": [],
                "triggers": [],
            }
            mdir = make_minimal_mission(
                Path(tmp), "empty-test", extra_encounters=empty_encounters
            )
            result = generate_mission_tree("empty-test", mdir, auto_approve=True)
            assert result["status"] == "ok"
            assert len(result["errors"]) == 0

    def test_empty_encounters_valid_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_encounters = {"spawn_points": [], "ai_groups": [], "waypoints": [],
                                "tasks": [], "triggers": []}
            mdir = make_minimal_mission(Path(tmp), "empty-valid", extra_encounters=empty_encounters)
            generate_mission_tree("empty-valid", mdir, auto_approve=True)
            report = validate_mission_tree(
                mdir / "output", self.catalog, load_mint_log(mdir)
            )
            assert report.passed, f"Empty encounters: validation errors = {report.errors}"

    def test_empty_ai_layer_has_comment(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_encounters = {"spawn_points": [], "ai_groups": [], "waypoints": [],
                                "tasks": [], "triggers": []}
            mdir = make_minimal_mission(Path(tmp), "empty-ai", extra_encounters=empty_encounters)
            generate_mission_tree("empty-ai", mdir, auto_approve=True)
            ai_files = list((mdir / "output" / "Worlds").glob("*_AI.layer"))
            assert ai_files
            text = ai_files[0].read_text()
            # Should have a comment explaining the empty layer
            assert "//" in text

    def test_no_encounters_file_uses_defaults(self):
        """Missing encounters.json entirely: pipeline uses safe defaults."""
        with tempfile.TemporaryDirectory() as tmp:
            mdir = Path(tmp) / "no-encounters"
            mdir.mkdir()
            (mdir / "narrative.json").write_text(json.dumps({
                "title": "No Encounters Test",
                "tagline": "test",
                "premise": "test",
                "factions": {
                    "player": {"id": "US", "asset_id_ref": "US_Campaign", "guid": "ADFDBDA163950168"},
                    "ai": {"id": "USSR", "asset_id_ref": "USSR_Campaign", "guid": "15B582F8FA0B0940"},
                },
                "biome": {"map_id_ref": "everon"},
                "time_of_day": {"hour": 12, "minute": 0},
                "weather": {"preset": "clear"},
                "player_setup": {"min_players": 1, "max_players": 4, "cooperative": True},
            }))
            # No encounters.json — pipeline should fall back gracefully
            result = generate_mission_tree("no-encounters", mdir, auto_approve=True)
            assert result["status"] == "ok", f"No encounters.json: {result['errors']}"


# ============================================================================
# 6. GUID HALLUCINATION DETECTION
# ============================================================================

class TestHallucinationDetection:
    """Any fabricated GUID must be caught — zero tolerance."""

    @pytest.fixture(autouse=True)
    def catalog(self):
        self.catalog = load_catalog_index()

    def test_fake_ai_group_guid_detected(self):
        """A clearly hallucinated GUID in ai_groups should cause an error, not be emitted."""
        encounters_with_fake_guid = {
            "spawn_points": [],
            "ai_groups": [{
                "name": "Fake_Group",
                "prefab_guid": "DEADBEEF12345678",  # not in catalog
                "prefab_path": "Prefabs/Groups/Fake/Fake.et",
                "coords": [100, 10, 100],
                "waypoint_refs": [],
            }],
            "waypoints": [],
            "tasks": [],
            "triggers": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            mdir = make_minimal_mission(
                Path(tmp), "hallucinated-test", extra_encounters=encounters_with_fake_guid
            )
            result = generate_mission_tree("hallucinated-test", mdir, auto_approve=True)
            # Should report the hallucinated GUID as error
            assert len(result["errors"]) > 0
            error_text = " ".join(result["errors"])
            assert "DEADBEEF12345678" in error_text or "HALLUCINATED" in error_text

    def test_fake_waypoint_guid_detected(self):
        encounters_with_fake_wp = {
            "spawn_points": [],
            "ai_groups": [],
            "waypoints": [{
                "name": "WP_Fake",
                "type": "move",
                "prefab_guid": "AAAA000011112222",  # hallucinated
                "prefab_path": "Prefabs/AI/Waypoints/FakeWaypoint.et",
                "coords": [200, 10, 200],
            }],
            "tasks": [],
            "triggers": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            mdir = make_minimal_mission(
                Path(tmp), "fake-wp-test", extra_encounters=encounters_with_fake_wp
            )
            result = generate_mission_tree("fake-wp-test", mdir, auto_approve=True)
            errors = result.get("errors", [])
            assert any("HALLUCINATED" in e or "AAAA000011112222" in e for e in errors), (
                f"Fake waypoint GUID not caught. errors={errors}"
            )

    def test_halt_required_asset_manifest_blocks_pipeline(self):
        """halt_required=true in asset-manifest.json must stop generation."""
        with tempfile.TemporaryDirectory() as tmp:
            mdir = Path(tmp) / "halt-test"
            mdir.mkdir()
            (mdir / "narrative.json").write_text(json.dumps({
                "title": "Halt Test",
                "tagline": "test",
                "premise": "test",
                "factions": {
                    "player": {"id": "US", "asset_id_ref": "US_Campaign", "guid": "ADFDBDA163950168"},
                    "ai": {"id": "USSR", "asset_id_ref": "USSR_Campaign", "guid": "15B582F8FA0B0940"},
                },
                "biome": {"map_id_ref": "everon"},
                "time_of_day": {"hour": 12, "minute": 0},
                "weather": {"preset": "clear"},
                "player_setup": {"min_players": 1, "max_players": 4, "cooperative": True},
            }))
            (mdir / "asset-manifest.json").write_text(json.dumps({
                "mission_id": "halt-test",
                "stage": 2,
                "resolved_assets": [],
                "missing_assets": [{"narrative_ref": "UnresolvableAsset"}],
                "halt_required": True,
                "halt_reason": "Critical asset missing",
            }))
            result = generate_mission_tree("halt-test", mdir, auto_approve=True)
            assert result["status"] == "halt", (
                f"Expected status='halt', got '{result['status']}'"
            )

    def test_schema_validator_catches_unknown_guid_in_layer(self):
        """schema validator Rule 9 must catch unknown GUIDs in layer files."""
        catalog = self.catalog
        known = set(catalog.get("guid_to_type", {}).keys())

        # Pick a GUID that is definitely NOT in catalog
        fake = "CAFEBABE12345678"
        while fake in known:
            fake = fake[:15] + chr(ord(fake[-1]) + 1)

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "output"
            worlds = out_dir / "Worlds"
            missions = out_dir / "Missions"
            worlds.mkdir(parents=True)
            missions.mkdir(parents=True)

            # Write minimal valid files
            (out_dir / "addon.gproj").write_text(
                f'GameProject {{\n GUID "{{58D0FB3206B6F859}}path.gproj"\n'
                f' Dependencies {{\n  "{{58D0FB3206B6F859}}"\n }}\n}}\n'
            )
            (missions / "test.conf").write_text(
                f'MissionHeader test {{\n m_sName "test"\n'
                f' m_sWorldPath "Worlds/test.ent"\n m_iPlayerCount 4\n}}\n'
            )
            (worlds / "test.ent").write_text(
                'SubScene {\n Parent "worlds/Everon/Everon.ent"\n}\n'
            )
            # Inject a fake GUID into a layer file
            (worlds / "test_AI.layer").write_text(
                f'SCR_AIGroup BadGroup : "{{{fake}}}Fake/Path.et" {{\n coords 0 0 0\n}}\n'
            )
            for layer in ["managers", "spawnpoints", "tasks", "triggers", "environment", "gamemode"]:
                (worlds / f"test_{layer}.layer").write_text("// empty\n")

            report = validate_mission_tree(out_dir, catalog, mission_mint_log=[])
            assert not report.passed, "Validator should fail on hallucinated GUID"
            error_text = " ".join(str(e) for e in report.errors)
            assert fake in error_text or "not in catalog" in error_text.lower()


# ============================================================================
# 7. LAYER SYNTAX CORRECTNESS
# ============================================================================

class TestLayerSyntax:
    """Fine-grained checks of emitted Reforger Brace-Syntax."""

    def test_trigger_entity_sphere_radius_field(self):
        """SphereRadius must be emitted — never m_fRadius."""
        layer = generate_trigger_entity(
            "SCR_BaseTriggerEntity", "Test_Trigger", [100, 10, 200], sphere_radius=75.0
        )
        assert "SphereRadius 75" in layer
        assert "m_fRadius" not in layer
        assert "SCR_BaseTriggerEntity Test_Trigger {" in layer
        assert "coords 100 10 200" in layer

    def test_trigger_entity_with_spawner_component(self):
        """SCR_AISpawnerComponent must use m_rnDefaultPrefab and include RplComponent."""
        spawners = [{
            "default_prefab_guid": "30ED11AA4F0D41E5",
            "default_prefab_path": "Prefabs/Groups/OPFOR/Group_USSR_FireGroup.et",
            "spawn_pos": [110, 10, 210],
            "waypoints": ["WP_1", "WP_2"],
        }]
        layer = generate_trigger_entity(
            "SCR_BaseTriggerEntity", "Spawn_Trigger", [100, 10, 200],
            sphere_radius=60.0, spawner_components=spawners
        )
        assert "SCR_AISpawnerComponent {" in layer
        assert "m_rnDefaultPrefab" in layer
        assert "m_vSpawnPosition" in layer
        assert "m_aWaypointsList" in layer
        assert '"WP_1"' in layer
        assert "RplComponent {" in layer

    def test_managers_layer_structure(self):
        """Managers layer: CoopFactionManager as prefab, inline LoadoutManager."""
        layer = generate_managers_layer()
        # Must have prefab-based CoopFactionManager
        assert 'SCR_FactionManager CoopFactionManager : "{E4075339B4E24E10}' in layer
        # Must have inline LoadoutManager
        assert "LoadoutManager LoadoutManager {" in layer
        # Must have inline TimeAndWeatherManagerEntity
        assert "TimeAndWeatherManagerEntity TimeAndWeatherManagerEntity {" in layer

    def test_grp_waypoint_pattern(self):
        """$grp emitter: correct grouped entity syntax."""
        entities = [{
            "$grp": True,
            "class_name": "AIWaypoint_Move",
            "prefab_guid": "750A8D1695BD6998",
            "prefab_path": "Prefabs/AI/Waypoints/AIWaypoint_Move.et",
            "instances": [
                {"name": "WP_A", "coords": [300, 10, 200]},
                {"name": "WP_B", "coords": [350, 10, 200]},
            ],
        }]
        layer = generate_layer(entities)
        assert '$grp AIWaypoint_Move : "{750A8D1695BD6998}' in layer
        assert "WP_A {" in layer
        assert "WP_B {" in layer
        assert "coords 300 10 200" in layer
        assert "coords 350 10 200" in layer

    def test_single_entity_no_empty_guid_ref(self):
        """Entity with no GUID must not emit empty {  }path.et ref."""
        entities = [{
            "class_name": "SCR_EliminateTask",
            "instance_name": "Task_01",
            # No prefab_guid
            "coords": [100, 10, 100],
        }]
        layer = generate_layer(entities)
        assert "{}" not in layer
        assert "SCR_EliminateTask Task_01 {" in layer

    def test_environment_layer_no_guid(self):
        """TimeAndWeatherManagerEntity is engine built-in — no GUID in output."""
        layer = generate_environment_layer(20, 30, "clear")
        assert "{" not in layer.split("TimeAndWeatherManagerEntity")[1][:30] or \
               GUID_RE.search(layer) is None

    def test_coord_formatting_integers(self):
        """Integer coordinates must be emitted as integers, not floats."""
        entities = [{"class_name": "SCR_SpawnPoint", "instance_name": "SP",
                     "prefab_guid": "CEA2B24051A44525",
                     "prefab_path": "PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et",
                     "coords": [300.0, 10.0, 200.0]}]
        layer = generate_layer(entities)
        assert "coords 300 10 200" in layer
        assert "300.0" not in layer


# ============================================================================
# 8. ALIAS RESOLUTION
# ============================================================================

class TestAliasResolution:
    """Semantic alias system: ENF_Faction_US -> GUID."""

    @pytest.fixture(autouse=True)
    def resolver(self):
        self.r = CatalogResolver()

    def test_us_faction_alias(self):
        result = self.r.resolve_alias("ENF_Faction_US")
        assert result is not None
        assert result["guid"] == "ADFDBDA163950168"
        assert "US_Campaign.conf" in result["path"]

    def test_ussr_faction_alias(self):
        result = self.r.resolve_alias("ENF_Faction_USSR")
        assert result is not None
        assert result["guid"] == "15B582F8FA0B0940"
        assert "USSR_Campaign.conf" in result["path"]

    def test_fia_faction_alias(self):
        result = self.r.resolve_alias("ENF_Faction_FIA")
        assert result is not None
        assert result["guid"] == "CF9447B87AB774DB"
        assert "FIA_Campaign.conf" in result["path"]

    def test_unknown_alias_returns_none(self):
        result = self.r.resolve_alias("ENF_Faction_UNICORN")
        assert result is None

    def test_list_aliases_has_three_factions(self):
        aliases = self.r.list_aliases()
        assert "ENF_Faction_US" in aliases
        assert "ENF_Faction_USSR" in aliases
        assert "ENF_Faction_FIA" in aliases

    def test_alias_guid_is_in_catalog(self):
        """Alias GUIDs must be catalog-verified, not invented."""
        catalog = load_catalog_index()
        known = set(catalog.get("guid_to_type", {}).keys())
        for name, guid in self.r.list_aliases().items():
            assert guid in known, (
                f"Alias '{name}' points to GUID '{guid}' not in catalog — HALLUCINATION!"
            )


# ============================================================================
# 9. OUTPUT FILE STRUCTURE
# ============================================================================

class TestOutputFileStructure:
    """All expected files must be present in the output tree."""

    REQUIRED_FILES = [
        "addon.gproj",
        "DISCLOSURE.md",
    ]
    REQUIRED_MISSIONS = [
        "{mid}.conf",
        "{mid}.conf.meta",
    ]
    REQUIRED_WORLDS = [
        "{mid}.ent",
        "{mid}.ent.meta",
        "{mid}_gamemode.layer",
        "{mid}_managers.layer",
        "{mid}_spawnpoints.layer",
        "{mid}_AI.layer",
        "{mid}_tasks.layer",
        "{mid}_triggers.layer",
        "{mid}_environment.layer",
    ]

    def test_night_recon_output_structure(self):
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        self._check_structure(mdir / "output", "night-recon-everon")

    def test_day_assault_output_structure(self):
        mdir = MISSIONS_DIR / "day-assault-arland"
        generate_mission_tree("day-assault-arland", mdir, auto_approve=True)
        self._check_structure(mdir / "output", "day-assault-arland")

    def test_fog_ambush_output_structure(self):
        mdir = MISSIONS_DIR / "fog-ambush-eden"
        generate_mission_tree("fog-ambush-eden", mdir, auto_approve=True)
        self._check_structure(mdir / "output", "fog-ambush-eden")

    def _check_structure(self, output_dir: Path, mission_id: str):
        for fname in self.REQUIRED_FILES:
            p = output_dir / fname
            assert p.exists(), f"Missing: {p.relative_to(output_dir.parent.parent.parent)}"

        for template in self.REQUIRED_MISSIONS:
            fname = template.format(mid=mission_id)
            p = output_dir / "Missions" / fname
            assert p.exists(), f"Missing: Missions/{fname}"

        for template in self.REQUIRED_WORLDS:
            fname = template.format(mid=mission_id)
            p = output_dir / "Worlds" / fname
            assert p.exists(), f"Missing: Worlds/{fname}"


# ============================================================================
# 10. GPROJ AND META FILE FORMAT
# ============================================================================

class TestGprojAndMetaFormat:
    """Structural checks on .gproj and .meta files."""

    def test_gproj_has_core_dependency(self):
        """addon.gproj must always declare the CORE dependency."""
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        gproj = (mdir / "output" / "addon.gproj").read_text()
        assert "58D0FB3206B6F859" in gproj

    def test_gproj_has_addon_guid(self):
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        gproj = (mdir / "output" / "addon.gproj").read_text()
        # Addon GUID is in {GUID} brace format; core dependency is plain quoted string without braces
        guids_in_braces = GUID_RE.findall(gproj)
        assert len(guids_in_braces) >= 1, "addon.gproj must have at least the addon GUID in {GUID} format"
        # Core dependency must also appear (plain string, no braces in deps block)
        assert "58D0FB3206B6F859" in gproj, "Core GUID dependency missing from addon.gproj"

    def test_conf_meta_has_five_platforms(self):
        """conf.meta must have all 5 platform Configurations entries.

        Confirmed platforms in generated .meta files:
          PC, XBOX_ONE, XBOX_SERIES, PS4, HEADLESS
        (Note: PS5 is not a separate platform key — PS5 uses the PS4 config via inheritance)
        """
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        meta_files = list((mdir / "output" / "Missions").glob("*.conf.meta"))
        assert meta_files
        meta = meta_files[0].read_text()
        for platform in ["PC", "XBOX_ONE", "XBOX_SERIES", "PS4", "HEADLESS"]:
            assert platform in meta, f"Platform '{platform}' missing from conf.meta"

    def test_ent_meta_has_guid(self):
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        meta_files = list((mdir / "output" / "Worlds").glob("*.ent.meta"))
        assert meta_files
        meta = meta_files[0].read_text()
        guids = GUID_RE.findall(meta)
        assert guids, "ent.meta has no GUID"


# ============================================================================
# 11. DISCLOSURE / EULA COMPLIANCE
# ============================================================================

class TestDisclosureEulaCompliance:
    """APL-ND and EULA compliance checks."""

    def test_disclosure_md_required_content(self):
        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            output_dir = MISSIONS_DIR / mission_id / "output"
            disclosure = output_dir / "DISCLOSURE.md"
            text = disclosure.read_text()
            assert "APL-ND" in text
            assert "AI Usage Disclosure" in text
            assert "No live AI calls occur during gameplay" in text

    def test_conf_description_has_ai_disclosure(self):
        """Mission .conf m_sDescription must mention AI authoring + APL-ND."""
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        conf_files = list((mdir / "output" / "Missions").glob("*.conf"))
        assert conf_files
        text = conf_files[0].read_text()
        assert "AI-assisted" in text or "ELOS" in text

    def test_no_runtime_llm_calls_in_mission_files(self):
        """Mission files must never reference LLM endpoints or API keys."""
        forbidden_patterns = [
            "anthropic.com", "openai.com", "api.anthropic", "ANTHROPIC_API_KEY",
            "sk-ant-", "claude.ai/api", "gpt-4", "gpt-3",
        ]
        for mission_id in ["night-recon-everon", "day-assault-arland", "fog-ambush-eden"]:
            output_dir = MISSIONS_DIR / mission_id / "output"
            for f in output_dir.rglob("*"):
                if f.is_file():
                    text = f.read_text(errors="ignore")
                    for pattern in forbidden_patterns:
                        assert pattern not in text, (
                            f"Runtime LLM reference '{pattern}' found in {f} — EULA VIOLATION!"
                        )


# ============================================================================
# 12. SNAPSHOT INTEGRATION
# ============================================================================

class TestSnapshotIntegration:
    """Version-keeper snapshot tests."""

    def test_snapshots_created_on_generation(self):
        """After generate_mission_tree, a mint-log (deterministic state) exists."""
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        # mint-log.json should exist
        assert (mdir / "mint-log.json").exists()

    def test_mission_guid_stable_on_re_run(self):
        """Re-running generation for same mission produces same addon GUID."""
        mdir = MISSIONS_DIR / "night-recon-everon"
        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        gproj1 = (mdir / "output" / "addon.gproj").read_text()
        guids1 = set(GUID_RE.findall(gproj1))

        generate_mission_tree("night-recon-everon", mdir, auto_approve=True)
        gproj2 = (mdir / "output" / "addon.gproj").read_text()
        guids2 = set(GUID_RE.findall(gproj2))

        # GUIDs should be stable (mint-log persists)
        assert guids1 == guids2, (
            f"GUIDs changed on re-run! First={guids1} Second={guids2}\n"
            "mint-log should prevent re-minting on re-run"
        )


# ============================================================================
# 13. FULL PIPELINE COMBINATION MATRIX
# ============================================================================

class TestPipelineCombinationMatrix:
    """Exhaustive combinations: map × time × weather."""

    @pytest.fixture(autouse=True)
    def catalog(self):
        self.catalog = load_catalog_index()

    @pytest.mark.parametrize("map_id,hour,weather", [
        ("everon", 2, "clear"),         # night, clear
        ("everon", 20, "fog_light"),    # evening, fog
        ("arland", 10, "overcast"),     # day, overcast
        ("arland", 6, "rain"),          # dawn, rain
        ("eden", 6, "fog_heavy"),       # dawn, heavy fog
        ("eden", 14, "clear_cold"),     # afternoon, cold
        ("malden", 20, "storm"),        # evening, storm
        ("malden", 0, "clear"),         # midnight, clear
    ])
    def test_map_time_weather_combination(self, map_id, hour, weather):
        with tempfile.TemporaryDirectory() as tmp:
            mid = f"combo-{map_id}-h{hour}-{weather}"
            mdir = make_minimal_mission(Path(tmp), mid, map_id=map_id, hour=hour, weather=weather)
            result = generate_mission_tree(mid, mdir, auto_approve=True)

            assert result["status"] == "ok", (
                f"Combo {map_id}/{hour}h/{weather}: {result['errors']}"
            )
            report = validate_mission_tree(mdir / "output", self.catalog, load_mint_log(mdir))
            assert report.passed, (
                f"Combo {map_id}/{hour}h/{weather}: {report.errors}"
            )

            # Map-specific assertion
            ent = (mdir / "output" / "Worlds" / f"{mid}.ent").read_text()
            assert map_id.capitalize() in ent or map_id in ent.lower()

            # Weather assertion
            env = (mdir / "output" / "Worlds" / f"{mid}_environment.layer").read_text()
            assert f"m_iDefaultHours {hour}" in env
            if weather != "clear":
                assert "WeatherPreset" in env
