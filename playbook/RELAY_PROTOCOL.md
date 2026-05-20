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
