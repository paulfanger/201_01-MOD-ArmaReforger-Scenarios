# Project State Snapshot — Arma Reforger AI-Native Mission Authoring System

> **Stand:** 2026-05-21 00:30 (vor Phase 2-3 Closeout Sprint)
> **Last commit:** `ec3831c` (Mac) / `37f2e16` (PC) — synced
> **Purpose:** Single-document onboarding for any fresh agent session (especially PC Sonnet
> for the sprint). Read this FIRST, then sprint-phase2-3-closeout.md.

---

## 1. Project Identity (60 sec read)

**Was:** AI-natives Co-Creation-System für Arma Reforger PVE/Koop-Missionen.
Non-Coder User (Paul) + Claude Code Subagent-Pipeline = cinematic, emergent, narrativ-dichte
Missionen. KEIN klassischer Mission-Generator.

**Architektur:** Mac-Side (Designer/Orchestrator, Opus 4.7) ↔ PC-Side (Windows-Executor,
Sonnet 4.6) via Git. Pipeline auf Mac (Python FastAPI Backend), Validierung + GUI-Tests
auf PC (Arma Reforger Tools Workbench-Diag).

**Tech-Stack:**
- Mac: Python 3.13, FastAPI Backend (Port 8765), Git, GH CLI
- PC: Win 11, PowerShell 5.1+, Arma Reforger Game + Tools 1.6.0.119, Steam
- Relay: Public GitHub repo `paulfanger/201_01-MOD-ArmaReforger-Scenarios`

**EULA Status:** GREEN (offline-authoring, APL-ND, kein Runtime-LLM-Call, Disclosure-Headers).

---

## 2. Phase Progress

| Phase | Status | Evidence |
|---|---|---|
| **Phase 0** Pre-Flight + Foundation | ✅ COMPLETE | `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` exist + reviewed |
| **Phase 1** Pipeline MVP (idea → mission files) | ✅ COMPLETE | 111/111 tests pass, 3 missions generated, validate-CI green |
| **Phase 2** Workbench Integration (validate gate) | ✅ 95% | 6× `-validate` PASS confirmed on PC; GUI smoke pending (Sprint Stage 2) |
| **Phase 3** Live Game Test | ⏳ PENDING | Sprint Stage 3 |
| **Phase 3.5** Revision Cycle Test (prompt → regen → re-test) | ⏳ PENDING | Sprint Stage 4 |
| **Phase 4** Polish + Final Paper | ⏳ PENDING | Sprint Stage 5 |
| **Phase 5+** Plugin development, more missions, AI-creative revision | ⏳ FUTURE | Beyond MVP scope |

**Status TL;DR: Pipeline funktioniert end-to-end bis Validate-Gate. Letzter Schritt vor
"prompt-based mission authoring is live": Sprint Stages 2-5.**

---

## 3. Mission Inventory

| Mission | Map | TOD | Weather | Players | Validate | Smoke (planned) | Game-Test |
|---|---|---|---|---|---|---|---|
| `night-recon-everon` | Everon | 02:30 | clear_cold | 1-4 | ✅ PASS 6× | ⏳ Sprint Stage 2 | ⏳ Sprint Stage 3 |
| `day-assault-arland` | Arland | 10:00 | clear | 2-8 | ✅ PASS | ⏳ Sprint Stage 2 | ⏳ |
| `fog-ambush-eden` | Eden | 06:00 | fog_light | 2-6 | ✅ PASS | ⏳ Sprint Stage 2 | ⏳ |
| `test-mission-pipeline-check` | (internal) | — | — | — | — | (self-test only) | n/a |

**All 3 production missions:** authored from narrative.json, GUIDs verified, addon.gproj
clean (kein Author-keyword), Disclosure-Header present, snapshots versioned.

---

## 4. Pipeline Status (Mac side)

```
narrative.json (German, designer input)
  → asset-curator (zero-hallucination guard, catalog/INDEX.json mit 1326 verified GUIDs)
  → encounter-designer (AI-Gruppen, Spawn-Waves)
  → flow-architect (Trigger, Pacing)
  → reforger-bridge (Brace-Syntax export)
  → mission files (addon.gproj + Missions/*.conf + Worlds/*.ent + Worlds/*.layer)
  → Git push
  → PC pull
  → PC Workbench-Diag -validate (compile gate ✅)
  → [PENDING] PC GUI Workbench load (Sprint Stage 2)
  → [PENDING] User Game-Launcher play (Sprint Stage 3)
```

**Backend tests:** 111/111 PASS, ~0.35s. No regression detected through 6 PC iterations.

---

## 5. Sub-Agent Fleet (active)

| Marker | Role | Side | Used in |
|---|---|---|---|
| 📝 logger | Always-on event capture | Both | Every turn |
| 🔧 dep-installer | Pre-flight check + auto-install | PC | Task 002, 005, Sprint Stage 1 |
| 📊 process-tracker | Long-running job monitor | PC | Steam install, Workbench launches |
| 🧪 tester | Generate + run tests | Both | Backend test suite, mission validators |
| 🐛 bug-fixer | Error analyzer + fix proposer | Both | Author-keyword diagnosis, smoke disconfirm |
| 🔍 auditor | Pre-push coverage + quality gate | Both | Every turn pre-push |
| 🛑 loop-detector | Repetition + error-hash dedup | Both | On retry (none fired since Turn 3 hardening) |
| 📸 ui-tester | Multimodal screenshot classify | PC | Sprint Stage 2-4 |
| 🔬 researcher | Deep research on demand | Mac | research/06, 07, 08 generated |

**Spawn pattern:** clear task + output file path + max-minutes. Sub-agent writes JSON,
orchestrator reads, decides next step. Never nested deeper than 3 levels.

---

## 6. Protocol & Blueprint Inventory

| File | Purpose | Status |
|---|---|---|
| `playbook/RELAY_PROTOCOL.md` | Mac↔PC chat-paste + Git protocol, 4 markers, Two-Phase Reception, Anti-Loop Guards, Sub-Agent Fleet, STATE.json, Reflexion-Pattern | ✅ Stable |
| `playbook/BLUEPRINT_PROJECT_KICKOFF.md` | Master prompt for kicking off new projects (Opus plans → Sonnet executes), Phase 0-5 architecture | ✅ Stable |
| `playbook/BLUEPRINT_LOOP_OPUS_SONNET.md` | Hybrid loop blueprint with handoff | ✅ Stable |
| `playbook/BLUEPRINT_LOOP_OPUS_ONLY.md` | Pure-Opus loop blueprint for deep-thought | ✅ Stable |
| `playbook/BLUEPRINT_FIRST_OUTPUT_TEMPLATE.md` | Project-specific primer template | ✅ Stable |
| `playbook/CHEATSHEET-PC.md` | PC's empirical knowledge (Windows-paths, PowerShell-pitfalls, recovery commands) | ✅ Written by PC, 235 lines |
| `playbook/VALIDATION_RULES.md` | Mission-file schema rules | ✅ Stable |
| `playbook/EULA_COMPLIANCE.md` | APL-ND disclosure rules | ✅ Stable |
| `playbook/handoffs/sprint-phase2-3-closeout.md` | THE SPRINT PLAN to execute next | ✅ Final, PC-reviewed |
| `tasks/PC_TASK_008_DRAFT.md` | Pre-staged GUI smoke task (now superseded by Sprint Stage 2) | ⚠️ Deprecated by sprint |

---

## 7. Research Inventory

| File | Topic | Used for |
|---|---|---|
| `research/00-synthesis.md` | Cross-research summary | Architecture |
| `research/01-workbench-sdk.md` | Workbench Plugin SDK / Enforce Script | Plugin path (Phase 5+) |
| `research/02-mission-format.md` | Reforger mission file anatomy | Pipeline schema |
| `research/03-eula-legal.md` | EULA + APL-ND | Compliance |
| `research/04-tasks-triggers-format.md` | Trigger + Task layer schema | Mission generation |
| `research/05-catalog-enrichment.md` | Catalog asset enrichment | catalog/ build |
| `research/06-workbench-cli-flags.md` | CLI flags (validate, wbSilent, etc.) — **Section B DISCONFIRMED** | Validate gate setup |
| `research/07-agentic-patterns-2026.md` | LangGraph, Reflexion, OpenHands StuckDetector — Top 3 integrated | Protocol hardening |
| `research/08-master-kickoff-patterns.md` | Anthropic orchestrator-worker, MetaGPT handoff, Sonnet prompt patterns | Master Kickoff Blueprint |

---

## 8. Test Status

**Backend (Mac):**
- `backend/tests/` — 111/111 PASS, ~0.35s
- Coverage: exporters, validators, schema, cross-file, catalog resolver, mint stability
- No regression through 6 PC iterations

**PC Validate-Gate (compile):**
- 6× consecutive PASS for all 3 missions (Tasks 003 retry, 005, 006-CS, 007-CS, 007b-CS)
- Validate semantics: 0 Fatal + 0 Error in console.log → PASS (exit-code is UNRELIABLE per Task 005 finding)

**PC GUI Smoke (world-load):**
- ⏳ Not yet attempted (Sprint Stage 2)
- research/06 Section B (CLI `-load -wbSilent`) was DISCONFIRMED empirically — sprint uses
  GUI + multimodal screenshot classify alternative

**PC Game-Launcher:**
- ⏳ Not yet attempted (Sprint Stage 3)
- 6 success criteria defined (A-F: scenario visible, loads <30s, spawn visible, movement
  works, TOD/weather match, AI optional)

**Revision Cycle:**
- ⏳ Not yet attempted (Sprint Stage 4)
- Pipeline supports it (slash-commands `/revise` defined, narrative.json editable)
- Untested end-to-end with re-validate + re-test

---

## 9. Known Limitations (be honest)

1. **GUI Workbench world-load:** CLI `-load $Addon:Worlds/X.ent` does NOT trigger Entities-load
   in Workbench-Diag 1.6.0.119 with `-wbSilent`. Sprint uses GUI + screenshot fallback.
2. **AI Encounters:** MVP missions have placeholder/empty encounters.json (Phase 2 deferred).
   Phase 3 game test will confirm spawn works without AI groups (acceptable for MVP).
3. **Plugin (Phase 5+):** `workbench-plugin/AI_GeneratePlugin.c` exists as Enforce Script
   pseudocode skeleton. Not functional. Phase 2 deliverable when Win-Workbench-Dev-Access available.
4. **Linux Dedi smoke alternative:** research/06 Section C mentioned `-listScenarios` on
   Linux dedicated server — not verified, would need Docker setup.
5. **`Author` keyword in addon.gproj:** previously emitted by backend, found incompatible
   with Enfusion schema. Fixed in commit `011f068`. Attribution lives in DISCLOSURE.md.
6. **PowerShell quoting:** subtle pitfalls documented in PC_AGENT_BRIEF.md + CHEATSHEET-PC.md
   (variable-before-colon, cmd-mklink, backtick-n).

---

## 10. Decision Log (key choices)

| Decision | When | Why |
|---|---|---|
| Sonnet 4.6 on PC | Task 006-CS | 70% cost savings, no quality drop for headless |
| Public GitHub repo | Loop Turn #2 | PC needs git pull without auth ceremony |
| Junction approach for vanilla deps | Task 003 (PC autonomous) | Needed by Workbench-Diag for addon resolution |
| Log-pattern over exit-code | Task 005 | Exit-code unreliable empirically |
| GUI+screenshot over -wbSilent smoke | Task 005 → Sprint design | -wbSilent disconfirmed |
| 🧪 DRY marker for destructive ops | Turn 4 (research/07) | Audit-trail + reversibility |
| StuckDetector threshold = 4 | Turn 4 (research/07) | Cursor false-positive lesson |
| Two-Phase Reception | Turn 4 (LangGraph pattern) | User can't be forced to context-switch mid-task |
| Reflexion-pattern (turn-N reflection) | Turn 4 | Memory across turns, +11% measured in original paper |
| Pre-staging via _DRAFT.md | Turn 7 | PC reviews before execution, reduces conflicts |

---

## 11. Loop Turn History (7 turns so far)

| Turn | Side | Outcome | Key artifact |
|---|---|---|---|
| 1 | Mac → PC | Handshake, env-check | Task 001 setup |
| 2 | PC → Mac | Tools-missing + 3 path corrections | Task 002 install |
| 3 | Mac → PC | Anti-loop guards + ui-tester (response to popup-loop) | Task 003 hardened validation |
| 4 | PC → Mac | Author-keyword bug found (PC's good escalation) + 3 junction retries | Author-fix, Task 005 spec |
| 5 | Mac → PC | Sonnet-switch enabled, pc-setup rewrite, DRY marker active | Task 006-CS |
| 6 | PC → Mac | 3/3 Validate PASS first time, DRY proven, Sonnet OK | CHEATSHEET-PC.md |
| 7 | Mac → PC | Sprint plan pre-staged, PC review caught 2 improvements | Final sprint plan |

**Pattern observed:** PC catches Mac-side bugs (Author, paths, smoke disconfirm) very
reliably. Mac iterates fast on protocol hardening. Sub-agent fleet stabilized after Turn 4.

---

## 12. Token Economics (approximate)

| Side | Estimated tokens used | Cost @ Opus rates | Cost @ Sonnet rates |
|---|---|---|---|
| Mac (Opus 4.7) | ~250-350k | $4-7 | n/a (was Opus) |
| PC (Opus → Sonnet at T5) | ~80k Opus + ~50k Sonnet | $1-2 + $0.5 | $0.5 only if Sonnet from start |
| Sub-agents | ~80k mixed | $1-2 | $0.5 |
| **Total estimated so far** | ~410-480k | **$6-11** | — |

**Sprint projected cost (Sonnet on PC):** ~$1-2 additional (vs $4-6 if all-Opus).

---

## 13. Next Concrete Step

**Sprint Phase 2-3 Closeout** (`playbook/handoffs/sprint-phase2-3-closeout.md`):
- **Trigger:** User finishes Counter-Strike, pastes wrapper prompt in PC chat
- **Duration:** 60-90 min
- **Stages:** 5 (Preflight → GUI Smoke → Game Test → Revision Cycle → Polish + Final Paper)
- **User actions required:** Stage 3 (open game, play 60s, report A-F criteria) + Stage 4
  (give revision prompt, replay)
- **Escalation conditions:** GUI smoke 0/3 PASS, Python backend error, 3× retry exhausted,
  token budget >80%

**Success = "smooth prompt-based authoring is live":**
1. ✅ Validate-Gate (already done)
2. ⏳ GUI loads mission (Sprint Stage 2)
3. ⏳ Mission plays in-game (Sprint Stage 3)
4. ⏳ Revision-cycle works (Sprint Stage 4)
5. ⏳ Final paper documents capability (Sprint Stage 5)

---

## 14. For Fresh Agent (Sonnet 4.6 running Sprint)

You inherit:
- Stable pipeline + 3 validated missions
- 6× consecutive validate-PASS history (CI gate trusted)
- Full sub-agent fleet (use them, don't reinvent)
- Anti-loop guards (3 retries, 5-min step budget, 90-min sprint budget)
- DRY marker for destructive ops (mandatory)
- Reflexion pattern (write reflection-sprint-stageN-pc.md per stage)
- Two-Phase Reception (Phase A user-check → Phase B verify → Phase C exec → Phase D return)
- User-action gates ARE pauses (not instant continue)

You do NOT:
- Modify mission narrative.json without explicit user prompt (designer territory)
- Skip the auditor pre-push (gates quality)
- Suppress popup-loops (escalate, never click for user)
- Push without DRY-plan for destructive ops

When in doubt: escalate via git push + chat-pause → Mac-Opus picks up.

---

## End-of-Report

Read this. Then `playbook/handoffs/sprint-phase2-3-closeout.md`. Then start Sprint Stage 1.

Good luck. The pipeline is stable, the plan is detailed, the escalation paths exist.
