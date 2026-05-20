# Master Project Kickoff Patterns — Research Synthesis

> Stand: 2026-05-20
> Research-Pass (2 background subagents, parallel) on hybrid Opus+Sonnet kickoff design.

---

## 1. Plan-and-Execute SOTA (hybrid models)

**Anthropic's orchestrator-worker** (Opus lead + Sonnet workers) beat single-Opus by
**90.2%** on internal research evals ([Anthropic Engineering Blog](https://www.anthropic.com/engineering/multi-agent-research-system)).

**Advisor Strategy** explicitly uses Opus as planner/critic, Sonnet/Haiku as executor
([MindStudio](https://www.mindstudio.ai/blog/claude-code-advisor-strategy-opus-sonnet-haiku)).

**MetaGPT** uses structured-document handoffs (PRD → Design → Task → Code) NOT free
dialogue. **ChatDev** uses dialogue between 7 roles. ([MetaGPT paper](https://arxiv.org/pdf/2308.00352))

LangChain's **Plan-and-Execute** decouples planner from executor; different model sizes
per role ([apxml course](https://apxml.com/courses/langchain-production-llm/chapter-2-sophisticated-agents-tools/agent-architectures)).

**Handoff format in production:** structured JSON/Markdown spec — NOT dialogue.
Communicator agent reformats across handoff boundaries ([ema.ai](https://www.ema.ai/additional-blogs/addition-blogs/multi-agent-workflows-langchain-langgraph)).

→ **Adopt:** XML-tagged structured document for Opus→Sonnet handoff in Phase 3.

## 2. Plan Saturation Detection

Termination signals from literature:

- **Breadth saturation** — new samples yield near-duplicates ([Lateral ToT](https://arxiv.org/pdf/2510.01500))
- **No new information from clarifications** — Cursor Composer plan mode stops asking
  when answers stop changing the plan
- **Explicit budget caps** — ToT/MCTS width/depth limits
- **Self-critique converges** — critic finds no new issues two cycles in a row

Practical pattern: **cap iterations at N=5**, require Opus to output a **confidence score**
+ **open questions list** each round, stop when both are empty/saturated.

→ **Adopt:** 5-turn hard cap, per-turn confidence + open-questions, saturation checklist
across 8 dimensions (goal/success/steps/tools/fallbacks/integrations/automation/risks).

## 3. Sonnet Prompt Patterns (minimize re-queries)

Sources: [Anthropic docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [Walturn](https://www.walturn.com/insights/mastering-prompt-engineering-for-claude).

- **XML-tagged sections** (`<context>`, `<task>`, `<constraints>`, `<success_criteria>`)
- **Numbered atomic steps**, each with explicit "DONE WHEN:" criteria
- **3–5 worked examples** of expected step output
- Constraints stated quantitatively ("exactly 3 sentences, under 20 words")
- Pre-declared output schema (JSON > prose)

Sonnet follows "contract-style" prompts most reliably.

→ **Adopt:** Phase 3 Sonnet plan uses XML-tagged structure with atomic steps + done_when
+ JSON output schemas.

## 4. Pre-Positioning / Inventory Step

MetaGPT's PRD stage enumerates required tools/APIs upfront. AutoGen Studio surfaces
Skills/Models/Agents/Workflows as a registry before any run ([AutoGen Studio](https://microsoft.github.io/autogen/stable//user-guide/autogenstudio-user-guide/installation.html)).

Pattern: **environment manifest** step that outputs `{required_tools, required_mcps,
required_permissions, missing}` before Phase A loop starts. Block on `missing != []`.

→ **Adopt:** Phase 0 = mandatory Environment Manifest with `env-inventory` sub-agent.

## 5. Brainstorm-Then-Narrow

Two-mode scaffolding works best: **Divergent mode** (broad, many candidates) → **Convergent
mode** (human judgment, targeted refinement) ([arXiv 2512.18388](https://arxiv.org/pdf/2512.18388)).
AI is measurably more creative on divergent tasks but humans must drive convergence ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10858891/)).

Practical: Opus generates 5–10 directions, user picks 1–2, Opus deep-dives.

→ **Adopt:** Phase 1's `idea-expander` (5-10 divergent) + `auditor` (convergent scoring) +
user `clarification-questioner` (final cut).

## 6. Visual Approval Gates

**Copilot Workspace** = explicit per-step approval, conservative-by-design ([Idlen](https://www.idlen.io/blog/claude-code-vs-copilot-workspace-vs-cursor-composer)).

**Cursor Composer** = autonomy slider + **single plan-approval gate** after clarifying questions.

Pattern that converts best: **numbered step list + diff preview + single "Approve plan"
button** (NOT per-step). Show estimated tokens/cost per step.

→ **Adopt:** Phase 2 single approval gate (not per-step) with estimated total cost shown.

## 7. Token Math (concrete)

[Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing):
- Opus 4.7: **$5 in / $25 out per Mtok**
- Sonnet 4.6: **$3 in / $15 out per Mtok**
- Output ratio: **~5×**

[MindStudio benchmark](https://www.mindstudio.ai/blog/claude-code-opus-plan-mode-token-savings):
- Hybrid (Opus plan + Sonnet exec): **60-80% API cost savings** vs all-Opus
- No quality loss observed in benchmarks
- Sonnet does **4-5× more output** within same session budget

Multi-agent uses ~15× tokens vs chat but justifies it via parallel context ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

→ **Adopt:** explicit token budgets per phase (Phase 1 per-turn 25k, Phase 4 per-step 100k,
project hard-cap 500k).

## 8. Auto-Logging & Failure Triggers

Production consensus ([Latitude](https://latitude.so/blog/ai-agent-failure-detection-guide),
[Agents Arcade](https://agentsarcade.com/blog/error-handling-agentic-systems-retries-rollbacks-graceful-failure)):

- **Hard retry cap: 3–5** per logical op, then escalate
- **Structured trace log** per invocation: `{step_id, attempt, tokens_in/out, latency, tool_calls, schema_valid, error}`
- **Schema validation between every agent boundary**
- Trigger retro/audit sub-agent on: `attempts >= 3`, `schema_valid=false`, `confidence < threshold`, or N-minute timer

Copyable schema:
```json
{"step_id":"a3","attempt":2,"phase":"B","model":"sonnet-4.6",
 "tokens":{"in":1200,"out":380},"tool_calls":[...],
 "success_criteria_met":false,"failure_reason":"schema_mismatch",
 "escalate":true}
```

→ **Adopt:** This exact schema for Phase 4 sonnet-exec.jsonl + auto-retro triggers.

---

## Top integrations für Master Kickoff Blueprint

1. ✅ **Phase 0 Environment Manifest** (MetaGPT pattern) — block on missing != []
2. ✅ **Phase 1 saturation loop** with 7 parallel sub-agents, 5-turn hard cap
3. ✅ **Per-turn confidence + open-questions** as saturation signal
4. ✅ **Phase 2 single approval gate** with cost estimate
5. ✅ **Phase 3 XML-tagged structured doc** as Sonnet handoff
6. ✅ **Phase 4 atomic steps + DONE WHEN + JSON schemas**
7. ✅ **Phase 5 auto-fired Opus audit** with final paper
8. ✅ **Token budgets per phase**, hard project-cap
9. ✅ **Structured trace log** + auto-retro triggers (3 fails / 5 min)
10. ✅ **Reflexion per turn** (research/07 pattern)
