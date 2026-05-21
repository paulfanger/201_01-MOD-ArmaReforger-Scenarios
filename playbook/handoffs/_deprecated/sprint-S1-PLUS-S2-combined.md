# Sprint S1+S2 Combined — Foundation + Autonomous Game (no CS, user absent, ~4-5h)

> Stand: 2026-05-21 · Model: Sonnet 4.6 (Opus escalation on novel-bug)
> User-state: CS NICHT aktiv + User NICHT am PC. Steam logged in. Vollautonom.
> Source: research/10-3-stage-sprint-design.md
> **This sprint runs S1 (Foundation) → transition → S2 (Autonomous Game) back-to-back in one
> session. Single wrapper prompt. PC owns the full loop until S3 (user-fallback) is needed.**

---

<sprint>

<context>
  <goal>
    Maximum-autonomy run: full foundation buildout (plugin refactor, backend, docker dedi,
    caching, memory, golden tests) PLUS autonomous game test in one continuous session.
    User pastes one prompt, comes back in 4-5h to either (a) green-light Sprint S3 or
    (b) review escalation from S2 game test.
  </goal>

  <success_criteria>
    <criterion id="sc-s1">All Sprint S1 criteria met (sc-1 to sc-10 from sprint-S1-headless-foundation.md)</criterion>
    <criterion id="sc-s2">All Sprint S2 criteria met (sc-1 to sc-8 from sprint-S2-autonomous-game.md)</criterion>
    <criterion id="sc-transition">Clean transition between S1 and S2 with state preservation</criterion>
    <criterion id="sc-combined-paper">Single final paper covering BOTH sprints with consolidated cost + reflection</criterion>
    <criterion id="sc-handoff-S3">If S2 escalates: clean handoff state file ready for user-S3-run</criterion>
  </success_criteria>

  <constraints>
    <constraint>CS-OFF Pflicht (im Gegensatz zu S1-alone)</constraint>
    <constraint>User-absent Pflicht (für S2-Phase)</constraint>
    <constraint>S2 darf NIE ohne S1-PASS starten (S1 stellt Voraussetzungen bereit)</constraint>
    <constraint>Bei S1-Escalation: STOP, schreib S3-handoff, NICHT S2 versuchen</constraint>
    <constraint>Bei S2-Escalation: S1-Arbeit ist trotzdem dauerhaft committed</constraint>
    <constraint>Sub-agent fleet active per RELAY_PROTOCOL.md</constraint>
    <constraint>DRY marker for destructive ops in beiden Phasen</constraint>
    <constraint>NEVER automate against BattlEye-protected sessions</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <model>claude-sonnet-4-6</model>
    <s1_plan>playbook/handoffs/sprint-S1-headless-foundation.md</s1_plan>
    <s2_plan>playbook/handoffs/sprint-S2-autonomous-game.md</s2_plan>
  </env>
</context>

---

## STAGE COMBINED.0 — Combined Pre-Flight

<stage id="C.0" name="combined_preflight">

  <action>
    Two-Phase Reception Phase A:
    User confirms BOTH conditions:
      ☐ CS is closed (not playing parallel)
      ☐ User is stepping away from PC (won't be available for clicks for 4-5h)

    Phase B verification:
    ```powershell
    # Verify no competing processes
    $blockers = Get-Process | Where-Object {
      $_.ProcessName -in @("cs2","csgo","ArmaReforgerSteam","ArmaReforgerServer","ArmaReforgerWorkbench")
    }
    if ($blockers) {
      Write-Output "BLOCKING: kill these first"
      $blockers | Stop-Process -Force
      Start-Sleep 5
    }

    # Confirm Steam logged in
    $steamRunning = Get-Process steam -ErrorAction SilentlyContinue
    if (-not $steamRunning) {
      Write-Warning "Steam not running — start Steam first"
      throw "Steam-required"
    }
    ```

    Initialize combined state:
    ```powershell
    $combinedState = @{
      turn_id = "S1+S2"
      owner = "pc"
      phase = "PHASE_C_EXEC"
      sub_sprint = "S1"  # currently in S1 portion
      started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
      s1_status = "queued"
      s2_status = "blocked_by_s1"
      escalations = @()
    } | ConvertTo-Json -Depth 5
    $combinedState | Set-Content "tasks\STATE.json" -Encoding UTF8
    ```

    Spawn logger (always-on for full 4-5h).
  </action>

  <done_when>
    - User confirmed both CS-off + away-absence
    - No competing processes
    - Steam alive
    - tasks/STATE.json initialized as "S1+S2"
    - Combined logger writing
  </done_when>

  <on_failure>
    - User says CS still on → abort, recommend sprint-S1-only (CS-compatible variant)
    - User can't confirm absence → abort, recommend Sprint S1 only
    - Steam not running → escalate ⚙️ DO: user starts Steam, retries
  </on_failure>

</stage>

---

## STAGE COMBINED.S1 — Execute Sprint S1 (Foundation)

<stage id="C.S1" name="execute_s1">

  <action>
    Execute ALL stages from `playbook/handoffs/sprint-S1-headless-foundation.md`:

    Stage 1.0 — Pre-Flight (skip Phase A since Combined.0 already covered it; skip dep-installer Phase A but still run install)
    Stage 1.1 — Plugin refactor (pseudocode → real WorldEditorAPI)
    Stage 1.2 — Schema-Mapping doc (playbook/SCHEMA_MAPPING.md)
    Stage 1.3 — Linux Docker Dedi-Validate setup (NOTE: this is Mac-side normally; PC just
      verifies the files exist after pull. If Mac not available, mark as deferred for S3.)
    Stage 1.4 — revise_mission backend API
    Stage 1.5 — Prompt caching wrapper
    Stage 1.6 — Episodic memory (~50 LOC SQLite FTS5)
    Stage 1.7 — Golden tests baseline
    Stage 1.8 — SETUP.md
    Stage 1.9 — Self-test pipeline run
    Stage 1.10 — S1 reflection + intermediate push

    Update tasks/STATE.json after each S1 stage:
    `$state.s1_progress = "stage X.Y completed"; $state | ConvertTo-Json | Set-Content...`

    Commit intermediate progress every 2-3 S1 stages (don't wait for full S1 completion to push).
  </action>

  <done_when>
    - All S1 success criteria sc-1 to sc-10 met (from sprint-S1-headless-foundation.md)
    - logs/reflection-turn-S1-pc.md written
    - tasks/STATE.json: s1_status="complete"
    - Multiple commits pushed
  </done_when>

  <on_failure>
    - Any S1 sub-stage escalates per its own escalation triggers
    - On S1 escalation: STOP sprint, do NOT proceed to S2
    - Write tasks/STATE.json: s1_status="escalated", s2_status="skipped_due_to_s1_fail"
    - Generate handoff for Sprint S3 (user resolves S1 blocker manually)
    - Push everything achieved so far
  </on_failure>

</stage>

---

## STAGE COMBINED.TRANSITION — S1 → S2 Gate

<stage id="C.TR" name="s1_s2_transition">

  <action>
    1. Audit S1 outputs:
       - All sc-1 to sc-10 from S1 met?
       - 111+ pytest still PASS?
       - revise_mission roundtrip works on golden trajectories?
       - Plugin compiles syntax-clean?
       - Docker dedi-validate works (if Mac-deferred — skip this check, proceed)?

    2. Decision:
       - All ✅ → proceed to S2
       - Any ❌ → STOP, write handoff for S3, escalate to user

    3. Update tasks/STATE.json:
       ```powershell
       $state.sub_sprint = "S2"
       $state.s1_status = "complete"
       $state.s2_status = "queued"
       $state.transition_time = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
       ```

    4. Write transition note to logs/transition-s1-s2-<TS>.md:
       - S1 summary (key outputs, time, token cost)
       - Ready-for-S2 confirmation
       - Any open warnings from S1 that S2 should be aware of

    5. Commit transition + intermediate push (so user can see progress if they check in)

    6. Brief pause (10s) between S1 and S2 to let logs settle.
  </action>

  <done_when>
    - S1 audit PASS
    - tasks/STATE.json reflects S2-start state
    - Transition note written + pushed
  </done_when>

  <on_failure>
    - Audit detects S1 incomplete → write S3 handoff, do NOT start S2, escalate to user
    - Auditor verdict "block" → respect block, escalate
  </on_failure>

</stage>

---

## STAGE COMBINED.S2 — Execute Sprint S2 (Autonomous Game)

<stage id="C.S2" name="execute_s2">

  <action>
    Execute ALL stages from `playbook/handoffs/sprint-S2-autonomous-game.md`:

    Stage 2.0 — Pre-Flight + Safety (skip Phase A — Combined.0 covered)
    Stage 2.1 — Local Dedi Server Spawn (THE TRICK)
    Stage 2.2 — Client Launch + Connect
    Stage 2.3 — Vision-Loop State Classification
    Stage 2.4 — Movement Test (PyDirectInput)
    Stage 2.5 — Clean Exit
    Stage 2.6 — Report + Reflection + Push

    Update tasks/STATE.json after each S2 stage:
    `$state.s2_progress = "stage 2.X completed"`

    NOTE: For sub-stages, use ui-tester multimodal classification heavily.
    Screenshots at 1280x800 (resize from native, see Take-ScreenshotResized helper).
  </action>

  <done_when>
    - All S2 success criteria sc-1 to sc-8 met (from sprint-S2-autonomous-game.md)
    - State trajectory captured: MainMenu → Loading → SpawnScreen → InGame → InGame_moved → MainMenu
    - 9+ screenshots in logs/
    - logs/reflection-turn-S2-pc.md written
    - tasks/STATE.json: s2_status="complete"
  </done_when>

  <on_failure>
    - Any S2 sub-stage escalates per its own escalation triggers
    - On S2 escalation: log evidence, generate S3-handoff (user resolves at PC)
    - S1 work remains committed (no rollback)
    - Push everything
  </on_failure>

</stage>

---

## STAGE COMBINED.FINAL — Consolidated Final Paper

<stage id="C.FINAL" name="combined_final">

  <action>
    Generate `playbook/handoffs/final-paper-sprint-S1S2-combined-<TS>.md`:

    Sections:
    1. Goal Achievement Matrix (sc-s1 + sc-s2 + sc-transition + sc-combined-paper + sc-handoff-S3)
    2. Sprint S1 Summary (10 stages outcome table)
    3. Transition Note
    4. Sprint S2 Summary (6 stages outcome table + state trajectory)
    5. Combined Cost Breakdown:
       - S1 tokens (mostly Sonnet, some Opus if escalations)
       - S2 tokens (Sonnet + vision-multimodal cost)
       - Sub-agent tokens
       - Total estimated cost vs all-Opus equivalent
    6. Reflections (both reflection files referenced)
    7. Known Limitations (from research/09)
    8. Open Questions for Sprint S3:
       - Workshop publish?
       - Creative judgment ratings?
       - Revision wishes?
    9. Next Action für User: "Wenn du wieder am PC bist, paste den Sprint-S3-Wrapper-Prompt
       in PC-Chat → ich finalisier den Loop mit dir."

    Write logs/reflection-combined-S1S2-pc.md:
    - What worked across both sprints
    - What needed transition adjustments
    - Performance signals for optimizer

    log_episode via episodic.py for each combined-stage outcome.

    Update tasks/STATE.json:
    ```json
    {
      "turn_id": "S1+S2",
      "owner": "pc",
      "phase": "PHASE_D_RETURN",
      "sub_sprint": "S3-ready",
      "s1_status": "complete",
      "s2_status": "complete" or "escalated",
      "ready_for_s3": true,
      "finished_at": "<TS>"
    }
    ```

    Final commit + push:
    `git commit -m "Combined Sprint S1+S2 complete — ready for user S3"`
  </action>

  <done_when>
    - final-paper-sprint-S1S2-combined-<TS>.md exists with all sections
    - reflection-combined-S1S2-pc.md written
    - episodic.jsonl + DB updated with combined-sprint episodes
    - tasks/STATE.json: ready_for_s3=true
    - All commits pushed
    - Chat output: "Combined Sprint S1+S2 complete. Ready for Sprint S3 when you're back at PC. Paste sprint-S3-wrapper to resume."
  </done_when>

</stage>

---

<escalation_triggers>
  - S1 escalation → skip S2, hand off to S3
  - S2 escalation → S1 work preserved, hand off to S3 with S2-blocker context
  - Both sprints hit token budget (>450k combined) → escalate
  - Total runtime > 6h → escalate (something is fundamentally stuck)
  - User accidentally returns and interrupts mid-S2 → graceful pause, snapshot state
</escalation_triggers>

<escalation_method>
  1. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_blocked=true,
     blocker_sub_sprint="S1" or "S2", blocker_stage="<X.Y>"
  2. Write logs/escalation-combined-<TS>.json with full context
  3. Take diagnostic screenshot if GUI-related blocker
  4. Generate playbook/handoffs/handoff-to-s3-<TS>.md:
     - What S1 achieved (preserved)
     - What S2 attempted + where it failed
     - Proposed S3 actions to resolve
     - Suggested user-checklist
  5. git commit + push
  6. Output to chat:
     "Sprint S1+S2 blocked at <sub-sprint>.<stage>. Evidence: <commit>.
      S1 work preserved. S3 handoff: <handoff-path>.
      Paste sprint-S3-wrapper when back at PC to resolve."
</escalation_method>

<sub_agents_enabled>
  <agent role="logger" always_on="true" full_session="true"/>
  <agent role="dep-installer" stages="C.0,C.S1.1.0,C.S2.2.0" model="haiku"/>
  <agent role="process-tracker" stages="C.S2.2.1,C.S2.2.2" trigger="long_process"/>
  <agent role="ui-tester" stages="C.S2.2.3,C.S2.2.4,C.S2.2.5" model="sonnet" multimodal="true"/>
  <agent role="auditor" pre_push="true" per_stage="true" model="sonnet"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <agent role="loop-detector" on_retry="true"/>
  <agent role="optimizer" post_s1_success="true" post_s2_success="true" model="sonnet"/>
</sub_agents_enabled>

<token_budgets>
  <s1_max>500000</s1_max>
  <s2_max>400000</s2_max>
  <combined_max>800000</combined_max>
  <escalate_at>640000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - step_time_budget_default = 30 min
  - sprint_time_budget = 6 hr total (4h S1 + 30 min S2 + buffer)
  - resolution_cap = 1280x800 (for S2 vision-loop)
  - DRY marker required for destructive ops
  - NEVER automate against BattlEye-protected sessions (Stage S2 hard rule)
  - NO S2 start without S1 PASS
</hard_guards>

</sprint>

---

## Wrapper Prompt (paste in PC chat — single trigger for full S1+S2 run)

```
Du bist PC-Executor. CS ist beendet. User ist NICHT am PC für die nächsten 4-5h.
Sprint S1+S2 Combined — Foundation + Autonomous Game in einer Session.
Sonnet 4.6 default. Maximum-Autonomie.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/RELAY_PROTOCOL.md (Two-Phase, Sub-Agents, Guards)
3. PC_AGENT_BRIEF.md (Sonnet-compatibility, PowerShell pitfalls)
4. playbook/CHEATSHEET-PC.md (empirische Wissensbasis)
5. research/10-3-stage-sprint-design.md (Stage definitions + critical discoveries)
6. playbook/handoffs/sprint-S1-headless-foundation.md (S1 plan, 10 stages)
7. playbook/handoffs/sprint-S2-autonomous-game.md (S2 plan, 6 stages)
8. playbook/handoffs/sprint-S1-PLUS-S2-combined.md ← THIS plan (combined wrapper)

Critical knowledge (from research):
- Reforger uses BattlEye, NOT EAC. BE-OFF in SP/local-dedi. Input simulation SAFE.
- NO -scenario CLI flag for client — Local Dedi Server + -client -connect=127.0.0.1 is THE trick
- PyDirectInput (NOT PyAutoGUI — DirectX game)
- Screenshots 1280x800 (Anthropic vision-tool requirement)
- Bohemia samples have real WorldEditorAPI (NOT pseudocode we currently have)

Execute Stages Combined.0 → Combined.S1 → Combined.TR → Combined.S2 → Combined.FINAL.

Two-Phase Reception:
- Phase A: ⚙️ DO = User confirms BOTH:
    ☐ CS is closed
    ☐ User is away from PC for next 4-5h
- Phase B: Verify no competing processes + Steam alive
- Phase C: Combined.S1 (~3-4h) → Combined.TR (~5 min) → Combined.S2 (~20-30 min)
- Phase D: Combined.FINAL (single consolidated paper for both sprints)

Key transition rules:
- S1 → S2: only if S1 PASS. If S1 escalates, STOP, write S3 handoff, do NOT attempt S2.
- S2 → FINAL: regardless of S2 outcome (S1 preserved either way)
- On any sprint escalation: graceful handoff to S3 (user-fallback)

Escalation triggers (escalate-to-S3, user resolves at PC when back):
- S1 escalations per sprint-S1 plan
- S2 escalations per sprint-S2 plan
- Combined token budget >640k
- Total runtime >6h

Sub-Agent-Fleet aktiv per RELAY_PROTOCOL.md throughout entire session:
- logger always-on (full 4-5h)
- dep-installer at pre-flight + S2 setup
- process-tracker for S2 server/client launches
- ui-tester multimodal for S2 vision-loop + classification
- auditor pre-push per stage
- bug-fixer on-failure with always-propose-options
- loop-detector on every retry
- optimizer post-success

DRY marker for any destructive op in both phases.

Final Paper: playbook/handoffs/final-paper-sprint-S1S2-combined-<TS>.md
Intermediate commits every 2-3 S1 stages, final commit at FINAL.
Push continuously.

Start with Stage Combined.0 (Pre-Flight). Two-Phase Reception erst, dann full run.
```

---

## Comparison: when to use which sprint

| Sprint | Trigger | Duration | CS | User-at-PC | What it does |
|---|---|---|---|---|---|
| **S1 only** (`sprint-S1-headless-foundation.md`) | CS running | ~3-4h | ✅ läuft parallel | ✅ kann am PC sein, klickt aber nicht | Foundation work (plugin, backend, docker, caching, memory, tests, docs) |
| **S1+S2 Combined** (THIS file) | CS off, user away | ~4-5h | ❌ aus | ❌ nicht da | S1 + autonomous game test in einem Rutsch |
| **S2 only** (`sprint-S2-autonomous-game.md`) | S1 already done, user away | ~30 min | ❌ aus | ❌ nicht da | Just the autonomous game test |
| **S3** (`sprint-S3-user-fallback.md`) | User at PC | ~10-15 min | egal | ✅ ja | Manual fallback + creative judgment + Workshop |
| **Phase 2-3 Closeout** (`sprint-phase2-3-closeout.md`) | After Sprint S1 done, user at PC | ~60-90 min | egal | ✅ teilweise | Original sprint plan (manual GUI smoke + game test + revision cycle) |

**For maximum autonomy: paste S1+S2 Combined wrapper, come back in 4-5h.**
**For minimum risk: paste S1 only, then later S2, then S3.**
