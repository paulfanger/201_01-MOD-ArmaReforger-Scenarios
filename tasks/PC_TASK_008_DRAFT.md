# PC Task — Task 008 DRAFT (PRE-STAGED, NOT YET ACTIVE)

> **Status:** DRAFT — wartet auf User-Signal "ready für GUI smoke" oder "Task 008 go"
> **Aktivierung:** Mac kopiert diesen Inhalt nach `tasks/PC_TASK.md` und pusht
> **PC darf NICHT executen bevor diese Promotion passiert ist**

TASK_ID: 008
TURN_ID: <wird bei Aktivierung gesetzt>
PHASE: 2 (Smoke) → bridge zu Phase 3 (Game Launch)
TYPE: cs_termination + gui_smoke + multimodal_ui_verify

## Kontext (für Review)

Task 005 lieferte 3/3 Validate PASS (CI-Gate stable). Smoke-Test mit `-wbSilent` ist
disconfirmed (research/06 Section B). Pfad: **(b) GUI + Auto-Screenshot + multimodal
ui-tester classify** wenn CS beendet ist.

## Phase A (Two-Phase Reception)

⚙️ DO Items:
1. [BLOCKING] **Counter-Strike komplett geschlossen** — kein cs2.exe-Prozess mehr,
   keine Steam-Game-Session aktiv. GPU muss frei sein für Workbench.

PC fragt User: "Ist CS komplett zu? Soll ich Step 0 (CS-Kill als Safety-Net) durchziehen?"
Wenn User "ja" → Phase B verifiziert, dann Phase C.

## Phase B — Verify

```powershell
$csProcs = Get-Process | Where-Object {
    $_.ProcessName -in @("cs2", "csgo", "Counter-Strike", "steamwebhelper") -or
    $_.MainWindowTitle -like "*Counter-Strike*"
}
if ($csProcs) {
    Write-Output "CS still running: $($csProcs | Select-Object Id, ProcessName, MainWindowTitle | Format-Table | Out-String)"
} else {
    Write-Output "✓ No CS processes detected"
}

# Workbench/Game prozesse vor Start aufräumen
Get-Process | Where-Object { $_.ProcessName -like "*Workbench*" -or $_.ProcessName -like "*ArmaReforger*" } | ForEach-Object {
    Write-Output "Pre-cleanup: Stopping PID $($_.Id) ($($_.ProcessName))"
    Stop-Process -Id $_.Id -Force
}
Start-Sleep -Seconds 3
```

Falls CS noch läuft: STOP, melde User → User schließt manuell.
Falls CS sauber zu: weiter Phase C.

## Phase C — Steps

### Step 0 — Safety: CS-Kill (falls noch da)

```powershell
# Nur als Safety-Net — sollte nach Phase B leer sein
$csProcs = Get-Process | Where-Object { $_.ProcessName -in @("cs2","csgo") }
if ($csProcs) {
    Write-Warning "CS still running, killing as user-approved safety net"
    $csProcs | Stop-Process -Force
    Start-Sleep -Seconds 5
}
```

### Step 1 — STATE.json + Logger + Reflection (Mac turn-7)

Standard pattern. STATE: turn_id=<active>, owner=pc, phase=PHASE_C_EXEC,
notes="GUI Smoke Test - CS beendet".

### Step 2 — Re-Confirm Validate (Pre-GUI sanity)

Alle 3 Missions schnell validate (~30s). Wenn nicht alle PASS → STOP (würde bedeuten
zwischen CS-Sessions etwas kaputt gegangen ist).

### Step 3 — GUI Workbench Launch pro Mission

```powershell
function Start-WorkbenchGUI {
    param([string]$Mission, [string]$Repo, [string]$AddonsRoot)

    $diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
    $addon = "$AddonsRoot\ai_$Mission"
    $gproj = "$addon\addon.gproj"
    $worldRef = "`$ai_${Mission}:Worlds/${Mission}.ent"
    $logDir = "$Repo\logs\gui-smoke-$Mission-task008"
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null

    # GUI mode — NO -wbSilent!
    $proc = Start-Process -FilePath $diag -ArgumentList @(
        "-gproj", "`"$gproj`"",
        "-load", "`"$worldRef`"",
        "-logsDir", "`"$logDir`""
    ) -PassThru

    # Screenshots at 60s / 90s / 120s
    $screenshots = @()
    foreach ($wait in 60, 90, 120) {
        # Wait incrementally
        $elapsedNow = if ($wait -eq 60) {60} else {30}
        Start-Sleep -Seconds $elapsedNow
        $shotPath = "$logDir\screenshot-${wait}sec.png"
        Take-Screenshot -OutPath $shotPath
        $screenshots += $shotPath

        $alive = -not $proc.HasExited
        Write-Output "[$Mission @ ${wait}s] alive=$alive · shot=$shotPath"

        if (-not $alive) {
            Write-Warning "[$Mission @ ${wait}s] Process exited unexpectedly"
            break
        }
    }

    # Window enum (final state)
    $windows = Get-VisibleWindows | Where-Object {
        $_.ProcessName -like "*Workbench*" -or $_.ProcessName -like "*ArmaReforger*"
    }

    # Close Workbench gracefully (so next Mission can start fresh)
    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
        Start-Sleep -Seconds 3
    }

    return @{
        mission = $Mission
        screenshots = $screenshots
        windows_at_end = $windows
        log_dir = $logDir
    }
}

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
    $guiResults[$mission] = Start-WorkbenchGUI -Mission $mission -Repo $repo -AddonsRoot $addonsRoot
    Start-Sleep -Seconds 5
}
```

### Step 4 — Spawn ui-tester pro Screenshot (9 total)

Multimodal-Vision-Classify pro PNG:
- `mission_loaded` — Karte mit Entitäten/Marker sichtbar
- `project_selector` — Workbench Dialog "Open Project"
- `error_popup` — Error-Dialog mit OCR-text
- `loading` — Splash / progress bar
- `crashed` — Window weg
- `unknown` — keiner davon

Output pro Screenshot: `logs/ui-task008-<mission>-<seconds>s.json`.

### Step 5 — Aggregate Verdict

Per Mission: ≥1 `mission_loaded` Screenshot = PASS. Sonst FAIL/UNKNOWN.

### Step 6 — Bug-fixer + Auditor

Falls 0/3 missions PASS: bug-fixer mit allen Screenshots + Workbench-Logs.
Auditor verifies: alle 9 PNGs in logs/, alle 9 ui-tester-JSONs, verdict-Aggregat
in result.

### Step 7 — Reflection-turn-<N>-pc.md + Push

---

## Pause-Conditions

- Phase B: CS noch aktiv → User-Action erforderlich (manuell schließen)
- Workbench-Diag crash <5s nach Start → STOP, bug-fixer
- 3/3 missions als project_selector → SendKeys-Simulation oder GUI-Auto-Click nötig?
  Mac entscheidet im Loop Turn #8
- turn_time_budget (30 min) → STOP

---

## Erwartete Dauer

- Phase A/B: 30s
- Step 2 Re-Validate: 30s
- Step 3 GUI Launch × 3 Missions (~135s GUI life + 5s spacing each): ~7 min
- Step 4 ui-tester × 9: 3 min
- Steps 5-7: 1 min

Total: ~12-15 min. PAUSE FLAG: nein (außer Phase B CS-still-running).

---

## DRAFT NOTES (für Mac-Review)

PC's Recommendation in Task 006-CS Notes: "CS explizit beendet vor GUI-Launch (GPU-Konflikt).
Als Step 0 im Task-008-Spec?" — JA, integriert als Phase B + Step 0 Safety-Net.

CHEATSHEET-PC Section 5 (GPU/Library) wird in Task 007b-CS ergänzt.
