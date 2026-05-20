Trigger die komplette Self-Testing-Pipeline manuell.

Argument: $ARGUMENTS — optional, Mission-ID. Default: aktive Mission

Workflow:
1. Identifiziere Target-Mission ($ARGUMENTS oder aktiv)
2. Verifiziere: missions/{id}/output/ existiert und nicht leer
3. Triggere Test-Sequenz:
   a. `pipeline-tester` → wartet auf Pass
   b. Bei Fail: `bug-fixer` → re-run a (max 5 Iterationen)
   c. `mission-validator` → wartet auf Pass
   d. Bei Fail: `bug-fixer` → re-run c (max 5 Iterationen)
   e. `workbench-integration-tester`
   f. Bei Mode-A-Fail: `bug-fixer` → re-run e
   g. Wenn alle grün: `readiness-reporter`
4. Output: 
   - Pass: README mit Status, Reports im Mission-Dir, READY_FOR_MANUAL_TESTING.md
   - Halt: HALT_BRIEFING.md mit Optionen für User
