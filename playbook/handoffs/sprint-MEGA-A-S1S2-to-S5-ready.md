# Sprint MEGA-A — S1+S2 with S5 End-Goal (PC-only, autonomous, ~5-7h)

> Stand: 2026-05-21 · Model: Sonnet 4.6 (Opus escalation only on novel architectural decisions)
> User-state: CS aus, User abwesend für 5-7h
> Source: research/11-s5-readiness-roadmap.md
> **End-state target:** PC is FULLY ready to build live-editor plugin in Sprint B (S3-S5).
> All Sprint S1+S2 capabilities PLUS plugin-dev environment + Bohemia samples cloned +
> first sample plugin compiles + AI_GeneratePlugin.c refactored with REAL API stubs.

---

<sprint>

<context>
  <goal>
    Bridge from current "validate-gate stable" state to "ready to build S5 live editor".
    Combines all of Sprint S1 (foundation work) + Sprint S2 (autonomous game test) +
    NEW S5-prep work (plugin dev environment, sample plugin verification, AI_GeneratePlugin
    real-API refactor with TODO markers). Single prompt-paste, ~5-7h autonomous PC time.
  </goal>

  <success_criteria>
    <!-- S1 Foundation criteria -->
    <criterion id="sc-1">backend/routes/revisions.py with JSON-Patch + jsonschema, pytest PASS</criterion>
    <criterion id="sc-2">backend/llm/__init__.py cached_completion() with Anthropic Prompt Caching</criterion>
    <criterion id="sc-3">backend/memory/episodic.py (~50 LOC SQLite FTS5), pytest PASS</criterion>
    <criterion id="sc-4">tests/golden/ baseline + revision trajectory, regression PASS</criterion>
    <criterion id="sc-5">scripts/docker-validate.sh + backend/scripts/validate_dedi.py (Linux dedi)</criterion>
    <criterion id="sc-6">playbook/SCHEMA_MAPPING.md complete (narrative.json → WorldEditorAPI)</criterion>
    <criterion id="sc-7">SETUP.md (Mac+PC replication)</criterion>
    <criterion id="sc-8">111+ backend tests still PASS</criterion>

    <!-- S2 Game Test criteria -->
    <criterion id="sc-9">Local dedi server + client-connect tested: state trajectory MainMenu→Loading→SpawnScreen→InGame→InGame_moved→MainMenu</criterion>
    <criterion id="sc-10">PyDirectInput WASD test confirmed working (scene-diff)</criterion>
    <criterion id="sc-11">9 screenshots + 9 ui-tester classifications captured</criterion>

    <!-- NEW S5-Prep criteria -->
    <criterion id="sc-12">Plugin dev tools installed: VSCode + Enforce extensions + chokidar-cli + npm</criterion>
    <criterion id="sc-13">Bohemia samples cloned: Arma-Reforger-Samples + Arma-Reforger-Script-Diff</criterion>
    <criterion id="sc-14">SampleWorldEditorPlugin.c compiles + runs in Workbench (proof-of-concept)</criterion>
    <criterion id="sc-15">workbench-plugin/AI_GeneratePlugin.c refactored with REAL WorldEditorAPI method names (TODO markers OK for unimplemented logic)</criterion>
    <criterion id="sc-16">File-watch infrastructure scaffolded (chokidar+sendkey OR PowerShell FileSystemWatcher)</criterion>

    <!-- Combined -->
    <criterion id="sc-17">Final paper: playbook/handoffs/final-paper-MEGA-A-<TS>.md with S5-readiness assessment</criterion>
    <criterion id="sc-18">tasks/STATE.json ready_for_sprint_B=true</criterion>
  </success_criteria>

  <constraints>
    <constraint>CS aus, User abwesend Pflicht</constraint>
    <constraint>NO functional plugin implementation — only spec refactor + sample compile + env setup</constraint>
    <constraint>S5-prep work additive, not blocking S1+S2 core</constraint>
    <constraint>Sub-agent fleet full per RELAY_PROTOCOL.md</constraint>
    <constraint>DRY marker for destructive ops</constraint>
    <constraint>NEVER automate against BattlEye-protected sessions</constraint>
    <constraint>Sub-agent depth ≤3 levels (orchestrator → siblings → utility)</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <model>claude-sonnet-4-6</model>
    <session_target>5-7h autonomous</session_target>
  </env>
</context>

---

## STAGE A.0 — Pre-Flight + Combined Setup (~10 min)

<stage id="A.0" name="preflight">

  <action>
    Phase A: User confirms BOTH:
      ☐ CS closed
      ☐ User absent for 5-7h
      ☐ Steam logged in
    Phase B: Verify no competing processes, Steam alive

    Spawn logger (always-on for full session).

    dep-installer pre-flight (autonomous, per Devin blueprint):
    ```powershell
    # Core dev tools
    winget install --id Git.Git -e --accept-package-agreements
    winget install --id Microsoft.VisualStudioCode -e
    winget install --id GitHub.cli -e
    winget install --id OpenJS.NodeJS.LTS -e
    winget install --id Python.Python.3.12 -e

    # VSCode extensions
    code --install-extension YouAreBamboozled.enforce-vscode-plugin
    code --install-extension YouAreBamboozled.enforce-script-syntax-highlighting
    code --install-extension ms-vscode.powershell

    # npm + pip
    npm install -g chokidar-cli
    pip install jsonpatch jsonschema anthropic pytest pydirectinput pillow
    ```

    Update tasks/STATE.json: turn_id="MEGA-A", phase=PHASE_C_EXEC, owner=pc.
    Initialize episodic memory (will be created in stage A.S1.6).
  </action>

  <done_when>
    - All deps installed + version-verified
    - VSCode extensions confirmed via `code --list-extensions`
    - chokidar-cli available via `chokidar --version`
    - Python 3.12+ + pip packages installed
    - tasks/STATE.json updated
  </done_when>

  <on_failure>
    - winget package not found → research alternative ID via `winget search`
    - npm/pip offline → escalate ⚙️ DO retry
    - VSCode extension install fail → log + continue (non-blocking)
  </on_failure>

</stage>

---

## STAGE A.S1 — Foundation (~3-4h)

<stage id="A.S1" name="s1_foundation">

  <action>
    Execute ALL S1 stages from sprint-S1-headless-foundation.md:

    Sub-stage A.S1.1 — Plugin Refactor (pseudocode → real API)
      → use SampleWorldEditorPlugin.c from Bohemia samples as reference
      → AI_GeneratePlugin.c gets REAL WorldEditorAPI method names
      → TODO markers for unimplemented logic (functional impl is Sprint B)

    Sub-stage A.S1.2 — SCHEMA_MAPPING.md (narrative.json → API calls table)

    Sub-stage A.S1.3 — Linux Docker Dedi setup
      → NOTE: this is Mac-side. PC verifies files exist post-pull.
      → If Mac unreachable: defer with note in result

    Sub-stage A.S1.4 — backend/routes/revisions.py (JSON-Patch + jsonschema)

    Sub-stage A.S1.5 — backend/llm/__init__.py cached_completion()

    Sub-stage A.S1.6 — backend/memory/episodic.py (~50 LOC + tests)
      → Bootstrap: import existing logs/reflection-turn-*.md files as historical episodes

    Sub-stage A.S1.7 — tests/golden/ baseline (night-recon + 1 revision trajectory)

    Sub-stage A.S1.8 — SETUP.md replication guide

    Sub-stage A.S1.9 — Self-test pipeline run (pytest + docker-validate if Mac done it)

    Sub-stage A.S1.10 — reflection-turn-MEGA-A-S1-pc.md + intermediate commit/push

    Commit intermediate every 2-3 sub-stages.
  </action>

  <done_when>
    - sc-1 to sc-8 from criteria all met
    - intermediate commits pushed
    - reflection written
  </done_when>

  <on_failure>
    - Per individual S1 sub-stage on_failure rules (see sprint-S1)
    - On hard escalation: STOP, do NOT proceed to A.S2, write handoff for S3
  </on_failure>

</stage>

---

## STAGE A.S2 — Autonomous Game Test (~30 min)

<stage id="A.S2" name="s2_autonomous_game">

  <skip_if>S1 escalated</skip_if>

  <action>
    Execute ALL S2 stages from sprint-S2-autonomous-game.md:

    Sub-stage A.S2.1 — Local Dedi Server spawn (config: night-recon-everon)
    Sub-stage A.S2.2 — Client launch -client -connect=127.0.0.1
    Sub-stage A.S2.3 — Vision-loop state classification (1280x800 resize)
    Sub-stage A.S2.4 — PyDirectInput WASD movement test
    Sub-stage A.S2.5 — Clean exit
    Sub-stage A.S2.6 — reflection-turn-MEGA-A-S2-pc.md + commit/push
  </action>

  <done_when>
    - sc-9 to sc-11 met
    - State trajectory captured + 9 screenshots
    - reflection written
  </done_when>

  <on_failure>
    - Per individual S2 sub-stage on_failure rules
    - S1 work preserved regardless
  </on_failure>

</stage>

---

## STAGE A.S5PREP — Plugin Dev Environment (~1-2h)

<stage id="A.S5PREP" name="s5_prep">

  <action>
    NEW work — sets up everything Sprint B needs for live-editor build.

    Sub-stage A.S5PREP.1 — Clone Bohemia Samples
    ```powershell
    cd $env:USERPROFILE\Documents\GitHub  # create if missing
    gh repo clone BohemiaInteractive/Arma-Reforger-Samples
    gh repo clone BohemiaInteractive/Arma-Reforger-Script-Diff
    ```
    Document file paths in playbook/CHEATSHEET-PC.md update.

    Sub-stage A.S5PREP.2 — Study sample plugin source
    Read 5 critical files (per research/11):
    - SampleMod_WorkbenchPlugin/Scripts/.../SampleWorldEditorPlugin.c
    - SampleMod_WorkbenchPlugin/addon.gproj
    - Script-Diff/.../WorkbenchPlugin.c (base class)
    - Script-Diff/.../WorldEditorPlugin.c (event hooks)
    - Script-Diff/.../Workbench.c (utilities)
    Write 2-sentence summary per file in logs/sample-plugin-study-A.md.

    Sub-stage A.S5PREP.3 — Verify sample plugin compiles
    Open SampleMod_WorkbenchPlugin in Workbench-Diag (GUI):
    ```powershell
    $diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
    $sampleAddon = "$env:USERPROFILE\Documents\GitHub\Arma-Reforger-Samples\SampleMod_WorkbenchPlugin\addon.gproj"
    Start-Process -FilePath $diag -ArgumentList @("-gproj", "`"$sampleAddon`"")
    Start-Sleep 30
    Take-Screenshot -OutPath "logs/sample-plugin-compile-check.png"
    # ui-tester classifies: did Workbench open? plugin loaded? errors?
    ```
    Verify: SamplePlugins menu entries appear in Plugins menu.

    Sub-stage A.S5PREP.4 — Refactor AI_GeneratePlugin.c with REAL API
    Replace pseudocode `CreateEntity()` etc. with real WorldEditorAPI signatures from
    Script-Diff repo. Use TODO markers for unimplemented logic. File MUST be syntax-clean
    (would pass -validate compile gate).

    Spec the file-watch architecture as comment block at top:
    ```
    // ai-spec.json schema:
    // { mission_id, version, ops: [{op, class, prefab_guid, coords, props}] }
    //
    // Reload mechanism: external chokidar watcher detects file change,
    // PowerShell SendKeys pushes Ctrl+Shift+R into Workbench window,
    // plugin's Run() method reads ai-spec.json and applies ops.
    //
    // Realistic latency: 1-2s with sendkey hack, 5-10s with manual hotkey
    ```

    Sub-stage A.S5PREP.5 — File-watch scaffold (chokidar OR PowerShell)
    Create scripts/file-watcher.ps1:
    ```powershell
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\profile\elos"
    $watcher.Filter = "ai-spec.json"
    $watcher.IncludeSubdirectories = $false
    $watcher.EnableRaisingEvents = $true

    $action = {
      Add-Type -AssemblyName System.Windows.Forms
      Start-Sleep -Milliseconds 100
      # Bring Workbench to foreground first
      $wb = Get-Process | Where-Object { $_.ProcessName -like "*Workbench*" } | Select-Object -First 1
      if ($wb) {
        [Microsoft.VisualBasic.Interaction]::AppActivate($wb.Id) | Out-Null
        Start-Sleep -Milliseconds 200
        [System.Windows.Forms.SendKeys]::SendWait("^+R")
      }
    }
    Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
    Write-Output "File watcher running. Watching: $($watcher.Path)\$($watcher.Filter)"
    ```
    Test: write a dummy ai-spec.json change, verify SendKeys fires.

    Sub-stage A.S5PREP.6 — Document Sprint B Prerequisites
    Write logs/sprint-b-prerequisites-A.md listing:
    - Tool versions confirmed
    - Bohemia samples local paths
    - Sample plugin compile verified yes/no
    - AI_GeneratePlugin.c real-API refactor: complete with X TODOs
    - File-watch scaffold tested yes/no
    - Open questions for Mac-side audit
  </action>

  <done_when>
    - sc-12 to sc-16 met
    - logs/sample-plugin-study-A.md exists
    - logs/sample-plugin-compile-check.png shows successful load
    - workbench-plugin/AI_GeneratePlugin.c syntactically valid with real API names
    - scripts/file-watcher.ps1 tested + working
    - logs/sprint-b-prerequisites-A.md complete
  </done_when>

  <on_failure>
    - Sample plugin won't compile → escalate: would block Sprint B entirely
    - VSCode Enforce extension throws errors → check API compatibility, log
    - SendKeys doesn't reach Workbench → switch to PyDirectInput / nircmd fallback
  </on_failure>

</stage>

---

## STAGE A.FINAL — Consolidated Final Paper (~10 min)

<stage id="A.FINAL" name="combined_final">

  <action>
    1. Aggregate all stage outputs
    2. Generate playbook/handoffs/final-paper-MEGA-A-<TS>.md:
       - Goal Achievement Matrix (sc-1 to sc-18)
       - S1 Foundation Summary (10 sub-stages outcome table)
       - S2 Game Test Summary (6 sub-stages outcome + state trajectory)
       - S5-Prep Summary (6 sub-stages + tool inventory + sample compile result)
       - Combined Cost Breakdown (Sonnet/Haiku/Opus token use)
       - Reflections (3 reflection files referenced)
       - **S5-Readiness Assessment** — most important section:
         * Plugin dev env: ready / blocked
         * Sample plugin compiles: yes / no
         * AI_GeneratePlugin refactor: complete with N TODOs
         * File-watch: tested / broken
         * Open questions for Mac-side audit
       - Known limitations
       - Next action: "Mac-side audit can begin"

    3. Write logs/reflection-MEGA-A-pc.md (combined)
    4. log_episode for combined-stage outcomes
    5. Update tasks/STATE.json: ready_for_audit=true, ready_for_sprint_B=true_if_no_escalations
    6. Final commit + push
    7. Chat output: "Sprint MEGA-A complete. Ready for Mac-side audit. Type 'audit go' in Mac chat to proceed."
  </action>

  <done_when>
    - Final paper exists with all sections
    - reflection-MEGA-A-pc.md written
    - episodic.jsonl updated
    - tasks/STATE.json: ready_for_audit=true
    - All commits pushed
  </done_when>

</stage>

---

<escalation_triggers>
  - S1 escalation → STOP, do NOT attempt S2 or S5PREP, full S3 handoff
  - S2 escalation → S1 + S5PREP still preserved, partial handoff
  - S5PREP escalation (sample plugin won't compile) → critical, Mac must audit ASAP
  - Combined token budget > 800k
  - Total runtime > 8h
  - Stuck-detector: 4× same error-class on any stage → researcher subagent → 2 more turns → escalate
</escalation_triggers>

<escalation_method>
  1. tasks/STATE.json: phase=PHASE_D_RETURN, blocker_stage=<X>, ready_for_audit=true (Mac
     should audit even on partial completion)
  2. Write logs/escalation-MEGA-A-<TS>.json
  3. Take diagnostic screenshot if GUI-related
  4. git commit + push
  5. Chat output: "MEGA-A blocked at <stage>. Audit + Mac-Opus decision needed.
     Type 'audit go' to proceed."
</escalation_method>

<sub_agents_enabled>
  <agent role="logger" always_on="true" full_session="true"/>
  <agent role="dep-installer" stages="A.0" model="haiku"/>
  <agent role="process-tracker" stages="A.S2,A.S5PREP" model="haiku"/>
  <agent role="ui-tester" stages="A.S2,A.S5PREP" model="sonnet" multimodal="true"/>
  <agent role="enforce-researcher" stages="A.S5PREP" model="sonnet"/>
  <agent role="auditor" pre_push="true" per_stage="true" model="sonnet"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <agent role="loop-detector" on_retry="true"/>
  <agent role="optimizer" post_success="true" model="sonnet"/>
</sub_agents_enabled>

<token_budgets>
  <s1_max>500000</s1_max>
  <s2_max>200000</s2_max>
  <s5prep_max>200000</s5prep_max>
  <combined_max>800000</combined_max>
  <escalate_at>640000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - step_time_budget_default = 30 min
  - sprint_time_budget = 8h total (5-7h target + 1h buffer)
  - resolution_cap = 1280x800 (for vision-loop in S2)
  - DRY marker required for destructive ops
  - NEVER automate against BattlEye-protected sessions
  - NO functional plugin implementation in MEGA-A (that's Sprint B)
  - Sub-agent depth ≤ 3 (L1 orchestrator → L2 siblings → L3 utility)
</hard_guards>

</sprint>

---

## Wrapper Prompt — paste ONCE in PC chat after CS done + you step away

```
Du bist PC-Executor. CS aus. User abwesend für 5-7h.
Sprint MEGA-A — S1+S2+S5-PREP in einer Session.
Sonnet 4.6 default. Goal: PC ist S5-ready für Sprint B.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/RELAY_PROTOCOL.md
3. PC_AGENT_BRIEF.md
4. playbook/CHEATSHEET-PC.md
5. research/10-3-stage-sprint-design.md (Stage definitions)
6. research/11-s5-readiness-roadmap.md ← CRITICAL: no native OnUpdate, sendkey hack, etc.
7. playbook/handoffs/sprint-S1-headless-foundation.md (S1 sub-stages)
8. playbook/handoffs/sprint-S2-autonomous-game.md (S2 sub-stages)
9. playbook/handoffs/sprint-MEGA-A-S1S2-to-S5-ready.md ← THIS plan

Critical knowledge:
- BattlEye-OFF for SP/local-dedi → automation safe
- Local Dedi Server + -client -connect=127.0.0.1 bypasses Reforger menu
- PyDirectInput (NOT PyAutoGUI — DirectX game)
- Screenshots 1280x800 (Anthropic vision-tool requirement)
- Plugins have NO native OnUpdate — file-watch via external chokidar+sendkey
- Bohemia samples at SampleMod_WorkbenchPlugin/Scripts/WorkbenchGame/SamplePlugins/
- Realistic plugin latency: 1-2s (sendkey) / 5-10s (manual hotkey)

Execute Stages A.0 → A.S1 → A.S2 → A.S5PREP → A.FINAL strictly per plan.

Two-Phase Reception:
- Phase A: ⚙️ DO = User confirms BOTH: CS aus + abwesend 5-7h + Steam logged in
- Phase B: Verify no competing processes
- Phase C: A.0 → A.S1 (~3-4h) → A.S2 (~30min) → A.S5PREP (~1-2h)
- Phase D: A.FINAL — consolidated paper

Transition rules:
- A.S1 escalation → STOP, no A.S2 attempt, full S3 handoff
- A.S2 escalation → A.S1 + A.S5PREP still preserved
- A.S5PREP escalation (sample plugin won't compile) → critical, write detailed blocker
- Combined token >640k OR runtime >8h → graceful escalate

Sub-Agent-Fleet (full session): logger always-on, dep-installer pre-flight,
process-tracker for game launches, ui-tester multimodal for vision,
enforce-researcher for plugin work, auditor pre-push, bug-fixer on-fail,
loop-detector on every retry, optimizer post-success.

Sub-agent depth ≤3 levels (L1 orchestrator → L2 siblings parallel DAG → L3 utility).

DRY marker for destructive ops (addon cleanup, etc.).
NEVER automate against BattlEye-protected sessions.
NO functional plugin implementation in MEGA-A (Sprint B does that).

Final Paper: playbook/handoffs/final-paper-MEGA-A-<TS>.md
Intermediate commits every 2-3 sub-stages, final commit at FINAL.

When done: chat output "Sprint MEGA-A complete. Type 'audit go' in Mac chat."

Start with Stage A.0.
```
