# Sprint Full Day — META Self-Optimize + S5+S6+S7 (single-paste, fully autonomous bootstrap)

> Pasted ONCE in PC Claude Code (Sonnet 4.6 default). Handles everything from there:
> git state cleanup, dependency verify, META self-optimize (5 safety improvements),
> then full S5+S6+S7 sprint. Two user-confirm pauses only.
> Duration: ~30-45 min META + 4-8h Sprint = 5-9h total.

---

## The trigger (paste ONLY this into PC Claude Code chat)

```
Read playbook/handoffs/SPRINT-FULL-DAY-WITH-META.md and execute the WRAPPER block at the bottom of this file. Handle git state autonomously (stash + commit regen artifacts if needed). Start with Phase 0 setup, then ask me to confirm before Phase META, then ask me again before Phase SPRINT. cd to the repo automatically — find it via $env:USERPROFILE\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios or wherever git rev-parse --show-toplevel resolves.
```

---

## WRAPPER (PC Claude Code executes this — do not paste manually)

```
═══════════════════════════════════════════════════════════════════════════════
 SPRINT FULL DAY: META Self-Optimize + S5 + S6 + S7
 Model: Sonnet 4.6 (default). Escalate to Mac-Opus via git push + chat-pause
        on the explicit triggers in PHASE SPRINT section F.
 Duration: ~30-45 min META + 4-8h SPRINT.
 User-present: Phase 0 confirm, PHASE SPRINT Stage A, PHASE SPRINT Stage D.
 Autonomous: PHASE META, PHASE SPRINT Stages B + C + E.
═══════════════════════════════════════════════════════════════════════════════

You are PC-Executor. You handle EVERYTHING from this prompt forward — git ops,
PowerShell scripts, file edits, sub-agent spawns. The user only confirms
2 pauses (after Phase 0, before PHASE SPRINT) and is present for Stages A + D.

PHASE 0 — Setup (~2 min, autonomous)
─────────────────────────────────────
Step 0.1 Find repo + cd
  - Try: cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
  - Fallback: git rev-parse --show-toplevel from current dir
  - Confirm: pwd output is the repo root

Step 0.2 Git state cleanup
  - git status
  - If uncommitted changes that look like regen artifacts (DISCLOSURE.md
    timestamp updates, mint-log changes, etc.):
    git add -A && git commit -m "chore: local regen artifacts pre-sprint"
  - If uncommitted changes that look intentional (real code edits):
    git stash, proceed, restore at end of Phase 0
  - git pull --rebase
  - Confirm: clean working tree

Step 0.3 Quick dep verify
  - powershell -ExecutionPolicy Bypass -File .\scripts\verify-deps.ps1
  - Expect: ALL DEPS PRESENT (per yesterday's verify run)
  - If any missing: report to user, ask if I should auto-install via
    .\scripts\verify-deps.ps1 -InstallMissing

Step 0.4 Read foundational docs (you must hold these in context)
  - playbook/handoffs/POSTMORTEM-AND-LESSONS.md
  - playbook/handoffs/SPRINT-TOMORROW-S5-S6-S7-TRIGGER.md (the sprint plan)
  - playbook/RELAY_PROTOCOL.md
  - PC_AGENT_BRIEF.md
  - playbook/CHEATSHEET-PC.md
  - pc-requirements.toml (manifest, do NOT install mid-sprint)

Step 0.5 USER PAUSE #1
  - Report to user:
    "Phase 0 done. Repo synced, deps green, docs read.
     Latest commit: <hash>.
     Ready to start PHASE META (~30-45 min self-optimize). Confirm 'meta go'
     to start, or 'skip meta' to go directly to PHASE SPRINT."

═══════════════════════════════════════════════════════════════════════════════
PHASE META — Self-Optimize Iteration Loop (~30-45 min, autonomous)
═══════════════════════════════════════════════════════════════════════════════

5 improvements that make the sprint safer for multi-hour autonomous run.
Implement M.1 → M.5 in order. Commit + push at end of phase.

M.1 KILL-SWITCH (~5 min)
─────────────────────────
- Create scripts/sprint-kill.ps1:
  Single line: New-Item -ItemType File -Path "$PSScriptRoot\..\sprint-kill.flag" -Force | Out-Null
  Plus header comment explaining: "User runs this from another PowerShell to
  signal sprint to halt cleanly at next branch transition."
- Add to .gitignore: sprint-kill.flag
- Update playbook/RELAY_PROTOCOL.md: add section "Kill-Switch":
  "Orchestrator polls sprint-kill.flag at every branch transition. If exists:
   delete flag, write final state to STATE.json including reason='user-kill',
   commit + push, exit cleanly. Goal: user can stop autonomous sprint without
   ctrl+C losing state."
- Verify: touch the flag manually + delete it (test it works).

M.2 CU FORENSIC LOG (~10 min)
──────────────────────────────
- Update scripts/computer-use/run_task.py:
  - Add LOG_DIR_PER_SESSION = LOG_DIR / f"cu-{ts}-session"
  - Save screenshot before every action: $LOG_DIR_PER_SESSION/screenshot-<turn>.png
  - Save transcript JSONL: $LOG_DIR_PER_SESSION/transcript.jsonl with
    {turn, screenshot_path, prompt_preview, tool_use, decision_reasoning}
  - At session end: write summary.md with first 5 + last 5 turns + outcome
- Goal: any CU session is replay-able for debugging.
- Test: run a tiny task (open notepad, close) and verify forensic dir created.

M.3 PROCESS WHITELIST (~10 min)
────────────────────────────────
- Create playbook/SAFETY-WHITELIST.md:
  Allowed Computer Use target windows (substring match on MainWindowTitle):
  - ArmaReforgerWorkbench (any variant)
  - Steam (Steam client)
  - Windows Terminal / PowerShell / cmd
  - Notepad (smoke tests)
  - File Explorer (path nav)
  REFUSE clicking into: any other window. Especially: banking sites, password
  managers, social media, anything personal.
- Update scripts/computer-use/windows_computer.py:
  - Add WHITELISTED_TITLES = [...] constant
  - Before every click action: get active window title, check substring match
  - If not whitelisted: refuse, log to forensic, raise NonWhitelistedWindow
- Update run_task.py to handle NonWhitelistedWindow: report blocker to STATE.json,
  pause for user, do NOT retry blindly.
- Test: temporarily add Notepad to NOT-whitelist, try smoke, confirm refusal.

M.4 DRY ENFORCEMENT (~10 min)
──────────────────────────────
- Create logs/destructive-ops.jsonl (append-only)
- Update RELAY_PROTOCOL.md DRY marker section:
  "Every destructive op (Remove-Item -Recurse, git reset --hard, file deletion,
  drop-database, etc.) MUST be preceded by a DRY plan committed to repo at
  playbook/dry-plans/<ts>-<short>.md. Auditor before push reads
  logs/destructive-ops.jsonl and cross-checks: every destructive op has a
  matching DRY plan committed before the op ran. If unmatched: BLOCK push.
  Sprint stops, escalates."
- Add to sprint trigger F section: orchestrator logs destructive ops to
  logs/destructive-ops.jsonl in format {ts, op, target, dry_plan_path, user_approved}.
- Test: simulate a Remove-Item without DRY plan, verify auditor blocks.

M.5 NETWORK EGRESS DOC (~5 min)
────────────────────────────────
- Create playbook/SAFETY-EGRESS.md:
  Allowed network endpoints during sprint:
  - api.anthropic.com (Anthropic SDK)
  - github.com / raw.githubusercontent.com (git)
  - api.github.com (gh CLI)
  - community.bistudio.com (Bohemia wiki — research)
  - github.com/BohemiaInteractive (samples — research)
  - reforger.armaplatform.com (Bohemia news/docs)
  - feedback.bistudio.com (BI files — research)
  - steamcommunity.com / store.steampowered.com (Steam — research)
  - pypi.org / pip indexes (when pc-requirements.toml install runs pre-sprint)
  - npmjs.com / npm registry (when chokidar install runs pre-sprint)
  Forbidden: anything else. If sprint code calls a non-listed host:
  - Auditor catches via grep of new urllib/requests/httpx calls in commits
  - Sprint stops, escalates for user review
- Test: search codebase for any external HTTP calls, verify all hit whitelisted hosts.

M.6 COMMIT + PUSH ALL META IMPROVEMENTS
─────────────────────────────────────────
- git add scripts/ playbook/ .gitignore logs/destructive-ops.jsonl (empty)
- git commit -m "feat: M.1-M.5 loop safety improvements pre-sprint
  - M.1 kill-switch (file-flag polled at branch transitions)
  - M.2 CU forensic log (screenshot+transcript per session, replay-able)
  - M.3 process whitelist (CU refuses non-whitelisted windows)
  - M.4 DRY enforcement (auditor blocks destructive ops without DRY plan)
  - M.5 network egress doc (allowed endpoints listed)
  Per Postmortem patterns + user request: safer for multi-hour autonomous."
- git push

═══════════════════════════════════════════════════════════════════════════════
USER PAUSE #2 — Confirm SPRINT start
═══════════════════════════════════════════════════════════════════════════════
- Report:
  "PHASE META done. 5 safety improvements committed.
   Latest commit: <hash>.
   Ready for PHASE SPRINT (S5 close + S6 polish + S7 foundation, 4-8h).
   Stage A (~1-2h) needs you at PC for live coaching.
   Stages B+C (~4h) autonomous — you can step away.
   Stage D (~1-2h) needs you at PC for manual ingame tests.
   Stage E (~30 min) autonomous final audit.
   Confirm 'sprint go' to start Stage A."

═══════════════════════════════════════════════════════════════════════════════
PHASE SPRINT — S5 close + S6 polish + S7 foundation (~4-8h)
═══════════════════════════════════════════════════════════════════════════════

Read the FULL sprint plan at:
playbook/handoffs/SPRINT-TOMORROW-S5-S6-S7-TRIGGER.md

Execute its WRAPPER block (the ╔══ block at the bottom), with these
modifications now active from PHASE META:

A. Poll sprint-kill.flag at every branch transition (M.1)
B. All Computer Use sessions log to forensic dir (M.2)
C. Computer Use refuses non-whitelisted windows (M.3)
D. Auditor enforces DRY before destructive ops (M.4)
E. Sprint code touches only whitelisted endpoints (M.5)

Stages (full detail in SPRINT-TOMORROW-S5-S6-S7-TRIGGER.md):
A. S5 Close — user at PC, refactor plugin to documented Bohemia pattern,
   CLI launch, viewport verify, snapshot (~1-2h)
B. S6 Polish — autonomous, PyWebView chat + streaming + Director mode (~2h)
C. S7 Foundation — autonomous, REAL Task() parallel spawn for Bohemia
   GameMaster sample scan + plugin skeleton + runtime bridge (~2h)
D. Manual ingame tests — user at PC, 5 GM prompts + paraphrase test (~1-2h)
E. Final audit + push + tag (~30 min)

ESCALATION TRIGGERS (write blocker via git push + ask user in chat):
- 3x retry exhausted on any step
- Validate-vs-live discrepancy (postmortem Failure #1)
- WorldEditor module returns null despite -wbmodule= flag
- Novel error class not in research/EMPIRICAL.md
- Token budget >900k
- sprint-kill.flag touched by user (clean exit, not escalation)
- Process whitelist denied 3+ times (something fundamentally wrong)
- Auditor blocks DRY check (destructive op without plan)

START NOW. Phase 0 first.
```

---

## Why this is better than yesterday's approach

| Yesterday | Today |
|---|---|
| Multi-step manual: I tell you shell commands, you paste | One paste, PC handles everything |
| Sprint trigger separate from setup | Sprint trigger includes setup |
| No self-optimize step | META improvements pre-sprint |
| Whitelist undefined | Process + egress + DRY all explicit |
| Kill-switch unclear | File-flag pattern, documented |
| CU sessions hard to replay | Forensic logging per session |

---

## What user does (literally)

1. Open PC Claude Code chat (Sonnet 4.6 selected)
2. Paste the 3-line trigger at top of this file
3. PC navigates to repo, handles git, runs verify-deps, reads docs
4. PC pauses: "Confirm meta go?"
5. User: "go"
6. PC runs M.1-M.5 (~30-45 min)
7. PC pauses: "Confirm sprint go?"
8. User: "go" (and stays nearby for Stage A coaching)
9. Sprint runs ~4-8h
10. Done.

Total user input: 1 paste + 2 confirmations. Everything else autonomous.
