# file-watcher.ps1 — AI-Spec File Watcher for Workbench Hot-Reload
#
# Sprint MEGA-A (A.S5PREP.5)
#
# Watches $profile:elos/ai-spec.json for changes.
# When changed: finds Workbench window, brings it to foreground,
# sends Ctrl+Shift+R ("Reload WB Scripts") to trigger AI_GeneratePlugin.Run().
#
# Realistic latency: 1-2s (from file write to plugin Run())
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\file-watcher.ps1
#   (run alongside Workbench; Ctrl+C to stop)
#
# Note on SendKeys:
#   Workbench is a standard Win32 app — SendKeys works.
#   For DirectX games, PyDirectInput would be needed instead.

$ErrorActionPreference = "Continue"

# ---- Config -----------------------------------------------------------------

$profileBase = "$env:USERPROFILE\Documents\My Games\ArmaReforgerWorkbench\profile\elos"
$watchFile   = "ai-spec.json"
$reloadKey   = "^+R"   # Ctrl+Shift+R = Workbench "Reload WB Scripts" shortcut

# ---- Assembly types ---------------------------------------------------------

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

# ---- Create watch directory if missing --------------------------------------

if (-not (Test-Path $profileBase)) {
    New-Item -ItemType Directory -Path $profileBase -Force | Out-Null
    Write-Output "Created watch dir: $profileBase"
}

# ---- Initialize FileSystemWatcher -------------------------------------------

$watcher                    = New-Object System.IO.FileSystemWatcher
$watcher.Path               = $profileBase
$watcher.Filter             = $watchFile
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents   = $false   # we'll enable after setup

# ---- Action: send reload to Workbench ---------------------------------------

$action = {
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    Write-Output "[$timestamp] ai-spec.json changed — sending Ctrl+Shift+R to Workbench"

    # Find Workbench window
    $wb = Get-Process | Where-Object {
        $_.ProcessName -like "*Workbench*" -and $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne ""
    } | Select-Object -First 1

    if (-not $wb) {
        Write-Warning "[$timestamp] Workbench not found — is it running with WorldEditor open?"
        return
    }

    # Bring window to foreground
    try {
        [Microsoft.VisualBasic.Interaction]::AppActivate($wb.Id) | Out-Null
        Start-Sleep -Milliseconds 150
    } catch {
        Write-Warning "AppActivate failed: $($_.Exception.Message) — trying SendKeys anyway"
    }

    # Send Ctrl+Shift+R (Reload WB Scripts)
    [System.Windows.Forms.SendKeys]::SendWait($reloadKey)
    Write-Output "[$timestamp] Sent $reloadKey to Workbench PID $($wb.Id) ('$($wb.MainWindowTitle)')"
}

# ---- Register event ---------------------------------------------------------

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
$watcher.EnableRaisingEvents = $true

Write-Output "File watcher ACTIVE"
Write-Output "  Watching: $profileBase\$watchFile"
Write-Output "  On change: Ctrl+Shift+R → Workbench Reload WB Scripts"
Write-Output "  Expected latency: 1-2s"
Write-Output "  Press Ctrl+C to stop."
Write-Output ""

# ---- Keep alive -------------------------------------------------------------

try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Write-Output "File watcher stopped."
}
