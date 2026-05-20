Zeige Status der aktuellen Mission-Stage.

Argument: $ARGUMENTS — optional, Stage-Nummer (1-8) zum Wechsel; leer für Anzeige

Workflow:
1. Identifiziere aktive Mission:
   - Lies `current-mission.json` im Repo-Root wenn vorhanden
   - Sonst: Liste alle `missions/*/current-stage.json`, frag User welche
2. Wenn $ARGUMENTS leer:
   - Zeige Stage-Status visuell:
   ```
   Mission: night-recon-everon
   
   Stage 1 ✅ approved (snapshot 001)
   Stage 2 ✅ approved (snapshot 002)
   Stage 6 🟡 in_progress (encounters being designed)
   ```
3. Wenn $ARGUMENTS = Stage-Nummer:
   - Validiere: stage_n existiert in Pipeline (1-8)
   - Validiere: stage_n ist in MVP-Scope (1, 2, 5, 6) — sonst warne
   - Validiere: vorherige Stages sind approved (kein Stage-Skipping)
   - Rufe mission-director: "User möchte zu Stage $ARGUMENTS wechseln"
4. Approval-Gates respektieren: Stage-Sprung ist NUR möglich wenn alle dazwischenliegenden Stages approved
