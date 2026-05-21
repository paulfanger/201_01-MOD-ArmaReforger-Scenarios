# Sample Plugin Study — Sprint MEGA-A A.S5PREP.2

> **Source:** `Arma-Reforger-Samples` + `Arma-Reforger-Script-Diff` (both cloned 2026-05-21)
> **Purpose:** Ground truth for refactoring AI_GeneratePlugin.c with real WorldEditorAPI

---

## File 1: SampleWorldEditorPlugin.c

```
Path: Arma-Reforger-Samples/SampleMod_WorkbenchPlugin/Scripts/WorkbenchGame/SamplePlugins/SampleWorldEditorPlugin.c
```

**Summary:** Minimal `WorldEditorPlugin` subclass that demonstrates the plugin entry-point pattern:
`Run()` fetches the `WorldEditor` module via `Workbench.GetModule(WorldEditor)`, gets the API via
`worldEditor.GetApi()`, then calls `api.GetSelectedEntitiesCount()` and logs the result via `Print()`.
This confirms the access pattern: `WorldEditorAPI api = (WorldEditor)Workbench.GetModule(WorldEditor)).GetApi()`.

---

## File 2: SampleMod_WorkbenchPlugin/addon.gproj

**Summary (from disk):**
```
GameProject {
 ID "SampleMod_WorkbenchPlugin"
 GUID "{...}"
 TITLE "Sample - Workbench Plugins"
 Dependencies { "58D0FB3206B6F859" }
}
```
Same dependency on vanilla ArmaReforger (`58D0FB3206B6F859`) as our missions — confirms our GUID was correct.
Vanilla junctions must be active for this to compile in Workbench-Diag.

---

## File 3: WorkbenchAPI/Plugins/WorkbenchPlugin.c (base class)

**Summary:** Abstract base for ALL plugins. Only 4 lifecycle hooks: `Run()` (triggered by menu/shortcut),
`RunCommandline()` (headless CLI invocation), `Configure()` (settings dialog), `OnResourceContextMenu()`.
**CONFIRMS research/11: NO OnUpdate, NO OnFrame, NO tick-events.** External file-watcher + sendkey hack
is mandatory for any kind of "reactive" behavior.

---

## File 4: WorkbenchAPI/Plugins/WorldEditorPlugin.c

**Summary:** Extends `WorkbenchPlugin` with 2 additional event hooks: `OnGameModeStarted(worldName, gameMode, ...)`
and `OnGameModeEnded()`, plus `OnWorldEditWindowDataDropped(...)` for drag-and-drop support.
Neither `OnGameModeStarted` nor `OnWorldEditWindowDataDropped` are useful for AI-spec apply-on-demand —
`Run()` remains the only viable entry point for our use case.

---

## File 5: WorkbenchAPI/Workbench.c (utilities)

**Summary:** Static utility class. Key methods: `GetModule(typename)` for accessing editor modules,
`GetAbsolutePath(relativePath, out absPath)` for resolving resource paths (critical for reading ai-spec.json),
`RunCmd(command)` for shell-outs, `GenerateGloballyUniqueID64()` for GUID minting.
`Dialog(caption, text)` can surface errors to user without crashing plugin.

---

## BONUS: WorldEditorAPI.c (entity manipulation)

```c
// CRITICAL method signatures (Sprint B needs these):
proto external IEntitySource CreateEntity(string className, string name, int layerId, IEntitySource parent, vector coords, vector angles);
proto external IEntitySource CreateEntityExt(string className, string name, int layerId, IEntitySource parent, vector coords, vector angles, int traceFlags);
proto external bool DeleteComponent(IEntitySource owner, IEntityComponentSource component);
proto external bool ModifyEntityKey(notnull IEntitySource ent, string key, string value);  // set any property key
proto external bool BeginEntityAction(string historyPointName);
proto external bool EndEntityAction(string historyPointName);
proto external bool BeginEditSequence(IEntitySource entSrc);  // batch edits without re-init
proto external bool EndEditSequence(IEntitySource entSrc);
proto external IEntitySource FindEntityByName(string name);
proto external IEntitySource FindEntityByID(EntityID id);
proto external bool RenameEntity(notnull IEntitySource ent, string newName);
```

**ModifyEntityKey is the universal setter** — takes entity + key string + value string. Covers all
property edits without needing type-specific setters. This is how fog_density, time_of_day, etc. will be set.

---

## Key Takeaways for AI_GeneratePlugin.c Refactor

1. Entry: `[WorkbenchPluginAttribute(name: "AI Generate", wbModules: {"WorldEditor"})]`
2. Access: `WorldEditor worldEditor = Workbench.GetModule(WorldEditor); WorldEditorAPI api = worldEditor.GetApi();`
3. JSON loading: `Workbench.GetAbsolutePath("$profile:elos/ai-spec.json", absPath)` → `FileIO.OpenFile(absPath, FileMode.READ)` → read string → parse via JsonApiDeserializer
4. Entity creation: `api.BeginEntityAction("AI-Op"); api.CreateEntity(className, name, layerId, null, coords, angles); api.EndEntityAction("AI-Op");`
5. Property setting: `api.BeginEntityAction("AI-Prop"); api.ModifyEntityKey(entSrc, "fogDensity", "0.9"); api.EndEntityAction("AI-Prop");`
6. File-watch trigger: External chokidar/PowerShell watcher → `SendKeys Ctrl+Shift+R` → Workbench "Reload WB Scripts" → `Run()` called
