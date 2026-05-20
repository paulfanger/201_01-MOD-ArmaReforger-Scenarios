# PC Task — Task 007b-CS: CHEATSHEET Section 5 + Task 008 Draft Review (kurz, CS-kompatibel)

STATUS: PENDING
TASK_ID: 007b-CS
TURN_ID: 7
PHASE: 2
TYPE: cheatsheet_extension + draft_review + headless_sanity
NOTE: User spielt CS weiter. KEINE GUI-Launches. Task 008 ist als DRAFT pre-staged
      (tasks/PC_TASK_008_DRAFT.md) — wartet auf "ready für GUI smoke" Signal post-CS.

## Kontext

Task 007-CS done (commit f5f60c9). PC schlug 2 Verbesserungen vor:

1. **CHEATSHEET-PC.md Section 5** ergänzen ("GPU + Steam-Library Quickref" mit
   PC-specific Info wie RX 5700 XT, 8GB VRAM, E: drive not mounted)
2. **Task 008 Step 0 = CS-Kill** vor GUI-Launch (GPU-Konflikt-Prevention)

Mac hat beide Vorschläge akzeptiert:
- (1) Du selbst (PC) ergänzt Section 5 in CHEATSHEET-PC.md (du kennst dein HW besser)
- (2) Mac hat Task 008 als DRAFT mit CS-Kill als Phase B + Step 0 Safety-Net pre-staged
  in `tasks/PC_TASK_008_DRAFT.md`. Du reviewst das, ich aktivier's wenn User ready.

Diese Task ist sehr klein (~3 min): Cheatsheet-Ergänzung + Draft-Review + sanity-validate + push.

## Phase A (Two-Phase Reception)

⚙️ DO Items: **0**. Direct zu Phase C.

## Phase C — Steps (alle headless)

### Step 1 — Sync + STATE + Mac-Reflection lesen

```powershell
$repo = "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios"
cd $repo
git pull --rebase

if (Test-Path "logs\reflection-turn-7-mac.md") {
    Get-Content "logs\reflection-turn-7-mac.md"
}

$state = @{
    turn_id = 7
    owner = "pc"
    phase = "PHASE_C_EXEC"
    started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    pending_do = @()
    pending_exec = @(
        @{ id="exec-1"; desc="Read Task 008 DRAFT for review"; status="queued" }
        @{ id="exec-2"; desc="Extend CHEATSHEET-PC.md with Section 5 (GPU + Steam-Library)"; status="queued" }
        @{ id="exec-3"; desc="Sanity re-validate (night-recon, 6th in row)"; status="queued" }
        @{ id="exec-4"; desc="Audit + reflection-turn-7-pc.md + push"; status="queued" }
    )
    loop_signals = @()
    notes = "CS still running. Final headless prep before post-CS GUI smoke task 008."
} | ConvertTo-Json -Depth 5
$state | Set-Content "tasks\STATE.json" -Encoding UTF8

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
"{`"t`":`"$((Get-Date -Format 's')+'Z')`",`"kind`":`"start`",`"turn_id`":7,`"task_id`":`"007b-CS`"}" | Add-Content "logs\pc-events-task007bcs-$ts.jsonl"
```

### Step 2 — Read Task 008 DRAFT für Review

```powershell
Get-Content "$repo\tasks\PC_TASK_008_DRAFT.md"
```

In Result-Template berichten:
- Stimmt der CS-Kill Step 0 mit deiner Empfehlung überein?
- Sind die GUI-Steps (3-7) reasonable?
- Fehlt etwas Critical (z.B. fehlende Pre-flight-Check, Edge-Case)?
- Würdest du etwas anders machen?

Diese Review hilft Mac den DRAFT vor Aktivierung zu verbessern.

### Step 3 — CHEATSHEET-PC.md Section 5 ergänzen

Lies aktuelles `playbook/CHEATSHEET-PC.md`, ergänze am Ende eine neue Sektion:

```markdown
## GPU + Steam-Library Quickref (PC-specific)

### Hardware
- GPU: <model + VRAM>
- CPU: <model>
- RAM: <amount>
- OS: Windows 11 Home (build 26200)

### Steam-Libraries
- Primary: `C:\Program Files (x86)\Steam` (Arma Reforger Game + Tools hier installiert)
- Secondary: <z.B. `E:\SteamLibrary` falls vorhanden — Status: not currently mounted>

### Concurrency
- ⚠️ GPU shared between Workbench + actively-played games → GUI Workbench-Tests
  brauchen exclusive GPU-Access (kill CS/AR/anderes Spiel vor Task 008 GUI-Launch)
- Headless `-wbSilent` Tasks (validate/compile) sind GPU-tolerant: laufen parallel zu Games ok
- Screenshot-Capture greift Primary-Monitor: bei multi-monitor adjust target

### Workbench-Specific
- Erste Workbench-Start nach Game-Update: kann länger dauern (asset reimport)
- Workbench-Diag verbraucht ~117 MB RAM idle, ~500 MB beim World-Load
```

Fülle Hardware-Werte aus deinem System ein (Get-WmiObject Win32_VideoController, Get-CimInstance Win32_Processor, etc.):

```powershell
Write-Output "=== GPU ==="
Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | Format-List
Write-Output "=== CPU ==="
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, MaxClockSpeed | Format-List
Write-Output "=== RAM ==="
$ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
Write-Output "Total: $([math]::Round($ram,1)) GB"
Write-Output "=== Steam Libraries ==="
Get-Content "C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf" -ErrorAction SilentlyContinue | Select-String "path"
```

Dann schreib die Section 5 mit den echten Werten.

### Step 4 — Sanity Re-Validate (night-recon-everon, 6th in Folge)

Standard pattern. ~15s. Erwartung: PASS (CI-Gate-stability streak weiterführen).

### Step 5 — Audit + Reflection + Push

- Auditor: CHEATSHEET-PC.md hat jetzt Section 5 + sanity PASS + reflection-turn-7-pc.md
- Reflection (Naming: `logs/reflection-turn-7-pc.md`)
- STATE → PHASE_D_RETURN
- Push

---

## Pause-Conditions

- Sanity-validate FAIL (6th in row would be FAIL) → STOP, bug-fixer (würde grosses
  Stability-Regression sein)
- turn_time_budget (10 min) → STOP

---

## Erwartete Dauer

- Steps 1-2: 30s
- Step 3 (Section 5 schreiben mit HW-Discovery): 1-2 min
- Step 4 (Sanity Validate): 15s
- Step 5 (Audit + reflection + push): 30s

**Total: ~3 min, headless durchgängig.**

PAUSE FLAG: nein.

---

## NEXT

Wenn User CS beendet + tippt **"ready für GUI smoke"** oder **"Task 008 go"** im Mac-Chat:
- Mac liest dein Review von Task 008 DRAFT
- Mac integriert deine Anmerkungen (falls vorhanden)
- Mac promotet DRAFT → `tasks/PC_TASK.md` (Task 008 aktiviert)
- Phase A asks dich "ist CS zu?" → Phase B verify → Phase C GUI Smoke

Bis dahin: kein weiterer Task-Push erwartet von Mac, außer User ändert Plan.
