# Blueprint — First-Output Template

> **Purpose:** The project-specific "primer" that combines with one of the BLUEPRINT_LOOP_*
> files to bootstrap a cross-device iteration loop. Fill in the placeholders before
> sending Loop Turn #1.

---

## How to use

1. Fork this template into `playbook/first-output-<project>.md` per new project
2. Fill in every `<placeholder>` — leave none blank
3. Pair with EITHER `BLUEPRINT_LOOP_OPUS_SONNET.md` OR `BLUEPRINT_LOOP_OPUS_ONLY.md`
4. Send both files as initial context to Opus 4.7 → it emits Loop Turn #1

---

# First-Output — <PROJECT NAME>

## 1. Goal (one paragraph)

<What are we building / fixing / achieving? Why? What does "done" look like?>

## 2. Success criteria (objective)

- <Bullet list of measurable outcomes>
- <Each one falsifiable>

## 3. Devices involved

| Device | Role | OS | Access |
|---|---|---|---|
| <e.g. Mac> | Designer / Orchestrator | macOS 14+ | Direct (user is here) |
| <e.g. PC> | Executor / Builder | Windows 11 | Via Git + Claude Code app |
| <e.g. Mobile> | <role> | <os> | <how reachable> |

## 4. Cross-device channel

| Channel | Used for |
|---|---|
| <e.g. Git/GitHub (public repo)> | Code, mission files, results, logs |
| <e.g. Chat-paste via user> | Coordination, decisions, pause/resume |
| <e.g. SSH> | <if applicable> |

## 5. File structure conventions

```
<paste tree of key paths>
```

- `<path>` — <what lives here>
- `<path>` — <what lives here>

## 6. Tooling

| Tool | Version | Where | Notes |
|---|---|---|---|
| <e.g. ArmaReforgerWorkbench> | 1.6.0.119 | PC: <path> | Diag variant |
| <e.g. Python> | 3.13 | Mac | Backend pipeline |
| <e.g. Git> | 2.53+ | Both | |

## 7. Constraints (hard)

- <e.g. No asset-ID hallucinations — all GUIDs must come from catalog>
- <e.g. EULA compliance — APL-ND license headers>
- <e.g. No runtime LLM calls in distributed artifacts>

## 8. Sub-agent fleet activation

| Role | On / Off | Notes |
|---|---|---|
| 🧪 tester | ON | Required for any artifact validation |
| 🐛 bug-fixer | ON | Auto on tester fail |
| 🔬 researcher | ON | Scheduled every 5 turns + on-demand |
| 📊 process-tracker | ON | Required for installs / builds |
| 🔍 auditor | ON | Pre-push, mandatory |
| 📝 logger | ON | Always-on per turn |
| 🎯 optimizer | ON | Post-success |

## 9. Pause-condition customizations

(Optional — additions to standard pause conditions in RELAY_PROTOCOL.md)

- <e.g. Pause if Workbench-Diag crashes with ExitCode != 0>
- <e.g. Pause if EULA-related popup detected>

## 10. Current state (turn 0)

- <Where are we starting from?>
- <What's already been done?>
- <What's the next concrete step?>

## 11. Initial loop turn focus

Loop Turn #1 should:
- <what to relay to other device>
- <what manual user action (if any)>
- <what sub-agents to spawn first>

## 12. Hand-off triggers (Opus+Sonnet blueprint only)

(Only fill if using BLUEPRINT_LOOP_OPUS_SONNET.md)

Switch from Opus → Sonnet when:
- <e.g. "Mission generation iterations are mechanical (template + GUID injection)">
- <e.g. "Mass log-parsing across 50+ files">

Switch back to Opus when:
- <e.g. "Sonnet completes, before final result paper">
- <always for final audit>

---

# Closing

Once filled, this First-Output + your chosen blueprint = ready-to-fire iteration loop.
Send both as initial system prompt. Opus 4.7 emits Loop Turn #1 immediately.
