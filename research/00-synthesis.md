# Research Synthesis — Decision-Ready Summary

> **Inputs:** `research/01-workbench-sdk.md`, `research/02-mission-format.md`, `research/03-eula-legal.md`, `arma-reforger-coop-setup-prompt.md`, `DECISIONS.md`
> **Date:** 2026-05-20
> **Synthesizer-Modell:** Claude Opus 4.7

---

## Executive Summary (3 Bullets)

- **Programmatic Mission-Authoring ist technisch realistisch.** Alle Mission-relevanten Files (`.gproj`/`.conf`/`.ent`/`.layer`/`.meta`) sind text-basierte Brace-Syntax, vier produktionsreife OSS-Sample-Repos belegen das Format vollständig.
- **macOS-only Workflow hat 90%-Lösung via Linux Dedicated Server, 100%-Lösung erfordert Windows-Zugang.** Workbench-Packaging + Publish ist Windows-only und nicht headless-fähig — aber direct-load via `-addonsDir`/`-mission` auf Linux-DediServer ist ein offener vielversprechender Bypass-Pfad (zu verifizieren).
- **EULA-Risiko GREEN für offline-Authoring** mit APL-ND + Disclosure. Bohemia ist tech-neutral, Precedents (AI War Mod live, enfusion-mcp public) bestätigen Praxis. Runtime-LLM bleibt out-of-scope.

---

## Original-Setup-Prompt vs. Research

| Architektur-Element | Original-Vision | Research-Finding | Anpassung |
|---|---|---|---|
| Workbench Plugin (Native C) | geplant für Phase 3 | Hybrid B realistisch jetzt, Native C nicht in 2026 | **defer Native C dauerhaft**, Hybrid B Plugin-Template aber jetzt erstellen |
| File-Pipeline Generation | MVP-Approach (External A) | feasible mit Brace-Syntax-Custom-Formatter | **keep + extend** — Backend schreibt direkt Enfusion Brace-Syntax, nicht JSON |
| Asset-Catalog Validation | Pflicht-Gate via asset-curator | GUID-Referenzen sind Mechanismus (16-hex), Halluzination kritisch | **harden**: catalog/ muss GUID-Mappings enthalten, nicht nur asset-Namen |
| Stage 3 (Spatial Scout) | geplant für Phase 2 | braucht Workbench-API-Access (`WorldEditorAPI`) → nur via Plugin | **defer zu Phase 2** (Win-Zugang erforderlich), Plugin-Template vorbereiten |
| Stage 4 (Moodboard) | geplant für Phase 2 | unabhängig von Reforger-SDK, nur Vision-API | **keep für Phase 2** unverändert |
| Stage 7 (Runtime AI Director) | langfristig | EULA-yellow (runtime-LLM), MANW disqualifiziert | **out-of-scope für MVP + Workshop**, nur als Single-Player-Experiment denkbar |
| GUID-Generation | nicht definiert | engine validiert nicht mathematisch, aber muss self-consistent | **Backend mintet random 16-hex-upper, Catalog tracked**; alternativ Plugin-Path delegiert an Workbench |
| Mission-File-Output | nicht spezifiziert | 6 Files: gproj + conf + conf.meta + ent + ent.meta + N layers | **reforger-bridge** generiert vollständiges Tree, nicht nur einzelne Files |
| Packaging zu .pak/Workshop | nicht spezifiziert | Workbench-only, Windows-only | **MVP exportiert unpacked addon-tree als .zip**, Publishing manuell |
| Linux Dedicated Server | nicht im Original | direct-load via `-addonsDir`/`-mission` möglich (zu verifizieren) | **als Test-Pfad in MVP einbauen** — wenn es klappt, brauchen wir Win-Box nur für finalen Workshop-Upload |
| Lizenz | nicht spezifiziert | APL-ND + Disclosure-Header empfohlen | **add to roadmap**: LICENSE.md + Mission-Header-Disclosure-Template |

---

## Decision Matrix: External vs. Hybrid vs. Native

| Kriterium | External (A) | Hybrid (B) | Native (C) |
|---|---|---|---|
| Feasibility 2026 | ✅ 100% (verifiziert, 4 OSS-Repos) | ✅ 80% (CRF_MissionCreationPlugin als Vorlage) | ❌ <10% (keine HTTP/Socket API in Enforce Script) |
| Mac-only Compatible | ⚠️ Authoring ja, Packaging nein | ❌ Plugin läuft Win-only | ❌ Win-only |
| Linux DediServer Compatible | ✅ (zu verifizieren) | ❌ Plugin = Workbench | ❌ |
| EULA-Risk | 🟢 GREEN | 🟢 GREEN (offline-Plugin) | 🟢 GREEN |
| Implementation-Effort (MVP) | LOW (Brace-Formatter + Schema) | MID (Plugin ~200 LOC + Spec-Reader) | HIGH (Custom-Native-Extension, nicht erlaubt) |
| User-Experience-Quality | Low (lange Iter-Loops, manueller Reload) | Mid-High (~5s Loop) | N/A |
| Asset-Hallucination-Risk | Mid (Backend könnte fakte GUIDs) | Low (Plugin nutzt Workbench-API) | N/A |
| Backend-Komplexität | Mid (Custom-Formatter) | Mid (Spec-JSON + Plugin-Sync) | High |
| Test-Coverage extern | High (file-diff) | Mid (braucht Workbench-CLI) | Low |
| Recommendation Score (1-10) | **8** | **6 (jetzt)** / **9 (mit Win-Zugang)** | **2** |

---

## Risk-Adjusted MVP Recommendation

**MVP-Architektur = External A + Hybrid B Skeleton (kein operatives Plugin im MVP)**

Begründung: User ist auf macOS, hat aktuell keinen Win-Zugang. External-A funktioniert end-to-end via Brace-Syntax-Generation und produziert ein unpacked addon-tree. Der Test-Pfad ist:

1. Backend generiert Mission-Files in `missions/{id}/output/`
2. Pipeline-Tester + Mission-Validator prüfen Schema + Asset-References
3. Bei verifiziertem Linux-DediServer-Direct-Load (Open Question 1 aus research/02): User kann lokal auf Linux-Dedi (oder VM) testen
4. Bei nicht-verifiziertem Path: User kopiert tree manuell an Win-Tester (Workshop-Publish bleibt Windows)

Hybrid-B-Plugin wird als **Plugin-Skeleton** in `workbench-plugin/` Ordner abgelegt, READY-TO-USE für späteren Win-Zugang, aber nicht aktiv im MVP-Test-Loop. Das spart Refactor wenn Win-Zugang kommt.

**MVP-Scope finale Stages:**
- ✅ Stage 1: Narrative Extraction (narrative-designer)
- ✅ Stage 2: Asset Validation (asset-curator gegen GUID-Catalog)
- ✅ Stage 5: Approval-Gates (mission-director)
- ✅ Stage 6: Mission Flow + File Generation (encounter-designer + flow-architect + reforger-bridge)
- ❌ Stages 3, 4, 7, 8 — deferred zu Phase 2/3/Long-Term

**Bonus Stretch-Goal:** Linux-DediServer-Smoke-Test als optionaler `workbench-integration-tester` Mode-A-Test wenn `WORKBENCH_DEDI_HOST` env-var gesetzt.

---

## Hard Blockers — Final List

1. **Workbench ist Windows-only.** macOS-User braucht Win-VM/-Box/-Tester für Packaging + Workshop-Upload. (Source: `01-workbench-sdk.md` Hard Blocker #1)
2. **Keine REST/HTTP/Socket-API in Enforce Script.** Native C nicht möglich. Externe Kommunikation = File-Watching oder `RunProcess`. (Source: `01-workbench-sdk.md` Hard Blocker #2)
3. **`.gproj` Packaging-Step ist Workbench-only.** Kein dokumentierter headless-Publish-Pfad. (Source: `02-mission-format.md` Generation Strategy)
4. **GUID-Referenzen auf nicht-existente Prefabs degradieren silent.** Asset-Halluzination = no error, just broken mission. (Source: `02-mission-format.md` Validation Rule #5)
5. **MANW 2025 Wettbewerb disqualifiziert "external software"-runtime.** Mission-Submissions mit Live-LLM-Calls = out. (Source: `03-eula-legal.md` Risk #9)

---

## Fallback Triggers — When to Switch

| Hard-Blocker / Trigger | Detection-Bedingung | Fallback-Aktion |
|---|---|---|
| Win-Workbench nicht verfügbar | User-Check ergibt kein Win-Host | **Mode A:** File-Pipeline-Only, .zip export. Plugin-Skeleton bleibt liegen. |
| Linux-DediServer-Test schlägt fehl | workbench-integration-tester Mode-A fail | Fallback zu Mode-B: `MANUAL_VERIFICATION_REQUIRED.md` mit Win-Tester-Steps. |
| Brace-Syntax-Generation produziert Garbage | mission-validator Schema-Check fail | **Re-Run mit Sample-Vorlage** (CoopTest.conf als Template), bug-fixer adjustiert Formatter. |
| GUID-Kollision detected | mission-validator Cross-File-Check fail | **Catalog-Sync** triggern, Backend re-mintet GUIDs, neue Snapshot. |
| Asset-Halluzination | mission-validator: asset_id nicht in catalog | **HALT** + User-Briefing. Niemals silent Fix durch Catalog-Erweiterung. |
| Reforger-Update bricht Schema | bisher grüne Mission failed validation | **Re-Run workbench-sdk-researcher** mit Diff-Brief, Architecture-Update via DECISIONS. |
| EULA-Policy ändert sich | News-Watch trigger | Workshop-Upload pausieren, README-Update, lokale Distribution-Only. |

---

## Architecture-Changes (vs. Original-Setup-Prompt)

1. **Subagent-Konsolidierung für MVP:**
   - Domain-Spezialisten (`faction-doctrine`, `weather-time`, `terrain-reader`) werden **gemerged** in `narrative-designer` und `encounter-designer` für MVP. Re-Split bei Phase 2 wenn nötig.
   - `cinematic-composer` bleibt deferred (Stage 4).
   - `spatial-scout`, `moodboard-analyst`, `ai-director-runtime`, `playtest-analyst` sind deferred.
   - Aktive MVP-Specialists: **7** statt 13 (Mission-Director + 6).

2. **Asset-Catalog wird GUID-zentriert:**
   - Schema: `{ "guid": "904EC091C347AEA9", "type": "prefab", "displayName": "CoopGameMode", "path": "Prefabs/MP/Modes/Coop/CoopGameMode.et", "source_dependency": "ArmaReforger_core", ... }`
   - Bootstrap: aus `BohemiaInteractive/Arma-Reforger-Samples` + `exocs/Reforger-Sample-Coop` extrahieren (Web-Scrape oder lokales Clone)
   - `/sync-catalog` ist Pflicht-Command vor erstem Build

3. **Reforger-Bridge generiert vollständiges Addon-Tree:**
   - Output ist nicht "ein Mission-File", sondern eine **vollständige addon-Hierarchie**:
     ```
     output/
     ├── addon.gproj
     ├── addon.gproj.meta (wenn nötig)
     ├── Missions/{name}.conf
     ├── Missions/{name}.conf.meta
     └── Worlds/{name}.ent + .meta + N layer files
     ```
   - Pack-Step: Tree → .zip für Transfer an Win-Host oder Linux-Dedi

4. **Workbench-Plugin-Template als deferred Asset:**
   - Ordner `workbench-plugin/` mit Skeleton-Enforce-Script (`AI_GeneratePlugin.c`), Plugin-Manifest, README mit Aktivierungs-Anleitung
   - Im MVP **nicht aktiv** — wartet auf Win-Zugang. Sonnet 4.6 implementiert Skeleton, aber kein Testing-Coverage.

5. **Linux-DediServer-Pfad als Test-Option:**
   - Wenn User Linux-Dedi (lokal oder remote) bereitstellt: `workbench-integration-tester` Mode-A versucht `reforger-dedi -addonsDir <path> -mission "{GUID}Missions/<name>.conf"`
   - Open Question 1 aus `02-mission-format.md` — empirisch zu testen

6. **EULA-Compliance-Layer hinzufügen:**
   - `LICENSE.md` mit APL-ND-Lizenztext
   - `playbook/EULA_COMPLIANCE.md` mit Disclosure-Templates
   - reforger-bridge inseriert auto-Disclosure in `m_sAuthor`/`m_sDescription` Felder von generated `.conf`-Files

7. **Backend-Module-Struktur verfeinert:**
   ```
   backend/
   ├── main.py
   ├── llm/                 # Provider-Abstraction (deferred Impl)
   ├── catalog/             # GUID-Resolver, Catalog-Reader/Writer
   ├── exporters/           # Brace-Syntax-Formatter
   │   ├── gproj.py
   │   ├── conf.py
   │   ├── ent.py
   │   ├── layer.py
   │   └── meta.py
   ├── validators/          # Schema-Checks aus `02-mission-format.md`
   │   ├── schema.py
   │   ├── guid_consistency.py
   │   └── cross_file.py
   ├── snapshots/           # Snapshot-Storage
   └── tests/               # Unit-Tests pro Module
   ```

8. **Catalog-Bootstrap-Strategy aktualisiert:**
   - Statt "Reforger-Tools scannen" → "OSS-Sample-Repos clonen und parsen"
   - Sources: `exocs/Reforger-Sample-Coop`, `BohemiaInteractive/Arma-Reforger-Samples`, `Kexanone/CombatOpsEnhanced_AR`, `gruppe-adler/GRAD-COOP-Template-Reforger`
   - Parser extrahiert `{GUID}Path.et` Patterns + Class-Names → catalog/

9. **Validation-Rules-Liste (aus 02-mission-format.md) wird Catalog-File:**
   - `playbook/VALIDATION_RULES.md` mit 12+ Regeln
   - `mission-validator` parst diese Datei und prüft jede Regel programmatisch

10. **Sonnet 4.6 erhält explizite Anweisung zur Open-Question-Verifikation:**
    - Open Question 1 (Linux-DediServer-Direct-Load) ist der wichtigste Empirie-Test
    - Sonnet 4.6 schreibt Test-Plan + bei verfügbarem Linux-Setup ausführen
    - Falls bestätigt: MVP wird massiv Mac-friendly. Falls nein: Win-Box-Empfehlung in `READY_FOR_MANUAL_TESTING.md`

---

## Critical Open Questions (für Sonnet 4.6)

1. **Linux-DediServer direct-load** — verifizieren, ob unpacked addon-tree ohne Workbench-Packaging ladbar ist. **Highest-Impact.**
2. **GUID-Mintng-Algorithmus** — observed-Pattern legt timestamp-prefix nahe, aber nicht verifiziert. Pragmatisch: random 16-hex-upper, dedupe gegen catalog.
3. **`.meta`-Sidecar-Pflichtfeld-Liste** — observed Files haben minimale `Configurations`-Blöcke, aber Vollständigkeit unklar. Backend startet mit 5-Platform-Inherit-Block (verifiziert in CoopTest.conf.meta).
4. **Scenario Framework Entity-Klassen** — `SCR_ScenarioFrameworkLayerTask*` etc. nicht vollständig dokumentiert. Follow-up-Research bei Bedarf für advanced Pacing.
