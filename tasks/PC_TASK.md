# PC Task — Task 003: Headless Validation Loop (autonom)

STATUS: PENDING
TASK_ID: 003
PHASE: 2
TYPE: headless_validation + sub_agent_iteration + logging

## Kontext

Task 002 PARTIAL ok — Workbench-Diag installiert, 3 Missionen kopiert, Workbench-Launch
mit GUI hängt am Project-Selector. Wir wechseln auf **vollständig headless** mit `-validate`
und `-wbSilent -exitAfterInit`, parsen `console.log`, aggregieren Pass/Fail.

Diese Task ist die erste, die das volle Sub-Agent-Fleet + Logging nutzt (siehe
`playbook/RELAY_PROTOCOL.md` Sektion "Sub-Agent Fleet" und "Logging & Process Tracking").

---

## Pre-flight

```powershell
# Vorhandenen Workbench-Process schließen (PID aus Task 002)
$wb = Get-Process -Name "ArmaReforgerWorkbench*" -ErrorAction SilentlyContinue
if ($wb) {
    Write-Output "Schließe alten Workbench PID $($wb.Id)"
    $wb | Stop-Process -Force
    Start-Sleep -Seconds 3
}

# Paths (verified)
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
$addonsRoot = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons"
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
$logsBase = "$repo\logs"
New-Item -ItemType Directory -Path $logsBase -Force | Out-Null

# Sanity checks
Test-Path $diag                           # MUST be True
Test-Path $addonsRoot                     # MUST be True
Test-Path "$addonsRoot\ai_night-recon-everon\addon.gproj"  # MUST be True
```

Falls einer der Paths fehlt: STOP, melde im Result als Blocker.

---

## Schritt 1 — Spawn Logger (always-on für diese Task)

Erzeuge `logs/pc-events-task003-<TS>.jsonl` (append-only). Logge alle EXEC-Aufrufe,
Sub-Agent-Spawns, Process-Events. Format pro Zeile:

```json
{"t":"<ISO8601>","kind":"exec|spawn|status|result","agent":"main|tester|...","cmd":"...","exit":0,"duration_ms":X,"msg":"..."}
```

Schreibe Start-Event sofort. Halte File-Handle für den Rest der Task offen.

---

## Schritt 2 — Compile-Gate für alle 3 Missionen (parallel-fähig)

Für jede Mission läuft `-validate` (10s pro Mission):

```powershell
$missions = @("night-recon-everon", "day-assault-arland", "fog-ambush-eden")
$validateResults = @{}

foreach ($mission in $missions) {
    $addon = "$addonsRoot\ai_$mission"
    $gproj = "$addon\addon.gproj"
    $missionLogDir = "$logsBase\validate-$mission"
    New-Item -ItemType Directory -Path $missionLogDir -Force | Out-Null

    $startMs = (Get-Date).Ticks / 10000
    & $diag -gproj $gproj -validate -logsDir $missionLogDir 2>&1 | Out-File -FilePath "$missionLogDir\stdout.txt"
    $exitCode = $LASTEXITCODE
    $durMs = ((Get-Date).Ticks / 10000) - $startMs

    $validateResults[$mission] = @{
        exit_code = $exitCode
        passed = ($exitCode -eq 0)
        duration_ms = $durMs
        log_dir = $missionLogDir
    }

    # Log event
    Write-Output "[validate] $mission exit=$exitCode dur=${durMs}ms"
}
```

Pusht ein Status-Event ins logger nach jedem `-validate`-Call.

---

## Schritt 3 — World-Load Smoke-Test für alle 3 Missionen

Für jede Mission die ihr `-validate` bestanden hat:

```powershell
$smokeResults = @{}

foreach ($mission in $missions) {
    if (-not $validateResults[$mission].passed) {
        $smokeResults[$mission] = @{ skipped = $true; reason = "validate failed" }
        continue
    }

    $addon = "$addonsRoot\ai_$mission"
    $gproj = "$addon\addon.gproj"
    $worldRef = "`$ai_${mission}:Worlds/${mission}.ent"
    $missionLogDir = "$logsBase\smoke-$mission"
    New-Item -ItemType Directory -Path $missionLogDir -Force | Out-Null

    $startMs = (Get-Date).Ticks / 10000

    # Process-tracker pattern — non-blocking start + monitor
    $proc = Start-Process -FilePath $diag -ArgumentList @(
        "-gproj", "`"$gproj`"",
        "-load", "`"$worldRef`"",
        "-wbSilent",
        "-exitAfterInit",
        "-logsDir", "`"$missionLogDir`""
    ) -PassThru -NoNewWindow

    # Spawn process-tracker (poll every 5s, max 3 min for smoke-test)
    $maxSeconds = 180
    $waitStart = Get-Date
    while (-not $proc.HasExited -and ((Get-Date) - $waitStart).TotalSeconds -lt $maxSeconds) {
        Start-Sleep -Seconds 5
        Write-Output "[smoke-$mission] still running, $((Get-Date - $waitStart).TotalSeconds)s elapsed"
    }

    if (-not $proc.HasExited) {
        Write-Output "[smoke-$mission] TIMEOUT after ${maxSeconds}s — killing"
        Stop-Process -Id $proc.Id -Force
        Start-Sleep -Seconds 2
    }

    $durMs = ((Get-Date).Ticks / 10000) - $startMs

    # Parse log
    $consoleLog = Get-ChildItem "$missionLogDir\logs_*\console.log" -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Desc | Select-Object -First 1

    if ($consoleLog) {
        $content = Get-Content $consoleLog.FullName -Raw
        $hasEntitiesLoad = $content -match "WORLD\s+:\s+Entities load"
        $hasLayerLoad   = $content -match "WORLD\s+:\s+Entity layer load"
        $fatals         = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(F\):"))
        $errors         = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(E\):"))

        $passed = ($proc.ExitCode -eq 0) -and $hasEntitiesLoad -and $hasLayerLoad -and ($fatals.Count -eq 0)

        $smokeResults[$mission] = @{
            passed = $passed
            exit_code = $proc.ExitCode
            duration_ms = $durMs
            entities_load = $hasEntitiesLoad
            layer_load = $hasLayerLoad
            fatal_count = $fatals.Count
            error_count = $errors.Count
            console_log = $consoleLog.FullName
            log_size = $consoleLog.Length
        }
    } else {
        $smokeResults[$mission] = @{
            passed = $false
            exit_code = $proc.ExitCode
            duration_ms = $durMs
            reason = "no console.log found"
        }
    }

    Write-Output "[smoke-$mission] passed=$($smokeResults[$mission].passed)"
}
```

---

## Schritt 4 — Spawn `bug-fixer` Sub-Agent (falls Errors)

Wenn smokeResults oder validateResults für irgendeine Mission `(E)` oder `(F)` enthalten:

Spawn ein bug-fixer Sub-Agent mit:
- Input: die fehlgeschlagene Mission, console.log-Pfad, Error-Patterns aus Log
- Aufgabe: Patterns aus Log extrahieren, mögliche Ursache klassifizieren (Asset missing? Layer syntax? GUID stale?)
- Output: `logs/bugfix-task003-<TS>.json`

**WICHTIG:** bug-fixer darf NICHT Mission-Files ändern. Er schlägt nur vor. Mission-Files
werden von Mac-Designer geändert. Bug-fixer schreibt Vorschlag in `next_actions` Array.

---

## Schritt 5 — Spawn `auditor` Sub-Agent (Pre-Push, mandatory)

Auditor prüft:
- Sind alle 3 Missionen tracked? (validate + smoke result für jede)
- Sind alle console.log-Pfade in result-File referenced?
- Sind alle (E)/(F)-Events triaged (bug-fixer angesprungen)?
- Result-Schema valide (alle Pflichtfelder)?

Output: `logs/audit-task003-<TS>.json`.

Wenn auditor `status: "fail"` → STOP, melde Audit-Failure als Blocker im Result-Template, **nicht pushen**.

---

## Schritt 6 — Schreibe PC_RESULT.md im Return-Template-Format

Verwende EXAKT das Template aus Loop Turn #2 (siehe Chat). Schreibe strukturiert:

- Pre-flight outcomes
- Validate results pro Mission (Tabelle)
- Smoke-test results pro Mission (Tabelle)
- Bug-fixer summary (falls gespawnt)
- Auditor summary
- Log-File-Pfade (alle pushen!)

STATUS am Top:
- **OK** wenn alle 3 Missionen sowohl validate als auch smoke bestanden
- **PARTIAL** wenn 1-2 Missionen ok, andere failed
- **ERROR** wenn keine Mission durchgekommen oder Tooling kaputt
- **BLOCKED** wenn auditor blocked

---

## Schritt 7 — Logs + Result committen + pushen

```powershell
cd $repo
git pull --rebase
git add tasks/PC_RESULT.md logs/
git commit -m "PC: Task 003 — headless validation + smoke tests"
git push
```

---

## Schritt 8 — Polling-Loop für Task 004

Nach Push: polle 30 min im 60s-Takt auf TASK_ID-Änderung in tasks/PC_TASK.md
(siehe PC_AGENT_BRIEF Polling-Pattern). Wenn neue Task: ausführen. Wenn nicht: ruhen.

---

## Pause-Conditions in dieser Task

Stoppe sofort und melde als Blocker wenn:
- Workbench-Diag fehlt (Path-Sanity-Fail in Pre-flight)
- Steam-Update läuft / Tools werden gerade neu installiert
- Disk-full
- Permission-Popup, das du nicht selbst grant'en kannst (auch nach Allow-always)
- Auditor explicit blocked

In allen anderen Fällen: bug-fixer übernimmt, iteriere autonom.

---

## Erwartete Dauer

- Validate × 3: ~30s
- Smoke × 3: ~3-9 min (1-3 min pro Mission)
- Logging + Audit: ~30s

Total: 4-10 min. Keine PAUSE-FLAG nötig — das geht durch ohne menschliche Klicks.
