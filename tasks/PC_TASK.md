# PC Task — Task 006-CS: Headless-Only DRY-Demo + Re-Validate (CS-kompatibel)

STATUS: PENDING
TASK_ID: 006-CS
TURN_ID: 5
PHASE: 2
TYPE: headless_verification + dry_pattern_demo + revalidate
NOTE: User spielt parallel Counter-Strike. KEINE GUI-Launches in dieser Task.
      GUI Smoke wurde in Task 007 (post-CS) verlegt.

## Kontext

Mac hat Smoke-Alternative (b) GUI+Screenshot gewählt + pc-setup.ps1 quoting bug gefixt
+ research/06 Section B als DISCONFIRMED markiert + 🧪 DRY marker activated.

User spielt jetzt CS auf Steam. Workbench-GUI würde mit CS um Focus + GPU kämpfen,
Screenshots würden Mischmasch capturen. → Diese Task macht **nur headless Steps**.

GUI Smoke (Steps 5-7 aus Task 006-original) ist in Task 007 verlegt → User triggert
das wenn CS fertig ist.

## Phase A (Two-Phase Reception)

⚙️ DO Items: **0** — alles headless, keine User-Klicks nötig.

Falls Sonnet-Switch gewünscht: vor Phase C im Modell-Selector wählen.
Sonst direkt Phase C starten.

## Phase C — Steps (alle headless)

### Step 1 — STATE.json + Logger + Reflection

```powershell
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
cd $repo
git pull --rebase

if (Test-Path "logs\reflection-turn-5.md") {
    Write-Output "=== Reading turn-5 reflection (Mac-side) ==="
    Get-Content "logs\reflection-turn-5.md"
}

$state = @{
    turn_id = 5
    owner = "pc"
    phase = "PHASE_C_EXEC"
    started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    pending_do = @()
    pending_exec = @(
        @{ id="exec-1"; desc="Verify pc-setup.ps1 fix (re-run idempotent)"; status="queued" }
        @{ id="exec-2"; desc="🧪 DRY plan compute + hash"; status="queued" }
        @{ id="exec-3"; desc="DRY approve + execute cleanup + recopy"; status="queued" }
        @{ id="exec-4"; desc="Re-validate 3 missions (confirm DRY didn't break)"; status="queued" }
        @{ id="exec-5"; desc="Auditor + reflection + push"; status="queued" }
    )
    loop_signals = @()
    notes = "CS parallel running on PC. NO GUI launches in this task. GUI smoke deferred to Task 007."
} | ConvertTo-Json -Depth 5
$state | Set-Content "tasks\STATE.json" -Encoding UTF8

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "logs\pc-events-task006cs-$ts.jsonl"
"{`"t`":`"$((Get-Date -Format 's')+'Z')`",`"kind`":`"start`",`"turn_id`":5,`"task_id`":`"006-CS`"}" | Add-Content $logFile
```

### Step 2 — Verify pc-setup.ps1 fix (re-run idempotent)

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\scripts\pc-setup.ps1"
```

Erwartung: **Kein Parse-Error mehr.** Output sollte:
- `[skip] Junction _vanilla_core existiert bereits`
- `[skip] Junction _vanilla_data existiert bereits`
- Leerzeile
- `Done. Workbench-Diag kann jetzt Vanilla-Deps resolven.`

Falls Parse-Error: Result mit Bug-Fix-Vorschlag, kein Block.

### Step 3 — 🧪 DRY Marker: Plan addon-cleanup + recopy

```powershell
$addonsRoot = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons"
$missions = @("night-recon-everon","day-assault-arland","fog-ambush-eden")

$dryPlan = @()
foreach ($mission in $missions) {
    $target = "$addonsRoot\ai_$mission"
    $src = "$repo\missions\$mission\output"
    $action = if (Test-Path $target) { "REMOVE_THEN_COPY" } else { "COPY" }
    $dryPlan += [PSCustomObject]@{
        mission = $mission
        target = $target
        src = $src
        action = $action
        files_to_delete = if (Test-Path $target) { (Get-ChildItem -Path $target -Recurse | Measure-Object).Count } else { 0 }
        files_to_copy = (Get-ChildItem -Path $src -Recurse | Measure-Object).Count
    }
}

$planJson = $dryPlan | ConvertTo-Json -Depth 3
$planHash = [BitConverter]::ToString(
    [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($planJson)
    )
).Replace("-","").Substring(0,16)

Write-Output "🧪 DRY PLAN (hash: $planHash)"
$dryPlan | Format-Table -AutoSize

$planJson | Set-Content "$repo\logs\dry-plan-task006cs-$ts.json"
"--- hash ---`n$planHash" | Add-Content "$repo\logs\dry-plan-task006cs-$ts.json"
```

### Step 4 — DRY Self-Approve + Execute

Cleanup ist reversibel (Re-Copy from missions/<id>/output), daher self-approve OK:

```powershell
Write-Output "DRY plan hash $planHash — self-approved (cleanup reversible via re-copy)"

foreach ($plan in $dryPlan) {
    if ($plan.action -eq "REMOVE_THEN_COPY") {
        Remove-Item -Path $plan.target -Recurse -Force
    }
    Copy-Item -Path $plan.src -Destination $plan.target -Recurse -Force
    Write-Output "[$($plan.mission)] $($plan.action): done"
}
```

### Step 5 — Re-Validate (confirms DRY didn't break anything)

```powershell
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
$revalidateResults = @{}

foreach ($mission in $missions) {
    $gproj = "$addonsRoot\ai_$mission\addon.gproj"
    $logDir = "$repo\logs\revalidate-$mission-task006cs"
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null

    $proc = Start-Process -FilePath $diag -ArgumentList @(
        "-gproj", "`"$gproj`"",
        "-validate",
        "-wbSilent",
        "-exitAfterInit",
        "-logsDir", "`"$logDir`""
    ) -PassThru -NoNewWindow

    $waitSec = 0
    while (-not $proc.HasExited -and $waitSec -lt 30) {
        Start-Sleep -Seconds 2
        $waitSec += 2
    }
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
        $revalidateResults[$mission] = @{status="TIMEOUT"}
        continue
    }

    $console = Get-ChildItem "$logDir\logs_*\console.log" -Recurse | Sort-Object LastWriteTime -Desc | Select-Object -First 1
    if (-not $console) {
        $revalidateResults[$mission] = @{status="NO_LOG"}
        continue
    }

    $content = Get-Content $console.FullName -Raw
    $fatals = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(F\):")).Count
    $errors = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(E\):")).Count

    $revalidateResults[$mission] = @{
        status = if (($fatals -eq 0) -and ($errors -eq 0)) {"PASS"} else {"FAIL"}
        fatal_count = $fatals
        error_count = $errors
        console_log = $console.FullName
    }
}

$revalidateResults | ConvertTo-Json -Depth 5 | Out-File "$repo\logs\revalidate-results-task006cs.json"
```

Erwartung: alle 3 PASS (wie Task 005). Falls FAIL → DRY hat was zerstört → bug-fixer.

**Wichtig**: Workbench-Diag läuft mit `-wbSilent -exitAfterInit -validate` — kein GUI-Fenster,
kein Focus-Steal, kein Screenshot. Sicher mit CS parallel.

### Step 6 — Auditor + Reflection + Push

```powershell
# Auditor (verifies):
# - DRY plan + hash + execute alle gepaired
# - Re-validate alle 3 PASS oder explicit bug-fixer-Vorschlag
# - keine GUI-Launches (regression check für CS-compat)

# reflection-turn-5.md (PC) schreiben
# Push:
cd $repo
$state = Get-Content "tasks\STATE.json" -Raw | ConvertFrom-Json
$state.phase = "PHASE_D_RETURN"
$state | ConvertTo-Json -Depth 5 | Set-Content "tasks\STATE.json" -Encoding UTF8

git pull --rebase
git add tasks/PC_RESULT.md tasks/STATE.json logs/
git commit -m "PC: Task 006-CS -- headless DRY + re-validate (CS-compat)"
git push
```

---

## Pause-Conditions

- DRY plan hash invalid zwischen Plan und Exec → STOP
- Re-validate FAIL für ≥1 Mission → STOP, bug-fixer (DRY hat etwas zerstört)
- Workbench-Diag crasht im validate-Mode → STOP (das wäre ein neuer Bug, nicht Task-Issue)
- turn_time_budget (15 min — Task ist kurz) → STOP

---

## Erwartete Dauer

- Steps 1-4: ~30s (alles File-Ops)
- Step 5 (Re-Validate × 3): ~30s
- Step 6 (Audit + reflection + push): ~1 min

**Total: ~2-3 min, alles headless, CS bleibt ungestört.**

PAUSE FLAG: nein.

---

## NEXT (Task 007, post-CS)

Wenn User CS beendet und in den Mac-Chat tippt "ready für GUI smoke" oder "Task 007 go":
Mac kompiliert Task 007 mit den GUI-Steps die ursprünglich in Task 006 waren (Workbench
launch + Screenshots + ui-tester multimodal classify).
