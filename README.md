# Arma Reforger AI-Native Mission Authoring System

> Status: **In Setup** — Phase 2 Research läuft. Trigger für Build via `EXECUTION_PROMPT_FOR_SONNET_4_6.md`.

## Was ist das?

Ein AI-natives kreatives Co-Creation-System für **cinematic, emergent, narrativ-dichte PVE/Koop-Missionen** in Arma Reforger. Es ist KEIN Mission-Generator. Es ist eine Partnerschaft zwischen einem Non-Coder Creative Director und einer hierarchischen AI-Subagent-Pipeline.

## Quick Start

1. **Foundation lesen:** `arma-reforger-coop-setup-prompt.md` (Original-Vision)
2. **Decisions verstehen:** `DECISIONS.md`
3. **Architecture-Stand:** `ARCHITECTURE.md` (wird nach Research finalisiert)
4. **Roadmap:** `ROADMAP.md`
5. **Sonnet-4.6-Trigger:** `EXECUTION_PROMPT_FOR_SONNET_4_6.md`

## Pipeline-Übersicht

```
User-Idee → mission-director
            ↓
            Stage 1: narrative-designer
            Stage 2: asset-curator
            Stage 6: encounter-designer + flow-architect → reforger-bridge
            ↓
            Self-Testing-Loop:
            pipeline-tester → mission-validator → workbench-integration-tester
            ↓
            bug-fixer (autonom, max 5 Iter)
            ↓
            readiness-reporter → User
```

## Stages im MVP

✅ Stage 1: Narrative Extraction  
✅ Stage 2: Asset Validation  
✅ Stage 5: Approval-Gates  
✅ Stage 6: Mission Flow Mapping → File Generation  
❌ Stage 3 (Spatial), 4 (Moodboard), 7 (Runtime AI Director), 8 (Telemetry) — spätere Phasen

## Slash Commands

- `/new-mission <name>` — Mission starten
- `/stage [n]` — Status oder Stage-Wechsel
- `/approve` — Stage approven + Snapshot
- `/revise <feedback>` — Stage iterieren
- `/snapshot <label>` — manueller Snapshot
- `/rollback <id>` — zurück zu Snapshot
- `/export` — Mission als Reforger-Files exportieren
- `/run-tests` — Self-Testing-Pipeline manuell triggern
- `/check-readiness` — Status-Check ohne Re-Run
- `/dashboard` — Projekt-Übersicht

## Architektur-Constraints

- ❌ KEINE Asset-Halluzinationen (catalog/ ist Pflicht-Gate)
- ❌ KEINE Stages ohne User-Approval überspringen
- ❌ KEINE Mission-Files ohne Snapshot
- ✅ Versionierung Pflicht
- ✅ User ist Non-Coder — alles in einfacher Sprache

## Status der Umgebung

- **OS:** macOS M1 (Workbench nicht lokal verfügbar)
- **MVP-Mode:** External File-Pipeline only (Workbench-Integration in späterer Phase)
- **Backend:** FastAPI/Python 3.13 (siehe `backend/`)
- **LLM:** Claude (Anthropic), Provider-Abstraction für späteren Swap

## Project Structure

```
arma-reforger-coop/
├── arma-reforger-coop-setup-prompt.md    Original-Foundation
├── ARCHITECTURE.md                       Refined Architecture (post-research)
├── DECISIONS.md                          All architectural decisions chronologisch
├── ROADMAP.md                            MVP → Mid → Long
├── WORK_LOG.md                           What was built, when
├── CLAUDE.md                             Briefing für Claude Code
├── EXECUTION_PROMPT_FOR_SONNET_4_6.md    Sonnet-Trigger (das hier ist der wichtige!)
├── .claude/
│   ├── agents/
│   │   ├── research/        Phase-2-Research-Specs (historisch)
│   │   ├── testing/         Permanent Self-Testing Agents
│   │   └── specialists/     Stage-Specialist Agents
│   └── commands/            Slash Commands
├── backend/                 Pure-Logic FastAPI
├── catalog/                 Validated Asset-Catalog
├── missions/                Generated Missions
├── research/                Research-Output (von Phase 2)
└── playbook/                Operating-Procedures
```

## Was ist gerade los?

Schau `WORK_LOG.md` für recent activity. Wenn Self-Testing läuft, schau `missions/{id}/test-report.json`.
