# Validation Rules — Mission File Format

> **Quelle:** `research/02-mission-format.md` Validation-Rules-Section
> **Implementiert in:** `backend/validators/schema.py` + `backend/validators/cross_file.py`
> **Stand:** 2026-05-20

---

## Übersicht

12 Validation-Rules werden bei jeder generierten Mission automatisch geprüft:

| Rule | Datei | Was wird geprüft | Severity |
|------|-------|------------------|----------|
| 1 | addon.gproj | Core Dependency 58D0FB3206B6F859 vorhanden | ERROR |
| 2 | output/ | Missions/ und Worlds/ Verzeichnisse existieren | ERROR |
| 3 | *.conf | SCR_MissionHeader mit Pflichtfeldern vorhanden | ERROR |
| 4 | *.conf.meta | .meta-Sidecar existiert | WARNING |
| 5 | *.conf/.ent/.layer | Alle GUID-Refs auflösbar in Catalog oder Mint-Log | ERROR |
| 6 | *.conf | m_iPlayerCount ≥ 2 für Coop/Conflict | ERROR |
| 7 | Worlds/ | .ent-World-Datei existiert | ERROR |
| 8 | Worlds/ | Mindestens eine .layer-Datei vorhanden | ERROR |
| 9 | *.conf | AI-Disclosure in m_sDescription | WARNING |
| 10 | *.ent.meta | .ent.meta-Sidecar existiert | WARNING |
| 11 | *.ent | Layer-Files in .ent deklariert (wenn Layer-Table-Pattern) | WARNING |
| 12 | output/ | Keine eingebetteten Assets (.edds, .pak, .pbo) | ERROR |

**Cross-File Rules:**

| Rule | Files | Was wird geprüft | Severity |
|------|-------|------------------|----------|
| cross-1 | asset-manifest.json | halt_required=false (keine ungelösten Pflicht-Assets) | ERROR/WARN |
| cross-2 | encounters.json / *.layer | GUID-Refs aus encounters.json in Layer-Files vorhanden | WARNING |
| cross-3 | narrative.json / asset-manifest.json | Factions-asset_id_refs resolved | WARNING |

---

## Regel-Details

### Rule 1: Core Dependency

**Datei:** `addon.gproj`

```
GameProject {
  Dependencies {
    "58D0FB3206B6F859"    ← MUSS vorhanden sein
  }
}
```

**Fix:** `generate_gproj()` injiziert immer automatisch.

---

### Rule 3: Mission Header Pflichtfelder

**Datei:** `Missions/*.conf`

Pflichtfelder: `SCR_MissionHeader`, `World`, `m_sName`, `m_sGameMode`, `m_iPlayerCount`

```
SCR_MissionHeader {
  World "{GUID}Worlds/Mission.ent"    ← GUID muss im Mint-Log sein
  m_sName "Night Recon Everon"
  m_sGameMode "Coop"
  m_iPlayerCount 4
}
```

---

### Rule 5: GUID-Halluzinations-Check

**Datei:** Alle `.conf`, `.ent`, `.layer` Files

Jede `{ABCDEF1234567890}path.et` Referenz wird gegen:
1. `catalog/INDEX.json` `guid_to_type` Map geprüft
2. `missions/{id}/mint-log.json` (neu gemintete Mission-GUIDs) geprüft

→ Wenn nicht gefunden: **ERROR** (Halluzination)

**Ausnahmen:**
- Engine Built-In Klassen (keine Prefab-GUID, kein `{GUID}path` Format)
- File's eigene GUID in `Name "{GUID}..."` Zeile

---

### Rule 9: AI-Disclosure

**Datei:** `Missions/*.conf`

Mindestens einer dieser Strings muss in `m_sDescription` vorkommen:
- "AI" (case-sensitive)
- "assisted" (case-insensitive)
- "LLM"

**Fix:** `generate_mission_header()` injiziert automatisch.

---

### Rule 12: Kein Asset-Embedding

**Datei:** Gesamte `output/` Hierarchie

Verbotene Datei-Extensions: `.edds`, `.pak`, `.pbo`

Wenn gefunden: **ERROR** (EULA-Verletzung, Mission wird sofort geblockt)

---

## Integration

```python
from backend.validators.schema import validate_mission_tree, ValidationReport
from backend.validators.cross_file import validate_cross_file_consistency
import json
from pathlib import Path

output_dir = Path("missions/my-mission/output")
catalog = json.loads(Path("catalog/INDEX.json").read_text())
mint_log = json.loads(Path("missions/my-mission/mint-log.json").read_text())

# Schema validation (Rules 1-12)
schema_report = validate_mission_tree(output_dir, catalog, mission_mint_log=mint_log)
print("Schema:", "PASS" if schema_report.passed else f"FAIL ({len(schema_report.errors)} errors)")

# Cross-file validation (Rules cross-1 bis cross-3)
cross_report = validate_cross_file_consistency(
    Path("missions/my-mission"),
    output_dir
)
print("Cross-file:", "PASS" if cross_report.passed else f"FAIL ({len(cross_report.errors)} errors)")
```
