# PC Setup — reproduzierbar per Junction-Anlage für Vanilla-Addon-Deps
# Per Loop Turn #4 / PC question 2 — codify what PC discovered manually in Task 003.
#
# Run once per PC. Creates symlinks (junctions) so Workbench-Diag can resolve vanilla
# deps (`core` + `data`) when validating user-Addons.
#
# Idempotent: re-running is safe (mklink errors if exists, we ignore).

$ErrorActionPreference = "Continue"

$wbAddons = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons"
$steamReforger = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons"
$altSteam = "E:\SteamLibrary\steamapps\common\Arma Reforger\addons"

if (-not (Test-Path $steamReforger) -and (Test-Path $altSteam)) {
    $steamReforger = $altSteam
}

if (-not (Test-Path $steamReforger)) {
    Write-Error "Arma Reforger Steam-Install nicht gefunden. Erwartet: $steamReforger oder $altSteam"
    exit 1
}

New-Item -ItemType Directory -Path $wbAddons -Force | Out-Null

$junctions = @(
    @{ name = "_vanilla_core"; target = "$steamReforger\core" }
    @{ name = "_vanilla_data"; target = "$steamReforger\data" }
)

foreach ($j in $junctions) {
    $linkPath = Join-Path $wbAddons $j.name
    if (Test-Path $linkPath) {
        Write-Output "[skip] Junction $($j.name) existiert bereits"
        continue
    }
    if (-not (Test-Path $j.target)) {
        Write-Warning "Target nicht gefunden: $($j.target) — skip"
        continue
    }
    cmd /c mklink /J "`"$linkPath`"" "`"$($j.target)`""
    if ($LASTEXITCODE -eq 0) {
        Write-Output "[ok] Junction $($j.name) -> $($j.target)"
    } else {
        Write-Warning "mklink failed for $($j.name)"
    }
}

Write-Output "`nDone. Workbench-Diag kann jetzt Vanilla-Deps resolven."
