// AI_GeneratePlugin.c — Arma Reforger Workbench Plugin
//
// Sprint MEGA-A (A.S5PREP.4) — Refactored with REAL WorldEditorAPI method names
// Sprint B will implement the TODO sections.
//
// Architecture summary:
//
//   ai-spec.json schema:
//   { mission_id, version, ops: [{op, class, prefab_guid, coords, props}] }
//
//   Reload mechanism: external chokidar / PowerShell FileSystemWatcher detects
//   ai-spec.json change, simulates Ctrl+Shift+R into Workbench window via
//   SendKeys / nircmd, triggering Workbench "Reload WB Scripts".
//   Plugin's Run() reads ai-spec.json and applies ops.
//
//   Realistic latency: 1-2s with sendkey hack, 5-10s with manual Shift+F7
//
// Sources:
//   Arma-Reforger-Script-Diff/scripts/Core/generated/WorkbenchAPI/WorldEditorAPI.c
//   Arma-Reforger-Script-Diff/scripts/GameLib/generated/WorkbenchAPI/Plugins/WorldEditorPlugin.c
//   Arma-Reforger-Samples/SampleMod_WorkbenchPlugin/Scripts/.../SampleWorldEditorPlugin.c
//   research/11-s5-readiness-roadmap.md

#ifdef WORKBENCH

// Attribute registers plugin with Workbench: menu name, keyboard shortcut, required module
[WorkbenchPluginAttribute(
    name: "AI Generate Mission",
    description: "ELOS AI-Native Mission Authoring — reads ai-spec.json and applies ops via WorldEditorAPI",
    category: "ELOS",
    shortcut: "Ctrl+Shift+G",
    wbModules: {"WorldEditor"}
)]
class AI_GeneratePlugin : WorldEditorPlugin
{
    // -------------------------------------------------------------------------
    // Configuration — paths use Workbench $profile: alias
    // -------------------------------------------------------------------------

    //! ai-spec.json written by Python backend (POST /missions/revise)
    protected static const string SPEC_FILE_PATH  = "$profile:elos/ai-spec.json";
    //! Plugin log (grep for "OK:" / "ERR:" to determine pass/fail in headless mode)
    protected static const string LOG_FILE_PATH   = "$profile:elos/ai-generate-log.txt";
    //! Max entities per Run() invocation (safety against runaway generation)
    protected static const int    MAX_OPS         = 500;

    // -------------------------------------------------------------------------
    // Entry point — called by Workbench when:
    //   a) User clicks ELOS > "AI Generate Mission" menu item
    //   b) User presses Ctrl+Shift+G shortcut
    //   c) External file-watcher sends Ctrl+Shift+R (script reload) into window
    //      after ai-spec.json changes — plugin Run() fires automatically
    // -------------------------------------------------------------------------

    override void Run()
    {
        Log("AI_GeneratePlugin: Run() triggered");

        // Step 1: Access WorldEditorAPI (pattern confirmed from SampleWorldEditorPlugin.c)
        WorldEditor worldEditor = Workbench.GetModule(WorldEditor);
        if (!worldEditor)
        {
            LogErr("WorldEditor module not available — is WorldEditor open?");
            Workbench.Dialog("AI Generate", "Error: WorldEditor module not available.");
            return;
        }
        WorldEditorAPI api = worldEditor.GetApi();
        if (!api)
        {
            LogErr("WorldEditorAPI unavailable");
            return;
        }

        // Step 2: Resolve and load ai-spec.json
        string specAbsPath;
        if (!Workbench.GetAbsolutePath(SPEC_FILE_PATH, specAbsPath, false))
        {
            // Path resolve failed — likely first run, no spec yet
            LogErr("Cannot resolve spec path: " + SPEC_FILE_PATH);
            Workbench.Dialog("AI Generate", "ai-spec.json not found.\nRun the Python backend to generate it first.");
            return;
        }

        string specContent = "";
        if (!ReadFile(specAbsPath, specContent) || specContent.Length() == 0)
        {
            LogErr("Cannot read spec: " + specAbsPath);
            return;
        }
        Log("Spec loaded: " + specContent.Length().ToString() + " chars from " + specAbsPath);

        // Step 3: Parse ai-spec.json
        //
        // TODO (Sprint B): Implement Enforce-Script JSON parsing.
        //
        // Enforce Script JSON pattern (per Script-Diff research):
        //   ScriptConvert.SerializeToString(object, outJsonString, flags);  // serialize
        //   // For deserialization, use JsonApiDeserializer or custom string parser
        //   // See SCR_JsonSerializer in Script-Diff for reference
        //
        // Expected ai-spec.json schema:
        // {
        //   "mission_id": "night-recon-everon",
        //   "version": 1,
        //   "ops": [
        //     { "op": "attribute-edit", "target": "fog_density", "value": "0.9" },
        //     { "op": "entity-create",  "class": "GenericEntity", "name": "patrol-01",
        //       "layer_id": 0, "coords": [123.0, 0.0, 456.0], "angles": [0,0,0] },
        //     { "op": "entity-delete",  "entity_name": "patrol-02" }
        //   ]
        // }
        //
        // For Sprint A: log content only (no parse)
        Log("Spec parse: TODO (Sprint B) — spec loaded OK, " + specContent.Length().ToString() + " chars");

        // Step 4: Apply ops via WorldEditorAPI
        //
        // Pattern for entity create (from WorldEditorAPI.c):
        //
        //   api.BeginEntityAction("AI-Create");
        //   IEntitySource ent = api.CreateEntity(
        //       "GenericEntity",    // className
        //       "patrol-waypoint",  // name
        //       0,                  // layerId (0 = root/default layer)
        //       null,               // parent (null = world root)
        //       "123.0 0.0 456.0",  // coords as vector string — TODO: verify format
        //       "0 0 0"             // angles
        //   );
        //   if (ent)
        //       Log("OK: created " + ent.GetClassName() + " at coords");
        //   else
        //       LogErr("ERR: CreateEntity failed for GenericEntity");
        //   api.EndEntityAction("AI-Create");
        //
        // Pattern for property edit (from WorldEditorAPI.c ModifyEntityKey):
        //
        //   IEntitySource target = api.FindEntityByName("FogController");
        //   if (target)
        //   {
        //       api.BeginEntityAction("AI-FogEdit");
        //       api.BeginEditSequence(target);   // batch edit = no re-init per op
        //       api.ModifyEntityKey(target, "fogDensity", "0.9");
        //       api.EndEditSequence(target);
        //       api.EndEntityAction("AI-FogEdit");
        //       Log("OK: fogDensity set to 0.9");
        //   }
        //
        // Pattern for entity delete:
        //
        //   IEntitySource toDelete = api.FindEntityByName("patrol-02");
        //   if (toDelete)
        //   {
        //       api.BeginEntityAction("AI-Delete");
        //       // TODO: find correct delete method — CutSelectedEntities() or
        //       // direct delete via DuplicateSelectedEntities + undo pattern
        //       api.EndEntityAction("AI-Delete");
        //   }

        // TODO (Sprint B): Deserialize ops[] array + loop over ops applying each
        Log("OK: Run() complete — ops apply TODO (Sprint B)");
        Workbench.Dialog("AI Generate", "ai-spec.json loaded OK.\nOps apply: Sprint B implementation pending.\nSee " + LOG_FILE_PATH + " for details.");
    }

    // -------------------------------------------------------------------------
    // Configure — opens settings dialog (optional, Sprint B can add fields)
    // -------------------------------------------------------------------------

    override void Configure()
    {
        // TODO (Sprint B): show a settings dialog (spec path override, dry-run mode, etc.)
        Workbench.Dialog("AI Generate Settings", "Spec path: " + SPEC_FILE_PATH);
    }

    // -------------------------------------------------------------------------
    // Utility: file read
    // -------------------------------------------------------------------------

    protected bool ReadFile(string absPath, out string content)
    {
        FileHandle fh = FileIO.OpenFile(absPath, FileMode.READ);
        if (!fh)
            return false;

        string line;
        while (fh.ReadLine(line) >= 0)
            content += line + "\n";

        fh.Close();
        return content.Length() > 0;
    }

    // -------------------------------------------------------------------------
    // Utility: logging
    // -------------------------------------------------------------------------

    protected void Log(string msg)
    {
        // Workbench console output (visible when Workbench is open)
        Print("[AI_GeneratePlugin] " + msg);

        // Append to log file — used by headless test harness to determine PASS/FAIL
        // grep "^OK:" = pass, grep "^ERR:" = fail
        FileHandle lf = FileIO.OpenFile(LOG_FILE_PATH, FileMode.APPEND);
        if (lf)
        {
            lf.WriteLine(msg);
            lf.Close();
        }
    }

    protected void LogErr(string msg)
    {
        Print("[AI_GeneratePlugin ERROR] " + msg);
        FileHandle lf = FileIO.OpenFile(LOG_FILE_PATH, FileMode.APPEND);
        if (lf)
        {
            lf.WriteLine("ERR: " + msg);
            lf.Close();
        }
    }
}

#endif // WORKBENCH
