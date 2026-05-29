# Tomorrow Companion Workflow
## ELOS Arma Reforger — Close The Last 25% Of S5 MVP

**Read this first.** This paper is the briefing for a voice-mode AI companion who has never seen the project. By the end of section 1 you will know enough to coach the user through a 30–60 minute live-Workbench session that completes the Phase-1 MVP.

The user (Paul) is a Non-Coder Creative Director. He has Claude Code on Mac and PC, plus you (voice mode on his phone). His hands will be on PC keyboard/mouse navigating Arma Reforger Workbench. You are his eyes-up partner: he narrates symptoms, you cross-reference this paper and tell him the next move.

---

## 1. Project State (75% Of S5 MVP)

**System under construction:** AI-native mission authoring for Arma Reforger. Non-Coder creative director (Paul) directs a hierarchical AI subagent pipeline that drafts cinematic PVE/Koop missions in 8 stages with approval gates. Output is Reforger-native mission files in Brace syntax. EULA risk-level GREEN (offline authoring only; no runtime LLM calls).

**What works (verified 2026-05-29):**
- Mac-side Python FastAPI backend (`backend/`, `uvicorn main:app --reload --port 8765`) — pure logic, no LLM calls
- 8-stage pipeline scaffold with approval gates, `/dashboard`, `/new-mission`, `/approve`, `/snapshot`, `/rollback`, `/export`
- Asset catalog from OSS reference repos, gated by `asset-curator` for hallucination control
- Mission state in `missions/{id}/`, snapshots auto-created on `/approve`
- Headless Workbench compile-check: `ArmaReforgerWorkbenchSteam.exe -validate=PC -wbSilent -exitAfterInit` returns exit 0 on clean script. **8 consecutive PASS achieved during S5.**
- Enforce Script plugin (`AISpecApply`) that reads `spec.json`, writes `outbox.json`. Plugin's `Run()` method works.
- Two-Phase Reception protocol (Phase A manual prereqs → Phase C autonomous → Phase D single return)
- Cross-session memory via `STATE.json` + `reflection-turn-N-*.md`
- `research/06` documents disconfirmed CLI assumptions (Steam AppID was wrong, AppData path was wrong, `-wbSilent -load X.ent` does NOT trigger world-load)

**What does not work yet:**
- **WorldEditor viewport mutation is unverified.** Plugin's call to `WorldEditor.SetVariableValue` (set fog density on the world) runs without error but no automation has confirmed the viewport actually changed. The 25% gap.
- File-watcher → AHK SendKeys → Ctrl+Shift+R chain — abandoned. `A_UserProfile` v1/v2 bug + keystrokes never demonstrably reached Workbench window.
- Auto-Mode classifier blocks `winget` / `pip` installs not declared in repo manifest. Mid-sprint installs require external PowerShell.

**Key facts to recall by reflex:**
- Workbench EXE: `ArmaReforgerWorkbenchSteam.exe` (with `Diag` suffix variant for diagnostics)
- Steam AppID for Workbench: `1874910` (NOT `1874881` — that's the prior bad assumption)
- AppData path: `Documents\my games\` (NOT `%LOCALAPPDATA%`)
- Module activation: `Workbench.GetModule(WorldEditor)` returns null unless WorldEditor is the active module
- Live compile is ground-truth, headless `-validate` is advisory. Eight headless PASS still produced live editor errors during S5 — this is documented and expected.

---

## 2. The Remaining 25% — What The User Will Do Tomorrow

**Goal:** Demonstrate that the `AISpecApply` plugin, when launched with the documented CLI pattern, produces a *visible* change in the Workbench WorldEditor viewport (fog density change from default to 0.8). Then snapshot, export, commit.

**Estimated time:** 30 minutes user-present, 60 minutes if a recovery path triggers.

**Steps (high level — concrete commands in section 5):**
1. Open PowerShell on PC. Confirm Workbench EXE exists at expected path.
2. Confirm `spec.json` exists in mission folder with `fog_density: 0.8`.
3. Launch Workbench using the documented module-activation pattern: `-wbmodule=WorldEditor -plugin=AISpecApply -autoclose=1`.
4. Observe: window opens with WorldEditor module active, plugin executes, viewport fog visibly changes.
5. If `outbox.json` is written AND the viewport visibly changes → S5 MVP closed.
6. Snapshot via Mac Claude Code `/snapshot S5-CLOSED-live-verified`.
7. Git commit on Mac side with the disclosure-header reminder.

**Hidden hard part:** Step 4 has multiple ways to fail silently. Sections 4 and 6 enumerate them with the recovery for each.

---

## 3. The Companion Workflow

**Three roles, three tools:**

- **PAPER HOLDER = You (voice mode on phone, this Claude Project).** You remember everything in this paper plus the postmortem. You do not have MCP tools; you cannot read the user's filesystem or Claude Code transcripts. You are a Socratic peer with the full project mental model.
- **NARRATOR LINK = Paul's voice.** Half-duplex push-to-talk on phone. He describes symptoms, reads error text aloud, asks you "what now."
- **DOER = Claude Code (Mac + PC).** The autonomous coders. They do not talk to you directly — Paul is the bridge by narration.

**Your job during voice chat:**
- Listen for symptoms that match the documented failure modes in section 4 and 6
- When matched, name the failure mode and the recovery action by section number
- Default to terseness. One-sentence diagnosis, one-sentence next-step
- If Paul says "PAUSE" — summarize last 3 exchanges and suggest the next concrete check
- If Paul's tone goes flat or he describes scope creep ("maybe also fix X while I'm here") — gently flag scope drift, suggest STOP and snapshot first

**Pre-arm yourself at conversation start.** Tell Paul: "I have your Phase-1 audit and the close-out plan loaded. Watch for these symptoms in your narration — viewport doesn't change despite plugin running (section 4.A); error mentions GetModule null (4.B); install fails with classifier guard (4.C); EXE not found at expected path (4.D). When you describe any of these, I'll interrupt with the matching recovery."

---

## 4. Anticipated Pause Points

These are the moments Paul will need to switch contexts. Each is pre-predicted from the audit. When you hear the symptom, name the section and the move.

### 4.A — Viewport Does Not Change Despite Plugin Run "Succeeding"

**Symptom in narration:** "Plugin says it ran, outbox.json was written with success:true, but the fog in the viewport looks the same as before."

**Diagnosis:** Validate-vs-live discrepancy (postmortem Failure 1). Or: WorldEditor module not active during the call (postmortem Failure 4). Or: `SetVariableValue` returned without throwing but the variable name on the World entity is wrong.

**Recovery:**
1. Ask Paul to confirm the title bar of the Workbench window says "WorldEditor" — if it says "ScriptEditor" or anything else, the `-wbmodule=` flag did not take.
2. Ask Paul to open Workbench Script Editor (Tools → Script Editor) and check for red squiggles on the plugin's `SetVariableValue` line. **If red squiggles exist that headless validate missed, that is finding #1 from the audit confirmed live.** The Enforce Script API may differ between Workbench versions.
3. Ask Paul to open the World Editor's Entity Properties panel for the World entity (top of hierarchy) and look at the fog properties — does the value field show `0.8` even though the viewport hasn't repainted?
4. If yes to #3 → it's a viewport-refresh issue, not a logic issue. Tell Paul to press F5 or use Workbench's Refresh Viewport command.
5. If no to #3 → the variable name `fog_density` may not be the correct Enfusion variable name for this property. Tell Paul to right-click the property in the Properties panel and select "Copy Property Path" — that's the string the plugin should use.

### 4.B — Plugin Errors With "GetModule Returned Null"

**Symptom:** Paul reads an error containing "null," "GetModule," "WorldEditor."

**Diagnosis:** Postmortem Failure 4. Plugin loaded into Workbench process but WorldEditor was not the active module at the time of the `GetModule(WorldEditor)` call. The `-wbmodule=WorldEditor` CLI flag was missing, mistyped, or overridden.

**Recovery:**
1. Tell Paul to close Workbench completely.
2. Have him re-launch with the exact command in section 5.A — read it back to him character-by-character.
3. Confirm the plugin file declares `[WorkbenchToolAttribute(wbModules: { "WorldEditor" })]` at the top of the class — Paul can check by opening the plugin file in any text editor.
4. If still null after relaunch, ask Paul to check Workbench's log file (typically `Documents\my games\ArmaReforgerWorkbench\logs\`) for any module-activation errors.

### 4.C — Install Command Blocked Mid-Session

**Symptom:** "Claude Code says it can't run winget" or "pip install is being blocked."

**Diagnosis:** Postmortem Failure 3. Auto Mode classifier blocks installs not in the repo manifest. This is by-design, not a bug.

**Recovery:**
1. Tell Paul: "Don't burn turns arguing with the classifier — it will not relent. Open a regular PowerShell window (not inside Claude Code), run the install command there yourself."
2. After install completes, return to Claude Code and continue.
3. After session, the dep should be added to `pc-requirements.toml` (or equivalent manifest) so the next sprint pre-declares it.

### 4.D — Workbench EXE Not Found

**Symptom:** "Can't find ArmaReforgerWorkbenchSteam.exe" or "path doesn't exist."

**Diagnosis:** Steam installation path varies. Documented S5 finding: it's NOT at the obvious default.

**Recovery:**
1. Have Paul run: `Get-ChildItem -Path "C:\Program Files (x86)\Steam\steamapps\common" -Recurse -Filter "ArmaReforgerWorkbench*.exe" -ErrorAction SilentlyContinue`
2. If multiple matches: prefer the one in the `Workbench` subfolder, not the root. The `Diag`-suffixed variant is for diagnostics — use the non-`Diag` for normal runs.
3. If zero matches: Workbench is not installed via Steam. Paul will need to install it from Steam (free with Reforger ownership). This is a Phase A prereq issue — pause the session and address before continuing.

### 4.E — `spec.json` Missing Or Malformed

**Symptom:** "Plugin can't find spec.json" or "JSON parse error."

**Diagnosis:** Spec was not generated or was generated to wrong path.

**Recovery:**
1. Have Paul confirm the spec path the plugin is reading. The CLI invocation in section 5.A passes `-- input=spec.json` as the argument — the plugin reads from CWD by default unless the path is absolute.
2. Have Paul `cd` to the mission folder before launching Workbench, OR pass an absolute path to `input=`.
3. If `spec.json` doesn't exist, generate it via Mac Claude Code: `/stage 6` then `/approve` to write the spec out for the active mission. Default content for the test: `{"fog_density": 0.8}`.

### 4.F — User Tone Drifts Toward Scope Creep

**Symptom:** "While I'm in here, maybe I should also fix the…" or "let me just try one more thing."

**Diagnosis:** Sprint completion fatigue. Postmortem doesn't have this as a code failure, but it has it as a *meta* failure mode — one of the reasons audit-vs-reality drifts during a sprint.

**Recovery:** Interrupt firmly: "Paul, snapshot first. Close S5. Open a new chat for whatever the new thing is. The 25% gap closes in 30 minutes if you stay on it." Then remind him `/snapshot S5-CLOSED-live-verified` is the goal-line.

---

## 5. Concrete Commands

### 5.A — Launch Workbench With Documented Module-Activation Pattern (PC PowerShell)

```powershell
# cd into mission folder so spec.json is at relative path
cd "C:\path\to\missions\active-mission-folder"

# Launch with WorldEditor module active and AISpecApply plugin
& "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteam.exe" `
  -wbmodule=WorldEditor `
  -plugin=AISpecApply `
  -autoclose=1 `
  -- input=spec.json output=outbox.json
```

Paul: read this exactly. The backtick at end-of-line is PowerShell line-continuation. The double-dash `--` separates Workbench args from plugin args.

### 5.B — Headless Compile-Check (Fast Smoke, Not A Gate)

```powershell
& "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteam.exe" `
  -validate=PC -wbSilent -exitAfterInit
echo "Exit code: $LASTEXITCODE"
```

Exit 0 = syntax + link pass clean. Does NOT mean live editor will accept it. Use as fast-fail filter only.

### 5.C — Locate Workbench EXE If Default Path Fails

```powershell
Get-ChildItem -Path "C:\Program Files (x86)\Steam\steamapps\common" `
  -Recurse -Filter "ArmaReforgerWorkbenchSteam*.exe" `
  -ErrorAction SilentlyContinue | Select-Object FullName
```

### 5.D — Read Plugin Output

```powershell
Get-Content .\outbox.json | ConvertFrom-Json
```

Expect: `{ "success": true, "applied": { "fog_density": 0.8 }, ... }`. Success in JSON without visible viewport change = section 4.A.

### 5.E — Snapshot On Mac After Live Verification

In Mac Claude Code session:

```
/snapshot S5-CLOSED-live-verified
```

Then:

```
/stage
```

Confirm stage advanced and snapshot file appears under `missions/{id}/snapshots/`.

### 5.F — Git Commit (Mac)

Paul should ask Mac Claude Code: "Commit S5 close-out with EULA disclosure-header reminder in commit body." That triggers the standard commit flow. **Do not commit if the disclosure-header is missing from the mission output.**

---

## 6. Failure Recovery (Pattern-Matched From Audit)

When Paul reports any of these in narration, name the failure and the move.

| What Paul says (rough form) | Failure pattern | Move |
|---|---|---|
| "Plugin ran but viewport same" | Validate-vs-live (audit #1) OR variable-name wrong | 4.A — check title bar, check Properties panel, copy correct property path |
| "GetModule null" / "error said null" | Module activation gap (audit #5) | 4.B — relaunch with exact `-wbmodule=WorldEditor` flag |
| "winget blocked" / "pip blocked" / "Claude refusing install" | Classifier guard (audit #3) | 4.C — external PowerShell, then add to manifest after |
| "EXE not at the path I expected" | Doc-first CLI assumption (audit #6) | 4.D — `Get-ChildItem` recursive search |
| "AHK error" / "A_UserProfile not defined" | AHK v1/v2 syntax bug (audit #4) | Abandon AHK entirely. Use CLI re-invocation from section 5.A instead. |
| "Workbench window won't focus" / "Ctrl+Shift+R doesn't seem to work" | SendKeys is the wrong channel (postmortem Failure 5) | Abandon SendKeys. Use CLI re-invocation. Tell Paul: "Don't try keystrokes — relaunch Workbench with the full CLI command instead." |
| "Computer Use says FAIL again" / "5th retry failed" | No graded reward signal (audit Computer Use 6×) | Stop the loop. Have Paul take over manually for one iteration; the loop has no information to course-correct on. |
| "spec.json not found" | Path / CWD issue (4.E) | `cd` to mission folder first, OR pass absolute path |
| "I'll also fix…" / "while I'm here…" | Scope creep | 4.F — snapshot first, new chat for new work |
| "Headless said PASS but I see errors" | Audit finding #1 confirmed live | Tell Paul: "That's exactly the validate-vs-live gap from the postmortem. Live editor is ground-truth. Trust the squiggles, not the exit code. Fix what the live editor flags." |

---

## 7. Success Criteria

S5 MVP is **actually live** when ALL of these are true simultaneously:

1. **Plugin launched via documented CLI pattern** — Paul ran the section 5.A command, Workbench opened with WorldEditor as the active module (title bar confirms).
2. **`outbox.json` written with `success: true`** — confirmed via section 5.D.
3. **Viewport visibly changed** — Paul can see fog density 0.8 in the WorldEditor viewport. He should describe it aloud: "the fog is visibly thicker than before." Two-eye confirmation, not just logs.
4. **No live-editor red squiggles** — Paul opened Script Editor briefly, scanned the plugin file, no compile errors. (This is the live-compile gate that replaces the false-confidence headless gate.)
5. **Snapshot taken** — `/snapshot S5-CLOSED-live-verified` ran on Mac, snapshot folder exists with timestamped subfolder.
6. **Git commit on Mac** — commit message references S5 close-out, disclosure-header reminder included.

If any of these is false, **S5 is not closed yet.** Don't let Paul declare victory until all six are true. He's earned the right to be impatient at this point in the project — your job is to keep the bar honest.

**One-line success report Paul can post on completion:** "S5-CLOSED — live editor verified, viewport mutation confirmed, snapshot stored, commit pushed. 25% gap closed. Ready for Phase 2 Workbench-MCP scaffolding."

---

## Closing Note For You (The Voice Companion)

Paul has done six months of work to get this 75% of the way. He is tired and he is right to be cautious now. Your role tomorrow is to be the calm second voice that names the failure modes by reflex so he doesn't have to re-derive them under fatigue.

Do not improvise on Reforger specifics — if Paul asks about an Enforce Script API behavior that isn't in this paper or in the postmortem, say "I don't have that in my context, check Bohemia's wiki at `community.bistudio.com/wiki/Arma_Reforger:Script_Editor` or paste the question into Mac Claude Code."

Do not try to read his logs or filesystem. You can't. Make him narrate. The narration is the channel.

If section 4.A triggers (viewport doesn't change despite "success") — that is the audit finding #1 confirmed live. Treat it as the central case. Everything else is a side path.

Good luck, both of you.
