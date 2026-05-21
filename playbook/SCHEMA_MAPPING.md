# Schema Mapping — narrative.json → WorldEditorAPI Calls

> **Stand:** 2026-05-21 · Sprint MEGA-A (A.S1.2)
> **Purpose:** Ground truth table linking narrative.json fields to the Enfusion
> WorldEditorAPI calls that AI_GeneratePlugin.c will use in Sprint B.
> Sources: SampleWorldEditorPlugin.c (Bohemia samples), research/11, research/01.

---

## Mapping Table

| narrative.json path | WorldEditorAPI call(s) | Enforce type | Sprint B status |
|---|---|---|---|
| `biome.map_id_ref` | `WorldEditorAPI.GetWorld().SetTerrainFile(path)` | `string` | TODO |
| `tone.primary` | No direct call — drives weather preset selection | `string` | Derived |
| `tone.color_palette_hint` | `SCR_WeatherManagerComponent.SetWeather(weatherPreset)` | `string` | TODO |
| `pacing.phase_N.ai_state` | `SCR_AIGroupComponent.SetCombatState(state)` | enum | TODO |
| `factions.player.id` | `SCR_FactionManager.GetFactionByKey(id)` | `string` | TODO |
| `factions.ai.id` | Same + assign to AI entities | `string` | TODO |
| `environment.time_of_day` | `ChimeraWorldDate.SetTime(hour, minute)` | `float` | TODO |
| `environment.fog_density` | `SCR_FogManagerComponent.SetFogDensity(density)` | `float` (0-1) | **PRIORITY P1 for Sprint B** |
| `environment.fog_distance` | `SCR_FogManagerComponent.SetFogDistance(dist)` | `float` | TODO |
| `entities[*].class` | `WorldEditorAPI.CreateEntity(className, worldPos)` | `string` | TODO |
| `entities[*].prefab_guid` | `Resource.Load(prefabPath)` + spawn | GUID string | TODO |
| `entities[*].coords` | `entity.SetOrigin(vector)` | `vector` (x,y,z) | TODO |
| `entities[*].props` | `entity.SetProperty(key, value)` per field | mixed | TODO |

---

## Enfusion WorldEditorAPI — Discovered Methods (from Script-Diff repo)

From `WorkbenchAPI/Plugins/WorldEditorPlugin.c`:
```c
class WorldEditorPlugin : WorkbenchPlugin
{
    // Lifecycle hooks (ALL available in plugin)
    void Run();                      // Entry point when user triggers plugin
    void Configure();                // Settings dialog

    // World access
    IEntitySource CreateEntitySource(string className, vector origin);
    void DeleteEntitySource(IEntitySource src);
    void SelectEntities(array<IEntity> entities);

    // Script reload (triggered by Ctrl+Shift+R via external file-watcher)
    // No OnUpdate / OnFrame — external watcher calls Run()
}
```

From `WorkbenchAPI/Workbench.c`:
```c
class Workbench
{
    // I/O
    static string GetAbsolutePath(string resourcePath);
    static string OpenFile(string title, string filter);
    static void OpenResource(ResourceName res);

    // Process
    static bool RunCmd(string command, string args, bool waitForFinish);
    static void RunProcess(string process, string args);

    // Dialog
    static void Dialog(string title, string message);
}
```

---

## op-type → API Call Matrix (Sprint B targets)

| op | narrative field | Primary API call | Secondary |
|---|---|---|---|
| `attribute-edit` | `tone.primary` → weather preset | `SCR_WeatherManagerComponent.SetWeather()` | `SCR_SunController` |
| `attribute-edit` | `environment.fog_density` | `SCR_FogManagerComponent.SetFogDensity()` | — |
| `entity-create` | `entities[+]` | `WorldEditorAPI.CreateEntitySource()` | `Resource.Load(prefab)` |
| `entity-delete` | `entities[-]` | `WorldEditorAPI.DeleteEntitySource()` | — |
| `entity-move` | `entities[x].coords` | `entity.SetOrigin(vector)` | — |
| `batch` | `entities[*]` | Loop over entity ops | — |

---

## File-watch → Plugin Trigger Chain

```
User/Agent writes ai-spec.json
       ↓
chokidar / PowerShell FileSystemWatcher detects change
       ↓
SendKeys: Ctrl+Shift+R into Workbench window
       ↓
Workbench: "Reload WB Scripts" executes
       ↓
AI_GeneratePlugin.Run() is called
       ↓
Plugin reads ai-spec.json (Workbench.GetAbsolutePath + FileIO)
       ↓
Plugin applies ops via WorldEditorAPI
       ↓
World updates in viewport, file saved
```

**Latency floor (per research/11):**
- With sendkey hack: 1-2s P50
- Manual hotkey (Shift+F7): 5-10s
- CLI headless (`-plugin=AI_GeneratePlugin`): 10-20s

---

## Open Questions for Mac-Side Audit

1. `SCR_FogManagerComponent` — verified in Script-Diff repo, but exact
   setter signature needs Sprint B empirical test.
2. `ChimeraWorldDate.SetTime()` — found in WorldEditorPlugin.c sample,
   needs version-specific validation (Workbench 1.6.x).
3. Entity prefab GUID format: `{GUID}` or unbraced? Samples use unbraced in
   script calls but braced in .gproj — need to confirm parser expectation.
4. `WorldEditorAPI.CreateEntitySource()` — confirmed from SampleWorldEditorPlugin.c;
   Sprint B must test if async or sync.
