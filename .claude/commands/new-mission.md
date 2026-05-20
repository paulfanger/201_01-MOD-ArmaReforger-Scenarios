Starte eine neue Mission.

Argument: $ARGUMENTS (Mission-Name in kebab-case, z.B. `night-recon-everon`)

Workflow:
1. Wenn $ARGUMENTS leer: frag User nach Mission-Namen
2. Validiere: $ARGUMENTS ist kebab-case (lowercase + hyphens), nicht "test-mission-pipeline-check" (reserved für Self-Testing)
3. Prüfe: existiert `missions/$ARGUMENTS/` bereits? Wenn ja: warne User, frag ob überschreiben oder abbrechen
4. Lege Struktur an:
   ```
   missions/$ARGUMENTS/
   ├── current-stage.json     ({"stage": 1, "status": "awaiting_input"})
   ├── narrative.json         (leer, wird von narrative-designer befüllt)
   ├── asset-manifest.json    (leer)
   ├── encounters.json        (leer)
   ├── output/                (leer)
   ├── snapshots/             (leer)
   ├── manual-test-results/   (leer)
   └── stage-log.jsonl        (leer)
   ```
5. Rufe `mission-director` Subagent mit Briefing:
   - Neue Mission `$ARGUMENTS` startet bei Stage 1
   - mission-director führt User durch Stage 1 (Narrative Extraction)
6. Logge Eintrag in `WORK_LOG.md`: "Mission $ARGUMENTS gestartet [timestamp]"
