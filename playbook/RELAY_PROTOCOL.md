# Relay Protocol — Paul ↔ Mac-side Claude ↔ PC-side Claude

Paul works on a Mac. The PC (Windows) runs Arma Reforger Workbench. Both have their own
Claude Code session. Their Claude sessions **don't talk to each other directly**.

Paul's Mac-side Claude (this one) generates structured outputs that Paul **relays** to the
PC-side Claude by copy-pasting into the PC's Claude Code chat. The PC's Claude replies
through a return template that Paul pastes back into the Mac chat.

Code & files flow through **Git/GitHub** (`tasks/PC_TASK.md`, `tasks/PC_RESULT.md`).
Decisions, blockers, manual steps flow through **Paul's chat-paste**.

This protocol exists so the relay loops fast and cleanly without each round being a
creative reinterpretation.

---

## When to use the relay

- **Use it** for: any cross-device action where one side waits on the other —
  PC environment setup, addon-copy operations, Workbench launch + result-parsing,
  bug-fix loops on Phase 2 missions, manual decisions (EULA accept, Steam install dialog).
- **Don't use it** for: pure Mac-only work (mission generation, code editing, schema fixes)
  or pure PC-only background polling. When real focused work is happening on one side
  alone, the loop **pauses** — see "Pause flag" below.

---

## Loop turn format

Each output Paul receives from Mac-side Claude has **three zones**:

```
═══════════════════════════════════════════════════════════
  🔄 LOOP TURN #N · YYYY-MM-DD HH:MM · Mac-side
═══════════════════════════════════════════════════════════

[Zone 1: meta context — Paul reads, optional]
[Zone 2: 🟢 FOR PAUL — Paul's actions on his side, optional]
[Zone 3: 📤 FOR PC — copy-paste block, optional]

⏸ PAUSE FLAG: yes / no
[If yes: "STOP LOOP. <reason>. Resume when <condition>."]
```

Each zone is optional. A pure-Paul turn skips Zone 3. A pure-relay turn might be just Zone 3.

---

## The PC-bound copy-paste block

When Paul sees this:

```
╔══════════════════════════════════════════════════════════
║ 📤 PAUL → PC · Loop Turn #N · timestamp
║
║ ...content...
║
║ ───── 📥 RETURN TEMPLATE — PC fills in below ─────
║ ...
╚══════════════════════════════════════════════════════════
```

He selects everything between the `╔══` and `╚══` lines, copies, pastes into the
PC-side Claude Code chat. The PC's Claude processes it, runs the prompts, fills in
the return template, sends back.

---

## Markers inside the PC-bound block

Every directive has one of four markers:

| Marker | Meaning | Who acts |
|---|---|---|
| **🤖 EXEC** | Paste into Claude Code on PC. Claude executes autonomously (Bash / PowerShell / Read / Write). | PC's Claude |
| **🧠 ANSWER** | Question for Paul himself, in his own words (decisions, preferences). | Paul (human) |
| **⚙️ DO** | Manual action on the PC by hand (UI click, EULA accept, Steam install dialog, settings.json edit). | Paul (human, at PC) |
| **🧪 DRY** | Emit the PLAN of an EXEC block + content hash, without running. Other side computes same hash from RESPONSE, then approves real run on next turn. Use for destructive / irreversible operations. (Per research/07 §8) | Both — emitter plans, receiver verifies |

### 🧪 DRY Enforcement Rules (M.4 — added PHASE META)

**Every destructive operation** (Remove-Item -Recurse, git reset --hard, file deletion,
database drop, etc.) MUST follow this procedure:

1. **Before running:** Commit a DRY plan to `playbook/dry-plans/<ts>-<short>.md`:
   - What will be deleted/modified
   - Why (justification)
   - Rollback procedure if needed
   
2. **When running:** Log the op to `logs/destructive-ops.jsonl`:
   ```json
   {"ts": "ISO8601", "op": "Remove-Item", "target": "path/to/thing", "dry_plan_path": "playbook/dry-plans/...", "user_approved": true}
   ```

3. **Auditor pre-push:** Reads `logs/destructive-ops.jsonl`, cross-checks that every entry
   has a matching `dry_plan_path` file committed BEFORE the op ran. If any entry is missing
   a dry plan → **BLOCK push**. Sprint stops and escalates.

4. **Self-approved destructive ops** (reversible ones like re-copying missions from repo)
   are allowed with `user_approved: false` — but still require the plan + log entry.

Test: simulate a `Remove-Item` without a DRY plan, verify auditor blocks in the pre-push check.

---

## Return template (standard)

Every PC-bound block ends with this template. PC's Claude fills the placeholders:

```
═══ PC → PAUL · Loop Turn #N RESPONSE ═══

Status: [done / partial / blocked / in-progress]

🤖 EXEC results:
  1. <prompt label>: <outcome — done / failed / partial / output snippet>
  2. ...

🧠 ANSWERS:
  Q1: <Paul's answer relayed back if PC asked Paul something>
  Q2: <...>

⚙️ DO outcomes:
  1. <task>: <done / not done / blocked-because>

Blockers (if any):
  - <what's stuck, what's needed to unblock>

New questions for Mac-side Claude:
  - <free form>

Notes:
  <free form, optional>

═══ END RESPONSE ═══
```

Paul copies the response, pastes into Mac-side chat. The next Loop Turn fires.

---

## Pause flag — when the loop stops

The loop is for **coordinating across the two devices**, not for **single-side focused work**.

When the next action is real focused work on one side only (≥10 min of waiting or computation
that the other side can't help with — e.g. Steam install download, Workbench compile, training run):

- The output ends with: `⏸ PAUSE FLAG: yes`
- Explanation: "STOP LOOP. <reason>. Resume by pasting PC return template when <condition>."
- Paul does NOT relay further turns until the PC returns.

When the loop should continue immediately (just decisions, no real work):

- The output ends with: `⏸ PAUSE FLAG: no`
- Paul relays, awaits PC response, paste back, next turn fires.

---

## Git vs. Chat — which channel for what?

| Type of payload | Channel | Why |
|---|---|---|
| Code, mission files, task instructions, results | **Git** (`tasks/PC_TASK.md`, `tasks/PC_RESULT.md`) | Versioned, large, structured |
| Loop coordination (turn # / status / pause flag) | **Chat-paste** | Fast, human-readable, in front of Paul |
| Manual decisions (EULA accept, settings choice) | **Chat-paste** (🧠 ANSWER / ⚙️ DO) | Needs Paul's eyes |
| Per-task command list | **Git** (in `PC_TASK.md`) | Long, structured, replayable |

Rule of thumb: if it's >10 lines or contains code → goes via Git into a TASK file.
If it's a 1-2 sentence decision → chat-paste.

---

## How to start a loop

Mac-side Claude opens **Loop Turn #1** spontaneously when:
1. A new Phase begins (Phase 2 Workbench testing, Phase 3 game testing).
2. PC reports a blocker that needs Paul's manual help.
3. Paul says "let's sync with the PC on X."

PC-side Claude gets Loop Turn #1 from Paul, processes, returns response. Paul sends
response to Mac. Loop Turn #2 fires.

---

## How to end a loop

Naturally — when PC return template has no new questions, no blockers, no pending work,
and Phase milestone is achieved. Final output has:

- `⏸ PAUSE FLAG: yes` (or `closed`)
- Summary of what was achieved across the loop
- Next action items each side now owns

---

## Example turn structures

**Loop Turn that needs both sides (most common):**
- Zone 1 (context recap, what just happened)
- Zone 2 (Paul: do these manual steps on PC)
- Zone 3 (PC: pull, EXEC, fill template)
- Pause: no

**Loop Turn that's Paul-only (rare):**
- Zone 1 (state)
- Zone 2 (Paul: confirm / decide / approve)
- No Zone 3
- Pause: depends

**Loop Turn that's pure relay (e.g. forwarding task without commentary):**
- Just Zone 3
- No Zone 1 or 2
- Pause: no

---

## Why this exists

Without a protocol, every relay-message gets reinvented. Paul (the relay) burns mental cycles
figuring out "what does the PC actually need to do here?" — and so does the PC when it opens
the message. A standardized format means: scan in 10 seconds, act, return, done.

`tasks/PC_TASK.md` and `tasks/PC_RESULT.md` handle large-payload async via Git.
This relay protocol handles the human-in-the-loop coordination layer **on top of** that.

---

## Two-Phase Reception (when a side RECEIVES a Loop Turn)

When you (any-side Claude) receive a Loop Turn copy-paste from the user, you MUST process
it in exactly these phases. Never mix "things the user must do" with "things you are doing
right now" — they are sequenced.

### Phase A — Manual-Action Review (~30 seconds)

1. Scan the incoming block for ALL `⚙️ DO` items.
2. List them as a clean numbered checklist at the TOP of your reply:

```
## 📋 Bevor ich loslege — diese Dinge musst DU machen:

1. [BLOCKING] <action> — <why it blocks>
2. [BLOCKING] <action> — <why it blocks>
3. [PARALLEL] <action> — kannst du auch während meiner Execution tun

Fragen dazu? Sonst sag "ready" / "go" / "alles erledigt — check" → ich verifizier + leg los.
```

3. Mark each item as **BLOCKING** (must be done before EXEC starts — installs, account
   creation, EULA, file edits the EXECs depend on) or **PARALLEL** (visual checks the user
   can do during execution).
4. STOP. Do not run any 🤖 EXEC yet. Wait for user signal.

### Phase B — Verification (~10 seconds)

When user signals "ready" / "go" / "alles erledigt":

1. For each BLOCKING ⚙️ DO item, verify if possible:
   - File expected? `Test-Path <path>` — must return True
   - App expected? Check binary path / version
   - Setting changed? Read setting back
   - Permission granted? Try a test command
2. If any verification fails:
   - List what's still missing (concrete + actionable)
   - Ask user to redo or override
   - Stay in Phase B until clear
3. If all verified:
   - One-sentence confirmation: "✅ Alle Blocking-Items verified. Starte Execution jetzt."
   - Move to Phase C immediately, no further user-input needed

### Phase C — Autonomous Execution (the long part)

1. Spawn `logger` (always-on for this turn).
2. Spawn `dep-installer` for pre-flight.
3. Run all 🤖 EXEC blocks in order.
4. Spawn other sub-agents as needed (tester, ui-tester, process-tracker, etc.).
5. Apply all hard guards (anti-loop, screenshot, time budgets).
6. Spawn `auditor` pre-push.
7. Build the return template incrementally — fill placeholders as data arrives.
8. Push to Git (`tasks/<RESULT>.md` + logs/).

If a sub-agent or guard fires a STOP (loop-detector, 3× retry, popup-dedup): jump to Phase D
with status `blocked` + evidence. Do not continue blindly.

### Phase D — Single Return Output

At the very end of your turn, emit EXACTLY one block — the filled return template — formatted
for copy-paste:

```
═══ <SIDE> → <OTHER-SIDE> · Loop Turn #N RESPONSE ═══

Status: [done / partial / blocked / loop_detected / in-progress]

🤖 EXEC results:
  ...

🧠 ANSWERS:
  ...

⚙️ DO outcomes:
  ...

Blockers (if any):
  ...

New questions for <other-side> Claude:
  ...

Notes:
  ...

═══ END RESPONSE ═══
```

Tell user: "Fertig. Kopier den Block oben → in den anderen Device-Chat → nächster Turn fires."

### Why this exists

Without two-phase reception, users get confused: is Claude running? Did I forget a manual
step? Am I supposed to do something now or wait? The cognitive load kills the loop's
benefit. Two-phase reception makes the contract crystal clear: **first you, then me, then
one output back to you.**

---

## Sub-Agent Fleet (both sides)

Each side spawns sub-agents to handle parts of the iteration autonomously. The MAIN agent
(Mac-side Opus or PC-side Claude) is the orchestrator. Sub-agents are short-lived: they
get a clear task + output target, run, and return.

### Sub-agent roles

| Marker | Role | Side | Trigger |
|---|---|---|---|
| 🧪 **tester** | Generate + execute tests against build artifacts (missions, addons, scripts) | Both | New artifact arrives, or before push |
| 🐛 **bug-fixer** | Analyze test failures, propose patches, apply if reversible & in-scope | Both | Tester returns failure |
| 🔬 **researcher** | Deep-research optimization opportunities, new ideas, additional tooling | Mac (cheap to scale) | Stuck in iteration loop, or opt-in scheduled scan |
| 📊 **process-tracker** | Monitor long-running OS processes (installs, builds, downloads), surface completion + anomalies | PC primarily | Long process kicked off (>2 min) |
| 🔍 **auditor** | Coverage + quality gate before any push; catches missed errors, validates result schema | Both | Pre-push hook in every iteration |
| 📝 **logger** | Capture every command + output to `logs/<side>-events-<TS>.jsonl`, push incrementally | Both | Always-on during a turn |
| 🎯 **optimizer** | Read logs after N iterations, propose workflow speed-ups | Mac | After each successful iteration cycle |
| 📸 **ui-tester** | Screenshot GUI state, parse via multimodal vision, classify as ok / error / popup / progress | PC primarily | After any GUI app launch, on any popup detection |
| 🔧 **dep-installer** | Pre-flight check + install missing CLI tools, modules, integrations | Both | Pre-flight before each task; opportunistically when gap detected |
| 🛑 **loop-detector** | Hash error/dialog/output, detect repetition, emit STOP signal | Both | Whenever an action retries |

### Sub-agent invocation pattern

```
SpawnAgent(role=<role>, mission=<one-paragraph mission>, output_file=<absolute path>, max_minutes=<N>)
  → Sub-agent runs autonomously
  → Writes structured output to output_file
  → Returns short summary to orchestrator
  → Orchestrator decides next step based on output
```

The orchestrator NEVER executes sub-agent work itself if a sub-agent can do it. This keeps
context window of the orchestrator clean for high-level decisions.

### Sub-agent output schema (mandatory)

Every sub-agent writes JSON to its output file:

```json
{
  "agent": "tester | bug-fixer | researcher | ...",
  "started_at": "2026-05-20T20:55:00Z",
  "finished_at": "2026-05-20T20:57:32Z",
  "status": "ok | warn | fail | partial",
  "summary": "one-sentence outcome",
  "details": {...role-specific schema...},
  "next_actions": ["machine-readable list"],
  "human_attention_required": false
}
```

If `human_attention_required: true` → orchestrator must surface in the next loop turn's
🧠 ANSWER or ⚙️ DO block.

---

## tasks/STATE.json — single-source-of-truth for the current turn

Per research/07 §5, this is novel cross-device coordination territory. Add a persistent
state file so either side can recover from crashes without re-reading chat:

```json
{
  "turn_id": 4,
  "owner": "pc",
  "phase": "PHASE_A_REVIEW | PHASE_B_VERIFY | PHASE_C_EXEC | PHASE_D_RETURN | IDLE",
  "started_at": "<ISO8601>",
  "pending_do": [
    {"id":"do-1","desc":"...","blocking":true,"verified":false}
  ],
  "pending_exec": [
    {"id":"exec-1","desc":"...","status":"queued|running|done|failed|skipped"}
  ],
  "last_reflection": "logs/reflection-turn-3.md",
  "rollback_snapshot": "logs/snap-turn-4.tar.gz",
  "loop_signals": []
}
```

Updated at every phase transition + every sub-agent return. Pushed alongside RESULT file.
On crash recovery: read STATE.json, resume from `phase`.

---

## Reflection per turn (Reflexion pattern, per research/07 §2)

At the end of every turn (just before Phase D return), the orchestrator MUST write:

`logs/reflection-turn-<N>-<side>.md`

where `<side>` is `mac` or `pc` (or other device id in multi-device setups).

Examples: `reflection-turn-5-mac.md`, `reflection-turn-5-pc.md`.

(Formalized per PC question in Task 006-CS — was inconsistently named in turns 3-4.
Existing files left as-is for history; convention applies from turn 5 onwards.)

With structure:

```markdown
# Turn <N> Reflection

## What went well
- ...

## What failed (and why)
- ...

## What I'd do differently next turn
- ...

## Signals for optimizer
- duration_ms: <X>
- sub-agents spawned: <N>
- guards fired: <list>
- loop signals: <list>
```

At start of next turn (Phase A), orchestrator reads `logs/reflection-turn-<N-1>.md` before
planning. This is the cheapest self-improvement loop with measurable upside (Reflexion paper:
80% → 91% on HumanEval).

---

## Logging & Process Tracking (always on)

Every turn produces `logs/<side>-events-<TS>.jsonl` — append-only line-delimited JSON.
Each event:

```json
{"t":"2026-05-20T20:55:01Z","kind":"exec","agent":"main","cmd":"git pull","exit":0,"duration_ms":342}
{"t":"2026-05-20T20:55:04Z","kind":"spawn","agent":"main","child":"process-tracker","mission":"steam install poll"}
{"t":"2026-05-20T20:55:05Z","kind":"status","agent":"process-tracker","msg":"steam install at 12%"}
```

These get pushed to git alongside `PC_RESULT.md`. Mac-side can run analytics on history
to detect: which sub-agents are slow, which commands flap, which iterations needed re-runs.

### Process-tracker pattern (PC-side, critical)

Long processes (Steam install, Workbench headless run, file copy >100MB) MUST be tracked
by a `process-tracker` sub-agent rather than blocking in the main agent. Pattern:

```
1. Main: kicks off process via Start-Process (non-blocking)
2. Main: spawns process-tracker with target process name / PID / completion signal
3. Process-tracker: polls every 30s, writes status events to logs/, returns when done OR timeout
4. Main: continues only when process-tracker returns
```

Result: main agent's context stays small, user gets real-time status events in logs.

---

## Iteration Loop (both sides)

Inside a single loop turn, each side runs an autonomous mini-loop:

```
ITERATION:
  1. Read task (Mac side: read user msg; PC side: read PC_TASK.md)
  2. Spawn logger (always-on for this turn)
  3. Plan: 1-3 sentences, decide which sub-agents to spawn
  4. Execute main work + spawn sub-agents in parallel
  5. Spawn auditor before any push/commit
  6. If auditor fails: spawn bug-fixer, retry up to 3×
  7. Spawn optimizer (Mac-side only, after success)
  8. Push result + logs
GUARD CONDITIONS (must stop iteration):
  - User question (🧠 ANSWER) needed
  - User manual action (⚙️ DO) needed
  - Cross-side decision needed (other device's input)
  - 3× retry exhausted without resolution
```

When a guard fires, generate a loop turn (chat-paste) addressing the blocker. Do NOT
continue iterating until human or other side responds.

---

## Anti-Loop Guards (HARD — non-negotiable, all sides)

User must NEVER be forced to dismiss the same error popup twice in a row. This is a
**protocol-level guarantee**, not a best-effort.

### Mandatory guards per action

| Guard | Limit | Action on breach |
|---|---|---|
| `max_retries_per_step` | **3** | STOP step, escalate to bug-fixer |
| `same_error_dedup` | **2 identical errors** (hash match on stderr/stdout/dialog title+content) | STOP step, mark as deterministic failure, escalate |
| `step_time_budget` | **5 min default, configurable per step** | Kill process via process-tracker, write timeout-event |
| `turn_time_budget` | **30 min default** | Emit pause turn with current progress, escalate to user |
| `no_progress_window` | **3 consecutive actions with identical visible state** (screenshot hash + window title hash) | STOP, emit `❌ LOOP_DETECTED` blocker with evidence |
| `popup_count` | **2 identical popups** | Auto-kill parent process, do NOT dismiss again |

### Error hash schema

When any error / popup / stderr is observed:

```json
{
  "step_id": "validate-night-recon",
  "iteration": 2,
  "error_hash": "sha256(<error_title>:<error_text>:<exit_code>)",
  "first_seen": "<ISO8601>",
  "count": 2,
  "evidence": ["logs/screenshot-<TS>.png", "logs/stderr-<TS>.txt"]
}
```

Logger appends this to `logs/error-history-<TS>.jsonl`. Loop-detector reads it at every
retry attempt.

### Loop-detector pattern (refined per research/07 §3 — OpenHands StuckDetector)

Detect THREE distinct loop types:

```
ON every retry of a step:
  1. Compute:
     - action_class    = high-level category of attempted action (e.g. "validate-mission", "install-tool")
     - error_class     = high-level category of failure (e.g. "popup-license", "timeout", "exit-nonzero")
     - state_hash      = sha256(visible_window_titles + screenshot_phash + last_50_log_lines)
  2. TYPE A — Identical-Repeat Loop:
     - If ≥4 retries in a row produce same (action_class, error_class, state_hash) → ❌ LOOP_DETECTED
     - (Threshold 4, not 2 — Cursor false-positive lesson)
  3. TYPE B — Repeated-Error Loop:
     - If ≥4 retries produce same error_class with DIFFERENT action_classes → ❌ REPEATED_ERROR_LOOP

---

## Kill-Switch

The orchestrator polls for `sprint-kill.flag` in the repo root at **every branch
transition** (start/end of each sprint stage, sub-task boundary, or before any
commit-and-push).

If the file exists:
1. Delete the flag
2. Write `tasks/STATE.json` with `reason: "user-kill"`, `phase: "PHASE_D_RETURN"`
   and whatever partial state was completed
3. Commit the current state: `git commit -m "chore: user-kill halt at <stage>"`
4. Push
5. Exit cleanly — NO `Ctrl+C`, NO unsaved state

How user triggers it:
  ```powershell
  # From any PowerShell window while sprint is running:
  powershell -ExecutionPolicy Bypass -File scripts\sprint-kill.ps1
  ```

Goal: user can stop an overnight autonomous sprint without losing state or leaving
the repo dirty. The flag approach survives across tool calls and process restarts.
     - Means underlying issue isn't action-shaped; bug-fixer must change problem framing
  4. TYPE C — Monologue Loop (model reasons without acting):
     - If ≥3 consecutive plan-only events with no tool-call → ❌ MONOLOGUE_LOOP
     - Means model is stuck thinking; escalate immediately
  5. TYPE D — No-Progress Loop (separate detector, not retry-bound):
     - If ≥3 turns close with workspace-diff = ∅ → ❌ NO_PROGRESS
     - Means even though things "ran", nothing changed

ON loop detected (any type):
  - kill responsible process if any
  - dump evidence (screenshots, logs, action history)
  - escalate via bug-fixer with loop type tag
  - if bug-fixer can't break loop in <3 min → emit pause turn to user
  - never ask user to "click OK" or "dismiss popup" — that's the protocol's job
```

### User-facing rule (NEVER violate)

If user is being asked the same question / shown the same prompt twice → that is a
**protocol bug**, NOT a user problem. Loop-detector must catch this before user sees it.
Escalate with evidence (screenshots + log dumps), do not retry blindly.

---

## Screenshot Evidence (mandatory for GUI claims)

Whenever main agent or sub-agent makes a claim about GUI state (e.g. "Workbench loaded",
"dialog dismissed", "mission visible on map"), screenshot evidence MUST be attached.

### Capture (Windows PowerShell — native, no install)

```powershell
function Take-Screenshot {
    param([string]$OutPath, [int]$DelaySec = 0)
    if ($DelaySec -gt 0) { Start-Sleep -Seconds $DelaySec }
    Add-Type -AssemblyName System.Windows.Forms,System.Drawing
    $bounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
    $gfx = [Drawing.Graphics]::FromImage($bmp)
    $gfx.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save($OutPath, [Drawing.Imaging.ImageFormat]::Png)
    $gfx.Dispose(); $bmp.Dispose()
    Write-Output "SCREENSHOT: $OutPath"
}
# Multi-monitor: use [Windows.Forms.Screen]::AllScreens
```

### Capture (macOS)

```bash
screencapture -x logs/screenshot-$(date +%s).png   # silent, no shutter sound
```

### Window enumeration (Windows — detect popups)

```powershell
function Get-VisibleWindows {
    Get-Process | Where-Object {
        $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne ""
    } | Select-Object Id, ProcessName, MainWindowTitle, Responding
}
```

### Schema

Every screenshot event is logged:

```json
{
  "t": "<ISO8601>",
  "kind": "screenshot",
  "path": "logs/screenshot-<TS>.png",
  "windows": [{"pid":1234, "name":"...", "title":"...", "responding":true}],
  "phash": "<perceptual hash>",
  "context": "post-validate-night-recon"
}
```

### Interpretation (ui-tester sub-agent)

ui-tester reads the PNG (Claude is multimodal), classifies:

```json
{
  "agent": "ui-tester",
  "screenshot": "logs/screenshot-<TS>.png",
  "classification": "ok | error_popup | progress | crashed | unknown",
  "extracted_text": "<OCR'd text from any dialog>",
  "suggested_action": "wait | dismiss | kill_process | escalate",
  "confidence": 0.0-1.0
}
```

If classification = `error_popup` and confidence ≥ 0.7:
- If error_hash matches previous → loop-detector fires
- If new → bug-fixer analyzes, proposes action
- Never auto-click "OK" on an error popup — that just hides the problem

---

## Dependency Pre-flight (dep-installer pattern)

Before any task that needs tools, verify ALL deps are present. Missing → install (with user
authorization only if cost/license/security gate applies).

### Pre-flight schema

```json
{
  "task_id": "004",
  "required_deps": [
    {"name":"git", "check":"git --version", "min_version":"2.40", "install":"winget install Git.Git"},
    {"name":"python", "check":"python --version", "min_version":"3.11", "install":"winget install Python.Python.3.12"},
    {"name":"powershell-screenshot", "check":"native", "min_version":null, "install":null},
    {"name":"workbench-diag", "check":"Test-Path '<path>'", "min_version":null, "install":"steam://install/1874910"}
  ]
}
```

dep-installer runs each `check`, captures result. If missing AND `install` ≠ null AND
not blocked by gate → executes install. Reports all outcomes to main agent.

### User-gate for installs

Auto-install when:
- Free, open-source CLI tool (winget / homebrew / pip)
- Already-licensed tool (Steam re-download)
- PowerShell native module

User confirmation required for:
- Paid software (Adobe, JetBrains, etc.)
- Anything that requires a login flow
- Modifications to system-wide PATH or registry

---

The loop typically lives in Opus 4.7 territory: novel problem-solving, sub-agent orchestration,
multi-step planning. But certain phases of a project are **execution-bound** — bulk processing,
mass-edit, repeated structured work where Opus's deep reasoning is overkill.

### When to hand off to Sonnet 4.6

Trigger conditions (ALL must be true):
1. The remaining work is a finite, well-defined plan (no open design questions)
2. Each step is mechanical (apply pattern X to N files, parse N logs, generate N reports)
3. The plan can be fully specified in <2000 tokens
4. Failures from a single Sonnet step are recoverable (idempotent or retryable)

### Handoff protocol

Opus produces a **Sonnet Brief** file at `playbook/handoffs/sonnet-brief-<TS>.md` containing:

```
# Sonnet Brief — <task name>

## Goal
<one-paragraph what + why>

## Inputs
- <file path / state needed>

## Steps (deterministic)
1. <atomic action>
2. ...

## Success criteria
- <objective check>

## Failure handling
- If <X>: <recovery>
- Else: stop, escalate to Opus

## Output target
<where to write results>
```

Sonnet executes the brief. Writes results back.

### Final Opus Audit

After Sonnet finishes, **Opus is auto-triggered** for a final iteration:

```
1. Read Sonnet's output
2. Spawn auditor sub-agent with the original Sonnet Brief + actual output
3. Identify gaps / quality issues / missed edge cases
4. Apply final polish (or kick another mini-Sonnet cycle if needed)
5. Generate final output paper → send back to other side via relay
```

Result: Opus does the framing + closing, Sonnet does the volume. Cost-efficient + quality-stable.

### Two blueprints

Reusable orchestration templates live in:

- `playbook/BLUEPRINT_LOOP_OPUS_SONNET.md` — hybrid loop (with handoff)
- `playbook/BLUEPRINT_LOOP_OPUS_ONLY.md` — pure Opus loop (no handoff, for deep-problem projects)

These are project-agnostic. Combine with a project-specific "First-Output" (goal + state
+ constraints) to bootstrap any new cross-device project.
