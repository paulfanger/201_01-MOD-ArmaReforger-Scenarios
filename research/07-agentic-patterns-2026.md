# Agentic Loop Patterns 2026 — Research Synthesis

> Research-Pass (background subagent, 2026-05-20) on what the SOTA in agentic frameworks
> can teach our cross-device Mac↔PC iteration loop. Source-cited, actionable.

---

## 1. Two-Phase Reception — solid foundation

What we built (Phase A manual-action review → Phase B verification → Phase C autonomous
execution → Phase D single return output) is the **LangGraph `interrupt()` + Two-Phase
Commit** idiom. State persists in a Checkpointer; agent pauses at interrupt; human acts;
resume via `Command(resume=...)`. Cognition's **Devin 2.0 "Interactive Planning"** does
the same. **Plan-and-Execute** (LangChain) formalizes planner→multi-step-executor.

Our chat-paste IS the resume-token. Map cleanly to: `plan_node → interrupt(human_review) → execute_dag → finalize_node`.

Sources: [LangGraph interrupt](https://www.langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt) · [Two-Phase Commit / LangGraph](https://www.marktechpost.com/2025/12/31/how-to-design-transactional-agentic-ai-systems-with-langgraph-using-two-phase-commit-human-interrupts-and-safe-rollbacks/) · [Devin 2.0 Interactive Planning](https://cognition.ai/blog/devin-2) · [Plan-and-Execute](https://blog.langchain.com/planning-agents/)

## 2. Self-Improving Loops

| Pattern | Source | What we adopt |
|---|---|---|
| **Reflexion** (Shinn 2023) — Actor/Evaluator/Self-Reflection trio writes post-mortems into episodic memory, consumed next trial. 80→91% HumanEval. | [arXiv 2303.11366](https://arxiv.org/abs/2303.11366) | After every Loop Turn write `logs/reflection-turn-N.md` (what failed, why, what to try). Optimizer consumes at next turn's plan phase. |
| **Voyager** (Wang 2023) — executable skill library indexed by docstring embeddings + iterative prompting + self-verification. | [arXiv 2305.16291](https://arxiv.org/abs/2305.16291) / [repo](https://github.com/MineDojo/Voyager) | Harvest successful EXEC blocks into `playbook/skills/*.md` keyed by intent. Sub-agents retrieve before planning. (Aspirational — Phase 4.) |
| **ADAS / Meta Agent Search** (Hu 2024 ICLR'25) — meta-agent edits agent code itself, archives discoveries. | [arXiv 2408.08435](https://arxiv.org/abs/2408.08435) / [repo](https://github.com/ShengranHu/ADAS) | Weekly `optimizer` pass that proposes protocol patches based on logged failure modes. (Aspirational.) |

## 3. Anti-Loop SOTA — refine our guard

**OpenHands `StuckDetector`** is the production reference (`openhands/controller/stuck.py`):
- Triggers on **4+ identical action-observation pairs** (not 2 — our threshold may be too
  aggressive and risk false-positives, see Cursor bug GH #5355)
- Catches **monologue loops** (model repeats reasoning without action)
- Catches **repeated-error loops** (different actions, same error class)
- Classify by **action-class + error-class**, not raw hash

Add **no-progress detector** (N turns without workspace diff) separate from identical-repeat.

Sources: [OpenHands Stuck Detector](https://docs.openhands.dev/sdk/guides/agent-stuck-detector) · [OpenHands SDK paper](https://arxiv.org/abs/2511.03690) · [Cursor false-positive](https://forum.cursor.com/t/too-aggressive-loop-detection/147781)

## 4. Screenshot UI Verification + Recovery

Anthropic's reference loop (computer_use_demo): **screenshot → vision-reason → action → re-screenshot → verify-against-goal**. Pixel-counting from reference UI elements for resolution-robustness. OpenAI CUA/Operator adds **perception/grounding separation** + user-confirmation gates for sensitive actions.

**Visual Confused Deputy** paper: independent verification of what-the-agent-thinks-it-clicked matters more than action generation.

Windows-specific (early 2026): computer-use macOS-first; on Windows use **OCR + UI Automation API element-tree** as second channel to cross-check vision.

Adopt: every UI action emits `{action, predicted_outcome, actual_screenshot_hash, ocr_diff}`. Mismatch → retry-with-different-grounding, NOT retry-same-action.

Sources: [Anthropic loop.py](https://github.com/anthropics/claude-quickstarts/blob/main/computer-use-demo/computer_use_demo/loop.py) · [OpenAI CUA](https://openai.com/index/computer-using-agent/) · [Visual Confused Deputy](https://arxiv.org/pdf/2603.14707)

## 5. Cross-Device via Git — NOVEL TERRITORY

No published protocol exists for chat-paste + git-files hybrid across physical machines.

Closest precedents:
- git-worktrees + shared `AGENTS.md`/task-list (MindStudio, Claude Code Agent Teams)
- Aider uses git as atomic commit log per turn, not cross-session bus

Heuristic confirmed: **large/structured via Git, ephemeral coordination via chat**. We do this.

**Add: `tasks/STATE.json`** with `{turn_id, owner, phase, pending_do, pending_exec}` so either side can recover after crash without re-reading chat.

Sources: [Parallel agentic git worktrees](https://www.mindstudio.ai/blog/git-worktrees-parallel-ai-coding-agents) · [Claude Code shared task list](https://www.mindstudio.ai/blog/claude-code-agent-teams-shared-task-list)

## 6. Sub-Agent Nesting Depth

Hard data: **Self-Organizing Agent Network** shows AutoGen → 37.2% and MetaGPT → 34.9% pass@1 at **5+ nested nodes** vs ~80% at depth 2-3.

**Stay ≤3 levels** (orchestrator → specialist → utility). Our current setup matches this.

Above depth 3: replace nesting with **DAG dispatched from one orchestrator** (Puppeteer/AgentOrchestra pattern).

Sources: [Self-Organizing Agent Network](https://arxiv.org/html/2508.13732v1) · [AgentOrchestra](https://arxiv.org/html/2506.12508v4)

## 7. Logging Schema Standards

**OpenTelemetry GenAI Semantic Conventions** is the converging standard: `invoke_agent` spans carry `{agent.id, input.size, output.size, eval.result}`; child spans for tools/retrieval/nested agents.

**AgentTrace** adds three-surface taxonomy: **cognitive** (thoughts/plans), **operational** (actions/results), **contextual** (env state).

Adopt: every Loop Turn writes one JSONL `{turn_id, do_items[], exec_items[], reflections[], stuck_signals[], duration_ms}`. Optimizer reads last N turns at session start.

Sources: [OTel GenAI conventions](https://opentelemetry.io/blog/2026/genai-observability/) · [AgentTrace](https://arxiv.org/html/2602.10133v1)

## 8. Biggest Missing Piece (CRITICAL)

**Reversibility + dry-run channel.** Nothing currently stops a destructive EXEC block from
running on the wrong machine. Add:

- **🧪 DRY marker** (4th marker): emit the PLAN of an EXEC block + a hash, without running it.
- Other side computes the same hash from the return template and only then approves the real run.
- Per-turn **rollback snapshot** (git stash + workspace tarball) keyed to `turn_id`.
- Any 🤖 EXEC failure can be undone in one command.

Result: **transactional turns** — every cross-device round-trip is either committed-with-snapshot
or rolled-back-clean. Two-Phase-Commit generalized to chat-paste topology.

---

## Top 3 immediate integrations (this turn)

1. ✅ **Two-Phase Reception** → explicit `tasks/STATE.json` with `{turn_id, owner, phase, pending_do[], pending_exec[]}` for crash-recovery
2. ✅ **StuckDetector** refinement → action-class + error-class dedup (not raw byte-hash) + monologue-loop + no-progress detectors
3. ✅ **Reflexion-style** per-turn `logs/reflection-turn-N.md` written by orchestrator at turn close, consumed at next turn's plan phase

## Top 2 follow-up integrations (next sprint)

4. **🧪 DRY marker** — predicted-outcome hash, approve-then-run
5. **Per-turn rollback snapshot** — git stash + tar at turn start, restore on any blocked-status close

## Aspirational (Phase 4+)

6. Voyager-style skills library in `playbook/skills/*.md`
7. ADAS-style optimizer that proposes protocol patches monthly
8. OTel-based observability with span exports to dev-dashboard
