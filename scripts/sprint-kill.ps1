# sprint-kill.ps1 — Emergency halt for autonomous sprint
#
# HOW TO USE:
#   Open a separate PowerShell window while sprint is running.
#   Run: powershell -ExecutionPolicy Bypass -File scripts\sprint-kill.ps1
#
# WHAT HAPPENS:
#   Creates sprint-kill.flag in repo root.
#   The orchestrator polls this file at every branch transition.
#   On detection: orchestrator deletes the flag, writes STATE.json
#   with reason='user-kill', commits + pushes current state, exits cleanly.
#   Goal: clean exit without Ctrl+C losing state or leaving repo dirty.
#
# WHEN TO USE:
#   - Sprint is going off the rails and you want a clean stop
#   - You need the PC for something else immediately
#   - An unexpected window appeared and you want sprint to pause
#
# DO NOT use Ctrl+C unless sprint is truly frozen — that loses STATE.

$repo = $PSScriptRoot | Split-Path -Parent
$flagPath = Join-Path $repo "sprint-kill.flag"

New-Item -ItemType File -Path $flagPath -Force | Out-Null
Write-Host "sprint-kill.flag created at: $flagPath" -ForegroundColor Yellow
Write-Host "Sprint will halt cleanly at next branch transition." -ForegroundColor Yellow
Write-Host "Check STATE.json for final state after halt." -ForegroundColor Cyan
