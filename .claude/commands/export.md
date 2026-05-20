Exportiere die aktuelle Mission als Reforger-Mission-Files.

Argument: $ARGUMENTS — optional, Output-Format. Default: "zip"

Workflow:
1. Identifiziere aktive Mission
2. Verifiziere: alle MVP-Stages approved (Stages 1, 2, 6)
3. Wenn nicht: warne User, list missing approvals
4. Rufe `reforger-bridge`:
   - Input: alle relevanten Mission-Files
   - Output: `missions/{mission-id}/output/` mit allen .conf/.et/.layer/.gproj
5. Rufe Testing-Pipeline:
   - pipeline-tester
   - mission-validator
   - workbench-integration-tester
6. Wenn alle grün: 
   - Pack `output/` zu ZIP: `missions/{mission-id}/{mission-id}.zip`
   - readiness-reporter schreibt READY_FOR_MANUAL_TESTING.md
7. Wenn Fail:
   - bug-fixer-Loop (max 5 Iterations)
   - Bei Halt: User-Briefing mit Optionen
