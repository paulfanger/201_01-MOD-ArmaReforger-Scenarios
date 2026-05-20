# PC Task — Task 004: Loop-Debrief + Hardened Validation Run

STATUS: PENDING
TASK_ID: 004
PHASE: 2
TYPE: debrief + dep_install + screenshot_setup + hardened_validation

## Kontext

User berichtete in Loop Turn #3: Endless-Loop von Error-Popups während Task 003.
User musste manuell Buttons klicken — das ist **ein Protokoll-Bug**, nicht User-Problem.

Diese Task:
1. **Debrief Task 003**: was ist passiert, mit Screenshots & Logs als Evidence
2. **STOP alle hängenden Workbench/Diag-Prozesse**
3. **Dep-Install**: Screenshot-Funktion + Window-Enum aktivieren + alle Tools verifizieren
4. **Hardened Validation**: gleicher Test wie Task 003, aber mit ALLEN Guards aktiv

Alle Guards (siehe PC_AGENT_BRIEF.md "Anti-Loop Guards" + RELAY_PROTOCOL.md) MÜSSEN aktiv sein.

---

## Schritt 0 — STOP everything (sofort)

```powershell
# Kill alle Workbench/Diag-Prozesse, auch hängende
Get-Process | Where-Object { $_.ProcessName -like "*Workbench*" -or $_.ProcessName -like "*ArmaReforger*Diag*" } | ForEach-Object {
    Write-Output "Killing PID $($_.Id) ($($_.ProcessName))"
    Stop-Process -Id $_.Id -Force
}
Start-Sleep -Seconds 3

# Verify clean state
Get-Process | Where-Object { $_.ProcessName -like "*Workbench*" } | ForEach-Object {
    Write-Output "STILL RUNNING: $($_.Id) $($_.ProcessName)"
}
```

Schreib Output in PC_RESULT.md unter `### Step 0 — Cleanup`.

---

## Schritt 1 — Logger spawn (always-on)

Erzeuge `logs/pc-events-task004-<TS>.jsonl`. Append-only. Log ALLE EXEC + Spawn + Status-Events.

---

## Schritt 2 — Task 003 Debrief (was ist passiert?)

Sammle Evidence:

```powershell
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
cd $repo

# Vorhandene Task-003-Logs auflisten
Get-ChildItem "$repo\logs" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.LastWriteTime -gt (Get-Date).AddHours(-3)
} | Select-Object FullName, Length, LastWriteTime | Format-Table

# Workbench-Logs aus dem letzten Run
$wbLogs = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\logs"
if (Test-Path $wbLogs) {
    Write-Output "=== Letzte 3 Workbench-Log-Folders ==="
    Get-ChildItem $wbLogs -Directory | Sort-Object LastWriteTime -Desc | Select-Object -First 3 | ForEach-Object {
        Write-Output "Folder: $($_.FullName) — $($_.LastWriteTime)"
        $console = Join-Path $_.FullName "console.log"
        if (Test-Path $console) {
            Write-Output "--- $($_.Name)/console.log (last 50 lines) ---"
            Get-Content $console -Tail 50
        }
    }
}

# Existierende Screenshots vom User (falls da)
if (Test-Path "$repo\evidence") {
    Get-ChildItem "$repo\evidence" -ErrorAction SilentlyContinue
}
```

Falls User Screenshots in `evidence/` ablegt (von seinen manuellen Wegklicks), die im Result referenzieren.

Schreib in PC_RESULT.md unter `### Task 003 Debrief`:
- Was wurde versucht?
- Welche Errors kamen?
- Wie viele Iterationen / Popups bevor User abbrach?
- Welche Workbench-Logs sind vorhanden?
- Welche Hypothese für die Loop-Ursache?

---

## Schritt 3 — Dep-Installer Sub-Agent

Spawn dep-installer mit folgender Liste:

```powershell
$deps = @(
    @{name="git";       check={(git --version) -match "git version"};                ok=$null; install=$null}
    @{name="powershell-screenshot"; check={
        try { Add-Type -AssemblyName System.Windows.Forms,System.Drawing -ErrorAction Stop; $true }
        catch { $false }
    }; install=$null}  # native
    @{name="workbench-diag"; check={
        Test-Path "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
    }; install={Start-Process "steam://install/1874910"}}
    @{name="python";    check={ try { (python --version) -match "Python 3"; } catch { $false } };
                        install={winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements}}
    @{name="pillow";    check={ try { (python -c "import PIL; print(PIL.__version__)") -match "\d"; } catch { $false } };
                        install={python -m pip install --user pillow}}
)

$depResults = @()
foreach ($d in $deps) {
    $result = & $d.check
    if (-not $result -and $d.install) {
        Write-Output "[dep-installer] Installing $($d.name)..."
        & $d.install
        Start-Sleep -Seconds 5
        $result = & $d.check
    }
    $depResults += [PSCustomObject]@{Name=$d.name; Available=$result}
}

$depResults | ConvertTo-Json | Out-File "$repo\logs\deps-task004-$(Get-Date -Format 'yyyyMMddHHmmss').json"
$depResults | Format-Table
```

Schreib in PC_RESULT.md unter `### Dep-Install`: Tabelle aller Deps + ob installiert.

**WICHTIG:** Falls eine Auto-Install läuft (Python winget), spawn process-tracker für sie. Nicht blockieren!

---

## Schritt 4 — Screenshot-Funktion verifizieren

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
    return Test-Path $OutPath
}

$testShot = "$repo\logs\screenshot-test-$(Get-Date -Format 'yyyyMMddHHmmss').png"
$ok = Take-Screenshot -OutPath $testShot
Write-Output "Screenshot test: $ok — $testShot"
```

Falls Screenshot-Capability funktioniert: spawn ui-tester Sub-Agent mit dem Test-PNG, der das Bild beschreibt (Sanity-Check der Vision-Pipeline).

Schreib in PC_RESULT.md unter `### Screenshot Capability`: ok + Test-PNG-Pfad + ui-tester-Description.

---

## Schritt 5 — Hardened Headless Validation (mit ALLEN Guards)

Jetzt der eigentliche Test — aber DIESMAL mit Guards.

```powershell
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
$addonsRoot = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons"
$missions = @("night-recon-everon", "day-assault-arland", "fog-ambush-eden")

$results = @{}

foreach ($mission in $missions) {
    $stepId = "validate-$mission"
    $iter = 0
    $maxIter = 3
    $stepBudgetSec = 60  # -validate sollte schnell sein
    $errorHashes = @()

    while ($iter -lt $maxIter) {
        $iter++
        $iterStart = Get-Date
        $addon = "$addonsRoot\ai_$mission"
        $gproj = "$addon\addon.gproj"
        $logDir = "$repo\logs\$stepId-iter$iter"
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null

        # Take screenshot BEFORE
        Take-Screenshot -OutPath "$logDir\before.png" | Out-Null

        # Run with time budget
        $proc = Start-Process -FilePath $diag -ArgumentList @(
            "-gproj", "`"$gproj`"",
            "-validate",
            "-logsDir", "`"$logDir`""
        ) -PassThru -NoNewWindow

        # process-tracker: poll with budget
        $waitSec = 0
        while (-not $proc.HasExited -and $waitSec -lt $stepBudgetSec) {
            Start-Sleep -Seconds 2
            $waitSec += 2
        }

        if (-not $proc.HasExited) {
            Write-Output "[$stepId iter$iter] TIMEOUT after ${stepBudgetSec}s"
            Take-Screenshot -OutPath "$logDir\timeout.png" | Out-Null
            Stop-Process -Id $proc.Id -Force
            $exitCode = -999  # timeout marker
        } else {
            $exitCode = $proc.ExitCode
        }

        # Take screenshot AFTER
        Take-Screenshot -OutPath "$logDir\after.png" | Out-Null

        # Check for popups via window enum
        $popups = Get-Process | Where-Object {
            $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne "" -and
            ($_.ProcessName -like "*Workbench*" -or $_.MainWindowTitle -match "Error|Warning|Critical")
        }

        # Error hash (combines exit code + log content + popup titles)
        $logFiles = Get-ChildItem "$logDir\logs_*\console.log" -Recurse -ErrorAction SilentlyContinue
        $logContent = if ($logFiles) { Get-Content $logFiles[0].FullName -Raw } else { "" }
        $errorPattern = ($logContent | Select-String -Pattern "^(WORLD|ENGINE|SCRIPT)\s+\((E|F)\):" -AllMatches).Matches | ForEach-Object { $_.Value } | Sort-Object -Unique
        $popupTitles = ($popups | ForEach-Object { $_.MainWindowTitle }) -join "|"

        $errorHash = ((($exitCode.ToString() + "|" + ($errorPattern -join ",") + "|" + $popupTitles) | ForEach-Object {
            [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($_))
        }) | ForEach-Object { [BitConverter]::ToString($_).Replace("-","") }) -join ""

        $errorHashes += $errorHash

        # LOOP DETECTOR: same error hash 2× → STOP
        $duplicates = $errorHashes | Group-Object | Where-Object { $_.Count -ge 2 }
        if ($duplicates) {
            Write-Output "[$stepId] ❌ LOOP_DETECTED — same error hash $iter× — STOPPING"

            # Kill remaining processes
            $popups | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }

            $results[$mission] = @{
                status = "LOOP_DETECTED"
                iterations = $iter
                exit_code = $exitCode
                error_hash = $errorHash
                screenshots = @("$logDir\after.png")
                log_files = $logFiles | ForEach-Object { $_.FullName }
                popups_seen = $popupTitles
                action_taken = "Killed processes; escalating to Mac-side via blocker"
            }
            break  # raus aus while
        }

        # Success check
        $passed = ($exitCode -eq 0)
        if ($passed) {
            $results[$mission] = @{
                status = "PASS"
                iterations = $iter
                exit_code = 0
                screenshots = @("$logDir\after.png")
                log_dir = $logDir
            }
            break  # raus aus while, weiter mit nächster Mission
        }

        # Fail (not loop yet) — bug-fixer would be spawned here in next iter
        if ($iter -lt $maxIter) {
            Write-Output "[$stepId] iter$iter failed (exit=$exitCode), retrying..."
            Start-Sleep -Seconds 5
        } else {
            $results[$mission] = @{
                status = "FAIL_MAX_RETRIES"
                iterations = $iter
                exit_code = $exitCode
                error_hash = $errorHash
                screenshots = @("$logDir\after.png")
                log_files = $logFiles | ForEach-Object { $_.FullName }
            }
        }
    }
}

# Persist
$results | ConvertTo-Json -Depth 5 | Out-File "$repo\logs\validate-results-task004.json"
$results.GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value.status)" }
```

Schreib in PC_RESULT.md unter `### Hardened Validate Results`: Tabelle pro Mission, Status, iterations, alle Screenshot-Pfade.

---

## Schritt 6 — Wenn alle 3 Missions PASS: Smoke-Test (same Guards)

Falls Step 5 für mind. eine Mission `PASS` ergab: gleicher Pattern mit `-wbSilent -exitAfterInit -load "$ai_<id>:Worlds/<id>.ent"` für jede passed Mission.

Skip wenn alle FAIL — dann ist Mission-Code-Issue, kein Workbench-Issue.

---

## Schritt 7 — Auditor Sub-Agent pre-push

Auditor prüft:
- Sind alle Screenshots referenced + im repo?
- Wurde loop-detector aktiviert wo nötig?
- Sind alle Step-Outputs strukturiert in PC_RESULT.md?
- Falls LOOP_DETECTED: ist bug-fixer-Vorschlag im Result?

Output: `logs/audit-task004-<TS>.json`.

Falls Audit blockt → PUSH NICHT, melde Blocker.

---

## Schritt 8 — Commit + Push (mit screenshots)

```powershell
cd $repo
git pull --rebase
git add tasks/PC_RESULT.md logs/
git commit -m "PC: Task 004 — debrief + hardened validation (with guards)"
git push
```

---

## Pause-Conditions (HARD STOP, sofort melden im Result)

- LOOP_DETECTED in irgendeiner Mission → STOP, escalate
- Steam-Tools fehlen nach dep-install → STOP, ⚙️ DO an User
- Workbench crasht <5s nach Start → STOP, bug-fixer im Result
- Screenshot-Capability funktioniert nicht → STOP, ⚙️ DO an User
- turn_time_budget (30 min) erreicht → STOP, was-bisher-erreicht im Result

---

## Erwartete Dauer

- Step 0-2 (Cleanup + Debrief): 1 min
- Step 3 (Dep-Install, falls Python fehlt): 2-5 min
- Step 4 (Screenshot test): <30s
- Step 5 (Hardened Validate): ~30s pro Mission × 3 = ~2 min (oder schneller fail, falls bug)
- Step 6 (Smoke, conditional): 1-3 min pro Mission
- Step 7-8 (Audit + Push): 1 min

Total: 5-12 min. PAUSE-FLAG: nein, sollte komplett durchlaufen.
