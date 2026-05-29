# verify-deps.ps1
# Reads pc-requirements.toml and reports which deps are installed vs missing.
# Run BEFORE starting any sprint — fix missing deps in user-present session.
# Per Postmortem #3 fix: deps must be pre-declared + pre-installed, never mid-sprint.

param(
    [switch]$InstallMissing = $false
)

$ErrorActionPreference = "Continue"
$repo = $PSScriptRoot | Split-Path -Parent
$manifestPath = Join-Path $repo "pc-requirements.toml"

if (-not (Test-Path $manifestPath)) {
    Write-Error "Manifest not found: $manifestPath"
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host " ELOS PC Dep Verification"
Write-Host " Manifest: $manifestPath"
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host ""

$results = @{ ok = @(); missing = @(); skipped = @() }

# ─── WINGET deps ────────────────────────────────────────────────────────────
Write-Host "── WINGET ──" -ForegroundColor Cyan
$wingetDeps = @(
    @{ id="Git.Git"; verify="git --version" },
    @{ id="GitHub.cli"; verify="gh --version" },
    @{ id="Microsoft.VisualStudioCode"; verify="code --version" },
    @{ id="OpenJS.NodeJS.LTS"; verify="node --version" },
    @{ id="Python.Python.3.12"; verify="python --version" },
    @{ id="AutoHotkey.AutoHotkey"; verify="where AutoHotkey"; deprecated=$true }
)
foreach ($d in $wingetDeps) {
    $deprecated = if ($d.deprecated) { " [deprecated]" } else { "" }
    try {
        $out = Invoke-Expression $d.verify 2>&1
        if ($LASTEXITCODE -eq 0 -or $out) {
            Write-Host "  [OK]      $($d.id)$deprecated" -ForegroundColor Green
            $results.ok += $d.id
        } else {
            Write-Host "  [MISSING] $($d.id)$deprecated" -ForegroundColor Red
            $results.missing += @{ kind="winget"; id=$d.id }
        }
    } catch {
        Write-Host "  [MISSING] $($d.id)$deprecated" -ForegroundColor Red
        $results.missing += @{ kind="winget"; id=$d.id }
    }
}

# ─── PIP deps (read requirements.txt) ───────────────────────────────────────
Write-Host ""
Write-Host "── PIP ──" -ForegroundColor Cyan
$reqPath = Join-Path $repo "requirements.txt"
if (Test-Path $reqPath) {
    $pipPackages = Get-Content $reqPath | Where-Object { $_ -and -not $_.StartsWith("#") } | ForEach-Object {
        ($_ -split '[<>=]')[0].Trim()
    }
    foreach ($pkg in $pipPackages) {
        $check = python -c "import importlib; importlib.import_module('$pkg'.replace('-','_'))" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK]      $pkg" -ForegroundColor Green
            $results.ok += "pip:$pkg"
        } else {
            Write-Host "  [MISSING] $pkg" -ForegroundColor Red
            $results.missing += @{ kind="pip"; id=$pkg }
        }
    }
} else {
    Write-Host "  requirements.txt not found, skipping pip check" -ForegroundColor Yellow
}

# ─── NPM GLOBAL ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "── NPM GLOBAL ──" -ForegroundColor Cyan
$npmGlobals = @("chokidar-cli")
foreach ($pkg in $npmGlobals) {
    $exists = npm list -g $pkg 2>$null | Select-String $pkg
    if ($exists) {
        Write-Host "  [OK]      $pkg" -ForegroundColor Green
        $results.ok += "npm:$pkg"
    } else {
        Write-Host "  [MISSING] $pkg" -ForegroundColor Red
        $results.missing += @{ kind="npm"; id=$pkg }
    }
}

# ─── STEAM APPS (path-based check) ──────────────────────────────────────────
Write-Host ""
Write-Host "── STEAM APPS ──" -ForegroundColor Cyan
$steamApps = @(
    @{ name="Arma Reforger"; path='C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerSteam.exe' },
    @{ name="Arma Reforger Tools"; path='C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteam.exe' }
)
foreach ($app in $steamApps) {
    if (Test-Path $app.path) {
        Write-Host "  [OK]      $($app.name)" -ForegroundColor Green
        $results.ok += "steam:$($app.name)"
    } else {
        Write-Host "  [MISSING] $($app.name) at $($app.path)" -ForegroundColor Red
        $results.missing += @{ kind="steam"; id=$app.name }
    }
}

# ─── ENV VARS ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "── ENV VARS ──" -ForegroundColor Cyan
$apiKey = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
if ($apiKey -and $apiKey.Length -gt 50) {
    Write-Host "  [OK]      ANTHROPIC_API_KEY (User scope, $($apiKey.Length) chars)" -ForegroundColor Green
    $results.ok += "env:ANTHROPIC_API_KEY"
} else {
    Write-Host "  [MISSING] ANTHROPIC_API_KEY in User scope" -ForegroundColor Red
    $results.missing += @{ kind="env"; id="ANTHROPIC_API_KEY" }
}

# ─── JUNCTIONS ──────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "── JUNCTIONS ──" -ForegroundColor Cyan
$junctions = @(
    "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_core",
    "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_data"
)
foreach ($j in $junctions) {
    if (Test-Path $j) {
        Write-Host "  [OK]      $(Split-Path $j -Leaf)" -ForegroundColor Green
        $results.ok += "junction:$(Split-Path $j -Leaf)"
    } else {
        Write-Host "  [MISSING] $(Split-Path $j -Leaf) — run scripts/pc-setup.ps1" -ForegroundColor Red
        $results.missing += @{ kind="junction"; id=(Split-Path $j -Leaf) }
    }
}

# ─── SUMMARY ────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host " SUMMARY"
Write-Host "═══════════════════════════════════════════════════════════════"
Write-Host "  OK:      $($results.ok.Count)" -ForegroundColor Green
Write-Host "  MISSING: $($results.missing.Count)" -ForegroundColor $(if ($results.missing.Count -gt 0) { "Red" } else { "Green" })

if ($results.missing.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✅ ALL DEPS PRESENT. Sprint can start." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "  ❌ MISSING DEPS — fix before sprint:" -ForegroundColor Red
Write-Host ""
foreach ($m in $results.missing) {
    switch ($m.kind) {
        "winget" { Write-Host "    winget install --id $($m.id) -e --accept-package-agreements --accept-source-agreements" }
        "pip"    { Write-Host "    pip install --user $($m.id)" }
        "npm"    { Write-Host "    npm install -g $($m.id)" }
        "steam"  { Write-Host "    Install '$($m.id)' via Steam client manually" }
        "env"    { Write-Host "    Set env var $($m.id) — see MANUAL-GATES-CHECKLIST P3" }
        "junction" { Write-Host "    Run: powershell -ExecutionPolicy Bypass -File scripts\pc-setup.ps1" }
    }
}
Write-Host ""

if ($InstallMissing) {
    Write-Host "Auto-installing missing winget/pip/npm packages..." -ForegroundColor Yellow
    foreach ($m in $results.missing) {
        switch ($m.kind) {
            "winget" {
                Write-Host "  Installing winget: $($m.id)" -ForegroundColor Cyan
                winget install --id $m.id -e --accept-package-agreements --accept-source-agreements --silent
            }
            "pip" {
                Write-Host "  Installing pip: $($m.id)" -ForegroundColor Cyan
                pip install --user $m.id
            }
            "npm" {
                Write-Host "  Installing npm: $($m.id)" -ForegroundColor Cyan
                npm install -g $m.id
            }
        }
    }
    Write-Host ""
    Write-Host "Re-run verify-deps.ps1 to confirm." -ForegroundColor Yellow
}

exit 1
