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

## Workbench-Pfade (Windows)

```
Addon-Ziel:    C:\Users\pfofa\AppData\Local\Bohemia Interactive\ArmaReforger\addons\
Workbench-Exe: C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe
Projekt-Repo:  C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios\
```

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
2. Kopiere `missions/{id}/output/` → Workbench Addon-Ordner
3. Starte Workbench
4. Warte auf Workbench-Logs in `%LOCALAPPDATA%\Bohemia Interactive\ArmaReforger\logs\`
5. Extrahiere Errors/Warnings aus Log
6. Schreibe Report in `tasks/PC_RESULT.md`
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

Für autonome Mission-Validierung:
- `-validate` → Exit code 0=ok, -1=compile fail
- `-wbSilent -exitAfterInit -gproj X -load Y` → world-load smoke test
- Logs: `%USERPROFILE%\Documents\My Games\ArmaReforgerWorkbench\logs\logs_<TS>\console.log`
- Fatal-Pattern: `^(WORLD|ENGINE|SCRIPT)\s+\((E|F)\):`
- Success-Heuristic: ≥1 `Entities load`, ≥1 `Entity layer load`, 0 `(F):` Zeilen, Exit-Code 0
