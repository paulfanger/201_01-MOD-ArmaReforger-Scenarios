# Turn 5 Reflection (Mac-side)

## What went well

- Task 005 (PC) lieferte einen großen Win: **3/3 Validate PASS** in iter=1. Author-Fix +
  Junction-Strategie wirken zusammen. Validate ist jetzt der stabile CI-Gate für Mac-Side
  iteration.
- Two-Phase Reception von PC korrekt ausgeführt: Phase A leer → direkt zu Phase C, Phase D
  als saubere single-output-block. Quick-Scan-Pattern funktioniert.
- StuckDetector mit threshold 4 (statt 2): nicht gefeuert in Task 005, weil alle Steps
  in 1 iter durchgingen. Threshold-Empfehlung aus research/07 ist sound.
- Reflexion-Pattern: reflection-turn-3.md (Mac) wurde von PC vor Phase C gelesen,
  reflection-turn-4.md von PC danach geschrieben. Memory funktioniert über die Devices.
- Research-Background-Agent für Master Kickoff Blueprint (research/08) lieferte
  konkrete source-cited Patterns in 81s.

## What failed (and why)

- **research/06 Section B (`-wbSilent -exitAfterInit -load`)**: empirisch disconfirmed.
  Workbench-Diag 1.6.0.119 mit der CLI-Form lädt keinen World, exited clean nach Engine-Init.
  Doc wurde auf Wiki/Community-Sources gestützt — die scheinen für ältere Versions zu
  gelten oder die `-load`-Semantic ist undokumentiert anders. Mac sollte künftige
  Spec-Claims empirisch validieren BEVOR sie in Task gehen.
- **pc-setup.ps1 Line 49 quoting bug**: backtick-n in double-quote war OK in PowerShell-Theorie,
  hat aber im echten Parser stolperte. Lesson: für portable PowerShell verwende lieber
  `Write-Output ""` + `Write-Output "..."` oder explizite Strings ohne Escape-Magie.
- **DRY marker noch nie eingesetzt**: definiert seit Turn 4, aber bisher kein Use-Case
  ausgelöst. Mac fügt Task 006 als ersten echten Demo-Case ein (addon-folder cleanup).

## What I'd do differently next turn

- **Empirische Validation vor Spec**: bevor research/N als "ready" markiert wird, mindestens
  einmal vom PC quick-test laufen lassen (low-cost validate-only-run).
- **PowerShell-Quoting empirisch**: bei jedem Script-Output, einmal `powershell -File X.ps1`
  testweise laufen lassen (Mac kann das per pwsh emulieren wenn installed, oder PC im
  pre-flight).
- **DRY-Pattern intuiver einbauen**: nicht nur als "marker", sondern als CONCRETE pattern
  in jedem Step der reversible/destructive Ops macht. Task 006 demonstriert.

## Signals for optimizer

- duration_ms (Mac-side this turn): ~2,700,000 (45 min — größtenteils Research + Doc-writing)
- sub-agents spawned (Mac): 2 background research (research/08 + style-profile)
- guards fired: none Mac-side (kein Execution)
- loop signals (Mac-side): none

## Decisions made this turn

- Smoke-test Alternative: **(b) GUI + Auto-Screenshot + multimodal ui-tester**
  (not plugin which is pseudocode, not Linux-dedi which needs extra setup)
- research/06 Section B: labelled DISCONFIRMED with task 005 commit ref
- pc-setup.ps1: rewritten with New-Item -Junction (PowerShell-native, no cmd-quoting)
- PC_AGENT_BRIEF: Sonnet-compatibility documented (escalation-triggers hold the line)
- 🧪 DRY marker: first real demo in Task 006 (addon-folder cleanup)

## Carry to next turn's plan

- Wenn Task 006 GUI-Smoke 1+ Mission als "mission_loaded" classifies → Phase 3 (Game
  Launcher test) kann starten. Plan: User opens game manually, picks mission from list,
  startet, spielt eine Minute, screenshot.
- Wenn 0 Missions loaded → bug-fixer-Vorschläge prüfen (Workbench-Plugin half-impl ist
  möglicherweise näher als wir dachten, wäre Mac-Side Phase 2 dev work)
- Sonnet-Switch auf PC: stille Beobachtung wenn Paul switched — Qualitäts-Drift?
  reflection-turn-N.md vom PC sollte Indikator sein.
