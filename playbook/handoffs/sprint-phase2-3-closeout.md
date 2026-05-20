# Sprint Plan — Phase 2-3 Closeout (PC-only, Sonnet 4.6 optimized)

> Stand: 2026-05-21
> Modell: Sonnet 4.6 (Opus 4.7 escalation only on novel-bug or unknown-error)
> Sprint-Duration target: 60-90 min, single session
> Goal: Confirm end-to-end workflow ist live (prompt → mission → playable → revision → playable)

---

<sprint>

<context>
  <goal>
    Confirm complete workflow on PC: GUI Workbench loads generated missions,
    Game Launcher plays them, revision-cycle works end-to-end. Final paper documents
    capability state, known limitations, next steps.
  </goal>

  <success_criteria>
    <criterion id="sc-1">At least 1 of 3 missions loads in GUI Workbench (visible map/entities) within 120s</criterion>
    <criterion id="sc-2">User plays mission in Arma Reforger Game for ≥60s without crash, confirms in chat</criterion>
    <criterion id="sc-3">Revision cycle: user-prompted change → narrative.json modified → mission regenerated → validate PASS → re-test in Workbench</criterion>
    <criterion id="sc-4">Final paper generated at playbook/handoffs/final-paper-phase2-3-closeout-&lt;TS&gt;.md</criterion>
    <criterion id="sc-5">All stages pushed to git, logs preserved, WORK_LOG.md updated</criterion>
  </success_criteria>

  <constraints>
    <constraint>NO destructive changes to mission-files without user prompt (mission-design = user territory)</constraint>
    <constraint>Counter-Strike MUST be terminated before Stage 2 (GPU exclusivity)</constraint>
    <constraint>Escalate to Mac-Opus via git push + chat-pause if: 3× retry exhausted, unknown error class, novel design decision needed</constraint>
    <constraint>All sub-agent fleet active per RELAY_PROTOCOL.md (logger, dep-installer, ui-tester, auditor, loop-detector)</constraint>
    <constraint>DRY-Marker for any destructive op (Remove-Item -Recurse, file deletion)</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <addons_root>%USERPROFILE%\Documents\my games\ArmaReforger\addons</addons_root>
    <workbench_diag>C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe</workbench_diag>
    <game_exe>C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerSteam.exe</game_exe>
  </env>
</context>

---

## STAGE 1 — Pre-flight + Dependencies (5-10 min)

<stage id="1" name="preflight">

  <action>
    1. Kill any running CS / Steam-Games / Workbench processes (auto, safe — they're games)
    2. Verify environment paths (workbench-diag, addons folder, all 3 mission folders)
    3. dep-installer sub-agent: install Python 3.12 if missing (winget), install pillow via pip
    4. Verify backend pipeline runnable: `python -c "from backend.scripts.generate_mission import generate_mission_tree; print('ok')"`
    5. git pull --rebase
    6. Run pc-setup.ps1 (idempotent, [skip] expected for existing junctions)
    7. Update tasks/STATE.json: phase=PHASE_C_EXEC, sprint_stage=1, owner=pc
    8. Spawn logger sub-agent (always-on for sprint duration)
  </action>

  <done_when>
    - No CS/Workbench/ArmaReforger processes alive
    - All paths verified (4× Test-Path = True)
    - Python 3.12+ available + pillow installed
    - Backend import test passes
    - tasks/STATE.json updated, logger writing to logs/pc-events-sprint-&lt;TS&gt;.jsonl
  </done_when>

  <on_failure>
    - If Python install fails (winget error): escalate to user via ⚙️ DO (manual install python.org)
    - If backend import fails: escalate to Mac (likely missing backend dep)
    - If junction creation fails: try New-Item -Junction PowerShell-native (CHEATSHEET-PC.md)
    - Max 3 retries per sub-step, then bug-fixer + escalate
  </on_failure>

  <log_to>logs/pc-events-sprint-&lt;TS&gt;.jsonl + logs/stage1-preflight-&lt;TS&gt;.json</log_to>

</stage>

---

## STAGE 2 — GUI Smoke Test (15-20 min)

<stage id="2" name="gui_smoke">

  <action>
    For each mission in [night-recon-everon, day-assault-arland, fog-ambush-eden]:

    1. Start Workbench-Diag in GUI mode (NO -wbSilent):
       ```powershell
       $proc = Start-Process -FilePath $diag -ArgumentList @(
         "-gproj", "&quot;$addon\addon.gproj&quot;",
         "-load", "&quot;`$ai_$mission:Worlds/$mission.ent&quot;",
         "-logsDir", "&quot;$logDir&quot;"
       ) -PassThru
       Start-Sleep -Seconds 5  # Window-Focus-Stabilisierung (per PC review Task 007b-CS)
       ```
    2. Wait 55s additional (60s total since launch), screenshot RESIZED to 960×540 (per PC review):
       ```powershell
       function Take-ScreenshotResized {
         param([string]$OutPath, [int]$Width = 960, [int]$Height = 540)
         Add-Type -AssemblyName System.Windows.Forms,System.Drawing
         $bounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
         $full = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
         $gfx = [Drawing.Graphics]::FromImage($full)
         $gfx.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)

         # Resize for git-friendly storage (per PC review: 27MB → ~3MB for 9 screenshots)
         $resized = New-Object Drawing.Bitmap $Width, $Height
         $rgfx = [Drawing.Graphics]::FromImage($resized)
         $rgfx.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
         $rgfx.DrawImage($full, 0, 0, $Width, $Height)
         $resized.Save($OutPath, [Drawing.Imaging.ImageFormat]::Png)

         $gfx.Dispose(); $full.Dispose(); $rgfx.Dispose(); $resized.Dispose()
       }
       Take-ScreenshotResized -OutPath "$logDir/60s.png"
       ```
    3. Wait 30s more (90s total), screenshot resized
    4. Wait 30s more (120s total), screenshot resized
    5. Enumerate visible windows (Get-VisibleWindows)
    6. Spawn ui-tester sub-agent per screenshot:
       - Multimodal classify: mission_loaded | project_selector | error_popup | loading | crashed | unknown
       - Extract OCR text if dialog visible
       - Confidence score
    7. Aggregate verdict per mission: ≥1 mission_loaded → PASS, sonst FAIL/UNKNOWN
    8. Gracefully close Workbench (Stop-Process if still running)
    9. Wait 5s spacing, next mission
  </action>

  <done_when>
    - 9 screenshots saved + 9 ui-tester JSONs in logs/
    - Aggregate verdict per mission: PASS, FAIL, or UNKNOWN
    - At least 1 of 3 missions = PASS (sc-1 met)
    - logs/gui-smoke-aggregate-&lt;TS&gt;.json written
  </done_when>

  <on_failure>
    - If all 3 missions = project_selector: try SendKeys-Enter simulation (one experimental retry, low confidence)
    - If all 3 missions = crashed: escalate to Mac (mission-file issue probable)
    - If all 3 missions = unknown: escalate, screenshots+window-titles for Mac analysis
    - If ≥1 PASS: proceed to Stage 3 (good enough for MVP confirmation)
  </on_failure>

  <log_to>logs/gui-smoke-aggregate-&lt;TS&gt;.json + 9 screenshots + 9 ui-tester JSONs</log_to>

</stage>

---

## STAGE 3 — Live Game Test (10-15 min, user-interactive)

<stage id="3" name="game_test">

  <action>
    1. Pick the BEST mission from Stage 2 (highest confidence mission_loaded)
    2. Confirm Game-EXE path exists
    3. ⚙️ USER ACTION request in PC chat (mit klaren Erfolgsmessern):
       ```
       Stage 3 ready. Bitte:
       1. Öffne Arma Reforger Game (NICHT Workbench) via Steam
       2. Game Menü → Scenarios → finde "&lt;mission_name&gt;" in der Liste
          ✅ ERFOLGSMESSER A: Mission ist in der Liste sichtbar
       3. Klick Play, warte bis Mission lädt
          ✅ ERFOLGSMESSER B: Mission lädt ohne Crash innerhalb 30s
       4. Im Spiel checken:
          ✅ ERFOLGSMESSER C: Spawn-Point sichtbar (du spawnst irgendwo)
          ✅ ERFOLGSMESSER D: Bewegung funktioniert (WASD reagiert)
          ✅ ERFOLGSMESSER E: Time-of-Day / Wetter wie konfiguriert
             (night-recon: dunkel mit fog · day-assault: hellichter Tag · fog-ambush: 06:00 nebelig)
          ✅ ERFOLGSMESSER F: AI-Gegner sind irgendwo da (falls Phase 2 active —
             Phase 1 MVP hat noch keine encounters, ist OK wenn leer)
       5. Spiel mindestens 60 Sekunden — bewege dich, schau dich um
       6. Tipp hier zurück eine Liste: "A:✓ B:✓ C:✓ D:✓ E:✓ F:- (kein AI im MVP)"
          ODER: "issue: &lt;was schiefging&gt;"
          ODER: "abort"
       ```
    4. Wait for user response (chat-prompt, no timeout — user-paced)
    5. While waiting: every 30s take screenshot (ambient evidence), classify
       (ui-tester: in-game | menu | loading | crashed)
    6. When user responds:
       - "spielt": PASS sc-2, proceed Stage 4
       - "issue: X": capture X, bug-fixer with screenshots + user feedback
       - "abort": stop sprint, document state
  </action>

  <done_when>
    - User confirmed mission played ≥60s without crash
    - Ambient screenshots show in-game classification at least once
    - sc-2 met
    - logs/game-test-&lt;TS&gt;.json written with user feedback + screenshots
  </done_when>

  <on_failure>
    - If user reports issue: bug-fixer analyzes, may need Mac-side fix
    - If user reports crash: capture crash dump if available, escalate
    - If mission not in scenario list: addon registration issue (gproj problem) — bug-fixer
  </on_failure>

  <log_to>logs/game-test-&lt;TS&gt;.json + ambient screenshots</log_to>

</stage>

---

## STAGE 4 — Revision Cycle Test (15-25 min, user-interactive)

<stage id="4" name="revision_cycle">

  <action>
    1. 🧠 USER PROMPT request in PC chat:
       ```
       Stage 4 ready. Wähle EINE Mission und gib mir eine konkrete Revision.
       Beispiele:
         "night-recon-everon: fog dichter, Phase 3 auf 5 min kürzen"
         "day-assault-arland: max_players auf 4 reduzieren, time_of_day auf 14:00"
         "fog-ambush-eden: weather von fog_light auf fog_heavy"
       Sei spezifisch. Du sagst die Änderung — ich modifizier narrative.json und regen.
       ```
    2. Wait for user response
    3. Parse user's revision: identify (a) which mission, (b) which fields, (c) new values
    4. 🧪 DRY plan: emit before-state + after-state + hash
    5. Read missions/&lt;mission&gt;/narrative.json, apply changes, write back
    6. Run backend pipeline:
       ```powershell
       python -m backend.scripts.generate_mission &lt;mission_id&gt;
       ```
    7. Verify generated files updated (timestamp check, content diff)
    8. Re-copy to addons folder (DRY pattern: cleanup + copy)
    9. Re-validate with Workbench-Diag (must PASS)
    10. Re-run GUI smoke for revised mission (1 screenshot at 90s, classify)
    11. If PASS: ⚙️ USER ACTION: "Re-öffne game, spiel revidierte Mission, bestätige Änderung sichtbar"
    12. User confirms: revision worked / revision not visible / new bug
  </action>

  <done_when>
    - narrative.json modified per user's revision
    - backend pipeline regenerated mission files
    - Re-validate PASS
    - User confirmed revision visible in-game (sc-3 met)
    - logs/revision-cycle-&lt;TS&gt;.json captured full diff + outcomes
  </done_when>

  <on_failure>
    - If user's revision needs creative interpretation (ambiguous): ask 1 clarifying question, max
    - If backend pipeline fails: escalate to Mac (Python error analysis needed)
    - If revision applied but not visible in-game: investigate ent-layer / gamemode-layer cross-reference
    - If new validation error: bug-fixer + Mac escalation
  </on_failure>

  <log_to>logs/revision-cycle-&lt;TS&gt;.json + narrative.json diff + regenerated files inventory</log_to>

</stage>

---

## STAGE 5 — Polish + Final Paper (10 min)

<stage id="5" name="final_paper">

  <action>
    1. Update WORK_LOG.md with sprint summary (append new section)
    2. Update README.md "Current Capability" section with confirmed end-to-end status
    3. Generate playbook/handoffs/final-paper-phase2-3-closeout-&lt;TS&gt;.md:
       - Goal achievement (sc-1 to sc-5 status)
       - Path traveled (5 stages summary)
       - Decisions made
       - Artifacts produced
       - Open questions / next steps (Phase 4? Plugin development? Additional missions?)
       - Cost breakdown (Sonnet tokens used, Opus escalations if any)
       - Known limitations explicit
    4. Final auditor pass: verify all stages logged, all artifacts in place
    5. Final reflection: logs/reflection-sprint-&lt;TS&gt;-pc.md
    6. STATE.json → PHASE_D_RETURN, sprint_complete=true
    7. Git add -A, commit, push
    8. Chat-output: "Sprint complete. Final paper: &lt;path&gt;. Pause for Mac review."
  </action>

  <done_when>
    - WORK_LOG.md updated
    - README.md updated
    - final-paper-&lt;TS&gt;.md exists with all sections filled
    - All logs committed + pushed
    - Reflection written
    - sc-4 + sc-5 met
  </done_when>

  <on_failure>
    - If push fails: retry up to 3 times (rebase if upstream changed)
    - If auditor flags issues: address before final push
  </on_failure>

  <log_to>logs/reflection-sprint-&lt;TS&gt;-pc.md + final-paper-*.md</log_to>

</stage>

---

<escalation_triggers>
  - Any stage's `<on_failure>` reaches "escalate to Mac"
  - 3× retry exhausted on any sub-step
  - User explicit "abort" / "stop" / "pause"
  - Token budget approaches 80% of 500k cap
  - Unknown error class (no pattern in CHEATSHEET-PC or PC's bug-history)
  - Mission-file change proposed that needs design decision (Mac territory)
</escalation_triggers>

<escalation_method>
  1. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_blocked=true, blocker=&lt;detail&gt;
  2. Write logs/escalation-&lt;TS&gt;.json with full context (which stage, what failed, attempts, evidence)
  3. git commit + push
  4. Chat-output: "Escalating to Mac. Blocker: &lt;1 sentence&gt;. Evidence: &lt;commit hash&gt;. Paste this in Mac chat to resume."
</escalation_method>

<sub_agents_enabled>
  <agent role="logger" always_on="true" output="logs/pc-events-sprint-&lt;TS&gt;.jsonl"/>
  <agent role="dep-installer" stage="1" output="logs/deps-sprint-&lt;TS&gt;.json"/>
  <agent role="ui-tester" stage="2,3,4" output="logs/ui-stage&lt;N&gt;-&lt;TS&gt;.json"/>
  <agent role="process-tracker" stages="1-5" trigger="long_process"/>
  <agent role="auditor" pre_push="true" per_stage="true"/>
  <agent role="bug-fixer" on_failure="true" output="logs/bugfix-stage&lt;N&gt;-&lt;TS&gt;.json"/>
  <agent role="loop-detector" on_retry="true"/>
</sub_agents_enabled>

<token_budgets>
  <per_stage_max>100000</per_stage_max>
  <total_max>500000</total_max>
  <escalate_at>400000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - step_time_budget = 5 min default (Stage 2/3/4 can override to 20 min)
  - sprint_time_budget = 90 min total
  - popup_count = 2 identical → auto-kill, do NOT dismiss (CS-like protection)
  - DRY marker required for any Remove-Item -Recurse op
</hard_guards>

<final_paper_template>
```markdown
# Final Paper — Phase 2-3 Closeout Sprint

> Stand: &lt;YYYY-MM-DD&gt;
> Sprint duration: &lt;X&gt; min
> Model: Sonnet 4.6 (Opus escalations: &lt;N&gt;)

## Goal Achievement

| Criterion | Status |
|---|---|
| sc-1 ≥1 mission GUI-loads | ✅/⏳/❌ |
| sc-2 game played ≥60s | ✅/⏳/❌ |
| sc-3 revision cycle works | ✅/⏳/❌ |
| sc-4 final paper generated | ✅ |
| sc-5 all pushed + WORK_LOG | ✅ |

## Path Traveled

| Stage | Duration | Outcome |
|---|---|---|
| 1 Preflight | X min | dep-install: X, env: ok |
| 2 GUI Smoke | X min | X/3 missions PASS |
| 3 Game Test | X min | user feedback: X |
| 4 Revision | X min | X→X applied, re-validate: X |
| 5 Polish | X min | docs updated |

## What Works

- &lt;list confirmed capabilities&gt;

## Known Limitations

- &lt;list explicit limitations from sprint findings&gt;

## Artifacts Produced

- &lt;file list&gt;

## Next Steps (Phase 4 candidates)

- &lt;suggestions for future work, e.g. plugin development,
  more missions, AI-driven creative revision, etc.&gt;

## Cost Breakdown

- Sonnet tokens: ~X · ~$Y
- Opus escalations: N · ~$Z
- Total: ~$W
- Estimated all-Opus cost would have been: ~$3W-5W

## Reflection

&lt;2-3 paragraphs honest assessment&gt;
```
</final_paper_template>

</sprint>

---

## Sprint Wrapper Prompt (für User zum Pasten in PC-Chat nach CS-End)

```
Du bist PC-Executor. CS ist beendet. Du führst jetzt einen kompletten
Phase 2-3 Closeout Sprint aus — alle 5 Stages end-to-end auf PC alleine.

Lies in dieser Reihenfolge:
1. playbook/RELAY_PROTOCOL.md (Two-Phase Reception, Sub-Agents, Guards)
2. PC_AGENT_BRIEF.md (deine Rolle, Pfade, Tools)
3. playbook/CHEATSHEET-PC.md (deine eigene empirische Wissensbasis)
4. playbook/handoffs/sprint-phase2-3-closeout.md ← der vollständige Sprint-Plan

Executiere Sprint Stages 1-5 strikt nach dem Plan.

User-Interaktion-Gates (warte auf User-Antwort):
- Stage 3 ⚙️ USER ACTION: User öffnet Game, spielt 1 min, bestätigt
- Stage 4 🧠 USER PROMPT: User gibt Revision-Wunsch + spielt revised mission

Escalate-to-Mac via git push + chat-pause wenn:
- Stage 2 zeigt 0/3 GUI smoke PASS
- Stage 4 backend pipeline fails (Python error)
- Jeder 3× retry exhausted ohne resolution
- Token budget > 80% von 500k

Sub-Agent-Fleet aktiv per RELAY_PROTOCOL: logger always-on, dep-installer pre-flight,
ui-tester pro GUI-launch, auditor pre-push, loop-detector on retry, bug-fixer on fail.

Final Paper: playbook/handoffs/final-paper-phase2-3-closeout-<TS>.md
Push everything continuously.

Modell-Check: ich bin auf Sonnet 4.6 (per User-Switch ab Task 006-CS).
Falls bei novel-bug Reasoning unzureichend → escalate via Stage's on_failure path.

Start mit Stage 1 (Preflight). Two-Phase Reception:
- Phase A: ⚙️ DO = "CS muss komplett zu sein" (BLOCKING) → User bestätigt
- Phase B: Verify keine CS/Workbench/Game-Prozesse aktiv
- Phase C: Stages 1-5 durchziehen
- Phase D: Final paper als single output zurück
```

---

## Notes für Sonnet während Execution

- Du folgst diesem Plan deterministisch. Wenn etwas ambiguous wird: kleines clarifying Q an User,
  max 1 pro Stage.
- Bei jedem Stage-Übergang: Auditor-Check + STATE.json-Update + commit-push (kleine Commits OK).
- Bei User-Action-Gate (Stage 3 + 4): klar formulieren WAS User tun soll, keine Verwirrung.
- Wenn User-Response unklar: nachfragen, nicht raten.
- Reflection-Pattern: am Ende jeder Stage 2-3 Zeilen in logs/reflection-sprint-stage&lt;N&gt;-pc.md
