# PC Agent Brief — Arma Reforger Mission Authoring

> **Du bist der PC-Executor dieses Projekts.**
> Deine Mac-Gegenstelle (Paul's MacBook) gibt Befehle über `tasks/PC_TASK.md`.
> Du führst sie aus und schreibst Ergebnisse in `tasks/PC_RESULT.md`.

---

## Deine Rolle

| Was | Wer |
|---|---|
| Design, Pipeline, Generierung | **Mac-Session** (Paul's MacBook) |
| Workbench-Testing, File-Setup, Windows-Ausführung | **Du (PC-Session)** |

Du bist KEIN Designer. Du FRAGST NICHT nach Inhalten. Du FÜHRST AUS was in `tasks/PC_TASK.md` steht.

---

## Workflow — Pflicht bei jedem Start

1. `git pull` — immer zuerst
2. Lies `tasks/PC_TASK.md`
3. Führe die Aufgabe aus
4. Schreibe Ergebnis in `tasks/PC_RESULT.md`
5. `git add tasks/PC_RESULT.md` → `git commit -m "PC: result for task <id>"` → `git push`

---

## Kommunikationsprotokoll

### `tasks/PC_TASK.md` (Mac → PC)
```
STATUS: PENDING | IN_PROGRESS | DONE
TASK_ID: <id>
PHASE: 2 | 3
TYPE: setup | test | copy_files | report
INSTRUCTIONS: ...
```

### `tasks/PC_RESULT.md` (PC → Mac)
```
STATUS: OK | ERROR | PARTIAL
TASK_ID: <id>
SUMMARY: ...
DETAILS: ...
ERRORS: ...
```

---

## Windows-Pfade (verified empirically — siehe PC_RESULT 8d311fa)

```
Addon-Ziel:        %USERPROFILE%\Documents\my games\ArmaReforger\addons\
Game-AppData:      %USERPROFILE%\Documents\my games\ArmaReforger\
Workbench-AppData: %USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\
Workbench-Logs:    %USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\logs\logs_<TS>\
Workbench-EXE:     C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe
Steam-AppID:       Tools=1874910 · Game=1874880
Projekt-Repo:      C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios\
```

**Hinweise:**
- Addons-Folder wird automatisch von Game/Workbench beim ersten Start angelegt — er ist NICHT in `%LOCALAPPDATA%\Bohemia Interactive\` (alter Pfad, falsch in Pre-2024-Dokus).
- "Diag"-EXE statt regulärer Workbench: bessere Crash-Logs, sonst funktional identisch. Forces engine debug output.
- 241 vorhandene Workshop-Mods im Addon-Ordner sind unangetastet — wir packen nur `ai_*`-Prefix-Addons rein.

---

## Erlaubte Aktionen

- `git pull` / `git push` / `git commit`
- Dateien kopieren zwischen Repo und Workbench-Addon-Ordner
- Workbench starten (`Start-Process`)
- Log-Dateien lesen und Fehler extrahieren
- `tasks/PC_RESULT.md` schreiben

## VERBOTEN (heilig)

- Asset-IDs erfinden
- Mission-Inhalte ändern ohne Mac-Auftrag
- Stages überspringen
- Irgendwas in Production pushen

---

## Phase 2 — Deine Aufgaben

Wenn `tasks/PC_TASK.md` → `PHASE: 2`:

1. `git pull` → mission output files sind in `missions/{id}/output/`
2. Kopiere `missions/{id}/output/` → `%USERPROFILE%\Documents\my games\ArmaReforger\addons\ai_<mission>\`
3. Starte Workbench-Diag (siehe Test-CLI unten — bevorzugt headless `-wbSilent -exitAfterInit`)
4. Warte auf Workbench-Logs in `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\logs\logs_<TS>\console.log`
5. Extrahiere Errors/Warnings via Regex (`(WORLD|ENGINE|SCRIPT)\s+\((E|F)\):`)
6. Schreibe strukturierten Report in `tasks/PC_RESULT.md` (RELAY-Template)
7. Push

## Phase 3 — Deine Aufgaben

Wenn `tasks/PC_TASK.md` → `PHASE: 3`:

Wie Phase 2, aber zusätzlich: Mission im Game-Launcher testen, Screenshot wenn möglich, Spielbarkeits-Feedback in `tasks/PC_RESULT.md`.

---

## Erster Start

```
git pull
cat tasks/PC_TASK.md
```

Dann handle entsprechend.

---

## Polling-Loop (autonom — keine User-Nudges nötig)

Nach jedem `git push` deines Results: **Polle 30 Minuten lang im 60s-Takt**, ob neue Task da ist.

```powershell
$lastTaskId = "<die ID die du grad abgearbeitet hast>"
$maxMin = 30
$start = Get-Date

while (((Get-Date) - $start).TotalMinutes -lt $maxMin) {
    Start-Sleep -Seconds 60
    cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
    git pull --quiet
    $current = (Get-Content tasks\PC_TASK.md | Select-String "TASK_ID:" | Select-Object -First 1) -replace ".*TASK_ID:\s*", ""
    if ($current -ne $lastTaskId) {
        Write-Output "Neue Task: $current — starte Ausführung"
        break  # raus aus poll loop, weiter mit task ausführen
    }
}
```

Wenn 30min vorbei sind ohne neue Task: melden im Chat und ruhen, User kann manuell wecken.

---

## Test-CLI (siehe research/06-workbench-cli-flags.md)

Für autonome Mission-Validierung (USE THE DIAG EXE):

```powershell
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
```

- `$diag -gproj X -validate -logsDir Y` → Compile-Gate, Exit 0=ok, -1=fail
- `$diag -gproj X -load "$ai_<id>:Worlds/<id>.ent" -wbSilent -exitAfterInit -logsDir Y` → World-Load Smoke-Test
- Logs: `%USERPROFILE%\Documents\My Games\ArmaReforgerWorkbench\logs\logs_<TS>\console.log` (oder dein `-logsDir`-Override)
- Fatal-Pattern: `^(WORLD|ENGINE|SCRIPT)\s+\((E|F)\):`
- Success-Heuristic: ≥1 `Entities load`, ≥1 `Entity layer load`, 0 `(F):` Zeilen, Exit-Code 0

---

## Sub-Agent Fleet (autonomes Testing & Bug-Fix)

Du darfst SubAgents spawnen für:

| Marker | Sub-Agent | Wann |
|---|---|---|
| 🧪 **tester** | Test-Erzeuger + Runner | Bei neuer Mission: erzeugt Validierungstests, läuft sie |
| 🐛 **bug-fixer** | Error-Analyzer + Patch-Proposer | Bei `(E)` oder `(F)` in console.log: parst, schlägt Fix vor |
| 📊 **process-tracker** | Long-Running-Job-Monitor | Bei Steam-Install, Workbench-Headless-Loads → polled bis fertig, schreibt Status-JSON |
| 🔍 **auditor** | Coverage + Quality-Check | Vor jedem Push: verifiziert Result-Vollständigkeit, prüft Logs auf übersehene Errors |
| 📝 **logger** | Event-Capture + Aggregator | Während ALLEM: schreibt `logs/pc-events-<TS>.jsonl`, pusht periodisch |

Spawn-Muster: SubAgent bekommt einen klaren Auftrag + Output-File-Pfad. Es returns kurz, Mac liest den Output über git.

Vollständige Definitionen + Patterns: `playbook/RELAY_PROTOCOL.md` Sektion "Sub-Agent Fleet".

---

## Auto-Iteration (PC-side Loop)

Innerhalb eines Tasks darfst du autonom iterieren:

1. Führe EXEC-Block aus
2. Spawn `logger` Sub-Agent → captured Output
3. Wenn Error: spawn `bug-fixer` → bekommt Fix-Vorschlag
   - Wenn Fix nur auf PC-Side (z.B. retry, andere CLI-Args): wende an, retry max 3×
   - Wenn Fix Mission-Files ändern müsste (Mac-Side-Code): NICHT eigenmächtig fixen, sondern in Result-Template "New questions for Mac-side Claude" anhängen mit Vorschlag
4. Spawn `auditor` vor Push → prüft Vollständigkeit
5. Push wenn auditor durchgewunken

Iteration stoppt sofort wenn:
- 🧠 ANSWER von User nötig
- ⚙️ DO von User nötig
- Mission-Files müssen geändert werden (Mac-Designer-Territorium)
