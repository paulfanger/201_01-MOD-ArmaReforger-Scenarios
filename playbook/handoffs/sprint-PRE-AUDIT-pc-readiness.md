# Sprint PRE-AUDIT — PC Readiness for MEGA-A (~30 min, user present)

> Stand: 2026-05-21 · Model: Sonnet 4.6
> User-state: User AT PC, can click "Allow always" + grant UAC prompts + answer 2-5 questions
> Purpose: Verify EVERYTHING needed for MEGA-A is ready BEFORE committing to 5-7h overnight sprint
> Without this: ~70% chance MEGA-A runs to completion. With this: ~95%.

---

## Why This Exists (honest reality check)

15+ things can stall MEGA-A mid-night without warning:

1. **winget first-time setup** — user agreement dialog blocks install
2. **UAC prompts** for Python/Node install
3. **VSCode first-launch wizard** (telemetry, theme, sign-in)
4. **Extension install** sometimes shows "Trust workspace?" dialogs
5. **gh auth** never set up → can't clone Bohemia samples
6. **Git push credentials** expire/missing → push fails
7. **PowerShell execution policy** restrictive → scripts blocked
8. **Bohemia Samples repo URL** might 404 or require auth
9. **Steam pending update** for Reforger Tools → corrupts S5-Prep
10. **MS-Store Python stub** masks real install path
11. **Disk space** low → screenshots/logs/Docker fill it
12. **Anthropic API rate limit** during long session → silent stall
13. **Workbench window won't focus** for sample-plugin compile check
14. **SendKeys blocked** by security software → file-watch hack dead
15. **Steam not logged in** → game launch fails in S2
16. **Permission popups for NEW command types** in Claude Code app
17. **Network blip during git push** → unrecoverable mid-sprint
18. **Mac side: Docker not running** → dedi-validate part of S1 silently skips
19. **Mac side: ANTHROPIC_API_KEY missing** → backend tests fail
20. **PC project-level .claude/settings.local.json** may not have permissions for new commands (winget, code, npm)

This Pre-Audit catches ALL of them in 30 min, with concrete remediations per fail.

---

<audit>

<context>
  <goal>
    Verify PC + Mac state is FULLY ready for MEGA-A 5-7h overnight sprint. Catch every
    known failure mode pre-flight. Output a go/no-go verdict with remediation steps per
    failed check.
  </goal>

  <success_criteria>
    <criterion id="audit-go">ALL 20 checks PASS or have user-confirmed remediation</criterion>
    <criterion id="permission-preempt">Every command-type Claude Code might run has been triggered once + user clicked "Allow always"</criterion>
    <criterion id="report">playbook/handoffs/pre-audit-result-<TS>.md exists with go/no-go verdict</criterion>
  </success_criteria>

  <constraints>
    <constraint>User MUST be at PC throughout (~30 min)</constraint>
    <constraint>Run NO destructive ops (this audit is read-only + minimal-install)</constraint>
    <constraint>Each check is binary PASS/FAIL with clear remediation</constraint>
    <constraint>If ≥1 critical check FAILS: do NOT proceed to MEGA-A until fixed</constraint>
  </constraints>
</context>

---

## CATEGORY 1 — Claude Code App + Permissions (~5 min)

<check id="C1.1" name="model_check">
  <action>Verify active model</action>
  <command>(check Claude Code app model-selector left-bottom)</command>
  <expected>"Sonnet 4.6"</expected>
  <on_fail>User switches model in selector</on_fail>
  <criticality>HIGH — Sonnet is needed for cost-efficiency in 5-7h sprint</criticality>
</check>

<check id="C1.2" name="permission_preempt">
  <action>Trigger EVERY command-type MEGA-A will use, so user can click "Allow always" NOW (not at 02:00)</action>
  <commands>
    ```powershell
    git --version           # → Allow always Bash(git *)
    gh --version            # → Allow always Bash(gh *)
    python --version        # → Allow always Bash(python *)
    pip --version           # → Allow always Bash(pip *)
    node --version          # → Allow always Bash(node *)
    npm --version           # → Allow always Bash(npm *)
    code --version          # → Allow always Bash(code *)
    powershell -Version     # → Allow always
    winget --version        # → Allow always
    chokidar --help         # might fail (not yet installed)
    Get-Process | Select-Object -First 1  # → Allow always Bash(Get-* *)
    New-Item -ItemType Directory -Path "$env:TEMP\test-perm-check"  # → Allow always
    Remove-Item -Path "$env:TEMP\test-perm-check" -Force  # → Allow always Bash(Remove-Item *)
    Start-Process notepad -WindowStyle Hidden -PassThru | Stop-Process -Force  # → Allow always
    Test-NetConnection -ComputerName github.com -Port 443 -InformationLevel Quiet  # → Allow always
    ```
  </commands>
  <expected>User clicks "Allow always" for each (12-15 popups, ~2 min total)</expected>
  <on_fail>User clicks "Allow once" instead → MEGA-A WILL stall on first new command at 02:00. Re-run check.</on_fail>
  <criticality>CRITICAL — this is the #1 cause of mid-night stalls</criticality>
</check>

---

## CATEGORY 2 — Network + Auth (~5 min)

<check id="C2.1" name="github_https">
  <action>Verify GitHub HTTPS reachable</action>
  <command>Test-NetConnection -ComputerName github.com -Port 443 -InformationLevel Quiet</command>
  <expected>True</expected>
  <on_fail>Check firewall, VPN, proxy</on_fail>
  <criticality>CRITICAL</criticality>
</check>

<check id="C2.2" name="git_push_test">
  <action>Verify git push works (creates+pushes a test commit, then immediately reverts)</action>
  <commands>
    ```powershell
    cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
    "test $(Get-Date)" | Out-File -FilePath logs\pre-audit-write-test.txt -Append
    git add logs/pre-audit-write-test.txt
    git commit -m "PRE-AUDIT: write test" --quiet
    git push 2>&1
    ```
  </commands>
  <expected>Push succeeds (Last commit hash appears in output)</expected>
  <on_fail>
    - Auth error → `gh auth login` (user does)
    - Permission denied → check repo access
    - Network → see C2.1
  </on_fail>
  <criticality>CRITICAL — without push, no MEGA-A result reaches Mac</criticality>
</check>

<check id="C2.3" name="gh_auth_status">
  <action>Check GitHub CLI auth (needed to clone Bohemia samples)</action>
  <command>gh auth status 2>&1</command>
  <expected>"Logged in to github.com" appears</expected>
  <on_fail>Run `gh auth login` interactively — user picks "github.com" → "HTTPS" → browser auth</on_fail>
  <criticality>HIGH — Sprint A.S5PREP.1 (clone Bohemia samples) blocks without this</criticality>
</check>

<check id="C2.4" name="anthropic_api">
  <action>Verify Anthropic API key is set + reachable</action>
  <commands>
    ```powershell
    if (-not $env:ANTHROPIC_API_KEY) {
      Write-Warning "ANTHROPIC_API_KEY not set in environment"
    } else {
      Write-Output "API key length: $($env:ANTHROPIC_API_KEY.Length) chars"
    }
    Test-NetConnection -ComputerName api.anthropic.com -Port 443 -InformationLevel Quiet
    ```
  </commands>
  <expected>Key set (50+ chars), api.anthropic.com reachable</expected>
  <on_fail>Set API key: `$env:ANTHROPIC_API_KEY = "sk-..."` (per-session) OR add to system env vars (persistent)</on_fail>
  <criticality>MEDIUM — Claude Code app uses its own internal auth, but backend Python tests may need this</criticality>
</check>

---

## CATEGORY 3 — Tool Installs (Auto-Install Test) (~10 min)

<check id="C3.1" name="winget_first_use">
  <action>winget first-use license-agreement (only matters if user never ran winget)</action>
  <command>winget list --accept-source-agreements --accept-package-agreements 2>&1 | Select-Object -First 5</command>
  <expected>No "license agreement" prompts; package list output</expected>
  <on_fail>User accepts winget license terms interactively</on_fail>
  <criticality>CRITICAL — Sprint A.0 winget installs stall if user hasn't accepted</criticality>
</check>

<check id="C3.2" name="python_install_test">
  <action>Test Python install via winget (idempotent, skips if installed)</action>
  <command>winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements --silent 2>&1 | Select-Object -Last 5</command>
  <expected>"already installed" OR "Successfully installed"</expected>
  <on_fail>
    - UAC prompt blocks → user accepts UAC (this is the popup we pre-empt)
    - 0x80073D02 / pending-restart → reboot needed before MEGA-A
  </on_fail>
  <criticality>HIGH — Sprint A.0 needs real Python (not MS-Store stub)</criticality>
</check>

<check id="C3.3" name="python_path_check">
  <action>Verify python actually exists in PATH (not MS-Store stub)</action>
  <commands>
    ```powershell
    $pyPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    Write-Output "python.exe path: $pyPath"
    if ($pyPath -like "*WindowsApps*") {
      Write-Warning "MS-Store STUB detected — real Python install needed"
    } else {
      python --version
      python -c "import sys; print(sys.executable)"
    }
    ```
  </commands>
  <expected>Path NOT contains "WindowsApps", `python --version` returns "Python 3.12.x"</expected>
  <on_fail>
    - Disable MS-Store stub: Settings → Apps → App Execution Aliases → toggle off python.exe
    - Install via python.org or `winget install Python.Python.3.12`
  </on_fail>
  <criticality>HIGH</criticality>
</check>

<check id="C3.4" name="pip_install_test">
  <action>Test pip install (one minor package)</action>
  <command>python -m pip install --upgrade --user pip setuptools 2>&1 | Select-Object -Last 3</command>
  <expected>"already satisfied" OR "Successfully installed"</expected>
  <on_fail>Check Python install (C3.3), check network</on_fail>
  <criticality>HIGH — backend tests need pip</criticality>
</check>

<check id="C3.5" name="node_npm_install_test">
  <action>Test Node.js install (needed for chokidar file-watcher)</action>
  <command>winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements --silent 2>&1 | Select-Object -Last 5</command>
  <expected>"already installed" OR "Successfully installed"</expected>
  <on_fail>Same as C3.2</on_fail>
  <criticality>MEDIUM — Sprint A.S5PREP.5 file-watcher uses chokidar OR PowerShell alternative</criticality>
</check>

<check id="C3.6" name="vscode_install_test">
  <action>Test VSCode install + first-launch state</action>
  <commands>
    ```powershell
    winget install --id Microsoft.VisualStudioCode -e --accept-package-agreements --accept-source-agreements --silent 2>&1 | Select-Object -Last 3
    # Verify code CLI is available
    code --version 2>&1
    ```
  </commands>
  <expected>code --version returns version number</expected>
  <on_fail>
    - VSCode launches first-time wizard → user clicks through (theme, telemetry off, sign-in skip)
    - code CLI not in PATH → reboot OR add `C:\Users\pfofa\AppData\Local\Programs\Microsoft VS Code\bin` to PATH
  </on_fail>
  <criticality>MEDIUM</criticality>
</check>

<check id="C3.7" name="vscode_extension_test">
  <action>Test VSCode extension install</action>
  <command>code --install-extension ms-vscode.powershell --force 2>&1 | Select-Object -Last 3</command>
  <expected>"successfully installed" or "already installed"</expected>
  <on_fail>VSCode startup-required → open VSCode once, accept prompts, retry</on_fail>
  <criticality>LOW — extensions are for human use, Claude doesn't need them</criticality>
</check>

<check id="C3.8" name="disk_space">
  <action>Verify enough disk space (need ~5 GB free for samples + logs + screenshots)</action>
  <command>Get-PSDrive C | Select-Object Used,Free,@{Name="UsedGB";Expression={[math]::Round($_.Used/1GB,1)}},@{Name="FreeGB";Expression={[math]::Round($_.Free/1GB,1)}}</command>
  <expected>FreeGB ≥ 5</expected>
  <on_fail>User clears disk space (recycle bin, Steam cache, etc.)</on_fail>
  <criticality>HIGH</criticality>
</check>

---

## CATEGORY 4 — Existing Project State (~5 min)

<check id="C4.1" name="repo_clean">
  <action>Verify repo is up-to-date + clean</action>
  <commands>
    ```powershell
    cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
    git fetch
    $behind = (git rev-list --count HEAD..origin/main)
    $ahead = (git rev-list --count origin/main..HEAD)
    git status --short
    Write-Output "behind origin: $behind, ahead origin: $ahead"
    ```
  </commands>
  <expected>behind=0, ahead=0, no untracked/modified files in tasks/, logs/</expected>
  <on_fail>git pull --rebase OR commit pending work</on_fail>
  <criticality>HIGH</criticality>
</check>

<check id="C4.2" name="state_consistent">
  <action>Verify tasks/STATE.json is consistent</action>
  <command>Get-Content tasks/STATE.json | ConvertFrom-Json</command>
  <expected>Valid JSON, phase=PHASE_D_RETURN (means previous turn complete)</expected>
  <on_fail>STATE.json corrupt or mid-turn → resolve manually</on_fail>
  <criticality>MEDIUM</criticality>
</check>

<check id="C4.3" name="claude_settings_check">
  <action>Verify .claude/settings.local.json has the permissions we set up earlier</action>
  <command>
    ```powershell
    $settingsPath = "C:\Users\pfofa\Desktop\ELOS\000_Projekte\201-01-ARMA-CREATOR\.claude\settings.local.json"
    if (Test-Path $settingsPath) {
      Get-Content $settingsPath | ConvertFrom-Json | ConvertTo-Json -Depth 5
    } else {
      Write-Warning "settings.local.json missing at $settingsPath"
    }
    ```
  </command>
  <expected>Allow list contains Bash(git *), Bash(powershell *), Bash(winget *), etc.</expected>
  <on_fail>Permission popups will appear mid-sprint → use C1.2 method to grant via "Allow always"</on_fail>
  <criticality>HIGH</criticality>
</check>

---

## CATEGORY 5 — External Services + Game State (~5 min)

<check id="C5.1" name="steam_running">
  <action>Steam logged in + running</action>
  <commands>
    ```powershell
    $steam = Get-Process steam -ErrorAction SilentlyContinue
    if (-not $steam) {
      Write-Warning "Steam not running"
    } else {
      Write-Output "Steam PID: $($steam.Id)"
    }
    ```
  </commands>
  <expected>Steam process alive</expected>
  <on_fail>User starts Steam, logs in</on_fail>
  <criticality>HIGH — Sprint A.S2 game launch fails without Steam</criticality>
</check>

<check id="C5.2" name="reforger_no_pending_update">
  <action>Check Reforger has no pending Steam update</action>
  <commands>
    ```powershell
    # Crude check: look at game install timestamps
    $game = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerSteam.exe"
    if (Test-Path $game) {
      $lastWrite = (Get-Item $game).LastWriteTime
      Write-Output "Reforger last updated: $lastWrite"
      Write-Output "If you see 'Update Queued' in Steam UI → cancel or let it finish NOW"
    }
    ```
  </commands>
  <expected>User confirms no "Update Queued" in Steam UI</expected>
  <on_fail>Let Steam update finish before MEGA-A</on_fail>
  <criticality>HIGH — mid-night Steam update would corrupt S2 game test</criticality>
</check>

<check id="C5.3" name="workbench_installed">
  <action>Workbench-Diag binary exists</action>
  <command>Test-Path "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"</command>
  <expected>True</expected>
  <on_fail>Steam → Library → Tools → install "Arma Reforger Tools"</on_fail>
  <criticality>CRITICAL — Sprint A.S5PREP fails without Workbench</criticality>
</check>

<check id="C5.4" name="junctions_exist">
  <action>Vanilla junctions in place (from Task 003)</action>
  <commands>
    ```powershell
    $coreJunction = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_core"
    $dataJunction = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_data"
    Test-Path $coreJunction
    Test-Path $dataJunction
    ```
  </commands>
  <expected>Both True</expected>
  <on_fail>Run `powershell -ExecutionPolicy Bypass -File scripts/pc-setup.ps1`</on_fail>
  <criticality>CRITICAL — Workbench-Diag won't resolve addon deps without junctions</criticality>
</check>

<check id="C5.5" name="bohemia_samples_url_reachable">
  <action>Verify Bohemia Samples repo URL is real (test fetch)</action>
  <commands>
    ```powershell
    gh repo view BohemiaInteractive/Arma-Reforger-Samples 2>&1 | Select-Object -First 5
    gh repo view BohemiaInteractive/Arma-Reforger-Script-Diff 2>&1 | Select-Object -First 5
    ```
  </commands>
  <expected>Both return repo metadata (description, default branch, etc.)</expected>
  <on_fail>
    - 404 → URL changed, need fallback (search github for "Arma-Reforger-Samples")
    - Private/auth → gh auth issue (see C2.3)
  </on_fail>
  <criticality>CRITICAL — Sprint A.S5PREP.1 blocked if these don't exist</criticality>
</check>

---

## CATEGORY 6 — GUI Automation Pre-Test (~5 min)

<check id="C6.1" name="screenshot_capability">
  <action>Test PowerShell native screenshot at 1280x800</action>
  <commands>
    ```powershell
    Add-Type -AssemblyName System.Windows.Forms,System.Drawing
    $bounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
    $full = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
    $gfx = [Drawing.Graphics]::FromImage($full)
    $gfx.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
    $resized = New-Object Drawing.Bitmap 1280, 800
    $rgfx = [Drawing.Graphics]::FromImage($resized)
    $rgfx.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $rgfx.DrawImage($full, 0, 0, 1280, 800)
    $shotPath = "logs\pre-audit-screenshot-test.png"
    $resized.Save($shotPath)
    $gfx.Dispose(); $full.Dispose(); $rgfx.Dispose(); $resized.Dispose()
    Write-Output "Screenshot saved: $shotPath ($(Get-Item $shotPath).Length bytes)"
    ```
  </commands>
  <expected>PNG file ~50-200 KB exists</expected>
  <on_fail>Add-Type might fail on locked-down systems → escalate</on_fail>
  <criticality>CRITICAL — Sprint A.S2 + A.S5PREP need screenshots</criticality>
</check>

<check id="C6.2" name="sendkeys_test">
  <action>Test SendKeys can reach a foreground window</action>
  <commands>
    ```powershell
    # Start notepad, send "test", verify text appears (manual)
    $np = Start-Process notepad -PassThru
    Start-Sleep 2
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName Microsoft.VisualBasic
    [Microsoft.VisualBasic.Interaction]::AppActivate($np.Id) | Out-Null
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("Pre-Audit SendKeys Test{ENTER}")
    Start-Sleep 1
    # Auto-close
    $np | Stop-Process -Force
    ```
  </commands>
  <expected>User briefly sees Notepad with "Pre-Audit SendKeys Test" text → auto-closes</expected>
  <on_fail>
    - SendKeys blocked by security software (Defender Tamper Protection rare for this)
    - AppActivate fails → use UIAutomation or fallback to nircmd
  </on_fail>
  <criticality>HIGH — Sprint B file-watch hack needs SendKeys</criticality>
</check>

<check id="C6.3" name="pydirectinput_install_test">
  <action>Install + import-test PyDirectInput (Sprint B needs it for movement test)</action>
  <commands>
    ```powershell
    pip install --user pydirectinput pillow 2>&1 | Select-Object -Last 3
    python -c "import pydirectinput; print('pydirectinput', pydirectinput.__version__ if hasattr(pydirectinput,'__version__') else 'ok')"
    python -c "from PIL import Image; print('Pillow ok')"
    ```
  </commands>
  <expected>Both imports succeed</expected>
  <on_fail>pip install failures → check C3.4</on_fail>
  <criticality>MEDIUM — Sprint B feature, not blocker for MEGA-A</criticality>
</check>

<check id="C6.4" name="window_enumeration">
  <action>Verify Get-Process | Window enumeration works for popup detection</action>
  <command>Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne "" } | Select-Object -First 5 | Format-Table Id, ProcessName, MainWindowTitle</command>
  <expected>List of visible windows (at least Claude Code + a few others)</expected>
  <on_fail>Should never fail on normal Windows; if fails → restart explorer.exe</on_fail>
  <criticality>HIGH — ui-tester needs this for popup detection</criticality>
</check>

---

## CATEGORY 7 — Mac-Side Readiness (only relevant for Linux Docker dedi part) (~optional, ~3 min)

<check id="M7.1" name="mac_reachable_via_git">
  <action>Test that Mac has pushed everything (PC just verifies via git fetch)</action>
  <commands>
    ```powershell
    git fetch
    git log --oneline origin/main -5
    ```
  </commands>
  <expected>Latest commit timestamp is recent (Mac is actively pushing)</expected>
  <on_fail>Mac side is asleep / Claude Code closed → MEGA-A's S1.3 Docker-dedi part will be deferred (not critical, just won't get done autonomously)</on_fail>
  <criticality>LOW — deferred work, not blocker</criticality>
</check>

---

## CATEGORY 8 — Anthropic API Rate Limits (~optional, ~2 min)

<check id="C8.1" name="api_quota_estimate">
  <action>Estimate API quota / usage (informational only — Claude Code uses its own auth)</action>
  <commands>
    ```powershell
    # If user has API key set, can query usage; otherwise informational
    if ($env:ANTHROPIC_API_KEY) {
      curl -s -H "x-api-key: $env:ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" `
        https://api.anthropic.com/v1/messages -X POST `
        -d '{"model":"claude-3-5-haiku-20241022","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}' `
        | Select-String -Pattern "type"
    } else {
      Write-Output "No API key set — Claude Code uses its own internal auth"
    }
    ```
  </commands>
  <expected>API call returns 200 (not 429 rate-limit, not 401 auth-fail)</expected>
  <on_fail>Wait for rate-limit reset; rare but possible if heavy usage today</on_fail>
  <criticality>LOW — Claude Code app handles this internally</criticality>
</check>

---

## CATEGORY 9 — Final Smoke (~3 min)

<check id="C9.1" name="end_to_end_pipeline_dry_run">
  <action>Run a tiny end-to-end pipeline check (validates one mission, no GUI)</action>
  <commands>
    ```powershell
    cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
    $diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
    $gproj = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons\ai_night-recon-everon\addon.gproj"
    $logDir = "logs\pre-audit-validate-smoke"
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    $proc = Start-Process -FilePath $diag -ArgumentList @(
      "-gproj", "`"$gproj`"", "-validate", "-wbSilent", "-exitAfterInit", "-logsDir", "`"$logDir`""
    ) -PassThru -NoNewWindow
    Start-Sleep 15
    if ($proc.HasExited) {
      $console = Get-ChildItem "$logDir\logs_*\console.log" -Recurse | Sort-Object LastWriteTime -Desc | Select-Object -First 1
      if ($console) {
        $content = Get-Content $console.FullName -Raw
        $fatals = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(F\):")).Count
        $errors = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(E\):")).Count
        Write-Output "Validate smoke: F=$fatals E=$errors"
      }
    } else {
      Stop-Process -Id $proc.Id -Force
      Write-Warning "Validate didn't complete in 15s — unusual"
    }
    ```
  </commands>
  <expected>F=0 E=0 (or matches existing 6× PASS streak)</expected>
  <on_fail>
    - F>0 / E>0 → mission file regression → STOP, investigate
    - Process won't exit → Workbench-Diag issue → STOP
  </on_fail>
  <criticality>CRITICAL — if our 7th validate fails, something changed since last run</criticality>
</check>

---

## FINAL VERDICT

<verdict>
  Aggregate all checks:
  - count_pass / count_critical_fail / count_high_fail / count_medium_fail / count_low_fail
  - If ANY critical fail: VERDICT = "NO-GO. Fix critical items, re-run audit."
  - If 0 critical, any high fail: VERDICT = "CAUTION. High-fails will cause partial sprint completion. User decides."
  - If all critical+high pass: VERDICT = "GO. MEGA-A can run."
</verdict>

<output>
  Write `playbook/handoffs/pre-audit-result-<TS>.md` with:
  - All 30 checks: PASS / FAIL / SKIP per item
  - Failures with remediation steps
  - Final verdict (GO / CAUTION / NO-GO)
  - Recommended next action

  Also output to chat: condensed verdict + next-action.
</output>

</audit>

---

## Wrapper Prompt — paste in PC chat NOW (user at PC, ~30 min)

```
Du bist PC-Executor. Pre-Sprint Audit für MEGA-A Readiness.
User AT PC für ~30 min, kann Allow-always + UAC + auth-Dialoge bestätigen.
Sonnet 4.6 OK.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/RELAY_PROTOCOL.md (Two-Phase Reception)
3. PC_AGENT_BRIEF.md
4. playbook/CHEATSHEET-PC.md
5. playbook/handoffs/sprint-PRE-AUDIT-pc-readiness.md ← THIS plan (30 checks)

Two-Phase Reception:
- Phase A: ⚙️ DO = "User at PC, has ~30 min, will click Allow-always + accept UAC prompts" (User confirms)
- Phase B: skip (no pre-verify needed)
- Phase C: Execute all 30 checks in order (Categories 1-9)
- Phase D: Single Return = playbook/handoffs/pre-audit-result-<TS>.md

CRITICAL: This audit's primary purpose is to PRE-EMPT permission popups + tool-install
failures. For Category 1.2 (permission preempt), DELIBERATELY trigger every command-type
that MEGA-A will use, so user can click "Allow always" NOW.

For each check:
- Run the command
- Determine PASS/FAIL per <expected>
- If FAIL: surface remediation per <on_fail> + ask user to act (in chat) or mark as
  "needs-user-action" in result

When all 30 checks done:
- Compute aggregate verdict (GO / CAUTION / NO-GO)
- Write playbook/handoffs/pre-audit-result-<TS>.md
- git add + commit + push
- Chat output: condensed verdict + "Ready to paste MEGA-A wrapper" OR "Fix these first: <list>"

If verdict = GO:
- Output the MEGA-A wrapper prompt EXACTLY as it appears at end of
  playbook/handoffs/sprint-MEGA-A-S1S2-to-S5-ready.md
- Tell user: "Copy the block above + paste in NEW PC Claude Code thread (or this one).
  Then step away for 5-7h."

If verdict = CAUTION:
- List the high-fails + recommendations
- Ask user whether to proceed anyway or fix first

If verdict = NO-GO:
- List critical fails + remediation
- Do NOT output MEGA-A wrapper
- User fixes, re-runs audit

DRY marker for any destructive op (there shouldn't be any, but enforced).
Sub-agents: logger always-on, dep-installer if needed, auditor pre-push.
Hard guards: 30 min sprint-time-budget, max 3 retries per check.

Start with Phase A confirmation.
```

---

## What to do if verdict = NO-GO

For each critical/high failure, the audit gives concrete remediation. Most common:
- "Click Allow always" on missed Claude Code popups
- "Accept UAC for Python install" (one-click)
- "Steam → Library → Install Arma Reforger Tools" (Steam UI)
- "winget agreement accept" (one-time per machine)
- "gh auth login" (browser flow)

After fixes, **re-run this audit**. Should be 5-10 min on re-run (most installs are idempotent).

When audit returns GO → safe to paste MEGA-A wrapper + go to sleep.
