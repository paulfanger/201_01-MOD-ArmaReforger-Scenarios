"""Generate Missions/<name>.conf and .conf.meta files.

Mission header: SCR_MissionHeader with all required fields.
Per research/02-mission-format.md Mission-Header schema.

Auto-inserts EULA-compliant disclosure into description field.
"""
from .braces import emit_meta_configurations

DISCLOSURE = "AI-assisted authoring. Human-reviewed. No live AI calls during gameplay. | ELOS AI-Native Mission Authoring System"


def generate_mission_header(
    *,
    name: str,
    author: str = "ELOS AI-Native Mission Authoring System",
    description: str,
    world_guid: str,
    world_path: str,       # e.g. "Worlds/MyMission.ent"
    game_mode: str = "Coop",
    player_count: int = 8,
    time_hour: int = 20,   # Default: 20:00 (night ops)
    time_minute: int = 0,
    weather_preset: str | None = None,
    extra_fields: dict | None = None,
) -> str:
    """Generate .conf content with SCR_MissionHeader.

    The disclosure string is auto-appended to description per APL-ND recommendation.
    """
    full_desc = f"{description} | {DISCLOSURE}"
    world_ref = f"{{{world_guid}}}{world_path}"

    out = "SCR_MissionHeader {\n"
    out += f' World "{world_ref}"\n'
    out += f' m_sName "{name}"\n'
    out += f' m_sAuthor "{author}"\n'
    out += f' m_sDescription "{full_desc}"\n'
    out += f' m_sGameMode "{game_mode}"\n'
    out += f' m_iPlayerCount {player_count}\n'
    out += f' m_bOverrideScenarioTimeAndWeather 1\n'
    out += f' m_iStartingHours {time_hour}\n'
    out += f' m_iStartingMinutes {time_minute}\n'
    if weather_preset:
        out += f' m_sWeatherPreset "{weather_preset}"\n'
    if extra_fields:
        for k, v in extra_fields.items():
            if isinstance(v, str):
                out += f' {k} "{v}"\n'
            else:
                out += f' {k} {v}\n'
    out += "}\n"
    return out


def generate_conf_meta(file_guid: str, file_path: str) -> str:
    """Generate .conf.meta sidecar file.

    Follows the 5-platform Configurations pattern observed in reference repos.
    """
    out = "MetaFileClass {\n"
    out += f' Name "{{{file_guid}}}{file_path}"\n'
    out += emit_meta_configurations("CONFResourceClass")
    out += "}\n"
    return out


def generate_ent_meta(file_guid: str, file_path: str) -> str:
    """Generate .ent.meta sidecar file."""
    out = "MetaFileClass {\n"
    out += f' Name "{{{file_guid}}}{file_path}"\n'
    out += emit_meta_configurations("ResourceClass")
    out += "}\n"
    return out
