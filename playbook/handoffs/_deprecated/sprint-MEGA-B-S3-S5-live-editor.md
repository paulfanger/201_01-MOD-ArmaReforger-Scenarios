# Sprint MEGA-B — S3-S5 Live Editor Build (PC, autonomous, ~6-10h)

> Stand: 2026-05-21 (initial draft, refined by Mac-Side Audit Pattern post-MEGA-A)
> Model: Sonnet 4.6 (default) with Opus escalation only on architectural decisions
> User-state: CS aus, User abwesend für 6-10h
> Source: research/11-s5-readiness-roadmap.md
> **End-state target:** S5 live editor MVP — user types prompt → 1-2s later mission
> changes appear in 3D Workbench editor. 95%+ reliability over 100 randomized prompts.

> ⚠️ **This is the initial draft.** The Mac-Side Audit Pattern
> (`audit-pattern-opus-S5-plan.md`) refines this plan POST-MEGA-A. Wait for audit
> output before triggering this sprint.

---

<sprint>

<context>
  <goal>
    Build the live-editor MVP autonomously. AI_GeneratePlugin.c becomes functional,
    file-watch hot-reload works, all 5 op types supported (attribute-edit, entity-create,
    entity-delete, entity-move, batch), 95%+ reliability over 100 randomized prompts.
    User only needed at very end for creative-judgment + final approval (S3 fallback).
  </goal>

  <success_criteria>
    <criterion id="sc-B1">AI_GeneratePlugin.c FUNCTIONAL (compiles + runs + applies ops to .ent)</criterion>
    <criterion id="sc-B2">File-watch hot-reload working: ai-spec.json change → plugin executes within 5s manual / 2s sendkey</criterion>
    <criterion id="sc-B3">All 5 op types supported: attribute-edit, entity-create, entity-delete, entity-move, batch (≥3 ops in one prompt)</criterion>
    <criterion id="sc-B4">Reliability: 10 consecutive revision-cycles, 0 manual interventions</criterion>
    <criterion id="sc-B5">Reliability extended: ≥95% over 100 randomized fuzzer prompts</criterion>
    <criterion id="sc-B6">Round-trip integrity: post-revision mission re-loads, entity-count delta = expected</criterion>
    <criterion id="sc-B7">Stability soak: 50 sequential revisions without Workbench restart</criterion>
    <criterion id="sc-B8">UX naturalness: 5 NL paraphrases of same intent → same diff (paraphrase test)</criterion>
    <criterion id="sc-B9">Latency P50 ≤ 2.0s with sendkey hack OR ≤ 5.0s with manual hotkey</criterion>
    <criterion id="sc-B10">Latency P95 ≤ 3.5s sendkey / ≤ 8s manual</criterion>
    <criterion id="sc-B11">tests/s5/ contains 50+ golden trajectories + property-based fuzzer</criterion>
    <criterion id="sc-B12">readiness-reporter green verdict on full §criteria sweep</criterion>
    <criterion id="sc-B13">Stage 3 user-gate prepared (creative judgment + 5 NL prompts UX session)</criterion>
    <criterion id="sc-B14">Final paper: playbook/handoffs/final-paper-MEGA-B-<TS>.md</criterion>
  </success_criteria>

  <constraints>
    <constraint>MEGA-A must be complete + audit done</constraint>
    <constraint>CS aus, User abwesend Pflicht</constraint>
    <constraint>BattlEye OFF (SP/Workbench/local-dedi only)</constraint>
    <constraint>Sub-agent depth ≤3 levels (per research/07 §6)</constraint>
    <constraint>3-layer iteration loop: Inner (sec) / Middle (min) / Outer (hr)</constraint>
    <constraint>Stuck-detector strict (4× same error-class → researcher → escalate)</constraint>
    <constraint>Token budget hard cap 1M for entire sprint</constraint>
    <constraint>DRY marker for destructive ops</constraint>
    <constraint>NEVER modify mission narrative.json without explicit user prompt</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <plugin>workbench-plugin/AI_GeneratePlugin.c</plugin>
    <test_addon>workbench-plugin/test-addon</test_addon>
    <samples>$env:USERPROFILE\Documents\GitHub\Arma-Reforger-Samples</samples>
    <script_diff>$env:USERPROFILE\Documents\GitHub\Arma-Reforger-Script-Diff</script_diff>
    <model>claude-sonnet-4-6</model>
  </env>
</context>

---

## STAGE B.0 — Pre-Flight (MEGA-A artifacts verify)

<stage id="B.0" name="preflight">

  <action>
    Phase A: User confirms CS aus + abwesend 6-10h + MEGA-A audit done
    Phase B: Verify all MEGA-A artifacts present:
      - workbench-plugin/AI_GeneratePlugin.c (refactored with real API + TODOs)
      - $env:USERPROFILE\Documents\GitHub\Arma-Reforger-Samples (cloned)
      - logs/sample-plugin-compile-check.png (compiles confirmed)
      - scripts/file-watcher.ps1 (scaffolded)
      - backend/routes/revisions.py (revise_mission live)
      - tests/golden/ (baseline regression)
      - memory/episodic.db (cross-session learning)

    Update tasks/STATE.json: turn_id="MEGA-B", phase=PHASE_C_EXEC, sprint_B_active=true.
    Spawn logger + enforce-researcher (always-on for full session).
  </action>

  <done_when>
    - All MEGA-A artifacts verified present
    - STATE.json updated
    - Loggers spawned
  </done_when>

  <on_failure>
    - Missing MEGA-A artifact → STOP, escalate to Mac (audit incomplete)
    - Plugin compile broken → STOP, fix needed before B.1
  </on_failure>

</stage>

---

## STAGE B.1 — Plugin Functional Implementation (Inner Loop)

<stage id="B.1" name="plugin_implementation">

  <action>
    Implement AI_GeneratePlugin.c functionally. Use 3-layer iteration loop:

    INNER LOOP (per-op-implementation, ~sec):
    For each of 5 op types [attribute-edit, entity-create, entity-delete, entity-move, batch]:
      1. Code op handler in plugin
      2. Compile via -validate
      3. Fire 1 canonical test (write ai-spec.json with this op)
      4. Trigger plugin via headless Workbench-Diag -plugin=AI_GeneratePlugin
      5. Parse plugin log for OK/ERR
      6. diff-verifier: compare resulting .layer file vs golden expected
      7. PASS → next op; FAIL → bug-fixer with options
      8. max 15 iterations per op (hard cap)

    MIDDLE LOOP (per-op-regression, ~min):
    After each op PASSES inner loop:
      1. Run 10-revision regression for that op (golden + 4 paraphrases)
      2. All green → commit + move to next op
      3. <100% green → bug-fixer + back to inner

    OUTER LOOP (full-suite, ~hr):
    After all 5 ops PASS middle loop:
      1. Run 100 fuzzed revisions (property-based, random valid)
      2. Run 50-revision stability soak
      3. Measure latency P50/P95
      4. readiness-reporter: pass/fail against sc-B1 to sc-B12

    Sub-agents:
    - s5-tester: generates test cases (golden + fuzz + paraphrase)
    - latency-monitor: TTFT + end-to-end measurement per revision
    - diff-verifier: JSON-Patch(pre, post) compare
    - ui-classifier: screenshot post-revision, VLM classify
    - enforce-researcher: when Bohemia API call unclear
    - bug-fixer: on inner-loop FAIL, always 2-3 labeled fix options
    - auditor: pre-each-commit
  </action>

  <done_when>
    - All 5 op types implemented + golden tests green
    - sc-B1, sc-B3 met
    - logs/plugin-impl-progress.md complete
  </done_when>

  <on_failure>
    - Single op type can't be implemented after 15 inner iterations → researcher consult, then if still stuck → escalate
    - Bohemia API method missing → enforce-researcher BI wiki + ESE repo, then escalate to Mac if no path
    - Stuck-detector (4× same error-class) → researcher → 2 more turns → blocker
  </on_failure>

</stage>

---

## STAGE B.2 — File-Watch Hot-Reload Setup

<stage id="B.2" name="hot_reload">

  <action>
    Setup external file-watcher → sendkey hack for sub-2s latency:

    1. Test scripts/file-watcher.ps1 (from MEGA-A scaffold) end-to-end:
       - Touch ai-spec.json
       - Verify SendKeys reaches Workbench window
       - Verify plugin Run() executes
       - Measure end-to-end latency

    2. If SendKeys unreliable → fallback to PyDirectInput / nircmd:
       ```powershell
       # Fallback: nircmd
       winget install --id NirSoft.nircmd -e
       # In watcher action: & nircmd sendkeypress ctrl+shift+r
       ```

    3. Add latency-monitor wrap:
       - timestamp at file-write (Python writes spec.json)
       - timestamp at plugin-log OK line
       - delta = end-to-end latency
       - log to logs/latency.csv

    4. Measure baseline:
       - 20 sequential revisions
       - Compute P50, P95
       - If P50 > 5s OR P95 > 10s → bug-fixer (sendkey window-focus might be lost)

    5. Backup path: if sendkey absolutely doesn't work →
       use Workbench Plugins menu auto-trigger (research enforce-script's RunCommandline()
       option which DOES exist per Bohemia samples)
  </action>

  <done_when>
    - File-watcher → sendkey verified working
    - Latency measured + within thresholds (sc-B9, sc-B10)
    - logs/latency.csv exists with baseline
  </done_when>

  <on_failure>
    - SendKeys completely blocked → use RunCommandline + polling-via-Workbench
    - Latency >10s → architectural issue, escalate to Mac for redesign
  </on_failure>

</stage>

---

## STAGE B.3 — End-to-End Iteration to Saturation (Outer Loop)

<stage id="B.3" name="end_to_end_iteration">

  <action>
    Full outer-loop runs until saturation:

    Iteration N:
      1. Generate 100 fuzzed revisions (property-based, mix of all 5 op types)
      2. Run all 100 through plugin
      3. Aggregate: pass rate, latency dist, crash count
      4. Score against sc-B4, sc-B5, sc-B6, sc-B7, sc-B9, sc-B10
      5. If ≥95% pass + no latency regression + no new failure modes → mark "outer-N green"
      6. If <95% pass → bug-fixer analyzes top failure cluster → fix → next iteration
      7. After 3 consecutive "outer-N green" runs → SATURATED

    Stop conditions (any true → halt):
      - 3× consecutive outer-N green (saturation)
      - hard cap: max 15 outer iterations
      - diminishing returns: rolling-3-turn errors_fixed_per_turn < 1 → researcher escalation
      - stuck-detector: 4× same error-class → researcher → escalate

    Parallel:
      - Stability soak runs continuously (background process): 50 sequential revisions
      - latency-monitor logs everything to logs/latency.csv
      - ui-classifier periodically screenshots Workbench, verifies no crash dialog
  </action>

  <done_when>
    - 3× outer-green achieved (saturation) OR explicit user-decision to ship at current state
    - sc-B4 to sc-B7, sc-B9, sc-B10 all met
    - logs/outer-loop-results.json complete
  </done_when>

  <on_failure>
    - Hard cap exceeded without saturation → blocker, escalate to Mac+user
    - Stuck on edge-case → researcher + Mac escalate
  </on_failure>

</stage>

---

## STAGE B.4 — Paraphrase + UX Naturalness Test

<stage id="B.4" name="paraphrase_test">

  <action>
    Test UX naturalness (sc-B8):
      1. For each of 10 intents (e.g. "make fog denser", "shorten phase 3", "add 2 spawn points east"):
         - Generate 5 NL paraphrases via LLM (different phrasings, same intent)
         - Run each through pipeline
         - Verify all 5 produce same JSON-Patch diff
      2. Aggregate paraphrase-robustness rate
      3. Target: ≥80% paraphrase consistency

    If <80%: bug-fixer suggests narrative-designer prompt refinement → re-test.
  </action>

  <done_when>
    - sc-B8 met (paraphrase robustness ≥80%)
    - logs/paraphrase-test-results.json complete
  </done_when>

</stage>

---

## STAGE B.5 — Stage 3 User Gate Preparation

<stage id="B.5" name="s3_prep">

  <action>
    Prepare for the irreducible user-touchpoint (Stage 3):

    1. Generate 5 NL prompts for user UX session:
       - 3 attribute-edit revisions (creative tone words: "scarier", "calmer", "earlier")
       - 1 entity-add ("Add a tank to the east hill")
       - 1 batch ("Make it a foggy dawn raid with 2 extra defenders")

    2. Generate user instructions:
       ```
       Wenn du am PC bist, mach diese 5-Min Flow-Session:
       1. Open Workbench mit ai_night-recon-everon
       2. Ensure file-watcher.ps1 running (Background)
       3. Open Claude Code chat, type each prompt 1-by-1
       4. Verify Workbench viewport updates within ~5s per prompt
       5. Rate UX:
          - Speed-feel: 1-5 (Cursor-Composer-vibe?)
          - Accuracy: prompts matched intent?
          - Bugs encountered: list
       ```

    3. Pre-stage all 5 prompts as ready-to-paste in logs/s3-ux-prompts.md
  </action>

  <done_when>
    - 5 NL prompts curated + saved
    - User instructions documented
    - sc-B13 met
  </done_when>

</stage>

---

## STAGE B.FINAL — Final Paper + Hand-off to User

<stage id="B.FINAL" name="final_paper">

  <action>
    1. Generate playbook/handoffs/final-paper-MEGA-B-<TS>.md:
       - Goal Achievement Matrix (sc-B1 to sc-B14)
       - Stage outcomes
       - Plugin implementation details (which ops, what API calls)
       - Latency measurements (P50, P95, distribution chart ASCII)
       - Reliability metrics (pass rate, fuzz coverage, stability soak)
       - Paraphrase robustness rate
       - Known limitations + edge cases
       - Pre-staged S3 user-prompts (link to logs/s3-ux-prompts.md)
       - Cost breakdown (Sonnet + Opus escalations)
       - Total runtime
       - Next action: "User at PC, run Sprint S3 wrapper for UX session + final approval"

    2. Write logs/reflection-MEGA-B-pc.md
    3. log_episode comprehensive entries
    4. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_B_complete=true,
       ready_for_user_s3=true
    5. Final commit + push
    6. Chat output: "Sprint MEGA-B complete. S5 live editor MVP at <readiness>%.
       When at PC: paste sprint-S3-user-fallback wrapper for UX session + final approval."
  </action>

  <done_when>
    - Final paper exists
    - sc-B14 met
    - All commits pushed
    - User informed
  </done_when>

</stage>

---

<escalation_triggers>
  - B.1 stuck on op-type after 15 inner iterations → researcher → escalate
  - B.2 SendKeys/RunCommandline completely fails → architectural redesign Mac-side
  - B.3 hard-cap 15 outer iterations without saturation → escalate
  - B.3 stuck-detector 4× same error-class → researcher → 2 more turns → escalate
  - Token budget > 800k → escalate
  - Total runtime > 12h → escalate
  - Workbench crashes repeatedly during stability soak → escalate
</escalation_triggers>

<sub_agents_enabled>
  <agent role="logger" always_on="true" full_session="true"/>
  <agent role="dep-installer" stages="B.0,B.2" model="haiku"/>
  <agent role="process-tracker" stages="B.1,B.3" model="haiku"/>
  <agent role="ui-classifier" stages="B.1,B.3,B.5" model="sonnet" multimodal="true"/>
  <agent role="s5-tester" stages="B.1,B.3,B.4" model="sonnet"/>
  <agent role="latency-monitor" stages="B.1,B.2,B.3" model="haiku"/>
  <agent role="diff-verifier" stages="B.1,B.3" model="sonnet"/>
  <agent role="enforce-researcher" stages="B.1,B.2" model="sonnet"/>
  <agent role="auditor" pre_push="true" per_stage="true" model="sonnet"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <agent role="loop-detector" on_retry="true"/>
  <agent role="optimizer" post_success="true" model="sonnet"/>
</sub_agents_enabled>

<token_budgets>
  <stage_max>200000</stage_max>
  <combined_max>1000000</combined_max>
  <escalate_at>800000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → researcher → 2 more turns → STOP
  - inner_loop_max = 15 per op-type
  - middle_loop_max = 10 attempts per regression run
  - outer_loop_max = 15 iterations to saturation
  - step_time_budget_default = 45 min
  - sprint_time_budget = 12h total (6-10h target + 2h buffer)
  - DRY marker required for destructive ops
  - NEVER automate against BattlEye-protected sessions
  - Sub-agent depth ≤ 3 (L1 orchestrator → L2 siblings → L3 utility)
  - Sub-agent siblings dispatched as parallel DAG (AgentOrchestra pattern)
</hard_guards>

</sprint>

---

## Wrapper Prompt — paste in PC chat AFTER MEGA-A done + Mac audit done

```
Du bist PC-Executor. CS aus. User abwesend für 6-10h.
Sprint MEGA-B — S3-S5 Live Editor Build. End-goal: live in-editor LLM revision MVP.
Sonnet 4.6 default. ~6-10h autonomous.

PRE-CHECK: MEGA-A muss done sein + Mac-Side Audit done.
Verify before starting: playbook/handoffs/final-paper-MEGA-A-*.md exists,
playbook/handoffs/sprint-MEGA-B-S3-S5-live-editor.md refined post-audit
(check for "audit-refined: <TS>" header).

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/handoffs/final-paper-MEGA-A-*.md (your prior work + audit findings)
3. playbook/RELAY_PROTOCOL.md
4. PC_AGENT_BRIEF.md
5. playbook/CHEATSHEET-PC.md
6. research/11-s5-readiness-roadmap.md ← S5 criteria + plugin reality
7. playbook/handoffs/sprint-MEGA-B-S3-S5-live-editor.md ← THIS plan (refined post-audit)

Critical knowledge:
- Plugins have NO native OnUpdate — external chokidar/PowerShell-watcher + sendkey hack
- Latency floor: 1-2s sendkey / 5-10s manual
- Bohemia samples in $env:USERPROFILE\Documents\GitHub\Arma-Reforger-Samples/
- SampleWorldEditorPlugin.c is primary reference
- 5 op types MVP: attribute-edit, entity-create, entity-delete, entity-move, batch
- Reload: Ctrl+Shift+R or Shift+F7 (no Workbench restart needed)

Execute Stages B.0 → B.1 → B.2 → B.3 → B.4 → B.5 → B.FINAL.

Two-Phase Reception:
- Phase A: ⚙️ DO = User confirms CS aus + 6-10h abwesend + MEGA-A+Audit done
- Phase B: Verify MEGA-A artifacts present (B.0 sub-check)
- Phase C: B.1 (plugin impl, 3-4h) → B.2 (file-watch, 30min) → B.3 (saturation, 2-4h)
          → B.4 (paraphrase, 30min) → B.5 (S3 prep, 15min) → B.FINAL (paper, 10min)
- Phase D: B.FINAL = consolidated paper, push, chat-output

3-layer iteration loop strict (Inner sec / Middle min / Outer hr).
Sub-agent depth ≤3 levels.
Stuck-detector + saturation criteria per research/11.

Escalation to Mac if:
- MEGA-A artifacts missing
- B.1 op-type stuck >15 inner iterations
- B.2 sendkey + fallbacks all fail
- B.3 no saturation after 15 outer iterations
- B.3 stuck-detector 4× same error → researcher → 2 more turns → escalate
- Token >800k OR runtime >12h

Sub-Agent-Fleet: logger always-on, dep-installer + process-tracker (haiku),
ui-classifier + s5-tester + diff-verifier + enforce-researcher + bug-fixer + auditor
(sonnet), latency-monitor (haiku), loop-detector + optimizer.

DRY marker for destructive ops. NEVER BE-protected sessions.

Final Paper: playbook/handoffs/final-paper-MEGA-B-<TS>.md
Intermediate commits per stage.

When done: chat output "Sprint MEGA-B complete. S5 MVP at X% readiness. User: paste
sprint-S3-user-fallback wrapper for UX session + final approval at PC."

Start with Stage B.0 (Pre-Flight + Artifact-Verify).
```
