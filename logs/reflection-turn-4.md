# Turn 4 Reflection (PC-side)

## What went well
- **Author-fix wirkte sofort**: alle 3 Missionen passten validate in iter=1, kein Loop-Retry nötig. Log-Pattern based pass/fail funktioniert sauber (`0 fatals + 0 errors` als Heuristik).
- **Junctions persistent**: aus Task 003 manuell angelegte `_vanilla_core` + `_vanilla_data` waren beim Re-Run automatisch da, kein Setup-Schritt nötig.
- **Two-Phase Reception** war schnell und klar — Phase A "Checklist leer → start C direkt" sparte einen Round-Trip.
- **STATE.json**: gut zu schreiben, Phase-Transitions (PHASE_D_RETURN → PHASE_C_EXEC → PHASE_D_RETURN) waren explizite Anker im Code.
- **Logger always-on**: JSONL append-only war zero-overhead; alle Events einsehbar.
- **Mac-Side Reflection turn-3** war direkt nützlich — wusste vorher schon, dass exit-code unreliable ist und log-pattern verwenden soll.

## What failed (and why)
- **smoke-test world-load triggert nicht** mit `-wbSilent -exitAfterInit -load $A:Worlds/X.ent` Form aus research/06 Sektion B. Workbench-Diag 1.6.0.119 exited nach Engine-Init in ~5s ohne "Entities load"/"Entity layer load" Pattern. Quick-probe ohne -exitAfterInit ergab gleiches Verhalten. **Empirische Disconfirmation von research/06 Section B.**
- **scripts/pc-setup.ps1 parse-error** on line 49 (backtick-n in `"`nDone..."`). Auf diesem PC wirkungslos (Junctions schon da), aber auf fresh PC würde das Setup-Script failen.
- **Validate exit-code immer empty** — bestätigt das Mac-Side-Finding aus reflection-turn-3. Log-Pattern war 100% richtig.

## What I'd do differently next turn
- **Smoke-Test mit echtem World-Load nachweisen** — nicht über `-wbSilent` Pfad sondern eine der 3 Alternativen aus bugfix-JSON wählen (workbench-plugin / GUI+Screenshot / Linux dedi). Klären welche Mac-Side bevorzugt.
- **CLI-Flag empirisch verifizieren** bevor man Patterns aus Docs übernimmt — kann mit einem Workbench `-help` mit `> capture.txt 2>&1` oder einer Plugin-Inspection erfolgen.
- **Loop-Detector NACH erfolgreichem iter=1 PASS** ist overkill — die Schleife hier hat overhead. OK aber, weil Test ist 4s.
- **pc-setup.ps1 lokal lint-en** vor Mac-Push (mit `powershell -NoProfile -Command "Get-Content X.ps1 | %{}"` oder ähnlich Smoke-Test).

## Signals for optimizer
- duration_ms: ~510_000 (8.5 min total — turn-budget 30 min weit unterschritten)
- sub-agents spawned: 3 (logger, dep-installer, bug-fixer, auditor → 4 actually, but dep-installer was inline)
- guards fired: keine — Validate PASS auf iter=1, smoke FAIL aber kein Retry-Loop
- loop signals: keine (action+error-class hash dedup nicht getriggert)
- workbench-runs: 6 validate + 4 smoke = 10 runs, ~55s gesamte Workbench-Compute-Zeit
- user-interrupts: 0 in this turn

## Carry to next turn's plan
- **Mac-Side decision needed**: welche Smoke-Test-Alternative (workbench-plugin / GUI+Screenshot / Linux dedi)?
- **pc-setup.ps1 Line 49 fix** ist ein Quick-Win (1-line PowerShell-Quoting-Korrektur)
- **research/06 Section B** sollte als "EMPIRICALLY DISCONFIRMED" markiert werden mit Hinweis auf bugfix-task005-...json
- **validate compile-gate** ist jetzt der **stabile Quality-Gate** für Mac-Side iterations — wenn validate PASS, sind addon.gproj + scripts compile-clean
- **DRY marker** (🧪) für die kommenden destructive ops (clean addon-folder, deleteJunctions) sollte langsam eingeführt werden — bisher noch nicht genutzt
