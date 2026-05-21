# Mac-Side Audit Pattern — Opus 4.7 between Sprint MEGA-A and MEGA-B

> Stand: 2026-05-21 · Model: Opus 4.7 (deep reasoning needed for plan refinement)
> User-state: User triggers this AFTER Sprint MEGA-A finishes (tipping "audit go" in Mac chat)
> Source: research/11-s5-readiness-roadmap.md
> **Purpose:** Opus reads MEGA-A outcome → research-loop → audit-loop → designs perfect
> Sprint MEGA-B plan optimized for Sonnet 4.6 execution. Uses Master Project Kickoff
> Blueprint pattern.

---

<audit_session>

<context>
  <goal>
    Between MEGA-A (foundation+game+s5-prep on PC, Sonnet) and MEGA-B (live editor build,
    Sonnet on PC), Mac-side Opus runs a structured audit-research-plan iteration loop.
    Produces a Sonnet-optimized Sprint MEGA-B plan calibrated to MEGA-A actual outcome.
  </goal>

  <input_artifacts>
    - playbook/handoffs/final-paper-MEGA-A-<TS>.md (the PC's combined result)
    - logs/reflection-MEGA-A-pc.md (PC reflection)
    - logs/sample-plugin-study-A.md (PC's notes on Bohemia samples)
    - logs/sprint-b-prerequisites-A.md (PC's S5-prep status)
    - logs/sample-plugin-compile-check.png (PC's evidence)
    - workbench-plugin/AI_GeneratePlugin.c (post-MEGA-A refactored version with TODOs)
    - tasks/STATE.json (current sprint state)
    - All MEGA-A commit history (git log)
  </input_artifacts>

  <output_artifact>
    playbook/handoffs/sprint-MEGA-B-S3-S5-live-editor.md (the Sprint B plan, already
    sketched but refined post-audit with MEGA-A reality calibration)
  </output_artifact>

  <process>Master Kickoff Blueprint applied: Phase 0 (env-manifest) → Phase 1 (iteration loop, max 5 turns) → Phase 2 (visual approval gate) → Phase 3 (plan compile)</process>
</context>

---

## PHASE 0 — Audit Inventory

<phase id="0" name="inventory">

  <action>
    Spawn `env-inventory` sub-agent — reads ALL input artifacts, generates state snapshot:

    ```json
    {
      "MEGA_A_status": "complete | partial-escalated",
      "S1_outcomes": {
        "revisions_api": "ok|missing|partial",
        "prompt_caching": "ok|missing|partial",
        "episodic_memory": "ok|missing|partial",
        "golden_tests": "ok|missing|partial",
        "schema_mapping": "ok|missing|partial"
      },
      "S2_outcomes": {
        "dedi_server_launch": "ok|failed",
        "state_trajectory": ["MainMenu","Loading","SpawnScreen","InGame","InGame_moved","MainMenu"],
        "pydirectinput_movement": "ok|failed"
      },
      "S5_PREP_outcomes": {
        "tools_installed": ["VSCode","Enforce-ext","chokidar","..."],
        "bohemia_samples_cloned": true,
        "sample_plugin_compiles": true|false,
        "ai_generate_plugin_refactor": "complete|partial|blocked",
        "file_watcher_tested": true|false
      },
      "open_questions_from_pc": ["...", "..."],
      "blockers": ["..."]
    }
    ```

    Output: logs/audit-inventory-MEGA-A.json
  </action>

  <done_when>
    - Inventory JSON complete
    - All input artifacts read
    - Blockers categorized
  </done_when>

</phase>

---

## PHASE 1 — Audit Iteration Loop (max 5 turns)

<phase id="1" name="audit_iteration">

  <per_turn_actions>
    Each turn spawns 6 sub-agents in parallel (per Master Kickoff Blueprint Phase 1):

    | Sub-agent | Mission | Model | Output |
    |---|---|---|---|
    | 🔬 project-researcher | Deep-research any blocker / open question from MEGA-A | sonnet→opus if novel | logs/audit/research-turn-N.md |
    | 💡 idea-expander | What WERE missed opportunities in MEGA-A? What COULD have been done better? | sonnet | logs/audit/ideas-turn-N.md |
    | 🔍 auditor | Score actual MEGA-A outcome against original sc-1...sc-18 criteria | sonnet | logs/audit/audit-turn-N.json |
    | 🔧 tooling-inventory | Are there tools we MISSED installing in MEGA-A that Sprint B needs? | haiku | logs/audit/tooling-turn-N.json |
    | 🧠 synthesizer | Compile findings → refined Sprint B plan draft | sonnet | logs/audit/sprint-b-draft-vN.md |
    | ❓ clarification-questioner | If something is unclear from PC's output → ask user (batched, AskUserQuestion) | sonnet | logs/audit/questions-turn-N.md |

    Saturation criteria (loop ends when ALL true):
    - project-researcher: 2 consecutive turns no new findings
    - idea-expander: 0 net-new ideas after auditor scoring
    - auditor verdict: "Sprint B draft covers all S5-readiness dimensions"
    - clarification-questioner: 0 open questions
    - OR user explicit "saturiert"
    - HARD CAP: 5 turns
  </per_turn_actions>

  <per_turn_output_to_user>
    ```
    ═══ AUDIT TURN #N · timestamp ═══

    ## What surfaced this turn
    - <project-research highlight>
    - <new ideas surviving audit>
    - <tooling gaps found>

    ## Refined Sprint B concept (v<N>)
    <one-paragraph evolving synthesis>

    ## Saturation Status
    - Research-saturation: 🟢/🟡/🔴
    - Idea-saturation: 🟢/🟡/🔴
    - Audit-coverage: 🟢/🟡/🔴 (X/8 dimensions: file-watch / plugin-impl / latency / tests / etc)
    - Open Q's: <N>

    ## 🧠 ANSWER — Paul beantwortet (falls Q's)
    [Batched questions per AskUserQuestion schema]

    ⏸ STATUS: iterating / saturated-awaiting-approval / paused
    ```
  </per_turn_output_to_user>

  <done_when>
    - Saturation criteria met
    - logs/audit/sprint-b-draft-vN.md is the final refined Sprint B plan
  </done_when>

</phase>

---

## PHASE 2 — Visual Approval Gate

<phase id="2" name="approval">

  <action>
    Output to user (in chat):
    ```
    ═══ 📋 SPRINT MEGA-B BLUEPRINT — APPROVAL GATE ═══

    ## Project at a glance
    <one-paragraph>

    ## 🎯 Goal: S5 Live Editor MVP

    ## ✅ Success Criteria (calibrated to MEGA-A reality)
    - <criterion 1, calibrated>
    - ...

    ## 🛠️ Approach (steps overview)
    1. <Stage B.1>
    2. <Stage B.2>
    ...

    ## 🔧 Required tooling (verified from MEGA-A inventory)
    | Tool | Status | Notes |
    | ... | ✅ installed in MEGA-A | ... |

    ## ⚠️ Risks + Mitigations
    - <risk 1>: <mitigation>

    ## 💰 Estimated Cost (Sonnet on PC)
    - ~$<N> for ~6-10h autonomous build cycle

    ## ⏸ DECISION REQUIRED
    ☐ Approve → "approve" / "freigegeben" / "go" → Opus compiles final Sprint B
    ☐ Refine → describe what to adjust → back to Phase 1
    ☐ Pause → "pause" → save state, resume later
    ```

    User says "approve" → Phase 3.
  </action>

  <done_when>
    - User explicit approval
  </done_when>

</phase>

---

## PHASE 3 — Compile Final Sprint MEGA-B

<phase id="3" name="compile_sprint_B">

  <action>
    Opus produces final `playbook/handoffs/sprint-MEGA-B-S3-S5-live-editor.md`:

    Format: same XML-tagged structure as sprint-MEGA-A.

    Calibrated to:
    - MEGA-A actual outcomes (not assumed)
    - Any S1/S2/S5-PREP gaps discovered in audit
    - User's answered clarification questions
    - Refined latency targets (5-10s manual vs 1-2s sendkey, per realistic PC test)
    - Concrete Bohemia API method names (no more pseudocode references)
    - 3-layer iteration loop with 5 new sub-agents (s5-tester, latency-monitor, diff-verifier, ui-classifier, enforce-researcher)

    Plus generate the wrapper prompt for PC at the end (paste-ready, same format as MEGA-A wrapper).
  </action>

  <done_when>
    - sprint-MEGA-B-S3-S5-live-editor.md exists (refined version)
    - Wrapper prompt at end is paste-ready
    - All MEGA-A reality reflected
    - All audit findings integrated
  </done_when>

</phase>

---

## PHASE 4 — Mac-Side Push + Hand-back

<phase id="4" name="push_handback">

  <action>
    1. Write logs/reflection-AUDIT-mac.md
    2. Update tasks/STATE.json: phase=AUDIT_COMPLETE, sprint_B_ready=true
    3. git commit + push
    4. Chat output to user:
       "Audit complete. Sprint MEGA-B plan ready at <path>.
        Wrapper prompt at end of file.
        Paste in PC chat when ready for Sprint B (~6-10h autonomous).
        Recommended: do this in second uninterrupted block (after MEGA-A done)."
  </action>

  <done_when>
    - All artifacts pushed
    - User informed
  </done_when>

</phase>

</audit_session>

---

## How to trigger this audit

**Pre-requisite:** Sprint MEGA-A complete (PC pushed final-paper-MEGA-A-*.md).

**User action in Mac chat:** type literally `"audit go"` or `"audit-mega-a"`.

That triggers me (Mac-side Opus 4.7) to:
1. Read all MEGA-A input artifacts
2. Run Phase 0-4 above (autonomous, asks you only at Phase 1 ANSWER batches + Phase 2 approval gate)
3. Output the refined Sprint MEGA-B plan + wrapper prompt
4. Pause for your approval to start Sprint B

Estimated audit duration: 20-40 minutes (depends on iteration depth + your answer-speed).
Estimated audit cost: $3-8 (Opus reasoning is expensive but justified for plan-compile).

---

## Why Opus 4.7 (not Sonnet) for the audit?

Per research/08 + 09:
- Audit needs **novel problem-solving** (gaps from MEGA-A might be unforeseen)
- Plan compilation needs **architectural reasoning** (calibrating to reality)
- 5-turn iteration loop with researcher = deep work
- Output quality determines Sprint B's 6-10h Sonnet execution success
- Opus tokens here (~$3-8) save Sonnet rework later (~$30-50 if plan is wrong)

This is exactly the Opus-where-novel, Sonnet-for-bulk split the project is built on.
