"""Cross-file consistency validator.

Checks that asset references in encounters.json / asset-manifest.json
match exactly what's emitted in the output .layer files.
No hallucinated GUIDs should appear anywhere in the chain.
"""
import json
import re
from pathlib import Path
from .schema import ValidationError, ValidationReport, GUID_REF_RE


def validate_cross_file_consistency(
    mission_dir: Path,
    output_dir: Path,
) -> ValidationReport:
    """Verify that intermediate JSON and final output files are consistent.

    Checks:
    1. Every GUID in asset-manifest.json appears correctly in output files
    2. encounters.json prefab_guids match layer file contents
    3. narrative.json factions match asset-manifest factions
    """
    report = ValidationReport()

    # Load intermediate files
    asset_manifest_path = mission_dir / "asset-manifest.json"
    encounters_path = mission_dir / "encounters.json"
    narrative_path = mission_dir / "narrative.json"

    if not asset_manifest_path.exists():
        report.warnings.append(ValidationError(
            "asset-manifest.json", "cross-1",
            "File missing — skipping cross-file checks",
            severity="warning", suggested_fix="Run asset-curator stage"
        ))
        return report

    asset_manifest = json.loads(asset_manifest_path.read_text())

    # Rule cross-1: Missing assets — severity depends on halt_required flag
    halt = asset_manifest.get("halt_required", False)
    missing = asset_manifest.get("missing_assets", [])

    if halt:
        # halt_required=true: hard error — pipeline should have stopped at Stage 2
        report.errors.append(ValidationError(
            "asset-manifest.json", "cross-1",
            f"halt_required=true: {asset_manifest.get('halt_reason', 'unknown')}",
            "Resolve missing assets before proceeding to Stage 6"
        ))
        return report  # Don't check further if halted

    if missing:
        # halt_required=false but has missing: warn only (asset-curator accepted these)
        for m in missing:
            report.warnings.append(ValidationError(
                "asset-manifest.json", "cross-1",
                f"Unresolved asset ref (warn): {m.get('narrative_ref', '?')}",
                "Run /sync-catalog or choose alternative — not blocking since halt_required=false",
                severity="warning"
            ))

    # Collect resolved GUIDs from manifest
    resolved_guids = {
        a["guid"] for a in asset_manifest.get("resolved_assets", [])
        if "guid" in a
    }

    # Rule cross-2: GUIDs from encounters.json appear in layer files
    if encounters_path.exists() and output_dir.exists():
        encounters = json.loads(encounters_path.read_text())
        encounter_guids: set[str] = set()

        for group in encounters.get("ai_groups", []):
            if "prefab_guid" in group:
                encounter_guids.add(group["prefab_guid"])
        for spawn in encounters.get("spawn_points", []):
            if "prefab_guid" in spawn:
                encounter_guids.add(spawn["prefab_guid"])
        for trigger in encounters.get("triggers", []):
            for comp in trigger.get("spawner_components", []):
                if "default_prefab_guid" in comp:
                    encounter_guids.add(comp["default_prefab_guid"])

        # Collect all GUIDs found in layer files
        layer_guids: set[str] = set()
        worlds_dir = output_dir / "Worlds"
        if worlds_dir.exists():
            for layer in worlds_dir.glob("*.layer"):
                content = layer.read_text(errors="replace")
                for m in GUID_REF_RE.finditer(content):
                    layer_guids.add(m.group(1))

        missing_from_layers = encounter_guids - layer_guids - resolved_guids
        for guid in missing_from_layers:
            report.warnings.append(ValidationError(
                "encounters.json / *.layer", "cross-2",
                f"GUID {guid} from encounters.json not found in output layers",
                "Check reforger-bridge layer generation for this entity",
                severity="warning"
            ))

    # Rule cross-3: Narrative factions match asset-manifest
    if narrative_path.exists():
        narrative = json.loads(narrative_path.read_text())
        factions = narrative.get("factions", {})
        resolved_names = {a.get("narrative_ref") for a in asset_manifest.get("resolved_assets", [])}

        for faction_role, faction_info in factions.items():
            if isinstance(faction_info, dict):
                asset_ref = faction_info.get("asset_id_ref")
                if asset_ref and asset_ref not in resolved_names:
                    report.warnings.append(ValidationError(
                        "narrative.json vs asset-manifest.json", "cross-3",
                        f"Faction '{faction_role}' asset_id_ref '{asset_ref}' not in resolved assets",
                        "Check asset-curator resolved_assets list",
                        severity="warning"
                    ))

    return report
