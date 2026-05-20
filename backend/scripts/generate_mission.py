"""Reforger Bridge — generates a complete Arma Reforger addon tree.

This is the Stage 6c implementation: takes narrative.json + asset-manifest.json
+ encounters.json and outputs a complete, valid Reforger mission addon tree
in missions/{id}/output/.

Usage (programmatic):
    from backend.scripts.generate_mission import generate_mission_tree
    result = generate_mission_tree("night-recon-everon", ROOT / "missions" / "night-recon-everon")

Usage (CLI):
    python3 backend/scripts/generate_mission.py <mission_id>
"""
import json
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.exporters.gproj import generate_gproj
from backend.exporters.conf import generate_mission_header, generate_conf_meta, generate_ent_meta
from backend.exporters.ent import generate_world_subscene, generate_world_with_layers
from backend.exporters.layer import (
    generate_layer, generate_managers_layer, generate_environment_layer,
    generate_trigger_entity
)
from backend.exporters.mint import mint_unique_guid, mint_mission_guids, mint_log_list
from backend.catalog.resolver import CatalogResolver

# Known safe GUIDs from catalog for standard entities
# These are verified GUIDs from Arma-Reforger-Samples / Reforger-Sample-Coop
SAFE_GAMEMODE_GUID = None   # Resolved from catalog at runtime
SAFE_SPAWNPOINT_GUID = None  # Resolved from catalog at runtime


def _resolve_gamemode_guid(resolver: CatalogResolver) -> tuple[str, str]:
    """Find a verified Coop gamemode GUID+path from catalog."""
    gamemodes = resolver.find_by_type("gamemode")
    if gamemodes:
        gm = gamemodes[0]
        return gm["guid"], gm.get("path", "Prefabs/MP/Modes/Coop/CoopGameMode.et")
    # Fallback: use a known pattern from research
    results = resolver.find_by_path_fragment("CoopGameMode")
    if results:
        return results[0]["guid"], results[0].get("path", "Prefabs/MP/Modes/Coop/CoopGameMode.et")
    return None, None


def _resolve_spawnpoint_guid(resolver: CatalogResolver, faction: str = "US") -> tuple[str, str]:
    """Find a verified spawn point GUID+path from catalog."""
    spawnpoints = resolver.find_by_type("spawnpoint")
    if spawnpoints:
        # Prefer faction-specific
        for sp in spawnpoints:
            path = sp.get("path", "")
            if faction.upper() in path.upper():
                return sp["guid"], path
        return spawnpoints[0]["guid"], spawnpoints[0].get("path", "")
    return None, None


def generate_mission_tree(
    mission_id: str,
    mission_dir: Path,
    auto_approve: bool = False,
) -> dict:
    """Generate the complete addon-tree for a mission.

    Args:
        mission_id: string identifier, e.g. "night-recon-everon"
        mission_dir: path to missions/{id}/
        auto_approve: if True, skip approval gates (for self-test only)

    Returns:
        dict with status, output_dir, files_written, errors
    """
    result = {
        "status": "ok",
        "mission_id": mission_id,
        "output_dir": str(mission_dir / "output"),
        "files_written": [],
        "errors": [],
        "warnings": [],
    }

    # ---- Load inputs -------------------------------------------------------
    narrative_path = mission_dir / "narrative.json"
    if not narrative_path.exists():
        result["status"] = "error"
        result["errors"].append("narrative.json missing — run Stage 1 first")
        return result

    narrative = json.loads(narrative_path.read_text())

    # Asset manifest (optional for self-test)
    asset_manifest = {}
    manifest_path = mission_dir / "asset-manifest.json"
    if manifest_path.exists():
        asset_manifest = json.loads(manifest_path.read_text())
        if asset_manifest.get("halt_required"):
            result["status"] = "halt"
            result["errors"].append(f"asset-manifest: halt_required — {asset_manifest.get('halt_reason')}")
            return result

    # Encounters (optional — may not exist yet for minimal test)
    encounters = {}
    encounters_path = mission_dir / "encounters.json"
    if encounters_path.exists():
        encounters = json.loads(encounters_path.read_text())

    # ---- Resolve catalog ---------------------------------------------------
    resolver = CatalogResolver()
    catalog_index = json.loads((ROOT / "catalog" / "INDEX.json").read_text())

    # ---- Mint mission GUIDs -----------------------------------------------
    mission_guids = mint_mission_guids(catalog_index, mission_dir)
    addon_guid = mission_guids["addon_guid"]
    header_guid = mission_guids["mission_header_guid"]
    world_guid = mission_guids["world_guid"]

    # Track all minted GUIDs for validator (use mint_log_list for correct dict/list handling)
    mint_log = mint_log_list(mission_dir)

    # ---- Prepare output tree -----------------------------------------------
    output_dir = mission_dir / "output"
    missions_out = output_dir / "Missions"
    worlds_out = output_dir / "Worlds"
    missions_out.mkdir(parents=True, exist_ok=True)
    worlds_out.mkdir(parents=True, exist_ok=True)

    # ---- Extract narrative fields ------------------------------------------
    title = narrative.get("title", mission_id)
    description = narrative.get("tagline", narrative.get("premise", "A tactical coop mission."))
    map_id = narrative.get("biome", {}).get("map_id_ref", "everon")
    time_hour = narrative.get("time_of_day", {}).get("hour", 20)
    time_minute = narrative.get("time_of_day", {}).get("minute", 0)
    weather = narrative.get("weather", {}).get("preset", "clear")
    player_count = narrative.get("player_setup", {}).get("max_players", 8)

    # encounters.json environment_overrides take precedence over narrative
    env_overrides = encounters.get("environment_overrides", {})
    if env_overrides:
        tod = env_overrides.get("time_of_day", {})
        if "hour" in tod:
            time_hour = tod["hour"]
        if "minute" in tod:
            time_minute = tod["minute"]
        if "weather_preset" in env_overrides:
            weather = env_overrides["weather_preset"]

    # ---- 1. addon.gproj ---------------------------------------------------
    addon_id = mission_id.replace("-", "").replace("_", "").replace(" ", "")
    gproj_content = generate_gproj(addon_id, addon_guid, title)
    gproj_path = output_dir / "addon.gproj"
    gproj_path.write_text(gproj_content)
    result["files_written"].append("addon.gproj")

    # ---- 2. Missions/<id>.conf --------------------------------------------
    world_path = f"Worlds/{mission_id}.ent"
    conf_content = generate_mission_header(
        name=title,
        description=description,
        world_guid=world_guid,
        world_path=world_path,
        player_count=player_count,
        time_hour=time_hour,
        time_minute=time_minute,
        weather_preset=weather if weather != "clear" else None,
    )
    conf_path = missions_out / f"{mission_id}.conf"
    conf_path.write_text(conf_content)
    result["files_written"].append(f"Missions/{mission_id}.conf")

    # ---- 3. Missions/<id>.conf.meta ---------------------------------------
    conf_meta = generate_conf_meta(header_guid, f"Missions/{mission_id}.conf")
    (missions_out / f"{mission_id}.conf.meta").write_text(conf_meta)
    result["files_written"].append(f"Missions/{mission_id}.conf.meta")

    # ---- 4. Worlds/<id>.ent -----------------------------------------------
    ent_content = generate_world_subscene(map_id)
    ent_path = worlds_out / f"{mission_id}.ent"
    ent_path.write_text(ent_content)
    result["files_written"].append(f"Worlds/{mission_id}.ent")

    # ---- 5. Worlds/<id>.ent.meta ------------------------------------------
    ent_meta = generate_ent_meta(world_guid, f"Worlds/{mission_id}.ent")
    (worlds_out / f"{mission_id}.ent.meta").write_text(ent_meta)
    result["files_written"].append(f"Worlds/{mission_id}.ent.meta")

    # ---- 6. Layer files ---------------------------------------------------

    # 6a. gamemode layer — find a real CoopGameMode from catalog
    gm_guid, gm_path = _resolve_gamemode_guid(resolver)
    if gm_guid:
        gamemode_entities = [{
            "class_name": "SCR_CoopGameMode",
            "instance_name": "CoopGameMode",
            "prefab_guid": gm_guid,
            "prefab_path": gm_path,
        }]
    else:
        gamemode_entities = []
        result["warnings"].append("No CoopGameMode GUID found in catalog — gamemode layer empty")

    gamemode_layer = generate_layer(gamemode_entities) if gamemode_entities else "// No gamemode entity — catalog missing CoopGameMode\n"
    _write_layer(worlds_out, mission_id, "gamemode", gamemode_layer, result)

    # 6b. managers layer
    managers_layer = generate_managers_layer()
    _write_layer(worlds_out, mission_id, "managers", managers_layer, result)

    # 6c. spawnpoints layer — use catalog spawnpoint if available
    spawn_entities = _build_spawnpoints(encounters, resolver, result)
    spawnpoints_layer = generate_layer(spawn_entities) if spawn_entities else "// Spawnpoints: no catalog data — add manually in Workbench\n"
    _write_layer(worlds_out, mission_id, "spawnpoints", spawnpoints_layer, result)

    # 6d. AI layer — groups + waypoints combined
    ai_layer = _build_ai_layer(encounters, resolver, result)
    _write_layer(worlds_out, mission_id, "AI", ai_layer, result)

    # 6e. tasks layer
    task_entities = _build_tasks(encounters, resolver, result)
    tasks_layer = generate_layer(task_entities) if task_entities else "// Tasks: none defined yet — add via encounter-designer\n"
    _write_layer(worlds_out, mission_id, "tasks", tasks_layer, result)

    # 6f. triggers layer — use generate_trigger_entity for correct SphereRadius syntax
    triggers_layer = _build_triggers_layer(encounters, resolver, result)
    _write_layer(worlds_out, mission_id, "triggers", triggers_layer, result)

    # 6g. environment layer
    env_layer = generate_environment_layer(time_hour, time_minute, weather)
    _write_layer(worlds_out, mission_id, "environment", env_layer, result)

    # ---- 7. DISCLOSURE.md -------------------------------------------------
    disclosure = f"""# Mission Disclosure

**Mission:** {title}
**Generated:** {date.today().isoformat()}
**System:** ELOS AI-Native Mission Authoring System

## AI Usage Disclosure

This mission was authored using LLM-assisted tooling (Claude by Anthropic).
- Narrative concept: AI-assisted, human-reviewed by Paul Fanger (ELOS)
- Asset references: catalog-validated, zero hallucination tolerance
- No live AI calls occur during gameplay
- Distribution: APL-ND (Arma Public License - No Derivatives)

## Technical
- Addon GUID: {addon_guid}
- World GUID: {world_guid}
- Catalog sources: Arma-Reforger-Samples, Reforger-Sample-Coop, CombatOpsEnhanced_AR, GRAD-COOP-Template-Reforger
- Files: {len(result['files_written'])} generated
"""
    (output_dir / "DISCLOSURE.md").write_text(disclosure)
    result["files_written"].append("DISCLOSURE.md")

    return result


def _write_layer(worlds_out: Path, mission_id: str, layer_name: str, content: str, result: dict) -> None:
    """Write a layer file and record it."""
    path = worlds_out / f"{mission_id}_{layer_name}.layer"
    path.write_text(content)
    result["files_written"].append(f"Worlds/{mission_id}_{layer_name}.layer")


def _build_spawnpoints(encounters: dict, resolver: CatalogResolver, result: dict) -> list[dict]:
    """Build spawnpoint entities from encounters.json or defaults."""
    entities = []
    spawn_points = encounters.get("spawn_points", [])

    # Default spawn points if encounters has none
    if not spawn_points:
        spawn_points = [
            {"team": "US", "coords": [263, 9, 245], "loadout_ref": "recon"},
        ]

    for sp in spawn_points:
        team = sp.get("team", "US")
        # Try to find matching spawnpoint in catalog
        sp_guid, sp_path = _resolve_spawnpoint_guid_for_team(resolver, team)
        if sp_guid:
            entities.append({
                "class_name": "SCR_SpawnPoint",
                "instance_name": f"SpawnPoint_{team}_01",
                "prefab_guid": sp_guid,
                "prefab_path": sp_path,
                "coords": sp.get("coords", [0, 0, 0]),
                "angle_y": sp.get("angle_y", 0),
            })
        else:
            result["warnings"].append(f"No spawnpoint GUID for team {team} in catalog")

    return entities


def _resolve_spawnpoint_guid_for_team(resolver: CatalogResolver, team: str) -> tuple[str | None, str]:
    """Find the best spawnpoint GUID for a given team."""
    results = resolver.find_by_type("spawnpoint")
    for r in results:
        path = r.get("path", "")
        if team.upper() in path.upper():
            return r["guid"], path
    if results:
        return results[0]["guid"], results[0].get("path", "")
    return None, ""


def _build_ai_layer(encounters: dict, resolver: CatalogResolver, result: dict) -> str:
    """Build the AI layer: groups + grouped waypoints, all with verified GUIDs."""
    from io import StringIO
    out = StringIO()

    # 1. Waypoints as $grp per waypoint-type (grouped by prefab)
    waypoints = encounters.get("waypoints", [])
    if waypoints:
        # Group waypoints by prefab_guid
        wp_by_prefab: dict[str, list[dict]] = {}
        for wp in waypoints:
            guid = wp.get("prefab_guid", "")
            path = wp.get("prefab_path", "")
            if not guid:
                continue
            if not resolver.is_valid_guid(guid):
                result["errors"].append(f"HALLUCINATED GUID in waypoint: {guid}")
                continue
            key = f"{guid}|{path}"
            wp_by_prefab.setdefault(key, []).append(wp)

        for key, wps in wp_by_prefab.items():
            guid, path = key.split("|", 1)
            # Use the class_name of the first waypoint or generic
            cn = wps[0].get("class_name", "AIWaypoint_Move")
            pref_ref = f"{{{guid}}}{path}"
            out.write(f'$grp {cn} : "{pref_ref}" {{\n')
            for wp in wps:
                c = wp.get("coords", [0, 0, 0])
                out.write(f' {wp["name"]} {{\n')
                out.write(f'  coords {_fmt_coord(c[0])} {_fmt_coord(c[1])} {_fmt_coord(c[2])}\n')
                out.write(f' }}\n')
            out.write(f'}}\n')

    # 2. AI Groups
    for group in encounters.get("ai_groups", []):
        # Skip groups that only spawn on trigger (handled in triggers layer)
        if group.get("spawn_on_trigger") and not encounters.get("triggers"):
            continue

        guid = group.get("prefab_guid")
        if not guid:
            result["warnings"].append(f"AI group '{group.get('name')}' has no prefab_guid — skipped")
            continue
        if not resolver.is_valid_guid(guid):
            result["errors"].append(f"HALLUCINATED GUID in ai_groups: {guid} — HALT")
            continue
        ref = resolver.resolve_guid(guid)
        path = ref.get("path", "") if ref else ""
        pref_ref = f"{{{guid}}}{path}"
        name = group.get("name", "AIGroup_01")
        c = group.get("coords", [0, 0, 0])

        out.write(f'SCR_AIGroup {name} : "{pref_ref}" {{\n')
        out.write(f' coords {_fmt_coord(c[0])} {_fmt_coord(c[1])} {_fmt_coord(c[2])}\n')
        # Waypoint list
        wp_refs = group.get("waypoint_refs", [])
        if wp_refs:
            out.write(f' m_aWaypoints {{\n')
            for wp in wp_refs:
                out.write(f'  "{wp}"\n')
            out.write(f' }}\n')
        out.write(f'}}\n')

    if not waypoints and not encounters.get("ai_groups"):
        out.write("// AI Layer: no groups or waypoints defined\n")

    return out.getvalue()


def _build_ai_entities(encounters: dict, resolver: CatalogResolver, result: dict) -> list[dict]:
    """Legacy stub — use _build_ai_layer instead."""
    return []


def _fmt_coord(v) -> str:
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def _build_tasks(encounters: dict, resolver: CatalogResolver, result: dict) -> list[dict]:
    """Build task entities from encounters.json.

    Tasks are engine built-in classes with no prefab GUID — emitted as inline class instances.
    """
    entities = []
    for task in encounters.get("tasks", []):
        cn = task.get("class", "SCR_EliminateTask")
        # No prefab_guid for engine built-in task classes
        entities.append({
            "class_name": cn,
            "instance_name": task.get("name", "Task_01"),
            # No prefab_guid — engine built-in, emitted as plain class instance
            "coords": task.get("coords", [0, 0, 0]),
            "fields": task.get("fields", {}),
        })
    return entities


def _build_triggers_layer(encounters: dict, resolver: CatalogResolver, result: dict) -> str:
    """Build triggers layer using generate_trigger_entity for correct Reforger syntax.

    Per research/04-tasks-triggers-format.md:
    - SphereRadius is the correct field name (not radius/m_fRadius)
    - SCR_AISpawnerComponent needs m_rnDefaultPrefab + RplComponent
    - Triggers are engine built-in classes (no prefab GUID)
    """
    from io import StringIO
    out = StringIO()

    triggers = encounters.get("triggers", [])
    if not triggers:
        out.write("// Triggers: none defined\n")
        return out.getvalue()

    for trigger in triggers:
        sphere_radius = trigger.get("radius", 50.0)
        spawner_comps = trigger.get("spawner_components", [])

        # Resolve spawner GUID paths from catalog if possible
        resolved_spawners = []
        for sc in spawner_comps:
            guid = sc.get("default_prefab_guid", "")
            if guid and resolver.is_valid_guid(guid):
                ref = resolver.resolve_guid(guid)
                sc["default_prefab_path"] = ref.get("path", "") if ref else ""
                resolved_spawners.append(sc)
            elif not guid:
                resolved_spawners.append(sc)
            else:
                result["errors"].append(f"HALLUCINATED GUID in trigger spawner: {guid}")

        out.write(generate_trigger_entity(
            class_name=trigger.get("class", "SCR_BaseTriggerEntity"),
            instance_name=trigger.get("name", "Trigger_01"),
            coords=trigger.get("coords", [0, 0, 0]),
            sphere_radius=sphere_radius,
            spawner_components=resolved_spawners if resolved_spawners else None,
        ))

    return out.getvalue()


def _build_triggers(encounters: dict, resolver: CatalogResolver, result: dict) -> list[dict]:
    """Legacy: kept for compatibility. Use _build_triggers_layer instead."""
    return []


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 backend/scripts/generate_mission.py <mission_id>")
        sys.exit(1)

    mid = sys.argv[1]
    mdir = ROOT / "missions" / mid

    if not mdir.exists():
        print(f"Mission dir not found: {mdir}")
        sys.exit(1)

    print(f"Generating mission tree for: {mid}")
    result = generate_mission_tree(mid, mdir, auto_approve=True)

    print(f"Status: {result['status']}")
    print(f"Files written: {len(result['files_written'])}")
    for f in result["files_written"]:
        print(f"  {f}")
    if result["warnings"]:
        print(f"Warnings: {len(result['warnings'])}")
        for w in result["warnings"]:
            print(f"  ⚠ {w}")
    if result["errors"]:
        print(f"ERRORS: {len(result['errors'])}")
        for e in result["errors"]:
            print(f"  ✗ {e}")
        sys.exit(1)
