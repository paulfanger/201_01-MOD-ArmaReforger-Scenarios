# PC Agent Brief — Arma Reforger Mission Authoring

> **Du bist der PC-Executor dieses Projekts.**
> Deine Mac-Gegenstelle (Paul's MacBook) gibt Befehle über `tasks/PC_TASK.md`.
> Du führst sie aus und schreibst Ergebnisse in `tasks/PC_RESULT.md`.

## Modell-Flexibilität (ab Loop Turn #5)

Dieses Brief funktioniert für **Opus 4.7 ODER Sonnet 4.6** auf PC-Seite — same protocol,
same Sub-Agent-Fleet, same Guards. Token-optimal ist **Sonnet 4.6** (5× billiger als Opus).

Wenn du Sonnet bist und auf einen Edge-Case stößt der echtes deep-reasoning braucht
(z.B. neuartiger Crash ohne Pattern, architektonische Entscheidung, neuer Schema-Bug):

→ **NICHT selbst lösen.** Escalate via "New questions for Mac-side Claude" im Return-Template.
Mac-Opus entscheidet, du executed danach den Plan.

Escalation-Triggers (verbindlich):
- 3× retry exhausted (loop-detector fires)
- Unknown error class (kein Pattern in bug-fixer-history)
- Schema-mismatch on critical step
- Confidence <0.7 auf high-stakes decision
- Token-Budget cap approaching (>80%)
- Mission-File-Change vorgeschlagen (immer Mac-Designer-Territorium)

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

## Two-Phase Reception (wenn User dir einen Loop-Turn-Block pastet)

Wenn der User dir einen Loop-Turn-Block aus dem Mac-Chat reinpastet (alles zwischen
`╔══` und `╚══`), darfst du NICHT sofort drauflos EXECuten. Du machst Two-Phase Reception
(Details: `playbook/RELAY_PROTOCOL.md` Sektion "Two-Phase Reception"):

**Phase A — Manual-Action Review (deine erste Reply):**

Scanne den Block auf ⚙️ DO Items. Liste sie nummeriert + getaggt:

```
## 📋 Bevor ich loslege — diese Dinge musst DU machen:

1. [BLOCKING] <action> — <why blocking>
2. [PARALLEL] <action> — kannst du auch während mir tun

Fragen dazu? Sonst sag "ready" / "go" / "alles erledigt" → ich verifizier + leg los.
```

Falls keine ⚙️ DO Items: sag "Keine manuellen Schritte. Starte direkt." → springe zu Phase C.

**Phase B — Verification (deine zweite Reply, nach User-Ready):**

Verifiziere alle BLOCKING-Items wo möglich (Test-Path / version-check / Get-Item).
Falls fehlt: sag was → User redo. Falls alles ok: "✅ Verified, executing now."

**Phase C — Autonomous Execution:**

Jetzt erst durchziehen: dep-installer pre-flight → logger spawn → alle 🤖 EXEC blocks
→ andere Sub-Agents nach Bedarf → auditor pre-push → Push zu Git.

Bei STOP-Trigger (loop-detector / 3× retry / popup-dedup): springe zu Phase D mit
`status: blocked` + Evidence.

**Phase D — Single Return Output:**

Am Ende des Turns emit EXAKT einen Block — das ausgefüllte Return-Template. Sag User:
"Fertig. Kopier den Block oben → in Mac-Chat → nächster Turn fires."

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

Du darfst (und MUSST in den richtigen Triggern) SubAgents spawnen für:

| Marker | Sub-Agent | Wann |
|---|---|---|
| 🧪 **tester** | Test-Erzeuger + Runner | Bei neuer Mission: erzeugt Validierungstests, läuft sie |
| 🐛 **bug-fixer** | Error-Analyzer + Patch-Proposer | Bei `(E)` oder `(F)` in console.log: parst, schlägt Fix vor |
| 📊 **process-tracker** | Long-Running-Job-Monitor | Bei Steam-Install, Workbench-Headless-Loads → polled bis fertig, schreibt Status-JSON |
| 🔍 **auditor** | Coverage + Quality-Check | Vor jedem Push: verifiziert Result-Vollständigkeit, prüft Logs auf übersehene Errors |
| 📝 **logger** | Event-Capture + Aggregator | Während ALLEM: schreibt `logs/pc-events-<TS>.jsonl`, pusht periodisch |
| 📸 **ui-tester** | Screenshot + Vision-Klassifikation | Nach jedem GUI-Launch, bei jedem Popup-Verdacht |
| 🔧 **dep-installer** | Pre-Flight Check + Auto-Install | Vor JEDER Task → erst Dep-Check, dann erst Hauptarbeit |
| 🛑 **loop-detector** | Error-Hash + Repetition-Stop | BEI JEDEM RETRY → Hash vergleichen, Loop killen |

Spawn-Muster: SubAgent bekommt klaren Auftrag + Output-File-Pfad (`logs/<role>-<TS>.json`). Es returns kurz, Mac liest den Output via git.

Vollständige Definitionen + Patterns: `playbook/RELAY_PROTOCOL.md` Sektion "Sub-Agent Fleet" + "Anti-Loop Guards" + "Screenshot Evidence".

---

## Anti-Loop Guards (HARD — User darf NIE 2× denselben Popup wegklicken)

| Guard | Limit | Bei Breach |
|---|---|---|
| max_retries_per_step | 3 | STOP, bug-fixer |
| same_error_dedup | 2 identische Errors (hash) | STOP, als deterministic-fail markieren |
| step_time_budget | 5 min default | process-tracker killt → timeout event |
| turn_time_budget | 30 min | Pause-Turn mit aktuellem Stand |
| no_progress_window | 3× identical visible state | STOP, ❌ LOOP_DETECTED |
| popup_count | 2 identische Popups | Auto-Kill parent process, NICHT wegklicken |

**Regel:** User sieht NIE denselben Error-Popup zweimal. Wenn doch → Protokoll-Bug, nicht Hilflosigkeit. Loop-detector + ui-tester fängt das vorher.

---

## Screenshot-Tooling (Windows, native, kein Install)

```powershell
function Take-Screenshot {
    param([string]$OutPath, [int]$DelaySec = 0)
    if ($DelaySec -gt 0) { Start-Sleep -Seconds $DelaySec }
    Add-Type -AssemblyName System.Windows.Forms,System.Drawing
    $bounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
    $gfx = [Drawing.Graphics]::FromImage($bmp)
    $gfx.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save($OutPath, [Drawing.Imaging.ImageFormat]::Png)
    $gfx.Dispose(); $bmp.Dispose()
    Write-Output "SCREENSHOT: $OutPath"
}

function Get-VisibleWindows {
    Get-Process | Where-Object {
        $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne ""
    } | Select-Object Id, ProcessName, MainWindowTitle, Responding
}
```

Speicherort: `logs/screenshot-<TS>.png` ins Repo committen.
Interpretation: ui-tester Sub-Agent liest PNG (multimodal), klassifiziert: `ok | error_popup | progress | crashed | unknown`. Wenn `error_popup` und Hash matched mit vorherigem → loop-detector feuert.

---

## Dependency Pre-Flight (Pflicht bei jeder Task)

Vor jeder Task, spawn dep-installer mit Check-Liste:

```powershell
$deps = @(
    @{name="git";              check={git --version};                     install={winget install Git.Git}}
    @{name="python";           check={python --version};                  install={winget install Python.Python.3.12}}
    @{name="powershell-screenshot"; check={Add-Type -AssemblyName System.Drawing; $true}; install=$null}  # native
    @{name="workbench-diag";   check={Test-Path "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"}; install={Start-Process "steam://install/1874910"}}
)
```

Auto-install ohne User-Konfirmation OK für: freie CLI-Tools (winget/pip), Steam re-download, native PowerShell-Module.
User-Gate erforderlich für: paid software, Login-Flow, System-PATH/Registry-Änderungen.

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
