Rolle Mission zu einem früheren Snapshot zurück.

Argument: $ARGUMENTS — Snapshot-ID (z.B. "002") oder Label (z.B. "stage-1-approved")

Workflow:
1. Identifiziere aktive Mission
2. Wenn $ARGUMENTS leer: zeige Snapshot-Liste aus INDEX.json, frag User welcher
3. Validiere: Snapshot existiert in INDEX.json
4. Bestätige mit User: "Rollback zu '{label}' vom {timestamp}? Aktuelle Änderungen werden in pre-rollback-{ts} gesichert."
5. Bei User-Bestätigung:
   - Rufe `version-keeper` mit Operation "rollback"
   - version-keeper erstellt pre-rollback-Snapshot
   - version-keeper restored Files
   - Update current-stage.json
6. Logge in `stage-log.jsonl`: `{"event": "rollback", "from": "{current-snapshot}", "to": "{target}", "timestamp": "..."}`
