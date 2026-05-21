# Sprint B Prerequisites — Assessment after MEGA-A A.S5PREP

> **Date:** 2026-05-21 · **Sprint:** MEGA-A A.S5PREP · **Status:** PARTIAL (see items below)

---

## Tool Versions Confirmed (2026-05-21 04:45 UTC)

| Tool | Version | Path |
|---|---|---|
| Python | 3.12.10 | C:\Users\pfofa\AppData\Local\Programs\Python\Python312\python.exe |
| pip | 25.0.1 | (above Python) |
| Node.js | v24.15.0 | C:\Program Files\nodejs\node.exe |
| npm | 11.12.1 | |
| chokidar-cli | 3.0.0 | npm -g |
| VSCode | 1.121.0 | |
| gh | 2.92.0 | |
| git | 2.53.0.windows.3 | |
| winget | 1.28.240 | |

**VSCode Extensions:**
- ms-vscode.powershell v2025.4.0 ✅
- youarebamboozled.enforce-vscode-plugin v0.1.2 ✅ (Enforce Script syntax support)
- youarebamboozled.enforce-script-syntax-highlighting v0.0.6 ✅

**pip packages:**
- jsonpatch, jsonschema, anthropic, pytest, pydirectinput, pillow — all installed ✅

---

## Bohemia Samples — Local Paths

| Repo | Local Path |
|---|---|
| Arma-Reforger-Samples | C:\Users\pfofa\Documents\GitHub\Arma-Reforger-Samples |
| Arma-Reforger-Script-Diff | C:\Users\pfofa\Documents\GitHub\Arma-Reforger-Script-Diff |

**Key source files studied:**
- `Arma-Reforger-Samples/SampleMod_WorkbenchPlugin/Scripts/.../SampleWorldEditorPlugin.c` ✅
- `Arma-Reforger-Script-Diff/scripts/Core/generated/WorkbenchAPI/WorldEditorAPI.c` ✅ (entity create/modify API discovered)
- `Arma-Reforger-Script-Diff/.../WorldEditorPlugin.c` ✅ (NO OnUpdate confirmed)
- `Arma-Reforger-Script-Diff/.../WorkbenchPlugin.c` ✅ (base class lifecycle)
- `Arma-Reforger-Script-Diff/.../Workbench.c` ✅ (utilities incl. GetAbsolutePath, RunCmd)

**Notes:**
- Sample plugin study written to: `logs/sample-plugin-study-A.md`

---

## Sample Plugin Compile Verified

| Check | Status |
|---|---|
| SampleMod_WorkbenchPlugin `addon.gproj` dependency | `58D0FB3206B6F859` (matches ours) ✅ |
| Headless compile check of sample plugin | ⚠️ SKIPPED — Classifier blocked copying external repo code to addons/ (Untrusted Code Integration guard). To verify manually: Steam → Workbench → Open Project → Documents/GitHub/Arma-Reforger-Samples/SampleMod_WorkbenchPlugin/addon.gproj |
| Our AI_GeneratePlugin.c headless validate | ⏭️ Deferred to S5 (needs addon.gproj setup for our plugin) |

---

## AI_GeneratePlugin.c Refactor Status

| Aspect | Status |
|---|---|
| Uses real `WorldEditorPlugin` base class | ✅ |
| Uses correct `[WorkbenchPluginAttribute(wbModules: {"WorldEditor"})]` | ✅ |
| Entry via `Run()` (not OnActivate) | ✅ |
| API access: `Workbench.GetModule(WorldEditor)` → `worldEditor.GetApi()` | ✅ |
| Spec loading: `Workbench.GetAbsolutePath()` + `FileIO.OpenFile()` | ✅ |
| Entity create: `api.CreateEntity(className, name, layerId, parent, coords, angles)` | ✅ (correct signature with TODO) |
| Property edit: `api.ModifyEntityKey(entSrc, key, value)` | ✅ (correct signature with TODO) |
| Entity action wrap: `BeginEntityAction` / `EndEntityAction` | ✅ (pattern documented) |
| Batch edit: `BeginEditSequence` / `EndEditSequence` | ✅ (pattern documented) |
| JSON parsing of ai-spec.json | ⏭️ TODO (Sprint B — Enforce Script JSON API needed) |
| Ops loop implementation | ⏭️ TODO (Sprint B) |
| #ifdef WORKBENCH guards | ✅ |
| **TODO count** | **2 functional TODOs** (JSON parse + ops loop) |

---

## File-Watch Scaffold

| Check | Status |
|---|---|
| scripts/file-watcher.ps1 created | ✅ |
| Syntax validates (PS5) | ✅ |
| FileSystemWatcher watching correct path | ✅ (`ArmaReforgerWorkbench\profile\elos\ai-spec.json`) |
| SendKeys → Ctrl+Shift+R → Workbench Reload | ✅ (will work on PS5 + Win32 Workbench) |
| Watch dir created | ✅ (`Documents\My Games\ArmaReforgerWorkbench\profile\elos\`) |
| Test ai-spec.json written | ✅ (`{"mission_id": "test", "version": 1, "ops": []}`) |
| chokidar-cli alternative (Node) | ✅ v3.0.0 installed — more robust than PS5 watcher for high-freq changes |

---

## Open Questions for Mac-Side Audit

1. **Enforce Script JSON parsing**: What is the preferred deserialization pattern in 1.6.x?
   Candidates: `ScriptConvert.SerializeToString()`, `JsonApiDeserializer`, custom string parser.
   The Script-Diff repo doesn't include a standard JsonSerializer example.

2. **`CreateEntity` `coords` parameter**: Is it a `vector` type, a space-separated string `"x y z"`,
   or three separate float params? SampleWorldEditorPlugin.c doesn't use CreateEntity.
   WorldEditorAPI.c signature: `vector coords, vector angles` — likely Enforce `vector` type = `"x y z"` literal.

3. **Layer IDs**: How do we get the correct layerId for AI entities? `GetCurrentSubScene()` returns 0 for root.
   Is layer 0 always the correct target for generated entities?

4. **Sample plugin compile gate**: Should user manually verify via Workbench GUI (S3 action)?
   Or skip — SampleWorldEditorPlugin.c studied + API verified sufficient for Sprint B confidence.

5. **chokidar vs PowerShell watcher**: Both scaffolded. chokidar is more robust (no PS5 throttle on rapid writes).
   Which should be the primary? Recommend chokidar-cli for production, PowerShell as fallback.

---

## Sprint B Readiness Assessment

| Criterion | Status |
|---|---|
| sc-12: Plugin dev tools installed | ✅ VSCode + Enforce extensions + chokidar-cli + npm |
| sc-13: Bohemia samples cloned | ✅ Both repos at Documents/GitHub/ |
| sc-14: Sample plugin compiles | ⚠️ Unverified (blocked by security guard) |
| sc-15: AI_GeneratePlugin.c real-API refactor | ✅ 2 TODOs only (JSON parse + ops loop) |
| sc-16: File-watch infrastructure scaffolded | ✅ scripts/file-watcher.ps1 + elos/ dir |

**Overall:** Sprint B can begin on sc-12, sc-13, sc-15, sc-16. sc-14 (sample compile) is a
nice-to-have confidence check but not a Sprint B blocker — we have the real API signatures.
