# Roadmap

> **Stand:** 2026-05-20, post-Research.
> Jede Phase hat klare Definition-of-Done. Phasen werden NICHT übersprungen.

---

## Phase 0 — Foundation (COMPLETE 2026-05-20)

✅ Pre-Flight, Original-Setup-Prompt persistiert
✅ Foundation-Decisions in DECISIONS.md
✅ Verzeichnis-Struktur angelegt
✅ Deep Research (3 parallele Agents)
✅ Synthesis + ARCHITECTURE.md
✅ Testing-Agent-Specs (5 Agents)
✅ Slash-Command-Specs (10 Commands)
✅ Backend-Skeleton + .gitignore + README
✅ EXECUTION_PROMPT_FOR_SONNET_4_6.md

---

## Phase 1 — MVP Implementation (COMPLETE 2026-05-20)

**Ausgeführt:** Claude Sonnet 4.6 (autonomer Run via EXECUTION_PROMPT_FOR_SONNET_4_6.md)

### Deliverables

- ✅ Asset-Catalog bootstrapped: **1326 GUIDs** aus 4 OSS-Repos (26× Minimum)
- ✅ Backend-Module komplett: `exporters/` (braces/gproj/conf/ent/layer/mint), `validators/`, `catalog/`, `snapshots/`
- ✅ Stage-Specialists: alle 7 MVP-Agents implementiert (mission-director, version-keeper, narrative-designer, asset-curator, encounter-designer, flow-architect, reforger-bridge)
- ✅ Self-Testing-Loop: `test-mission-pipeline-check` läuft end-to-end, 51 Unit-Tests pass
- ✅ `READY_FOR_MANUAL_TESTING.md` generiert
- ✅ `MANUAL_VERIFICATION_REQUIRED.md` generiert (Linux-Dedi nicht verfügbar → Mode B)
- ✅ `LICENSE.md` (APL-ND + MIT) + `playbook/EULA_COMPLIANCE.md`
- ✅ `workbench-plugin/AI_GeneratePlugin.c` (Phase-2-Skeleton)
- ⏳ night-recon-everon: wartet auf User-Approval für Pipeline-Start (Sacred Approval Gate)
- ⏳ Linux-Dedi-Empirie-Test: deferred (kein Docker/Dedi verfügbar) → `OPEN_QUESTION_1_DEFERRED.md`

### Definition of Done — Status

1. ✅ `/new-mission test-mission-pipeline-check` läuft End-to-End ohne Errors
2. ✅ Output 13 Files: gproj, conf, conf.meta, ent, ent.meta, 7 layers, DISCLOSURE.md
3. ✅ mission-validator: 0 hallucinations, 0 schema errors, 0 cross-file inconsistencies
4. ✅ `MANUAL_VERIFICATION_REQUIRED.md` mit Windows-Tester-Steps
5. ✅ `READY_FOR_MANUAL_TESTING.md` von readiness-reporter
6. ✅ 4 Snapshots pro Approval-Gate
7. ✅ WORK_LOG.md komplett für Phase 1–7
8. ⏳ Git-Commit pending User-Approval

---

## Phase 2 — Hybrid B Plugin + Spatial/Moodboard (Win-Zugang erforderlich, 4-8 Wochen)

**Trigger:** User bestätigt Win-Zugang (eigener PC, VM, oder dedizierter Tester-Account).

### Deliverables

- [ ] `workbench-plugin/AI_GeneratePlugin.c` (~200 LOC Enforce Script) implementiert
  - liest `$profile:ai-spec.json`
  - ruft `WorldEditorAPI.CreateEntity()`, `worldEditor.Save()`
  - error reporting via `Print()` + file-log
- [ ] Plugin-Manifest mit `[WorkbenchPluginAttribute]`
- [ ] Headless-CLI-Trigger funktioniert: `WorkbenchSteamDiag.exe -plugin=AI_GeneratePlugin -spec=path.json -exitAfterInit`
- [ ] `workbench-integration-tester` Mode-A nutzt Plugin statt Mode-B-Manual
- [ ] Stage 3 (`spatial-scout`) aktiviert — nutzt Plugin für Viewport-Screenshots
- [ ] Stage 4 (`moodboard-analyst`) aktiviert — Claude Vision-Calls
- [ ] Iteration-Loop User → Spec → Plugin → Mission < 30s

### Definition of Done

1. End-to-End-Loop: User schreibt Briefing → Plugin generiert Mission im Workbench → User sieht Result < 60s
2. Stage 3 generiert mind. 3 Location-Proposals mit Screenshots
3. Stage 4 nimmt Moodboard-Image, extrahiert Tags die in Stage 6 reingehen
4. Bekannter Bug-Pattern: alle 12 Validation-Rules aus `02-mission-format.md` haben Test-Coverage

---

## Phase 3 — Production-Ready + Workshop-Publish (8-16 Wochen)

### Deliverables

- [ ] Auto-Disclosure-Header in Workshop-Description-Generator
- [ ] `/publish` Command — bereitet Bundle vor (kein Auto-Upload, das bleibt User-Action)
- [ ] Multi-Mission-Library mit Browsing (`/library`)
- [ ] Mission-Remix-Feature: bestehende Mission als Vorlage neu erweitern
- [ ] Voice-Generator-Stub (deferred — nur Skeleton, kein aktives Whisper/ElevenLabs)
- [ ] Performance-Profiling: Pipeline-Run < 5min für Standard-Mission
- [ ] Erste 3 produzierte Missions im Reforger Workshop (mit APL-ND + Disclosure)

### Definition of Done

1. mind. 3 Mission live im Workshop
2. Kein Mission-Removal innerhalb 2 Wochen post-Upload
3. mind. 1 Reproduktions-Test durch dritte Person (Ody oder externer Tester)
4. Workflow-Doku in `playbook/` vollständig

---

## Phase 4 — Long-Term (6+ Monate out)

### Vision

- Stage 7 Runtime AI Director (single-player experiment, NICHT für Workshop)
- Stage 8 Telemetry + Playtest Analysis
- Voice-Layer (Whisper + ElevenLabs)
- Workshop-Browser-Integration mit Mission-Empfehlungen
- Cross-Mission-Narrative-Arcs (Mission-Series mit Persistenz)

### Nicht-Ziele (auch long-term)

- PVP
- Multiplayer-AI-Director-Sync
- Native Workbench-Chat-UI (technisch nicht möglich)
- Standalone-Spiele-Engine

---

## Risk-Watchlist (kontinuierlich)

| Risiko | Detection | Action |
|---|---|---|
| Bohemia ändert AI-Policy | News-Watch via Wiki + Blog | Workshop-Pause, lokale Distribution-Only |
| Reforger-Update bricht Schema | mission-validator regression | Re-Research, Architecture-Update |
| Catalog-Halluzination häuft sich | Multiple hallucinated-asset HALTs | Catalog-Re-Bootstrap, Sonnet-4.6-Brief |
| User-Workflow zu komplex | Mehrere abgebrochene Missions | Slash-Command-Vereinfachung, Tutorial-Mode |
| MANW-Deadline-Druck | Eigenes Ziel | Stage 7 strikt off, Submission-Compliance-Check |

---

## Next Steps für User

1. ✅ Phase 0 abgeschlossen
2. ✅ Phase 1 abgeschlossen (Sonnet 4.6 autonomer Run, 2026-05-20)
3. 🎯 **Git-Commit approven** — `/approve` für ersten Commit
4. 🎯 **Manuelle Test-Session** — `missions/test-mission-pipeline-check/READY_FOR_MANUAL_TESTING.md` lesen → Windows-Workbench-Test
5. 🎯 **Erste echte Mission** — `/new-mission night-recon-everon` starten (wartet auf dein /approve)
6. ⏳ Bei Windows-Zugang: Phase 2 triggern (Plugin-Activation)
