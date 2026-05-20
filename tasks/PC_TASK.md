# PC Task — Task 006: GUI Smoke-Test mit Auto-Screenshot + Multimodal Verify

STATUS: PENDING
TASK_ID: 006
TURN_ID: 5
PHASE: 2-3 (Smoke-Bridge)
TYPE: gui_smoke_test + multimodal_ui_verify + dry_pattern_intro

## Kontext

Task 005 lieferte den grossen Win: **3/3 Validate PASS** (commit 6cf9b9a). Smoke-Test
mit `-wbSilent -exitAfterInit -load X.ent` schlug fehl — research/06 Section B ist
empirisch disconfirmed.

Mac hat entschieden (Loop Turn #5):
- ✅ Smoke-Alternative **Option (b) GUI + Auto-Screenshot** (Plugin ist nur Skeleton, Linux-Dedi braucht extra Setup)
- ✅ research/06 Section B mit DISCONFIRMED-Label gepatcht
- ✅ pc-setup.ps1 Line 49 quoting bug gefixt (Mac commit incoming)
- ✅ 🧪 DRY marker als Safety-Pattern für destructive Ops ab dieser Task aktiv
- ✅ Du darfst (sollst) auf Sonnet 4.6 switchen — Protocol funktioniert identisch

## Phase A (Two-Phase Reception)

⚙️ DO Items: **EINS** — du selbst (PC-Side) entscheidest beim Modell-Switch:
- Im Claude-Code-App-Modell-Selector auf Sonnet 4.6 wechseln (optional, kostenoptimiert)
- ODER auf Opus 4.7 bleiben (sicherer aber teurer)

Wenn du diesen Block bekommst, sag User: "Möchtest du jetzt auf Sonnet 4.6 switchen
(empfohlen, 70% billiger), oder Opus 4.7 weiter?"

Egal welche Wahl: Phase C kann beides ausführen.

## Phase C — Steps

### Step 1 — STATE.json + Logger + Reflection

```powershell
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
cd $repo
git pull --rebase

if (Test-Path "logs\reflection-turn-4.md") {
    Write-Output "=== Reading turn-4 reflection (PC own) ==="
    Get-Content "logs\reflection-turn-4.md"
}

# STATE.json update
$state = @{
    turn_id = 5
    owner = "pc"
    phase = "PHASE_C_EXEC"
    started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    pending_do = @()
    pending_exec = @(
        @{ id="exec-1"; desc="Verify pc-setup.ps1 fix (re-run idempotent)"; status="queued" }
        @{ id="exec-2"; desc="🧪 DRY plan for addon re-copy (cleanup + recopy)"; status="queued" }
        @{ id="exec-3"; desc="Approve DRY → execute cleanup + recopy"; status="queued" }
        @{ id="exec-4"; desc="GUI Workbench launch (no -wbSilent) for night-recon-everon"; status="queued" }
        @{ id="exec-5"; desc="Screenshot at +60s, +90s, +120s"; status="queued" }
        @{ id="exec-6"; desc="ui-tester sub-agent classify screenshots"; status="queued" }
        @{ id="exec-7"; desc="Repeat 4-6 für day-assault, fog-ambush"; status="queued" }
        @{ id="exec-8"; desc="Auditor + reflection + push"; status="queued" }
    )
    loop_signals = @()
} | ConvertTo-Json -Depth 5
$state | Set-Content "tasks\STATE.json" -Encoding UTF8

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "logs\pc-events-task006-$ts.jsonl"
"{`"t`":`"$((Get-Date -Format 's')+'Z')`",`"kind`":`"start`",`"turn_id`":5,`"task_id`":`"006`"}" | Add-Content $logFile
```

### Step 2 — Verify pc-setup.ps1 fix

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\scripts\pc-setup.ps1"
```

Sollte `[skip]` für beide Junctions melden + "Done." am Ende — **ohne Parse-Error diesmal**.

Capture full output in Result.

### Step 3 — 🧪 DRY Marker: Plan addon-cleanup + recopy

**NEU in Task 006**: vor destructive Ops emittierst du erst einen DRY-Plan mit Hash.

```powershell
# 1. Compute DRY plan
$addonsRoot = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons"
$missions = @("night-recon-everon","day-assault-arland","fog-ambush-eden")

$dryPlan = @()
foreach ($mission in $missions) {
    $target = "$addonsRoot\ai_$mission"
    $src = "$repo\missions\$mission\output"
    $action = if (Test-Path $target) { "REMOVE then COPY" } else { "COPY" }
    $dryPlan += [PSCustomObject]@{
        mission = $mission
        target = $target
        src = $src
        action = $action
        files_to_delete = (Get-ChildItem -Path $target -Recurse -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count)
        files_to_copy = (Get-ChildItem -Path $src -Recurse | Measure-Object).Count
    }
}

# 2. Hash the plan
$planJson = $dryPlan | ConvertTo-Json -Depth 3
$planHash = (Get-FileHash -InputStream ([IO.MemoryStream]::new([Text.Encoding]::UTF8.GetBytes($planJson))) -Algorithm SHA256).Hash.Substring(0,16)

Write-Output "🧪 DRY PLAN (hash: $planHash):"
$dryPlan | Format-Table

# 3. Save plan + hash for evidence
$planJson | Set-Content "$repo\logs\dry-plan-task006-$ts.json"
"hash: $planHash" | Add-Content "$repo\logs\dry-plan-task006-$ts.json"
```

### Step 4 — DRY Approve + Execute cleanup + recopy

```powershell
# Self-approve (no Mission-File-Changes, only addon-folder-cleanup which IS reversible
# via re-copy from missions/<id>/output)
Write-Output "DRY plan hash $planHash — self-approved (cleanup is reversible)"

foreach ($plan in $dryPlan) {
    if ($plan.action -eq "REMOVE then COPY") {
        Remove-Item -Path $plan.target -Recurse -Force
    }
    Copy-Item -Path $plan.src -Destination $plan.target -Recurse -Force
    Write-Output "[$($plan.mission)] $($plan.action): done"
}
```

Schreib in PC_RESULT.md unter `### DRY Pattern Demo` die Erfahrung damit. Wenn das Pattern
funktioniert, übernehmen wir es für künftige destructive Ops.

### Step 5 — GUI Workbench Launch (one mission at a time)

```powershell
function Test-MissionGUI {
    param([string]$Mission, [string]$Repo, [string]$AddonsRoot)

    $diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
    $addon = "$AddonsRoot\ai_$Mission"
    $gproj = "$addon\addon.gproj"
    $worldRef = "`$ai_${Mission}:Worlds/${Mission}.ent"
    $missionLogDir = "$Repo\logs\gui-smoke-$Mission"
    New-Item -ItemType Directory -Path $missionLogDir -Force | Out-Null

    # Launch WITHOUT -wbSilent (GUI mode) + WITH -load (try auto-load)
    $proc = Start-Process -FilePath $diag -ArgumentList @(
        "-gproj", "`"$gproj`"",
        "-load", "`"$worldRef`"",
        "-logsDir", "`"$missionLogDir`""
    ) -PassThru

    # Take screenshots at 60s, 90s, 120s
    $screenshots = @()
    foreach ($wait in @(60, 90, 120)) {
        Start-Sleep -Seconds 30  # 30s each (60, 90, 120 cumulative)
        $shotPath = "$missionLogDir\screenshot-$wait-sec.png"
        Take-Screenshot -OutPath $shotPath
        $screenshots += $shotPath

        # Check if process still alive
        $alive = -not $proc.HasExited
        Write-Output "[$Mission @ ${wait}s] Process alive: $alive · Screenshot: $shotPath"
    }

    # Get window info
    $windows = Get-VisibleWindows | Where-Object { $_.ProcessName -like "*Workbench*" -or $_.ProcessName -like "*ArmaReforger*" }

    # Try to close Workbench gracefully
    if (-not $proc.HasExited) {
        $proc | Stop-Process -Force
        Start-Sleep -Seconds 2
    }

    return @{
        mission = $Mission
        screenshots = $screenshots
        windows = $windows
        process_alive_at_120s = ($alive)
        log_dir = $missionLogDir
    }
}

# Screenshot helper (already in PC_AGENT_BRIEF)
function Take-Screenshot {
    param([string]$OutPath)
    Add-Type -AssemblyName System.Windows.Forms,System.Drawing
    $bounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
    $gfx = [Drawing.Graphics]::FromImage($bmp)
    $gfx.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
    $bmp.Save($OutPath, [Drawing.Imaging.ImageFormat]::Png)
    $gfx.Dispose(); $bmp.Dispose()
}

function Get-VisibleWindows {
    Get-Process | Where-Object {
        $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne ""
    } | Select-Object Id, ProcessName, MainWindowTitle, Responding
}

$guiResults = @{}
foreach ($mission in @("night-recon-everon","day-assault-arland","fog-ambush-eden")) {
    $guiResults[$mission] = Test-MissionGUI -Mission $mission -Repo $repo -AddonsRoot $addonsRoot
    Start-Sleep -Seconds 5  # spacing between missions
}
```

### Step 6 — Spawn ui-tester Sub-Agent für jeden Screenshot

Für jedes Screenshot-Set (3 Screenshots × 3 Missions = 9 PNGs):

Spawn `ui-tester` Sub-Agent mit:
- Input: screenshot PNG path
- Aufgabe: multimodal-vision-classify
  - `mission_loaded`: Karte mit Entitäten sichtbar, Mission-Name im Title
  - `project_selector`: Workbench zeigt Project-Selection-Dialog
  - `error_popup`: Error-Dialog im Vordergrund (extract OCR-text)
  - `loading`: Splash/Loading-Screen
  - `crashed`: Window weg, Process exited
  - `unknown`: nichts davon

Output pro Screenshot: `logs/ui-task006-<mission>-<ts>-<seconds>s.json` mit
`{classification, confidence, extracted_text, suggested_next_action}`.

### Step 7 — Wenn `mission_loaded` ≥1 Screenshot pro Mission: PASS

Aggregation:

```powershell
$smokeVerdict = @{}
foreach ($mission in @("night-recon-everon","day-assault-arland","fog-ambush-eden")) {
    $shotResults = Get-ChildItem "$repo\logs" -Filter "ui-task006-$mission-*.json" | ForEach-Object {
        Get-Content $_.FullName | ConvertFrom-Json
    }

    $hasLoaded = $shotResults | Where-Object { $_.classification -eq "mission_loaded" }
    $hasError = $shotResults | Where-Object { $_.classification -eq "error_popup" }
    $hasCrash = $shotResults | Where-Object { $_.classification -eq "crashed" }

    if ($hasLoaded) {
        $smokeVerdict[$mission] = "PASS"
    } elseif ($hasCrash -or $hasError) {
        $smokeVerdict[$mission] = "FAIL"
    } else {
        $smokeVerdict[$mission] = "UNKNOWN"  # still loading or project selector visible
    }
}
$smokeVerdict | ConvertTo-Json | Out-File "$repo\logs\gui-smoke-verdict-task006.json"
```

### Step 8 — Bug-fixer wenn FAIL oder UNKNOWN

Falls Status nicht PASS für ≥1 Mission:

Spawn bug-fixer mit:
- Input: alle ui-task006 JSONs für betroffene Mission + screenshots
- Aufgabe: was zeigt der Screenshot? Liegt Mission an Project-Selector? Crash? Specific Error?
- Output: `logs/bugfix-task006-<ts>.json` mit Vorschlag

bug-fixer ändert KEINE Mission-Files. Vorschläge gehen an Mac.

### Step 9 — Auditor + Reflection

Auditor verifies:
- DRY plan recorded + hash matches
- Alle 9 Screenshots in logs/
- Alle 9 ui-tester JSONs vorhanden
- ≥1 von 3 Missions mit mission_loaded ODER explicit bug-fixer-Vorschlag

Reflection-turn-5.md schreiben (PC-side).

### Step 10 — Push

```powershell
cd $repo
$state = Get-Content "tasks\STATE.json" -Raw | ConvertFrom-Json
$state.phase = "PHASE_D_RETURN"
$state | ConvertTo-Json -Depth 5 | Set-Content "tasks\STATE.json" -Encoding UTF8

git pull --rebase
git add tasks/PC_RESULT.md tasks/STATE.json logs/
git commit -m "PC: Task 006 -- GUI smoke + DRY marker demo"
git push
```

---

## Pause-Conditions

- DRY plan hash invalid / verändert sich zwischen plan und exec → STOP (race condition)
- Workbench-Diag crasht in 5s mit (F) → STOP, bug-fixer
- ui-tester verweigert Klassifikation (confidence <0.5 für alle Screenshots) → bug-fixer
- 3+ Missions mit error_popup → STOP, ⚙️ DO an User
- turn_time_budget (30 min) → STOP

---

## Erwartete Dauer

- Steps 0-4: ~30s
- Step 5 (3 missions × ~135s GUI launch + 5s spacing): ~7 min
- Step 6 (ui-tester × 9): ~3 min
- Steps 7-10: ~1 min

Total: ~12-15 min. PAUSE FLAG: nein.

---

## Ergänzende Notes (Sonnet-fähig)

Wenn du auf Sonnet 4.6 switched bist (nach Phase A): nichts ändert sich an Steps oder Sub-Agents.
Dein Reasoning für bug-fixer Vorschläge in Step 8 könnte etwas weniger kreativ sein als bei Opus —
das ist OK. Escaliere die "welche Smoke-Alternative langfristig" Mac-Side-Entscheidungen wie immer
via "New questions for Mac-side Claude".
