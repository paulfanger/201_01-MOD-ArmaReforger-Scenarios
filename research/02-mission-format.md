# Mission File Format — Reforger 2026

> **Investigation goal:** Can an external backend generate valid Arma Reforger mission files programmatically, without Workbench UI?
> **TL;DR:** Yes for the text-based files (`.conf`, `.gproj`, `.ent`, `.layer`), but you cannot avoid the Workbench for: (a) packaging into the publishable bundle, (b) building data per platform, (c) generating GUIDs that the engine recognises in `.meta` files, and (d) any asset that has to be pre-baked (navmesh, terrain BSP). Mission *content* generation is realistic; mission *publishing* is not headless-friendly on macOS (Workbench is Windows-only).

---

## Overview

The minimum publishable Coop scenario consists of roughly six text files plus their meta-sidecars, anchored by a single `.gproj` and a single `MissionHeader.conf` that references one `.ent` (world) which loads sibling `.layer` files. Visual:

```
MyCoopAddon/
├── addon.gproj                    # Project root. ID + GUID + dependencies.
├── Missions/
│   ├── MyCoop.conf                # SCR_MissionHeader → references World
│   └── MyCoop.conf.meta           # Resource manifest (autogen by Workbench)
└── Worlds/
    ├── MyCoop.ent                 # Layer table OR SubScene { Parent ... }
    ├── MyCoop.ent.meta
    ├── MyCoop_gamemode.layer      # GameMode prefab, FactionManager, LoadoutManager
    ├── MyCoop_managers.layer      # Map, Camera, TimeAndWeather, Radio, Chat, Tasks
    ├── MyCoop_AI.layer            # Static AI groups + waypoints
    ├── MyCoop_tasks.layer         # SCR_*Task instances (Eliminate/Move/Defend/…)
    ├── MyCoop_triggers.layer      # SCR_BaseTriggerEntity + SCR_AISpawnerComponent
    ├── MyCoop_spawnpoints.layer   # SCR_SpawnPoint entities for players
    └── MyCoop_environment.layer   # Static props, weather, lighting overrides
```

**Smallest possible variant** (verified, see SampleMod_Main below): a single `.gproj`, a single `.conf` that names a World, and one `.ent` that `SubScene`-extends an existing world. Everything else is optional layering.

---

## File-by-File Anatomy

> **Source files** below are real text from these public repos (not invented):
>   - `exocs/Reforger-Sample-Coop` ([github](https://github.com/exocs/Reforger-Sample-Coop)) — the canonical "minimal coop" sample
>   - `Kexanone/CombatOpsEnhanced_AR` ([github](https://github.com/Kexanone/CombatOpsEnhanced_AR)) — production-grade scenario inheritance
>   - `gruppe-adler/GRAD-COOP-Template-Reforger` ([github](https://github.com/gruppe-adler/GRAD-COOP-Template-Reforger)) — Game Master coop template
>   - `BohemiaInteractive/Arma-Reforger-Samples` ([github](https://github.com/BohemiaInteractive/Arma-Reforger-Samples)) — Bohemia's official samples

### `addon.gproj`

**Purpose:** Project descriptor. Workbench uses this to mount the project tree and resolve cross-project asset references via dependency GUIDs.

**Schema:** Plain-text "Enfusion Resource Format" (ERF) — a brace-delimited key/value DSL. Order of keys does not appear to matter, but case does.

**Annotated example** (real, from `Reforger-Sample-Coop/SampleCoop/addon.gproj`):
```text
GameProject {
 ID "SampleCoop"                  # Internal identifier, used in folder & launch
 GUID "5966E5428E081A6C"          # 16-hex-char project ID. Unique. Engine-generated.
 TITLE "SampleCoop"               # Display name in launcher / Workbench
 Dependencies {                   # GUIDs of upstream addons this needs
  "58D0FB3206B6F859"              #   → ArmaReforger core (always required)
 }
}
```

The full-featured form (from `GRAD-COOP-Template-Reforger/addon.gproj`) adds `Configurations { GameProjectConfig PC { … HEADLESS { … } … } }` blocks per platform, where Workbench writes language tables, WidgetManager settings, etc.

**Required fields:** `ID`, `GUID`, `TITLE`, `Dependencies { "58D0FB3206B6F859" }` (core).
**Optional fields:** `Configurations { GameProjectConfig <PLATFORM> { … } }` per target.
**Source:** `/tmp/Reforger-Sample-Coop/SampleCoop/addon.gproj`, `/tmp/GRAD-COOP-Template-Reforger/addon.gproj`.

---

### `Missions/<name>.conf` — Mission Header

**Purpose:** Tells Reforger this scenario exists; provides menu metadata, points at world, sets game-mode rules. Must contain exactly one root class instance.

**Schema:** A single class block whose class name must extend `MissionHeader`. The two canonical options:
- `SCR_MissionHeader { … }` — base scripted header.
- `SCR_MissionHeaderCampaign { … }` — adds Conflict-mode fields.
- Custom subclasses (`COE_MissionHeader`, etc.) are allowed when the addon defines them in `.c` scripts.

Class fields come from the script declaration via `[Attribute(...)]` annotations. The full inventory of `SCR_MissionHeader` fields was sourced from `arexplorer.zeroy.com/_s_c_r___mission_header_8c_source.html`.

**Annotated example #1 — minimal viable** (real, from `Reforger-Sample-Coop/SampleCoop/Missions/CoopTest.conf`):
```text
SCR_MissionHeader {
 World "{E6945F6DC070C755}Worlds/CoopTest.ent"   # GUID + relative path
 m_sName "Coop Test Scenario"
 m_sGameMode "Coop"
 m_iPlayerCount 8
}
```

**Annotated example #2 — production-grade with inheritance** (real, from `CombatOpsEnhanced_AR/.../Missions/COE_Eden_US.conf`):
```text
COE_MissionHeader : "{08F4BF055DCA172B}Configs/MissionHeaders/COE_Eden.conf" {
 m_sName "Combat Ops Enhanced - Everon (US)"
 m_aCOE_OpposingFactionsConfigs {
  COE_OpposingFactionsConfig "{5F0538AABA889566}" {
   m_sPlayerFactionKey "US"
   m_sEnemyFactionKey "USSR"
  }
 }
}
```
The `Class : "{GUID}path/to/parent.conf" { … }` syntax means *inherit from*, then override fields. This is how COE keeps one base header and spins per-faction variants in 8 lines.

**Required fields** (engine will reject without them):
- `World` — `"{GUID}Worlds/<file>.ent"` reference.

**Strongly recommended:**
- `m_sName` — visible in menu (blank = "Untitled").
- `m_sGameMode` — string tag, the canonical values are `"Sandbox"` (default), `"Coop"`, `"Conflict"`, `"GameMaster"`.
- `m_iPlayerCount` — slot count.

**All `SCR_MissionHeader` fields** (verified from script source):

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `m_sName` | string | `""` | Display name |
| `m_sAuthor` | string | `""` | Author credit |
| `m_sPath` | string | `""` | Mission path (rarely written manually) |
| `m_sDescription` | string | `""` | Short blurb |
| `m_sDetails` | string | `""` | Long briefing text (supports `#KEY` localisation refs) |
| `m_sIcon` | ResourceName | `"{...}UI/Textures/WorldSelection/Default.edds"` | GUID + .edds path |
| `m_sLoadingScreen` | ResourceName | `"{...}placeholder_1.edds"` | GUID + .edds path |
| `m_sPreviewImage` | ResourceName | `"{...}placeholder_1.edds"` | GUID + .edds path |
| `m_sGameMode` | string | `"Sandbox"` | `Coop`, `Conflict`, `GameMaster`, `Sandbox` |
| `m_iPlayerCount` | int | `1` | If > 1, mission is treated as multiplayer |
| `m_eEditableGameFlags` | EGameFlags bitmask | `0` | Which flags players can toggle in lobby |
| `m_eDefaultGameFlags` | EGameFlags bitmask | `0` | Default lobby setting |
| `m_bIsSavingEnabled` | bool | `0` | Allow save/load |
| `m_sSaveFileName` | string | `""` | Slot name when saving |
| `m_sBriefingConfig` | ResourceName | `""` | Briefing screen config |
| `m_bOverrideScenarioTimeAndWeather` | bool | `0` | If 1, the next 5 fields take effect |
| `m_iStartingHours` | int | `8` | 0–23 |
| `m_iStartingMinutes` | int | `0` | 0–59 |
| `m_bRandomStartingDaytime` | bool | `0` | Overrides hour/minute |
| `m_fDayTimeAcceleration` | float | `1.0` | Day-time multiplier |
| `m_fNightTimeAcceleration` | float | `1.0` | Night-time multiplier |
| `m_bRandomStartingWeather` | bool | `0` | |
| `m_bRandomWeatherChanges` | bool | `0` | Mid-game shifts |
| `m_fXpMultiplier` | float | `1.0` | |
| `m_bMapMarkerEnableDeleteByAnyone` | bool | — | Faction-level marker delete |
| `m_iMapMarkerLimitPerPlayer` | int | `10` | |
| `m_bLoadOnStart` | bool | — | |
| `m_sOwner` | string | — | |

**`SCR_MissionHeaderCampaign`** adds: `m_iControlPointsCap`, `m_fVictoryTimeout`, `m_iStartingHQSupplies`, `m_iMinimumBaseSupplies`, `m_iMaximumBaseSupplies`, `m_bCustomBaseWhitelist`, `m_bIgnoreMinimumVehicleRank`, `m_aCampaignCustomBaseList`.

**Sidecar file:** Every `.conf` has a `.conf.meta` sibling (auto-generated by Workbench on first save) that maps the file's own GUID and platform config classes. **BEST INFERENCE, NOT VERIFIED:** the `.meta` is regenerated by Workbench whenever it inspects the resource; backend can probably stub it but the GUID inside *must* be unique and 16 hex chars upper case.

**Sources:** `/tmp/Reforger-Sample-Coop/SampleCoop/Missions/CoopTest.conf`, `arexplorer.zeroy.com/_s_c_r___mission_header_8c_source.html`, `xgamingserver.com/docs/arma-reforger/mission-header`.

---

### `Worlds/<name>.ent` — World / Scene File

**Purpose:** The world entity tree root. Two patterns:

1. **Inherit-from-base-world** (when you put your scenario *on top of* Eden/Arland):
```text
SubScene {
 Parent "worlds/Eden/Eden.ent"
}
```
This is what GRAD does for `GRAD_GM_Eden.ent`, COE does for `COE/Eden/Eden.ent`, and Sample Mod does for `Assets_Showcase_Basic.ent`. The whole base world (terrain, navmesh, vegetation) loads from the dependency; you only contribute layers.

2. **Self-contained world** (only used for truly new terrains, like the `CoopTest.ent` test island):
```text
Layer default     { Index 0 }     # Master layer list — order matches *_<name>.layer files
Layer managers    { Index 1 }
Layer gamemode    { Index 2 }
Layer environment { Index 3 }
Layer triggers    { Index 4 }
Layer AI          { Index 5 }
Layer comments    { Index 6 }
Layer tasks       { Index 7 }
```
Each `Layer <name> { Index N }` declaration corresponds to a sibling file `<world>_<name>.layer` that holds the actual entities.

**Required:**
- Either `SubScene { Parent "<path>" }` *or* a `Layer … { Index N }` table.

**Source:** `/tmp/Reforger-Sample-Coop/SampleCoop/Worlds/CoopTest.ent`, `/tmp/GRAD-COOP-Template-Reforger/Worlds/GRAD_GM_Eden.ent`, `/tmp/Arma-Reforger-Samples/SampleMod_Main/Worlds/Modding/Assets_Showcase_Basic.ent`.

---

### `Worlds/<name>_<layer>.layer` — Entity Layers

**Purpose:** Contains a flat list of entity instances (one per logical world slice). Loaded in order; positions in world-space.

**Schema:** Sequence of entity declarations. The general grammar (inferred from all observed files):

```text
<ClassName> <InstanceName>? : "{GUID}<prefab/path>.et" {
 ID "<HEXID>"?                # Optional persistent ID
 coords X Y Z                 # World position
 angleX <deg>                 # Optional rotation
 angleY <deg>
 angleZ <deg>
 <field> <value>              # Class-specific fields
 components {
  <ComponentClass> "{GUID}" { <fields> }
 }
 { <nested-children-block> }   # Children attached to this entity
}

# Grouping form — multiple instances of one prefab
$grp <ClassName> : "{GUID}<prefab>.et" {
 <NamedInstance1> { coords X Y Z … }
 <NamedInstance2> { coords X Y Z … }
}
```

**Annotated GameMode layer** (real, from `CoopTest_gamemode.layer`):
```text
SCR_AIWorld : "{E0A05C76552E7F58}Prefabs/AI/SCR_AIWorld.et" {}
PerceptionManager PerceptionManager1 : "{028DAEAD63E056BE}Prefabs/World/Game/PerceptionManager.et" {}
SCR_BaseGameMode GameMode : "{904EC091C347AEA9}Prefabs/MP/Modes/Coop/CoopGameMode.et" {
 components {
  SCR_RespawnMenuHandlerComponent "{5966E56DB0ABC25D}" {}
 }
}
SCR_FactionManager FactionManager : "{E4075339B4E24E10}Prefabs/MP/Managers/Factions/CoopFactionManager.et" {}
SCR_LoadoutManager LoadoutManager : "{0C4D399744D5B3FD}Prefabs/MP/Managers/Loadouts/CoopLoadoutManager.et" {}
SCR_SpawnPoint SpawnPoint_US : "{CEA2B24051A44525}PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et" {
 coords 263 9 245
 angleY -60
 m_Info SCR_UIInfo "{56B4CC4ECACA2C37}" {
  Name "Mustang"
 }
}
```

**Annotated AI layer** (real, from `CoopTest_AI.layer`):
```text
$grp SCR_AIWaypoint : "{750A8D1695BD6998}Prefabs/AI/Waypoints/AIWaypoint_Move.et" {
 WP3 { coords 24.115 10.001 250.042 }
 WP4 { coords 24.115 10.001 287.042 }
 WP5 { coords 67.615 10.001 195.042 }
}
$grp SCR_DefendWaypoint : "{93291E72AC23930F}Prefabs/AI/Waypoints/AIWaypoint_Defend.et" {
 WP1 { coords 190.218 10.001 207.565 }
 WP2 { coords 190.218 10.001 309.065 }
}
SCR_AIGroup StaticGroup : "{A2F75E45C66B1C0A}Prefabs/Groups/OPFOR/Group_USSR_MachineGunTeam.et" {
 coords 85.159 10.001 178.148
 m_aStaticWaypoints {           # AI patrols these waypoints in order
  "WP4" "WP5" "WP1"
 }
}
```

**Annotated Tasks layer** (real, from `CoopTest_tasks.layer`):
```text
SCR_TriggerTask MoveTask_1 : "{7259F0B101761BD5}Prefabs/Tasks/MoveTask.et" {
 coords 263 10 270
 m_sName "Move to red trigger!"
 m_sDescription "Immediately!"
 m_eAssignMessage NONE
 m_eUnassignMessage NONE
 {
  SCR_BaseFactionTriggerEntity {
   ID "55D072570E7E8ABF"
   coords 0 0 0
   SphereRadius 2
   m_sOwnerFactionKey "US"
  }
 }
}
$grp SCR_EliminateTask : "{B866318EB7E84833}Prefabs/Tasks/EliminateTask.et" {
 EliminateTaskB { coords 86.897 10.001 176.849 }
 EliminateTaskA {
  coords 239.915 10.001 270.184
  m_sName "Eliminate UAZ"
 }
}
```

**Annotated Trigger/Spawner layer with inlined Enfusion-Script** (real, from `CoopTest_triggers.layer`):
```text
$grp SCR_BaseTriggerEntity : "{3F294A5E2B52B65E}Prefabs/MP/Triggers/CoopTriggerSpawner.et" {
 DynamicTriggerSpawn2 {
  components {
   SCR_AISpawnerComponent "{5966F2A840D93A01}" {
    m_rnDefaultPrefab "{30ED11AA4F0D41E5}Prefabs/Groups/OPFOR/Group_USSR_FireGroup.et"
    m_vSpawnPosition 207.415 10 269.989
    m_vSpawnRotation 0 40 0
   }
   RplComponent "{5966F2A87A6B4E62}" {}
  }
  coords 240 10 260
  userScript "	protected SCR_AISpawnerComponent m_pSpawner;"
  SphereRadius 2
  EOnInit ""\
  "		super.EOnInit(owner);"\
  "		m_pSpawner = SCR_AISpawnerComponent.Cast(owner.FindComponent(SCR_AISpawnerComponent));"\
  …
 }
}
```
That last block proves layers can embed Enfusion Script verbatim as quoted lines joined with `\` continuations — important for backend generation: scripts are first-class string content.

**Required:** at minimum, declarations are well-formed `Class { coords X Y Z }` blocks. There is no required field common to all entity classes — required-ness is per-class.

**Sources:** `/tmp/Reforger-Sample-Coop/SampleCoop/Worlds/*.layer`, `/tmp/CombatOpsEnhanced_AR/optionals/COE_Kunar_Compat/worlds/COE/Kunar/Kunar_Layers/*.layer`.

---

### `.meta` Sidecars (`.conf.meta`, `.ent.meta`, `.et.meta`)

**Purpose:** Resource manifest for the Workbench's resource database. Maps a file to its GUID and declares platform-specific resource configurations.

**Annotated example** (real, from `CoopTest.conf.meta`):
```text
MetaFileClass {
 Name "{85A748EB80EE1051}Missions/CoopTest.conf"     # Self-reference GUID + path
 Configurations {
  CONFResourceClass PC          {}                   # Per-platform overrides go here
  CONFResourceClass XBOX_ONE : PC {}                 # Inherit PC's behaviour
  CONFResourceClass XBOX_SERIES : PC {}
  CONFResourceClass PS4 : PC {}
  CONFResourceClass HEADLESS : PC {}
 }
}
```
The class suffix (`CONFResourceClass`, `ENTResourceClass`, `ETResourceClass`) maps to the data type of the parent file.

**BEST INFERENCE, NOT VERIFIED:** Workbench regenerates these on save; backend can probably emit them with stub config blocks. The GUID must match what the engine sees when it scans the resource — meaning if you fabricate a GUID, you must be self-consistent with all *references* to it in other files.

---

## Minimum Viable Mission Schema (JSON-Schema, draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ReforgerMVPMission",
  "description": "Programmatic representation of the smallest valid Reforger coop mission. Backend serialises to Enfusion .conf/.ent/.layer text.",
  "type": "object",
  "required": ["project", "missionHeader", "world"],
  "properties": {
    "project": {
      "type": "object",
      "required": ["id", "guid", "title"],
      "properties": {
        "id":           { "type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_.\\- ]{0,63}$" },
        "guid":         { "type": "string", "pattern": "^[0-9A-F]{16}$",
                          "description": "16-char uppercase hex. Must be globally unique. BEST INFERENCE, NOT VERIFIED: generation rule is opaque; copy-and-bump from existing or use random uppercase hex." },
        "title":        { "type": "string" },
        "dependencies": {
          "type": "array",
          "items": { "type": "string", "pattern": "^[0-9A-F]{16}$" },
          "default": ["58D0FB3206B6F859"],
          "description": "Must include core Arma Reforger GUID 58D0FB3206B6F859."
        }
      }
    },
    "missionHeader": {
      "type": "object",
      "required": ["filename", "guid", "worldRef"],
      "properties": {
        "filename":     { "type": "string", "pattern": "^Missions/.+\\.conf$" },
        "guid":         { "type": "string", "pattern": "^[0-9A-F]{16}$" },
        "class":        { "enum": ["SCR_MissionHeader", "SCR_MissionHeaderCampaign"], "default": "SCR_MissionHeader" },
        "extendsConf":  { "type": ["string","null"], "description": "Optional parent .conf for inheritance, formatted as '{GUID}path.conf'." },
        "worldRef":     { "type": "string", "pattern": "^\\{[0-9A-F]{16}\\}.+\\.ent$" },
        "fields": {
          "type": "object",
          "properties": {
            "m_sName":               { "type": "string" },
            "m_sAuthor":             { "type": "string" },
            "m_sDescription":        { "type": "string" },
            "m_sDetails":            { "type": "string" },
            "m_sIcon":               { "type": "string", "pattern": "^\\{[0-9A-F]{16}\\}.+\\.edds$" },
            "m_sLoadingScreen":      { "type": "string", "pattern": "^\\{[0-9A-F]{16}\\}.+\\.edds$" },
            "m_sPreviewImage":       { "type": "string", "pattern": "^\\{[0-9A-F]{16}\\}.+\\.edds$" },
            "m_sGameMode":           { "enum": ["Sandbox", "Coop", "Conflict", "GameMaster"], "default": "Coop" },
            "m_iPlayerCount":        { "type": "integer", "minimum": 1, "maximum": 256 },
            "m_eEditableGameFlags":  { "type": "integer" },
            "m_eDefaultGameFlags":   { "type": "integer" },
            "m_bIsSavingEnabled":    { "type": "boolean" },
            "m_sSaveFileName":       { "type": "string" },
            "m_bOverrideScenarioTimeAndWeather": { "type": "boolean" },
            "m_iStartingHours":      { "type": "integer", "minimum": 0, "maximum": 23 },
            "m_iStartingMinutes":    { "type": "integer", "minimum": 0, "maximum": 59 },
            "m_bRandomStartingDaytime": { "type": "boolean" },
            "m_fDayTimeAcceleration":   { "type": "number" },
            "m_fNightTimeAcceleration": { "type": "number" },
            "m_bRandomStartingWeather": { "type": "boolean" },
            "m_bRandomWeatherChanges":  { "type": "boolean" },
            "m_fXpMultiplier":          { "type": "number" }
          }
        }
      }
    },
    "world": {
      "type": "object",
      "required": ["filename", "guid"],
      "properties": {
        "filename": { "type": "string", "pattern": "^Worlds/.+\\.ent$" },
        "guid":     { "type": "string", "pattern": "^[0-9A-F]{16}$" },
        "mode": {
          "oneOf": [
            { "type": "object", "required": ["subSceneParent"],
              "properties": { "subSceneParent": { "type": "string", "description": "Base world to inherit, e.g. 'worlds/Eden/Eden.ent'." } } },
            { "type": "object", "required": ["layers"],
              "properties": {
                "layers": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": ["name", "index"],
                    "properties": {
                      "name": { "type": "string", "enum": ["default","managers","gamemode","environment","triggers","AI","tasks","comments","spawnpoints"] },
                      "index": { "type": "integer", "minimum": 0 }
                    }
                  }
                }
              }
            }
          ]
        }
      }
    },
    "layers": {
      "type": "object",
      "description": "Each key is a layer name (managers/gamemode/AI/…); each value is a list of entity declarations.",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["className", "prefabRef"],
          "properties": {
            "className":   { "type": "string", "description": "e.g. SCR_SpawnPoint, SCR_AIGroup, SCR_EliminateTask" },
            "instanceName":{ "type": ["string","null"] },
            "prefabRef":   { "type": "string", "pattern": "^\\{[0-9A-F]{16}\\}.+\\.et$",
                             "description": "MUST be an existing prefab from a dependency. Backend must NEVER fabricate GUIDs here." },
            "coords":      { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
            "angleX":      { "type": "number" },
            "angleY":      { "type": "number" },
            "angleZ":      { "type": "number" },
            "fields":      { "type": "object", "additionalProperties": true },
            "components":  { "type": "array", "items": { "type": "object" } },
            "children":    { "type": "array", "items": { "$ref": "#/properties/layers/additionalProperties/items" } }
          }
        }
      }
    }
  }
}
```

Markers:
- `MISSING:` how Workbench computes the .meta `Configurations` block per platform — best inference: emit a default 5-platform block (PC + 4 inheritors) and let the engine accept it.
- `MISSING:` whether a `.gproj.meta` exists — observed samples don't have one.

---

## Validation Rules — what breaks a mission

Confirmed-from-observed-failures + per-wiki notes:

1. **Missing `Dependencies { "58D0FB3206B6F859" }`** in `addon.gproj` → mod will not load (every mod implicitly needs the core).
2. **GUID collision in two `.meta` files** → resource manager drops one, leading to "missing resource" errors at scenario list time.
3. **`World` field in MissionHeader points to a GUID/path that doesn't exist** in the project or any dependency → scenario will not boot. Especially common when copying a sample but forgetting to repath.
4. **Layer order in `.ent` doesn't match `<world>_<layer>.layer` filenames** → silent: missing layers just don't load. Engine doesn't fail loud.
5. **Referencing a prefab `{GUID}…/Prefab.et` that isn't a dependency** → entity becomes a placeholder; gameplay degrades silently.
6. **`m_iPlayerCount == 1` while game-mode prefab is a multiplayer game-mode** → `SCR_MissionHeader.IsMultiplayer()` returns false; lobby may fail. Use `>= 2` for any coop scenario.
7. **`m_sGameMode` doesn't match a registered game-mode tag** → mission appears in list but launch fails. Stick to `Coop` / `Conflict` / `GameMaster` / `Sandbox`.
8. **Embedded script in `EOnInit` references undeclared variable** → mission loads, runtime exception fires. Worth caching with a syntax pre-check.
9. **`Configurations` block in `.meta` missing `PC`** → resource won't be available in any platform build (PC must exist; others can inherit).
10. **Calling `MissionHeader.ReadMissionHeader("path/to/file.conf")`** at runtime requires the GUID-resolved path to be reachable. Backend-generated files placed outside the project root won't be discoverable.
11. **`.layer` file present on disk but not declared as `Layer name { Index N }` in `.ent`** → the layer is orphaned.
12. **Workbench wiki note** (per modding-update Feb 2024): entity-class changes between engine versions can data-loss your file. Backend must lock to a specific Reforger version or maintain a class-name compatibility map.

---

## Generation Strategy

### Backend writes (text-only, fully programmatic) — YES

- `addon.gproj` — trivial template, just GUID + dependency list.
- `Missions/<name>.conf` — `SCR_MissionHeader { … }` body, including `m_sName`, `m_sGameMode`, `m_iPlayerCount`, time-of-day, weather flags, briefing path, **provided `World` GUID points at something that exists.**
- `Missions/<name>.conf.meta` — fixed template with own GUID + 5-platform `Configurations` block.
- `Worlds/<name>.ent` — either `SubScene { Parent "<existing-world>" }` or `Layer N { … }` table.
- `Worlds/<name>.ent.meta` — same template form.
- `Worlds/<name>_<layer>.layer` — full content (spawn points, AI groups, waypoints, tasks, triggers, environment overrides). Any combination of:
  - `SCR_SpawnPoint` instances (player spawn points) → real example `SpawnPoint_US.et`, `SpawnPoint_USSR.et`, `SpawnPoint_FIA.et`.
  - `SCR_AIGroup` (static AI patrols) with `m_aStaticWaypoints` referencing named `SCR_AIWaypoint` / `SCR_DefendWaypoint` instances.
  - `SCR_*Task` (`SCR_EliminateTask`, `SCR_TriggerTask`, `MoveTask`) — these become the task list when registered in the `CoopTaskManager`'s `m_aInitialTaskNames`.
  - `SCR_BaseTriggerEntity` with `SCR_AISpawnerComponent` for dynamic spawns.
  - `TimeAndWeatherManagerEntity`, `GenericWorldFogEntity`, `GenericWorldLightEntity` overrides for weather/lighting.
  - `RadioManagerEntity`, `ScriptedChatEntity`, `ProjectileSoundsManager` for audio.
  - Inlined Enfusion Script for win conditions (`EOnInit ""\ "…" \ "…"` blocks).

### Workbench UI / Native Tooling required — NO programmatic path

- **Packaging** to publishable bundle (`Workbench > Publish Project`). Wiki confirms: "Mods in Arma Reforger can only be created and published using the Enfusion Workbench on PC." No documented headless publish.
- **`-builddata` step** — Workbench bakes per-platform data (PC, HEADLESS, XBOX_*…) before Workshop upload. CLI exists (`-gproj` and `-gprojConfig`) but still requires Workbench install (Windows only, ~25 GB).
- **Terrain `.terr`** and Navmesh `.nmn` — binary, generated. Backend must reference pre-existing terrains/navmeshes from dependencies (Arland, Eden, etc.).
- **Texture `.edds`** — binary mipmapped texture; mission previews must be authored in image tool then encoded by Workbench.
- **String tables `.st`** — Workbench compiles `Language/<addon>.st` master into per-language `.conf` runtime files. Backend could emit the `.conf` runtime form, but the master `.st` is binary-ish (observed in GRAD repo: `GRAD_Localisation.st` exists alongside per-lang `.conf` files).
- **Workshop publish** (Steam-style upload to `reforger.armaplatform.com/workshop/`) — Workbench-only UI flow.
- **Modding for macOS user (you)** — Workbench has no macOS build. You must either (a) run a Windows VM/server to do the build+publish step, or (b) target a Linux dedicated-server install of Reforger that can load *unpacked* addon trees directly (the same `.gproj` directory structure is accepted by the dedicated server).

### Mixed / Plausible-but-Risky

- **GUID generation** — `.meta` sidecars carry the file's GUID. Backend can mint random 16-char-uppercase-hex GUIDs as long as they're unique within the project and don't collide with dependencies. *BEST INFERENCE:* engine doesn't appear to verify mathematically; it just uses GUID as primary key. No first-party generator documented.
- **Direct-load on dedicated server** — Reforger dedicated server can load addons from disk via `-addonsDir` and `-mission` startup parameters. **If the backend writes a tree that mimics a published bundle's *layout*, the dedicated server may load it without Workbench packaging.** This is the most promising bypass route for an AI-native authoring system — needs empirical test on Linux server.
- **`.meta` writability** — Workbench overwrites these on next open. Backend writing them is fine for runtime; round-tripping with Workbench requires the GUID to remain stable.

---

## Open Questions

1. **Direct headless load.** Does an Arma Reforger Linux dedicated server load an *unpacked* addon directory (gproj + missions + worlds tree as files) without prior Workbench `-builddata`? If yes → 90% of the authoring pipeline can be backend-driven. If no → Workbench packaging is hard-required and a macOS-only user is blocked on a Windows VM or remote Workbench build step. **Test plan:** spin up a Linux dedicated server, drop in `Reforger-Sample-Coop` unpacked, set `-mission "{85A748EB80EE1051}Missions/CoopTest.conf"`, observe.
2. **`.gproj` Configurations block.** Is the per-platform `GameProjectConfig` block required for a server-side load, or only for Workbench packaging? Sample mods omit it; GRAD includes it. Likely Workbench-only.
3. **GUID generation algorithm.** Is the 16-hex-char GUID validated for any structural property (timestamp, hash, signature)? Inspection of observed GUIDs (`5966E5428E081A6C`, `5EB4779B97BA28CD`, `5614E48162D7B84F`) suggests they begin with a creation-time-derived prefix (`56`, `59`, `5E`), but later/random parts. **BEST INFERENCE, NOT VERIFIED.**
4. **Briefing config (`m_sBriefingConfig`).** Observed empty in all sample missions; no public example of a populated briefing-screen `.conf` was found.
5. **Radio chatter / faction-comms tracks.** `RadioManagerEntity` is referenced in `_managers.layer`, but the actual radio asset bundle is part of dependencies. No public example of a custom radio-set was found in this research.
6. **Audio cue triggering.** No first-class "play sound at trigger" entity found in sample missions; this is typically done with `userScript` blocks calling `AudioSystem.PlaySound(...)` from Enfusion Script.
7. **Trigger / Task graph editor.** The Scenario Framework wiki page is gated; the GitHub Herbiie tutorial mentions a hierarchical `Area → Layer → Slot → Task` graph but the specific class names (`SCR_ScenarioFrameworkLayerTask`, `SCR_ScenarioFrameworkLayerTaskDefend`, `SCR_ScenarioFrameworkLayerTaskMove`, `SCR_ScenarioFrameworkSlotTaskAI`, `SCR_ScenarioFrameworkTaskArea`) and their full schemas need direct Reforger source access. **Recommend a follow-up research task focused on Scenario Framework entity classes.**

---

## Key Source URLs

- [Reforger-Sample-Coop GitHub](https://github.com/exocs/Reforger-Sample-Coop) — minimal coop sample (verified file contents above)
- [CombatOpsEnhanced_AR GitHub](https://github.com/Kexanone/CombatOpsEnhanced_AR) — production scenario with inheritance pattern
- [GRAD-COOP-Template-Reforger GitHub](https://github.com/gruppe-adler/GRAD-COOP-Template-Reforger) — Game Master coop with localisation
- [BohemiaInteractive/Arma-Reforger-Samples GitHub](https://github.com/BohemiaInteractive/Arma-Reforger-Samples) — official Bohemia modding samples
- [SCR_MissionHeader source viewer (arexplorer)](https://arexplorer.zeroy.com/_s_c_r___mission_header_8c_source.html) — full field inventory
- [SCR_MissionHeaderCampaign source viewer (arexplorer)](https://arexplorer.zeroy.com/_s_c_r___mission_header_campaign_8c_source.html) — Conflict-mode extension fields
- [XGamingServer Mission Header Reference](https://xgamingserver.com/docs/arma-reforger/mission-header) — fields as documented by hosting provider
- [Bohemia Wiki — Scenario Framework Setup Tutorial](https://community.bistudio.com/wiki/Arma_Reforger:Scenario_Framework_Setup_Tutorial) (HTML 403 to fetch tools, accessible via browser)
- [Bohemia Wiki — File Types](https://community.bistudio.com/wiki/Arma_Reforger:File_Types) (HTML 403)
- [Bohemia Wiki — Startup Parameters](https://community.bistudio.com/wiki/Arma_Reforger:Startup_Parameters) (HTML 403; mentions `-gproj`, `-gprojConfig`, `-builddata`, `-listScenarios`, `-addonsDir`, `-mission`, `-worldSystemsConfig`)
- [Bohemia Wiki — Mod Publishing Process](https://community.bistudio.com/wiki/Arma_Reforger:Mod_Publishing_Process) (HTML 403)
- [awesome-reforger curated list](https://github.com/ofpisnotdead-com/awesome-reforger)
- [firefly2442/arma-reforger-modding-notes](https://github.com/firefly2442/arma-reforger-modding-notes)
