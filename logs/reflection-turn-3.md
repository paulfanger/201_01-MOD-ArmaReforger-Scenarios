# Turn 3 Reflection (Mac-side)

## What went well
- Anti-loop guards landed before next PC run — protocol gap closed.
- PC's Task 003 result reached us cleanly via Git (commit 655c2f4). Structured report,
  clear blockers, four well-formed questions.
- PC autonomously fixed engine-init via vanilla-junctions — exactly the right scope
  (PC-side reversible fix, not Mission-Files territory). Correctly escalated the
  `Author`-keyword issue to Mac as "New questions" because it's a Mac-side code change.
- Sub-agent fleet did its job: logger, bug-fixer, auditor all ran, auditor allowed push
  despite smoke-skip with a warning. Good calibration.

## What failed (and why)
- **Author keyword in addon.gproj** — backend/exporters/gproj.py emitted `Author "X"` line.
  Enfusion schema doesn't accept it → `-validate` failed on all 3 missions. Root cause:
  pre-flight schema check missing; we used research/02 mission-format docs but didn't
  empirically validate every keyword against the actual Workbench-Diag.
- **`-validate` exit-code is unreliable** — PC reports empty exit-code on success AND
  failure. We relied on it. Need to switch to log-pattern matching per research/06.
- **No `tasks/STATE.json` existed** — if PC had crashed mid-task, recovery would have
  required re-reading the chat. Fixed in this turn.
- **No `reflection.md` from Turn 2** — Reflexion-style memory wasn't yet a thing.
  Starting now.

## What I'd do differently next turn
- Empirically validate every codegen template against real `-validate` BEFORE shipping
  it (run smoke test from Mac side via Linux dedi server if accessible — Open Question 1
  is unblocker here).
- Switch validation criterion from exit-code to log-pattern matching (`Entities load` +
  `Entity layer load` + zero `(F):`).
- Write reflection at end of every turn. Read predecessor at start of next turn.
- Update `tasks/STATE.json` at every phase transition.

## Signals for optimizer
- duration_ms: ~4500000 (75 min, including big research + multi-file edits)
- sub-agents spawned (mac-side): 1 (deep research agent, 120s, completed)
- sub-agents spawned (pc-side, reported): 3 (logger, bug-fixer, auditor)
- guards fired: none on mac-side (was prep work, not execution)
- loop signals (pc-side reported): 1 user-interrupt during Task 003 retry1 (Workbench
  GUI-error-popup; PC added `-wbSilent` → headless ok). This is BORDERLINE — ui-tester
  would have caught it earlier.

## Decisions made this turn
- Author-keyword removed from gproj.py template AND from all 3 mission addon.gproj files
- 4th marker `🧪 DRY` added to relay protocol (research/07 §8 missing piece)
- Loop-detector refined per OpenHands StuckDetector (4 types of loops, not just identical-hash)
- `tasks/STATE.json` schema established
- `logs/reflection-turn-<N>.md` mandatory per turn

## Carry to next turn's plan
- PC needs: Author-fix is shipped (commit incoming), proceed with hardened Task 005
- PC asked: pc-setup.ps1 for vanilla-junctions — YES, codify
- PC asked: exit-code vs log-pattern — switch to log-pattern (per research/06 success heuristic)
- PC asked: proceed with Task 004 vs wait — wait for this commit, then run Task 005 (rebased version)
