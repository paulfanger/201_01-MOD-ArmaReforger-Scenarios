# Postmortem: The 75%-S5 Sprint
## Five Load-Bearing Assumptions That Each Cost Six Iterations

**Date:** 2026-05-29
**Sprint:** FINAL S5 MAXED — Arma Reforger AI-Native Mission Authoring, Phase 1 Workbench bridge
**Outcome:** 75% MVP. Plugin runs, reads spec.json, writes outbox.json. WorldEditor viewport mutation remains unverified by automation. Estimated 30-minute user-present session to close.
**Style:** Google-SRE blameless. Root cause is structural, not human.

---

## TL;DR

Five separate failures during the sprint all reduce to the same shape: **a load-bearing assumption that two surfaces were equivalent, when in fact one was advisory and the other was ground-truth.** The sprint paid for each assumption in 5–8 debug iterations.

| # | The pair we treated as equivalent | Actual relationship |
|---|---|---|
| 1 | Headless `-validate` vs. live Workbench compiler | Subset (validate runs only the syntax-and-link pass; live runs that PLUS module-activation post-processing) |
| 2 | Sub-agent persona vs. spawned isolated context | Persona is journaling; agent is `Task()` with separate context window |
| 3 | User-turn authorization vs. classifier authority | Three competing authority sources with no precedence rule that survives turns |
| 4 | "Plugin launched" vs. "target module active" | Two distinct states; `Workbench.GetModule(WorldEditor)` returns null in the first |
| 5 | File-watcher event vs. action-commit channel | "Something changed" signal vs. "execute" trigger; SendKeys is the worst possible bridge |

The general lesson: **in every multi-surface system, designate ONE surface as ground-truth and treat the other as advisory.** Then automate the gate that lives on the ground-truth surface.

---

## Failure 1 — Validate-Green ≠ Live-Green

**Observation:** Eight consecutive runs of `ArmaReforgerWorkbenchSteam.exe -validate=PC -wbSilent -exitAfterInit` returned exit code 0 ("compile-check PASS"). The same code, opened in the live Workbench Script Editor, displayed 8+ errors. Six Computer Use turns were spent chasing a discrepancy that was structural, not behavioral.

### 5 Whys

1. **Why did `-validate` pass and live compile fail?** They run different compile pipelines.
2. **Why are they different?** The 1.1 Modding Update introduced a post-processing pass that *seals* all Game-module classes and re-resolves mod-class `extends` chains after module activation. `-validate` runs the syntax-and-link pass before that seal.
3. **Why was the post-processing pass added?** Sealed-class inlining and ref-keyword strictness require knowing the full module graph at seal time. (Source: `reforger.armaplatform.com/news/modding-update-scripting-1-1`.)
4. **Why didn't we know `-validate` skipped this pass?** Bohemia's wiki documents `-validate` as "checks if the game scripts are compilable" — a one-sentence semantic claim that omits which passes run. (Source: `community.bistudio.com/wiki/Arma_Reforger:Startup_Parameters`.)
5. **Why did we treat the documented one-sentence claim as equivalence?** Sprint plan named `-validate` as "CI gate." A CI gate is, by reflex, ground-truth. We made the headless surface ground-truth because it was scriptable, when in fact the live editor was ground-truth and the headless was advisory.

**Root cause:** There is no single "compiler binary" in Reforger — there is a compile pipeline whose stages are gated by which modules are loaded. The Steam community thread `4348859098833074738` corroborates state-dependent compile failures (errors appearing only after addon-folder restoration patterns), which is the same bug surfacing in user-land.

**Industry context:** This is not Reforger-specific. The 2026 ITSecurityGuru survey reports 51% of developers find vulnerabilities post-deploy and only 9% believe testing keeps pace with dev velocity. Unreal's documented answer is **editor-only validation modules that run the same ruleset locally AND in CI** — the validate-vs-live separation is meant to be eliminated, not papered over. (Source: `spongehammer.com/unreal-engine-editor-only-module-data-validation/`, `dev.epicgames.com/documentation/en-us/unreal-engine/data-validation-in-unreal-engine`.)

---

## Failure 2 — The Sub-Agent Fleet Was Journaling, Not Delegation

**Observation:** The sprint plan named nine specialist agents (`mission-director`, `narrative-designer`, `asset-curator`, `version-keeper`, `pipeline-tester`, `mission-validator`, `workbench-integration-tester`, `bug-fixer`, `readiness-reporter`). Audit reveals: three real `Task()` spawns (one Explore for SteamDB, two general-purpose for Enforce syntax fixes), one Computer Use loop. The remaining "agents" were one main agent with a journaling convention.

### 5 Whys

1. **Why did the fleet look real on paper but not in execution?** Most "agents" never used `Task()` or any documented isolated-context spawn primitive.
2. **Why use the journaling convention instead of real spawns?** It produced real useful artifacts (logs, audit notes, bug reports) at lower cost than 9 separate contexts.
3. **Why was that the right economic choice?** The work was *sequential* (debug one compile-error chain → fix → re-run). The arxiv 2026-05 paper *"Towards a Science of Scaling Agent Systems"* (`arxiv.org/abs/2512.08296`) measures **−70.0% degradation on sequential planning** when forced into multi-agent vs. single-agent — and **+80.8% improvement on decomposable financial reasoning**. Multi-agent helps when work is parallelizable; hurts otherwise.
4. **Why did the plan call for 9 agents anyway?** Aspirational architecture inherited from "fleet" frame popular in 2025. The frame assumes named contexts produce specialization. The arxiv 2026 paper *"Rethinking the Value of Multi-Agent Workflow: A Strong Single Agent Baseline"* (`arxiv.org/abs/2601.12307`) shows OneFlow (single agent + multi-turn) matches **homogeneous** multi-agent workflows because they all share the same base LLM — only differing in system prompts.
5. **Why did the framing persist after empirical disconfirmation?** "Fleet" is a more legible artifact for a Creative Director audience than "one agent with branch/return folding." It made the system narratively explicable. The cost was a mismatch between the architecture diagram and the execution graph.

**Root cause:** If all "agents" share one base model, one context, and one conversation, **they are personas, not agents.** Test of realness: does the spawn use `Task()` / `TaskCreate` / `Delegate()` with documented context isolation? If not, it's a journaling convention.

**The 2026 architectural answer is not "more real agents."** Cognition's context-folding paper (`context-folding.github.io`, Oct 2025) and productionized SWE-1.5 (`cognition.ai/blog/swe-1-5`, Nov 2025) show one orchestrator with explicit `BRANCH(subtask)` / `RETURN(summary)` markers hits **58.0% SWE-bench Verified at 32K tokens vs. baselines needing 327K**. The fix is not more named contexts; it is making branch/return folding explicit *inside* one orchestrator.

Anthropic's own multi-agent research system measured a **15x token premium**, justified by +90.2% on parallelizable research evals — but documented up to **−70% degradation on sequential coding tasks** (PlanCraft benchmark). (Source: `theaiengineer.substack.com/p/how-anthropic-built-multi-agent-deep`.)

---

## Failure 3 — Classifier Blocked Authorized Installs Mid-Sprint

**Observation:** Even with explicit user "step away for 5–7h" authorization in the conversation turn, Auto Mode classifier blocked routine `winget` and `pip` installs as global install guards. User had to run them in external PowerShell, defeating the autonomous-overnight property the sprint was designed to demonstrate.

### 5 Whys

1. **Why did the classifier block authorized installs?** Auto Mode classifies each tool call in isolation; conversation-turn authorizations do not persist across tool boundaries.
2. **Why don't they persist?** Three competing authority sources — user-turn, settings-file, classifier-policy — with no documented precedence rule that survives turns. GitHub issue `anthropics/claude-code#58222` is the canonical bug: "Auto-mode classifier blocks authorized operator workflows," with documented blow-up from ~15-minute task to ~3-hour debug.
3. **Why was the policy designed this way?** Anthropic's auto-mode design doc (`anthropic.com/engineering/claude-code-auto-mode`) explicitly states Tier 1 install commands are allowlisted **only for "packages already declared in the repo's manifest."** Ad-hoc `winget install <X>` / `pip install <Y>` are deliberately NOT in the manifest and are deliberately blocked.
4. **Why didn't we declare deps in a manifest pre-sprint?** The sprint plan treated dep-install as a runtime concern of the agent, not a build-time concern of the repo. (This is also the reflex of someone whose mental model is "Mac homebrew once, then forget.")
5. **Why is this the right design from Anthropic's side?** Classifier FPR 0.4% / FNR 17%. That FNR is too high for unsupervised high-stakes work. The block is correct policy. The bug is in our sprint plan, not in Auto Mode.

**Root cause:** Three competing authority sources without a precedence rule that survives turns. **The SOTA solution is OS-level isolation, not classifier-level reasoning.**

- Devin uses `Exec(prefix)` matching with `--sandbox` at OS level, so installs auto-approve INSIDE the sandbox (`cli.devin.ai/docs/reference/permissions`).
- Cursor ships "sane defaults" (npm test, pnpm install, tsc whitelisted; sudo/rm-rf blocked) and explicitly states "allowlist is best-effort — bypasses are possible" (`cursor.com/docs/agent/security`).
- OpenHands runs the entire agent inside a Docker container with `runtime_extra_deps` for pre-baked dependencies (`docs.openhands.dev/openhands/usage/advanced/custom-sandbox-guide`).

Cursor 3's Automations (March 5, 2026) and Claude Code Routines (April 2026 research preview) push this further: **event-triggered cloud routines, each spinning up its own sandbox with configured MCPs.** This is the architectural answer to "overnight autonomy on the user's laptop."

---

## Failure 4 — Plugin Launched ≠ Target Module Active

**Observation:** `Workbench.GetModule(WorldEditor)` repeatedly returned null. The plugin had loaded into the Workbench process; the WorldEditor module was not the active module. This is the documented behavior, not a bug.

### 5 Whys

1. **Why did `GetModule(WorldEditor)` return null?** WorldEditor was not the active Workbench module when the call ran.
2. **Why wasn't it active?** Plugin was launched without `-wbmodule=WorldEditor`. The plugin loads into whichever module is active at launch.
3. **Why didn't the sample show this?** The Bohemia sample `SampleWorldEditorTool.c` does not defensive-null-check because it relies on the `WorkbenchToolAttribute(wbModules=...)` activation system. The metadata declares the binding; the launcher selects the module. (Source: `github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/main/SampleMod_WorkbenchPlugin/Scripts/WorkbenchGame/SamplePlugins/SampleWorldEditorTool.c`.)
4. **Why is this universal?** Every production plugin system has the same gap. Unreal: `GEditor->GetWorld()` returns null without active editor world. Blender: `bpy.ops` operators raise RuntimeError when called in wrong context. Unity: `EditorApplication.isPlaying` state-change is deferred until end-of-frame.
5. **Why didn't our plan account for it?** We treated "plugin runs" as a single state. It is two states: (a) plugin loaded into process; (b) target subsystem active.

**Root cause:** Plugin systems separate "plugin loaded into process" from "target subsystem active." Mitigation is **declarative module binding in plugin metadata + CLI-driven module activation**, never relying on runtime introspection.

Documented invocation: `ArmaReforgerWorkbenchSteam.exe -wbmodule=WorldEditor -plugin=YourPlugin -autoclose=1`. The `-wbmodule=` flag sets the active module **before** plugin load, so `GetModule(WorldEditor)` is guaranteed non-null when the plugin's `RunCommandline()` runs.

---

## Failure 5 — File-Watcher → SendKeys Was the Wrong Channel

**Observation:** The chain (chokidar → AHK SendKeys → Workbench focus → Ctrl+Shift+R hotkey) had five failure surfaces. The AHK `A_UserProfile` variable error surfaced first (v1-vs-v2 syntax issue; v2 dropped many `A_` variables). Even after fixing, Ctrl+Shift+R was never demonstrably received by the Workbench window.

### 5 Whys

1. **Why did SendKeys not reach Workbench?** `PostMessage WM_KEYDOWN` fails when the target uses low-level hooks, RawInput, or checks foreground-window state. Workbench (Enfusion engine) does all three.
2. **Why use SendKeys at all?** We needed a way for an external file event to trigger an in-process action in Workbench.
3. **Why is that hard?** Reforger has no HTTP API in Enforce Script; there is no in-process listener exposing a trigger surface. The documented automation pattern is **CLI re-invocation** (`-plugin=…-autoclose=1`), not in-process re-trigger.
4. **Why didn't we use CLI re-invocation?** The plan assumed Workbench would stay open for iteration, and keystrokes would re-trigger the running plugin. This is the GUI-centric mental model; the CLI pattern is the documented one.
5. **Why does the documented pattern exist?** Because the Microsoft Win32 stack is full of half-implemented automation surfaces. `ReadDirectoryChangesW` silently drops events on buffer overflow (returns true with `lpBytesReturned=0`; buffer ceiling 64KB over network, ~16380 DWORDs locally). Chokidar's `atomic` and `awaitWriteFinish` options exist precisely because editor-temp-file-rename patterns generate spurious events. The Win32 SOTA for "external event triggers in-process action" is **WM_COPYDATA (synchronous, requires receiver window-class) or named pipes (`\\.\pipe\name`, faster than TCP locally, full duplex, no focus required)**. Keystrokes are the worst possible channel.

**Root cause:** File-watcher events are "something changed" signals, not "commit to action" signals. The fix is two channels: (a) debounce ("`awaitWriteFinish` with stabilityThreshold 500ms" or `watchexec --debounce 50ms`) AND (b) a deterministic action channel (named pipe or CLI re-spawn) — never keystrokes.

---

## What We Tried | Why It Failed | What To Do Instead

| What we tried | Why it failed | What to do instead |
|---|---|---|
| `-validate -wbSilent` as the CI gate | Validate runs syntax/link pass only; live editor runs PLUS module-activation post-processing | Keep `-validate` as fast-fail filter (rename "CI smoke"). Add live-compile gate via `-wbmodule=WorldEditor -plugin=… -autoclose=1` that writes `compile-errors.json`. Mission READY only when both pass. |
| Nine named sub-agents in plan | Sequential work — multi-agent measured −70% on PlanCraft sequential coding | One orchestrator with explicit `BRANCH(subtask)` / `RETURN(summary)` markers. Reserve real `Task()` spawns for parallelizable work (e.g., scan 5 OSS repos for asset patterns: +81–90%). |
| Mid-sprint `winget install` / `pip install` | Auto Mode classifier deliberately blocks installs not in manifest | Pre-declare every dep in `pc-requirements.toml` / `pyproject.toml`. Sprint never installs at runtime; sprint *uses* what manifest declared. Bonus: classifier never sees an install call. |
| Runtime `Workbench.GetModule(WorldEditor)` lookup | Returns null unless WorldEditor is active module | Declarative `[WorkbenchToolAttribute(wbModules: { 'WorldEditor' })]` + CLI `-wbmodule=WorldEditor -plugin=… -autoclose=1`. Activation is launcher's job, not plugin's. |
| chokidar → AHK SendKeys → Workbench hotkey | Five failure surfaces; `A_UserProfile` v1/v2 bug; `PostMessage` blocked by RawInput | chokidar with `awaitWriteFinish: { stabilityThreshold: 500, pollInterval: 100 }` → `spawn(ArmaReforgerWorkbenchSteam.exe, ['-wbmodule=WorldEditor', '-plugin=AISpecApply', '-autoclose=1', '--', 'input='+spec])`. No keystrokes. No focus dependency. |
| Computer Use loop reporting FAIL 6× without fixing | No graded reward between actions — loop saw failure, had no signal to course-correct mid-trajectory | Add PRM-style mid-trajectory score 0–100 vs. spec.json target. Score drops 2 turns in a row → BREAK and pause-and-ask. PRMs deliver +10.6 pp on SWE-bench Verified (40.0 → 50.6%). (Source: `arxiv.org/pdf/2509.02360`.) |
| Doc-first CLI assumptions (Steam AppID 1874881, `%LOCALAPPDATA%`, validate=live-compile) | Every unverified Mac-side claim was wrong on PC | Standing `research/EMPIRICAL.md` index. Pre-sprint audit reads it; sprint refuses to plan around any unverified-on-PC claim. Tag confirmed/disconfirmed claims with date and discovery source. |

---

## Patterns To Adopt

**1. Compile-twice gate.** Never trust `-validate` alone. Run it as 60–90s pre-commit, then a live-Workbench gate via documented `-wbmodule=WorldEditor -plugin=… -autoclose=1` pattern that writes `compile-errors.json`. Both must pass before READY.

**2. Manifest-declared deps.** Stop trying to bypass the classifier. Run the autonomous sprint inside a context where every install is pre-declared. `pc-bootstrap.ps1` runs in user-foreground BEFORE Phase A; Phase C never installs, only uses.

**3. Realness test for sub-agents.** If the spawn doesn't use `Task()` / `TaskCreate` / `Delegate()` AND doesn't return a separate transcript, it's a journaling convention. Don't call it a fleet. Use OneFlow-style single-agent + multi-turn for homogeneous work (cheaper, same quality). Reserve real spawns for heterogeneous (different models) or large-output context-isolation.

**4. Declarative module activation.** Every Workbench plugin invocation uses `[WorkbenchToolAttribute(wbModules: { '<Module>' })]` + CLI `-wbmodule=<Module>` flag. Runtime `GetModule()` lookup is for verification, never activation.

**5. Two-layer event channel.** chokidar with `awaitWriteFinish` for debounce; CLI re-spawn (or named pipe `\\.\pipe\reforger-spec`) for action. Never SendKeys.

**6. PRM-style mid-trajectory scoring in Computer Use loops.** After each action, score 0–100 vs. target. Two consecutive drops → BREAK and pause-and-ask. This is the documented +10.6 pp lift on SWE-bench.

**7. Audit-as-design-input.** Every divergence between documented capability and observed reality goes into `research/EMPIRICAL.md` with an `[EMPIRICAL-DISCONFIRM YYYY-MM-DD]` tag. Pre-sprint audit reads this index.

**8. Build a Workbench-MCP plugin (~200 LOC Enforce Script) for Phase 2.** Mirror `github.com/ChiR24/Unreal_mcp` architecture. Expose 5–10 tools: `get_viewport_state`, `set_fog_density`, `list_entities`, `place_entity`, `validate_world`. Claude Code reads results via MCP rather than screenshot-grep. This is the documented direction for game-engine GUI verification in 2026 — `flopperam/unreal-engine-mcp`, `kvick-games/UnrealMCP` both ship production code for this exact pattern.

**9. Move overnight autonomy to event-triggered cloud routines.** Phase 3+: a GitHub event triggers a cloud sandbox routine that runs Phase C autonomously, writes results to `STATE.json`, posts one notification when Phase D begins. Auto-halts after 3 consecutive denials or 20 total per session (Auto Mode default). (Source: `cursor.com/blog/cursor-3` Automations; `chatforest.com` Routines.)

**10. Calibrated pause-and-ask.** Each sprint phase emits a confidence-score 0–100 to `STATE.json`. Below 70 the agent writes a pause-card to `scenarios/CURRENT_TURN_FOR_USER.md` and stops. Devin 2.1 added this exact pattern (confidence ratings in Linear/Jira integrations) as the pause-trigger signal. HITL checkpoints reduce critical errors from 1-in-35 to fewer than 1-in-500. (Source: `onereach.ai/blog/human-in-the-loop-agentic-ai-systems/`.)

---

## What Actually Worked (Preserve These)

- **Two-Phase Reception** (Phase A manual prereqs → Phase C autonomous → Phase D single return). This is the right macro-shape; what failed was the granular decisions inside Phase C, not the protocol.
- **`-validate` as a smoke filter** — 8 consecutive PASS caught real syntax bugs. The error was calling it a CI gate, not running it.
- **Computer Use loop for actual GUI navigation.** The ONLY truly autonomous automation in the sprint. Keep it; add PRM scoring.
- **Empirical-first debugging.** PC discovered vanilla-junctions in 3 strategies; this kind of in-situ discovery is exactly what the Mac-side planning could never produce.
- **`STATE.json` + `reflection-turn-N-*.md` cross-session memory.** The narrative continuity layer worked. Voice-companion workflow extends this pattern (paper preloaded into Claude Project plays the same role as STATE.json plays in-session).
- **Pre-Sprint Audit.** Caught disk space, missing tools, pre-empted UAC popups. Bake harder: read `research/EMPIRICAL.md`, refuse to plan around unverified claims.

---

## Closing

The five failures were not five separate bugs. They were five instances of the same pattern: **treating an advisory surface as ground-truth.** Headless validate is advisory; live editor is ground-truth. Persona is advisory; spawned context is ground-truth. User-turn authorization is advisory; classifier policy is ground-truth. Plugin loaded is advisory; module active is ground-truth. File-watcher event is advisory; CLI re-invocation is ground-truth.

The fix in every case is the same shape: **identify the ground-truth surface, automate the gate that lives on it, treat the advisory surface as a fast-fail filter.**

That is the design discipline going into Phase 2.
