# Sprint S1 — Headless Foundation (during CS, ~3-4h)

> Stand: 2026-05-21 · Model: Sonnet 4.6 default (Opus escalation only)
> User-state: spielt Counter-Strike auf PC — KEIN GPU/Game/Workbench touch erlaubt
> Source: research/10-3-stage-sprint-design.md

---

<sprint>

<context>
  <goal>
    Build the foundation layer toward the end-goal of LLM-driven in-editor live revisions:
    plugin refactor with real WorldEditorAPI, schema-mapping doc, Linux Docker dedi-validation,
    revise_mission backend API, prompt caching, episodic memory, golden tests, setup docs.
    All pure-text headless work. No GPU touch.
  </goal>

  <success_criteria>
    <criterion id="sc-1">workbench-plugin/AI_GeneratePlugin.c uses REAL WorldEditorAPI method names from Bohemia samples (no more pseudocode)</criterion>
    <criterion id="sc-2">playbook/SCHEMA_MAPPING.md maps every narrative.json field to API call sequence</criterion>
    <criterion id="sc-3">Linux Docker dedi-validate works: `docker run ... -listScenarios` lists all 3 missions</criterion>
    <criterion id="sc-4">backend/routes/revisions.py with JSON-Patch + schema validation, pytest passes</criterion>
    <criterion id="sc-5">backend/llm/__init__.py with cached_completion() wrapper, prompt-cache verified working</criterion>
    <criterion id="sc-6">backend/memory/episodic.py with SQLite FTS5 (~50 LOC), pytest passes</criterion>
    <criterion id="sc-7">tests/golden/ has night-recon baseline + 1 revision trajectory, regression PASS</criterion>
    <criterion id="sc-8">SETUP.md covers Mac+PC replication from clean install</criterion>
    <criterion id="sc-9">All pytest still 111/111 PASS (no regression)</criterion>
    <criterion id="sc-10">Final paper + reflection-turn-S1-pc.md generated</criterion>
  </success_criteria>

  <constraints>
    <constraint>NO Workbench launch (User plays CS, GPU blocked)</constraint>
    <constraint>NO Game launch</constraint>
    <constraint>NO Windows GUI automation (focus-steal forbidden)</constraint>
    <constraint>NO screenshots (would capture CS)</constraint>
    <constraint>Mac is primary executor for code work; PC pulls + verifies</constraint>
    <constraint>Sub-agent fleet active per RELAY_PROTOCOL.md</constraint>
    <constraint>DRY marker for any destructive op (jsonpatch destructive overwrites etc.)</constraint>
  </constraints>

  <env>
    <repo>C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios</repo>
    <python_required>3.12+ (winget auto-install via dep-installer)</python_required>
    <pip_packages>jsonpatch, jsonschema, anthropic, pytest</pip_packages>
    <docker_required>Docker Desktop on Mac (NOT on PC — Mac does dedi-validate)</docker_required>
  </env>
</context>

---

## STAGE 1.0 — Pre-Flight + State Update

<stage id="1.0" name="preflight">

  <action>
    1. cd repo, git pull --rebase
    2. Verify NO Workbench/Game/CS processes (only CS is OK and stays running)
    3. dep-installer sub-agent: install Python 3.12 via winget if missing, install pip packages
       (jsonpatch jsonschema anthropic pytest)
    4. Update tasks/STATE.json: turn_id=S1, phase=PHASE_C_EXEC, owner=pc, 10 pending_execs
    5. Spawn logger sub-agent (always-on)
  </action>

  <done_when>
    - python --version >= 3.12
    - pip list shows jsonpatch + jsonschema + anthropic + pytest
    - tasks/STATE.json updated
    - logs/pc-events-sprint-S1-<TS>.jsonl writing
  </done_when>

  <on_failure>
    - Python install fail → escalate ⚙️ DO: manual install python.org
    - Pip package fail → check network, retry max 3
  </on_failure>

</stage>

---

## STAGE 1.1 — Plugin Refactor (Pseudocode → Real WorldEditorAPI)

<stage id="1.1" name="plugin_refactor">

  <action>
    1. Read existing workbench-plugin/AI_GeneratePlugin.c (current pseudocode)
    2. Read Bohemia samples reference:
       - https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff
       - Specifically: scripts/GameLib/generated/WorkbenchAPI/Workbench.c
         + WorkbenchAPI/Modules/WorldEditorAPI.c
       - Plus: https://github.com/BohemiaInteractive/Arma-Reforger-Samples — SampleMod_WorkbenchPlugin
       - Plus CRF reference if accessible: CoalitionArma/Coalition-Reforger-Framework
         Scripts/WorkbenchGame/MissionPlugins/CRF_MissionCreationPlugin.c
    3. Refactor AI_GeneratePlugin.c:
       - Replace pseudocode `CreateEntity()` calls with real API: `WorldEditorAPI.CreateEntity(class, prefabGUID, coords)`
       - Add hot-reload file-watch in OnUpdate(): poll `$profile:elos/ai-spec.json` mtime at 1 Hz
       - Add error handling: wrap CreateEntity in try-with-LogError, abort batch on >5 failures
       - Define ai-spec.json schema as comments: `{mission_id, version, ops:[{op,class,prefab_guid,coords,props}]}`
       - Operation-based + idempotent (safe to re-run)
    4. Update workbench-plugin/README.md with file-watch protocol contract
  </action>

  <done_when>
    - AI_GeneratePlugin.c is functional Enforce Script (would compile syntax-clean on PC Workbench)
    - All TODO Phase 2 markers replaced with actual code
    - File-watch loop implemented
    - workbench-plugin/README.md updated with protocol
  </done_when>

  <on_failure>
    - Bohemia repo URL changed → web search "Arma-Reforger-Script-Diff" + fallback to community refs
    - API signature unclear → flag as 🧠 ANSWER, ask user to clarify or escalate to Mac
  </on_failure>

</stage>

---

## STAGE 1.2 — Schema-Mapping (narrative.json → API)

<stage id="1.2" name="schema_mapping">

  <action>
    Generate playbook/SCHEMA_MAPPING.md mit Tabelle für ALLE narrative.json fields:

    | Field | API call sequence | Example |
    |---|---|---|
    | time_of_day.hour/minute | SetVariableValue(timeAndWeatherManager, "m_iHour"/"m_iMinute", val) | "06:00" → SetVar(twm, m_iHour, 6) + SetVar(twm, m_iMinute, 0) |
    | weather.preset | SetVariableValue(weatherManager, "m_sActivePreset", presetName) + BeginEntityAction(weatherManager, "ApplyPreset") | "fog_light" → "Foggy" preset apply |
    | fog_density | SetVariableValue(weatherManager, "m_fFogDensity", float) | Revise: lerp from current to target |
    | spawn_points[] | for each: CreateEntity("SCR_AISpawnPoint", prefab_guid, coords) + SetVariableValue(e, "m_sFactionKey", faction) | 4 SP at given coords |
    | ai_groups[] | CreateEntity("SCR_AIGroup", prefab_guid, coords) + child waypoints via CreateEntity("AIWaypoint_Move", ...) | OPFOR fire group at coords with patrol |
    | triggers[] | CreateEntity("SCR_BaseTriggerEntity", prefab_guid, coords) + SetVariableValue(e, "m_OnActivate", scriptRef) | Phase trigger at coords |
    | tasks[] | CreateEntity("SCR_BaseTask", ...) | Mission objective |

    Plus revision example: "make fog denser" → JSON-Patch [{"op":"replace","path":"/weather/fog_density","value":0.9}]
    → backend regen → plugin reads ai-spec.json → SetVar(weatherManager, m_fFogDensity, 0.9) + worldEditor.Save()
  </action>

  <done_when>
    - SCHEMA_MAPPING.md complete with all narrative fields mapped
    - At least 5 concrete revision examples included
    - Cross-referenced with research/02-mission-format.md + research/04-tasks-triggers-format.md
  </done_when>

  <on_failure>
    - Unknown API for a field → flag in Open Questions section, defer to Phase 5 prototyping
  </on_failure>

</stage>

---

## STAGE 1.3 — Linux Docker Dedi-Validate Setup

<stage id="1.3" name="docker_dedi">

  <action>
    NOTE: This step runs on MAC, not PC. PC just verifies via git pull afterwards.

    Mac-side preparation (PC reads this in result + verifies via git):
    1. Mac: docker pull acemod/docker-reforger:latest (or community alternative if 404)
    2. Mac: write scripts/docker-validate.sh:
       ```bash
       #!/bin/bash
       MISSION_ADDONS_DIR="$1"
       docker run --rm \
         -v "$MISSION_ADDONS_DIR:/profile/addons:ro" \
         acemod/docker-reforger \
         -listScenarios -addonsDir /profile/addons -logFile /tmp/scenarios.txt
       ```
    3. Mac: write backend/scripts/validate_dedi.py:
       - Subprocess.run scripts/docker-validate.sh
       - Parse stdout for ".conf" mission paths
       - Return PASS/FAIL per mission
    4. Mac: test against generated addons → 3 missions found?
    5. Mac: commit + push
    6. PC: git pull, verify files present in result-report (no execution)
  </action>

  <done_when>
    - Files exist: scripts/docker-validate.sh + backend/scripts/validate_dedi.py
    - Mac test shows 3 missions discoverable via `-listScenarios`
    - PC confirms files synced
  </done_when>

  <on_failure>
    - Docker image 404 → try alternatives (Kexanone, RouHim, sknnr per research/09)
    - acemod image works but `-listScenarios` empty → debug addon-path mounting
  </on_failure>

</stage>

---

## STAGE 1.4 — revise_mission Backend API

<stage id="1.4" name="revise_mission">

  <action>
    NOTE: This runs on Mac. PC verifies via tests/ pytest run.

    Mac-side:
    1. Create backend/routes/__init__.py (if not exists)
    2. Create backend/routes/revisions.py:
       ```python
       from fastapi import APIRouter, HTTPException
       import jsonpatch, jsonschema
       from pathlib import Path
       import json

       router = APIRouter()

       REVISION_SCHEMA = {  # schema for incoming revision-spec
         "type": "object",
         "required": ["mission_id", "ops"],
         "properties": {
           "mission_id": {"type": "string"},
           "ops": {"type": "array", "items": {
             "type": "object",
             "required": ["op", "path"],
             "properties": {
               "op": {"enum": ["replace", "add", "remove"]},
               "path": {"type": "string"},
               "value": {}
             }
           }}
         }
       }

       @router.post("/revise/{mission_id}")
       def revise_mission(mission_id: str, revision: dict):
           jsonschema.validate(revision, REVISION_SCHEMA)
           narrative_path = Path(f"missions/{mission_id}/narrative.json")
           if not narrative_path.exists():
               raise HTTPException(404, f"Mission {mission_id} not found")
           narrative = json.loads(narrative_path.read_text())
           patch = jsonpatch.JsonPatch(revision["ops"])
           new_narrative = patch.apply(narrative)
           narrative_path.write_text(json.dumps(new_narrative, indent=2, ensure_ascii=False))
           # Trigger regen
           from backend.scripts.generate_mission import generate_mission_tree
           result = generate_mission_tree(mission_id, narrative_path.parent, auto_approve=True)
           return {"status": "ok", "result": result}
       ```
    3. Wire router into backend/main.py
    4. Add backend/schemas/revision.schema.json + backend/schemas/narrative.schema.json (skeleton)
    5. Add tests in backend/tests/test_revisions.py:
       - Test revise night-recon-everon: change fog_density 0.5 → 0.9
       - Verify narrative.json updated + output regenerated + still validates
  </action>

  <done_when>
    - backend/routes/revisions.py exists with revise_mission endpoint
    - pytest backend/tests/test_revisions.py PASSES
    - 111+ tests still PASS (no regression)
    - Roundtrip works on 3 missions, deterministic outputs
  </done_when>

  <on_failure>
    - jsonschema validation fails → schema fix
    - regen produces different outputs each time → idempotency fix via GUID seed
  </on_failure>

</stage>

---

## STAGE 1.5 — Prompt Caching Integration

<stage id="1.5" name="prompt_caching">

  <action>
    NOTE: Runs on Mac. PC verifies via tests + log inspection.

    Mac-side:
    1. Create backend/llm/__init__.py:
       ```python
       from anthropic import Anthropic
       client = Anthropic()

       CACHED_PREFIXES = {
         "claude_md": "CLAUDE.md content",
         "architecture": "ARCHITECTURE.md content",
         "catalog_index": "catalog/INDEX.json content"
       }

       def cached_completion(user_message: str, model: str = "claude-sonnet-4-6"):
           system_content = [
             {"type": "text", "text": CACHED_PREFIXES["claude_md"],
              "cache_control": {"type": "ephemeral"}},
             {"type": "text", "text": CACHED_PREFIXES["architecture"],
              "cache_control": {"type": "ephemeral"}},
             {"type": "text", "text": CACHED_PREFIXES["catalog_index"],
              "cache_control": {"type": "ephemeral"}}
           ]
           return client.messages.create(
             model=model,
             max_tokens=4096,
             system=system_content,
             messages=[{"role": "user", "content": user_message}]
           )
       ```
    2. Add backend/tests/test_llm_cache.py: verify cache_read_tokens > 0 on 2nd call
       (skip if no ANTHROPIC_API_KEY set)
    3. Document expected savings in research/09 (~90% input cost on hit)
  </action>

  <done_when>
    - backend/llm/__init__.py with cached_completion wrapper exists
    - Test verifies cache_control is in API request payload
    - Documentation cross-ref in research/09
  </done_when>

  <on_failure>
    - No API key in env → test skips gracefully
    - SDK API changed → adapt to current Anthropic SDK version
  </on_failure>

</stage>

---

## STAGE 1.6 — Episodic Memory (Letta-style)

<stage id="1.6" name="episodic_memory">

  <action>
    Mac-side, ~50 LOC:

    1. Create backend/memory/__init__.py + backend/memory/episodic.py:
       ```python
       import sqlite3, json
       from pathlib import Path
       from datetime import datetime

       DB_PATH = Path("memory/episodic.db")
       JSONL_PATH = Path("memory/episodic.jsonl")

       def _init_db():
           DB_PATH.parent.mkdir(exist_ok=True)
           conn = sqlite3.connect(DB_PATH)
           conn.execute("""
               CREATE VIRTUAL TABLE IF NOT EXISTS episodes USING fts5(
                 turn, intent, outcome, lesson, timestamp
               )
           """)
           conn.commit()
           return conn

       def log_episode(turn: int, intent: str, outcome: str, lesson: str):
           ts = datetime.utcnow().isoformat()
           with open(JSONL_PATH, "a") as f:
               f.write(json.dumps({
                 "turn": turn, "intent": intent, "outcome": outcome,
                 "lesson": lesson, "timestamp": ts
               }) + "\n")
           conn = _init_db()
           conn.execute("INSERT INTO episodes VALUES (?, ?, ?, ?, ?)",
                        (turn, intent, outcome, lesson, ts))
           conn.commit()
           conn.close()

       def search(query: str, k: int = 5):
           conn = _init_db()
           cursor = conn.execute("""
               SELECT turn, intent, outcome, lesson, timestamp
               FROM episodes WHERE episodes MATCH ? ORDER BY rank LIMIT ?
           """, (query, k))
           rows = cursor.fetchall()
           conn.close()
           return [{"turn": r[0], "intent": r[1], "outcome": r[2], "lesson": r[3]} for r in rows]
       ```
    2. Bootstrap: import existing logs/reflection-turn-*.md files → parse → log_episode for each
    3. Add backend/tests/test_episodic.py: log + search roundtrip works
  </action>

  <done_when>
    - backend/memory/episodic.py exists + tests PASS
    - memory/episodic.jsonl + episodic.db created
    - Existing reflection-turn-*.md files imported as historical episodes
  </done_when>

  <on_failure>
    - SQLite FTS5 not available → fallback to grep-based JSONL search
  </on_failure>

</stage>

---

## STAGE 1.7 — Golden Tests Baseline

<stage id="1.7" name="golden_tests">

  <action>
    Mac-side:

    1. Create tests/golden/ folder
    2. Create tests/golden/night-recon-everon-baseline.json:
       - Snapshot current missions/night-recon-everon/narrative.json
       - Snapshot expected output files: sha256 of every generated file
    3. Create tests/golden/revision-fog-denser.json:
       - Input: night-recon-everon/narrative.json + revision-spec
         {"ops": [{"op": "replace", "path": "/weather/fog_density", "value": 0.9}]}
       - Expected: regenerated narrative + regenerated output sha256s
    4. Add backend/tests/test_golden.py:
       - Run pipeline against baseline input
       - Assert all expected file sha256s match
       - Run revision pipeline against revision input
       - Assert revised file sha256s match expected
    5. Gate /export on pytest pass (mention in EXPORT.md)
  </action>

  <done_when>
    - tests/golden/ has 2 trajectories
    - pytest backend/tests/test_golden.py PASSES
    - Documentation mentions /export gate
  </done_when>

  <on_failure>
    - Non-deterministic GUID minting → fix in mint.py via uuid5 with NAMESPACE_OID
    - File-content drift → debug pipeline determinism
  </on_failure>

</stage>

---

## STAGE 1.8 — SETUP.md Documentation

<stage id="1.8" name="setup_md">

  <action>
    Generate SETUP.md (Mac+PC replication guide):

    ```markdown
    # SETUP.md — Arma Reforger AI Mission Authoring

    ## Mac Setup
    1. brew install python@3.13 git gh docker
    2. git clone https://github.com/paulfanger/201_01-MOD-ArmaReforger-Scenarios.git
    3. cd 201_01-MOD-ArmaReforger-Scenarios
    4. python3 -m venv backend/.venv
    5. backend/.venv/bin/pip install -r backend/requirements.txt
    6. docker pull acemod/docker-reforger:latest
    7. export ANTHROPIC_API_KEY=sk-...
    8. Test: cd backend && pytest

    ## PC Setup (Windows 11)
    1. Install: Git, Python 3.12 (winget), Steam, Arma Reforger Game, Arma Reforger Tools
    2. git clone <same repo>
    3. powershell -ExecutionPolicy Bypass -File scripts/pc-setup.ps1  # creates junctions
    4. In Claude Code app: open project at <repo path>, switch to Sonnet 4.6
    5. First-time: User clicks "Install" in Steam dialogs (Tools etc.)

    ## First Mission
    1. Mac: `/new-mission <description>`
    2. Mac: pipeline generates files
    3. Mac: docker validate (or PC: workbench-diag validate)
    4. Push to GitHub
    5. PC: git pull + execute next sprint
    ```
  </action>

  <done_when>
    - SETUP.md exists and is complete
    - Cross-references to all blueprints, RELAY_PROTOCOL, sprint plans
  </done_when>

</stage>

---

## STAGE 1.9 — Self-Test + Pipeline Run

<stage id="1.9" name="self_test">

  <action>
    PC-side (or Mac if Docker dedi confirmed):
    1. Run full pytest: pytest backend/tests/ -v
    2. Run docker dedi-validate on all 3 missions (or workbench-diag -validate as fallback)
    3. Run golden trajectory regression
    4. Spawn auditor sub-agent: verify all stages 1.1-1.8 produced expected artifacts
    5. Generate final paper: playbook/handoffs/final-paper-sprint-S1-<TS>.md
  </action>

  <done_when>
    - 111+ tests still PASS
    - Docker dedi finds all 3 missions OR workbench-diag validates 6th+ in row
    - Golden tests PASS
    - Auditor verdict: status=ok
    - Final paper generated
  </done_when>

  <on_failure>
    - Test regression → bug-fixer + escalate to Mac
    - Docker fail + workbench validate fail → escalate (regression in pipeline)
  </on_failure>

</stage>

---

## STAGE 1.10 — Reflection + Push

<stage id="1.10" name="reflection_push">

  <action>
    1. Write logs/reflection-turn-S1-pc.md:
       - What went well
       - What failed and why
       - What I'd do differently next sprint
       - Signals for optimizer
    2. Log_episode (using episodic.py) for each sub-stage outcome
    3. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_S1_complete=true
    4. git pull --rebase, git add -A, git commit, git push
    5. Output to user chat: "Sprint S1 complete. Final paper: <path>. Ready for Sprint S2 (when CS done + you step away from PC)."
  </action>

  <done_when>
    - reflection-turn-S1-pc.md written
    - episodic.jsonl has Sprint-S1 entries
    - STATE.json updated
    - All commits pushed
    - User chat message sent
  </done_when>

</stage>

---

<escalation_triggers>
  - pytest regression (111 tests no longer pass) → escalate (likely Mac-side code change needed)
  - Docker image 404 + all fallbacks fail → escalate (Mac decides alternative)
  - 3× retry exhausted on any sub-stage
  - Token budget >80% of 500k
  - Plugin refactor: API method unclear from Bohemia docs → flag for Mac decision
</escalation_triggers>

<sub_agents_enabled>
  <agent role="logger" always_on="true"/>
  <agent role="dep-installer" stage="1.0" model="haiku"/>
  <agent role="auditor" pre_push="true" per_stage="true" model="sonnet"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <agent role="loop-detector" on_retry="true"/>
  <agent role="optimizer" post_success="true" model="sonnet"/>
</sub_agents_enabled>

<token_budgets>
  <per_stage_max>50000</per_stage_max>
  <total_max>500000</total_max>
  <escalate_at>400000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - same_error_class_dedup = 4 → STOP
  - step_time_budget = 30 min default
  - sprint_time_budget = 4 hr total
  - DRY marker required for any destructive op
  - NO GUI/Game/Workbench launches (CS-safety)
</hard_guards>

</sprint>

---

## Wrapper Prompt (paste in PC chat while CS runs)

```
Du bist PC-Executor. CS läuft parallel. Sprint S1 — Headless Foundation.
Sonnet 4.6 default. ~3-4h headless work, ZERO GUI/Game touch.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/RELAY_PROTOCOL.md (Two-Phase, Sub-Agents, Guards)
3. PC_AGENT_BRIEF.md (Sonnet-compatibility note included)
4. playbook/CHEATSHEET-PC.md
5. research/10-3-stage-sprint-design.md (Stage-context)
6. playbook/handoffs/sprint-S1-headless-foundation.md ← THIS PLAN

Execute Stages 1.0-1.10 strictly per plan. ALL headless. NO GUI/Game/Workbench launches.

Two-Phase Reception:
- Phase A: ⚙️ DO = "CS may stay running, but NO Workbench/Game" → User confirms
- Phase B: Verify processes (Workbench/Game/ArmaReforger must NOT be running, CS is OK)
- Phase C: Stages 1.0-1.10
- Phase D: Single Return + reflection-turn-S1-pc.md

Escalation:
- pytest regression
- Bohemia API docs unclear → flag for Mac
- 3× retry exhausted anywhere
- Token >80% cap

Sub-Agent-Fleet aktiv per RELAY_PROTOCOL. DRY marker for destructive ops.

Final Paper: playbook/handoffs/final-paper-sprint-S1-<TS>.md
Push continuously.

Start with Stage 1.0 (Pre-Flight).
```
