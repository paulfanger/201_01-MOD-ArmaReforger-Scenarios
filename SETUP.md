# SETUP.md — Arma Reforger AI-Native Mission Authoring System

> **Complete replication guide for Mac + PC.** Read this first in any new session.
> Last updated: 2026-05-21 (Sprint MEGA-A)

---

## Prerequisites

### Mac (Design + Pipeline)
- Python 3.13+ (`brew install python`)
- Git + GitHub CLI (`brew install git gh`)
- `gh auth login` (GitHub account with repo access)
- Docker Desktop (for Linux dedi validation — optional but recommended)

### PC (Workbench Testing + Game)
- Windows 11 (Build 26200+ tested)
- Steam (logged in, `game 1874880` + `tools 1874910` installed)
- PowerShell 5.1+ (built-in)
- Git for Windows (`winget install Git.Git`)

---

## Quick Start (first time)

### 1. Clone Repo

```bash
# Mac
cd ~/dev  # or wherever
git clone https://github.com/paulfanger/201_01-MOD-ArmaReforger-Scenarios.git

# PC
cd C:\Users\pfofa\Desktop\000_Projekte
git clone https://github.com/paulfanger/201_01-MOD-ArmaReforger-Scenarios.git
```

### 2. Mac — Python Backend Setup

```bash
cd 201_01-MOD-ArmaReforger-Scenarios/backend
pip install -r requirements.txt

# Run tests
pytest --tb=short

# Start server (for interactive use)
python -m uvicorn main:app --reload --port 8765
```

### 3. PC — One-time Setup

```powershell
# Run the setup script (idempotent — safe to re-run)
cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
powershell -ExecutionPolicy Bypass -File scripts\pc-setup.ps1
```

This creates two junctions for Workbench vanilla-addon resolution:
- `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_core`
- `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\addons\_vanilla_data`

### 4. PC — Additional Tools (MEGA-A sprint pre-requisites)

```powershell
# Already installed during PRE-AUDIT or MEGA-A.0:
# - Python 3.12.10, Node.js v24.15.0, VSCode 1.121.0, gh 2.92.0
# - chokidar-cli (npm -g), pydirectinput, pillow, jsonpatch, jsonschema

# Verify:
python --version  # 3.12.x
node --version    # v24.x.x
gh --version      # 2.x.x
chokidar --version  # 3.0.0
```

---

## Verified Paths (Windows PC — empirically confirmed 2026-05-20)

```
Game:      C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerSteam.exe
Server:    C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerServer.exe
Workbench: C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe
Addons:    %USERPROFILE%\Documents\my games\ArmaReforger\addons\
WB-Addons: %USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\addons\
WB-Logs:   %USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\logs\
Steam IDs: Game=1874880  Tools=1874910
```

---

## Running Tests

```bash
# Mac — full suite
cd backend && pytest --tb=short -v

# PC — same, uses Windows Python
cd C:\...\201_01-MOD-ArmaReforger-Scenarios\backend
python -m pytest --tb=short -v

# PC — golden trajectories only
python -m pytest tests\golden\ -v

# Workbench validate (headless, 3 missions):
powershell -Command "
  $diag = 'C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe'
  $addons = \"$env:USERPROFILE\Documents\my games\ArmaReforger\addons\"
  foreach ($m in 'night-recon-everon','day-assault-arland','fog-ambush-eden') {
    \$gproj = \"\$addons\ai_\$m\addon.gproj\"
    Start-Process \$diag -Args @('-gproj', \$gproj, '-validate', '-wbSilent', '-exitAfterInit') -Wait
    Write-Output \"\$m: validate complete\"
  }
"
```

---

## Project Structure

```
201_01-MOD-ArmaReforger-Scenarios/
├── backend/
│   ├── main.py               # FastAPI entry point (port 8765)
│   ├── requirements.txt
│   ├── catalog/              # Asset catalog + faction data
│   ├── exporters/            # Enfusion file generators (.gproj, .ent, .layer, .conf)
│   ├── llm/                  # LLM integration (cached_completion)
│   ├── memory/               # Episodic memory (SQLite FTS5)
│   ├── routes/               # FastAPI routers
│   │   └── revisions.py      # POST /missions/revise (JSON-Patch)
│   ├── scripts/              # CLI scripts
│   ├── snapshots/            # Snapshot management
│   ├── tests/                # pytest test suite
│   └── validators/           # Schema + cross-file validators
├── missions/                 # Generated mission files (3 missions)
│   └── {id}/output/          # addon.gproj + .ent + .layer + .conf + .meta
├── playbook/                 # Protocol docs + cheatsheets + blueprints
│   ├── CHEATSHEET-PC.md      # PC setup + empirical findings
│   ├── RELAY_PROTOCOL.md     # Mac↔PC relay protocol
│   └── SCHEMA_MAPPING.md     # narrative.json → WorldEditorAPI mapping
├── scripts/
│   ├── pc-setup.ps1          # Idempotent PC junction setup
│   └── file-watcher.ps1      # FileSystemWatcher for hot-reload (Sprint B)
├── tests/
│   └── golden/               # Golden trajectory regression tests
├── workbench-plugin/
│   └── AI_GeneratePlugin.c   # Enforce Script plugin (Sprint B implementation)
├── tasks/                    # Agent communication (PC_TASK.md, PC_RESULT.md, STATE.json)
├── logs/                     # Validation logs + screenshots + reflections
├── CLAUDE.md                 # Claude Code rules (this project)
├── SETUP.md                  # THIS FILE
└── PC_AGENT_BRIEF.md         # PC agent orientation
```

---

## Mac↔PC Relay Protocol

See `playbook/RELAY_PROTOCOL.md` for full spec.

**Short version:**
1. Mac pushes task to `tasks/PC_TASK.md`
2. PC reads, executes, writes result to `tasks/PC_RESULT.md`
3. PC pushes → Mac reads
4. Both write `logs/reflection-turn-N-{side}.md` per turn

Current state: `tasks/STATE.json` → `turn_id`, `phase`, `owner`, `loop_signals`.

---

## Contact / Escalation

- **Paul** (User): primary decision-maker for content/creative choices
- **Mac-Claude** (Opus): architecture, novel reasoning, sub-agent orchestration
- **PC-Claude** (Sonnet): execution, testing, Windows-specific work
