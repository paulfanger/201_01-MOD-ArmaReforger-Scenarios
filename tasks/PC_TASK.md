# PC Task — Task 005: Author-Fix Re-Validation (autonom, headless, log-pattern based)

STATUS: PENDING
TASK_ID: 005
PHASE: 2
TYPE: hardened_validation + log_pattern_pass_fail

## Kontext

Du hattest in Task 003 (Result commit 655c2f4) den Mac-Side-Bug aufgedeckt:
`Author "..."` in `addon.gproj` ist nicht im Enfusion-Schema, kein gültiges Keyword.

Mac hat behoben (commit incoming):
- `backend/exporters/gproj.py` Author-Zeile entfernt
- Alle 3 `missions/<id>/output/addon.gproj` Author-Zeile entfernt
- 111/111 Tests passen unverändert

**Du hattest 4 Fragen — Antworten:**

| Q | Antwort |
|---|---|
| Author-Attribution Place | DISCLOSURE.md ist die Heimat (bereits dort). Kein Kommentar im gproj — Enfusion akzeptiert es nicht. Fix ist komplett. |
| pc-setup.ps1 für Junctions | Ja — angelegt in `scripts/pc-setup.ps1`. Du kannst es re-runnen, idempotent. |
| Exit-Code vs Log-Pattern | Switch zu Log-Pattern. Success-Heuristik aus `research/06`: ≥1 `Entities load`, ≥1 `Entity layer load`, 0 `(F):` Zeilen. Exit-Code ignoriert ab Task 005. |
| Task 004 oder warten | Task 005 ersetzt 004. Direkt mit dieser Spec starten. |

Plus: Mac-Side hat Research-Findings integriert (`research/07-agentic-patterns-2026.md`):
- **🧪 DRY marker** für destructive operations (4th marker)
- Loop-Detector refined: 4 Loop-Typen (identical / repeated-error / monologue / no-progress)
- `tasks/STATE.json` für Crash-Recovery
- `logs/reflection-turn-<N>.md` Pflicht am Turn-Ende (Reflexion-Pattern)

---

## Schritt 0 — Two-Phase Reception verifizieren

Wenn du diesen Block bekommst, BEVOR du EXECutest:

**Phase A:** Da sind keine ⚙️ DO-Items in diesem Turn (Author-Fix war Mac-Side, kein User-Klick).
Sag User: "Keine manuellen Schritte. Starte Phase C direkt."

**Phase B:** Skip — keine Items zu verifizieren.

**Phase C (jetzt):** Run Steps 1-9 unten.

**Phase D:** Single Return Output am Ende.

---

## Schritt 1 — Update STATE.json + Logger + Reflection lesen

```powershell
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
cd $repo
git pull --rebase

# Read predecessor reflection (Reflexion pattern)
if (Test-Path "logs\reflection-turn-3.md") {
    Write-Output "=== Reading turn-3 reflection (Mac-side) ==="
    Get-Content "logs\reflection-turn-3.md"
}

# Update STATE.json: phase → PHASE_C_EXEC, owner → pc, turn_id 4 (this is your response to Mac's turn 4)
$state = @{
    turn_id = 4
    owner = "pc"
    phase = "PHASE_C_EXEC"
    started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    pending_do = @()
    pending_exec = @(
        @{ id="exec-1"; desc="pc-setup.ps1 (junctions)"; status="queued" }
        @{ id="exec-2"; desc="dep-installer pre-flight"; status="queued" }
        @{ id="exec-3"; desc="Re-copy 3 missions to addons"; status="queued" }
        @{ id="exec-4"; desc="Validate via log-pattern (3 missions)"; status="queued" }
        @{ id="exec-5"; desc="Smoke via log-pattern (3 missions)"; status="queued" }
        @{ id="exec-6"; desc="Auditor + reflection + push"; status="queued" }
    )
    loop_signals = @()
} | ConvertTo-Json -Depth 5
$state | Set-Content "tasks\STATE.json" -Encoding UTF8

# Start logger
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "logs\pc-events-task005-$ts.jsonl"
"{`"t`":`"$((Get-Date -Format 's')+'Z')`",`"kind`":`"start`",`"turn_id`":4,`"task_id`":`"005`"}" | Add-Content $logFile
```

## Schritt 2 — Junctions per scripts/pc-setup.ps1

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\scripts\pc-setup.ps1"
```

Capture Output. Falls schon vorhanden: `[skip]` ist ok.

## Schritt 3 — Dep-installer pre-flight

Wie Task 004 (spawned als sub-agent):
- git, powershell-screenshot, workbench-diag, python, pillow

Bei Auto-Install: process-tracker dafür. Output: `logs/deps-task005-<ts>.json`.

## Schritt 4 — Mission-Files frisch kopieren (Author-Fix anwenden)

```powershell
$addonsRoot = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons"
foreach ($mission in @("night-recon-everon","day-assault-arland","fog-ambush-eden")) {
    $src = "$repo\missions\$mission\output"
    $dst = "$addonsRoot\ai_$mission"
    Remove-Item -Path $dst -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item -Path $src -Destination $dst -Recurse -Force
    Write-Output "RECOPIED: $mission"

    # Verify: addon.gproj should NOT contain "Author"
    $gproj = Get-Content "$dst\addon.gproj" -Raw
    if ($gproj -match "^\s*Author\s") {
        Write-Output "FAIL: $mission still has Author line!"
    } else {
        Write-Output "OK: $mission addon.gproj clean"
    }
}
```

## Schritt 5 — Validate via LOG-PATTERN (jede Mission, max 3 retries, mit guards)

Pro Mission:

```powershell
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"

function Test-MissionValidate {
    param([string]$Mission, [string]$Repo, [string]$AddonsRoot)

    $addon = "$AddonsRoot\ai_$Mission"
    $gproj = "$addon\addon.gproj"
    $logDir = "$Repo\logs\validate-$Mission-task005"
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null

    $proc = Start-Process -FilePath $diag -ArgumentList @(
        "-gproj", "`"$gproj`"",
        "-validate",
        "-wbSilent",           # mandatory — sonst öffnet sich GUI-Dialog
        "-exitAfterInit",
        "-logsDir", "`"$logDir`""
    ) -PassThru -NoNewWindow

    # 60s budget per validate
    $waitSec = 0
    while (-not $proc.HasExited -and $waitSec -lt 60) {
        Start-Sleep -Seconds 2
        $waitSec += 2
    }

    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
        return @{ status="TIMEOUT"; mission=$Mission; logs=$null }
    }

    # Parse console.log — log-pattern based pass/fail (NOT exit code)
    $console = Get-ChildItem "$logDir\logs_*\console.log" -Recurse | Sort-Object LastWriteTime -Desc | Select-Object -First 1
    if (-not $console) {
        return @{ status="NO_LOG"; mission=$Mission; exit_code=$proc.ExitCode }
    }

    $content = Get-Content $console.FullName -Raw
    $hasEntitiesLoad = $content -match "WORLD\s+:\s+Entities load"
    $hasLayerLoad    = $content -match "WORLD\s+:\s+Entity layer load"
    $fatals          = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(F\):")).Count
    $errors          = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(E\):")).Count

    # -validate only compiles, doesn't necessarily emit Entities load
    # Success = NO fatals + NO non-author errors
    $passed = ($fatals -eq 0) -and ($errors -eq 0)

    return @{
        status = if ($passed) {"PASS"} else {"FAIL"}
        mission = $Mission
        exit_code = $proc.ExitCode  # informational only
        entities_load = $hasEntitiesLoad
        layer_load = $hasLayerLoad
        fatal_count = $fatals
        error_count = $errors
        console_log = $console.FullName
        error_lines = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\((E|F)\):.*$") | ForEach-Object { $_.Value } | Select-Object -First 10)
    }
}

$validateResults = @{}
foreach ($mission in @("night-recon-everon","day-assault-arland","fog-ambush-eden")) {
    $iter = 0
    $errorHashes = @()  # for action-class + error-class loop-detector
    while ($iter -lt 3) {
        $iter++
        $r = Test-MissionValidate -Mission $mission -Repo $repo -AddonsRoot $addonsRoot
        $r.iter = $iter

        # Loop-detector (action-class + error-class)
        $errorClass = if ($r.status -eq "PASS") { "ok" } else { "$($r.status):$($r.fatal_count)F-$($r.error_count)E" }
        $errorHashes += $errorClass

        if ($r.status -eq "PASS") {
            $validateResults[$mission] = $r
            break
        }

        # Same error-class 4× → LOOP_DETECTED (StuckDetector threshold)
        $dupes = $errorHashes | Group-Object | Where-Object { $_.Count -ge 4 }
        if ($dupes) {
            Write-Output "LOOP_DETECTED on $mission — same error-class $iter× — escalating"
            $r.status = "LOOP_DETECTED"
            $validateResults[$mission] = $r
            break
        }

        Start-Sleep -Seconds 3
    }

    if (-not $validateResults.ContainsKey($mission)) {
        $validateResults[$mission] = @{ status="FAIL_MAX_RETRIES"; mission=$mission; iter=$iter }
    }
}

$validateResults | ConvertTo-Json -Depth 5 | Out-File "$repo\logs\validate-results-task005.json"
```

## Schritt 6 — Smoke-Test (conditional auf Validate PASS)

Für jede Mission die Validate PASSED:

```powershell
function Test-MissionSmoke {
    param([string]$Mission, [string]$Repo, [string]$AddonsRoot)

    $diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
    $addon = "$AddonsRoot\ai_$Mission"
    $gproj = "$addon\addon.gproj"
    $worldRef = "`$ai_${Mission}:Worlds/${Mission}.ent"
    $logDir = "$Repo\logs\smoke-$Mission-task005"
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null

    $proc = Start-Process -FilePath $diag -ArgumentList @(
        "-gproj", "`"$gproj`"",
        "-load", "`"$worldRef`"",
        "-wbSilent",
        "-exitAfterInit",
        "-logsDir", "`"$logDir`""
    ) -PassThru -NoNewWindow

    # 180s budget
    $waitSec = 0
    while (-not $proc.HasExited -and $waitSec -lt 180) {
        Start-Sleep -Seconds 5
        $waitSec += 5
    }

    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
        return @{ status="TIMEOUT"; mission=$Mission }
    }

    # SUCCESS HEURISTIC (log-pattern, per research/06 + 07):
    # ≥1 Entities load + ≥1 Entity layer load + 0 fatal lines
    $console = Get-ChildItem "$logDir\logs_*\console.log" -Recurse | Sort-Object LastWriteTime -Desc | Select-Object -First 1
    if (-not $console) {
        return @{ status="NO_LOG"; mission=$Mission }
    }

    $content = Get-Content $console.FullName -Raw
    $hasEntitiesLoad = $content -match "WORLD\s+:\s+Entities load"
    $hasLayerLoad    = $content -match "WORLD\s+:\s+Entity layer load"
    $fatals          = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(F\):")).Count
    $errors          = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(E\):")).Count

    $passed = $hasEntitiesLoad -and $hasLayerLoad -and ($fatals -eq 0)

    return @{
        status = if ($passed) {"PASS"} else {"FAIL"}
        mission = $Mission
        entities_load = $hasEntitiesLoad
        layer_load = $hasLayerLoad
        fatal_count = $fatals
        error_count = $errors
        console_log = $console.FullName
        error_lines = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\((E|F)\):.*$") | ForEach-Object { $_.Value } | Select-Object -First 15)
    }
}

$smokeResults = @{}
foreach ($mission in @("night-recon-everon","day-assault-arland","fog-ambush-eden")) {
    if ($validateResults[$mission].status -ne "PASS") {
        $smokeResults[$mission] = @{ status="SKIP"; reason="validate failed/loop"; mission=$mission }
        continue
    }
    $smokeResults[$mission] = Test-MissionSmoke -Mission $mission -Repo $repo -AddonsRoot $addonsRoot
}
$smokeResults | ConvertTo-Json -Depth 5 | Out-File "$repo\logs\smoke-results-task005.json"
```

## Schritt 7 — Bug-fixer (falls FAILs)

Falls Validate oder Smoke FAILs hat: spawn bug-fixer mit den error_lines aus den
console.logs. Output: `logs/bugfix-task005-<ts>.json`.

bug-fixer schlägt VOR, ändert KEINE Mission-Files.

## Schritt 8 — Auditor pre-push

Auditor verifiziert:
- alle 3 Missions tracked (validate + smoke)
- alle console.logs in result referenced
- alle (E)/(F) triaged (bug-fixer angesprungen wenn nötig)
- STATE.json korrekt (phase=PHASE_D_RETURN at end)
- reflection-turn-4.md geschrieben

Output: `logs/audit-task005-<ts>.json`.

Falls Audit BLOCKED → STOP, melde im Result.

## Schritt 9 — Reflection schreiben (Reflexion pattern)

Schreib `logs/reflection-turn-4.md` (PC-side) mit Struktur:

```markdown
# Turn 4 Reflection (PC-side)

## What went well
- ...

## What failed (and why)
- ...

## What I'd do differently next turn
- ...

## Signals for optimizer
- duration_ms: <X>
- sub-agents spawned: <N>
- guards fired: <list>
- loop signals: <list>
```

## Schritt 10 — Commit + Push

```powershell
cd $repo
# Update STATE.json: phase → PHASE_D_RETURN
$state = Get-Content "tasks\STATE.json" -Raw | ConvertFrom-Json
$state.phase = "PHASE_D_RETURN"
$state | ConvertTo-Json -Depth 5 | Set-Content "tasks\STATE.json" -Encoding UTF8

git pull --rebase
git add tasks/PC_RESULT.md tasks/STATE.json logs/
git commit -m "PC: Task 005 — Author-fix validate + smoke (log-pattern)"
git push
```

---

## Pause-Conditions (HARD STOP)

- LOOP_DETECTED (4 retries same error-class) → STOP, blocker mit evidence
- Steam-Tools fehlt nach dep-install → STOP, ⚙️ DO
- Workbench-Diag crash <5s mit (F) → STOP, bug-fixer im Result
- Junction creation fails → STOP, Workbench kann nicht resolven
- turn_time_budget (30 min) → STOP, was-bisher-erreicht

---

## Erwartete Dauer

- Steps 0-3: ~30s
- Step 4 (Re-Copy): ~10s
- Step 5 (Validate × 3): ~30s (10s/Mission, ohne retries)
- Step 6 (Smoke × 3): 3-9 min (1-3 min/Mission)
- Steps 7-10: ~60s

Total: 5-12 min, ohne User-Klicks. PAUSE FLAG: nein.
