# PC Setup — reproduzierbar per Junction-Anlage für Vanilla-Addon-Deps
# Per Loop Turn #5 / fixes Line 49 quoting bug reported in Task 005.
#
# Run once per PC. Creates symlinks (junctions) so Workbench-Diag can resolve vanilla
# deps (`core` + `data`) when validating user-Addons.
#
# Idempotent: re-running is safe.

$ErrorActionPreference = "Continue"

$wbAddons = Join-Path $env:USERPROFILE "Documents\my games\ArmaReforgerWorkbench\addons"
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
    @{ name = "_vanilla_core"; target = (Join-Path $steamReforger "core") }
    @{ name = "_vanilla_data"; target = (Join-Path $steamReforger "data") }
)

foreach ($j in $junctions) {
    $linkPath = Join-Path $wbAddons $j.name
    if (Test-Path $linkPath) {
        Write-Output ("[skip] Junction {0} existiert bereits" -f $j.name)
        continue
    }
    if (-not (Test-Path $j.target)) {
        Write-Warning ("Target nicht gefunden: {0} -- skip" -f $j.target)
        continue
    }
    # Use New-Item with SymbolicLink (PowerShell-native, no cmd.exe quoting issues)
    try {
        New-Item -ItemType Junction -Path $linkPath -Target $j.target -Force | Out-Null
        Write-Output ("[ok] Junction {0} -> {1}" -f $j.name, $j.target)
    } catch {
        Write-Warning ("Junction creation failed for {0}: {1}" -f $j.name, $_.Exception.Message)
    }
}

Write-Output ""
Write-Output "Done. Workbench-Diag kann jetzt Vanilla-Deps resolven."
