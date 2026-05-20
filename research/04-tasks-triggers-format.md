# Tasks & Triggers Format Research — Reforger .layer Syntax

Stand: 20. Mai 2026. Quellen: OSS-Repos in `/tmp/reforger-research/`.

## Sources

- `Reforger-Sample-Coop` — offizielle Bohemia-Sample, vollständige Coop-Mission
- `CombatOpsEnhanced_AR` — production-grade community mod, Eden-Map
- `GRAD-COOP-Template-Reforger` — GM-Editor-basierte Coop-Vorlage
- `Arma-Reforger-Samples` — offizielle Bohemia Asset/Faction Samples

Alle Layer-Files: Brace-Syntax (nicht JSON), Felder ohne Anführungszeichen außer String-Values.

---

## 1. SCR_TriggerTask — Exact Field Names

Quelle: `Reforger-Sample-Coop/SampleCoop/Worlds/CoopTest_tasks.layer`

```
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
   DrawShape 1
   ShapeColor 0.502 0 0 0.392
   m_sOwnerFactionKey "US"
  }
 }
}
```

**Felder:**
| Feld | Typ | Beschreibung |
|---|---|---|
| `m_sName` | String | Angezeigter Task-Name in der Spieler-UI |
| `m_sDescription` | String | Beschreibungstext |
| `m_eAssignMessage` | Enum | `NONE` oder Meldungs-Enum |
| `m_eUnassignMessage` | Enum | `NONE` oder Meldungs-Enum |
| Inline-Block `{...}` | — | Enthält Trigger-Entität (Completion-Trigger) |

**Inline-Trigger im TriggerTask** (SCR_BaseFactionTriggerEntity):
| Feld | Typ |
|---|---|
| `ID` | String (GUID) |
| `coords` | `x y z` (relativ zum Task) |
| `SphereRadius` | Float (Meter) |
| `DrawShape` | Bool (1 = sichtbar im Editor) |
| `ShapeColor` | `R G B A` (0–1 float) |
| `m_sOwnerFactionKey` | String — Faction-Key der triggernden Faction (`"US"`, `"USSR"`, `"FIA"`) |

---

## 2. SCR_EliminateTask — Exact Field Names

Quelle: `Reforger-Sample-Coop/SampleCoop/Worlds/CoopTest_tasks.layer`

```
$grp SCR_EliminateTask : "{B866318EB7E84833}Prefabs/Tasks/EliminateTask.et" {
 EliminateTaskB {
  coords 86.897 10.001 176.849
 }
 EliminateTaskA {
  coords 239.915 10.001 270.184
  m_sName "Eliminate UAZ"
 }
}
```

**Aufbau:**
- Prefix `$grp` — Gruppe von benannten Task-Instanzen
- Jede Instanz (z.B. `EliminateTaskA`, `EliminateTaskB`) ist ein named Entity
- `m_sName` pro Instanz ist der UI-Anzeigetext
- `coords` — Weltposition des Task-Markers (nicht des Elimination-Targets)
- Kein Inline-Trigger — Completion-Detection läuft über Scripting oder Vehicles mit `SCR_VehicleDamageManagerComponent`

**Registrierung im CoopTaskManager:**
```
SCR_CoopTaskManager CoopTaskManager : "{BA79FF1D825A3F3A}Prefabs/MP/Managers/Tasks/CoopTaskManager.et" {
 coords 229.281 10.001 247.172
 m_aSupportedTaskTypes {
  SCR_EliminateTaskSupportClass "{5968C9C362B1A0E9}" {
   m_TaskPrefab "{B866318EB7E84833}Prefabs/Tasks/EliminateTask.et"
  }
 }
 m_aInitialTaskNames {
  "MoveTask_1" "EliminateTaskA" "EliminateTaskB"
 }
}
```

| Feld | Beschreibung |
|---|---|
| `m_aSupportedTaskTypes` | Liste von `SCR_EliminateTaskSupportClass` oder anderen, mit `m_TaskPrefab` |
| `m_aInitialTaskNames` | Space-separierte Namen der Task-Entities, die beim Missionsstart aktiv sind |

---

## 3. SCR_BaseTriggerEntity — Exact Field Names

Quelle: `Reforger-Sample-Coop/SampleCoop/Worlds/CoopTest_triggers.layer`

```
$grp SCR_BaseTriggerEntity : "{3F294A5E2B52B65E}Prefabs/MP/Triggers/CoopTriggerSpawner.et" {
 DynamicTriggerSpawn1 {
  components {
   SCR_AISpawnerComponent "{5966F2A840D93A01}" {
    m_vSpawnPosition 200.193 10 242.115
    m_vSpawnRotation 0 87 0
   }
   RplComponent "{5966F2A87A6B4E62}" {
   }
  }
  coords 240 10 240
  SphereRadius 2
  DrawShape 1
  ShapeColor 0.318 0.561 0.071 0.392
 }
 DynamicTriggerSpawn2 {
  components {
   SCR_AISpawnerComponent "{5966F2A840D93A01}" {
    m_rnDefaultPrefab "{30ED11AA4F0D41E5}Prefabs/Groups/OPFOR/Group_USSR_FireGroup.et"
    m_vSpawnPosition 207.415 10 269.989
    m_vSpawnRotation 0 40 0
    m_aWaypointsList {
     "WP3" "WP4"
    }
   }
   RplComponent "{5966F2A87A6B4E62}" {
   }
  }
  coords 240 10 260
  SphereRadius 2
  DrawShape 1
  ShapeColor 0.157 0.624 0.624 0.392
 }
}
```

**Trigger-Felder (pro Instanz):**
| Feld | Typ | Beschreibung |
|---|---|---|
| `coords` | `x y z` | Weltposition des Trigger-Mittelpunkts |
| `SphereRadius` | Float | Aktivierungsradius in Metern |
| `DrawShape` | Bool | `1` = Editor-Debug-Visualisierung |
| `ShapeColor` | `R G B A` | Editor-Debug-Farbe (0–1 float) |

**SCR_AISpawnerComponent-Felder:**
| Feld | Typ | Beschreibung |
|---|---|---|
| `m_rnDefaultPrefab` | GUID-String | Prefab-Pfad der zu spawnenden Gruppe |
| `m_vSpawnPosition` | `x y z` | Spawn-Weltposition |
| `m_vSpawnRotation` | `x y z` | Spawn-Rotation (Y = Heading in Grad) |
| `m_aWaypointsList` | String-Array | Space-separierte Namen von Waypoint-Entities |

**RplComponent ist immer dabei** — Replication-Component, kein Daten-Feld.

**Scripted Trigger (inline Enforce Script):** Trigger-Instanzen können `EOnInit` mit Enforce-Script-Snippets enthalten (z.B. für `OnTriggerEmpty`-Callback um `EndGameMode` auszulösen).

---

## 4. FactionManager in CoopGameMode

Quelle: `Reforger-Sample-Coop/SampleCoop/Worlds/CoopTest_gamemode.layer`

```
SCR_FactionManager FactionManager : "{E4075339B4E24E10}Prefabs/MP/Managers/Factions/CoopFactionManager.et" {
}
```

- **Kein eigener Block** — der `CoopFactionManager`-Prefab enthält alle Faction-Defaults.
- Steht als **eigenes Top-Level-Entity** in der Layer (nicht als Komponente des GameMode).
- Prefab-GUID: `{E4075339B4E24E10}` für Standard-Coop.

**GameMode-Entity** ist separat:
```
SCR_BaseGameMode GameMode : "{904EC091C347AEA9}Prefabs/MP/Modes/Coop/CoopGameMode.et" {
 components {
  SCR_RespawnMenuHandlerComponent "{5966E56DB0ABC25D}" {
  }
 }
}
```

**Standard-Coop-Manager-Set** (alle eigene Top-Level-Entities in `*_gamemode.layer`):
| Entity | Prefab | Zweck |
|---|---|---|
| `SCR_BaseGameMode GameMode` | `Prefabs/MP/Modes/Coop/CoopGameMode.et` | Spielmodus |
| `SCR_FactionManager FactionManager` | `Prefabs/MP/Managers/Factions/CoopFactionManager.et` | Factions |
| `SCR_LoadoutManager LoadoutManager` | `Prefabs/MP/Managers/Loadouts/CoopLoadoutManager.et` | Loadouts |
| `SCR_SpawnPoint SpawnPoint_US` | `PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et` | US-Spawnpunkt |

---

## 5. Vollständige Coop-Mission Layer-Struktur

Quelle: `Reforger-Sample-Coop` — alle Layer-Files der `CoopTest`-Mission.

**Layer-Aufteilung (empfohlenes Pattern):**

| Layer-File | Inhalt |
|---|---|
| `*_gamemode.layer` | GameMode, FactionManager, LoadoutManager, SpawnPoints |
| `*_managers.layer` | MapEntity, CameraManager, TimeAndWeatherManager, RadioManager, ChatEntity, DestructionManager, CoopTaskManager, GenericEntity (CoopLogic-Script) |
| `*_tasks.layer` | SCR_TriggerTask, SCR_EliminateTask (und Elimination-Target-Vehicles) |
| `*_triggers.layer` | SCR_BaseTriggerEntity mit SCR_AISpawnerComponents, SCR_SpawnPoint |
| `*_AI.layer` | SCR_AIWaypoint-Gruppen, SCR_DefendWaypoint, SCR_AIGroup (statische Gruppen) |
| `*_spawnpoints.layer` | Weitere SCR_SpawnPoint-Instanzen |
| `*_default.layer` | Environment/Terrain-Objekte |
| `*_comments.layer` | Nur Editor-Kommentare (GenericEntities ohne Gameplay-Funktion) |

**AI-World und PerceptionManager** stehen in `*_gamemode.layer` oder eigener Layer:
```
SCR_AIWorld : "{E0A05C76552E7F58}Prefabs/AI/SCR_AIWorld.et" {
}
PerceptionManager PerceptionManager1 : "{028DAEAD63E056BE}Prefabs/World/Game/PerceptionManager.et" {
}
```

---

## 6. Scripted Completion Logic (GenericEntity CoopLogic)

Für EliminateTask-Completion → EndGameMode wird ein inline-scripted `GenericEntity` in `*_managers.layer` genutzt:

```
GenericEntity CoopLogic {
 coords 265.941 10.001 268.581
 userScript "	// code here"
 constructor ""\
 "		SetEventMask(EntityEvent.INIT);"\
 "	"
 EOnInit ""\
 "		SCR_EliminateTask task = SCR_EliminateTask.Cast(GetWorld().FindEntityByName(\"EliminateTaskA\"));"\
 "		if (task)"\
 "		{"\
 "			task.GetOnEliminatedInvoker().Insert(OnTaskComplete);"\
 "		}"\
 "	}"\
 "	"\
 "	void OnTaskComplete(SCR_BaseTask task) "\
 "	{"\
 "		SCR_BaseGameMode gameMode = SCR_BaseGameMode.Cast(GetGame().GetGameMode());"\
 "		if (!gameMode || !gameMode.IsMaster())"\
 "			return;"\
 "		"\
 "		Faction faction = task.GetTargetFaction();"\
 "		int factionIndex = GetGame().GetFactionManager().GetFactionIndex(faction);"\
 "        gameMode.EndGameMode(SCR_GameModeEndData.CreateSimple(SCR_GameModeEndData.ENDREASON_EDITOR_FACTION_VICTORY, -1, factionIndex));"\
 "	"
}
```

**Wichtige API-Calls (verifiziert aus Samples):**
- `GetWorld().FindEntityByName("EntityName")` — Entity by name lookup
- `task.GetOnEliminatedInvoker().Insert(callback)` — EliminateTask completion event
- `GetGame().GetFactionManager().GetFactionByKey("US")` — Faction lookup
- `GetGame().GetFactionManager().GetFactionIndex(faction)` — Faction index
- `gameMode.EndGameMode(SCR_GameModeEndData.CreateSimple(...))` — Mission end
- `SCR_GameModeEndData.ENDREASON_EDITOR_FACTION_VICTORY` — Standard Coop-Sieg

---

## Key Takeaways für den Export-Generator

1. **Task-Namen in `m_aInitialTaskNames`** müssen exakt mit den Entity-Namen der Task-Entities übereinstimmen (case-sensitive).
2. **SphereRadius** ist das korrekte Feld (nicht `radius`, nicht `m_fRadius`).
3. **FactionManager steht NICHT als Komponente** im GameMode — eigenes Top-Level-Entity.
4. **`$grp`-Prefix** bei EliminateTask bedeutet eine Gruppe von named Instanzen, nicht eine einzelne Entity.
5. **SCR_BaseFactionTriggerEntity** kann als Inline-Block **innerhalb** eines SCR_TriggerTask stehen (Completion-Trigger) — oder als eigenständige Trigger-Instanz in einer `$grp`-Gruppe.
6. **RplComponent** muss immer mit dabei sein wenn SCR_AISpawnerComponent verwendet wird.
7. **m_aWaypointsList** enthält Space-separated quoted Namen — keine Kommas.
