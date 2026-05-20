Manueller Snapshot der aktuellen Mission-State, OHNE Stage-Advance.

Argument: $ARGUMENTS — Label für den Snapshot (z.B. "before-encounter-experiment")

Workflow:
1. Wenn $ARGUMENTS leer: frag User nach Label
2. Validiere: Label ist kebab-case, kein Conflict mit auto-Labels (stage-N-approved, pre-rollback-*, pre-fix-*)
3. Identifiziere aktive Mission
4. Rufe `version-keeper`:
   - Trigger: manual
   - Label: $ARGUMENTS
5. Bestätige User: "Snapshot 'XXX_$ARGUMENTS' erstellt"
