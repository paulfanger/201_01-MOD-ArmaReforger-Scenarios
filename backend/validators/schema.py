"""Mission tree validator — 12 rules from research/02-mission-format.md.

Zero-tolerance for hallucinated GUIDs: any GUID reference that isn't
in the catalog OR a locally-minted mission GUID = ValidationError.

Run after reforger-bridge generates the output tree.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CORE_GUID = "58D0FB3206B6F859"
GUID_REF_RE = re.compile(r'\{([0-9A-F]{16})\}')
PLAYER_COUNT_RE = re.compile(r'm_iPlayerCount\s+(\d+)')
GAME_MODE_RE = re.compile(r'm_sGameMode\s+"(\w+)"')
LAYER_DECL_RE = re.compile(r'Layer\s+(\w+)\s*\{')


@dataclass
class ValidationError:
    """A single validation failure with remediation hint."""
    file: str
    rule: str
    issue: str
    suggested_fix: str = ""
    severity: str = "error"  # 'error' | 'warning'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.file} — Rule {self.rule}: {self.issue}"


@dataclass
class ValidationReport:
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    checked_files: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    @property
    def passed_all(self) -> bool:
        return len(self.errors) == 0 and len(self.warnings) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "checked_files": self.checked_files,
            "errors": [str(e) for e in self.errors],
            "warnings": [str(w) for w in self.warnings],
        }


def validate_mission_tree(
    output_dir: Path,
    catalog_index: dict,
    mission_mint_log: list[str] | None = None,
) -> ValidationReport:
    """Run all validation rules against the generated mission tree.

    Args:
        output_dir: path to missions/{id}/output/
        catalog_index: loaded INDEX.json
        mission_mint_log: list of locally-minted GUIDs for this mission

    Returns:
        ValidationReport with errors and warnings.
    """
    report = ValidationReport()
    known_guids: set[str] = set(catalog_index.get("guid_to_type", {}).keys())
    known_guids.add(CORE_GUID)
    if mission_mint_log:
        known_guids.update(mission_mint_log)

    # ---- Rule 1: addon.gproj exists and has core dependency ----------------
    gproj = output_dir / "addon.gproj"
    if not gproj.exists():
        report.errors.append(ValidationError(
            "addon.gproj", "1",
            "File missing — addon.gproj is required",
            "Run reforger-bridge to regenerate"
        ))
    else:
        report.checked_files.append(str(gproj))
        content = gproj.read_text()
        if CORE_GUID not in content:
            report.errors.append(ValidationError(
                "addon.gproj", "1",
                f"Missing core dependency {CORE_GUID}",
                f'Add "{CORE_GUID}" to Dependencies block'
            ))

    # ---- Rule 2: Missions/ directory structure -----------------------------
    missions_dir = output_dir / "Missions"
    worlds_dir = output_dir / "Worlds"
    if not missions_dir.exists():
        report.errors.append(ValidationError("output/Missions/", "2", "Missions/ directory missing", "Create via reforger-bridge"))
    if not worlds_dir.exists():
        report.errors.append(ValidationError("output/Worlds/", "2", "Worlds/ directory missing", "Create via reforger-bridge"))

    # ---- Rule 3: .conf file exists with required fields -------------------
    conf_files = list(missions_dir.glob("*.conf")) if missions_dir.exists() else []
    if not conf_files:
        report.errors.append(ValidationError("Missions/*.conf", "3", "No .conf mission header file", "reforger-bridge: generate_mission_header()"))
    else:
        for conf in conf_files:
            report.checked_files.append(str(conf))
            content = conf.read_text()
            for required_field in ["SCR_MissionHeader", "World", "m_sName", "m_sGameMode", "m_iPlayerCount"]:
                if required_field not in content:
                    report.errors.append(ValidationError(
                        conf.name, "3",
                        f"Required field '{required_field}' missing",
                        f"Add {required_field} to SCR_MissionHeader block"
                    ))
            # Rule 6: player count sanity for multiplayer mode
            # Solo (1 player) is valid in coop mode (Arma Reforger supports single-player coop).
            # Emit WARNING for count=1 (playable but unusual); ERROR only for count<1.
            gm_match = GAME_MODE_RE.search(content)
            pc_match = PLAYER_COUNT_RE.search(content)
            if gm_match and gm_match.group(1) in ("Coop", "Conflict", "Multiplayer"):
                if pc_match:
                    pc = int(pc_match.group(1))
                    if pc < 1:
                        report.errors.append(ValidationError(
                            conf.name, "6",
                            f"player_count={pc} is invalid (must be >= 1)",
                            "Set m_iPlayerCount to at least 1"
                        ))
                    elif pc == 1:
                        report.warnings.append(ValidationError(
                            conf.name, "6",
                            "player_count=1 in coop mode — solo play is supported but unusual",
                            "Increase m_iPlayerCount if this is intended as a multiplayer mission",
                            severity="warning"
                        ))

    # ---- Rule 4: .conf.meta exists ----------------------------------------
    if missions_dir.exists():
        for conf in missions_dir.glob("*.conf"):
            meta = conf.with_suffix(".conf.meta")
            if not meta.exists():
                report.warnings.append(ValidationError(
                    conf.name, "4",
                    ".conf.meta sidecar missing",
                    "generate_conf_meta() from exporters/conf.py",
                    severity="warning"
                ))

    # ---- Rule 5: All GUID refs resolve against catalog or mint log ---------
    for check_dir in [missions_dir, worlds_dir]:
        if not check_dir or not check_dir.exists():
            continue
        for f in check_dir.iterdir():
            if not f.is_file() or f.suffix not in (".conf", ".ent", ".layer"):
                continue
            report.checked_files.append(str(f))
            content = f.read_text(errors="replace")
            own_guids = set(GUID_REF_RE.findall(_extract_meta_name_line(content)))
            for m in GUID_REF_RE.finditer(content):
                guid = m.group(1)
                if guid not in known_guids and guid not in own_guids:
                    report.errors.append(ValidationError(
                        f.name, "5",
                        f"Hallucinated/unknown GUID: {guid}",
                        "Replace with verified GUID from catalog/ or use minted mission GUID"
                    ))

    # ---- Rule 7: .ent file exists -----------------------------------------
    ent_files = list(worlds_dir.glob("*.ent")) if worlds_dir.exists() else []
    if not ent_files:
        report.errors.append(ValidationError("Worlds/*.ent", "7", "No .ent world file", "reforger-bridge: generate_world_subscene()"))

    # ---- Rule 8: At least one .layer file exists --------------------------
    if worlds_dir and worlds_dir.exists():
        layer_files = list(worlds_dir.glob("*.layer"))
        if not layer_files:
            report.errors.append(ValidationError("Worlds/*.layer", "8", "No .layer files", "reforger-bridge must generate at least gamemode + spawnpoints layers"))
        else:
            report.checked_files.extend(str(f) for f in layer_files)

    # ---- Rule 9: Disclosure in .conf description --------------------------
    for conf in conf_files:
        content = conf.read_text()
        if "AI" not in content and "assisted" not in content.lower() and "LLM" not in content.upper():
            report.warnings.append(ValidationError(
                conf.name, "9",
                "No AI disclosure in description field",
                "generate_mission_header() auto-inserts disclosure — check if it was stripped",
                severity="warning"
            ))

    # ---- Rule 10: .ent.meta exists ----------------------------------------
    if worlds_dir and worlds_dir.exists():
        for ent in worlds_dir.glob("*.ent"):
            meta = ent.with_suffix(".ent.meta")
            if not meta.exists():
                report.warnings.append(ValidationError(
                    ent.name, "10",
                    ".ent.meta sidecar missing",
                    "generate_ent_meta() from exporters/conf.py",
                    severity="warning"
                ))

    # ---- Rule 11: Layer files referenced in .ent --------------------------
    if ent_files and worlds_dir and worlds_dir.exists():
        ent_content = ent_files[0].read_text()
        if "Layer " in ent_content:
            declared = set(LAYER_DECL_RE.findall(ent_content))
            actual_layer_stems = {f.stem for f in worlds_dir.glob("*.layer")}
            # world_stem_name_layer
            undeclared = actual_layer_stems - declared
            for orphan in undeclared:
                report.warnings.append(ValidationError(
                    f"{orphan}.layer", "11",
                    "Layer file exists but not declared in .ent",
                    f"Add 'Layer {orphan} {{ Index N }}' to {ent_files[0].name}",
                    severity="warning"
                ))

    # ---- Rule 12: No embedded asset files (.edds, .pak, etc.) ------------
    if output_dir.exists():
        for f in output_dir.rglob("*"):
            if f.suffix in (".edds", ".pak", ".pbo"):
                report.errors.append(ValidationError(
                    str(f.relative_to(output_dir)), "12",
                    "Embedded asset file found — EULA violation",
                    "Remove asset files. Only GUID references allowed."
                ))

    return report


def _extract_meta_name_line(content: str) -> str:
    """Extract the Name field line to get the file's own GUID."""
    m = re.search(r'Name\s+"(\{[0-9A-F]{16}\}[^"]+)"', content)
    return m.group(1) if m else ""
