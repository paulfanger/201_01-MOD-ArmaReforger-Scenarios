# Blueprint — Master Project Kickoff (Opus plans → Sonnet executes)

> Stand: 2026-05-20
> Purpose: Idee + Kontext → Opus 4.7 iteriert mit Sub-Agents bis Plan saturiert →
> Sonnet 4.6 executed den fertigen Plan → Opus auditiert final. Token-optimal split.

---

## Wann nutzen / wann nicht

| ✅ Use it for | ❌ Don't use it for |
|---|---|
| Brand-new Projekt (Plan existiert noch nicht) | Plan da → nutze `BLUEPRINT_LOOP_OPUS_SONNET` direkt |
| Plan mit >5 atomaren Execution-Steps | Trivial One-Shot (≤3 Steps) |
| Multi-Phase / multi-week Arbeit | <30 min Total-Arbeit |
| Token-Budget zählt | Latency zählt mehr als Cost |
| Domain-agnostisch (Code, Content, Ops, Research, …) | Pure Conversation ohne Artefakte |

---

## Empirie (warum sich der Split lohnt)

- Anthropic Orchestrator-Worker: **+90.2% vs single-Opus** auf Research-Evals ([Anthropic Engineering Blog](https://www.anthropic.com/engineering/multi-agent-research-system))
- Opus 4.7: **$5 in / $25 out per Mtok** · Sonnet 4.6: **$3 in / $15 out per Mtok** → **5× output cost ratio** ([Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing))
- Hybrid (Opus plan + Sonnet exec): **60-80% API cost savings**, no quality loss ([MindStudio benchmark](https://www.mindstudio.ai/blog/claude-code-opus-plan-mode-token-savings))
- Sonnet liefert **4-5× mehr Output** im gleichen Session-Budget bei strukturierten Plänen

---

## How to invoke

User pastet diesen Blueprint + den projektspezifischen **Kickoff-Input** in eine frische
Opus 4.7 Session:

```
## Idee
<1-3 Sätze: was bauen wir, warum>

## Kontext
<1 Absatz: bestehender Stand, Beteiligte, Constraints, Deadline, Budget>

## (optional) Präferenzen
<Stack-Wünsche, Style, Deadlines, Tooling-Vorlieben>
```

Opus 4.7 emittiert sofort **Phase 0 (Environment Manifest)**.

---

## Architecture-Overview

```
[USER: Idee + Kontext]
        ↓
┌──────────────────────────────────────────┐
│ PHASE 0: Environment Manifest (Opus)     │  ← inventory step
│   sub-agent: env-inventory               │
│   blockt Phase 1 wenn missing != []      │
└──────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│ PHASE 1: Iteration Loop (Opus + 7 Subs)  │  ← saturation loop
│   max 5 Turns, dann hard escalate         │
│   per Turn: 7 Sub-Agents parallel         │
│   end: alle Saturation-Kriterien ✅       │
└──────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│ PHASE 2: Visual Approval Gate (Opus→User)│  ← user signs off
│   single approve-or-refine decision      │
└──────────────────────────────────────────┘
        ↓ "approve" / "freigegeben"
┌──────────────────────────────────────────┐
│ PHASE 3: Sonnet Plan Compilation (Opus)  │  ← structured handoff doc
│   XML-tagged, numbered atomic steps,     │
│   DONE WHEN criteria, escalation triggers│
└──────────────────────────────────────────┘
        ↓ user paste in fresh Sonnet session + "go"
┌──────────────────────────────────────────┐
│ PHASE 4: Sonnet Execution (Sonnet 4.6)   │  ← bulk work
│   contract-style follow-the-plan         │
│   escalates only on defined triggers     │
└──────────────────────────────────────────┘
        ↓ Sonnet done / escalation
┌──────────────────────────────────────────┐
│ PHASE 5: Opus Final Audit (Opus 4.7)     │  ← polish
│   auditor sub-agent + final paper        │
└──────────────────────────────────────────┘
        ↓
[FINAL OUTPUT PAPER]
```

---

## Phase 0 — Environment Manifest

**Opus's allererste Aktion.** Inventory (per MetaGPT/AutoGen pattern). Sub-agent
`env-inventory` listet ALLES auf, was das Projekt braucht:

```json
{
  "required_tools": [
    {"name":"git", "min_version":"2.40", "check_cmd":"git --version", "auto_installable":true}
  ],
  "required_mcps": [
    {"name":"clickup", "auth_status":"unknown", "user_gated":true}
  ],
  "required_permissions": [
    {"scope":"file:write", "granted":false, "auto_grantable":true}
  ],
  "required_accounts": [
    {"service":"github", "logged_in":false, "user_gated":true}
  ],
  "missing": ["clickup-mcp-auth", "github-login"],
  "auto_installable": ["git", "powershell-modules"],
  "user_gated": ["clickup-auth", "github-login"]
}
```

### Opus emittiert in Chat:

```
═══════════════════════════════════════════════════════════
  🔄 KICKOFF · PHASE 0 · Environment Manifest
═══════════════════════════════════════════════════════════

## 📋 Was dein Projekt braucht (Inventory)

### ✅ Bereits vorhanden
| Tool | Version | OK |
| git | 2.53 | ✅ |
| ... | ... | ✅ |

### 🤖 Auto-installierbar (1 Klick freigegeben)
- powershell-screenshot (native, kein Install)
- python 3.12 (winget)
- pillow (pip)

### ⚙️ DO — User-Gated (manuelle Schritte)
1. ClickUp MCP authentifizieren via /mcp clickup
2. GitHub login: gh auth login

### ⏸ APPROVAL GATE: Sag "auto-install ok" → ich install alles automatisch,
   du machst nur die ⚙️ DO-Items. Oder spezifiziere Auswahl.
```

**Block Phase 1 bis `missing == []`.**

---

## Phase 1 — Iteration Loop (Saturation)

Jeder Turn spawnt 7 Sub-Agents **parallel**. Insgesamt max 5 Turns (Hard-Cap).

### Sub-Agent Fleet (Phase 1)

| Marker | Sub-Agent | Aufgabe | Zeit | Output |
|---|---|---|---|---|
| 🔬 | **project-researcher** | External Research: similar projects, prior art, best practices in Domain | 10 min | `logs/kickoff/research-turn-N.md` |
| 💡 | **idea-expander** | Brainstorm 5-10 Ideen die das Projekt besser machen | 5 min | `logs/kickoff/ideas-turn-N.md` |
| 🔍 | **auditor** | Score collected items: Impact × Feasibility × Strategic Fit | 3 min | `logs/kickoff/audit-turn-N.json` |
| 🔧 | **tooling-inventory** | Precise list aller Tools/Integrations/MCPs/programs/APIs/libs | 5 min | `logs/kickoff/tooling-turn-N.json` |
| 🧠 | **synthesizer** | Compile zu evolving concept-Doc (incrementell) | 3 min | `logs/kickoff/concept-v<N>.md` |
| ❓ | **clarification-questioner** | 2-5 sharp gap-questions für User | 1 min | `logs/kickoff/questions-turn-N.md` |
| 🤖 | **automation-prepositioner** | Identifiziere was JETZT schon auto-installierbar/konfigurierbar ist | 3 min | `logs/kickoff/automation-turn-N.md` |

### Saturation Criteria — Loop endet wenn ALLE wahr

- 🟢 project-researcher: **2 consecutive Turns ohne New Findings**
- 🟢 idea-expander: **0 net-new ideas after auditor-scoring**
- 🟢 auditor verdict: `coverage_complete` (alle 8 Dimensionen: goal/success/steps/tools/fallbacks/integrations/automation/risks)
- 🟢 clarification-questioner: **0 open questions**
- ODER user explizit: `"saturiert"` / `"ready"` / `"go"`
- HARD CAP: **5 Turns**, dann escalate via auditor

### Per-Turn Chat-Output (User sieht das)

```
═══════════════════════════════════════════════════════════
  🔄 KICKOFF TURN #N · 2026-MM-DD HH:MM · saturating
═══════════════════════════════════════════════════════════

## Was in dieser Iteration neu ist

**Research:**
- <project-research highlight 1>
- <project-research highlight 2>

**Ideen die's durch den Audit geschafft haben:**
- <idea 1> (Impact 8/10, Feasibility 6/10, Strategic Fit 9/10)
- <idea 2> (...)

**Neue Tools im Inventar:**
- <tool 1> — <warum>

**Automation-Vorschläge die JETZT laufen können:**
- <auto-action 1>

## Aktueller Concept (v<N>)

<1-2 Absätze evolving synthesis — knapp, kein wall-of-text>

## Saturation Status

| Dimension | Stand |
|---|---|
| Research-Sättigung | 🟢/🟡/🔴 |
| Idea-Sättigung | 🟢/🟡/🔴 |
| Audit-Coverage | 🟢/🟡/🔴 (X/8 dimensions) |
| Open Questions | <N> |

## 🧠 ANSWER — bitte beantworte selbst (optional)

Q1: <sharp clarification question>
Q2: ...

## ⏸ STATUS: iterating · saturated-awaiting-approval · paused

Nächste Aktion: <iterate further / awaiting your answers / approve to proceed>
```

### Reflexion (Pflicht am Turn-Ende)

Opus schreibt `logs/kickoff/reflection-turn-N.md` (per Reflexion-Pattern, research/07):
- What surfaced new this turn
- What's converged
- What's still open
- Signals für Optimizer (token-Verbrauch, Sub-Agent-Times)

Wird in Turn N+1's Plan-Phase gelesen.

---

## Phase 2 — Visual Approval Gate

Wenn Saturation reached → Opus emittiert die **Visual Summary**:

```
═══════════════════════════════════════════════════════════
  📋 PROJECT BLUEPRINT — APPROVAL GATE
═══════════════════════════════════════════════════════════

## Project at a glance

<one-paragraph north-star>

## 🎯 Goal + Success Criteria

- **Primary Goal:** <objective>
- ✅ Success when:
  - <criterion 1, objective + measurable>
  - <criterion 2>
  - <criterion 3>

## 🛠️ Approach (steps overview)

1. **<Step Group 1>** — <one-liner>
2. **<Step Group 2>** — <one-liner>
3. **<Step Group 3>** — <one-liner>

## 🔧 Required tooling

| Tool | Status | Cost | License |
|---|---|---|---|
| git | ✅ installed | $0 | GPL |
| python | ✅ installed | $0 | PSF |
| ClickUp MCP | ⚙️ auth needed | $0 (free tier) | Proprietary |

## ⚠️ Risks + Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| <risk> | M | <mitigation> |

## 💰 Estimated Cost (token math)

- Opus Phase 1 + 5: ~<X> tokens (~$<Y>)
- Sonnet Phase 4: ~<X> tokens (~$<Y>)
- Sub-Agents: ~<X> tokens (~$<Y>)
- **Total: ~$<X+Y+Z>**

(Pro Vergleich: pure-Opus wäre ~$<3-5×>)

## 📦 Artefakte die entstehen werden

- `playbook/handoffs/sonnet-plan-<project>-<TS>.md`
- `<output artifact 1>`
- `<output artifact 2>`
- `playbook/handoffs/final-paper-<project>-<TS>.md`

## ⏸ DECISION REQUIRED

☐ **Approve** → sag "approve" / "freigegeben" / "go" → Opus compiles Sonnet plan
☐ **Refine** → beschreibe was angepasst werden soll → zurück in Phase 1
☐ **Pause** → sag "pause" → State gespeichert, später resume
```

User says "approve" → Phase 3.

---

## Phase 3 — Sonnet Plan Compilation

Opus produziert **eine einzige Datei**: `playbook/handoffs/sonnet-plan-<project>-<TS>.md`.

Format (per MetaGPT structured-doc + Anthropic Sonnet best practices):

```xml
<context>
  <goal>...</goal>
  <success_criteria>
    <criterion id="sc-1">objective + measurable</criterion>
  </success_criteria>
  <constraints>
    <constraint>...</constraint>
  </constraints>
  <env>
    <tool>git@2.53</tool>
    <mcp>clickup</mcp>
    <permission>file:write</permission>
  </env>
</context>

<steps>
  <step id="s-1">
    <action>concrete atomic action (one verb, one object)</action>
    <inputs>
      - <file path or state>
    </inputs>
    <output_schema>
      {"key": "type", "...": "..."}
    </output_schema>
    <done_when>
      - <criterion 1, falsifiable>
      - <criterion 2>
    </done_when>
    <on_failure>
      - retry max 3× with 5s backoff
      - if still failing: escalate-to-opus with {step_id, error_class, evidence}
    </on_failure>
    <log_to>logs/sonnet-exec-<TS>.jsonl</log_to>
  </step>
  <!-- 5-50 atomic steps -->
</steps>

<escalation_triggers>
  - <step.success_criteria_met == false after 3 retries>
  - <schema_valid == false>
  - <confidence < 0.7 on critical step>
  - <token_budget approaching cap>
  - <unknown error class observed>
</escalation_triggers>

<sub_agents_enabled>
  <agent role="logger" always_on="true"/>
  <agent role="dep-installer" pre_flight="true"/>
  <agent role="auditor" pre_push="true"/>
  <agent role="ui-tester" on_gui_launch="true"/>
  <agent role="loop-detector" on_every_retry="true"/>
</sub_agents_enabled>

<final_audit>
  - Opus reviews all logs/sonnet-exec-*.jsonl
  - Opus checks all <success_criteria> met
  - Opus produces final-paper-<TS>.md
</final_audit>

<token_budgets>
  <per_step_max>100000</per_step_max>
  <total_max>500000</total_max>
  <escalate_at>0.8 × total_max</escalate_at>
</token_budgets>
```

### Was macht den Plan Sonnet-optimal

Per research findings:
- ✅ **XML-tagged sections** → Sonnet folgt Struktur zuverlässiger als Prose
- ✅ **Atomic steps** (one verb, one object) → keine Mehrdeutigkeit
- ✅ **Explicit `done_when`** pro Step → kein Ratespiel
- ✅ **JSON output schemas** pro Step → schema-validate-between-boundaries
- ✅ **Quantitative constraints** ("exactly 3", "under 20 words") → reduziert re-queries
- ✅ **Escalation triggers explicit** → Sonnet weiß WANN sie zurück zu Opus muss

---

## Phase 4 — Sonnet Execution

User triggert: paste den Sonnet-Plan in eine **frische Sonnet 4.6 Session** mit:

```
Execute this plan. Follow <steps> in order.
Spawn the <sub_agents_enabled>.
Escalate per <escalation_triggers>.
Log to <log_to> per step.
When done, write playbook/handoffs/sonnet-exec-result-<TS>.md.

[paste sonnet-plan content]
```

### Sonnet folgt deterministisch:

1. Read plan, validate against schema
2. Spawn logger (always-on, log_to per step)
3. dep-installer pre-flight (block on missing)
4. Loop through `<steps>`:
   - Execute action
   - Validate output against `<output_schema>`
   - Check `<done_when>` criteria
   - If fail: retry max 3, then escalate
   - Log every event
5. Write `sonnet-exec-result-<TS>.md` mit:
   - Each step status (✅/⏳/❌)
   - All success_criteria_met flags
   - Logs reference
   - Escalations triggered (if any)

### Trace-Log Schema (per step)

```json
{
  "step_id": "s-3",
  "attempt": 1,
  "phase": "B",
  "model": "claude-sonnet-4.6",
  "started_at": "<ISO>",
  "finished_at": "<ISO>",
  "tokens": {"in": 1200, "out": 380},
  "tool_calls": ["bash:git pull", "read:tasks/STATE.json"],
  "schema_valid": true,
  "success_criteria_met": true,
  "failure_reason": null,
  "escalate": false
}
```

---

## Phase 5 — Opus Final Audit

**Auto-triggered** wenn Sonnet finished oder escalation.

Opus:

1. Reads `sonnet-plan-<TS>.md` + `sonnet-exec-result-<TS>.md` + `logs/sonnet-exec-*.jsonl`
2. Spawns `auditor` mit Original-Goal + All-Artifacts
3. Identifies:
   - Welche `<success_criteria>` met / not-met
   - Quality issues
   - Missed edge cases
   - Schema mismatches in any step
4. Action:
   - Wenn ≤2 gaps: Opus polished direkt
   - Wenn 3-5 gaps: mini-Sonnet-cycle für die Sub-Gaps
   - Wenn >5 gaps oder critical fail: re-enter Phase 1 (Iteration Loop) mit Audit-Findings als Input
5. Produces **Final Output Paper**: `playbook/handoffs/final-paper-<project>-<TS>.md`

### Final Paper Format

```markdown
# Final Paper — <Project Name>

> Stand: <YYYY-MM-DD>
> Status: ✅ Goal Reached / ⏳ Partial / ❌ Blocked

## Goal Achievement

- Primary goal: <restatement>
- Success criteria met: ✅ X/Y · ⏳ A/Y · ❌ B/Y

## Path Traveled

| Phase | Turns | Tokens | Cost | Outcome |
|---|---|---|---|---|
| 0 | 1 | <X> | $<Y> | env complete |
| 1 | <N> | <X> | $<Y> | saturated |
| 2 | 1 | <X> | $<Y> | approved |
| 3 | 1 | <X> | $<Y> | plan compiled |
| 4 | <N> | <X> | $<Y> | executed |
| 5 | 1 | <X> | $<Y> | audited |

## Decisions Made

- <decision 1> — rationale: <why>
- ...

## Artefakte produziert

- `<path 1>` — <description>
- ...

## Open Questions für Future

- <question 1>

## Cost Breakdown

- Opus tokens (planning + audit): <X> · $<Y>
- Sonnet tokens (execution): <X> · $<Y>
- Sub-agents tokens: <X> · $<Y>
- **Total: $<Z>**
- Vergleich pure-Opus: hätte ~$<3-5×Z> gekostet
- **Saving: ~<60-80>%**

## Reflection (final)

<2-3 Absätze: was funktionierte, was nicht, was nächstes Mal besser>
```

⏸ PAUSE FLAG: **closed**

---

## Logging & Tracking (always on)

Per Turn:
- `logs/kickoff-events-<TS>.jsonl` — alle Events
- `logs/kickoff/reflection-turn-<N>.md` — Reflexion-Pattern
- `tasks/STATE.json` — single source of truth

Per Sub-Agent:
- `{agent, started_at, finished_at, status, summary, details, next_actions, human_attention_required}`

### Trigger für Auto-Retro-Analyse

- ≥3 failed attempts auf gleichem Step → spawn `bug-fixer` mit Evidence
- ≥5 min timer ohne Progress → spawn `process-tracker` audit
- schema_valid == false zweimal → escalate-to-opus
- confidence < 0.7 → researcher spawned mit fragestellung

---

## Pause-Conditions (Hard Stops)

| Trigger | Marker | Resume bei |
|---|---|---|
| Clarification-Q needs User | 🧠 ANSWER | User antwortet |
| Manual Action User-only | ⚙️ DO | User confirms done |
| Auditor confidence below threshold | 🔍 STALL | Re-research-cycle returns |
| 3× retry exhausted | ❌ ESCALATE | User decides direction |
| Token budget approaching cap | 💰 BUDGET | User approves continue oder closes |
| Cross-device dep | 📤 FOR <other> | Other side responds |
| Goal reached | ✅ closed | Loop ends |

Loop pausiert NICHT für:
- Sub-Agent fails (bug-fixer handles)
- Single retries (built-in)
- Logging/research backgrounds
- Short waits <2 min

---

## Integration mit anderen Blueprints

Nach Phase 3 (Sonnet plan compiled):

- **Single-device execution** → direkter Sonnet-Run wie hier beschrieben (Phase 4)
- **Multi-device execution** → Sonnet plan in `BLUEPRINT_LOOP_OPUS_SONNET` einspeisen (Two-Phase Reception, relay format, etc.)
- **Pure deep-thought across all execution** → seltener Fall, lieber `BLUEPRINT_LOOP_OPUS_ONLY`

---

## Anti-Patterns (heilig)

- ❌ Skip Phase 0 — führt zu Mid-Execution-Blockern wegen fehlender Tools
- ❌ Phase 1 mehr als 5 Turns ohne Saturation — Auditor muss escalate
- ❌ Sonnet plan compilen BEVOR User approved — wastes Opus tokens
- ❌ Sonnet executed ohne explicit escalation_triggers — Black-Box-Failures
- ❌ Final Opus-Audit skippen — Sonnet output kann Edge-Cases übersehen
- ❌ User sieht gleiche clarification-Q zweimal — Protocol Bug
- ❌ Sub-Agents in Schleifen ohne logger — keine Retro möglich
- ❌ Free-Dialogue-Handoff statt structured-doc — Sonnet re-queried Opus 3-5× häufiger
- ❌ Token-budget ignorieren — Cost-Blowout

---

## Saved Artifacts (was nach voll-Run existiert)

```
playbook/handoffs/
  env-manifest-<TS>.json
  sonnet-plan-<project>-<TS>.md
  sonnet-exec-result-<TS>.md
  final-paper-<project>-<TS>.md

logs/kickoff/
  research-turn-1.md ... research-turn-N.md
  ideas-turn-1.md ... ideas-turn-N.md
  audit-turn-1.json ... audit-turn-N.json
  tooling-turn-1.json ... tooling-turn-N.json
  concept-v1.md ... concept-vN.md
  questions-turn-1.md ... questions-turn-N.md
  automation-turn-1.md ... automation-turn-N.md
  reflection-turn-1.md ... reflection-turn-N.md

logs/
  kickoff-events-<TS>.jsonl
  sonnet-exec-<TS>.jsonl
  audit-final-<TS>.json

tasks/
  STATE.json (last state)
```

Alle inspizierbar, re-runnable, reusable.

---

## Quick-Start (TL;DR für User)

1. **Paste:** dieser Blueprint + dein Idee+Kontext (siehe "How to invoke")
2. **Phase 0:** approve oder spezifiziere Tooling-Auto-Install
3. **Phase 1:** beantworte ggf. 2-5 Clarification-Q pro Turn (oder weniger), bis Plan saturated
4. **Phase 2:** sag "approve" / "refine X" / "pause"
5. **Phase 3:** Opus compiles `sonnet-plan-<TS>.md` — kopieren bereit
6. **Phase 4:** frische Sonnet 4.6 Session öffnen, Plan reinpasten, "go" sagen
7. **Phase 5:** Opus auto-fires audit, schreibt final paper
8. **Done.** Token-Cost ~60-80% niedriger als pure-Opus, Quality stabil.
