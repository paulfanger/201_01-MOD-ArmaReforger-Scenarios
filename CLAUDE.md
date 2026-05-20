# Arma Reforger AI-Native Mission Authoring System

## Project Identity

Standalone-Repo unter `/Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios/`. Teil der ELOS-Projekt-Familie. **KEIN** Monorepo (`control`-Pfad aus Original-Setup war Annahme, nicht Realität — siehe `DECISIONS.md`).

Ein AI-natives kreatives Co-Creation-System für cinematic, emergent, narrativ-dichte PVE/Koop-Missionen in Arma Reforger. KEIN Mission-Generator. Partnerschaft zwischen Non-Coder Creative Director (Paul) und hierarchischer AI-Subagent-Pipeline.

## Wie Claude Code sich hier verhält

### Session Start

1. Lies diese `CLAUDE.md`
2. Lies `ARCHITECTURE.md` für aktuellen Architecture-Stand
3. Lies `ROADMAP.md` für aktuelle Phase
4. Lies letzten 5 Einträge aus `WORK_LOG.md` für Recent Context
5. Wenn Mission aktiv: lies `missions/{active-id}/current-stage.json` + letzten Snapshot
6. Frag was wir heute arbeiten ODER schlage `/dashboard` vor

### Working Principles

- **User ist Non-Coder.** Erklärung VOR Aktion, in deutscher Sprache, ohne Jargon. NIEMALS davon ausgehen dass User Code editiert.
- **Plan-First für non-trivial Tasks.** Vor mehr als 5 Zeilen Code-Änderung oder neuer File-Anlage: 1-2 Sätze Begründung, dann handeln.
- **8-Stage-Pipeline ist NIEMALS autonom.** Approval-Gates sind heilig.
- **Asset-Halluzinationen sind verboten.** Jeder asset_id-Reference durch `asset-curator`.
- **Versionierung Pflicht.** Jeder `/approve` erzeugt Snapshot via `version-keeper`.
- **EULA-Konformität:** Offline-Authoring, APL-ND-Lizenz, Disclosure-Header (siehe `DECISIONS.md`).

### Subagent Invocation Pattern

Hierarchisch — Orchestrator → Stage-Specialist → Domain-Specialist → Utility-Agent. Niemals Stage-Specialists direkt zwischen sich (geht via mission-director).

**MVP-Specialists (jetzt aktiv):**
- `mission-director` — Orchestrator, ALWAYS first entry-point
- `narrative-designer` — Stage 1
- `asset-curator` — Stage 2 (Pflicht-Gate)
- `encounter-designer` — Stage 6 (Patrols, Spawnwaves)
- `flow-architect` — Stage 6 (Trigger-Graph, Pacing)
- `reforger-bridge` — Mission-File Export (Brace-Syntax)
- `version-keeper` — Snapshots (auto bei approve)

**Testing-Agents (permanent, auto-trigger):**
- `pipeline-tester` → `mission-validator` → `workbench-integration-tester` → `bug-fixer` → `readiness-reporter`

**Deferred (Phase 2+):**
- `spatial-scout` (Stage 3) — braucht Workbench-Viewport-Access
- `moodboard-analyst` (Stage 4) — Vision-Calls, später
- `ai-director-runtime` (Stage 7) — Long-term
- `playtest-analyst` (Stage 8) — Long-term
- `cinematic-composer`, `terrain-reader`, `faction-doctrine`, `weather-time` — werden im MVP in Stage-Specialists gemerged

### File Discipline

- Mission-State lebt in `missions/{id}/` — NIEMALS Mission-Daten anderswo schreiben
- Snapshots gehen in `missions/{id}/snapshots/` automatisch
- Asset-Catalog ist read-only während Mission-Building; nur via `/sync-catalog` updaten
- Generierte Output-Files in `missions/{id}/output/`
- Self-Testing-Reports in `missions/{id}/{test|validation|integration}-report.json`

### Backend

- Python FastAPI in `backend/` — pure logic, KEINE LLM-Calls hier
- Start dev: `cd backend && uvicorn main:app --reload --port 8765`
- LLM-Calls passieren in Claude Code Subagents, Backend bekommt nur structured Specs

### Workbench Integration (Status)

- **Phase 1 (aktuell):** External File-Pipeline. Backend schreibt Brace-Syntax-Files. User kopiert auf Win-Host für Workbench.
- **Phase 2 (geplant):** Hybrid B — kleines Workbench-Plugin (~150 LOC Enforce Script) konsumiert JSON-Spec. CLI-Headless-Build via `-plugin=AI_GeneratePlugin`.
- **Phase 3 (long-term):** Native C nicht realistisch in 2026 (keine HTTP-API in Enforce Script).

Siehe `research/01-workbench-sdk.md` für Details.

## Available Slash Commands

- `/dashboard` — Projekt-Status
- `/new-mission <name>` — neue Mission starten
- `/stage [n]` — Status / Stage-Wechsel
- `/approve` — Stage approven + Snapshot
- `/revise <feedback>` — Stage iterieren
- `/snapshot <label>` — manueller Snapshot
- `/rollback <id>` — zu Snapshot zurück
- `/export` — Mission als Reforger-Files exportieren
- `/run-tests` — Self-Testing-Pipeline manuell triggern
- `/check-readiness` — Status-Check ohne Re-Run

## EULA / Legal Status

Risiko-Level **GREEN** für offline-Authoring (siehe `research/03-eula-legal.md`):
- LLM läuft nur dev-time
- Output ist statisch Reforger-nativ
- APL-ND-Lizenz
- Disclosure-Header in Mission, README, Workshop-Description

**ROT-Bereich:** Runtime-LLM-Calls. Niemals in MVP.

## Communication Style

- Deutsch für User-Facing
- English für Code/Comments/Filenames
- Klar strukturiert, kein Wall-of-Text
- Bei größeren Steps: 1-2 Sätze Erklärung dann Aktion
- Bei Unsicherheit: fragen, nicht raten

## Anti-Patterns (heilig)

- ❌ Asset-IDs erfinden ohne Catalog-Validierung
- ❌ Stages ohne explizite User-Approval überspringen
- ❌ Mission-Files schreiben ohne Snapshot
- ❌ Subagent-Calls direkt zwischen Specialists ohne mission-director
- ❌ Workbench-Plugin-Code committen bevor wir Win-Zugang haben
- ❌ User mit technischem Jargon zuschütten
- ❌ Hand-Edit von Code annehmen
- ❌ Architektur-Änderungen ohne `DECISIONS.md`-Eintrag
- ❌ Halluzinierte Reforger-API-Calls (immer Quelle: `research/01-workbench-sdk.md`)
- ❌ Runtime-LLM-Calls in Mission-Files

## Collaborator Notes

- User (Paul) ist Creative Director, kein Coder. Alles geht via Claude Code.
- Ody als optional collaborator (gleicher Workflow).
- Bei Zweifel: in einfacher Sprache fragen.
