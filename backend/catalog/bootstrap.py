"""Catalog Bootstrap Parser.

Extracts {GUID}Path.et patterns from cloned reference repos.
Writes to catalog/{type}/{guid}.json + catalog/INDEX.json.

Sources (clone once to /tmp/reforger-research/):
- exocs/Reforger-Sample-Coop
- BohemiaInteractive/Arma-Reforger-Samples
- Kexanone/CombatOpsEnhanced_AR
- gruppe-adler/GRAD-COOP-Template-Reforger

Usage:
    python3 backend/catalog/bootstrap.py [--dry-run]
"""
import re
import json
import sys
from pathlib import Path
from datetime import date

# Matches: {ABCDEF1234567890}some/path.et
GUID_PATTERN = re.compile(r'\{([0-9A-F]{16})\}([^"\s\r\n]+\.(et|gproj|conf|ent|edds|st))')

# Matches entity declarations like:  SomeClass entityName : "{GUID}path.et"
ENTITY_DECL = re.compile(
    r'^\s*(SCR_\w+|\w+Manager\w*|\w+Entity\w*|GenericEntity|\w+Component\w*)\s+\w+\s*:\s*"\{([0-9A-F]{16})\}([^"]+)"',
    re.MULTILINE
)

# Matches prefab inheritance inside Brace-Syntax files
INHERIT_DECL = re.compile(
    r'^\s*(\w+)\s+\w+\s*:\s*"(\{[0-9A-F]{16}\}[^"]+)"',
    re.MULTILINE
)

CORE_GUID = "58D0FB3206B6F859"  # Arma Reforger core dependency — always required

REPO_PATHS = [
    Path("/tmp/reforger-research/Reforger-Sample-Coop"),
    Path("/tmp/reforger-research/Arma-Reforger-Samples"),
    Path("/tmp/reforger-research/CombatOpsEnhanced_AR"),
    Path("/tmp/reforger-research/GRAD-COOP-Template-Reforger"),
]

CATALOG_DIR = Path(__file__).parent.parent.parent / "catalog"
TODAY = date.today().isoformat()


def parse_repo(repo_path: Path) -> list[dict]:
    """Walk repo, find mission/layer/conf/ent files, extract GUID-refs."""
    found = []
    extensions = {".layer", ".conf", ".ent", ".gproj", ".et"}

    for f in repo_path.rglob("*"):
        if f.suffix not in extensions or not f.is_file():
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        rel = str(f.relative_to(repo_path))

        # Generic GUID refs (highest volume)
        for m in GUID_PATTERN.finditer(content):
            found.append({
                "guid": m.group(1),
                "path": m.group(2),
                "ext": m.group(3),
                "source_file": rel,
                "source_repo": repo_path.name,
            })

        # Rich entity declarations (class name known)
        for m in ENTITY_DECL.finditer(content):
            found.append({
                "class_name": m.group(1),
                "guid": m.group(2),
                "path": m.group(3),
                "source_file": rel,
                "source_repo": repo_path.name,
                "kind": "entity_decl",
            })

    return found


def classify_type(path: str, class_name: str | None) -> str:
    """Classify asset type from path hints and class name."""
    p = path.lower()
    cn = (class_name or "").lower()

    # Class-name based (most specific)
    if "faction" in cn:
        return "faction"
    if "loadout" in cn:
        return "loadout"
    if "spawnpoint" in cn or "spawn" in cn:
        return "spawnpoint"
    if "waypoint" in cn:
        return "waypoint"
    if "task" in cn and "scr_" in cn:
        return "task"
    if "gamemode" in cn or "game_mode" in cn:
        return "gamemode"
    if "trigger" in cn:
        return "trigger"
    if "aigroup" in cn or "aigroup" in cn or "_ai" in cn:
        return "ai_group"

    # Path based
    if "/vehicles/" in p or "/vehicle/" in p:
        return "vehicle"
    if "/weapons/" in p or "/weapon/" in p:
        return "weapon"
    if "/factions/" in p or "/faction/" in p:
        return "faction"
    if "/groups/" in p or "/group/" in p:
        return "group"
    if "/loadouts/" in p or "/loadout/" in p:
        return "loadout"
    if "/spawnpoints/" in p or "/spawn/" in p:
        return "spawnpoint"
    if "/waypoints/" in p or "/waypoint/" in p:
        return "waypoint"
    if "/tasks/" in p or "/task/" in p:
        return "task"
    if "/gamemodes/" in p or "/modes/" in p:
        return "gamemode"
    if "/triggers/" in p or "/trigger/" in p:
        return "trigger"

    # Extension based (least specific)
    if p.endswith(".gproj"):
        return "gproj"
    if p.endswith(".conf"):
        return "config"
    if p.endswith(".et"):
        return "prefab"

    return "unknown"


def main(dry_run: bool = False) -> None:
    all_refs: list[dict] = []

    # Collect from all repos
    for rp in REPO_PATHS:
        if not rp.exists():
            print(f"WARNING: repo not found: {rp} — skipping")
            continue
        refs = parse_repo(rp)
        all_refs.extend(refs)
        print(f"  {rp.name}: {len(refs)} refs found")

    print(f"\nTotal raw refs: {len(all_refs)}")

    # Dedupe by GUID — prefer richest entry (class_name > plain)
    by_guid: dict[str, dict] = {}
    for ref in all_refs:
        g = ref["guid"]
        if g not in by_guid:
            by_guid[g] = ref
        else:
            existing = by_guid[g]
            # Prefer entity_decl (has class_name) over plain ref
            if ref.get("kind") == "entity_decl" and existing.get("kind") != "entity_decl":
                by_guid[g] = ref

    print(f"Unique GUIDs: {len(by_guid)}")

    # Classify + enrich
    by_type: dict[str, dict[str, dict]] = {}
    for guid, ref in by_guid.items():
        t = classify_type(ref.get("path", ""), ref.get("class_name"))
        ref["type"] = t
        ref["display_name"] = ref.get("class_name") or Path(ref.get("path", "unknown")).stem
        ref["verified_at"] = TODAY
        ref["verified_by"] = "catalog-bootstrap"
        by_type.setdefault(t, {})[guid] = ref

    if dry_run:
        print("\nDRY RUN — no files written")
        for t, items in sorted(by_type.items()):
            print(f"  {t}: {len(items)}")
        return

    # Write per-guid files — preserve enrichment fields added by enrich_factions.py
    ENRICHMENT_KEYS = {
        "faction_key", "faction_side", "class_hint", "aliases",
        "enriched_at", "enriched_by",
    }

    CATALOG_DIR.mkdir(exist_ok=True)
    for t, items in by_type.items():
        type_dir = CATALOG_DIR / t
        type_dir.mkdir(parents=True, exist_ok=True)
        for guid, ref in items.items():
            fp = type_dir / f"{guid}.json"
            if fp.exists():
                # Preserve enrichment fields from previous runs
                existing = json.loads(fp.read_text())
                for key in ENRICHMENT_KEYS:
                    if key in existing and key not in ref:
                        ref[key] = existing[key]
            fp.write_text(json.dumps(ref, indent=2, ensure_ascii=False))

    # Write INDEX — preserve semantic aliases written by enrich_factions.py
    existing_index: dict = {}
    index_path = CATALOG_DIR / "INDEX.json"
    if index_path.exists():
        existing_index = json.loads(index_path.read_text())

    index = {
        "version": 1,
        "generated_at": TODAY,
        "total_assets": len(by_guid),
        "by_type": {t: len(items) for t, items in sorted(by_type.items())},
        "core_guid": CORE_GUID,
        "guid_to_type": {g: ref["type"] for g, ref in by_guid.items()},
        "sources": [rp.name for rp in REPO_PATHS if rp.exists()],
    }
    # Preserve enrichment extensions
    if "semantic_aliases" in existing_index:
        index["semantic_aliases"] = existing_index["semantic_aliases"]
    if "aliases_file" in existing_index:
        index["aliases_file"] = existing_index["aliases_file"]

    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    print(f"\nCatalog written to: {CATALOG_DIR}")
    print(f"Total unique GUIDs: {len(by_guid)}")
    print("By type:")
    for t, count in sorted(index["by_type"].items()):
        print(f"  {t}: {count}")
    print(f"\nCore GUID present in index: {CORE_GUID}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
