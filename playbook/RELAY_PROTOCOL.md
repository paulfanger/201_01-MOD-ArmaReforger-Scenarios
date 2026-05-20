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

Every directive has one of three markers:

| Marker | Meaning | Who acts |
|---|---|---|
| **🤖 EXEC** | Paste into Claude Code on PC. Claude executes autonomously (Bash / PowerShell / Read / Write). | PC's Claude |
| **🧠 ANSWER** | Question for Paul himself, in his own words (decisions, preferences). | Paul (human) |
| **⚙️ DO** | Manual action on the PC by hand (UI click, EULA accept, Steam install dialog, settings.json edit). | Paul (human, at PC) |

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

## Opus 4.7 → Sonnet 4.6 Handoff

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
