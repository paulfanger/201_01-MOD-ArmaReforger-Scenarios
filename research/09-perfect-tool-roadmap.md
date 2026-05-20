# Perfect Tool Roadmap — Research Synthesis

> Stand: 2026-05-21
> Source: 3 parallel research agents — Arma Ecosystem · Self-Improving Agentic 2026 · AI-Revision UX
> Purpose: Prioritized actionable list of integrations + features to make the system maximally
> autonomous, self-improving, and user-friction-minimal.

---

## 🎯 Executive Summary — Top 3 Findings

**1. Linux Docker Dedi + `-listScenarios` is REAL** (Bohemia Wiki verified)
- Kills the entire Windows-GUI-smoke dependency
- Free (vs Windows VM), runs natively, scenario-discovery built-in
- 4+ community Docker images ready: acemod, Kexanone, RouHim, sknnr
- **Impact:** Mac alone can validate-smoke missions without PC. Massive workflow simplification.

**2. Anthropic Prompt Caching** = 90% input-token cost reduction
- Cache CLAUDE.md + ARCHITECTURE.md + asset-catalog as stable prefix
- Cache read = 10% of standard input cost (write = 125% one-time)
- **Impact:** ~60-80% additional cost savings ON TOP of Sonnet hybrid

**3. BohemiaInteractive/Arma-Reforger-Samples** has the REAL WorldEditorAPI
- `CreateEntity()`, `SetVariableValue()`, `BeginEntityAction()`, etc. — our pseudocode is OFF
- Plugin to functional: 2-4 dev-days (not the weeks we feared)
- **Impact:** Phase 5+ plugin path is much shorter than expected

---

## 🟢 HIGH-VALUE LOW-EFFORT — Do Next Sprint or Week

### 1. Pivot smoke-test to Linux Docker (PIVOT)

```bash
# Mac-side, no PC needed:
docker pull acemod/docker-reforger:latest
docker run -v ./missions:/profile/missions \
  -v ./generated-addons:/profile/addons \
  acemod/docker-reforger \
  -listScenarios -addonsDir /profile/addons
# Output: list of discovered .conf paths
```

- Verifies addon-tree parses + scenario.conf reachable
- Replaces the now-disconfirmed `-wbSilent -load X.ent` CLI pattern
- Sources: [acemod/docker-reforger](https://github.com/acemod/docker-reforger),
  [BI Wiki Startup Parameters](https://community.bistudio.com/wiki/Arma_Reforger:Startup_Parameters)

**Impact:** Mac can self-test missions without PC. PC-dependency for validate-gate eliminated.
PC only needed for Phase 3 (actual game play).

**Effort:** ~2 hours to wire into self-test pipeline.

### 2. Anthropic Prompt Caching (Cache stable prefixes)

```python
# Pseudocode for cached requests
messages = [
    {"role": "system", "content": [
        {"type": "text", "text": claude_md, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": architecture_md, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": asset_catalog_index, "cache_control": {"type": "ephemeral"}}
    ]},
    {"role": "user", "content": current_turn_input}
]
```

- 90% input-cost reduction on cache hits
- Stable prefix MUST come first (caching from start)
- Source: [Anthropic Prompt Caching Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

**Impact:** ~60-80% cost reduction on each Mac-side turn on top of Sonnet hybrid.

**Effort:** Backend change in `backend/*` LLM-call wrappers (if any) — ~1 hour.

### 3. Two-Threshold HITL Confidence Pattern

Add to `playbook/RELAY_PROTOCOL.md` Sektion "Confidence-Driven Clarification":

| Confidence | Action |
|---|---|
| > 0.85 | Proceed silent — Default + Override option in log only |
| 0.70 - 0.85 | Propose with override: "Going with X — sag 'change' to adjust, sonst proceed" |
| < 0.70 | Batch into one `🧠 ANSWER` block via AskUserQuestion (2-4 options + Other) |

- Target HITL rate: 10-15% of decisions (Mavik Labs benchmark)
- Source: [Cognition Devin 2.1](https://cognition.ai/blog/devin-2-1)

**Impact:** ~50% reduction in user interruptions, while increasing user-trust.

**Effort:** 30 min protocol doc update.

### 4. AskUserQuestion Batching — formalize

We're already using Claude Code's `AskUserQuestion` tool. **Formalize as standard pattern:**

- Never ask sequential questions one-by-one
- Batch 2-4 related questions in single call
- Each question: 2-4 mutually exclusive options + auto-"Other" fallback
- Schema:
  ```
  {
    question: "...?",
    header: "...",  // ≤12 chars
    options: [{label, description}],
    multiSelect: false
  }
  ```

- Reference: [Spring AI AskUserQuestionTool](https://spring.io/blog/2026/01/16/spring-ai-ask-user-question-tool/)

**Impact:** Round-trip count reduced 3-5×.

**Effort:** Just protocol doc — already implemented in tool.

### 5. bug-fixer always-propose-options Rule (hardcode)

Update bug-fixer sub-agent spec in `playbook/RELAY_PROTOCOL.md`:

> bug-fixer NEVER outputs "what should we do?". It MUST emit:
> ```json
> {
>   "diagnosis": "what failed + suspected cause",
>   "proposed_fixes": [
>     {"label": "Fix A short", "description": "X", "risk": "low"},
>     {"label": "Fix B short", "description": "Y", "risk": "med"},
>     {"label": "Fix C short", "description": "Z", "risk": "high"}
>   ],
>   "recommended": "Fix A"
> }
> ```
> User picks from labeled options or types Other. Diagnose-then-PROPOSE, never diagnose-then-ASK.

- Sources: [Latitude](https://latitude.so/blog/ai-agent-failure-detection-guide),
  [Antler Digital](https://antler.digital/blog/how-ai-agents-diagnose-and-fix-errors)

**Effort:** 15 min spec update.

### 6. memory/episodic.jsonl + SQLite FTS5 (cross-session memory)

```
memory/episodic.jsonl  — append-only, one event per line
{"turn":5,"intent":"validate addon.gproj","outcome":"PASS","lesson":"Author keyword removed, junctions needed"}
{"turn":8,"intent":"smoke test world load","outcome":"FAIL","lesson":"-wbSilent does not trigger world-load"}

# SQLite FTS5 index for retrieval:
memory/episodic.db (FTS5 virtual table on top of jsonl)
```

- Sub-agent reads relevant prior episodes before planning
- Compounds learning across projects
- Source: [Letta-OS pattern](https://docs.letta.com/concepts/letta/)

**Effort:** ~50 LOC Python — ~2 hours.

### 7. `awesome-reforger` Index — add to research/

Save as `research/10-awesome-reforger-index.md` with:
- Link list of community frameworks (CRF, RHS, GRAD COOP, scalespeeder)
- Docker images (acemod, Kexanone, RouHim, sknnr)
- Bohemia samples repo (WorldEditorAPI reference)
- Workshop publishing CLI (`-publishAddon`)

- Source: [awesome-reforger](https://github.com/ofpisnotdead-com/awesome-reforger)

**Effort:** 30 min curation.

---

## 🟡 MEDIUM-VALUE MEDIUM-EFFORT — Phase 4+

### 8. tests/golden/ Trajectory Regression

```
tests/golden/
  ├── night-recon-everon-baseline.json  (canonical narrative.json input)
  ├── night-recon-everon-expected-files.json  (expected gproj/ent/layer outputs)
  ├── revision-1-fog-density.json  (input: "make fog denser"; expected diff)
  └── ...
```

- Backend test: run pipeline + compare outputs to baseline
- Gate `/export` on regression PASS
- 10 canonical trajectories per project

- Source: [Maxim Golden Dataset Guide](https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/)

**Effort:** 4-6 hours setup, +30 min per added trajectory.

### 9. LangFuse Self-Hosted (Continuous Agent Tracing)

```bash
docker run -d -p 3000:3000 langfuse/langfuse:latest
```

- Self-hostable, framework-agnostic, OpenTelemetry-compatible
- Trace every sub-agent invocation with token/latency/quality scores
- Find performance regressions

- Source: [Latitude Observability Comparison 2026](https://latitude.so/blog/ai-agent-observability-tools-compared-latitude-vs-langfuse-langsmith-braintrust)

**Avoid:** Helicone (in maintenance since March 2026).

**Effort:** 4 hours setup + backend instrumentation.

### 10. RouteLLM-style Sub-Agent Routing

```python
# Pseudocode
def route_sub_agent(role, task_complexity):
    if role in ["logger", "dep-installer", "auditor"]:
        return "haiku"  # cheap mechanical work
    if role in ["bug-fixer", "researcher", "narrative-designer"]:
        return "sonnet" if task_complexity < 0.7 else "opus"
    if role == "main-orchestrator":
        return "opus"
    return "sonnet"  # default
```

- 75-85% cost reduction observed in production
- Source: [RouteLLM](https://zilliz.com/learn/routellm-open-source-framework-for-navigate-cost-quality-trade-offs-in-llm-deployment)

**Effort:** 2-3 hours backend routing layer.

### 11. Workshop Publishing CLI Integration

```powershell
ArmaReforgerWorkbenchSteamDiag.exe -wbModule=ResourceManager `
  -publishAddon -publishAddonVersion "1.0.0" `
  -publishAddonChangeNote "AI-generated night-recon-everon v1" `
  -publishAddonPreviewImage "preview.png" `
  -publishAddonScreenshots "shots/"
```

- Fully scriptable, requires linked BI+Steam account (one-time)
- Wire into `/export` slash-command as Phase 6 deliverable

- Source: [Mod Publishing Process Wiki](https://community.bistudio.com/wiki/Arma_Reforger:Mod_Publishing_Process)

**Effort:** 2 hours (after first-time account linking).

### 12. Windows MCP Servers — opt-in for PC workflows

If we ever go back to Windows-heavy testing (after Linux Docker pivot, probably not):

- `win-cli-mcp-server` (PowerShell/CMD/Git Bash/SSH) — [repo](https://github.com/simon-ami/win-cli-mcp-server)
- `mcp-screenshots-windows` — [repo](https://github.com/YossiAshkenazi/mcp-screenshots-windows)
- `mcp-file-operations-server` (streaming + watch) — [repo](https://github.com/bsmi021/mcp-file-operations-server)

**Effort:** ~1 hour per MCP server to install + config.

---

## 🔴 HIGH-VALUE HIGH-EFFORT — Phase 5+

### 13. Voyager-style Skill Library

```
skills/
  ├── add-mission/
  │   ├── skill.md     (NL description, intent, args schema)
  │   └── skill.sh     (executable steps)
  ├── revise-weather/
  │   ├── skill.md
  │   └── skill.sh
  └── ...
```

- Indexer scans successful EXEC blocks (`outcome=success`) in STATE.json
- Sub-agent generalizes → writes skill.md
- Planner retrieves via embedding sim before generating fresh code
- Start with 5 hand-curated, let agent propose new ones gated by `/approve`

- Sources: [Voyager arXiv:2305.16291](https://arxiv.org/abs/2305.16291),
  [kodustech/awesome-agent-skills](https://github.com/kodustech/awesome-agent-skills)

**Effort:** ~200 LOC + ongoing curation. 1-2 dev-days initial.

### 14. AI_GeneratePlugin.c (Enforce Script — Workbench Plugin)

- Use [BohemiaInteractive/Arma-Reforger-Samples](https://github.com/BohemiaInteractive/Arma-Reforger-Samples) as reference
- Real API: `CreateEntity()`, `DeleteEntities()`, `SetVariableValue()`, etc.
- Compile on Windows Workbench, plugin reads `$profile:elos/ai-spec.json` and generates entities

- Sources: [Workbench Plugin Tutorial](https://community.bistudio.com/wiki/Arma_Reforger:Workbench_Plugin_Tutorial),
  [WorldEditorAPI Usage](https://community.bistudio.com/wiki/Arma_Reforger:WorldEditorAPI_Usage)

**Effort:** 2-4 dev-days against the samples.

### 15. ADAS-style Weekly Optimizer Pass

```python
# Pseudocode
def weekly_optimizer_pass():
    reflections = read_reflections(days=7)
    clusters = cluster_by_embedding(reflections)
    top_failure_mode = clusters[0]
    prompt_diff = propose_prompt_change(top_failure_mode)
    golden_test = generate_locking_test(prompt_diff)
    pr = create_github_pr(prompt_diff, golden_test)
    # NEVER auto-merge. User reviews.
```

- Track Goal Drift Index (GDI) — measure agent drift over time
- Self-improvement only where outcomes are objectively testable
- Source: [SAHOO arXiv:2603.06333](https://arxiv.org/pdf/2603.06333),
  [Agent Drift arXiv:2601.04170](https://arxiv.org/pdf/2601.04170)

**Effort:** 2 dev-days + weekly review time.

---

## ⛔ NOT WORTH IT (negative findings)

- **Helicone** — in maintenance mode since March 2026. Don't adopt.
- **Microsoft Power Automate Desktop** — overkill for our use case.
- **CRF_MissionCreationPlugin.c** — not publicly mirrored. Can't reference.
- **Native Reforger Server mission rotation** — doesn't exist. One scenarioId per config.
- **Standalone "Reforger Workshop Editor"** — doesn't exist. Workbench IS the editor.

---

## Priority Matrix

```
                  HIGH-VALUE
                      |
   13 Voyager        |  1 Linux Docker ✓
   14 Plugin          |  2 Prompt Caching ✓
   15 ADAS Optimizer  |  3 Two-Threshold HITL ✓
                      |  4 AskUserQ batching ✓
                      |  5 bug-fixer rule ✓
   ―――――――――――――――――― + ―――――――――――――――――――― 
                      |  6 episodic.jsonl ✓
   8 tests/golden/    |  7 awesome-reforger ✓
   9 LangFuse         |
   10 RouteLLM        |
   11 Workshop CLI    |
   12 Windows MCPs    |
                      |
                  LOW-VALUE
        HIGH-EFFORT  ←—→  LOW-EFFORT
```

Items in **HIGH-VALUE × LOW-EFFORT quadrant (1-7)** = sprint-or-week wins.
Aspirational items (13-15) = Phase 5+.

---

## Recommended Sequencing

**This Sprint (Phase 2-3 Closeout) — current plan:**
- Already covers GUI smoke + Game Test + Revision Cycle + Polish
- DO NOT expand sprint scope. Stay focused.

**Sprint+1 (Phase 4 — Optimization Sprint, ~2-3 days post-MVP):**
- #1 Linux Docker pivot
- #2 Prompt Caching
- #3 Two-Threshold HITL
- #4 AskUserQ batching (just doc)
- #5 bug-fixer rule (just doc)
- #6 episodic.jsonl
- #7 awesome-reforger index

**Sprint+2 (Phase 4.5 — Quality + Observability):**
- #8 tests/golden/
- #9 LangFuse
- #10 RouteLLM routing
- #11 Workshop publishing

**Sprint+3+ (Phase 5 — Advanced):**
- #13 Voyager skills
- #14 Plugin
- #15 ADAS optimizer

---

## Final Reflection

The system is **functionally complete for MVP**. These additions:
- **#1 alone** (Linux Docker) dramatically reduces cross-device coordination
- **#2 + #10** (caching + routing) cut costs 80-90% from current baseline
- **#3-5 + #6** (HITL improvements + memory) make UX measurably smoother
- **#13-15** are aspirational — beautiful but not required for "smooth prompt-based authoring"

**Honest take:** if you do #1-7 after this sprint, you'll have a system that's 2-3× better than what most game-modding-AI tools achieve today. #13-15 turn it into something that compounds learning over years.

Start with #1 (Linux Docker pivot) — it's the biggest unlock.
