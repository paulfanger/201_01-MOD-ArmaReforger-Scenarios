# S5 Readiness Roadmap — Synthesized Research

> Stand: 2026-05-21
> Source: 3 parallel research agents on Plugin Dev Workflow + S5-Readiness + Build-Test-Fix patterns
> Purpose: ground truth for designing Mega-Sprint A (S1+S2→S5-ready) + Audit Pattern + Mega-Sprint B (S3-S5 live editor)

---

## ⚠️ CRITICAL FINDINGS — Reality Check

### 1. NO native OnUpdate event in Enforce Script Plugins

Research/01's assumption of 1Hz polling pattern in `OnUpdate()` is **DISCONFIRMED**.

Per Bohemia Script-Diff repo, `WorkbenchPlugin` + `WorldEditorPlugin` base classes have ONLY:
- `Run`, `RunCommandline`, `Configure`
- `OnResourceContextMenu`
- `OnGameModeStarted/Ended` (WorldEditor)
- `OnWorldEditWindowDataDropped`

**NO** `OnUpdate`, `OnFrame`, or tick-events. Background polling **not natively supported**.

### 2. Reload mechanism: Ctrl+Shift+R (no restart)

Workbench Plugins menu → "Reload WB Scripts" (default `Ctrl+Shift+R`) or `Shift+F7` in WorldEditor.
Code change → save → hotkey → run. No restart needed for script-only changes.

### 3. Realistic Latency Floors

| Mode | Cycle Time | Notes |
|---|---|---|
| Manual hotkey | **5-10 sec** | User presses hotkey after save |
| CLI headless | **10-20 sec** | Workbench init dominates |
| External-watcher + sendkey hack | **1-2 sec** | Hacky: chokidar/PowerShell-watcher detects file → simulates `Ctrl+Shift+R` → plugin runs |
| Native OnUpdate (does not exist) | n/a | Not possible without engine changes |

**S5-Goal "≤2s latency" achievable ONLY via external-watcher hack.** Fragile but proven pattern.

### 4. Time Estimate (Pseudocode → Live Edit)

Per Agent A:
- Pseudocode refactor → real API: **6-10 h**
- File-loading + JSON parsing: **1-2 h**
- First successful headless test: **2-4 h**
- Iterate to "fog density change visible <2s": **6-10 h** (incl. sendkey hack)

**Total: 15-26 dev-hours = 2-4 focused days** (confirms research/09 #14 estimate).

---

## Falsifiable S5-Ready Criteria (Agent B)

| Dimension | Target | Verifier |
|---|---|---|
| Latency P50 (prompt → repaint) | **≤ 2.0 sec** | `latency-monitor` measures timestamp delta |
| Latency P95 | **≤ 3.5 sec** | Same, regression-tracked per commit |
| Op coverage (MVP) | 5 types: attribute-edit, entity-create, entity-delete, entity-move, batch | Op-matrix test grid |
| Reliability | **10 consecutive** revisions, 0 manual interventions | Headless self-test pipeline |
| Reliability (extended) | **≥ 95%** over 100 randomized prompts | Property-based fuzzer |
| Round-trip integrity | Mission reloads cleanly, entity count delta = expected | `mission-validator` |
| UX naturalness | NL prompts, 0 JSON in user chat, paraphrase-robust (5 rewordings → same diff) | Paraphrase test-set |
| Stability soak | 50 sequential revisions without Workbench restart | Long-run soak test |

---

## New Sub-Agents for S5 (Agent B)

Add to existing fleet:

| Marker | Role | Output |
|---|---|---|
| 🧪 **s5-tester** | Generates synthetic revisions: golden (50 hand-curated) + fuzz + paraphrase | `tests/s5/test-cases.jsonl` |
| ⏱️ **latency-monitor** | Wraps every revision, logs TTFT + end-to-end; alerts if P95 regresses >10% | `logs/latency.csv` + alert events |
| 🔀 **diff-verifier** | Computes JSON-Patch(pre, post), compares vs expected; semantic diff on entity-IDs | `logs/diff-report.json` |
| 📸 **ui-classifier** | Screenshots Workbench viewport, VLM classifies "rendered/error/blank" | `logs/ui-state.json` |
| 🔬 **enforce-researcher** | When API call fails: searches BI wiki, ESE repo, Reforger patch notes | `logs/enforce-findings.md` |

Plus existing: logger, dep-installer, auditor, bug-fixer, loop-detector, ui-tester, process-tracker.

---

## 3-Layer Iteration Loop (Agent B + C combined)

```
INNER (seconds, per single revision):
  code/prompt change → compile-plugin → fire 1 canonical revision
  → latency-monitor + diff-verifier + ui-classifier
  → fail-fast on first red

MIDDLE (minutes, regression suite):
  10-revision regression (1 per op-type + 4 paraphrase mixes)
  → all green → commit

OUTER (hours, full criteria sweep):
  100 fuzzed revisions + 50-revision plugin-stability soak
  → all §criteria met → readiness-reporter green

TERMINATION (saturation):
  3 consecutive outer-loop runs with:
    - ≥95% pass rate
    - no latency regression
    - no new failure modes for 24h
```

Plus stop conditions (any true → halt):
1. All-green N=2 consecutive turns
2. Researcher returns "no new findings" AND error class unchanged
3. Hard cap: max 15 iterations per sprint
4. Diminishing returns: rolling-3-turn `errors_fixed_per_turn` < 1 → researcher escalation

---

## Sub-Agent Depth (Agent C — confirmed from research/07 §6)

Stay **≤ 3 levels**:
- L1: `mission-director` orchestrator
- L2 (siblings, parallel DAG): `bug-fixer`, `pipeline-tester`, `researcher`, `s5-tester`, `latency-monitor`, `diff-verifier`
- L3: utility only (`asset-curator`, `version-keeper`)

Flatten when specialists need to talk → use AgentOrchestra DAG pattern with shared state.

---

## Stuck Recovery Ladder (Agent C)

Per OpenHands StuckDetector + research/07 §3:

1. Trigger: 4 identical action-observation pairs (action-class + error-class, not raw hash)
2. → spawn `researcher` subagent
3. If still stuck after 2 more turns → write blocker to STATE.json
4. → escalate to Mac-Opus or user
5. **Graceful recovery, not crash** — enter error state, resume on new input

---

## Build Environment Provisioning (Devin blueprint pattern)

Per Agent A + C:

### Auto-installable (high confidence):
```powershell
winget install --id Git.Git -e
winget install --id Microsoft.VisualStudioCode -e
winget install --id GitHub.cli -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.12 -e
winget install --id Microsoft.PowerShell -e

# VSCode extensions
code --install-extension YouAreBamboozled.enforce-vscode-plugin
code --install-extension YouAreBamboozled.enforce-script-syntax-highlighting
code --install-extension ms-vscode.powershell

# CLI helpers
npm install -g chokidar-cli

# Pip
pip install jsonpatch jsonschema anthropic pytest pydirectinput pillow
```

### User-gated:
- Arma Reforger Tools (Steam install, manual click)
- Account-login required (gh auth)
- Anything mutating system-wide `%PATH%`

### Snapshot post-success
to skip next run.

---

## Bohemia Samples — Study Order

```bash
gh repo clone BohemiaInteractive/Arma-Reforger-Samples
gh repo clone BohemiaInteractive/Arma-Reforger-Script-Diff
```

1. `Arma-Reforger-Samples/SampleMod_WorkbenchPlugin/Scripts/WorkbenchGame/SamplePlugins/`
   - `SampleResourceManagerPlugin.c`
   - `SampleScriptEditorPlugin.c`
   - `SampleStringEditorPlugin.c`
   - `SampleWorldEditorPlugin.c` ← **primary reference for our use case**
   - `SampleWorldEditorTool.c`
2. `Arma-Reforger-Samples/SampleMod_WorkbenchPlugin/addon.gproj` (minimal manifest)
3. `Arma-Reforger-Script-Diff/scripts/GameLib/generated/WorkbenchAPI/Plugins/WorkbenchPlugin.c` (base class signatures)
4. `WorkbenchAPI/Plugins/WorldEditorPlugin.c` (event hooks)
5. `WorkbenchAPI/Workbench.c` (RunProcess, RunCmd, Dialog, OpenResource, GetAbsolutePath)

---

## File-Watch Hack (since no native OnUpdate)

```javascript
// Pseudocode for chokidar watcher running as background process
const chokidar = require('chokidar');
const { exec } = require('child_process');
chokidar.watch('$profile/elos/ai-spec.json').on('change', () => {
  // Use nircmd or AHK to push Ctrl+Shift+R into Workbench window
  exec('nircmd sendkeypress ctrl+shift+r');
});
```

PowerShell alternative:
```powershell
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\profile\elos"
$watcher.Filter = "ai-spec.json"
$action = {
  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.SendKeys]::SendWait("^+R")
}
Register-ObjectEvent $watcher "Changed" -Action $action
```

⚠️ NOTE: SendKeys won't work for DirectInput games, but Workbench is a standard Windows app — SendKeys should work. PyDirectInput as fallback.

---

## Plugin Testing Strategy (no manual GUI)

Per Agent A — there's no community test framework for Enforce Script. Build our own:

### Headless test command:
```powershell
ArmaReforgerWorkbenchSteamDiag.exe `
  -gproj <addon-path> `
  -wbModule=WorldEditor `
  -plugin=AI_GeneratePlugin `
  -spec=<json-path> `
  -wbSilent -exitAfterInit `
  -logsDir <log-path>
```

### Assertion via log:
- Plugin writes `OK:` / `ERR:` lines via `FileIO.OpenFile` to `$profile:elos/ai-generate-log.txt`
- Python `tests/s5/parse_log.py` greps for outcome lines, asserts pass/fail
- Resulting `.layer` file diff vs golden baseline

### Golden trajectory pattern:
- `tests/s5/golden/fog-density-0.5-to-0.9.json` (input narrative + revision-spec)
- `tests/s5/golden/fog-density-0.5-to-0.9-expected-output.json` (sha256 of expected .layer)
- Pytest: run plugin headless → assert sha256 matches OR semantic-diff acceptable

---

## Top 3 Actionable Sprint-A Targets (S5-prep)

1. **Plugin dev environment fully installed + verified** (winget deps, VSCode extensions, npm chokidar, Bohemia samples cloned)
2. **First sample plugin compiles + runs** (use `SampleWorldEditorPlugin.c` from Bohemia samples as proof-of-concept BEFORE refactoring our own)
3. **Pseudocode AI_GeneratePlugin.c refactored using real WorldEditorAPI** (no functional implementation yet — just clean spec with TODO markers for actual API calls)

---

## Top 5 Actionable Sprint-B Targets (S3-S5 build to live editor)

1. **Implement file-loading + JSON parsing** in AI_GeneratePlugin.c
2. **Implement single attribute-edit op** (fog_density) — proof of concept
3. **Set up chokidar+sendkey watcher** for hot-reload
4. **Headless test harness** with golden trajectories
5. **Iterate to all 5 op types + reliability targets** until §criteria green

---

## What we CAN'T Test Autonomously (S3 user-required)

- "Cursor-Composer-feel" subjective experience
- "Cinematic intent preserved" aesthetic judgment
- Final visual confirmation in Workbench viewport (multimodal classifier is best-effort but user gate is final)
- 5-min flow session with paraphrased prompts (UX validation)

These are the S3 user-gates — minimized but irreducible.

---

## Sources

- Agent A research output `tasks/aca24d6c201d76fc9.output`
- Agent B research output `tasks/a708d670a3d8a1e11.output`
- Agent C research output `tasks/a4986976bfc47ef10.output`
- Cross-referenced research/01, 06, 07, 08, 09, 10
- Bohemia Wiki, Bohemia Samples/Script-Diff repos, VSCode marketplace, MCP registry
