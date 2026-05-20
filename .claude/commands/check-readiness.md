Checke ob aktive Mission ready für Manual Testing ist. KEIN Re-Run, nur Read.

Argument: $ARGUMENTS — optional, Mission-ID. Default: aktive Mission

Workflow:
1. Identifiziere Target-Mission
2. Lies alle Test-Reports:
   - test-report.json
   - validation-report.json
   - integration-report.json
3. Lies READY_FOR_MANUAL_TESTING.md ODER HALT_BRIEFING.md (wenn vorhanden)
4. Output an User (kurz):
   ```
   Mission: {name}
   Pipeline: {pass/fail}
   Validation: {pass/fail}
   Integration: {pass/manual_required/fail}
   
   Status: {ready_for_manual / iterating / halted / not_started}
   
   Nächster Schritt: {konkrete Action für User}
   ```
