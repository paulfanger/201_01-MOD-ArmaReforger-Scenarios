# Sprint S2 — Autonomous Game Control (user absent, ~30 min)

> Stand: 2026-05-21 · Model: Sonnet 4.6 (Opus escalation on vision-loop failures)
> User-state: NICHT am PC. Steam logged in. Game installed. BattlEye-OFF environment.
> Source: research/10-3-stage-sprint-design.md

---

<sprint>

<context>
  <goal>
    PC autonomously launches Arma Reforger, loads a mission via Local-Dedi-Server-Trick
    (bypass menu), verifies in-game state via vision-loop, tests player input via PyDirectInput,
    cleanly exits, reports back via git push. No user present, no manual clicks.
  </goal>

  <success_criteria>
    <criterion id="sc-1">Local dedi server starts + listens on port 2001 with night-recon-everon scenario</criterion>
    <criterion id="sc-2">Client connects via `steam.exe -applaunch 1874880 -client -connect=127.0.0.1`</criterion>
    <criterion id="sc-3">Vision-loop classifies state trajectory: MainMenu → Loading → SpawnScreen → InGame</criterion>
    <criterion id="sc-4">PyDirectInput WASD test changes screen content (scene-diff confirmed)</criterion>
    <criterion id="sc-5">Clean exit back to MainMenu</criterion>
    <criterion id="sc-6">Total runtime < 20 min including all retries</criterion>
    <criterion id="sc-7">9 screenshots + 9 vision-classifications + 1 movement-test-result in logs/</criterion>
    <criterion id="sc-8">Final paper documents trajectory + any anomalies</criterion>
  </success_criteria>

  <constraints>
    <constraint>NO user-clicks expected (true autonomous)</constraint>
    <constraint>BattlEye-protected MP scenarios FORBIDDEN (only local SP/dedi)</constraint>
    <constraint>Resolution forced 1280x800 windowed (Anthropic computer-use guideline)</constraint>
    <constraint>PyDirectInput required (NOT PyAutoGUI — DirectX game)</constraint>
    <constraint>Screenshots resized to 1280x800 before vision API call</constraint>
    <constraint>Hard escalation triggers → Stage 3 (user-at-PC fallback)</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <game_exe>C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerSteam.exe</game_exe>
    <server_exe>C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerServer.exe</server_exe>
    <steam_exe>C:\Program Files (x86)\Steam\steam.exe</steam_exe>
    <addons_root>%USERPROFILE%\Documents\my games\ArmaReforger\addons</addons_root>
    <pip_required>pydirectinput, pillow, pytesseract (optional)</pip_required>
  </env>
</context>

---

## STAGE 2.0 — Pre-Flight + Safety

<stage id="2.0" name="preflight">

  <action>
    1. ⚙️ DO Phase A verify: User confirms CS is closed + has stepped away from PC
    2. Phase B verify:
       ```powershell
       Get-Process | Where-Object {
         $_.ProcessName -in @("cs2","csgo","ArmaReforgerSteam","ArmaReforgerServer","ArmaReforgerWorkbench")
       } | ForEach-Object { Stop-Process -Id $_.Id -Force }
       Start-Sleep 5
       ```
    3. dep-installer: pip install pydirectinput pillow
    4. Test screenshot at 1280x800 (resize from native):
       ```powershell
       function Take-ScreenshotResized {
         param([string]$OutPath, [int]$Width = 1280, [int]$Height = 800)
         Add-Type -AssemblyName System.Windows.Forms,System.Drawing
         $bounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
         $full = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
         $gfx = [Drawing.Graphics]::FromImage($full)
         $gfx.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
         $resized = New-Object Drawing.Bitmap $Width, $Height
         $rgfx = [Drawing.Graphics]::FromImage($resized)
         $rgfx.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
         $rgfx.DrawImage($full, 0, 0, $Width, $Height)
         $resized.Save($OutPath)
       }
       Take-ScreenshotResized -OutPath "logs/screenshot-test-S2.png"
       ```
    5. Update tasks/STATE.json: turn_id=S2, phase=PHASE_C_EXEC
    6. Logger spawn
  </action>

  <done_when>
    - User confirmed absence
    - No competing processes
    - pydirectinput installed
    - Test screenshot saved at 1280x800
    - STATE.json updated
  </done_when>

  <on_failure>
    - pip install fail (offline?) → escalate to user
    - Resolution mismatch → save coord-scale-factor for later use
  </on_failure>

</stage>

---

## STAGE 2.1 — Local Dedi Server Spawn (THE TRICK)

<stage id="2.1" name="dedi_server">

  <action>
    1. Write dedi-config-night-recon.json:
       ```json
       {
         "bindAddress": "127.0.0.1",
         "bindPort": 2001,
         "publicAddress": "",
         "publicPort": 0,
         "a2s": {
           "address": "127.0.0.1",
           "port": 17777
         },
         "game": {
           "name": "ELOS AI Test - night-recon",
           "password": "",
           "passwordAdmin": "",
           "scenarioId": "{8B56608D5A651540}",
           "playerCountLimit": 4,
           "autoJoinable": false,
           "visible": false,
           "supportedPlatforms": ["PLATFORM_PC"],
           "gameProperties": {
             "serverMaxViewDistance": 1500,
             "serverMinGrassDistance": 50,
             "networkViewDistance": 1500,
             "disableThirdPerson": false,
             "fastValidation": true,
             "battlEye": false,
             "VONDisableUI": false,
             "VONDisableDirectSpeech": false,
             "missionHeader": {}
           },
           "modIds": []
         },
         "operating": {
           "lobbyPlayerSynchronise": true,
           "playerSaveTime": 120,
           "aiLimit": -1,
           "slotReservationTimeout": 60
         }
       }
       ```
    2. Spawn server background:
       ```powershell
       $serverConfig = "$repo\dedi-config-night-recon.json"
       $proc = Start-Process -FilePath $env:server_exe `
         -ArgumentList @("-config", "`"$serverConfig`"", "-autoreload", "0",
                         "-logFile", "logs/dedi-server-S2.log") `
         -PassThru -WindowStyle Minimized
       ```
    3. Wait for "Listening for clients" in server log, max 60s
    4. Verify port 2001 listening: `Test-NetConnection -ComputerName 127.0.0.1 -Port 2001`
  </action>

  <done_when>
    - Server process alive
    - Port 2001 listening
    - Server log shows "Listening for clients"
    - scenarioId GUID matched night-recon-everon addon
  </done_when>

  <on_failure>
    - Server fails to start → check addons folder, mission GUID, dedi-config schema
    - Port 2001 already in use → choose alternative (2010)
    - "Listening" never appears → kill, escalate with server log dump
  </on_failure>

</stage>

---

## STAGE 2.2 — Client Launch + Connect

<stage id="2.2" name="client_connect">

  <action>
    1. Disable Steam overlay (avoid intercept popups):
       ```powershell
       & $env:steam_exe -flushconfig
       ```
    2. Launch client with -client -connect:
       ```powershell
       & $env:steam_exe -applaunch 1874880 -client -connect=127.0.0.1:2001 `
         -window -resX=1280 -resY=800 -newErrorsAsWarnings
       ```
    3. Wait 60s for client process + connection
    4. Verify client process alive: Get-Process ArmaReforgerSteam
    5. Spawn process-tracker: poll every 5s until client+server stable
  </action>

  <done_when>
    - Client process running
    - 60s elapsed without crash
    - process-tracker confirms stable state
  </done_when>

  <on_failure>
    - Client crash on launch → log dump from `%LOCALAPPDATA%\ArmaReforger\logs\` + escalate
    - Steam update mid-launch (rare) → wait max 600s
    - Cannot connect to 127.0.0.1:2001 → check server still alive
  </on_failure>

</stage>

---

## STAGE 2.3 — Vision-Loop State Classification

<stage id="2.3" name="vision_loop">

  <action>
    Iterate 8× (max 8 cycles, 5s spacing = 40s total budget):

    For each cycle:
    1. Take-ScreenshotResized → logs/gui-state-S2-cycle{N}.png
    2. Spawn ui-tester sub-agent multimodal vision:
       - Input: PNG path
       - Output JSON: {state, confidence, next_action}
       - Possible states:
         * MainMenu (large "PLAY"/"SCENARIOS" tile, no HUD)
         * Loading (dark frame, progress bar bottom)
         * SpawnScreen (deployment map, "DEPLOY"/"SPAWN" button)
         * InGame (stamina/compass HUD visible bottom-left)
         * Death (dimmed, "RESPAWN" overlay)
         * Crashed (process exited)
         * Unknown (confidence < 0.5)
    3. Log classification
    4. If state == "InGame": break to Stage 2.4
    5. If state == "SpawnScreen": vision-locate "DEPLOY" button → PyDirectInput click
    6. If state == "Crashed": escalate
    7. If state == "Unknown" 3× in a row: escalate (vision uncertainty)
    8. If state == "Loading" persists 120s: escalate (mission load failed)

    State trajectory expected: Loading → SpawnScreen → (click DEPLOY) → InGame
  </action>

  <done_when>
    - State == "InGame" classified with confidence > 0.7
    - State trajectory logged in logs/state-trajectory-S2.json
    - 9 screenshots captured
  </done_when>

  <on_failure>
    - Unknown 3× → escalate via Stage 3
    - Loading > 120s → kill, escalate
    - Crashed → log dump, escalate
  </on_failure>

</stage>

---

## STAGE 2.4 — Movement Test (PyDirectInput)

<stage id="2.4" name="movement_test">

  <action>
    1. Take "before" screenshot → logs/movement-before-S2.png
    2. Run movement via PyDirectInput:
       ```powershell
       python -c @"
       import pydirectinput
       import time
       # Walk forward 2 seconds
       pydirectinput.keyDown('w')
       time.sleep(2)
       pydirectinput.keyUp('w')
       # Look around (mouse move)
       pydirectinput.moveRel(200, 0, duration=0.5)
       time.sleep(0.5)
       pydirectinput.moveRel(-200, 0, duration=0.5)
       "@
       ```
    3. Take "after" screenshot → logs/movement-after-S2.png
    4. Compare: ui-tester multimodal compares before/after, expects DIFFERENT scene
    5. Verify still in "InGame" state (didn't open menu accidentally)
  </action>

  <done_when>
    - PyDirectInput executed without errors
    - Scene-diff confirmed (before ≠ after)
    - State still "InGame" after movement
  </done_when>

  <on_failure>
    - PyDirectInput rejected → try pyinterception fallback
    - Scene identical (no input effect) → escalate (DirectInput injection failure)
    - Accidentally opened menu → press Esc to dismiss, continue or escalate
  </on_failure>

</stage>

---

## STAGE 2.5 — Clean Exit

<stage id="2.5" name="clean_exit">

  <action>
    1. Press Esc → opens in-game menu
       ```powershell
       python -c "import pydirectinput; pydirectinput.press('escape')"
       Start-Sleep 1
       ```
    2. Take screenshot, vision-classify menu state
    3. Vision-locate "EXIT TO MAIN MENU" or equivalent button
    4. PyDirectInput click on located coord (resolution-scaled)
    5. Wait 10s
    6. Verify state == "MainMenu"
    7. Press Esc + Esc + click "EXIT TO DESKTOP" (or Alt+F4 fallback)
    8. Wait 15s
    9. Verify client process exited: Get-Process ArmaReforgerSteam null
    10. Kill dedi server: Stop-Process -Name ArmaReforgerServer -Force
    11. Cleanup logs/state-trajectory completion
  </action>

  <done_when>
    - Client process exited gracefully
    - Server process killed
    - Final state == "process-exited"
  </done_when>

  <on_failure>
    - Click on "EXIT" failed → Alt+F4 fallback
    - Process won't exit → Stop-Process -Force after 30s
  </on_failure>

</stage>

---

## STAGE 2.6 — Report + Reflection + Push

<stage id="2.6" name="report_push">

  <action>
    1. Aggregate logs/state-trajectory-S2.json:
       - All screenshots
       - All classifications
       - Movement-test result
       - Total runtime
    2. Generate playbook/handoffs/final-paper-sprint-S2-<TS>.md:
       - Goal achievement (sc-1 to sc-8)
       - State trajectory visualization
       - Anomalies / surprises
       - Cost breakdown (Sonnet vision tokens)
       - Next steps (Stage 3 prep)
    3. Write logs/reflection-turn-S2-pc.md
    4. log_episode via episodic.py for each stage outcome
    5. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_S2_complete=true
    6. git pull --rebase, git add -A, git commit, git push
    7. Output to chat: "Sprint S2 complete. Trajectory: <list>. Final paper: <path>."
  </action>

  <done_when>
    - Final paper generated
    - reflection-turn-S2-pc.md written
    - episodic.jsonl + DB updated
    - All commits pushed
  </done_when>

</stage>

---

<escalation_triggers>
  - Dedi server fails to start after 3 retries
  - Client crash on launch (process exits within 30s)
  - BattlEye prompt detected (SHOULD NOT happen offline — bug)
  - Steam login expired
  - Vision confidence < 0.4 three times in a row
  - 3 nav-loop failures (can't reach InGame state)
  - PyDirectInput injection failure on movement test
  - 20 min total runtime exceeded
  - Token budget > 400k
</escalation_triggers>

<escalation_method>
  1. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_blocked=true, blocker_stage=<X>
  2. Write logs/escalation-S2-<TS>.json with full context
  3. Take diagnostic screenshot of current screen state
  4. git commit + push
  5. Output to user chat: "Sprint S2 blocked at Stage 2.<X>. Evidence: <commit>. Stage 3 manual fallback needed."
</escalation_method>

<sub_agents_enabled>
  <agent role="logger" always_on="true"/>
  <agent role="dep-installer" stage="2.0" model="haiku"/>
  <agent role="process-tracker" stages="2.1,2.2" trigger="dedi_server,client_launch"/>
  <agent role="ui-tester" stage="2.3,2.4,2.5" model="sonnet" multimodal="true"/>
  <agent role="auditor" pre_push="true" model="sonnet"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <agent role="loop-detector" on_retry="true"/>
</sub_agents_enabled>

<token_budgets>
  <per_stage_max>50000</per_stage_max>
  <total_max>400000</total_max>
  <escalate_at>320000</escalate_at>
  <vision_cycle_max>20000</vision_cycle_max>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - step_time_budget = 5 min default (Stage 2.3 vision-loop = 1 min)
  - sprint_time_budget = 20 min total
  - resolution_cap = 1280x800 (Anthropic computer-use guideline)
  - DRY marker for cleanup ops
  - NEVER automate against BattlEye-protected sessions
</hard_guards>

</sprint>

---

## Wrapper Prompt (paste in PC chat when user steps away)

```
Du bist PC-Executor. User ist NICHT am PC. CS ist beendet. Sprint S2 — Autonomous Game.
Sonnet 4.6 default. ~20 min autonomous. Local-Dedi-Server-Trick + Vision-Loop + PyDirectInput.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/RELAY_PROTOCOL.md
3. PC_AGENT_BRIEF.md
4. playbook/CHEATSHEET-PC.md
5. research/10-3-stage-sprint-design.md (Stage-2 critical findings, esp. Dedi-Trick + BattlEye-safe)
6. playbook/handoffs/sprint-S2-autonomous-game.md ← THIS PLAN

Critical knowledge:
- Reforger uses BattlEye, NOT EAC. BattlEye-OFF in SP/local-dedi. Input-simulation SAFE.
- NO -scenario CLI flag for client — use Local Dedi Server + -client -connect=127.0.0.1
- PyDirectInput (NOT PyAutoGUI — DirectX game)
- Screenshots 1280x800 (Anthropic vision-tool requirement, downscale from native)

Execute Stages 2.0-2.6 strictly per plan.

Two-Phase Reception:
- Phase A: ⚙️ DO = "CS komplett zu" + "User NICHT am PC, kann nicht klicken" (User confirms)
- Phase B: Verify no competing processes
- Phase C: Stages 2.0-2.6 (~15-20 min autonomous)
- Phase D: Single Return + reflection-turn-S2-pc.md

Escalate-to-Stage-3 wenn:
- Dedi server fails to start (3× retry)
- Client crashes
- Vision confidence < 0.4 three times
- PyDirectInput injection fails
- 20 min total budget exceeded
- BattlEye prompt appears (shouldn't but safety net)

Sub-Agent-Fleet aktiv per RELAY_PROTOCOL. DRY marker for cleanup.

Final Paper: playbook/handoffs/final-paper-sprint-S2-<TS>.md
Push continuously.

Start with Stage 2.0 (Pre-Flight + Safety).
```
