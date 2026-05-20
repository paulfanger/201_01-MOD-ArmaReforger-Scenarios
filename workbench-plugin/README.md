# Workbench Plugin — Phase 2 Skeleton

> **Status:** SKELETON ONLY — Phase 2, wartet auf Windows-Workbench-Zugang
> **Referenz:** `research/01-workbench-sdk.md` Hybrid B Pattern

---

## Was ist das?

Arma Reforger Workbench Plugin (`AI_GeneratePlugin.c`) im Enforce Script Format.
Das Plugin liest `$profile:elos/ai-spec.json` (von Python-Backend generiert) und ruft
`WorldEditorAPI.CreateEntity()` auf um Entities direkt im Workbench zu erstellen.

## Aktivierung (Phase 2, Windows erforderlich)

### 1. Plugin-Datei kopieren

```
workbench-plugin/AI_GeneratePlugin.c
→ C:\ArmaReforger\Data\Scripts\Plugins\AI_GeneratePlugin.c
```

Oder in deinen Addon-Ordner:
```
missions/{id}/output/Scripts/WorkbenchPlugin/AI_GeneratePlugin.c
```

### 2. Headless-Run (CLI)

```bat
ArmaReforgerWorkbenchSteamDiag.exe ^
  -plugin=AI_GeneratePlugin ^
  -spec="C:\ArmaReforger\Profile\elos\ai-spec.json" ^
  -buildData HEADLESS ^
  -exitAfterInit
```

### 3. Interactive-Run

1. Workbench öffnen
2. Plugins → AI_GeneratePlugin
3. Operation: "Generate from AI Spec"
4. Spec-Datei wird gelesen, Entities erstellt

## ai-spec.json Format (Phase 2)

Das Python-Backend schreibt diese Datei nach `$profile:elos/ai-spec.json`:

```json
{
  "mission_id": "night-recon-everon",
  "spawn_points": [
    {
      "class_name": "SCR_SpawnPoint",
      "prefab_guid": "{ABCDEF1234567890}PrefabsEditable/SpawnPoints/E_SpawnPoint_US.et",
      "coords": [263, 9, 245],
      "angle_y": -60
    }
  ],
  "ai_groups": [...],
  "waypoints": [...]
}
```

## Externe IPC-Pattern

Plugin nutzt **File-Watching** für IPC (kein HTTP/REST in Enforce Script):
1. Python-Backend schreibt `ai-spec.json` in `$profile:elos/`
2. Plugin liest File via `FileIO.OpenFile()`
3. Plugin schreibt `ai-result.json` zurück
4. Python-Backend liest Result-File

## Bekannte Limitierungen

- Enforce Script hat **kein HTTP/REST** — File-IO ist der einzige IPC-Kanal
- JSON-Parsing via `JsonSerializer` (eingeschränkt, Schema muss exakt matchen)
- WorldEditorAPI ist **nur im Workbench** verfügbar — kein runtime-Zugriff
- Headless-Mode: `-exitAfterInit` terminiert nach Plugin-Ausführung

## Phase-2-Trigger

Wenn Win-Zugang verfügbar:
1. Plugin in Workbench testen (interactive Mode)
2. JSON-Parsing implementieren (Phase 2 TODOs in `AI_GeneratePlugin.c`)
3. `workbench-integration-tester` Mode-A aktivieren
4. `DECISIONS.md` mit Phase-2-Implementation-Start-Eintrag

**Nicht in Phase 1 aktiv.** Kein Testing-Coverage. Kein Commit-Pflicht.
