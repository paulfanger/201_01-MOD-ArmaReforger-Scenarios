# PC Task — Task 002: Workbench Install + Game First-Start

STATUS: PENDING
TASK_ID: 002
PHASE: 2-prep
TYPE: install_tools + game_first_start + addon_setup
APPROVAL: granted (Mac-Session autorisiert Steam-Install via CLI + Game-First-Start)

---

## Übersicht

PC hat in Task 001 gemeldet: Arma Reforger Tools fehlen, AppData fehlt.
Diese Task löst beide Blocker. **Du darfst Steam-CLI nutzen und das Game einmalig starten.**

Alle Schritte ausführen, dann **einmal** pushen mit kompletten Ergebnissen.

---

## Schritt 1 — Arma Reforger Tools via Steam installieren

```powershell
# App-ID für Arma Reforger Tools: 1874881
Start-Process "steam://install/1874881"
Write-Output "STEAM_INSTALL_TRIGGERED"
```

Steam-UI öffnet sich. Klicke "Install" wenn Steam-Dialog erscheint — das ist die einzige manuelle Interaktion die nötig ist. Falls Steam autonom installiert: noch besser.

**Warte auf Install** (poll bis Ordner existiert, max 20 Minuten):

```powershell
$toolsPath = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe"
$alt = "E:\SteamLibrary\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe"
$maxWaitMin = 20
$start = Get-Date

while (-not (Test-Path $toolsPath) -and -not (Test-Path $alt)) {
    Start-Sleep -Seconds 30
    $elapsed = (Get-Date) - $start
    Write-Output "Warte auf Install... $($elapsed.TotalMinutes.ToString('0.0')) min"
    if ($elapsed.TotalMinutes -gt $maxWaitMin) {
        Write-Output "TIMEOUT — Install dauert zu lange. Abbruch."
        break
    }
}

if (Test-Path $toolsPath) {
    $foundPath = $toolsPath
} elseif (Test-Path $alt) {
    $foundPath = $alt
} else {
    $foundPath = $null
}
Write-Output "WORKBENCH_PATH: $foundPath"
```

Schreib in PC_RESULT.md unter `### Tools Install`: ob installation erfolgreich, Pfad.

---

## Schritt 2 — Game First-Start (für AppData-Ordner)

```powershell
# Game einmal starten, damit Bohemia AppData-Ordner entsteht
Start-Process "steam://run/1874880"  # Arma Reforger Game
Start-Sleep -Seconds 60  # Warte bis Game zumindest geladen hat

# Prüfe ob AppData entstanden ist
$appData = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger"
$exists = Test-Path $appData
Write-Output "APPDATA_CREATED: $exists"

# Falls Game gestartet ist, schließen wir es wieder
$gameProc = Get-Process -Name "ArmaReforger*" -ErrorAction SilentlyContinue
if ($gameProc) {
    Write-Output "Schliesse Game..."
    $gameProc | Stop-Process -Force
    Start-Sleep -Seconds 5
}
```

**Hinweis:** Wenn beim Game-Start ein EULA-Fenster erscheint, klicke "Accept". Das ist eine einmalige manuelle Aktion. Falls Game stumm im Hintergrund läuft → ok.

Schreib in PC_RESULT.md unter `### Game First-Start`: ob AppData entstanden, welcher Pfad.

---

## Schritt 3 — Addon-Ordner anlegen

```powershell
$addonsRoot = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger\addons"
New-Item -ItemType Directory -Path $addonsRoot -Force | Out-Null
Get-Item $addonsRoot
```

Schreib in PC_RESULT.md unter `### Addon Folder`: Existenz bestätigt.

---

## Schritt 4 — Missions kopieren

Wie in Task 001 geplant, jetzt mit existenten Pfaden:

```powershell
$projectRoot = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
$addonsRoot = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger\addons"

$missions = @("night-recon-everon", "day-assault-arland", "fog-ambush-eden")
foreach ($mission in $missions) {
    $src = "$projectRoot\missions\$mission\output"
    $dst = "$addonsRoot\ai_$mission"
    if (Test-Path $src) {
        Remove-Item -Path $dst -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item -Path $src -Destination $dst -Recurse -Force
        Write-Output "COPIED: $mission -> $dst"
    } else {
        Write-Output "MISSING_SOURCE: $src"
    }
}
```

Schreib in PC_RESULT.md unter `### Mission Copy`: alle 3 Missionen kopiert?

---

## Schritt 5 — File Integrity Check

```powershell
$addonsRoot = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger\addons"
$results = @()
foreach ($mission in @("night-recon-everon", "day-assault-arland", "fog-ambush-eden")) {
    $base = "$addonsRoot\ai_$mission"
    $files = @(
        "addon.gproj",
        "Missions\$mission.conf",
        "Worlds\$mission.ent",
        "Worlds\${mission}_gamemode.layer",
        "Worlds\${mission}_spawnpoints.layer",
        "Worlds\${mission}_managers.layer",
        "Worlds\${mission}_AI.layer",
        "Worlds\${mission}_environment.layer",
        "Worlds\${mission}_triggers.layer",
        "Worlds\${mission}_tasks.layer"
    )
    foreach ($f in $files) {
        $exists = Test-Path "$base\$f"
        $results += [PSCustomObject]@{Mission=$mission; File=$f; Exists=$exists}
    }
}
$results | Format-Table -AutoSize
```

Schreib in PC_RESULT.md unter `### File Integrity`: tabellarisch alle Files.

---

## Schritt 6 — Workbench Help (CLI Capabilities)

Sobald Workbench installiert ist:

```powershell
$workbench = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe"
if (-not (Test-Path $workbench)) {
    $workbench = "E:\SteamLibrary\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe"
}

if (Test-Path $workbench) {
    Write-Output "=== Workbench -help ==="
    & $workbench -help 2>&1 | Select-Object -First 50

    Write-Output "=== Workbench /? ==="
    & $workbench /? 2>&1 | Select-Object -First 50

    # Auch ohne Args starten, dann sofort killen — manchmal zeigt Usage-Dialog
    Write-Output "=== Workbench Version Info via FileInfo ==="
    Get-Item $workbench | Select-Object -Property Name, Length, LastWriteTime
    (Get-Item $workbench).VersionInfo
}
```

Schreib in PC_RESULT.md unter `### Workbench CLI`: alle Outputs.

---

## Schritt 7 — Workbench Test-Launch mit erstem Addon

```powershell
$workbench = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe"
if (-not (Test-Path $workbench)) {
    $workbench = "E:\SteamLibrary\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbench.exe"
}
$addon = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger\addons\ai_night-recon-everon\addon.gproj"

if ((Test-Path $workbench) -and (Test-Path $addon)) {
    Write-Output "Starte Workbench mit Addon..."
    $proc = Start-Process -FilePath $workbench -ArgumentList "`"$addon`"" -PassThru
    Start-Sleep -Seconds 30
    if ($proc.HasExited) {
        Write-Output "WORKBENCH_CRASHED: ExitCode $($proc.ExitCode)"
    } else {
        Write-Output "WORKBENCH_RUNNING: PID $($proc.Id)"
    }

    # Workbench-Logs einsammeln
    Start-Sleep -Seconds 5
    $logDir = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger\logs"
    if (Test-Path $logDir) {
        Write-Output "=== Neueste 3 Log-Files ==="
        Get-ChildItem $logDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | Format-Table FullName, Length, LastWriteTime
        $newest = Get-ChildItem $logDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($newest) {
            Write-Output "=== Letzte 80 Zeilen von $($newest.Name) ==="
            Get-Content $newest.FullName -Tail 80
        }
    } else {
        Write-Output "KEIN_LOG_DIR: $logDir"
    }
}
```

**Workbench laufen lassen.** Nicht killen. User schaut visuell.

Schreib in PC_RESULT.md unter `### Workbench Launch`: PID, Crash ja/nein, Log-Output.

---

## Schritt 8 — Push

```powershell
cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
git pull --rebase
git add tasks/PC_RESULT.md
git commit -m "PC: Task 002 — tools install + game start + addon setup"
git push
```

Setze STATUS oben in PC_RESULT.md:
- **OK** wenn Workbench läuft mit Addon ohne Crash
- **PARTIAL** wenn Workbench läuft aber Logs zeigen Errors
- **ERROR** wenn Workbench nicht startet oder crasht

---

## Wichtig

- Falls Steam-Install fehlt (z.B. Steam zeigt Dialog): warte bis User klickt, dann weiter
- Falls EULA-Popup beim Game-Start: warte 30s, falls noch da → Game schließen, ohne EULA-Accept geht nichts weiter; im Result als BLOCKER vermerken
- Wenn Workbench läuft, lass es **offen** — User schaut visuell ob Mission erscheint
