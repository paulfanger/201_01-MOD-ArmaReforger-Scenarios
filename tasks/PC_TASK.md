# PC Task — Task 007-CS: Empirical Cheatsheet + Sanity-Check (kurz, CS-kompatibel)

STATUS: PENDING
TASK_ID: 007-CS
TURN_ID: 6
PHASE: 2
TYPE: documentation_capture + headless_sanity
NOTE: User spielt weiter CS. KEINE GUI-Launches, KEINE Screenshots.
      GUI Smoke wartet auf Task 008 (post-CS, "ready für GUI smoke").

## Kontext

Task 006-CS lieferte:
- ✅ pc-setup.ps1 fix verifiziert (kein Parse-Error mehr)
- ✅ DRY pattern erfolgreich demonstriert (hash 1AB7CCED395B508F, 3× cleanup+recopy)
- ✅ Re-validate 3/3 PASS (DRY hat nichts kaputt gemacht)
- ✅ Sonnet 4.6 keine Qualitäts-Differenz für structured headless
- ✅ Turn-Budget: 1.25 min von 15 min (sehr effizient)

Mac hat 3 PC-Qs beantwortet:
1. **Reflection naming formalisiert**: `logs/reflection-turn-<N>-<side>.md` (siehe RELAY_PROTOCOL)
2. **PowerShell-Quoting-Rule dokumentiert**: PC_AGENT_BRIEF neue Sektion "PowerShell-Quoting Pitfalls"
3. **Task 008 GUI smoke**: wartet auf User-Signal post-CS

Diese Task ist sehr klein (~2 min): pull updates, validiere Empirie-Wissen, schreib
einen PC-Cheatsheet, push.

## Phase A (Two-Phase Reception)

⚙️ DO Items: **0**. Direct zu Phase C.

## Phase C — Steps (alle headless)

### Step 1 — Sync + STATE + Reflection lesen

```powershell
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
cd $repo
git pull --rebase

# Read Mac reflection-turn-5-mac.md if exists (new naming convention)
if (Test-Path "logs\reflection-turn-5-mac.md") {
    Get-Content "logs\reflection-turn-5-mac.md"
} elseif (Test-Path "logs\reflection-turn-5.md") {
    Get-Content "logs\reflection-turn-5.md"  # old naming, still valid
}

# Update STATE
$state = @{
    turn_id = 6
    owner = "pc"
    phase = "PHASE_C_EXEC"
    started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    pending_do = @()
    pending_exec = @(
        @{ id="exec-1"; desc="Read Mac doc updates (RELAY + PC_AGENT_BRIEF)"; status="queued" }
        @{ id="exec-2"; desc="Write playbook/CHEATSHEET-PC.md with empirical learnings"; status="queued" }
        @{ id="exec-3"; desc="Quick sanity re-validate (just night-recon, fast check)"; status="queued" }
        @{ id="exec-4"; desc="Audit + reflection-turn-6-pc.md + push"; status="queued" }
    )
    loop_signals = @()
    notes = "CS still running. Headless-only. Cheatsheet capture from PC empirical knowledge."
} | ConvertTo-Json -Depth 5
$state | Set-Content "tasks\STATE.json" -Encoding UTF8

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
"{`"t`":`"$((Get-Date -Format 's')+'Z')`",`"kind`":`"start`",`"turn_id`":6,`"task_id`":`"007-CS`"}" | Add-Content "logs\pc-events-task007cs-$ts.jsonl"
```

### Step 2 — Read Mac doc updates

Lies (2 Sätze Summary je File):
1. `playbook/RELAY_PROTOCOL.md` — neue Sektion "Reflection per turn" mit Naming-Convention
2. `PC_AGENT_BRIEF.md` — neue Sektion "PowerShell-Quoting Pitfalls"

Bestätige im Result dass beide gefunden + verstanden.

### Step 3 — Write playbook/CHEATSHEET-PC.md (deine Empirie)

Du hast jetzt empirisches Wissen aus 6 Turns. Schreib einen Cheatsheet aus PC-Perspektive
mit dem was funktioniert (validated) vs. was nicht funktioniert (disconfirmed). Format:

```markdown
# PC Cheatsheet — Arma Reforger Workbench on Windows

> Stand: 2026-05-20
> Source: empirical learnings from Tasks 001-007 (PC-side)

## Verified Working ✅

### Steam install via CLI
- `Start-Process "steam://install/<AppID>"` — Steam-Dialog opens, user clicks Install
- App-IDs: Game=1874880, Tools=1874910 (NOT 1874881 as old docs claim)

### Workbench-Diag executable
- Pfad: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe`
- Version 1.6.0.119 (Stand 2026-01-23)
- NICHT direkt im Tools-Ordner — im Sub-Folder `Workbench\`
- Diag-Variante: mehr crash-info als plain Workbench, sonst funktional identisch

### Vanilla addon junctions (one-time setup)
- Workbench-Diag braucht `core` + `data` als findable addons
- Setup: `scripts/pc-setup.ps1` (PowerShell-native New-Item -Junction)
- Lokationen:
  - `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_core`
  - `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_data`

### Validate compile-gate (headless, no GUI)
- CLI: `WorkbenchDiag.exe -gproj "X.gproj" -validate -wbSilent -exitAfterInit -logsDir "Y"`
- Pass: 0 Fatal + 0 Error im console.log
- Dauer: ~6s pro Mission
- Exit-Code: UNRELIABLE — use log-pattern matching

### File paths (Windows post-2024)
- Addons: `%USERPROFILE%\Documents\my games\ArmaReforger\addons\` (NOT %LOCALAPPDATA%)
- Workbench Logs: `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\logs\logs_<TS>\`
- Game AppData: `%USERPROFILE%\Documents\my games\ArmaReforger\`

### Screenshot (native PowerShell, no install)
```powershell
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$bmp = New-Object Drawing.Bitmap [width],[height]
# ... see PC_AGENT_BRIEF
```

## Disconfirmed Empirically ❌

### World-load smoke test via CLI
- `-load "$Addon:Worlds/X.ent" -wbSilent -exitAfterInit` — does NOT trigger world load
- Workbench-Diag 1.6.0.119 exited clean nach Engine-Init in ~5s ohne Entities-Load
- Alternatives: (a) Workbench-Plugin (pseudocode skeleton only), (b) GUI+Screenshot,
  (c) Linux dedi -listScenarios
- Status: research/06 Section B labelled DISCONFIRMED 2026-05-20

### `Author` keyword in addon.gproj
- Enfusion Schema kennt das nicht — `-validate` fails mit "Unknown keyword 'Author'"
- Fix: removed from gproj.py template + alle 3 mission outputs (commit 011f068)
- Attribution lebt in DISCLOSURE.md

### Exit codes from Workbench-Diag
- Empty exit-code bei success UND failure
- Switch zu log-pattern matching (siehe research/06 success heuristic)

## PowerShell Pitfalls (siehe PC_AGENT_BRIEF)

### Variable vor Colon
- `"$mission:path"` → "<mission-drive>:path" attempt
- `"${mission}:path"` ✓ or `"$($mission):path"` ✓

### Embedded quotes für cmd.exe
- Vermeiden, PowerShell-native nehmen (z.B. New-Item -Junction statt mklink)

### Backtick-n in double-quoted strings
- ⚠️ kann parse-error werfen
- ✅ separate `Write-Output ""` + `Write-Output "..."`

## Anti-Patterns (heilig)

- ❌ Mission-Files eigenmächtig ändern (Mac-Designer territory)
- ❌ User klicken lassen wenn ui-tester + loop-detector verfügbar sind
- ❌ Exit-Code als Pass/Fail-Signal nehmen (UNRELIABLE)
- ❌ `-Author`-keyword wieder in gproj einfügen
- ❌ `-load $A:X.ent -wbSilent` als smoke (disconfirmed)

## Recovery / Cleanup

### Junctions weg
```powershell
cmd /c rmdir "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_core"
cmd /c rmdir "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_data"
```

### Workbench/Game-Prozesse killen
```powershell
Get-Process | Where-Object { $_.ProcessName -like "*Workbench*" -or $_.ProcessName -like "*ArmaReforger*" } | Stop-Process -Force
```

### Mission-Addons löschen (vor DRY-Recopy)
- Self-approve OK weil reversibel (Source liegt im Repo: missions/<id>/output)
- Verwende `Remove-Item -Recurse -Force` (oder DRY-Pattern mit Hash für Audit-Trail)
```

Speicher als `playbook/CHEATSHEET-PC.md`.

### Step 4 — Quick Sanity Re-Validate (nur night-recon, fast)

```powershell
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"
$gproj = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons\ai_night-recon-everon\addon.gproj"
$logDir = "$repo\logs\sanity-validate-task007cs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$proc = Start-Process -FilePath $diag -ArgumentList @(
    "-gproj", "`"$gproj`"",
    "-validate",
    "-wbSilent",
    "-exitAfterInit",
    "-logsDir", "`"$logDir`""
) -PassThru -NoNewWindow

$waitSec = 0
while (-not $proc.HasExited -and $waitSec -lt 20) {
    Start-Sleep -Seconds 2
    $waitSec += 2
}

$console = Get-ChildItem "$logDir\logs_*\console.log" -Recurse | Sort-Object LastWriteTime -Desc | Select-Object -First 1
$content = if ($console) { Get-Content $console.FullName -Raw } else { "" }
$fatals = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(F\):")).Count
$errors = ([regex]::Matches($content, "(?m)^(WORLD|ENGINE|SCRIPT)\s+\(E\):")).Count
$verdict = if (($fatals -eq 0) -and ($errors -eq 0)) {"PASS"} else {"FAIL"}

Write-Output "Sanity re-validate (night-recon): $verdict · Fatal=$fatals · Error=$errors"
```

Erwartung: PASS (CI-gate ist stabil, 4× in Folge jetzt).

### Step 5 — Audit + Reflection + Push

```powershell
# Auditor: CHEATSHEET-PC.md exists + sanity PASS + reflection-turn-6-pc.md exists
# Reflection (NEUE Naming-Convention)
$reflectionPath = "$repo\logs\reflection-turn-6-pc.md"
# ... schreib Turn-6 reflection mit Standard-Struktur

cd $repo
$state = Get-Content "tasks\STATE.json" -Raw | ConvertFrom-Json
$state.phase = "PHASE_D_RETURN"
$state | ConvertTo-Json -Depth 5 | Set-Content "tasks\STATE.json" -Encoding UTF8

git pull --rebase
git add playbook/CHEATSHEET-PC.md tasks/PC_RESULT.md tasks/STATE.json logs/
git commit -m "PC: Task 007-CS -- empirical cheatsheet + sanity (CS-compat)"
git push
```

---

## Pause-Conditions

- Sanity re-validate FAIL → bug-fixer + STOP (würde bedeuten der Validate-Gate ist plötzlich brüchig — wäre Big Deal)
- turn_time_budget (10 min — task ist kurz) → STOP

---

## Erwartete Dauer

- Steps 1-2: 30s
- Step 3 (Cheatsheet schreiben): 1-2 min (länger weil substantielle Doc)
- Step 4 (Sanity Validate): 15s
- Step 5 (Audit + reflection + push): 30s

**Total: ~3 min, headless durchgängig, CS bleibt ungestört.**

PAUSE FLAG: nein.

---

## NEXT

Wenn User CS beendet → tippt im Mac-Chat "GUI smoke go" → Mac compiles Task 008 mit
GUI-Workbench-Launch + Screenshots + multimodal ui-tester classify (ursprünglich
geplant für Task 006, deferred zu post-CS).
