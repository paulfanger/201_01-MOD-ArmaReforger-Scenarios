"""Generate Worlds/<name>_<type>.layer files.

Per research/02-mission-format.md Entity Layers schema.

Supported entity patterns:
- Single entity (most common): ClassName name : "{GUID}path.et" { ... }
- Grouped entities ($grp): for waypoints, AI groups with multiple instances
- Inline component list: components { ComponentClass { ... } }

Layer types in the standard MVP tree:
- gamemode: SCR_CoopGameMode
- managers: GameMode, FactionManager, LoadoutManager, TimeAndWeather
- spawnpoints: SCR_SpawnPoint for US/USSR player spawns
- AI: SCR_AIGroup with patrols, USSR groups
- tasks: SCR_EliminateTask, SCR_TriggerTask
- triggers: SCR_BaseTriggerEntity with SCR_AISpawnerComponent
- environment: TimeAndWeatherManagerEntity
"""
from io import StringIO
from typing import Any


def generate_layer(entities: list[dict]) -> str:
    """Generate a .layer file from a list of entity specs.

    Each entity dict has:
      Required:
        class_name (str): Enfusion class, e.g. "SCR_SpawnPoint"
        prefab_guid (str): 16-char hex GUID from catalog
        prefab_path (str): path part of prefab ref, e.g. "PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et"

      Optional:
        instance_name (str): entity instance name, e.g. "SpawnPoint_US_01"
        coords (list[float]): [x, y, z] world coordinates
        angle_y (float): rotation around Y axis (yaw)
        angle_x (float): rotation around X axis (pitch)
        angle_z (float): rotation around Z axis (roll)
        fields (dict): additional Enfusion fields {key: value}
        components (list[dict]): embedded component blocks
        children (list[dict]): child entities (recursive)
        $grp (bool): if True, emit as $grp grouped entity

    For $grp entities, additionally:
        instances (list[dict]): each with {name, coords, fields?}
    """
    out = StringIO()
    for ent in entities:
        if ent.get("$grp"):
            out.write(_emit_grouped(ent))
        else:
            out.write(_emit_single(ent))
    return out.getvalue()


def generate_gamemode_layer(
    gamemode_guid: str,
    gamemode_path: str,
    gamemode_class: str = "SCR_CoopGameMode",
    instance_name: str = "CoopGameMode",
) -> str:
    """Convenience: generate the gamemode layer."""
    return generate_layer([{
        "class_name": gamemode_class,
        "instance_name": instance_name,
        "prefab_guid": gamemode_guid,
        "prefab_path": gamemode_path,
    }])


def generate_managers_layer(
    managers: list[str] | None = None,
    coop_faction_manager_guid: str = "E4075339B4E24E10",
) -> str:
    """Generate the managers layer.

    Per research/04-tasks-triggers-format.md: FactionManager must be a top-level
    prefab-based entity (CoopFactionManager.et), NOT an inline class instance.
    Other managers (GameMode, LoadoutManager, TimeAndWeather) are engine built-ins.

    Args:
        managers: optional override list of inline manager class names
        coop_faction_manager_guid: verified GUID for CoopFactionManager.et
    """
    out = StringIO()

    # FactionManager: prefab-based top-level entity (confirmed by research/04)
    coop_faction_path = "Prefabs/MP/Managers/Factions/CoopFactionManager.et"
    out.write(
        f'SCR_FactionManager CoopFactionManager : "{{{coop_faction_manager_guid}}}{coop_faction_path}" {{\n'
        f'}}\n'
    )

    # Engine built-in managers (inline, no prefab GUID)
    inline_managers = managers or ["LoadoutManager", "TimeAndWeatherManagerEntity"]
    for mgr in inline_managers:
        out.write(f"{mgr} {mgr} {{\n}}\n")

    return out.getvalue()


def generate_trigger_entity(
    class_name: str,
    instance_name: str,
    coords: list,
    sphere_radius: float = 50.0,
    spawner_components: list | None = None,
) -> str:
    """Generate a trigger entity with correct Reforger field names.

    Per research/04-tasks-triggers-format.md:
    - Correct field: SphereRadius (NOT radius or m_fRadius)
    - SCR_AISpawnerComponent uses m_rnDefaultPrefab, m_vSpawnPosition, m_aWaypointsList
    - RplComponent required alongside SCR_AISpawnerComponent
    """
    out = StringIO()
    c = coords
    out.write(f"{class_name} {instance_name} {{\n")
    out.write(f" coords {_fmt_coord(c[0])} {_fmt_coord(c[1])} {_fmt_coord(c[2])}\n")
    out.write(f" SphereRadius {sphere_radius}\n")

    if spawner_components:
        for spawner in spawner_components:
            prefab_guid = spawner.get("default_prefab_guid", "")
            prefab_path = spawner.get("default_prefab_path", "")
            spawn_pos = spawner.get("spawn_pos", [c[0] + 5, c[1], c[2] + 5])
            waypoints = spawner.get("waypoints", [])

            if prefab_guid and prefab_path:
                pref_ref = f"{{{prefab_guid}}}{prefab_path}"
                out.write(f' components SCR_AISpawnerComponent {{\n')
                out.write(f'  m_rnDefaultPrefab "{pref_ref}"\n')
                out.write(f'  m_vSpawnPosition {_fmt_coord(spawn_pos[0])} {_fmt_coord(spawn_pos[1])} {_fmt_coord(spawn_pos[2])}\n')
                if waypoints:
                    out.write(f'  m_aWaypointsList {{\n')
                    for wp in waypoints:
                        out.write(f'   "{wp}"\n')
                    out.write(f'  }}\n')
                out.write(f' }}\n')
                # RplComponent always accompanies SCR_AISpawnerComponent
                out.write(f' components RplComponent {{\n }}\n')

    out.write(f"}}\n")
    return out.getvalue()


def generate_environment_layer(time_hour: int = 20, time_minute: int = 0, weather: str = "clear") -> str:
    """Generate environment override layer.

    TimeAndWeatherManagerEntity is an engine built-in class — no prefab GUID.
    Emitted as a plain inline class instance.
    """
    out = StringIO()
    out.write(f"TimeAndWeatherManagerEntity TimeAndWeatherManager {{\n")
    out.write(f" TimeOfDay {{\n")
    out.write(f"  m_iDefaultHours {time_hour}\n")
    out.write(f"  m_iDefaultMinutes {time_minute}\n")
    out.write(f" }}\n")
    if weather and weather != "clear":
        out.write(f' WeatherPreset "{weather}"\n')
    out.write(f"}}\n")
    return out.getvalue()


# ---- Internal emitters -------------------------------------------------------

def _emit_single(ent: dict) -> str:
    out = StringIO()
    cn = ent.get("class_name", "GenericEntity")
    inst = ent.get("instance_name", "")
    guid = ent.get("prefab_guid", "")
    path = ent.get("prefab_path", "")

    # Only use prefab ref if guid is provided AND non-empty (engine built-ins have no guid)
    pref_ref = f"{{{guid}}}{path}" if (guid and path) else ""

    # Build header line
    if pref_ref and inst:
        header = f'{cn} {inst} : "{pref_ref}"'
    elif pref_ref:
        header = f'{cn} : "{pref_ref}"'
    elif inst:
        header = f"{cn} {inst}"
    else:
        header = cn

    out.write(f"{header} {{\n")

    # Coords
    if "coords" in ent:
        c = ent["coords"]
        out.write(f" coords {_fmt_coord(c[0])} {_fmt_coord(c[1])} {_fmt_coord(c[2])}\n")

    # Rotation
    for axis, field in [("angle_x", "angleX"), ("angle_y", "angleY"), ("angle_z", "angleZ")]:
        if axis in ent:
            out.write(f" {field} {ent[axis]}\n")

    # Additional fields
    for k, v in (ent.get("fields") or {}).items():
        out.write(_emit_field(k, v, level=1))

    # Components
    for comp in (ent.get("components") or []):
        out.write(_emit_component(comp))

    # Children
    for child in (ent.get("children") or []):
        out.write(_emit_single(child))

    out.write("}\n")
    return out.getvalue()


def _emit_grouped(grp: dict) -> str:
    """Emit $grp pattern for grouped instances (e.g. waypoints)."""
    out = StringIO()
    cn = grp.get("class_name", "GenericEntity")
    guid = grp.get("prefab_guid", "")
    path = grp.get("prefab_path", "")
    pref_ref = f"{{{guid}}}{path}" if guid else ""

    if pref_ref:
        out.write(f'$grp {cn} : "{pref_ref}" {{\n')
    else:
        out.write(f"$grp {cn} {{\n")

    for inst in grp.get("instances", []):
        name = inst.get("name", "inst")
        out.write(f" {name} {{\n")
        if "coords" in inst:
            c = inst["coords"]
            out.write(f"  coords {_fmt_coord(c[0])} {_fmt_coord(c[1])} {_fmt_coord(c[2])}\n")
        for k, v in (inst.get("fields") or {}).items():
            out.write(_emit_field(k, v, level=2))
        out.write(" }\n")

    out.write("}\n")
    return out.getvalue()


def _emit_component(comp: dict) -> str:
    """Emit a component block inside an entity."""
    out = StringIO()
    cn = comp.get("class_name", "Component")
    out.write(f" components {cn} {{\n")
    for k, v in (comp.get("fields") or {}).items():
        out.write(_emit_field(k, v, level=2))
    out.write(" }\n")
    return out.getvalue()


def _emit_field(key: str, value: Any, level: int = 1) -> str:
    indent = " " * level
    if isinstance(value, dict):
        lines = f"{indent}{key} {{\n"
        for k, v in value.items():
            lines += _emit_field(k, v, level + 1)
        lines += f"{indent}}}\n"
        return lines
    elif isinstance(value, list):
        lines = f"{indent}{key} {{\n"
        for item in value:
            if isinstance(item, str):
                lines += f'{indent} "{item}"\n'
            elif isinstance(item, dict):
                for k, v in item.items():
                    lines += _emit_field(k, v, level + 1)
            else:
                lines += f"{indent} {item}\n"
        lines += f"{indent}}}\n"
        return lines
    elif isinstance(value, str):
        escaped = value.replace('"', '\\"')
        return f'{indent}{key} "{escaped}"\n'
    elif isinstance(value, bool):
        return f"{indent}{key} {'1' if value else '0'}\n"
    else:
        return f"{indent}{key} {value}\n"


def _fmt_coord(v: Any) -> str:
    """Format a coordinate value (int or float)."""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)
