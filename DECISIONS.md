# Architecture Decisions

> Chronologisch. Jede Entscheidung referenziert Kontext, Quelle, Trade-offs.

---

## 2026-05-20: Projekt-Standort = Standalone-Repo, nicht Monorepo

**Context:** Original-Setup-Prompt nahm `control` Monorepo unter `~/Projects/control/gaming/projects/mods/arma-reforger-coop/` an. Pre-Flight Phase 0 hat festgestellt: kein `control`-Repo existiert. Stattdessen: ELOS-Project-Folder unter `/Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios/` (passt zum bestehenden ELOS-Nummerierungs-Pattern: 100_, 101_, 102_, etc).

**Decision:** Standalone-Repo. Kein Monorepo-Aufbau. Wenn später Monorepo nötig wird, ist Migration via git subtree machbar.

**Source:** Pre-Flight Bash-Check 2026-05-20, parent-dir listing.

**Trade-offs:** Kein zentraler Monorepo-Vorteil (geteilte Configs/Tooling über mehrere Projekte). Dafür schneller Setup, klare Projekt-Boundaries.

---

## 2026-05-20: MVP-Modus = External-Only File-Pipeline (Mac-First)

**Context:** Arma Reforger Tools (Workbench) sind Windows-only. User-Hauptsystem ist macOS M1. Phase 0 Pre-Flight hat keinen Reforger-Install gefunden.

**Decision:**
- MVP läuft komplett extern auf macOS
- Output: Mission-Files (.conf/.et/.layer) in `missions/{name}/output/`
- User importiert manuell auf Windows-System (oder Tester) ins Workbench
- Phase 2 (Hybrid B) und Phase 3 (Native C) werden in `ROADMAP.md` als "Windows-Required" markiert und für später verschoben

**Source:** Phase 0 Pre-Flight 2026-05-20, OS-Detection.

**Trade-offs:** Keine Live-Spawning oder Workbench-IPC im MVP. Dafür: alles testbar auf macOS, kein VM/Bootcamp-Overhead.

---

## 2026-05-20: Phase-1-Clarifying-Questions übersprungen (Auto Mode, konservative Defaults)

**Context:** Phase 2 Research-Prompt erlaubt Skip von Clarifying-Questions wenn der Original-Setup-Prompt klar genug ist. User hat Auto Mode aktiviert (autonom, Action vor Planning).

**Decision:** Folgende Defaults werden gesetzt und in nachfolgenden Entscheidungen referenziert:

1. **Test-Mission (Reference Goal):** "Night Recon Everon" — minimale Coop-Mission, 2-4 Spieler, Insertion bei Nacht, 1 Recon-Objective, Patrol-AI, Exfil. Wenn Research zeigt dass dies zu ambitioniert ist: Fallback "Stationary Defense vs. 1 AI Wave".
2. **Risk-Tolerance:** Konservativ. Bei jedem Hard-Blocker → automatischer Switch zur File-Pipeline-Variante, kein Nachfragen. Nur Soft-Blocker werden dem User zur Entscheidung vorgelegt.
3. **Time Budget:** MVP-Scope (open-ended, aber begrenzt auf Self-Testing-Pipeline-Reife, nicht auf Feature-Vollständigkeit).
4. **Self-Testing-Endpunkt:** Stufe (c) — "Mission lässt sich in Workbench öffnen" ist Ziel, dokumentiert als manual-verification-required (da Mac → kein Workbench lokal).
5. **Workbench-Integration-Tiefe:** Strikt MVP-External. Kein Hybrid-/Native-Code in dieser Iteration.

**Source:** Phase 2 Research-Prompt, Section 1; Auto Mode aktiv.

**Trade-offs:** Möglicherweise Nachjustierung nötig, wenn User andere Test-Mission im Kopf hatte. Risikominimum gewahrt.

---

## 2026-05-20: LLM-Backend = Claude only (Anthropic), Provider-Swap-Ready

**Context:** Original-Setup-Prompt-Frage 4 nicht final beantwortet. Auto Mode → konservativer Default.

**Decision:** Claude only via Anthropic API. Backend-Code wird mit Provider-Abstraction-Layer geschrieben (LLM-Interface in `backend/llm/`), so dass spätere Erweiterung um OpenAI/Gemini ohne Pipeline-Refactor möglich ist.

**Source:** Phase 1 Frage 4 (übersprungen), konservativer Default.

**Trade-offs:** Single-Provider-Risiko (API-Outage, Pricing). Mitigiert durch saubere Abstraction.

---

## 2026-05-20: Research-Sub-Agents als Single-Call General-Purpose Agents

**Context:** Phase 2 Research-Prompt schreibt Sub-Agent-Spec-Files unter `.claude/agents/research/` vor. Aber: tatsächliche Research-Arbeit braucht WebSearch + WebFetch und parallele Ausführung.

**Decision:** Doppelte Implementierung:
- **Spec-Files** unter `.claude/agents/research/*.md` werden geschrieben (dokumentarisch, für Reproduzierbarkeit + Audit-Trail)
- **Actual Research** wird via `Agent`-Tool mit `subagent_type: general-purpose` parallel gestartet (3 Agents gleichzeitig)
- Research-Outputs landen in `research/0X-*.md`

**Source:** Phase 2 Prompt, plus Praktikabilität (Spec-Files allein führen keine Recherche durch).

**Trade-offs:** Etwas doppelte Arbeit (Spec + Invocation), aber maximale Klarheit für spätere Audits.

---

## 2026-05-20: Workbench-Integration-Path = Hybrid B mit External-Fallback (Research-Bestätigt)

**Context:** workbench-sdk-researcher hat verifiziert (Output: `research/01-workbench-sdk.md`):
- Headless/CLI-Mode EXISTIERT offiziell (`-wbsilent`, `-buildData HEADLESS`, `-validate`, `-plugin=`)
- `.layer`/`.ent`/`.et`/`.gproj` sind text-basiert mit Brace-Syntax → programmatic Generation realistisch
- KEINE Sockets/HTTP in Enforce Script — External IPC NUR via `RunProcess` oder File-Watching (Discord-RP-Pattern)
- BohemiaInteractive/Arma-Reforger-Script-Diff (offen seit 09/2025) liefert die komplette API-Reference
- Coalition-Reforger-Framework `CRF_MissionCreationPlugin` ist canonical Reference für programmatic Mission-Generation

**Decision:** Architektur wird auf Hybrid-B-Ready aufgebaut, MVP läuft aber als External-Only (A):
- **MVP (jetzt, macOS-only):** Backend generiert `.layer`/`.conf`/`.gproj` als Brace-Syntax-Text. User kopiert auf Win-Host und öffnet in Workbench.
- **Phase 2 (sobald Win-Zugang):** Wir bauen eine kleine `WorkbenchPlugin` (Enforce Script, ~150-300 LOC) basierend auf CRF-Plugin-Pattern. Plugin liest JSON-Spec via `FileIO`, ruft `WorldEditorAPI.CreateEntity()`, `worldEditor.Save()`. Headless-Build via `-plugin=AI_GeneratePlugin -spec=path.json -exitAfterInit`.
- Native C bleibt langfristig out-of-scope (kein bidirektionaler Channel in Workbench-API).

**Source:** `research/01-workbench-sdk.md` Sections 4 (Headless), 5 (Entity-Spawning), 6 (Community-Plugins). Empfehlung B.

**Trade-offs:** Mehr Konzeption-Aufwand jetzt für eine Plugin-Bridge die wir noch nicht bauen. Aber: spart später Refactor. Reforger-bridge-Agent wird so designed dass beide Outputs gehen (raw Files für A, Spec-JSON für B).

---

## 2026-05-20: Mission-File-Format = Brace-Syntax-Generation, KEINE Workbench-UI-Steps zwingend

**Context:** Research bestätigt: `.layer` Files sind text-basierte Brace-Syntax, parsbar wie YAML/HOCON. Verifiziertes Beispiel von BohemiaInteractive/Arma-Reforger-Samples:
```
CinematicEntity Cinematic_Tutorial {
    coords 0 0 0
    Scene CinematicScene "{GUID}" {
        Tracks { ... }
    }
}
```

**Decision:** 
- Backend `reforger-bridge` Agent schreibt Brace-Syntax direkt (Custom-Formatter, nicht JSON-Serialization)
- GUIDs werden NICHT selbst generiert — wenn programmatic-Generation auf Win-Side via Plugin läuft, dann lässt Plugin die Workbench-API GUIDs vergeben. MVP-External: User klickt einmal in Workbench um neue GUIDs zu Reload-Time vergeben zu lassen.
- Schema-Validation: best-effort Pre-Check im Backend (Brace-Balance, required fields) + post-import-Validation via Workbench `-validate` Flag.

**Source:** `research/01-workbench-sdk.md` Section 5 (Entity-Spawning), File-Type Constants.

**Trade-offs:** Custom-Formatter statt Standard-Library. Mitigiert durch Test-Suite die echte BI-Sample-Files re-serialisiert und vergleicht.

---

## 2026-05-20: EULA-Konformität = Offline-Authoring + APL-ND + Disclosure-Header (Risk GREEN)

**Context:** eula-legal-researcher hat verifiziert (Output: `research/03-eula-legal.md`):
- Bohemia EULA ist technologisch-neutral, AI wird nicht erwähnt
- Workshop Terms erlauben Tools (Zitat: "any software associated with the Game")
- Precedent "AI War" Mod live im Workshop seit 03/2026 ohne Removal
- enfusion-mcp (Claude-driven Modding) existiert publicly auf GitHub
- MANW 2025 disqualifiziert "external software" runtime — betrifft NUR runtime-LLM, nicht offline-Authoring
- Asset-References via GUID = OK; Asset-Embedding = verboten

**Decision:**
- **MVP-Mode = strikt offline-Authoring:** LLM läuft nur dev-time, Runtime-Mission ist 100% statisch Reforger-nativ
- **Lizenz:** APL-ND (Arma Public License — No Derivatives) für alle generierten Mission-Outputs
- **Disclosure** Pflicht in 3 Stellen:
  1. Mission-Header (`.conf` description field): 1-Satz-Notiz "Authored with LLM-assisted tooling. Human review by [Author]."
  2. Workshop-Upload-Description: Section "AI Disclosure" mit Tool-Liste
  3. README.md im Repo: ausführliche Methodik
- **Keine Bohemia-Asset-Training:** LLMs werden NICHT auf extrahierten Game-Files feingetuned
- **Human-in-the-Loop:** Jeder Output wird vor Workshop-Upload manuell gesichtet (Approval-Gates der Pipeline erfüllen das)

**Source:** `research/03-eula-legal.md` Sections "Recommended Disclosure Approach" + "Mitigation Strategies" + "Asset Handling".

**Trade-offs:** APL-ND verhindert externe Re-Use unserer Mission-Outputs (positiv für Schutz, einschränkend für offene Community-Workflows). Disclosure-Pflicht kostet etwas Texten je Upload. MANW-Submission ist nur möglich wenn 100% offline-Authoring nachweisbar — passt zu MVP.

---

## 2026-05-20: Hard Blockers identifiziert + Fallback-Strategien festgelegt

**Context:** Research-Output identifiziert 4 Hard-Blocker:
1. Workbench ist Windows-only (kein nativer Mac-Build)
2. Keine REST/HTTP/Socket-API in Enforce Script
3. Keine Custom Native Extensions im Script-Sandbox
4. Kein formales Schema für `.layer`/`.ent` (Reverse-Engineering von Samples nötig)

**Decision — Fallback-Strategien:**

| Hard-Blocker | Trigger | Fallback |
|---|---|---|
| Win-Workbench nicht verfügbar | User-Check ergibt kein Win-Host | **Mode A:** File-Pipeline-Only. Output ist .zip, User schickt an Tester mit Windows. Hybrid-B-Plugin bleibt in Plugin-Repo, ungetested bis Win-Zugang. |
| Brace-Syntax-Generation bricht | mission-validator findet syntax-Error in generated Files | **Step-back zu Cinematic-Tutorial-Schema** (verified working). Re-test mit Sample-Vorlage. Max 5 bug-fixer-Iterationen, dann Halt + User-Ping. |
| GUIDs nicht stabil | Cross-File-Inconsistency detected | **Plugin-Path nutzen** statt extern (Workbench-API vergibt GUIDs). Falls kein Win-Host: User-Anweisung "Open in Workbench, save once" generieren. |
| Schema-Drift bei Reforger-Update | Re-Test eines bisher grünen Mission-Files fail | **Re-run workbench-sdk-researcher** mit spezifischem Diff zur vorherigen Reforger-Version. Architecture-Update via DECISIONS-Eintrag. |

Plus die zwei aus dem Original-Prompt Phase 4.4:
- **EULA-Risk Eskalation** (z.B. Bohemia ändert Policy): Workshop-Upload pausieren, lokale Distribution-Only, README mit aktuellem Status.
- **Asset-Catalog leer:** Placeholder mit Vanilla-Defaults nutzen, markiert "incomplete", `/sync-catalog` nach Win-Setup ausführen.

**Source:** `research/01-workbench-sdk.md` Hard Blockers + Soft Blockers; `research/03-eula-legal.md` Worst-Case Section.

**Trade-offs:** Fallbacks reduzieren Feature-Set des MVP, aber sichern testbaren End-to-End-Pfad.
