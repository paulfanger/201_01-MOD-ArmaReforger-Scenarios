# Workbench CLI / Headless Testing — Verified Flags

> **Source:** Background research run (2026-05-20), cross-verified against
> BI Wiki, real `console.log` samples, and community docs.
> Status: GOLD. Use these flags in test pipelines.

---

## Binary

- `ArmaReforgerWorkbench.exe` — production
- `ArmaReforgerWorkbenchSteamDiag.exe` — diag/debug variant (use for testing; cannot mix with non-Diag)

## Critical Flags (verified)

| Flag | Purpose |
|---|---|
| `-gproj "path/to/Addon.gproj"` | Open specific addon, skip selection UI |
| `-load "path"` | Load file (use `.ent` for worlds, NOT `-world`) |
| `-wbSilent` | Headless — init engine + modules, no windows |
| `-exitAfterInit` | Exit once initialized (added 1.1.0) |
| `-validate [CONFIG]` | Compile gate — **exit code 0=success, -1=fail** |
| `-logsDir "path"` | Override log location (for deterministic CI) |
| `-logAppend` | Append vs new timestamped folder |
| `-plugin=NAME` | Run custom Enforce plugin (Phase 2 path) |
| `-noGameScriptsOnInit` | Skip game-script compile (faster) |
| `-buildData PC "outPath" [Addon]` | Per-platform data bake |

**No `-loadMission`, no `-headless`, no `-nogui` flag.** Headless = `-wbSilent` + `-exitAfterInit`.

---

## Log Paths (Windows)

```
%USERPROFILE%\Documents\My Games\ArmaReforgerWorkbench\logs\logs_<DATE>_<TIME>\
  ├── console.log
  ├── script.log
  ├── error.log
  └── .backend
```

OneDrive variant: `Documents` might be `OneDrive\Documents`.

Game/Dedi logs: `Documents\My Games\ArmaReforger\profile\logs\<timestamp>\console.log`

---

## Success/Failure Detection from console.log

Verified verbatim patterns:

| Pattern | Meaning |
|---|---|
| `^WORLD\s+:\s+Entities load '([^']+)'` | World load started |
| `^WORLD\s+:\s+Entity layer load @"([^"]+)"` | Layer loaded |
| `^ENGINE\s+:\s+dir:\s+'([^']+)'` | Addon registered |
| `^SCRIPT\s+\(W\):` | Script warning (non-fatal) |
| `^(WORLD\|ENGINE\|SCRIPT)\s+\((E\|F)\):` | Error/Fatal |
| `^ENGINE\s+\(F\):\s+Crashed` | Hard crash terminator |

**No single "loaded successfully" sentinel exists.** Pragmatic success heuristic:
1. ≥1 `Entities load '<ent>'` line
2. ≥1 `Entity layer load`
3. ZERO `(F):` lines
4. Process exit code = 0

---

## Two Verification Paths

### A) Script-compile gate (fastest, ~10s)
```
ArmaReforgerWorkbenchSteamDiag.exe -gproj "C:\elos\addon.gproj" -validate -logsDir "C:\elos\logs"
```
Exit code 0 = scripts compile. Does NOT verify world load.

### B) World-load smoke test (~30-60s) ⚠️ DISCONFIRMED

> **[DISCONFIRMED 2026-05-20 — Task 005 commit 6cf9b9a]**
> Workbench-Diag 1.6.0.119 mit `-wbSilent -exitAfterInit -load $Addon:Worlds/X.ent`
> exited sauber nach Engine-Init in ~5s **OHNE** `Entities load` Trigger.
> Test ohne `-exitAfterInit`: gleiches Verhalten. Engine läuft komplett durch, lädt
> aber die `.ent` nicht.
> Details: `tasks/archive/PC_RESULT_task003.md` + Task 005 bug-fixer output
> `logs/bugfix-task005-*.json`.
>
> **Alternativen für Smoke-Test (per Task 006):**
> - (a) Custom Workbench-Plugin (Enforce Script) — skeleton in `workbench-plugin/AI_GeneratePlugin.c`, aber noch pseudocode (Phase 2 deliverable)
> - **(b) GUI + Auto-Screenshot + multimodal ui-tester classify** — gewählt für Task 006
> - (c) Linux dedi `-listScenarios` — needs Docker/Linux machine, ungetestet

~~Original (kept for historical reference, do not use as-is):~~

```
ArmaReforgerWorkbenchSteamDiag.exe -gproj "C:\elos\addon.gproj" -load "$Addon:Worlds/Name/Name.ent" -wbSilent -exitAfterInit -logsDir "C:\elos\logs"
```

Parse the new `logs_<TS>\console.log` for success patterns — confirmed only for
`-validate`, NOT for world-load.

### C) Mac-friendly fallback (NOT YET VERIFIED)
Linux dedicated server `-listScenarios` flag — prints discovered scenarios from `-addonsDir`. Confirms addon tree parses without GUI. Reference: `OPEN_QUESTION_1_DEFERRED.md`.

---

## Batch Testing Strategy

- **No native batch mode in Workbench**, no in-config mission rotation.
- **Shell-loop**: invoke Workbench once per mission, each run gets own `logs_<TS>\`. Clean separation for CI.
- **Plugin batch**: `-plugin=AI_BatchTester -missions=path1,path2,...` — use `Workbench.OpenResource()` + `WorldEditor.Save()` per mission, write results JSON. Pattern from CRF_MissionCreationPlugin.

---

## Concrete Command for Our Project (template)

```powershell
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\ArmaReforgerWorkbenchSteamDiag.exe"
$addon = "$env:LOCALAPPDATA\Bohemia Interactive\ArmaReforger\addons\ai_night-recon-everon"
$logDir = "$addon\.test-logs"

# Smoke test
& $diag `
    -gproj "$addon\addon.gproj" `
    -load "`$ai_night-recon-everon:Worlds/night-recon-everon.ent" `
    -wbSilent `
    -exitAfterInit `
    -logsDir $logDir

# Check exit code + parse log
$exitCode = $LASTEXITCODE
$consoleLog = Get-ChildItem "$logDir\logs_*\console.log" -Recurse | Sort-Object LastWriteTime -Desc | Select-Object -First 1

$success = ($exitCode -eq 0) -and
           ($consoleLog | Select-String "WORLD\s+:\s+Entities load") -and
           -not ($consoleLog | Select-String "(WORLD|ENGINE|SCRIPT)\s+\(F\):")
```

---

## Unknowns (explicit — needs empirical test)

- Exit code for `-wbSilent`/`-exitAfterInit` alone (no `-validate`): undocumented
- Does `-load` accept `.conf` (mission) or only `.ent` (world)? Community only shows `.ent`
- Linux dedi `-listScenarios` with unpacked addons: still unverified (Open Question 1)

---

## Phase 2 Plan (post-tools-install)

1. PC runs Path A (`-validate`) against all 3 addons → quick compile check
2. PC runs Path B (smoke test) against each mission → world-load verification
3. Parse all `console.log` files → aggregate pass/fail
4. Push results in `tasks/PC_RESULT.md`
5. Mac generates next iteration (fix bugs, retry, or approve)

This is the path to truly autonomous testing.

---

## Sources

- [BI Wiki: Startup Parameters](https://community.bistudio.com/wiki/Arma_Reforger:Startup_Parameters)
- [BI Wiki: Resource Manager](https://community.bistudio.com/wiki/Arma_Reforger:Resource_Manager)
- [BI Wiki: Workbench Plugin Tutorial](https://community.bistudio.com/wiki/Arma_Reforger:Workbench_Plugin_Tutorial)
- [BI Feedback console.log sample](https://feedback.bistudio.com/file/download/cu77nc25wznkd4ayhn4c/PHID-FILE-74gmnl2a4ar65jk6dmro/console.log)
- [XGamingServer log docs](https://xgamingserver.com/docs/arma-reforger/server-logs)
- [Arma-Reforger-Script-Diff WorkbenchAPI](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff)
