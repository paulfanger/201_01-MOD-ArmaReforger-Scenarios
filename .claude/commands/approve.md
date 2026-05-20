Approve die aktuelle Stage der aktiven Mission. Triggert Snapshot und Stage-Advance.

Argument: $ARGUMENTS — leer (default), oder Label-Override für den Snapshot

Workflow:
1. Identifiziere aktive Mission (siehe /stage)
2. Lies `current-stage.json` → aktuelle Stage N
3. Verifiziere: Stage-N-Output existiert und ist nicht-leer
   - Stage 1: narrative.json hat min. Felder title, factions, biome, tone
   - Stage 2: asset-manifest.json hat min. 1 resolved asset
   - Stage 6: encounters.json + output/*.conf
4. Rufe `version-keeper`:
   - Snapshot-Label: `$ARGUMENTS` ODER default `stage-{N}-approved`
   - Inkludiere alle relevanten Files (siehe version-keeper.md schema)
5. Update `current-stage.json`:
   - status: "approved"
   - Wenn N+1 in MVP-Scope: stage=N+1, status="awaiting_input"
   - Sonst: status="mvp-complete"
6. Rufe `mission-director`:
   - Briefing: Stage N approved, snapshot {id} created, advance zu Stage N+1
   - mission-director triggert nächste Stage automatisch
7. Logge in `stage-log.jsonl`: `{"event": "approve", "stage": N, "snapshot": "...", "timestamp": "..."}`
