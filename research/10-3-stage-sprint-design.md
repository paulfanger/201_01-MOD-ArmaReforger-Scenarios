# 3-Stage Sprint Design — Research Synthesis

> Stand: 2026-05-21
> Source: 3 parallel research agents on Stage 1 (headless), Stage 2 (autonomous game), Stage 3 (irreducible user)
> Purpose: design optimal sprint plans + wrapper prompts for each user-availability state

---

## Critical Discoveries (game-changing)

### 1. Bypass-Menu-Trick for Stage 2 autonomy
**Local Dedi Server + `-client -connect` skipped das Hauptmenü.** Statt vision-loop durch Steam → Reforger-Menu → Scenarios → Click-Play, läuft:
```bash
ArmaReforgerServer.exe -config night-recon-config.json -autoreload 0  # Background
ArmaReforgerSteam.exe -client -connect=127.0.0.1
```
→ Game spawnt direkt in Mission. ~30-60 Sek statt 3-5 Min Menu-Navigation.

### 2. BattlEye-Reality (corrects EAC-fear)
- Reforger uses **BattlEye**, NOT EAC
- BattlEye ist nur auf BE-protected MP servern aktiv
- **Workbench, Game Master, lokale SP-Scenarios, lokale Dedi: BattlEye-OFF**
- Input-Simulation via PyDirectInput in SP = **0% Ban-Risiko** (ACM 2025 paper bestätigt)

### 3. PyDirectInput statt PyAutoGUI
- Reforger ist DirectX-Game → PyAutoGUI's `keybd_event` wird IGNORIERT
- **PyDirectInput** (`pip install pydirectinput`) → `SendInput()` mit DirectX scan codes → funktioniert
- pyinterception als Fallback (kernel driver, bypasses LLKHF_INJECTED flag)

### 4. Vision-Loop Resolution-Constraint (Anthropic docs)
- Native 1080p/4K screenshots → click-accuracy degradiert massiv
- **Capture native, downscale auf 1280x800 (oder 1024x768) BEVOR API call**
- Maintain coord-scale-factor für click-back
- Cycle time: ~8 sec per click, max 8 cycles menu→in-game

### 5. Game-Client-Flags die NICHT existieren
- KEIN `-scenario`, `-mission`, `-autorun` für Retail-Client (nur server-side)
- `-loadSessionSave [UUID]` lädt save FÜR currently selected scenario
- **Daher: Dedi-Server + Client-Connect ist DIE Lösung**

### 6. Steam launch-best-practice
- `steam.exe -applaunch 1874880 <args>` ist zuverlässig
- `steam://run/<appid>//-args` URIs sind unreliable (Valve confirmed Beta thread)

### 7. Reforger UI ist Custom (nicht Win32/MSAA)
- UI Automation API → empty tree
- pywinauto/AutoIt control-based ansätze tot
- **Image/Vision-basiert ist EINZIGER Weg** (für Menu, falls Dedi-Trick nicht klappt)

---

## Stage Definitions

| Stage | User-Verfügbarkeit | Workload | Wo passiert |
|---|---|---|---|
| **S1** | User spielt CS — KEIN GPU/Game/Workbench touch erlaubt | Pure-text headless work | Mac primär + PC für validate-pulls |
| **S2** | User abwesend — Steam logged in, Game installed, BE-OFF environment | Autonome Game-Steuerung via Dedi-Trick + Vision | PC primär (Sonnet 4.6) |
| **S3** | User AM PC — manuelle Aktionen erlaubt | Irreducible user-gates + creative judgment | PC + User-Klicks |

---

## Stage 1 — Headless Foundation Sprint (during CS)

Per Stage 1 research findings. ALL of these are pure-text/file work, NO GPU touch:

**Workload-Breakdown (3-4 Std insgesamt):**

| Step | Action | Output | Verifier |
|---|---|---|---|
| S1.1 | Plugin refactor: Pseudocode → real WorldEditorAPI calls (Bohemia Script-Diff Repo Reference) | `workbench-plugin/AI_GeneratePlugin.c` (functional Enforce-Script, compiles in theory) | PC syntax-check (Enforce IDE if installed) |
| S1.2 | Schema-Mapping Tabelle narrative.json → API calls | `playbook/SCHEMA_MAPPING.md` | Mac auditor |
| S1.3 | Linux Docker Dedi setup auf Mac + `-listScenarios` integration | `scripts/docker-validate.sh` + `backend/scripts/validate_dedi.py` | Mac smoke-test |
| S1.4 | `backend/routes/revisions.py` mit JSON-Patch (RFC 6902) + jsonschema | `revise_mission()` API endpoint | pytest |
| S1.5 | `backend/llm/__init__.py` mit `cached_completion()` wrapper (Anthropic Prompt Caching) | LLM-Call mit ephemeral cache_control für stable prefixes | pytest |
| S1.6 | `backend/memory/episodic.py` (~50 LOC, SQLite FTS5) | episodic log + search functions | pytest |
| S1.7 | `tests/golden/` baseline für night-recon-everon + 1 revision case | Golden trajectory regression | pytest |
| S1.8 | `SETUP.md` (Mac+PC replication guide) | Standalone setup doc | Mac auditor |
| S1.9 | Self-test pipeline run + golden regression | Full test pass | PC docker-validate |
| S1.10 | Audit + reflection-turn-N-pc.md + push | Sprint result | auditor |

**Saturation:** ≥6× docker-listScenarios PASS + plugin compiles syntax-clean + revise_mission round-trip works on 3 golden trajectories + prompt-cache hit-rate >70% over 10 turns.

---

## Stage 2 — Autonomous Game Control Sprint (user absent)

Per Stage 2 research. **Dedi-Trick + PyDirectInput + Vision-Loop:**

**Workload-Breakdown (~30 min autonomous, plus prep):**

| Step | Action | Output | Verifier |
|---|---|---|---|
| S2.0 | Pre-flight: kill Workbench/Game/CS processes, verify Steam logged in, force resolution 1920x1080 windowed | clean state | PC auditor |
| S2.1 | dep-installer: install Python + pydirectinput + Pillow + pytesseract | deps verified | PC auditor |
| S2.2 | Generate dedi-config for night-recon-everon: write `dedi-config-night-recon.json` mit scenarioId | config valid | jsonschema |
| S2.3 | Spawn dedi server background: `Start-Process ArmaReforgerServer.exe -config dedi-config.json -autoreload 0` | server PID alive, port 2001 listening | netstat |
| S2.4 | Wait dedi ready (parse server log for "Listening for clients") max 60s | server ready signal | log-parse |
| S2.5 | Launch client: `steam.exe -applaunch 1874880 -client -connect=127.0.0.1 -window -resX=1280 -resY=800 -newErrorsAsWarnings` | client process alive | Get-Process |
| S2.6 | Vision-loop @ 1280x800 screenshots every 5s, classify state: MainMenu/Loading/SpawnScreen/InGame/Death/Crashed (Anthropic computer-use loop pattern) | state trajectory | multimodal classifier |
| S2.7 | Wenn SpawnScreen erreicht: click "DEPLOY" (vision-located coord, scaled back to native) | InGame state | multimodal verify |
| S2.8 | Wenn InGame: PyDirectInput WASD test (W 2s + space jump), screenshot, verify scene different | movement confirmed | screenshot-diff |
| S2.9 | Clean exit: SendKey Esc + Esc + click "EXIT TO MAIN MENU" (vision-located) | MainMenu state | multimodal verify |
| S2.10 | Kill dedi server + client processes | clean | Get-Process |
| S2.11 | Report + screenshots + reflection-turn-N-pc.md + push | Sprint result | auditor |

**Saturation:** state-trajectory `[MainMenu→Loading→SpawnScreen→InGame→InGame_moved→MainMenu]` + screenshots evidence + no crashes + total runtime <20 min.

**Escalation (→Stage 3):** crash on launch, BattlEye prompt (shouldn't happen offline but as safety net), Steam login expired, vision confidence <0.4 3x, 3 nav-loop failures.

---

## Stage 3 — User-at-PC Fallback Sprint

Per Stage 3 research. Minimal, ~10-15 min:

**Workload-Breakdown:**

| Step | Action | User-Aktion | Auto-able? |
|---|---|---|---|
| S3.1 | Read S2 result + reflection | — | — |
| S3.2 | Falls Workshop-Publish-Pfad: BI-Account verlinken (Workbench → Link) | ☐ User clicks | NEIN, OAuth-Popup |
| S3.3 | Falls Workshop: ToS accept | ☐ User clicks | NEIN |
| S3.4 | Falls Workshop: Preview-Image wählen | ☐ User picks file | NEIN |
| S3.5 | Falls Workshop: Tags bestätigen (Agent schlägt 3-5 vor) | ☐ User confirms | Half-auto (proposal) |
| S3.6 | Falls Workshop: Visibility wählen | ☐ User picks (Public/Friends/Private) | NEIN |
| S3.7 | **Creative Judgment Pass**: User spielt 60s im Workbench/Editor, bewertet "Fun" + "Atmosphere" + "Balance" subjektiv | ☐ User plays + rates 1-5 each | NEIN (judgment) |
| S3.8 | User-Feedback flows zurück in narrative.json (via Mac → Sprint S1 again if changes wanted) | ☐ User types feedback in chat | Half-auto |
| S3.9 | Push final approval as snapshot | — | Auto |

**Irreducible total: ~6 clicks first-time, ~3 per subsequent publish + 1 creative pass.**

---

## Wrapper-Prompt Pattern

Each Stage hat einen wrapper-prompt der User in den PC-Chat pastet. Pattern aus
sprint-phase2-3-closeout extended:

1. Read PROJECT_STATE_<DATE>.md
2. Read RELAY_PROTOCOL.md + PC_AGENT_BRIEF.md + CHEATSHEET-PC.md
3. Read THIS sprint plan
4. Execute Stages 0-N strict per plan
5. Sub-agent fleet aktiv (logger always-on + dep-installer pre-flight + ui-tester for GUI + auditor pre-push + loop-detector + bug-fixer)
6. Escalate-to-Mac if conditions met
7. Final paper at end
8. Two-Phase Reception

---

## Stage-Sequence Logic

```
Phase: CS running
   ↓
S1 sprint (3-4h headless, foundation work)
   ↓
Phase: CS done, user steps away
   ↓
S2 sprint (~30 min autonomous game test)
   ↓
Phase: User comes back to PC
   ↓
S3 sprint (~15 min creative judgment + Workshop gates)
   ↓
Loop closed: production-ready system
```

S1 + S2 + S3 sequential, but S1 + S2 can also be parallel (S1 Mac-only, S2 PC-only) wenn user gleichzeitig CS spielt UND PC frei lässt — unwahrscheinlich aber möglich.

---

## Sources

- Stage 1 research: agent_a1e7eb6750b059b10 (89s runtime, 13 tool uses)
- Stage 2 research: agent_abe10ed1bb6bbccf0 (145s runtime, 21 tool uses)
- Stage 3 research: agent_a341887c7d5db5b27 (64s runtime, 7 tool uses)
- All cite-able URLs preserved in agent outputs
- Cross-referenced research/01, 06, 07, 08, 09
