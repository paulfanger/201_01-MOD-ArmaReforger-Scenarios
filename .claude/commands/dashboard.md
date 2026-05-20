Zeige Projekt-Übersicht: alle Missionen, Status, recent activity.

Argument: keine

Workflow:
1. Lies `missions/*/current-stage.json` für alle aktiven Missionen
2. Lies letzten 5 Einträge aus jeder `stage-log.jsonl`
3. Lies `WORK_LOG.md` letzten Eintrag
4. Output Tabelle:
   ```
   ## Active Missions
   
   | Mission-ID | Stage | Status | Last Action | Snapshot |
   |---|---|---|---|---|
   | night-recon-everon | 2 | awaiting_approval | 2026-05-20 14:23 | 001_stage-1-approved |
   | convoy-ambush-arland | 6 | iterating | 2026-05-20 13:55 | 003_stage-6-approved |
   
   ## Recent Activity (last 5)
   ...
   
   ## Git Status
   {git status output}
   
   ## Project Health
   - Catalog: {N} factions, {M} vehicles, {K} weapons
   - Active backend: {running on :8765 / not running}
   ```
5. Wenn keine aktive Mission: hint zu /new-mission
