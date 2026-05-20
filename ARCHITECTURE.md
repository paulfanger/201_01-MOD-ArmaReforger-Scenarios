# Architecture — Arma Reforger AI-Native Mission Authoring System

> **Stand:** 2026-05-20, post-Research (Phase 2 Synthesis).
> **Quelle:** `research/00-synthesis.md` konsolidiert `research/01-workbench-sdk.md`, `research/02-mission-format.md`, `research/03-eula-legal.md`.
> Diese Datei ist die aktuelle Architektur-Wahrheit. Original-Vision in `arma-reforger-coop-setup-prompt.md`, alle Änderungen in `DECISIONS.md`.

---

## 1. System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      User (Paul, Creative Director, Non-Coder)            │
│                              ↓ /new-mission, /approve, /revise            │
├──────────────────────────────────────────────────────────────────────────┤
│                        Claude Code (Subagent-Orchestration)               │
│                                                                           │
│   mission-director ──┬─→ narrative-designer ──→ narrative.json            │
│   (orchestrator)     │                                                     │
│                       ├─→ asset-curator ────→ asset-manifest.json         │
│                       │       ↓ validates against catalog/                 │
│                       │                                                     │
│                       ├─→ encounter-designer ──┐                          │
│                       ├─→ flow-architect ─────┤→ encounters.json          │
│                       │                                                     │
│                       └─→ reforger-bridge ────→ output/*.{gproj,conf,..}  │
│                                ↑                                            │
│                                │ uses                                       │
│                                └── backend/exporters/ (Brace-Formatter)    │
│                                                                             │
│                       Testing-Loop (autonomous):                            │
│                       pipeline-tester → mission-validator → wb-integration │
│                              ↓ fail                                         │
│                              bug-fixer (auto, max 5 iter)                  │
│                              ↓ pass                                         │
│                              readiness-reporter → User                      │
├──────────────────────────────────────────────────────────────────────────┤
│                  Backend (FastAPI, Pure Logic, no LLM)                    │
│                                                                            │
│   catalog/ (GUID-DB) + validators/ + exporters/ + snapshots/              │
├──────────────────────────────────────────────────────────────────────────┤
│            Output: missions/{id}/output/ (unpacked addon-tree)             │
│                            ↓                                                │
│   [Phase 1 MVP]    User kopiert manuell → Win-Workbench → Workshop        │
│   [Phase 2]        Workbench-Plugin liest Spec, ruft WorldEditorAPI       │
│   [Stretch Goal]   Linux-Dedi-Server: -addonsDir + -mission direct-load   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 8-Stage Pipeline (post-Research)

> Stages **MVP**-aktiv, **DEFER**-Phase-2/3, **OUT-OF-SCOPE** = nicht im MVP-Roadmap.

### Stage 1: Narrative Extraction — **MVP**

- **Input:** User-Briefing (Freitext, 2-5 Sätze)
- **Specialist:** `narrative-designer`
- **Output:** `missions/{id}/narrative.json` (semantisches Modell)
- **Approval-Gate:** User sieht title, factions, biome, tone, pacing; entscheidet `/approve` oder `/revise <feedback>`
- **MVP-Anpassung:** `faction-doctrine`, `weather-time`, `terrain-reader` Domain-Agents in narrative-designer gemerged (Konsolidierung aus Synthesis Change #1)

### Stage 2: Asset Constraints — **MVP**

- **Input:** narrative.json
- **Specialist:** `asset-curator`
- **Output:** `missions/{id}/asset-manifest.json` (GUID-aufgelöste Asset-Refs)
- **Pflicht-Gate:** Halluzinations-Check, jeder asset-ref muss in `catalog/` GUID haben (Synthesis Change #2)
- **Failure-Action:** HALT, User-Briefing mit konkretem Ersatz-Vorschlag aus catalog

### Stage 3: Spatial Location Proposals — **DEFER Phase 2**

- Braucht Workbench-Viewport-Access (`WorldEditorAPI` von im-Plugin)
- Vermerk in Roadmap, im MVP übersprungen

### Stage 4: Moodboard Understanding — **DEFER Phase 2**

- Reines Vision-API, unabhängig von Reforger-SDK
- Vermerk in Roadmap

### Stage 5: Iterative Approval Pipeline — **MVP**

- **Implementation:** mission-director + version-keeper
- **Verhalten:** `/approve` triggert Snapshot UND Stage-Advance. `/revise` triggert Stage-Specialist erneut.
- **Snapshot-Storage:** `missions/{id}/snapshots/00X_label.json` mit inline content (siehe `version-keeper.md`)

### Stage 6: Mission Flow Mapping — **MVP**

- **Input:** narrative.json + asset-manifest.json
- **Specialists:** `encounter-designer` (Patrols, Spawnwaves, AI-States) + `flow-architect` (Triggers, State-Machines, Pacing)
- **Output:** `missions/{id}/encounters.json`
- **Sub-Stage 6b — File Generation:** `reforger-bridge` generiert vollständiges Addon-Tree in `missions/{id}/output/`

### Stage 7: Runtime AI Director — **OUT-OF-SCOPE**

- Runtime-LLM-Calls sind EULA-YELLOW + MANW-disqualifiziert
- Bleibt komplette long-term Vision, kein MVP

### Stage 8: Testing / Refinement — **DEFER Phase 4**

- Telemetry braucht laufende Sessions auf Win/Console
- Im MVP ersetzt durch automatische Pipeline-Tester (siehe Section 7)

---

## 3. Subagent Hierarchy (MVP)

```
mission-director (orchestrator, ALWAYS first)
├── narrative-designer    (Stage 1, mergt: faction-doctrine, weather-time, terrain-reader)
├── asset-curator         (Stage 2, Pflicht-Gate, GUID-Validation)
├── encounter-designer    (Stage 6a, mergt: cinematic-composer für MVP)
├── flow-architect        (Stage 6b)
├── reforger-bridge       (Stage 6c — File-Generation via backend/exporters/)
└── version-keeper        (auto bei /approve)

Testing-Pipeline (auto-triggered, separat von Stage-Pipeline):
├── pipeline-tester
├── mission-validator
├── workbench-integration-tester
├── bug-fixer (autonom, max 5 iter)
└── readiness-reporter (einziger User-Facing Tester)

Research-Agents (historisch, in .claude/agents/research/, archive nach Phase 2)
```

**Konsolidierung-Begründung** (aus Synthesis): MVP-Specialists = 7 (Mission-Director + 6) statt original 13. Re-Split bei Phase 2 wenn Token-Budget oder Klarheit es erfordert.

---

## 4. Data Models

### narrative.json (Stage 1 Output)

Siehe Beispiel in `.claude/agents/specialists/narrative-designer.md`. Kernfelder:
- `title`, `tagline`, `premise`
- `factions { player, ai }` mit asset_id_ref (zu resolven gegen catalog)
- `biome { map_id_ref, region_hint }`
- `tone { primary, secondary[], color_palette_hint[] }`
- `pacing { phase_1..N }`
- `time_of_day`, `weather`, `player_setup`
- `narrative_anchors[]`, `out_of_scope[]`

### asset-manifest.json (Stage 2 Output)

```json
{
  "resolved_assets": [
    {
      "narrative_ref": "ENF_Faction_US",
      "guid": "{GUID-FROM-CATALOG}",
      "path": "Configs/Factions/...",
      "type": "faction",
      "source_dependency": "ArmaReforger_core"
    }
  ],
  "missing_assets": [],
  "halt_required": false
}
```

### encounters.json (Stage 6 Output)

```json
{
  "spawn_points": [{ "team": "US", "coords": [x,y,z], "loadout_ref": "..." }],
  "ai_groups": [
    {
      "name": "USSR_Patrol_North",
      "prefab_guid": "{...}",
      "coords": [x,y,z],
      "waypoint_refs": ["WP_North_1", "WP_North_2"],
      "behavior_mode": "patrol"
    }
  ],
  "waypoints": [
    { "name": "WP_North_1", "type": "move", "coords": [x,y,z] }
  ],
  "tasks": [
    {
      "name": "Eliminate_HVT",
      "class": "SCR_EliminateTask",
      "coords": [x,y,z],
      "fields": { "m_sName": "Eliminate UAZ", "m_sDescription": "..." }
    }
  ],
  "triggers": [
    {
      "class": "SCR_BaseTriggerEntity",
      "name": "ZoneAlpha",
      "coords": [x,y,z],
      "radius": 50,
      "spawner_components": [
        {
          "class": "SCR_AISpawnerComponent",
          "default_prefab_guid": "{...}",
          "spawn_pos": [x,y,z]
        }
      ]
    }
  ],
  "managers": ["GameMode", "FactionManager", "LoadoutManager", "TimeAndWeather"],
  "environment_overrides": {
    "time_of_day": { "hour": 2, "minute": 30 },
    "weather_preset": "clear_cold"
  }
}
```

### Mission-Output-Tree (Stage 6c)

```
missions/{id}/output/
├── addon.gproj
├── Missions/{id}.conf
├── Missions/{id}.conf.meta
└── Worlds/
    ├── {id}.ent
    ├── {id}.ent.meta
    ├── {id}_gamemode.layer
    ├── {id}_managers.layer
    ├── {id}_spawnpoints.layer
    ├── {id}_AI.layer
    ├── {id}_tasks.layer
    ├── {id}_triggers.layer
    └── {id}_environment.layer
```

(Vollständiges JSON-Schema in `research/02-mission-format.md`.)

### catalog/*.json (Asset-Catalog Schema)

```json
{
  "guid": "904EC091C347AEA9",
  "type": "prefab|faction|loadout|map|vehicle|weapon",
  "displayName": "CoopGameMode",
  "path": "Prefabs/MP/Modes/Coop/CoopGameMode.et",
  "source_dependency": "ArmaReforger_core",
  "source_repo": "https://github.com/...",
  "verified_at": "2026-05-20",
  "verified_by": "manual|catalog-bootstrap"
}
```

---

## 5. Reforger Integration Strategy

### Phase 1 (MVP): External-Only File-Pipeline

- Backend schreibt vollständige addon-Tree als Brace-Syntax-Text
- Output ist unpacked (kein .pak), kann von Workbench geladen werden
- Pack-Step: `output/` → `output.zip` für Transfer
- User-Workflow:
  1. `/new-mission night-recon-everon` → System generiert Tree
  2. Self-Testing-Loop läuft
  3. User kopiert `output/` auf Win-PC
  4. Workbench → Open Workspace → Tree → Mission spielbar

### Phase 2: Hybrid B (Plugin)

- Workbench-Plugin (`AI_GeneratePlugin.c`, ~200 LOC Enforce Script)
- Backend schreibt **Spec-JSON** in shared file (z.B. `$profile:ai-spec.json`)
- Plugin liest Spec, ruft `WorldEditorAPI.CreateEntity()`, `worldEditor.Save()`
- Headless-Mode: `ArmaReforgerWorkbenchSteamDiag.exe -plugin=AI_GeneratePlugin -spec=path.json -buildData HEADLESS -exitAfterInit`
- Aktivierung: erst wenn Win-Zugang verfügbar (siehe ROADMAP)

### Phase 3: Native C — **DROPPED**

- Nicht realistisch in 2026 (research/01-workbench-sdk.md Section "C")
- Plan-Update: Wird nicht weiter verfolgt. Phase 2 ist End-Game.

### Stretch Goal: Linux-DediServer-Direct-Load

- Open Question 1 aus `02-mission-format.md`
- Wenn empirisch verifiziert: User kann lokal/remote auf Linux-Dedi testen ohne Win-Box
- Test-Plan: `reforger-dedi -addonsDir <path-to-output> -mission "{GUID}Missions/{id}.conf"`
- Wenn klappt: 90% mac-friendly workflow

---

## 6. Asset Validation Strategy

### Catalog Bootstrap (Sonnet 4.6 Phase 1 Task)

- Clone diese Repos lokal in `/tmp/`:
  - `BohemiaInteractive/Arma-Reforger-Samples`
  - `exocs/Reforger-Sample-Coop`
  - `Kexanone/CombatOpsEnhanced_AR`
  - `gruppe-adler/GRAD-COOP-Template-Reforger`
- Parser extrahiert alle `{GUID}<path>.et`-Pattern + Class-Name + Source-Repo
- Schreibe nach `catalog/{type}/{guid}.json` plus `catalog/INDEX.json`

### Validation in asset-curator

```python
# Pseudo
for ref in narrative.asset_id_refs + encounters.prefab_guids:
    if ref.guid not in catalog:
        manifest.missing_assets.append(ref)
if manifest.missing_assets:
    halt(reason="hallucinated_asset_ref", details=missing)
    # mission-director ruft User-Briefing
```

### Sync-Updates

- `/sync-catalog` Command — re-scant configured repos + optional lokaler Reforger-Install (wenn vorhanden)
- Inkrementell — neue GUIDs hinzufügen, existierende mit verified_at-Update

---

## 7. Self-Testing Pipeline

```
[Sonnet 4.6 schreibt Code]
        ↓
[pipeline-tester]  → fail → [bug-fixer] → re-run (max 5)
        ↓ pass
[mission-validator] → fail → [bug-fixer] → re-run (max 5)
        ↓ pass
[workbench-integration-tester]
        ↓
   Mode A: Linux-Dedi verfügbar → empirischer Test
   Mode B: nicht verfügbar       → MANUAL_VERIFICATION_REQUIRED.md
        ↓ pass / pending_manual
[readiness-reporter]
        ↓
   USER MANUAL TESTING
```

Spezifikationen unter `.claude/agents/testing/*.md`.

---

## 8. Multimodal Pipeline (Stage 4, Phase 2)

Deferred zu Phase 2. Wenn aktiv:
- Bild-Upload → `moodboard-analyst` (Claude Vision)
- Output: mood-tags, color-palette, density-score
- Wird in `encounter-designer` als Constraint reingegeben

---

## 9. Runtime AI Director (Stage 7) — DROPPED FOR MVP

Out-of-Scope wegen EULA-Risk + MANW-Disqualifikation.

---

## 10. Telemetry (Stage 8) — DEFER

Lokale SQLite-DB, später. `playtest-analyst` Subagent reviewed Sessions.

---

## 11. Technology Choices (post-Research)

- **Backend:** Python 3.13+, FastAPI, Pydantic, jsonschema, anthropic SDK
- **Frontend Workbench Plugin (Phase 2):** Enforce Script (.c), Plugin-Manifest via `[WorkbenchPluginAttribute]`
- **Storage:** SQLite (lokal, snapshots), JSON-Files (versionsiert via git)
- **Vision (Phase 2):** Claude Sonnet/Opus mit Vision
- **Voice (Out-of-Scope):** Whisper.cpp + ElevenLabs
- **Test-Plattform MVP:** Linux Dedicated Server (wenn verifiziert) ODER Windows-VM (manueller Fallback)
- **Lizenz:** APL-ND für Mission-Outputs

---

## 12. Out of Scope (final)

- Multiplayer-Sync der AI-Director-Entscheidungen
- PVP-Modi
- Native-C Workbench-UI (technisch nicht möglich 2026)
- Standalone-Spiele-Engine-Migration (nur Reforger)
- Mobile/Web-Frontend
- Runtime-LLM-Calls in Mission-Files
- Automatischer Workshop-Upload (Workbench-only)
- Asset-Embedding (EULA verboten)
- LLM-Training auf Reforger-Assets (EULA verboten)

---

## 13. Decision Reference

Alle Architektur-affecting Decisions sind in `DECISIONS.md` mit Source-Verweis auf `research/*.md` dokumentiert. Vor jeder architecture-relevanten Änderung: neuer DECISIONS-Eintrag PFLICHT.
