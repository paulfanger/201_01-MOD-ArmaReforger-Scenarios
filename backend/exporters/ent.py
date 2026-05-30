"""Generate Worlds/<name>.ent — the world/scene file.

Two patterns from research/02-mission-format.md:
1. SubScene { Parent "worlds/Eden/Eden.ent" }
   — Most common for missions on existing maps (Eden, Everon, Arland, etc.)
   — Inherits terrain, lighting, environment from parent
   — Layer files extend/override parent content

2. Self-contained world with explicit Layer table
   — Each Layer entry gets an Index
   — Used for standalone missions or test worlds

Mission maps (known parent paths from reference repos):
  - Everon: "worlds/Everon/Everon.ent"
  - Eden (Everon+): "worlds/Eden/Eden.ent"
  - Arland: "worlds/Arland/Arland.ent"
  - Conflict (Everon): typically same world
"""
from typing import Literal

# Known world paths from reference repos
WORLD_PATHS = {
    "everon": "worlds/Everon/Everon.ent",
    "eden": "worlds/Eden/Eden.ent",
    "arland": "worlds/Arland/Arland.ent",
    "malden": "worlds/Malden/Malden.ent",
}

WorldMap = Literal["everon", "eden", "arland", "malden"]

# Layer names for the standard MVP addon-tree
STANDARD_LAYERS = [
    "gamemode",
    "managers",
    "spawnpoints",
    "AI",
    "tasks",
    "triggers",
    "environment",
]


def generate_world_subscene(
    map_id: str = "everon",
    custom_parent: str | None = None,
    include_layers: bool = True,
    layer_names: list[str] | None = None,
) -> str:
    """Generate .ent using SubScene pattern (inherits from existing map).

    Per empirical discovery 2026-05-30: .ent MUST include Layer entries for
    all layer files that are part of the world. Without them, WorldEditor only
    shows the 'default' layer and entities defined in layer files are invisible
    to the WorldEditorAPI (FindEntityByName returns null).

    Format verified from Arma-Reforger-Samples/SampleMod_NewFaction:
      SubScene { Parent "..." }
      Layer <name> { Index <n> }

    Args:
        map_id: one of 'everon', 'eden', 'arland', 'malden'
        custom_parent: override parent path if map not in known list
        include_layers: whether to include Layer entries (default True)
        layer_names: override default STANDARD_LAYERS list

    Returns:
        String content for .ent file.
    """
    parent = custom_parent or WORLD_PATHS.get(map_id.lower(), WORLD_PATHS["everon"])
    out = f'SubScene {{\n Parent "{parent}"\n}}\n'

    if include_layers:
        layers = layer_names or STANDARD_LAYERS
        # Default layer is always index 0
        out += "Layer default {\n Index 0\n}\n"
        for idx, name in enumerate(layers, start=1):
            out += f"Layer {name} {{\n Index {idx}\n}}\n"

    return out


def generate_world_with_layers(
    mission_id: str,
    layer_names: list[str] | None = None,
) -> str:
    """Generate .ent with explicit Layer table (self-contained world).

    Args:
        mission_id: mission identifier (used as layer filename prefix)
        layer_names: list of layer suffixes. Defaults to STANDARD_LAYERS.

    Returns:
        String content for .ent file.
    """
    layers = layer_names or STANDARD_LAYERS
    out = ""
    for idx, name in enumerate(layers):
        out += f"Layer {mission_id}_{name}     {{ Index {idx} }}\n"
    return out


def get_world_parent_path(map_id: str) -> str:
    """Return the world parent path for a given map_id."""
    return WORLD_PATHS.get(map_id.lower(), WORLD_PATHS["everon"])
