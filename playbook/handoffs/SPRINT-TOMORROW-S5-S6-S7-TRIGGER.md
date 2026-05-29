# Sprint Trigger — Tomorrow's Full Day S5→S6→S7 (Sonnet 4.6 optimized)

> Single-paste prompt for PC Claude Code (Sonnet 4.6 default).
> Includes iteration-loops + real Task() spawns where they matter + explicit pause-to-Opus triggers.
> ~7-9h total. User-present for Stages A + D. Autonomous for B + C + E.

---

## How to use

1. Wake up, coffee, sit at PC
2. Open PC Claude Code, select **Sonnet 4.6** model (left bottom)
3. Verify: `git pull --rebase` runs clean
4. Paste the **TRIGGER PROMPT** below in one go
5. Confirm Phase A bestätigung when asked
6. Coach via Mac-chat when prompted ("PC ready, los")
7. Step away for B + C (autonomous, ~4h)
8. Come back for Stage D ingame tests
9. Sprint pushes final paper, you tag the day

---

## TRIGGER PROMPT (copy from `╔══` to `╚══`, paste in PC chat)

```
╔══════════════════════════════════════════════════════════════════════════════
║ SPRINT TRIGGER — FULL DAY S5+S6+S7
║ Model: Sonnet 4.6 default. Escalate to Mac-Opus via git push + chat-pause
║         on the explicit triggers listed below.
║ Repo: C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
║ Duration: ~7-9h total. User-present Stages A + D. Autonomous B + C + E.
║══════════════════════════════════════════════════════════════════════════════

You are PC-Executor for a 5-stage full-day sprint closing S5 + polishing S6 +
laying S7 foundation. You will NOT operate the aspirational 9-named-agent fleet
from prior sprints — postmortem proved it was journaling, not delegation.
Instead: ONE orchestrator (you) with explicit branch/return folding, plus
REAL Task() spawns only where postmortem proved they pay (parallelizable work).

CRITICAL READ-ORDER (do this first, ~5 min):
1. playbook/handoffs/POSTMORTEM-AND-LESSONS.md
   - 5 failures + 10 patterns to adopt + what worked
   - Failures #1 (validate-vs-live), #3 (classifier blocks installs), #4 (module
     activation), #5 (file-watcher channel) are the ground-truth landmines
2. playbook/handoffs/MANUAL-GATES-CHECKLIST.md
   - P1 (S5 close), P2 (plugin pattern fix), P4 (Workshop optional)
3. PC_AGENT_BRIEF.md (your role + paths)
4. playbook/CHEATSHEET-PC.md (empirical PC knowledge — paths, gotchas)
5. pc-requirements.toml (ALL deps pre-declared — do NOT install mid-sprint)
6. workbench-plugin/AI_GeneratePlugin.c (current S5 plugin — review structure)

NON-NEGOTIABLE PATTERNS (postmortem-derived):

A. COMPILE-TWICE GATE
   - `-validate=PC -wbSilent -exitAfterInit` = fast smoke filter ONLY
   - Live gate = `-wbmodule=WorldEditor -plugin=X -autoclose=1` writing
     compile-errors.json. Sprint READY only when BOTH pass.

B. DOCUMENTED MODULE ACTIVATION
   - Plugin must use `[WorkbenchToolAttribute(name="X", category="ELOS",
     wbModules:{"WorldEditor"})]` AND `override void RunCommandline()`
   - Launcher must use `-wbmodule=WorldEditor -plugin=X -autoclose=1` CLI
   - Runtime `Workbench.GetModule(WorldEditor)` lookup = DEPRECATED pattern,
     refuse to write code that relies on it

C. NO MID-SPRINT INSTALLS
   - Every dep is in pc-requirements.toml already
   - If you encounter a missing tool: STOP, escalate to Mac-Opus, do NOT try
     winget/pip — classifier will block

D. REAL Task() ONLY FOR PARALLELIZABLE WORK
   - STAGE C ONLY uses real Task() spawns: 3 parallel agents scanning Bohemia
     samples for GameMaster API patterns. Isolated context = correct use case.
   - All other "agents" = you with branch/return markers, honest about it
   - Test of realness: did the spawn use the Task tool with isolated context?
     If not, it is a persona not an agent. Do not call it a fleet.

E. PRM-STYLE MID-TRAJECTORY SCORING
   - After each significant action: rate 0-100 vs current stage target
   - Log score to STATE.json each turn
   - 2 consecutive drops → BREAK current branch, escalate
   - Source: arxiv.org/pdf/2509.02360 (+10.6 pp SWE-bench Verified)

F. PAUSE-TO-MAC-OPUS TRIGGERS (write blocker, git push, chat-pause)
   - 3× retry exhausted on any step
   - Validate-vs-live discrepancy (live errors but headless clean)
   - WorldEditor module returns null DESPITE -wbmodule=WorldEditor flag
   - Novel error class not in research/EMPIRICAL.md
   - Token budget >800k
   - User-present stage user reports unexpected symptom
   - "I don't know what to do next" feeling

═══════════════════════════════════════════════════════════════════════════════
SPRINT STAGES (A → E, in order)
═══════════════════════════════════════════════════════════════════════════════

STAGE A — S5 CLOSE (user-present, ~1-2h)
─────────────────────────────────────────
Trigger: Phase A confirm with user "User AT PC, ready, willing to coach"

Sub-tasks:
A.1  Pull git, check STATE.json, read last reflection
A.2  Inspect workbench-plugin/AI_GeneratePlugin.c — current pattern
A.3  Decision gate: try Option A (current plugin as-is via menu) OR
     directly Option B (refactor to documented WorkbenchToolAttribute
     pattern + RunCommandline + CLI launch)
     - Recommend Option B per postmortem Failure #4
     - If user says "try A first" — honor 5 min budget, fall back to B
A.4  If Option B: refactor plugin
     - [WorkbenchToolAttribute(name="AI Generate Mission",
        category="ELOS", wbModules:{"WorldEditor"})]
     - override void RunCommandline()
     - Read GetCmdLine(), parse `input=X output=Y`
     - WorldEditor module guaranteed active when CLI flag set
     - Write outbox.json with success + applied + errors
A.5  Compile-twice gate:
     1. validate smoke (60s)
     2. live RunCommandline launch with test spec.json
A.6  Coach user through CLI launch:
     cd to mission folder
     ArmaReforgerWorkbenchSteam.exe -wbmodule=WorldEditor
       -plugin=AI_GeneratePlugin -autoclose=1 -- input=spec.json
       output=outbox.json
A.7  Verify: outbox.json shows success AND user reports viewport visibly
     changed (fog dichter). Both required.
A.8  Snapshot via Mac /snapshot S5-CLOSED-live-verified
A.9  Commit. Stage A done.

Stage A completion criteria (ALL true):
✓ Plugin uses WorkbenchToolAttribute + RunCommandline
✓ CLI invocation produces outbox.json with success: true
✓ User reports viewport visibly changed
✓ Snapshot taken
✓ Commit pushed

STAGE B — S6 POLISH (autonomous, ~2h)
─────────────────────────────────────
Trigger: Stage A complete + user says "B autonomous go" OR user steps away

Sub-tasks (branch/return folding inside YOU):
B.1  Branch: PyWebView chat window
     - Replace scripts/chat-window/elos_chat.py (Tk → PyWebView)
     - HTML/CSS styled chat (use ELOS orange/dark theme from
       treatment/concept-treatment-S7-storyteller-vision.html)
     - Stream tokens as they arrive
     - Return: scripts/chat-window/elos_chat.py rewritten

B.2  Branch: Streaming SSE in bridge.py
     - Anthropic stream=True mode
     - Token-by-token write to chat history
     - Return: scripts/chat-window/bridge.py updated

B.3  Branch: Director Mode toggle in chat
     - UI toggle Design ↔ Director
     - Different system prompt per mode
     - Different file write target (spec.json vs runtime-spec.json)
     - Return: chat window has working toggle

B.4  Branch: Compile-twice gate test
     - Headless validate of plugin from Stage A
     - Live RunCommandline check
     - Both must pass
     - Return: green or blocker

B.5  Auditor REAL Task() spawn (separate context, pre-push):
     "Audit Stage B deliverables: do PyWebView, streaming, director mode
      work end-to-end? List any gaps with concrete reproduction steps."
     - Must use Task tool, not journaling
     - Verdict: allow_push or block_with_options

B.6  Commit + push if auditor green

Stage B completion criteria:
✓ PyWebView chat opens, accepts input, displays streaming response
✓ Director mode toggle works (verified via file-write target)
✓ Compile-twice gate passes for plugin
✓ Auditor (real Task) verdict: allow_push

STAGE C — S7 FOUNDATION (autonomous, ~2h, REAL multi-agent spawn here)
──────────────────────────────────────────────────────────────────────
Trigger: Stage B complete OR escalation from B resolved

Sub-tasks:
C.1  REAL parallel Task() spawn (this is the postmortem-correct use case):
     3 agents in parallel:
       Agent 1: Scan github.com/BohemiaInteractive/Arma-Reforger-Samples for
                GameMaster references (SCR_BaseGameMaster, SCR_GameModeBase)
       Agent 2: Scan github.com/BohemiaInteractive/Arma-Reforger-Script-Diff
                for runtime SCR_* method signatures (AISpawnPoint, FactionMgr)
       Agent 3: Scan community samples (acemod/docker-reforger, scalespeeder)
                for production GameMaster server config patterns
     Each agent returns:
       - confirmed_apis: [method signatures]
       - reference_files: [paths in repo]
       - gotchas: [doc-says-X-but-empirically-Y]
     Output: research/14-game-master-architecture.md

C.2  Branch: ELOS_GameMasterPlugin.c skeleton
     - File location: workbench-plugin/ELOS_GameMasterPlugin.c
     - But this is GAME-side runtime, not Workbench-side
     - extends SCR_BaseGameMaster OR is a game-mode component
     - Real method signatures from C.1
     - Ops: spawn_wave, despawn_entity, weather_change, schedule_event
     - TODO markers for unimplemented (don't fake completeness)
     - Return: plugin file compiles via headless validate

C.3  Branch: Game-side spec.json schema (runtime-spec.json)
     - Distinct from design-time spec.json
     - playbook/SCHEMA_MAPPING_GM.md natural-lang → runtime ops

C.4  Branch: gm-runtime-bridge.py
     - scripts/chat-window/gm-runtime-bridge.py
     - Polls runtime-spec.json (game-side has no OnUpdate either)
     - Logs runtime latency separately from design-time

C.5  Compile-twice gate on plugin

C.6  REAL Task() auditor pre-push:
     "Audit Stage C: does ELOS_GameMasterPlugin.c compile? Are real SCR_*
      method signatures used (not pseudocode)? Are TODO markers honest?"

C.7  Commit + push

Stage C completion criteria:
✓ research/14-game-master-architecture.md exists with cited SCR_* APIs
✓ ELOS_GameMasterPlugin.c compiles via validate (smoke)
✓ Uses real method signatures from sample-scan, NOT pseudocode
✓ TODO markers honest about unimplemented parts
✓ gm-runtime-bridge.py created
✓ Auditor verdict: allow_push

ESCALATE TO MAC-OPUS IF:
- C.1 parallel agents can't find Bohemia samples (404, repo moved)
- Plugin compile fails with novel error not in EMPIRICAL.md
- No clear runtime SCR_* method for one of the 5 ops

STAGE D — MANUAL INGAME TESTS (user-present, ~1-2h)
───────────────────────────────────────────────────
Trigger: Stage C complete + user says "D ingame go"

Sub-tasks:
D.1  Coach user through:
     1. Close Workbench
     2. Open Arma Reforger Game (NOT Workbench, the actual game)
     3. Steam Library → Reforger → Play
     4. Scenario list → ai_night-recon-everon (or whichever active mission)
     5. Start in Game Master mode (Coop/GM scenario type)
D.2  Coach: open elos_chat.py (PyWebView from Stage B), toggle to Director Mode
D.3  Coach test prompts (user types in chat, narrates result):
     - "spawn 3 OPFOR east of player"
     - "weather to storm in 30 seconds"
     - "spawn medic 50m north of player"
     - "increase enemy aggression"
     - "trigger ambush in 60 seconds"
D.4  User narrates: which worked, which didn't, what the symptom looked like
D.5  Document each result in logs/stage-d-ingame-test-results.json:
     - prompt
     - expected outcome
     - actual outcome
     - latency (eyeball ok)
     - failure mode if any
D.6  5 NL paraphrase test (S6 UX validation):
     - "fog dichter", "mach Nebel dichter", "more fog", "denser haze",
       "atmospheric thicker" — all should produce same diff
     - Document paraphrase robustness score 0/5 to 5/5
D.7  Update research/EMPIRICAL.md with any new disconfirmed-on-PC claims
     tagged [EMPIRICAL-DISCONFIRM 2026-05-31]

Stage D completion criteria:
✓ User has tested 5 GM prompts ingame
✓ Each result documented (pass/fail/partial)
✓ Paraphrase test ≥3/5 (some robustness)
✓ EMPIRICAL.md updated with findings

ESCALATE TO MAC-OPUS IF:
- 0/5 GM ops worked ingame (foundational issue)
- Game crashes on plugin load
- Plugin not found by Game Master (registration issue)

STAGE E — AUDIT + PUSH (autonomous, ~30 min)
────────────────────────────────────────────
Trigger: Stage D complete

Sub-tasks:
E.1  Final REAL Task() audit:
     "Read all commits from today's sprint. Read stage-d-ingame-test-results.
      Read EMPIRICAL.md updates. Produce honest day-audit:
      - Goal achievement (S5 closed? S6 polished? S7 foundation?)
      - What worked
      - What partial
      - What blocked
      - Token cost rough estimate
      - Next sprint suggestions
      Output: playbook/handoffs/DAY-AUDIT-2026-05-31.md"

E.2  Update STATE.json:
     - s5_mvp_complete: true (if Stage A criteria met)
     - s6_polish_complete: true/partial
     - s7_foundation_complete: true/partial
     - next_session_focus: "..."

E.3  Tag git: `git tag s5-s6-s7-mvp-2026-05-31`

E.4  Chat output to user:
     "Day sprint complete. S5: [status]. S6: [status]. S7: [status].
      Audit at playbook/handoffs/DAY-AUDIT-2026-05-31.md.
      Next session: [focus from E.2]."

═══════════════════════════════════════════════════════════════════════════════
ITERATION-LOOP PIPELINE (active throughout)
═══════════════════════════════════════════════════════════════════════════════

For each sub-task in any stage:

1. PLAN (1-3 sentences in your own context — visible thinking)
2. EXECUTE (tool call: bash, edit, write)
3. PRM-STYLE SCORE 0-100 vs sub-task target → log to STATE.json
4. CHECK score trend:
   - 2 consecutive drops → BREAK + escalate
   - Plateau at <70 for 3 turns → escalate
   - Score 90+ → continue
5. AUDITOR CHECK (real Task() spawn at end of each stage, NOT mid-stage):
   - Verdict: allow_push or block
   - If block: surface concrete reproducible options
6. COMMIT only if auditor green

Honest journaling (not theater):
- "Branch: <subtask>" before starting
- "Return: <result>" after finishing
- Use STATE.json branch_id field — orchestrator tracks branches by ID
- These are convention markers in YOUR context, not separate agents
- Be transparent in commit messages: "branch B.2 streaming SSE complete"

═══════════════════════════════════════════════════════════════════════════════
HARD GUARDS (non-negotiable)
═══════════════════════════════════════════════════════════════════════════════

- max_retries_per_step = 3
- same_error_class_dedup = 4 → escalate (OpenHands StuckDetector pattern)
- stage_time_budget = 2h default (A 2h, B 2h, C 2h, D 2h, E 30min)
- token_budget_total = 1.2M
- escalate_at_token = 900k
- DRY marker required for destructive ops (Remove-Item -Recurse,
  git reset --hard, anything that destroys state)
- NEVER automate against BattlEye-protected MP sessions
- NEVER install mid-sprint (manifest-only)
- NEVER use AHK SendKeys (postmortem Failure #5)
- NEVER claim a journaling pattern is a "sub-agent fleet"

═══════════════════════════════════════════════════════════════════════════════
START NOW
═══════════════════════════════════════════════════════════════════════════════

Two-Phase Reception:
Phase A: ⚙️ DO = user confirms:
   ☐ User AT PC for at least Stage A and Stage D
   ☐ pc-requirements.toml present and deps installed
   ☐ Mac-Opus reachable for escalation (Paul checks Mac chat occasionally)
   ☐ Sonnet 4.6 selected (you, current model)
   Ask user: "confirm Phase A items, when ready I start Stage A?"

Phase B: Verify no competing processes (cs2, ArmaReforgerSteam, ArmaReforgerServer,
         ArmaReforgerWorkbench) running

Phase C: Stages A → E

Phase D: Final paper + chat output

╚══════════════════════════════════════════════════════════════════════════════
```

---

## What this prompt does differently from prior sprints

| Postmortem failure | How this sprint fixes it |
|---|---|
| #1 validate-vs-live | Compile-twice gate built into every stage |
| #2 fleet theater | Real Task() ONLY in C.1 (parallel research) + auditors. Everything else = honest branch/return |
| #3 classifier blocks | pc-requirements.toml pre-declared, NO mid-sprint installs |
| #4 module activation | Plugin refactored to WorkbenchToolAttribute + RunCommandline + CLI |
| #5 SendKeys channel | Plugin re-triggered via CLI re-invocation, no AHK |

## What this prompt does NEW

- PRM-style mid-trajectory scoring (the "self-fixing gap" answer)
- Explicit pause-to-Opus triggers (not just retry-3-times-and-die)
- Real Task() spawn in C.1 (parallelizable scan of Bohemia samples = right use case)
- Honest journaling (no aspirational fleet naming)

## Cost estimate

- Sonnet 4.6 main loop: ~$15-25
- Real Task() spawns (C.1 × 3 agents, B.5/C.6/E.1 auditors × 3): ~$5-10
- Mac-Opus escalations (if any): ~$3-8
- **Total: ~$25-45** (vs all-Opus equivalent ~$150-300, savings ~80%)

## Pre-flight (heute Abend)

Before pasting tomorrow morning, run these (~10 min):

1. Mac chat: `"P5 go"` → I create pc-requirements.toml
2. Wait for commit
3. PC PowerShell:
   ```powershell
   cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
   git pull --rebase
   Get-Content pc-requirements.toml
   ```
4. Read the file, confirm all listed deps are installed via `winget list` / `pip list`
5. If anything missing: install NOW (you're at PC, no classifier issue)

Tomorrow morning: 1 paste, 1 confirm, sprint runs.
