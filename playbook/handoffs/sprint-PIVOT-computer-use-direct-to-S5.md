# Sprint PIVOT — Computer Use Bootstrap + Direct to S5 (~3-5h, user mostly absent)

> Stand: 2026-05-21
> Model: Sonnet 4.6 (for Computer Use steps + plugin work)
> Reset of the overnight strategy. Acknowledges what MEGA-A actually achieved + uses
> Anthropic Computer Use for the manual-blocker steps that killed MEGA-A's S2.
> Source: research/12-computer-use-windows-host.md

---

## Honest Assessment of Where We Are

**MEGA-A achieved (16/18 criteria DONE):**
- ✅ Backend foundation (revisions API, prompt caching, episodic memory, golden tests)
- ✅ 116/116 backend tests PASS
- ✅ Bohemia samples cloned + studied
- ✅ AI_GeneratePlugin.c refactored with REAL WorldEditorAPI (2 TODOs left)
- ✅ File-watch infrastructure scaffolded
- ✅ Plugin dev environment installed (VSCode + Enforce ext + chokidar + npm)
- ✅ 8× Validate PASS streak (CI gate rock solid)

**Blocked (2 criteria):**
- ❌ S2 Game Test: `ArmaReforgerServer.exe` not installed (AppID 1874900 needs Steam click)
- ⚠️ Sample plugin compile unverified (security classifier blocked external code load)

**The blocker class:** Steam Library "Install Tool" dialog + EULA + UAC. Not automatable
WITHOUT Anthropic Computer Use loop. That's what this sprint adds.

---

<sprint>

<context>
  <goal>
    Pivot to Anthropic Computer Use for autonomous Windows GUI control. Use it to install
    ArmaReforgerServer (the missing piece), then bridge directly to S5 (live-editor plugin
    work). Skip S2 standalone game test for now — verify via plugin headless test instead.
  </goal>

  <success_criteria>
    <criterion id="sc-1">Windows Computer Use host installed: pyautogui + mss + pygetwindow + anthropic SDK + AutoHotkey</criterion>
    <criterion id="sc-2">~200 LOC windows_computer.py functional (screenshot + click + type + key actions wired to Anthropic API)</criterion>
    <criterion id="sc-3">Demo task: "open Notepad, type 'hello', close" works autonomously</criterion>
    <criterion id="sc-4">Steam Library navigation: install ArmaReforgerServer (AppID 1874900) autonomously</criterion>
    <criterion id="sc-5">Workbench-Diag launches + sample plugin verified compiled (1 successful run)</criterion>
    <criterion id="sc-6">AI_GeneratePlugin.c 2 TODOs filled (JSON parse + ops loop)</criterion>
    <criterion id="sc-7">First end-to-end test: write spec.json → AHK Ctrl+Shift+R → plugin applies → diff verified</criterion>
    <criterion id="sc-8">Latency measurement on op-type attribute-edit</criterion>
    <criterion id="sc-9">Final paper: playbook/handoffs/final-paper-PIVOT-<TS>.md</criterion>
  </success_criteria>

  <constraints>
    <constraint>User must have ANTHROPIC_API_KEY set in environment (one-time, persistent)</constraint>
    <constraint>Steam pre-login required (user does ONCE before sprint, no 2FA mid-sprint)</constraint>
    <constraint>UAC prompts for new installs may appear — user clicks if at PC, else escalate</constraint>
    <constraint>Stay ≤3 sub-agent depth</constraint>
    <constraint>DRY marker for destructive ops (rare in this sprint)</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <model>claude-sonnet-4-6 (Computer Use steps), claude-opus-4-7 if novel bug</model>
    <computer_use_beta>computer-use-2025-11-24</computer_use_beta>
    <api_key_env>$env:ANTHROPIC_API_KEY (set persistently before sprint)</api_key_env>
  </env>
</context>

---

## STAGE P.0 — Setup Computer Use Host (~30 min)

<stage id="P.0" name="cu_host_setup">

  <action>
    Phase A: User confirms ANTHROPIC_API_KEY is set, Steam is logged in (no 2FA expected)

    1. Install Python packages:
    ```powershell
    python -m pip install --upgrade --user anthropic pyautogui mss pygetwindow pillow
    ```

    2. Install AutoHotkey v2:
    ```powershell
    winget install AutoHotkey.AutoHotkey -e --accept-package-agreements --silent
    ```

    3. Create scripts/computer-use/windows_computer.py (~200 LOC):
       - take_screenshot() → base64 PNG via mss
       - click(x, y) → pyautogui.click
       - type_text(text) → pyautogui.typewrite (with interval)
       - key(combo) → pyautogui.hotkey (split by "+")
       - scroll(direction, amount) → pyautogui.scroll
       - wait(seconds) → time.sleep
       - get_window_titles() → pygetwindow.getAllTitles
       - activate_window(title) → window.activate

    4. Create scripts/computer-use/run_task.py:
       - sampling loop per Anthropic quickstart
       - Connects to Anthropic API with computer-use-2025-11-24 beta
       - Model: claude-sonnet-4-6
       - tools=[{"type": "computer_20251124", "name": "computer",
                 "display_width_px": 1920, "display_height_px": 1080}]
       - Iterates until stop_reason == "end_turn"
       - Logs every action + screenshot to logs/cu-{task}-{ts}.jsonl
  </action>

  <done_when>
    - python -c "import anthropic, pyautogui, mss, pygetwindow, PIL" succeeds
    - windows_computer.py + run_task.py exist
    - AutoHotkey v2 installed
    - sc-1 + sc-2 met
  </done_when>

</stage>

---

## STAGE P.1 — Verify Computer Use Loop Works (~10 min)

<stage id="P.1" name="cu_verification">

  <action>
    Run sanity demo:
    ```powershell
    python scripts/computer-use/run_task.py "Open Notepad, type 'ELOS CU test', wait 2 seconds, close without saving"
    ```

    Watch + verify:
    - Notepad opens via Computer Use
    - Text gets typed
    - Notepad closes (Alt+F4 → Don't Save)
    - All actions logged to logs/cu-demo-<TS>.jsonl
    - Total ~10-15 screenshots used

    If FAIL: bug-fixer diagnoses (api key? screen-capture permissions? pyautogui blocked?)
  </action>

  <done_when>
    - Demo task completes autonomously
    - sc-3 met
  </done_when>

  <on_failure>
    - API key wrong → user updates env var
    - Screenshot returns black → screen permissions issue → user grants
    - Click coords off-screen → Claude's vision needs higher-res screenshots
  </on_failure>

</stage>

---

## STAGE P.2 — Install ArmaReforgerServer via Computer Use (~15 min)

<stage id="P.2" name="install_server">

  <action>
    THE thing that killed MEGA-A. Now automated.

    ```powershell
    python scripts/computer-use/run_task.py @"
    Task: Install 'Arma Reforger Server' tool via Steam Library.

    Steps:
    1. Bring Steam to foreground (already running; window title contains 'Steam')
    2. Click 'Library' in left sidebar
    3. In the filter, search for 'Arma Reforger Server' (this is a Tool, not Game)
    4. If found in library: click Install button
       If not found: click 'Tools' filter dropdown first, then search
    5. When Steam install dialog appears (file location, shortcuts):
       Accept defaults, click Next/Install
    6. Wait for download to complete (could be 5-10 min, ~200MB)
       Monitor progress every 30 seconds via screenshot
    7. When 'Play'/'Launch' button appears for Arma Reforger Server: DONE
    8. Verify install: check C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Server\ exists

    Constraints:
    - If UAC prompt appears: STOP, escalate (cannot bypass UAC)
    - If Steam 2FA: STOP, escalate (user phone)
    - If 'Cancel'/'X' button accidentally hit: undo + retry
    - Max 80 turns total
    "@
    ```

    Result: tools/ArmaReforgerServer/ArmaReforgerServer.exe should exist.
  </action>

  <done_when>
    - ArmaReforgerServer.exe present in expected path
    - sc-4 met
    - logs/cu-install-server-<TS>.jsonl saved
  </done_when>

  <on_failure>
    - UAC blocks → escalate to user (1-click fix)
    - 2FA → escalate (phone tap)
    - Steam offline → check connection
    - Computer Use stuck in loop → loop-detector fires, escalate
  </on_failure>

</stage>

---

## STAGE P.3 — Verify Sample Plugin Compiles via Computer Use (~10 min)

<stage id="P.3" name="sample_plugin_verify">

  <action>
    ```powershell
    python scripts/computer-use/run_task.py @"
    Task: Verify SampleWorldEditorPlugin compiles in Workbench.

    Steps:
    1. Open Workbench-Diag: C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe
       with argument: -gproj=$env:USERPROFILE\Documents\GitHub\Arma-Reforger-Samples\SampleMod_WorkbenchPlugin\addon.gproj
    2. Wait for Workbench to fully load (look for menu bar)
    3. Click 'Plugins' menu (top menu bar)
    4. Look for 'SamplePlugins' submenu
    5. If 'Generate from AI Spec' or similar entries exist: PASS — sample compiled
    6. Take final screenshot as evidence
    7. Close Workbench cleanly (Alt+F4)

    Constraints:
    - If Workbench crashes on launch: PASS-with-warning, log error
    - If 'Plugins' menu empty: FAIL — sample plugin didn't compile
    - Max 30 turns
    "@
    ```
  </action>

  <done_when>
    - Plugins menu shows SamplePlugins entries
    - sc-5 met
  </done_when>

  <on_failure>
    - Workbench crash → escalate, may need different sample
    - Sample not compiling → fixable via plugin code review (separate task)
  </on_failure>

</stage>

---

## STAGE P.4 — Fill AI_GeneratePlugin.c TODOs (~1-2h, Sonnet work)

<stage id="P.4" name="plugin_implementation">

  <action>
    Implement the 2 TODOs in workbench-plugin/AI_GeneratePlugin.c:
    1. JSON parsing via JsonSerializer.Deserialize (read $profile:elos/ai-spec.json)
    2. Ops loop: for each op in spec.ops, dispatch to attribute_edit / entity_create / etc.

    Use Bohemia samples as reference:
    - SampleWorldEditorPlugin.c for WorldEditorAPI usage
    - WorkbenchPlugin.c for base class signatures
    - Script-Diff repo for exact method names

    Iteration loop (inner per op-type):
    - Code change → save .c file
    - Trigger headless validate via Workbench-Diag -plugin=AI_GeneratePlugin
    - Parse plugin log for OK:/ERR:
    - If FAIL: bug-fixer suggests fix
    - Max 15 inner iterations per op-type

    Op types to implement:
    - attribute_edit (fog_density, time_of_day)
    - entity_create (spawn_point, ai_group)
    - entity_delete
    - entity_move
    - batch (composite of above)
  </action>

  <done_when>
    - All 5 op-types working (JSON spec → plugin log shows OK:)
    - sc-6 met
  </done_when>

  <on_failure>
    - Enforce API unclear → enforce-researcher consults BI wiki + Script-Diff repo
    - 4× same error-class → researcher escalation
  </on_failure>

</stage>

---

## STAGE P.5 — First End-to-End Live Edit Test (~30 min)

<stage id="P.5" name="first_live_edit">

  <action>
    The proof-of-concept moment.

    Setup:
    1. Open Workbench with night-recon-everon addon (manual or via Computer Use)
    2. Start file-watcher (scripts/file-watcher.ps1) in background — watches
       $profile:elos/ai-spec.json
    3. AHK script registers Ctrl+Shift+R global hotkey-trigger

    Test:
    1. Write to ai-spec.json:
    ```json
    {
      "mission_id": "night-recon-everon",
      "version": "test-001",
      "ops": [
        {"op": "attribute_edit", "target": "weather", "field": "fog_density", "value": 0.7}
      ]
    }
    ```
    2. File-watcher detects change → fires AHK Ctrl+Shift+R into Workbench window
    3. Workbench reloads scripts → AI_GeneratePlugin.Run() executes
    4. Plugin reads spec → calls SetVariableValue(weatherManager, "m_fFogDensity", 0.7)
    5. Viewport repaints with denser fog

    Measure latency: file-write timestamp → plugin log "OK:" timestamp.

    Capture screenshot of viewport before + after via Computer Use.
    Verify visual diff (fog visibly denser).
  </action>

  <done_when>
    - One revision applied + visible in viewport
    - Latency measured + logged
    - sc-7 + sc-8 met
    - logs/first-live-edit-test.json complete
  </done_when>

  <on_failure>
    - File-watcher doesn't fire → check chokidar/PowerShell script
    - AHK doesn't reach Workbench → focus issue, try PyDirectInput fallback
    - Plugin doesn't see ai-spec.json → permission or path issue
    - Plugin runs but viewport doesn't update → API call wrong, debug WorldEditorAPI usage
  </on_failure>

</stage>

---

## STAGE P.FINAL — Consolidated Paper

<stage id="P.FINAL" name="final_paper">

  <action>
    Generate playbook/handoffs/final-paper-PIVOT-<TS>.md:
    - Goal Achievement Matrix (sc-1 to sc-9)
    - Stages outcomes
    - Computer Use loop performance (turns/cost per task)
    - First live-edit latency measurement
    - Cost breakdown (Sonnet + Computer Use overhead)
    - Path to MVP S5: which op-types still need work
    - Known issues + workarounds

    log_episode + reflection-PIVOT-pc.md
    Update STATE.json: pivot_complete=true, ready_for_full_S5=true
    Push.
  </action>

</stage>

---

<escalation_triggers>
  - UAC prompt during Steam install (cannot bypass) → escalate, user 1-click fix
  - Steam 2FA mobile prompt → escalate, user phone tap
  - Computer Use loop stuck (4× same screen state) → loop-detector, escalate
  - Plugin compile fails after 15 inner iterations → escalate
  - Token budget > 500k for entire sprint → escalate
  - Total runtime > 6h → escalate
</escalation_triggers>

<sub_agents_enabled>
  <agent role="logger" always_on="true"/>
  <agent role="dep-installer" stage="P.0" model="haiku"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <agent role="enforce-researcher" stages="P.4" model="sonnet"/>
  <agent role="loop-detector" on_retry="true"/>
  <agent role="auditor" pre_push="true" model="sonnet"/>
  <agent role="diff-verifier" stages="P.5" model="sonnet"/>
  <agent role="latency-monitor" stage="P.5" model="haiku"/>
</sub_agents_enabled>

<token_budgets>
  <cu_per_task_max>100000</cu_per_task_max>
  <combined_max>500000</combined_max>
  <escalate_at>400000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - cu_max_turns_per_task = 80
  - step_time_budget = 30 min default (P.4 can override 2h)
  - sprint_time_budget = 6h
  - DRY marker for destructive ops
  - NEVER bypass UAC / 2FA / SmartScreen
  - Sub-agent depth ≤3
</hard_guards>

</sprint>

---

## Wrapper Prompt — paste in PC chat (user mostly absent, periodic check-ins ok)

```
Du bist PC-Executor. PIVOT-Sprint: Computer Use + direct to S5.
Sonnet 4.6 default. ~3-5h.

MEGA-A war zu 80% Erfolg — alle Foundation done, blocker war ArmaReforgerServer
Install (Steam manual click). DIESER Sprint nutzt Anthropic Computer Use für
diesen Blocker.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/handoffs/final-paper-MEGA-A-20260521.md ← was schon erreicht
3. research/12-computer-use-windows-host.md ← Computer Use Strategy
4. playbook/RELAY_PROTOCOL.md
5. PC_AGENT_BRIEF.md
6. playbook/CHEATSHEET-PC.md
7. playbook/handoffs/sprint-PIVOT-computer-use-direct-to-S5.md ← THIS plan

Critical Knowledge:
- Anthropic Computer Use is GA-Beta — use beta header "computer-use-2025-11-24"
- Tool type: "computer_20251124"
- Models: claude-sonnet-4-6 (default, click-precise) or claude-opus-4-7 (hard scenes)
- Windows host = roll your own (~200 LOC Python with pyautogui + mss + anthropic SDK)
- Steam UI + Reforger Game + Workbench are ALL opaque to UIA — pixel-based only
- AHK for known hotkeys (Ctrl+Shift+R Workbench reload)
- Hard limits: UAC, 2FA, SmartScreen → escalate, can't bypass

Pre-flight check (Phase A):
- ANTHROPIC_API_KEY set persistently? (echo $env:ANTHROPIC_API_KEY)
- Steam logged in, no 2FA mid-sprint?
- User available for 1-2 click-throughs if UAC fires?

Execute Stages P.0 → P.5 → P.FINAL strictly per plan:
- P.0 Setup Computer Use Host (30 min)
- P.1 Verify CU loop (Notepad demo, 10 min)
- P.2 Install ArmaReforgerServer via CU (15 min, the actual win)
- P.3 Verify Sample Plugin via CU (10 min)
- P.4 Fill AI_GeneratePlugin.c 2 TODOs (1-2h, plugin work)
- P.5 First end-to-end live edit (30 min — the magic moment)
- P.FINAL Paper + push

Sub-agents per RELAY_PROTOCOL. DRY marker. Depth ≤3.
Escalate-to-Mac if UAC/2FA/SmartScreen prompts appear, or CU loop stuck.

When done: chat output "PIVOT complete. First live-edit working at <latency>s.
Ready for full S5 op-type buildout."

Start with Phase A confirmation (API key + Steam state).
```
