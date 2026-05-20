// AI_GeneratePlugin.c — Arma Reforger Workbench Plugin Skeleton
//
// Phase 2 deliverable — NOT active in Phase 1 MVP.
// Awaiting Windows Workbench access.
//
// Purpose: Read ai-spec.json from $profile, call WorldEditorAPI to create entities.
// Activation: when Win-Zugang verfügbar, see workbench-plugin/README.md
//
// Reference:
//   - research/01-workbench-sdk.md (Hybrid B Plugin Pattern)
//   - CoalitionArma/Coalition-Reforger-Framework CRF_MissionCreationPlugin.c
//   - BohemiaInteractive/Arma-Reforger-Script-Diff (official API dump)
//
// IMPORTANT: This is Enforce Script (.c), NOT C/C++.
// Compilation: Workbench only. No standalone build.

[WorkbenchPluginAttribute(name: "AI_GeneratePlugin", description: "ELOS AI-Native Mission Generation — reads ai-spec.json and creates entities via WorldEditorAPI.")]
class AI_GeneratePlugin: WorkbenchPlugin
{
    // ---- Configuration -------------------------------------------------------

    // Path to spec file written by Python backend
    // Use $profile: alias for ArmaReforger profile directory
    static const string SPEC_FILE_PATH = "$profile:elos/ai-spec.json";

    // Log file for debugging headless runs
    static const string LOG_FILE_PATH = "$profile:elos/ai-generate-log.txt";

    // Max entities to create in one run (safety limit)
    static const int MAX_ENTITIES = 500;

    // ---- Plugin Lifecycle ---------------------------------------------------

    override void OnActivate(inout array<ref WorkbenchPluginOperation> outOperations)
    {
        // Register operations that appear in Workbench menu
        WorkbenchPluginOperation genOp = new WorkbenchPluginOperation();
        genOp.m_sName = "Generate from AI Spec";
        genOp.m_sDescription = "Load ai-spec.json and generate mission entities";
        outOperations.Insert(genOp);

        WorkbenchPluginOperation syncOp = new WorkbenchPluginOperation();
        syncOp.m_sName = "Check Spec File";
        syncOp.m_sDescription = "Verify ai-spec.json exists and is valid";
        outOperations.Insert(syncOp);
    }

    override void OnOperationExecuted(string operationName)
    {
        if (operationName == "Generate from AI Spec")
        {
            GenerateFromSpec();
        }
        else if (operationName == "Check Spec File")
        {
            CheckSpecFile();
        }
    }

    // ---- Core Logic ---------------------------------------------------------

    void GenerateFromSpec()
    {
        Log("AI_GeneratePlugin: Starting generation from " + SPEC_FILE_PATH);

        // Read spec file
        string specContent = "";
        if (!ReadSpecFile(specContent))
        {
            LogError("Cannot read spec file: " + SPEC_FILE_PATH);
            return;
        }

        // Parse JSON spec
        // NOTE: Enforce Script has limited JSON support via JsonSerializer
        // For Phase 2 implementation, use Workbench's JSON API
        // Ref: Workbench.JsonSerializer.Deserialize()

        // TODO Phase 2: Implement full JSON parsing
        // For now: log the spec content for debugging
        Log("Spec content loaded (" + specContent.Length().ToString() + " chars)");

        // === PHASE 2 IMPLEMENTATION POINT ===
        // The following is pseudocode showing the intended logic:
        //
        // AISpec spec = new AISpec();
        // JsonSerializer.Deserialize(spec, specContent);
        //
        // WorldEditorAPI api = Workbench.GetModule(WorldEditorAPI);
        // WorldEditor editor = api.GetCurrentEditor();
        //
        // foreach (SpawnPointSpec sp : spec.spawn_points)
        // {
        //     IEntitySource entity = api.CreateEntity(sp.class_name, sp.prefab_guid, sp.coords);
        //     if (!entity)
        //     {
        //         LogError("Failed to create entity: " + sp.class_name);
        //         continue;
        //     }
        //     Log("Created: " + sp.class_name + " at " + sp.coords.ToString());
        // }
        //
        // editor.Save();
        // Log("Generation complete. " + spec.spawn_points.Count() + " entities created.");

        Log("SKELETON ONLY — Phase 2 implementation pending Win-Zugang");
    }

    void CheckSpecFile()
    {
        string content = "";
        if (ReadSpecFile(content))
        {
            Log("Spec file OK: " + SPEC_FILE_PATH + " (" + content.Length().ToString() + " chars)");
            Print("[AI_GeneratePlugin] Spec file: OK");
        }
        else
        {
            LogError("Spec file not found or unreadable: " + SPEC_FILE_PATH);
            Print("[AI_GeneratePlugin] Spec file: MISSING — run backend to generate ai-spec.json first");
        }
    }

    // ---- Utilities ----------------------------------------------------------

    bool ReadSpecFile(out string content)
    {
        FileHandle fh = FileIO.OpenFile(SPEC_FILE_PATH, FileMode.READ);
        if (!fh)
            return false;

        string line;
        while (fh.ReadLine(line) >= 0)
        {
            content += line;
        }
        fh.Close();
        return content.Length() > 0;
    }

    void Log(string message)
    {
        Print("[AI_GeneratePlugin] " + message);

        // Also write to log file for headless debugging
        FileHandle logFh = FileIO.OpenFile(LOG_FILE_PATH, FileMode.APPEND);
        if (logFh)
        {
            logFh.WriteLine("[" + System.GetTime() + "] " + message);
            logFh.Close();
        }
    }

    void LogError(string message)
    {
        Print("[AI_GeneratePlugin ERROR] " + message);

        FileHandle logFh = FileIO.OpenFile(LOG_FILE_PATH, FileMode.APPEND);
        if (logFh)
        {
            logFh.WriteLine("[" + System.GetTime() + "] ERROR: " + message);
            logFh.Close();
        }
    }
}

// ---- Data classes (Phase 2 stubs) ------------------------------------------
// These will be populated when Enforce Script JSON parsing is implemented

class AISpec
{
    // Populated from ai-spec.json
    // ref array<ref SpawnPointSpec> spawn_points;
    // ref array<ref AIGroupSpec> ai_groups;
    // ref array<ref WaypointSpec> waypoints;
    // string mission_id;
}
