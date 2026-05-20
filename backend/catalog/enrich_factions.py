"""Catalog Enrichment — Phase 1: Faction Semantic Aliases + Loadout GUIDs.

Adds semantic alias entries so narrative-designer refs like ENF_Faction_US
and ENF_Faction_USSR resolve correctly via asset-curator.

Also enriches existing US/USSR faction entries with faction_key metadata
and adds a semantic ALIASES index for the resolver.

Usage:
    python3 backend/catalog/enrich_factions.py [--dry-run]
"""
import json
import sys
from pathlib import Path
from datetime import date

CATALOG_DIR = Path(__file__).parent.parent.parent / "catalog"
TODAY = date.today().isoformat()


# ---- Semantic aliases: maps narrative_designer asset_id_ref -> actual catalog GUID ----
# Source: confirmed via Reforger-Sample-Coop/CoopFactionManager.et +
#         CombatOpsEnhanced_AR/COE_FactionManager.et (verified 2026-05-20)

SEMANTIC_ALIASES = {
    "ENF_Faction_US": {
        "guid": "ADFDBDA163950168",
        "path": "Configs/Factions/US_Campaign.conf",
        "type": "faction",
        "faction_key": "US",
        "display_name": "US_Campaign",
        "description": "US Army — vanilla coop faction config (BLUFOR). "
                       "Player faction for PVE coop missions on Everon/Arland.",
        "source_verified": "Reforger-Sample-Coop/CoopFactionManager.et",
    },
    "ENF_Faction_USSR": {
        "guid": "15B582F8FA0B0940",
        "path": "Configs/Factions/USSR_Campaign.conf",
        "type": "faction",
        "faction_key": "USSR",
        "display_name": "USSR_Campaign",
        "description": "USSR Army — vanilla coop faction config (OPFOR). "
                       "AI enemy faction for PVE coop missions.",
        "source_verified": "Reforger-Sample-Coop/CoopFactionManager.et",
    },
    "ENF_Faction_FIA": {
        "guid": "CF9447B87AB774DB",
        "path": "Configs/Factions/FIA_Campaign.conf",
        "type": "faction",
        "faction_key": "FIA",
        "display_name": "FIA_Campaign",
        "description": "FIA (Freedom & Independence Army) — INDFOR faction. "
                       "Partisan/resistance force, usable as neutral or 3rd faction.",
        "source_verified": "Reforger-Sample-Coop/CoopFactionManager.et",
    },
}

# ---- Additional confirmed GUIDs not yet enriched ----
# From COE_FactionManager.et + COE_LoadoutManager.et (verified 2026-05-20)

ADDITIONAL_FACTION_ENRICHMENT = [
    # Faction-level prefab entries — enrich with faction_key metadata
    {
        "guid": "ADFDBDA163950168",
        "faction_key": "US",
        "faction_side": "BLUFOR",
        "class_hint": "SCR_CampaignFaction",
        "aliases": ["ENF_Faction_US", "US_Campaign"],
    },
    {
        "guid": "15B582F8FA0B0940",
        "faction_key": "USSR",
        "faction_side": "OPFOR",
        "class_hint": "SCR_CampaignFaction",
        "aliases": ["ENF_Faction_USSR", "USSR_Campaign"],
    },
    {
        "guid": "CF9447B87AB774DB",
        "faction_key": "FIA",
        "faction_side": "INDFOR",
        "class_hint": "SCR_CampaignFaction",
        "aliases": ["ENF_Faction_FIA", "FIA_Campaign"],
    },
]

# ---- Character prefab entries with faction_key (from COE_FactionManager.et) ----
# These already exist in catalog but can be enriched with faction_key field

CHARACTER_FACTION_KEYS = {
    # US Army characters
    "5B1996C05B1E51A4": "US",   # Character_US_AR
    "84029128FA6F6BB9": "US",   # Character_US_GL
    "42A502E3BB727CEB": "US",   # Character_US_HeliPilot
    "27BF1FF235DD6036": "US",   # Character_US_LAT
    "1623EA3AEFACA0E4": "US",   # Character_US_MG
    "3726077BE60962FF": "US",   # Character_US_RTO
    "E45F1E163F5CA080": "US",   # Character_US_SL
    "0F6689B491641155": "US",   # Character_US_Sniper
    "DB108F0264C75F14": "US",   # Character_US_Officer (COE)
    "284E735C6C70DAD2": "US",   # Character_US_BaseLoadout

    # USSR Army characters
    "23ADBBC31B6A3DC6": "USSR",  # Character_USSR_AR
    "1C78331E156A3D65": "USSR",  # Character_USSR_AT
    "5346CF7E39A65A6B": "USSR",  # Character_USSR_Base
    "8E0FE664CE7D1CA9": "USSR",  # Character_USSR_GL
    "A62FA97C4EC64F14": "USSR",  # Character_USSR_HeliPilot
    "96C784C502AC37DA": "USSR",  # Character_USSR_MG
    "AB9726163EC1BD81": "USSR",  # Character_USSR_Medic
    "5117311FB822FD1F": "USSR",  # Character_USSR_Officer
    "612F43A4D5AE765F": "USSR",  # Character_USSR_RTO
    "DCB41B3746FDD1BE": "USSR",  # Character_USSR_Rifleman
    "5436629450D8387A": "USSR",  # Character_USSR_SL
    "976AC400219898FA": "USSR",  # Character_USSR_Sharpshooter

    # US Groups
    "84E5BBAB25EA23E5": "US",   # Group_US_FireTeam
    "FCF7F5DC4F83955C": "US",   # Group_US_LightFireTeam
    "958039B857396B7B": "US",   # Group_US_MachineGunTeam
    "D807C7047E818488": "US",   # Group_US_SniperTeam
    "DE747BC9217D383C": "US",   # Group_US_Team_GL
    "FAEA8B9E1252F56E": "US",   # Group_US_Team_LAT
    "81B6DBF2B88545F5": "US",   # Group_US_Team_Suppress

    # USSR Groups
    "A2F75E45C66B1C0A": "USSR",  # Group_USSR_MachineGunTeam
    "30ED11AA4F0D41E5": "USSR",  # Group_USSR_FireGroup
    "657590C1EC9E27D3": "USSR",  # Group_USSR_LightFireTeam
    "96BAB56E6558788E": "USSR",  # Group_USSR_Team_AT
    "43C7A28EEB660FF8": "USSR",  # Group_USSR_Team_GL
    "1C0502B5729E7231": "USSR",  # Group_USSR_Team_Suppress
    "8DE0C0830FE0C33D": "USSR",  # Group_USSR_Base
    "359353A0A5A52216": "USSR",  # Group_USSR_Defenders

    # US Loadouts
    "7C7C65FD583E6612": "US",   # Loadout_US_Rifleman.conf
    "AFA36BB8828E381A": "US",   # Loadout_US_MG.conf
    "121FC1ABB7FE098C": "US",   # Loadout_US_LAT.conf
    "0B4549C656AFC7AE": "US",   # Loadout_US_GL.conf
    "0EFB9B7C7EF8B247": "US",   # Loadout_US_Sniper.conf

    # USSR Loadouts
    "5F9034642E99437D": "USSR",  # Loadout_USSR_Rifleman.conf
    "E97C426E941D8FDC": "USSR",  # Loadout_USSR_MG.conf
    "C1C1DB68C6FC265B": "USSR",  # Loadout_USSR_AT.conf
    "A62BF2390565DC0B": "USSR",  # Loadout_USSR_GL.conf
    "FB56BAF9A1BBAB39": "USSR",  # Loadout_USSR_Sharpshooter.conf
}


def update_catalog_entry(guid: str, updates: dict, dry_run: bool = False) -> bool:
    """Update an existing catalog entry with additional metadata."""
    # Find the file
    for type_dir in CATALOG_DIR.iterdir():
        if not type_dir.is_dir():
            continue
        fp = type_dir / f"{guid}.json"
        if fp.exists():
            data = json.loads(fp.read_text())
            changed = False
            for k, v in updates.items():
                if data.get(k) != v:
                    data[k] = v
                    changed = True
            if changed:
                data["enriched_at"] = TODAY
                data["enriched_by"] = "catalog-enrich-factions"
                if not dry_run:
                    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
                return True
            return False
    return False


def main(dry_run: bool = False) -> None:
    if not CATALOG_DIR.exists():
        print("ERROR: Catalog not bootstrapped. Run bootstrap.py first.")
        sys.exit(1)

    index_path = CATALOG_DIR / "INDEX.json"
    index = json.loads(index_path.read_text())

    print("=== Phase 1: Semantic Alias File ===")
    aliases_path = CATALOG_DIR / "ALIASES.json"

    # Build aliases file mapping semantic names -> GUID
    aliases = {
        "version": 1,
        "generated_at": TODAY,
        "description": "Semantic alias map: narrative_designer asset_id_ref -> catalog GUID",
        "aliases": {
            name: {
                "guid": info["guid"],
                "path": info["path"],
                "type": info["type"],
                "faction_key": info.get("faction_key"),
                "display_name": info["display_name"],
                "description": info.get("description", ""),
                "aliases": [name],
            }
            for name, info in SEMANTIC_ALIASES.items()
        }
    }

    if dry_run:
        print(f"  Would write {aliases_path}")
        for name in SEMANTIC_ALIASES:
            guid = SEMANTIC_ALIASES[name]["guid"]
            print(f"  {name} -> {guid}")
    else:
        aliases_path.write_text(json.dumps(aliases, indent=2, ensure_ascii=False))
        print(f"  Written: {aliases_path}")
        for name in SEMANTIC_ALIASES:
            guid = SEMANTIC_ALIASES[name]["guid"]
            print(f"  {name} -> {guid}")

    print(f"\n=== Phase 2: Enrich Faction Entries with faction_key ===")
    enriched_count = 0
    for enrich in ADDITIONAL_FACTION_ENRICHMENT:
        guid = enrich["guid"]
        updates = {}
        if "faction_key" in enrich:
            updates["faction_key"] = enrich["faction_key"]
        if "faction_side" in enrich:
            updates["faction_side"] = enrich["faction_side"]
        if "class_hint" in enrich:
            updates["class_hint"] = enrich["class_hint"]
        if "aliases" in enrich:
            updates["aliases"] = enrich["aliases"]

        result = update_catalog_entry(guid, updates, dry_run)
        action = "Would update" if dry_run else "Updated"
        status = "changed" if result else "unchanged"
        print(f"  {action} {guid}: {status}")
        if result:
            enriched_count += 1

    print(f"\n=== Phase 3: Add faction_key to Character/Group/Loadout entries ===")
    char_enriched = 0
    char_missing = []
    for guid, faction_key in CHARACTER_FACTION_KEYS.items():
        if guid in index["guid_to_type"]:
            result = update_catalog_entry(guid, {"faction_key": faction_key}, dry_run)
            if result:
                char_enriched += 1
        else:
            char_missing.append(guid)

    print(f"  Entries enriched with faction_key: {char_enriched}")
    if char_missing:
        print(f"  WARNING: {len(char_missing)} GUIDs not found in catalog: {char_missing}")

    print(f"\n=== Phase 4: Update INDEX with alias support ===")
    if not dry_run:
        # Add aliases registry to index
        index["aliases_file"] = "ALIASES.json"
        index["semantic_aliases"] = {
            name: info["guid"] for name, info in SEMANTIC_ALIASES.items()
        }
        index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))
        print(f"  INDEX updated with {len(SEMANTIC_ALIASES)} semantic aliases")
    else:
        print(f"  Would add {len(SEMANTIC_ALIASES)} semantic aliases to INDEX")

    print(f"\n=== Summary ===")
    print(f"  Semantic aliases registered: {len(SEMANTIC_ALIASES)}")
    print(f"  Faction entries enriched: {enriched_count}")
    print(f"  Character/Group/Loadout entries enriched: {char_enriched}")
    if dry_run:
        print("  [DRY RUN — no files written]")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
