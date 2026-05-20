# Original Setup-Auftrag: Arma Reforger AI-Native Mission Authoring System

> **Status:** Foundation document. Aus DEV-03-Chat (Phase 1). Diese Datei ist die Quelle der Wahrheit für die ursprüngliche Vision. Alle Architektur-Änderungen werden in `DECISIONS.md` dokumentiert und referenzieren diese Foundation.

## Variablen

- **PROJECT_NAME:** `arma-reforger-coop`
- **PARENT_REPO:** ursprünglich `control` Monorepo → **revidiert** zu Standalone-Repo (siehe `DECISIONS.md` 2026-05-20)
- **GITHUB_USER:** `paulfanger`
- **PRIMARY_NAME:** Paul (Creative Director, Non-Coder)
- **COLLABORATOR_NAME:** Ody (optional)
- **REFORGER_TOOLS_PATH:** nicht verfügbar auf macOS — siehe Fallbacks

## Mission

Wir bauen ein AI-native Mission Authoring System für Arma Reforger. Das System ist NICHT ein Mission-Generator. Es ist eine kreative Co-Creation-Umgebung, in der ein Non-Coder (Creative Director) gemeinsam mit AI cinematic, emergent, narrativ-dichte PVE/Koop-Missionen baut.

**Fokus:**
- Singleplayer + Koop vs. AI (kein PVP)
- Narrative Konsistenz, filmische Atmosphäre, glaubwürdige militärische Logik
- Emergente Situationen, intelligentes Pacing, räumliches Storytelling
- Iterative Mensch-AI-Zusammenarbeit, NICHT Autonomie

## 8-Stage Pipeline (Vision)

1. **Narrative Extraction** — Idee/Storyline → semantisches Missionsmodell (Faktionen, Doktrinen, Terrain, Tonalität, Pacing)
2. **Asset Constraints** — Validierter World-Katalog, KEINE Halluzinationen
3. **Spatial Location Proposals** — Mehrere Location-Vorschläge mit Viewport-Screenshots, Sichtlinien, Tageszeit
4. **Storyboard/Moodboard Understanding** — Multimodale Bild-Inputs für Stimmung
5. **Iterative User Approval Pipeline** — Graph-basiert, versioniert, Undo/Redo. NIEMALS autonom.
6. **Mission Flow / Gameplay Mapping** — Objectives, Patrols, Trigger, Spawnwaves, AI-States, Eskalation
7. **Runtime AI Director** (Langzeit-Vision) — Cinematic AI Director während Gameplay
8. **Testing / Refinement** — Telemetry, Heatmaps, Pacing-Analyse, automatisierte Verbesserungen

## Workbench-Integration (Phasen)

- **Phase 1 (MVP):** External Only (A) — Backend schreibt Mission-Files, User importiert manuell
- **Phase 2:** Hybrid (B) — Backend ↔ Workbench Plugin via REST/IPC, Hot-Reload
- **Phase 3:** Native (C) — Chat-Panel im Editor, Viewport-Control, Live-Spawning

## Subagent-Architektur (Original-Vision)

**Hierarchisches Orchestrator + Spezialisten-Pattern:**

- **1× Orchestrator:** `mission-director` — koordiniert alle, hält Mission-State, User-Approval-Gates
- **Stage-Spezialisten:** `narrative-designer`, `asset-curator`, `spatial-scout`, `moodboard-analyst`, `encounter-designer`, `flow-architect`, `ai-director-runtime`, `playtest-analyst`
- **Domain-Spezialisten:** `faction-doctrine`, `weather-time`, `cinematic-composer`, `terrain-reader`
- **Utility-Agenten:** `version-keeper`, `reforger-bridge`

## Kritische Prinzipien

- ❌ LLM darf KEINE Assets halluzinieren
- ❌ Pipeline ist NICHT autonom — Approval-Gates sind heilig
- ✅ Versionierung ist Pflicht
- ✅ User ist Non-Coder — einfache Sprache, Erklärung vor Aktion

## Anti-Patterns (NIEMALS)

- Asset-IDs erfinden, die nicht im catalog/ existieren
- Stages ohne explizite User-Approval überspringen
- Mission-Files schreiben ohne Snapshot
- Subagent-Calls direkt zwischen Specialists ohne mission-director
- Workbench-Plugin-Code committen vor Hybrid-B-Stage
- User mit technischem Jargon zuschütten
- Hand-Edit von Code annehmen
- Architektur-Änderungen ohne `DECISIONS.md`-Eintrag
- Halluzinierte Reforger-API-Calls

## Pfad-Revision (2026-05-20)

Original-Plan: `control/gaming/projects/mods/arma-reforger-coop/`
Realität: kein `control`-Monorepo vorhanden auf User-Mac.
**Entscheidung:** Standalone-Repo unter `/Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios/` — passt zum ELOS-Nummerierungs-Pattern.

## Environment-Realität (2026-05-20)

- **OS:** macOS (M1 ARM, Darwin 25.0.0)
- **Reforger Tools:** NICHT installiert (Windows-only Tool, auf diesem Mac nicht verfügbar)
- **Konsequenz:** MVP läuft als External-Only File-Pipeline. Hybrid B + Native C brauchen Windows-Zugang (später).
