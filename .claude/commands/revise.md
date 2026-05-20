Revidiere die aktuelle Stage mit User-Feedback. KEIN Snapshot (Snapshot nur bei /approve).

Argument: $ARGUMENTS — User-Feedback in natürlicher Sprache

Workflow:
1. Identifiziere aktive Mission und aktuelle Stage N
2. Wenn $ARGUMENTS leer: frag User nach Feedback
3. Lies aktuellen Stage-Output (z.B. narrative.json bei Stage 1)
4. Rufe entsprechenden Stage-Specialist mit:
   - Current-Output
   - User-Feedback ($ARGUMENTS)
   - Hinweis: "REVISE — nicht regenerate from scratch. Behalte was gut ist, ändere was User kritisiert."
5. Specialist schreibt neuen Output (überschreibt Stage-Output-File)
6. Stage-Status bleibt "in_progress"
7. Logge in `stage-log.jsonl`: `{"event": "revise", "stage": N, "feedback": "$ARGUMENTS", "timestamp": "..."}`
8. mission-director präsentiert User die Änderungen + erneuter Approval-Gate
