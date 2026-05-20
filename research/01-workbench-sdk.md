# Workbench SDK Research — Reforger 2026

Stand: 20. Mai 2026. Reforger Version 1.6.0.119 ("Final Strike" Milestone).

## Source Map

| Quelle | Letzter Update | Status |
|---|---|---|
| Wiki: Workbench Plugin (community.bohemia.net) | 26.02.2025 | aktiv |
| Wiki: Startup Parameters | 21.11.2025 | aktiv |
| Wiki: Development Executables | 13.03.2024 | veraltet aber gueltig |
| Wiki: Mod Project Setup | n/a | aktiv |
| Wiki: File Types | n/a | aktiv |
| Wiki: World Editor Plugin | n/a | aktiv |
| Wiki: Resource Manager Plugin | n/a | aktiv |
| Wiki: Script Editor Plugin | n/a | aktiv |
| Dev Hub (reforger.armaplatform.com) | 04.11.2025 (last news) | aktiv |
| BohemiaInteractive/Arma-Reforger-Samples | pushed 16.04.2025 | offiziell, 298 stars |
| BohemiaInteractive/Arma-Reforger-Script-Diff | pushed 29.01.2026 | offiziell, neu seit 09/2025 |
| Modding-Update 1.1 Scripting (News) | 03.04.2024 | historisch |
| Modding-Update 1.6 Task System | 07.10.2025 | aktuell |
| awesome-reforger (curated list) | aktiv 05/2026 | community |

URLs siehe Reference Repos und in-line Quellen.

## Verified Facts

### 1) Plugin-APIs

- Workbench Plugins werden in Enforce Script (.c Files) geschrieben, erben von `WorkbenchPlugin` und werden ueber `[WorkbenchPluginAttribute(...)]` registriert. Spezialklassen: `WorldEditorPlugin`, `ResourceManagerPlugin`, `WorldEditorTool`. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Workbench_Plugin)
- Plugin-Files liegen unter `Scripts/WorkbenchGame/<EditorModule>/`. Discovery erfolgt automatisch ueber Class Attribute, kein separates Manifest. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Workbench_Plugin_Tutorial)
- Die offizielle WorkbenchAPI ist im BI-Repo `Arma-Reforger-Script-Diff` unter `scripts/GameLib/generated/WorkbenchAPI/` einsehbar (verifiziert: 11 Top-Level Files inkl. `Workbench.c`, `Modules/`, `Plugins/`). (Source: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/tree/main/scripts/GameLib/generated/WorkbenchAPI)
- `WorkbenchPluginAttribute` Signatur: `(string name, string description, string shortcut, string icon, array<string> wbModules, string category, int awesomeFontCode)`. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Workbench_Plugin_Tutorial)

### 2) Externe Tool-Kommunikation

- Plugins koennen externe Prozesse starten: `Workbench.RunProcess(string command)` (returns `ProcessHandle`), `Workbench.RunCmd(string command, bool wait)`, `KillProcess`, `WaitProcess`. Verifiziert in offizieller API. (Source: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/main/scripts/GameLib/generated/WorkbenchAPI/Workbench.c)
- File I/O ist verfuegbar via `FileIO.OpenFile`, `FileIO.MakeDirectory`, `FileHandle.FPrintln/WriteLine/CloseFile`. Belegt durch DiscordRP (schreibt Workbench-State in `RPState.txt`, der von externer `EnfusionWorkbenchRP.exe` gelesen wird). (Source: https://github.com/NarcoMarshDev/Enforce-Script-Extensions/blob/master/scripts/WorkbenchGame/DiscordRP/DiscordRP.c)
- Es gibt KEINE offizielle REST API, KEINE Named Pipes API und KEINE Sockets API in der dokumentierten Workbench-Layer. Externe Kommunikation laeuft ueber (a) File-Watching auf gemeinsamen Files (Discord RP Pattern) oder (b) `RunProcess` + Pipes/stdout. (Source: WorkbenchAPI ohne Socket/Net Methoden, https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/main/scripts/GameLib/generated/WorkbenchAPI/Workbench.c)
- Plugins koennen via `Workbench.GetAbsolutePath()` Pfade ausserhalb der Resource-Hierarchie ansprechen; `FileMode.WRITE` schreibt beliebige Files. Belegt durch Tactical-Data-Link (exportiert nach `$profile:TDL_TerrainExport` als GeoJSON/JSON). (Source: https://github.com/Colton1070/Tactical-Data-Link/blob/main/Scripts/WorkbenchGame/WorldEditor/AG0_TDLTerrainExporterPlugin.c)

### 3) Plugin-Load-Mechanismus

- Plugin Discovery: automatisch beim Workbench-Start, scant `Scripts/WorkbenchGame/` aller geladenen Addons nach Klassen mit `WorkbenchPluginAttribute`. Kein Manifest, kein eigenes File-Format. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Workbench_Plugin_Tutorial)
- `.gproj` Files sind text-basierte Project-Manifests im Enfusion-Brace-Format. Beispiel-Struktur: `GameProject { ID "..." GUID "..." TITLE "..." Dependencies { ... } Configurations { GameProjectConfig {...} } }`. Verifiziert an `SampleMod.gproj` (488 Bytes). (Source: https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/main/SampleMod_Main/SampleMod.gproj)
- Plugins koennen via CLI per `-plugin=TAG_PluginName` mit Argumenten gestartet werden, erfordert `-wbModule=<editor>` Kontext. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Startup_Parameters)
- Plugins koennen externe `.dll` Files mitliefern (z.B. DiscordRP mit `discord_game_sdk.dll`); werden vom externen Process geladen, nicht von Workbench selbst. (Source: https://github.com/NarcoMarshDev/Enforce-Script-Extensions/tree/master/scripts/WorkbenchGame/DiscordRP)

### 4) Headless / CLI-Build-Mode (existiert)

- Offizielle Headless-Parameter: `-wbsilent` (init + exit ohne UI), `-exitAfterInit` (UI dann auto-exit), `-validate` (Script-Compile-Check, Return-Code 0/-1), `-buildData PC|HEADLESS|XBOX_ONE|XBOX_SERIES|PS4 <outpath>` (data build), `-loadBuiltData` (validate built resources), `-metaFiles` (copy meta-files), `-rebuild-database-only`. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Startup_Parameters)
- Plattform `HEADLESS` ist als Build-Target erste Klasse, neben PC/Console. (Source: ibid.)
- Beispiel offizielles Cmd: `ArmaReforgerWorkbenchSteamDiag.exe -wbModule=ResourceManager -builddata PC "C:\Data\PCData"`. (Source: ibid.)
- Workbench-Binary heisst `ArmaReforgerWorkbenchSteamDiag.exe`. Diag- und Non-Diag-Variants koennen sich nicht ueberkreuz verbinden. (Source: https://community.bohemia.net/wiki/Arma_Reforger:Development_Executables)

### 5) Entity-Spawning per File-Manipulation

- `.layer` Files sind text-basiert mit hierarchischer Brace-Syntax. Verifiziertes Beispiel aus offiziellem BI-Sample: `CinematicEntity Cinematic_Tutorial { coords 0 0 0 Scene CinematicScene "{GUID}" { Tracks { ... } } }`. Properties sind space-separated. (Source: https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/main/SampleMod_CinematicTutorial/Scenes/Cinematic_Tutorial_default.layer)
- `.ent` Worlds aggregieren mehrere `.layer` Files. Inhalt: sequentielle Entity-Eintraege mit Class, Prefab-GUID, Coords. Format: `SCR_DestructibleBuildingEntity : "{GUID}PrefabLibrary/.../Shed.et" { coords X Y Z }`. (Source: Wiki File Types via WebSearch-Auszug; bestaetigt durch `.layer` Sample oben)
- `.et` Prefabs sind ebenfalls text-basiert, gleiche Brace-Syntax (Entity Templates). (Source: https://community.bohemia.net/wiki/Arma_Reforger:File_Types via WebFetch)
- **Wichtig:** Programmatic Generation funktioniert auf 2 Wegen: (a) via WorldEditorAPI in Plugin (`api.CreateEntity`, `api.CreateSubsceneLayer`, `worldEditor.Save()`) — verifiziert in CRF Mission Creation Plugin; (b) ueber direkte File-Manipulation extern (Text-Edit, dann von Workbench parsen lassen). (Source: https://github.com/CoalitionArma/Coalition-Reforger-Framework/blob/release/Scripts/WorkbenchGame/MissionPlugins/CRF_MissionCreationPlugin.c)
- Kein formales JSON/XML-Schema dokumentiert. Schema = "was die Engine parst". Reverse Engineering ueber bestehende Files noetig.

### 6) Community-Plugins als Reference

Siehe Section "Reference Repos" unten.

### 7) Bohemia Reforger Wiki State

- Wiki ist aktiv. Verschiedene Pages mit unterschiedlichem Pflege-Stand: Startup Parameters zuletzt 21.11.2025, Workbench Plugin 26.02.2025. (Source: explicit footer dates)
- Curl auf `community.bistudio.com` gibt 403, der Mirror `community.bohemia.net` funktioniert via WebFetch und gibt MediaWiki-Page-Footers mit Datum aus.
- Dev Hub (reforger.armaplatform.com) ist primaere News-Quelle, letzter Eintrag 04.11.2025. (Source: https://reforger.armaplatform.com/dev-hub)
- BI hat im Sep 2025 ein neues offizielles Repo veroeffentlicht: `Arma-Reforger-Script-Diff` mit kompletter generierter WorkbenchAPI. Massiver Sprung in Transparenz. (Source: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff)

## Open Questions

- Wie genau das `ScriptDialog`-System dynamische Forms zur Laufzeit baut (vermutlich via reflektierte Class-Fields, aber nicht offiziell dokumentiert).
- Ob `RunProcess` stdin/stdout-Pipe-Zugriff auf gestartete Children erlaubt (Signaturen zeigen nur Handle, kein Stream-Read). Wahrscheinlich nein, Kommunikation muss ueber Files.
- Exakte Konstanten-Liste fuer `wbModules` Array (verifiziert: `ScriptEditor`, `ResourceManager`, `WorldEditor`, `ParticleEditor`, `AnimEditor`, `AudioEditor`, `BehaviorEditor`, `NavmeshGeneratorMain`, `ProcAnimEditor`, `LocalizationEditor` — aus DiscordRP enum, nicht offiziell als Tabelle).
- Ob `.gproj` GUID-Kollisionen tooling-seitig verhindert werden oder nur runtime erkannt.
- Schema-Validation: ob Workbench beim Laden eines extern editierten `.layer` formal validiert oder nur best-effort parsed (Risiko: Silent Data Loss).
- macOS/Linux Workbench Roadmap: keine offizielle Aussage. Stand 2026: Workbench Windows-only.

## Recommended Integration Path (Mai 2026)

### A) External Only

**Realistisch fuer macOS-Author-Workflow.** Limits:

- Editor selbst nicht ansteuerbar von extern (kein RPC). External Tool schreibt `.layer`/`.ent`/`.et`/`.gproj` als Text-Files; User oeffnet Workbench manuell und Workbench laedt die Files.
- Build/Validate funktioniert headless via `-validate` und `-buildData HEADLESS` — aber nur auf Windows-Host. macOS-User braucht Windows-VM/Box oder CI-Runner.
- Live-Feedback Loop ist Sekunden bis Minuten (Tool schreibt, User reloaded, dann erst Visual Check).
- Klar moeglich: AI generiert Layer-Files in Brace-Syntax, User pullt sie in Workbench-Projekt, Workbench parsed.
- Limits: keine garantierte Schema-Validation; bei syntaktischem Fehler crashed/skipped Workbench den File.

### B) Hybrid (External Generator + In-Workbench Plugin)

**Realistisch und Best-of-Both.** Was es braucht:

- macOS Backend (Python/Node/Go) generiert Mission-Spec als JSON o.ae.
- Eine kleine `WorkbenchPlugin` (Enforce Script) liest die Spec via `FileIO.OpenFile`, ruft `WorldEditorAPI.CreateEntity()` etc. und ruft `worldEditor.Save()`.
- Plugin laeuft im laufenden Workbench (User klickt Menue oder Shortcut). Optional CLI-Trigger via `-plugin=` zum Headless-Run.
- Bridge File: gemeinsamer Path (z.B. `$profile:ai-spec.json`). Optional File-Watcher (Polling im Plugin, max 1 Hz, da Workbench single-threaded UI).
- Macht den Author-Loop sehr eng: User editiert Spec auf Mac, sync'd auf Win-VM, klickt 1x in Workbench, sieht Resultat.
- Headless-Variante: User triggert via CLI `-buildData HEADLESS` + `-plugin=AI_GeneratePlugin -spec=path.json -exitAfterInit` und bekommt fertige `.layer` aus dem Backend ohne UI.

### C) Native (AI im Workbench-UI)

**Nicht realistisch in 2026.** Was es braeuchte:

- HTTP-Client API in Enforce Script (nicht dokumentiert vorhanden) ODER Custom Native Extension (Enfusion erlaubt keine eigenen DLLs ins Script-Layer; DiscordRP umgeht das via externem Companion-Process).
- UI-Embedding ist nur via `Workbench.Dialog`/`ScriptDialog` moeglich — diese sind Modal, kein Rich-UI, kein Streaming.
- Selbst wenn man `RunProcess` einen lokalen LLM-Server starten laesst, kein bidirektionaler Channel.

### Empfehlung: **B (Hybrid)**

Begruendung: Auf macOS laeuft alles ausser dem finalen Render/Build. Backend generiert Brace-Syntax-Spec. Win-Side Plugin (~150 LOC Enforce Script) konsumiert. Loop ist ~5-10s. Migrationspfad nach C bleibt offen falls BI in Zukunft Sockets exposed. Pfad A ist als Fallback fuer den Fall, dass User keinen Win-Host hat — `.layer` Generation direkt funktioniert, aber kostet Feedback-Speed.

## Hard Blockers

1. **Workbench ist Windows-only**. Kein nativer macOS-Build, CodeWeavers/CrossOver einzige Option. Bestaetigt via Steam Community + Wiki. (Source: https://steamcommunity.com/app/1874880/discussions/0/594030049494284140/, https://www.codeweavers.com/compatibility/crossover/arma-reforger)
2. **Keine REST/HTTP/Socket API in Enforce Script**. Komplette WorkbenchAPI gepruefft (`Workbench.c`, 2979 Bytes): nur `RunProcess`, `RunCmd`, `Dialog`, `OpenResource`, `GetAbsolutePath`, `SavePixelRawData`, `Exit`. Kein `HttpClient`, kein `Socket`, kein `NamedPipe`. (Source: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/main/scripts/GameLib/generated/WorkbenchAPI/Workbench.c)
3. **Keine Custom Native Extensions im Enforce Script Sandbox**. DLLs werden nur ueber externe Companion-Processes geladen, niemals direkt vom Script. Bestaetigt durch DiscordRP-Pattern (separater .exe Companion). (Source: https://github.com/NarcoMarshDev/Enforce-Script-Extensions/tree/master/scripts/WorkbenchGame/DiscordRP)
4. **Kein formal dokumentiertes Schema fuer `.layer`/`.ent`/`.et`/`.gproj`**. Format ist Brace-Syntax, aber Class-Listen + Property-Namen sind nicht versioniert exportiert. Generierung erfordert Reverse Engineering von Sample-Files oder Live-API-Capture via Plugin.

## Soft Blockers

1. **`.layer` Editing extern ist syntax-fragil**. Tippfehler in Brace-Struktur kann Workbench crashen oder den File silent skippen. Workaround: Generator schreibt via `FileIO` aus laufendem Plugin (API-validated path) statt extern.
2. **Workbench Build-Pipeline braucht Diag-Executables fuer Debug**. Mischbetrieb Diag/Non-Diag Clients nicht moeglich. Workaround: CI/Headless Pipeline immer auf Diag-Variant pinnen.
3. **Plugin Reload erfordert Workbench Restart oder Script-Reload**. Hot-Reload zwischen Plugin-Iterationen langsam. Workaround: Plugin-Code stabil halten, Daten/Specs extern variieren.
4. **Cloudflare blockt curl auf `community.bistudio.com`**. Doku-Scraping fuer Tooling muss `community.bohemia.net` Mirror nutzen oder Browser-Headers via WebFetch. Bestaetigt mehrfach in dieser Recherche.
5. **GUID-Stabilitaet bei Auto-Generation**. Jeder Entity/Layer braucht stable GUID; falsche GUIDs brechen Cross-Mod References. Workaround: GUIDs nicht selber generieren, sondern Workbench-API ueber Plugin sie vergeben lassen (`worldEditor.Save()` produces them).
6. **Build-Daten-Pfad-Konventionen** (z.B. Path nicht in OneDrive/Program Files). Operational Friction. Workaround: dedizierte WSL/Win-VM mit sauberem Pfad.

## Reference Repos

1. **[BohemiaInteractive/Arma-Reforger-Samples](https://github.com/BohemiaInteractive/Arma-Reforger-Samples)** — Offizielles Samples-Repo (298 stars, last push 16.04.2025). `SampleMod_WorkbenchPlugin/` enthaelt minimale Plugin-Templates fuer alle 4 Editor-Module + WorldEditorTool. Pflicht-Reference.
2. **[BohemiaInteractive/Arma-Reforger-Script-Diff](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff)** — Offizielle generierte API-Dumps (15 stars, neu seit 09/2025, last push 29.01.2026). Enthaelt `scripts/GameLib/generated/WorkbenchAPI/` — die authoritative Source fuer alle Plugin-API-Signaturen. **Game-Changer fuer Tooling**.
3. **[CoalitionArma/Coalition-Reforger-Framework](https://github.com/CoalitionArma/Coalition-Reforger-Framework)** — Production-Framework (11 stars, 33 forks, aktiv 19.05.2026). `Scripts/WorkbenchGame/MissionPlugins/` enthaelt **6 Mission-Creation-Plugins inkl. CRF_MissionCreationPlugin** (kanonisches Beispiel fuer programmatic Mission/Layer/Entity-Erzeugung via WorldEditorAPI).
4. **[Colton1070/Tactical-Data-Link](https://github.com/Colton1070/Tactical-Data-Link)** — Aktiver Reforger Mod (6 stars, aktiv 05/2026). `AG0_TDLTerrainExporterPlugin.c` ist das **kanonische Pattern fuer External File Export** (Heightmap, Roads, POIs als GeoJSON/JSON ausserhalb der Resource-Hierarchie).
5. **[NarcoMarshDev/Enforce-Script-Extensions](https://github.com/NarcoMarshDev/Enforce-Script-Extensions)** — Script-Bibliothek + DiscordRP Plugin. `DiscordRP/` ist das **kanonische External-IPC-Pattern**: Plugin schreibt State-File, externer `EnfusionWorkbenchRP.exe` Companion liest und sendet an Discord. Direkt uebertragbar auf "Plugin schreibt Spec-Request, externes AI-Backend liest und schreibt Response".
6. **[Arkensor/EnfusionDatabaseFramework](https://github.com/Arkensor/EnfusionDatabaseFramework)** — DB-Framework fuer SQL/Mongo/File-DBs (54 stars, MIT, last push 14.04.2026). Reference fuer **Datenbank-Bruecken aus laufendem Workbench/Game**. Relevant fuer Backend-Sync Patterns.
7. **[ofpisnotdead-com/awesome-reforger](https://github.com/ofpisnotdead-com/awesome-reforger)** — Curated List, aktiv 14.05.2026. Verzeichnis aller Community-Tools.

Bonus: **[BohemiaInteractive/Arma-Reforger-Misc](https://github.com/BohemiaInteractive/Arma-Reforger-Misc)** — weitere offizielle Modder-Ressourcen.
