# Sprint FINAL-S5-MAXED — One Sprint to S5 Live Editor

> Stand: 2026-05-21 · Model: Sonnet 4.6 (Computer Use steps + plugin work)
> Estimated runtime: 5-7h autonomous (user mostly absent)
> Goal: floating chat window + AI_GeneratePlugin + AHK file-watch = **S5 MVP live editor**
> Source: research/11 + research/12 + research/13 + MEGA-A actual outcomes

---

## What This Sprint REPLACES

| Old plan | Status | Reason |
|---|---|---|
| sprint-MEGA-A-S1S2-to-S5-ready.md | ⛔ deprecated | Failed at Steam Server install (no Computer Use) |
| sprint-MEGA-B-S3-S5-live-editor.md | ⛔ deprecated | Pre-PIVOT design, didn't include chat window |
| sprint-S1-PLUS-S2-combined.md | ⛔ deprecated | Same Steam blocker |
| sprint-PIVOT-computer-use-direct-to-S5.md | ⛔ superseded | Pre-research/13 (had wrong "embedded chat" assumption) |
| **sprint-FINAL-S5-MAXED.md** ⭐ | ✅ **USE THIS** | All research integrated, Option B architecture |

Old plans archived to `playbook/handoffs/_deprecated/` for reference only.

---

## End-State: S5 MVP

**What works after this sprint:**

```
┌─────────────────────┐         ┌──────────────────────────┐
│  ELOS Chat Window   │         │  Reforger Workbench      │
│  (floating right)   │ ←files→ │  + AI_GeneratePlugin     │
│  Python/Tk · 520px  │         │  + 3D Viewport (live)    │
└─────────────────────┘         └──────────────────────────┘

User: "fog dichter" → 1-3 sec later: fog dichter im 3D viewport
```

**Falsifiable success criteria (sc-1 to sc-12):**

1. ArmaReforgerServer.exe installed (was MEGA-A blocker)
2. AI_GeneratePlugin.c compiles + loads in Workbench (sample-verify-equivalent)
3. Plugin handles 5 op types (attribute_edit, entity_create, entity_delete, entity_move, batch)
4. Python ELOS chat window launches + Anthropic API call succeeds
5. bridge writes spec.json → AHK detects → Workbench reload-hotkey fires
6. Plugin reads spec.json → executes WorldEditorAPI calls → writes outbox.json
7. ONE end-to-end revision proven: type "fog dichter" → see fog dichter
8. 5 different revision types proven: weather / time / entity-add / entity-delete / batch
9. Latency P50 ≤ 3s, P95 ≤ 6s
10. 10 sequential revisions, 0 manual interventions
11. Final paper with cost breakdown + reflection
12. Code skeletons replaced with functional versions

---

<sprint>

<context>
  <goal>
    Achieve S5 MVP in ONE autonomous sprint. Use Anthropic Computer Use for Steam UI
    automation (install Server EXE), fill plugin TODOs with real Enforce Script logic,
    build floating chat window (Tk + bridge.py), wire AHK file-watch, prove end-to-end.
  </goal>

  <prerequisites>
    - ANTHROPIC_API_KEY set persistently in user env
    - Steam logged in (no 2FA mid-sprint — disable mobile-confirm OR mark machine trusted)
    - Workbench installed (already verified MEGA-A)
    - Junctions in place (already verified MEGA-A)
    - User available for 1-2 UAC clicks in first 30 min (rare but possible)
  </prerequisites>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <model>claude-sonnet-4-6</model>
    <cu_beta>computer-use-2025-11-24</cu_beta>
    <cu_tool_type>computer_20251124</cu_tool_type>
    <profile_elos>%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\profile\ELOS</profile_elos>
  </env>
</context>

---

## STAGE F.0 — Pre-Flight + Tooling (~20 min)

<stage id="F.0" name="preflight">
  <action>
    Phase A (user confirms):
    ☐ CS aus
    ☐ ANTHROPIC_API_KEY env-var set ([System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User"))
    ☐ Steam logged in (no 2FA expected)
    ☐ User available for ~30 min UAC-click window

    Phase B verify + bootstrap tools:
    ```powershell
    # Install missing deps (idempotent)
    winget install Python.Python.3.12 -e --silent --accept-package-agreements
    winget install AutoHotkey.AutoHotkey -e --silent --accept-package-agreements
    winget install GitHub.cli -e --silent --accept-package-agreements

    # Python packages
    python -m pip install --user --upgrade anthropic pyautogui mss pygetwindow pillow

    # Verify
    python -c "import anthropic, pyautogui, mss, pygetwindow, PIL; print('OK')"
    Test-Path "C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"
    ```

    Create profile dir:
    ```powershell
    New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\profile\ELOS" -Force
    ```

    Update tasks/STATE.json: turn_id="FINAL-S5-MAXED", phase=PHASE_C_EXEC, owner=pc.
    Spawn logger (always-on full session).
  </action>

  <done_when>
    - All Python deps importable
    - AutoHotkey v2 installed
    - ELOS profile dir created
    - STATE.json updated
  </done_when>

  <on_failure>
    - UAC needed for winget install → user 1-click (or already done from MEGA-A)
    - pip offline → check network, retry
    - AutoHotkey path differs → adapt scripts/computer-use/run_task.py invocation
  </on_failure>
</stage>

---

## STAGE F.1 — Computer Use Loop Smoke Test (~10 min)

<stage id="F.1" name="cu_smoke_test">
  <action>
    Skeletons exist in repo (Mac-pre-staged). Verify Computer Use roundtrip works:

    ```powershell
    cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
    python scripts\computer-use\windows_computer.py  # smoke test prints screenshot info

    # Real CU loop demo:
    python scripts\computer-use\run_task.py "Open Notepad, type 'ELOS S5 test', wait 2 seconds, close without saving"
    ```

    Watch logs/computer-use/cu-*.jsonl — expect ~10-20 turns total.
  </action>

  <done_when>
    - windows_computer.py smoke test prints native res + 5 window titles
    - run_task.py completes Notepad demo with exit code 0
    - Logged to logs/computer-use/cu-<TS>.jsonl
  </done_when>

  <on_failure>
    - API call fails → check ANTHROPIC_API_KEY env
    - pyautogui blocked → user grants screen-record permission (rare on Windows)
    - Screenshot black → primary monitor issue, try secondary
  </on_failure>
</stage>

---

## STAGE F.2 — Install ArmaReforgerServer via Computer Use (~15 min)

<stage id="F.2" name="install_server">
  <action>
    THE thing that killed MEGA-A. Now autonomous.

    ```powershell
    python scripts\computer-use\run_task.py @"
Install 'Arma Reforger Server' tool via Steam Library.

Steps:
1. Find Steam window (already running). Bring to front via activate_window 'Steam'.
2. Click Library tab in left sidebar.
3. Filter for Tools (left dropdown if needed).
4. Search 'Arma Reforger Server' in the filter box.
5. Click the entry. Click Install button.
6. Steam install dialog: accept defaults. Click Next/Install.
7. Wait for download (~200 MB, may take 5-10 min). Take screenshot every 30s.
8. When 'Play'/'Launch' button appears: done.
9. Verify install: Test-Path 'C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Server\ArmaReforgerServer.exe'

Constraints:
- If UAC prompt: STOP, escalate (cannot bypass)
- If Steam 2FA: STOP, escalate (user phone)
- Max 60 turns
"@
    ```
  </action>

  <done_when>
    - ArmaReforgerServer.exe present in expected path
    - logs/computer-use/cu-<TS>.jsonl saved
  </done_when>

  <on_failure>
    - UAC blocks → escalate (user 1-click fix)
    - 2FA prompt → escalate (phone tap)
    - Steam offline → wait + retry once
    - Stuck >60 turns → loop-detector fires, escalate with screenshot
  </on_failure>
</stage>

---

## STAGE F.3 — Fill AI_GeneratePlugin.c TODOs (~2-3h)

<stage id="F.3" name="plugin_implementation">
  <action>
    workbench-plugin/AI_GeneratePlugin.c has 2 TODOs from MEGA-A:
    1. JSON parsing via JsonSerializer.Deserialize
    2. Ops loop dispatch

    Implement using **3-layer iteration loop** per research/11:

    INNER (per op-type, ~sec):
    1. Code op handler (e.g. attribute_edit)
    2. Validate via Workbench-Diag CLI: `ArmaReforgerWorkbenchSteamDiag.exe -gproj X -validate -wbSilent -exitAfterInit`
    3. Check console.log for 0 fatals + 0 errors
    4. Write test ai-spec.json with this op
    5. Invoke plugin headless: `-gproj X -wbModule=WorldEditor -plugin=AI_GeneratePlugin`
    6. Parse plugin log for OK:/ERR:
    7. diff-verifier: compare resulting .layer file vs golden
    8. PASS → next op. FAIL → bug-fixer with 3 options.
    9. Max 15 inner iterations per op type

    MIDDLE (per op-type regression, ~min):
    - 5 test cases per op type (variations of params)
    - All green → commit + move to next op

    OUTER (full coverage, ~hr):
    - All 5 op types × 10 = 50 test revisions
    - ≥95% pass = saturation

    Op-Types to implement (from research/11 + SCHEMA_MAPPING.md):

    ```c
    // Pseudocode of the 5 ops the plugin must handle
    void ApplyOp(SCR_AIOp op) {
      switch (op.op_type) {
        case "attribute_edit":
          IEntity entity = ResolveTarget(op.target);  // e.g. "weatherManager"
          SetVariableValue(entity, op.field, op.value);
          break;
        case "entity_create":
          IEntity created = CreateEntity(op.class_name, op.prefab_guid, op.coords);
          ApplyProps(created, op.props);
          break;
        case "entity_delete":
          IEntity target = FindEntityByName(op.target);
          DeleteEntities([target]);
          break;
        case "entity_move":
          IEntity moved = FindEntityByName(op.target);
          SetEntityTransform(moved, op.new_coords);
          break;
        case "batch":
          foreach (SCR_AIOp sub : op.sub_ops) ApplyOp(sub);
          break;
      }
    }
    ```

    Use Bohemia samples for exact API:
    - SampleWorldEditorPlugin.c → CreateEntity, BeginEntityAction
    - Script-Diff WorldEditorAPI.c → SetVariableValue, DeleteEntities
    - DiscordRP → FileIO patterns

    Sub-agents:
    - enforce-researcher when API unclear (consults BI wiki + Script-Diff)
    - bug-fixer on FAIL with always-3-options
    - diff-verifier for .layer comparison
    - loop-detector on retry
  </action>

  <done_when>
    - All 5 op-types green in golden tests
    - 116/116 backend tests still PASS
    - Plugin compiles via -validate in CLI
    - Commit pushed
  </done_when>

  <on_failure>
    - Bohemia API method missing → enforce-researcher web search + BI forum
    - 4× same error-class → researcher consultation
    - Op-type fundamentally not supported in Enforce → document as known-limit, skip + adjust scope
  </on_failure>
</stage>

---

## STAGE F.4 — Verify Plugin Loads in Workbench (~10 min)

<stage id="F.4" name="plugin_verify">
  <action>
    Computer Use task — open Workbench, verify plugin entry appears:

    ```powershell
    python scripts\computer-use\run_task.py @"
Verify AI_GeneratePlugin compiles + loads in Workbench.

Steps:
1. Launch Workbench-Diag with our addon:
   Start-Process 'C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe' -ArgumentList '-gproj=C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios\missions\night-recon-everon\output\addon.gproj'
2. Wait for Workbench to fully load (~30s, menu bar visible).
3. Click 'Plugins' menu in top menu bar.
4. Look for 'ELOS' submenu OR 'AI_GeneratePlugin' entry.
5. If present: take screenshot as evidence. PASS.
6. If 'Plugins' menu empty: FAIL — log error.
7. Close Workbench (Alt+F4 or window close button).

Max 30 turns.
"@
    ```
  </action>

  <done_when>
    - Plugin entry appears in Plugins menu (screenshot evidence)
    - Workbench closed cleanly
  </done_when>

  <on_failure>
    - Plugin not in menu → check addon.gproj attribute syntax, retry compile
    - Workbench crash on launch → log dump, escalate
  </on_failure>
</stage>

---

## STAGE F.5 — Wire AHK File-Watcher (~10 min)

<stage id="F.5" name="ahk_watcher">
  <action>
    Skeleton at scripts/chat-window/elos-reload.ahk. Verify:

    ```powershell
    # Start AHK watcher as background process
    Start-Process "C:\Program Files\AutoHotkey\v2\AutoHotkey.exe" `
      -ArgumentList "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios\scripts\chat-window\elos-reload.ahk"

    # Verify it's running (tray icon)
    Get-Process AutoHotkey -ErrorAction SilentlyContinue
    ```

    Test the watch trigger:
    1. Manually create dummy spec.json:
       `'{"test":true}' | Out-File "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\profile\ELOS\spec.json"`
    2. Verify AHK detected change (TrayTip should fire)
    3. If Workbench open: Ctrl+Shift+R should fire automatically
  </action>

  <done_when>
    - AHK process running
    - File-write triggers TrayTip
    - With Workbench open: hotkey reaches Workbench window
  </done_when>

  <on_failure>
    - AHK script syntax error → check version (v2 required, not v1)
    - Hotkey doesn't reach Workbench → activate_window via Computer Use, then SendKeys
  </on_failure>
</stage>

---

## STAGE F.6 — First End-to-End Live Edit Test (~30 min)

<stage id="F.6" name="first_live_edit">
  <action>
    THE moment of truth. Setup:
    1. Workbench open with night-recon-everon mission
    2. AHK watcher running
    3. ELOS chat window launches:
       ```powershell
       python scripts\chat-window\elos_chat.py
       ```

    Test sequence:
    1. Type in chat window: "fog dichter"
    2. Chat window writes spec.json with fog_density patch
    3. AHK detects → fires Ctrl+Shift+R into Workbench
    4. Plugin runs, reads spec, applies SetVariableValue(weatherManager, "m_fFogDensity", 0.7)
    5. Plugin writes outbox.json with "OK"
    6. Chat window reads outbox, displays applied confirmation + latency
    7. Take Computer Use screenshot of Workbench viewport — verify fog visibly denser

    Measure: P50 + P95 latency over 5 sequential revisions.
  </action>

  <done_when>
    - 1 revision applied + visible in viewport
    - Latency measured: P50 ≤ 3s
    - 5 sequential revisions tested (different op types)
    - All produce visible change
    - logs/first-live-edit-test.json saved
  </done_when>

  <on_failure>
    - Chat window can't reach Claude API → API key check
    - spec.json written but plugin doesn't run → AHK reach check
    - Plugin runs but no visual change → WorldEditorAPI call wrong, debug
    - Latency >10s → optimize bridge.py prompt caching
  </on_failure>
</stage>

---

## STAGE F.7 — 10-Revision Reliability Test (~30 min)

<stage id="F.7" name="reliability">
  <action>
    Inner loop validation per research/11 sc-B4:
    - 10 sequential revisions, 0 manual interventions
    - Mix of op types: 3 attribute_edit, 3 entity_create, 2 entity_delete, 2 batch
    - Each revision: write to chat → wait response → verify visual

    If a revision fails:
    - Capture error
    - Bug-fixer with 3 options
    - Apply fix, retry
    - Max 3 retries per revision

    If 5+ revisions fail → escalate (something fundamental broken).

    Track:
    - Pass rate (target ≥95%)
    - Median latency
    - Error categories
  </action>

  <done_when>
    - 10/10 (or ≥9.5/10 with 1 retry) pass rate
    - No Workbench crashes
    - logs/reliability-test.json with full stats
  </done_when>

  <on_failure>
    - <80% pass rate → architectural issue, escalate
    - Plugin crashes Workbench → memory/leak issue, debug
  </on_failure>
</stage>

---

## STAGE F.8 — Phase 7 (Game Master) Foundation Prep (~60-90 min)

> **NEW: Added mid-sprint via git pull.** PC sees this stage after F.7 completes.
> Goal: do EVERYTHING for Phase 7 (Game Master live-direction integration) that
> does NOT require user-at-PC. Hand off a fully-spec'd ready-to-finalize roadmap
> for when user returns this week.

<stage id="F.8" name="phase7_foundation">

  <action>

    ### F.8.1 — Research Game Master Plugin Architecture (~15 min)

    Spawn `enforce-researcher` sub-agent with mission:

    "Research how to build a runtime LLM-controlled plugin for Arma Reforger Game Master
    (in-game scenario director, NOT Workbench editor). Investigate:

    1. SCR_BaseGameMaster + related Game Master scripts in
       $env:USERPROFILE\Documents\GitHub\Arma-Reforger-Script-Diff\scripts\Game\GameMode\
       (or equivalent paths in Script-Diff repo)

    2. Game-side runtime API surface:
       - SCR_AISpawnPoint runtime control
       - SCR_FactionManager (live faction switches)
       - SCR_GameModeBase scenario state
       - SCR_BaseTriggerEntity (live trigger creation)
       - Weather/Time live changes via runtime
       - Player tracking + AI behavior modification

    3. Game Master UI extension points:
       - Can we add custom Game Master toolbar entry?
       - Can we open custom GM dialog from script?
       - Does Game Master have a 'tool palette' equivalent we can extend?

    4. Networking architecture:
       - Is Game Master available in single-player + multiplayer?
       - How does authority work for runtime spawns (server-only ops)?
       - Can a client-side script trigger server-side spawns?

    5. File I/O at runtime — does game-side FileIO work like Workbench-side?
       (Probably yes — same Enforce Script runtime)

    Output: research/14-game-master-architecture.md with:
    - Confirmed API methods + signatures
    - Plugin/script entry points
    - File-watch architecture feasibility for runtime spec.json
    - Realistic dev-time estimate to functional Game Master plugin
    - List of hard limits requiring user-in-game
    - Sources (BI wiki URLs, Script-Diff file paths)

    Cite Bohemia wiki:
    - https://community.bistudio.com/wiki/Arma_Reforger:Game_Master
    - https://community.bistudio.com/wiki/Arma_Reforger:Scripting:_Game_Mode
    - Plus actual Script-Diff repo browsing"

    ### F.8.2 — Game Master Plugin Skeleton (~20 min)

    Create workbench-plugin/ELOS_GameMasterPlugin.c:

    ```c
    // ELOS_GameMasterPlugin.c — Runtime LLM-controlled scenario director
    //
    // GOAL: Live-edit a running mission via file-watch on runtime-spec.json
    //
    // ARCHITECTURE:
    //   - Mounted as Game Mode component (NOT Workbench plugin)
    //   - Reads runtime-spec.json on demand (file-watch via polling OR explicit trigger)
    //   - Applies ops via SCR_* runtime methods
    //   - Writes runtime-outbox.json with status
    //
    // OPS SUPPORTED (Phase 7 MVP):
    //   - spawn_wave (SCR_AISpawnPoint runtime-spawn)
    //   - despawn_entity (find by ID, delete)
    //   - modify_faction (SCR_FactionManager)
    //   - schedule_event (delayed trigger)
    //   - weather_change (runtime weather transition)
    //   - difficulty_modifier (AI behavior aggressiveness)
    //
    // INSTALLATION:
    //   - Drop into addon's Scripts/Game/GameMode/Components/
    //   - Add to scenario's gameMode entity as component
    //   - Game Master must be enabled for the scenario
    ```

    Use Bohemia Script-Diff for REAL method signatures from
    SCR_BaseGameMaster, SCR_GameModeBase, SCR_AISpawnPoint. Mark TODOs for
    unimplemented logic. File must be syntax-clean.

    ### F.8.3 — Game Master Schema Mapping (~15 min)

    Create playbook/SCHEMA_MAPPING_GM.md — natural-language prompts → runtime ops:

    | Field | Live Op | Example |
    |---|---|---|
    | spawn enemy wave at coords | `spawn_wave` | "spawn OPFOR squad south at hill" → SCR_AIGroup.Spawn(coords, faction) |
    | despawn entity | `despawn_entity` | "kill that MG team" → entity.Delete() |
    | change weather mid-play | `weather_change` | "storm in 2 min" → schedule weatherManager preset switch |
    | trigger event | `trigger_event` | "ambush triggers when squad enters zone" → SCR_BaseTriggerEntity setup |
    | difficulty | `difficulty_modifier` | "make AI more aggressive" → SCR_AIBehavior.SetAggressiveness |

    Distinct from playbook/SCHEMA_MAPPING.md (design-time) — runtime ops have
    different constraints (authority, latency, side-effects on running players).

    ### F.8.4 — Extend elos_chat.py with Director Mode (~20 min)

    Update scripts/chat-window/elos_chat.py:
    - Add toggle: Design Mode (current, default) ↔ Director Mode (new)
    - Director Mode reads runtime-spec.json (different file from spec.json)
    - Director Mode uses different system prompt (runtime ops, urgency, player-aware)
    - UI difference: orange accent ↔ red accent for Director Mode (matches S7 treatment)
    - Mission-context loader: in Director Mode, ALSO load current game-state if
      runtime-state.json present

    Test: Director Mode toggle works, writes correct file, doesn't break Design Mode.

    ### F.8.5 — Game-Side File-Watch Helper (~15 min)

    Create scripts/chat-window/gm-runtime-bridge.py:
    - Polls runtime-spec.json (since game-side Enforce Script also lacks OnUpdate)
    - When new spec detected: writes a "trigger" file the GM plugin polls
    - Reads runtime-outbox.json for plugin responses
    - Logs latency for runtime ops (likely higher than design-time)

    NOTE: this is the runtime equivalent of the AHK Ctrl+Shift+R hack — but
    in-game we can't send keystrokes, so we need a poll-based protocol.
    Document realistic latency target: 2-5 sec for runtime ops (acceptable
    since they're not as visually-immediate as design-time edits).

    ### F.8.6 — Phase 7 Roadmap + Audit Checklist (~10 min)

    Create playbook/PHASE_7_GAME_MASTER_ROADMAP.md with:

    **Foundation (this F.8 work) — Done:**
    - [x] Game Master architecture research
    - [x] ELOS_GameMasterPlugin.c skeleton with real SCR_* method names
    - [x] Schema mapping for runtime ops
    - [x] Director Mode in chat window
    - [x] gm-runtime-bridge.py file-watch

    **Manual Steps (require user at PC) — Pending:**
    - [ ] Test ELOS_GameMasterPlugin.c compiles in Workbench (load addon, check Plugins menu)
    - [ ] Place plugin component in scenario's gameMode entity (Workbench edit)
    - [ ] Launch mission with Game Master mode enabled (in-game UI)
    - [ ] Verify Director Mode chat → file-watch → plugin → runtime op cycle
    - [ ] First live-spawn test: "spawn 3 OPFOR south" → see entities appear in-game
    - [ ] Reliability test: 10 runtime ops, ≤95% success
    - [ ] Multiplayer test if applicable (authority handling)

    **Audit Items for user-when-returns:**
    - Review research/14 findings — any architecture surprises?
    - Validate ELOS_GameMasterPlugin.c TODO list — anything missed?
    - Test compile path manually
    - Decide: SP-first or MP-first for testing?

    **Estimated dev-time after manual gates resolved:**
    - 2-3 dev-days for fully functional Game Master plugin
    - Plus 1-2 days for in-game UI polish

    ### F.8.7 — Update STATE.json + Commit

    ```powershell
    cd $repo
    git add workbench-plugin/ELOS_GameMasterPlugin.c
    git add playbook/SCHEMA_MAPPING_GM.md
    git add playbook/PHASE_7_GAME_MASTER_ROADMAP.md
    git add research/14-game-master-architecture.md
    git add scripts/chat-window/elos_chat.py
    git add scripts/chat-window/gm-runtime-bridge.py
    git commit -m "feat: Phase 7 (Game Master) foundation — ready for user finalization"
    git push
    ```

    Update tasks/STATE.json:
    ```json
    {
      "phase_5_mvp_complete": true,
      "phase_7_foundation_complete": true,
      "phase_7_status": "awaiting_user_for_in_game_validation",
      "next_action_user": "review PHASE_7_GAME_MASTER_ROADMAP.md when at PC"
    }
    ```
  </action>

  <done_when>
    - research/14-game-master-architecture.md exists with cited findings
    - workbench-plugin/ELOS_GameMasterPlugin.c skeleton with real SCR_* API
    - playbook/SCHEMA_MAPPING_GM.md complete
    - scripts/chat-window/elos_chat.py extended with Director Mode toggle
    - scripts/chat-window/gm-runtime-bridge.py created
    - playbook/PHASE_7_GAME_MASTER_ROADMAP.md with done/pending/audit sections
    - STATE.json updated
    - All committed + pushed
  </done_when>

  <on_failure>
    - If Bohemia Script-Diff doesn't have Game Master internals → document gaps
      in research/14, mark architecture as "needs further research with user"
    - If extending elos_chat.py breaks Design Mode → revert + ship as separate file
      (elos_chat_director.py)
    - Skip rather than block — F.8 is BONUS work, S5 MVP from F.0-F.FINAL is the
      hard goal
  </on_failure>

</stage>

---

## STAGE F.FINAL — Consolidated Final Paper (~15 min)

<stage id="F.FINAL" name="final_paper">
  <action>
    Generate playbook/handoffs/final-paper-FINAL-S5-MAXED-<TS>.md:
    - Goal Achievement Matrix (sc-1 to sc-12 for S5 MVP)
    - Stage outcomes table (F.0 → F.8 inclusive)
    - Computer Use task statistics (turns/cost per task)
    - Plugin op-type matrix (which work, which have issues)
    - Latency measurements: P50, P95, distribution histogram (ASCII)
    - Reliability test results (10/10 or whatever)
    - **Phase 7 Foundation Status (from F.8):**
      - Game Master architecture research complete
      - Plugin skeleton ready with real SCR_* API
      - Director Mode in chat window
      - Roadmap doc with done/pending/audit sections
      - Pending: user-at-PC validation steps (5-7 items)
    - Cost breakdown (Sonnet + Computer Use overhead, broken down per stage)
    - Known limitations (S5 + Phase 7)
    - Future work (Phase 7 finalization, Phase 8 replay analysis, Phase 9 voice)
    - Next action (for user when back):
      1. Launch elos_chat.py + AHK + Workbench → use S5 MVP daily
      2. Read playbook/PHASE_7_GAME_MASTER_ROADMAP.md
      3. Run the 5-7 pending Phase 7 validation steps (manual gates only)
      4. Tip in Mac chat "audit phase 7" → Opus designs finalization sprint

    Write logs/reflection-FINAL-S5-MAXED-pc.md (covers BOTH S5 + Phase 7 prep).
    log_episode for each stage.
    Update tasks/STATE.json:
    - s5_mvp_complete: true
    - phase_7_foundation_complete: true
    - phase_7_status: "awaiting_user_for_in_game_validation"
    Final commit + push.

    Chat output:
    "S5 MVP LIVE. Plus Phase 7 (Game Master) foundation pre-staged for user.
    Launch elos_chat.py for design-time editing.
    Phase 7 roadmap: playbook/PHASE_7_GAME_MASTER_ROADMAP.md.
    Type 'audit phase 7' in Mac chat when back to plan finalization sprint. 🎯"
  </action>

  <done_when>
    - Final paper exists
    - reflection written
    - STATE.json updated
    - All commits pushed
    - User notified
  </done_when>
</stage>

---

<escalation_triggers>
  - F.0 deps install fail after winget retry → escalate
  - F.2 UAC/2FA/SmartScreen prompt → escalate (cannot bypass)
  - F.3 plugin op-type stuck >15 inner iterations → researcher → escalate
  - F.5 AHK hotkey can't reach Workbench (security software?) → escalate
  - F.6 first revision can't produce visual change → architectural issue, escalate
  - F.7 reliability <80% → escalate
  - Token budget >800k → escalate
  - Total runtime >8h → escalate
</escalation_triggers>

<sub_agents_enabled>
  <agent role="logger" always_on="true" full_session="true"/>
  <agent role="dep-installer" stage="F.0" model="haiku"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"
         output_rule="MANDATORY 3 labeled fix options + recommended"/>
  <agent role="enforce-researcher" stages="F.3,F.8" model="sonnet"/>
  <agent role="diff-verifier" stages="F.3,F.6,F.7" model="sonnet"/>
  <agent role="latency-monitor" stages="F.6,F.7" model="haiku"/>
  <agent role="ui-classifier" stages="F.2,F.4,F.6" model="sonnet" multimodal="true"/>
  <agent role="loop-detector" on_retry="true"/>
  <agent role="auditor" pre_push="true" model="sonnet"/>
  <agent role="optimizer" post_success="true" model="sonnet"/>
  <agent role="phase7-architect" stages="F.8" model="sonnet"/>
</sub_agents_enabled>

<token_budgets>
  <cu_per_task_max>100000</cu_per_task_max>
  <plugin_dev_max>300000</plugin_dev_max>
  <phase_7_prep_max>200000</phase_7_prep_max>
  <combined_max>1200000</combined_max>
  <escalate_at>950000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - cu_max_turns_per_task = 60
  - inner_loop_max = 15 per op-type
  - middle_loop_max = 10 per regression
  - outer_loop_max = 15 to saturation
  - step_time_budget = 30 min default (F.3 override: 3h)
  - sprint_time_budget = 8h total
  - DRY marker for destructive ops (rare)
  - NEVER bypass UAC/2FA/SmartScreen
  - Sub-agent depth ≤3
  - Always include 3 labeled options in bug-fixer outputs
</hard_guards>

</sprint>

---

## Wrapper Prompt — paste in PC Claude Code (Sonnet 4.6)

```
Du bist PC-Executor. Sprint FINAL-S5-MAXED — One Sprint to S5.
Sonnet 4.6 default. ~5-7h autonomous. End-state: S5 MVP live editor.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/handoffs/final-paper-MEGA-A-20260521.md ← was bereits erreicht
3. research/12-computer-use-windows-host.md ← Anthropic CU strategy
4. research/13-chat-panel-architecture-final.md ← floating window (NOT embedded)
5. playbook/RELAY_PROTOCOL.md
6. PC_AGENT_BRIEF.md
7. playbook/CHEATSHEET-PC.md
8. playbook/handoffs/sprint-FINAL-S5-MAXED.md ← THIS plan

Critical Knowledge:
- Anthropic Computer Use is GA-Beta — header "computer-use-2025-11-24", tool "computer_20251124"
- Models: claude-sonnet-4-6 (default, click-precise) or claude-opus-4-7 (hard scenes)
- Blender-MCP architecture: floating-chat-window EXTERNAL + plugin acts as tool server
  → MIRROR this: scripts/chat-window/elos_chat.py is the floating window
- Code skeletons already exist at scripts/computer-use/ + scripts/chat-window/
  → Sprint fills in the gaps (e.g. plugin TODOs, bridge polish)
- Hard limits: UAC, 2FA, SmartScreen → escalate, cannot bypass

Pre-flight (Phase A):
☐ CS aus
☐ ANTHROPIC_API_KEY env-var set persistently
☐ Steam logged in (no 2FA mid-sprint)
☐ User available ~30 min for UAC clicks if needed

Execute Stages F.0 → F.1 → F.2 → F.3 → F.4 → F.5 → F.6 → F.7 → F.FINAL.

3-layer iteration loop (F.3 plugin work):
- Inner (sec, per op-type compile-test)
- Middle (min, 5 cases per op-type regression)
- Outer (hr, all 5 ops × 10 revisions = 50 sweep)
- Saturation: ≥95% pass rate over outer loop

Sub-Agent-Fleet (full session): logger, dep-installer, ui-classifier multimodal,
enforce-researcher, bug-fixer (MANDATORY 3-options output), diff-verifier,
latency-monitor, loop-detector, auditor pre-push, optimizer post-success.

Stuck-Detection: 4× same error-class → researcher → 2 more turns → escalate.
Saturation: 3 consecutive outer-N-green OR hard cap 15 outer iterations.

Escalate-to-Mac if:
- UAC/2FA prompts (1-click user fix)
- F.3 op-type stuck >15 inner iter
- F.6 first revision no visual change
- F.7 reliability <80%
- Token >800k OR runtime >8h

Final Paper: playbook/handoffs/final-paper-FINAL-S5-MAXED-<TS>.md
Intermediate commits per stage.

When done: chat output "S5 MVP LIVE. Type 'fog dichter' in elos_chat.py → see in Workbench."

Start with Stage F.0 (Pre-Flight).
```

---

## File Inventory (created by this sprint design)

```
scripts/
  computer-use/
    windows_computer.py  ← ~250 LOC Windows host adapter (Anthropic CU)
    run_task.py          ← ~150 LOC sampling loop runner
  chat-window/
    elos_chat.py         ← ~280 LOC Tk floating chat window
    elos-reload.ahk      ← ~50 LOC AutoHotkey v2 file-watcher
    (bridge.py)          ← created during F.3 (Claude API client)
```

All Mac-pre-staged. Sprint fills in:
- AI_GeneratePlugin.c TODOs (JSON parse + 5 op-types)
- Any missing glue between components
- Tests + golden trajectories

---

## Cost Estimate

| Component | Tokens | Cost |
|---|---|---|
| F.0-F.1 setup + smoke | ~20k | ~$0.50 |
| F.2 Steam install via CU | ~80k | ~$2.50 |
| F.3 plugin dev (3-layer iter) | ~400k | ~$12 |
| F.4-F.5 verify | ~30k | ~$1 |
| F.6 first live edit | ~50k | ~$1.50 |
| F.7 10-revision reliability | ~150k | ~$5 |
| F.FINAL paper | ~30k | ~$1 |
| **Total estimate** | **~760k** | **~$23-30** |

vs pure-Opus equivalent: ~$120-180. Saving ~80%.

---

## Why This Will Work

1. ✅ **MEGA-A already did 80%** — backend, plugin refactor with real API, file-watch scaffold, sample-clone
2. ✅ **Computer Use solves the manual-click problem** — Steam Server install now autonomous
3. ✅ **Floating chat = proven pattern** — Blender-MCP, Unity-MCP, Unreal-MCP all do this
4. ✅ **Code skeletons pre-staged** — Mac-side, ready to fill in
5. ✅ **Iteration loops + sub-agent fleet** — self-testing + auto-bug-fix proven in Devin/Aider/Cursor
6. ✅ **6-7h realistic** — not 30 min fantasy, not 30 day perfection
