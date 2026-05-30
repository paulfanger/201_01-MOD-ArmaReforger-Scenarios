// AI_GeneratePlugin.c — ELOS Live Mission Editor Plugin
// Sprint STAGE-A (S5 Close) — Refactored to documented Bohemia RunCommandline() pattern
//
// TWO ENTRY POINTS:
//   1. RunCommandline() — CLI-driven, WorldEditor guaranteed active via -wbmodule=WorldEditor
//   2. Run()            — Menu-driven (ELOS > AI Generate Mission), may need WorldEditor open
//
// CLI INVOCATION (guaranteed to work, per postmortem Failure #4 fix):
//   ArmaReforgerWorkbenchSteamDiag.exe ^
//     -gproj "path\to\addon.gproj" ^
//     -wbmodule=WorldEditor ^
//     -plugin=AI_GeneratePlugin ^
//     -exitAfterInit ^
//     -- -input=spec.json -output=outbox.json
//
// FILE PATHS (spec.json + outbox.json):
//   Default: $profile:ELOS/spec.json + $profile:ELOS/outbox.json
//   CLI override: -input=<absPath> -output=<absPath>
//
// SPEC FORMAT: { "ops": [{ "op": "attribute_edit|entity_create|...", ... }] }
//
// Sources: Arma-Reforger-Script-Diff ShoreTool.c + WorldTestTool.c (GetCmdLine pattern)

#ifdef WORKBENCH

[WorkbenchPluginAttribute(
    name: "AI Generate Mission",
    description: "ELOS Live Editor - RunCommandline for CLI, Run for menu. See category ELOS.",
    category: "ELOS",
    shortcut: "Ctrl+Shift+G"
)]
class AI_GeneratePlugin : WorkbenchPlugin
{
    // Default paths (used when no CLI -input/-output args given)
    static const string DEFAULT_SPEC_PATH   = "$profile:ELOS/spec.json";
    static const string DEFAULT_OUTBOX_PATH = "$profile:ELOS/outbox.json";
    static const string LOG_PATH            = "$profile:ELOS/plugin-log.txt";

    // -------------------------------------------------------------------------
    // ENTRY POINT 1: CLI (called by -plugin=AI_GeneratePlugin with -wbmodule=WorldEditor)
    // WorldEditor is guaranteed active when -wbmodule=WorldEditor is used.
    // Pattern: ShoreTool.c + WorldTestTool.c (RunCommandline + GetCmdLine)

    override void RunCommandline()
    {
        Log("AI_GeneratePlugin.RunCommandline() - CLI mode starting");

        // Ensure WorldEditor is open (may already be active via -wbmodule=WorldEditor)
        WorldEditor we = Workbench.GetModule(WorldEditor);
        if (!we)
        {
            Log("WorldEditor not active, opening module...");
            Workbench.OpenModule(WorldEditor);
            we = Workbench.GetModule(WorldEditor);
        }

        if (!we)
        {
            Log("ERROR: WorldEditor module unavailable in CLI mode");
            WriteOutbox(DEFAULT_OUTBOX_PATH, "error", 0, {"WorldEditor module unavailable"});
            Workbench.Exit(-1);
            return;
        }

        WorldEditorAPI api = we.GetApi();
        if (!api)
        {
            Log("ERROR: WorldEditorAPI unavailable");
            WriteOutbox(DEFAULT_OUTBOX_PATH, "error", 0, {"WorldEditorAPI unavailable"});
            Workbench.Exit(-1);
            return;
        }

        // Parse CLI args using documented Bohemia pattern (per ShoreTool.c line 12, WorldTestTool.c line 9)
        // CLI: -- -input=<path> -output=<path>
        string specArgPath;
        string outboxArgPath;
        we.GetCmdLine("-input", specArgPath);
        we.GetCmdLine("-output", outboxArgPath);

        // Fall back to defaults if not provided
        string specAbsPath;
        string outboxAbsPath;

        if (specArgPath)
        {
            specAbsPath = specArgPath;
            Log("spec path from CLI arg: " + specAbsPath);
        }
        else
        {
            if (!Workbench.GetAbsolutePath(DEFAULT_SPEC_PATH, specAbsPath, false))
            {
                Log("ERROR: Cannot resolve default spec path: " + DEFAULT_SPEC_PATH);
                WriteOutbox(DEFAULT_OUTBOX_PATH, "error", 0, {"spec.json path not resolvable"});
                Workbench.Exit(-1);
                return;
            }
        }

        if (outboxArgPath)
        {
            outboxAbsPath = outboxArgPath;
        }
        else
        {
            if (!Workbench.GetAbsolutePath(DEFAULT_OUTBOX_PATH, outboxAbsPath, false))
            {
                Log("WARNING: Cannot resolve default outbox path, using spec dir");
                outboxAbsPath = specAbsPath;  // fallback, shouldn't happen
            }
        }

        Log("spec: " + specAbsPath);
        Log("outbox: " + outboxAbsPath);

        // Execute
        int exitCode = DoWork(api, specAbsPath, outboxAbsPath);
        Log("RunCommandline() done, exit code: " + exitCode.ToString());
        Workbench.Exit(exitCode);
    }

    // -------------------------------------------------------------------------
    // ENTRY POINT 2: Menu (called by ELOS > AI Generate Mission menu click)
    // WorldEditor must be the active module when this fires.

    override void Run()
    {
        Log("AI_GeneratePlugin.Run() - menu mode starting");

        WorldEditor we = Workbench.GetModule(WorldEditor);
        if (!we)
        {
            WriteOutbox(DEFAULT_OUTBOX_PATH, "error", 0, {"WorldEditor module unavailable - open via Editors > World Editor first"});
            Workbench.Dialog("AI Generate Mission", "Open World Editor first (Editors menu), then try again.");
            return;
        }

        WorldEditorAPI api = we.GetApi();
        if (!api)
        {
            WriteOutbox(DEFAULT_OUTBOX_PATH, "error", 0, {"WorldEditorAPI unavailable"});
            return;
        }

        string specAbsPath;
        string outboxAbsPath;
        if (!Workbench.GetAbsolutePath(DEFAULT_SPEC_PATH, specAbsPath, false))
        {
            WriteOutbox(DEFAULT_OUTBOX_PATH, "error", 0, {"spec.json not found at: " + DEFAULT_SPEC_PATH});
            Workbench.Dialog("AI Generate Mission", "spec.json not found. Run elos_chat.py first.");
            return;
        }
        Workbench.GetAbsolutePath(DEFAULT_OUTBOX_PATH, outboxAbsPath, false);

        DoWork(api, specAbsPath, outboxAbsPath);
    }

    // -------------------------------------------------------------------------
    // SHARED WORK: parse spec.json + execute ops via WorldEditorAPI

    protected int DoWork(WorldEditorAPI api, string specAbsPath, string outboxAbsPath)
    {
        // Read spec.json
        string specContent;
        if (!ReadFile(specAbsPath, specContent) || specContent.Length() == 0)
        {
            Log("ERROR: spec.json empty or unreadable: " + specAbsPath);
            WriteOutbox(outboxAbsPath, "error", 0, {"spec.json empty or unreadable: " + specAbsPath});
            return -1;
        }
        Log("spec loaded: " + specContent.Length().ToString() + " chars");

        // Parse ops
        array<ref SCR_AIOp> ops = ParseOps(specContent);
        if (!ops || ops.Count() == 0)
        {
            Log("No ops in spec - nothing to do");
            WriteOutbox(outboxAbsPath, "ok", 0, {});
            return 0;
        }

        Log("Executing " + ops.Count().ToString() + " ops...");

        // Execute ops
        int applied = 0;
        array<string> errors = {};

        api.BeginEntityAction("ELOS-batch");
        foreach (SCR_AIOp op : ops)
        {
            string err = ApplyOp(api, op);
            if (err.IsEmpty())
                applied++;
            else
            {
                errors.Insert(err);
                Log("Op error: " + err);
            }
        }
        api.EndEntityAction("ELOS-batch");

        string status;
        if (errors.Count() == 0)
            status = "ok";
        else
            status = "partial";

        WriteOutbox(outboxAbsPath, status, applied, errors);
        Log("Done: " + applied.ToString() + " applied, " + errors.Count().ToString() + " errors");
        if (errors.Count() == 0)
            return 0;
        else
            return 1;
    }

    // -------------------------------------------------------------------------
    // Op dispatch

    protected string ApplyOp(WorldEditorAPI api, SCR_AIOp op)
    {
        switch (op.op_type)
        {
            case "attribute_edit":  return Op_AttributeEdit(api, op);
            case "entity_create":   return Op_EntityCreate(api, op);
            case "entity_delete":   return Op_EntityDelete(api, op);
            case "entity_move":     return Op_EntityMove(api, op);
            case "batch":
            {
                foreach (SCR_AIOp sub : op.sub_ops)
                {
                    string err = ApplyOp(api, sub);
                    if (!err.IsEmpty())
                        return err;
                }
                return "";
            }
            default: return "unknown op_type: " + op.op_type;
        }
        return "";
    }

    // ---- attribute_edit -------------------------------------------------------
    protected string Op_AttributeEdit(WorldEditorAPI api, SCR_AIOp op)
    {
        if (op.target.IsEmpty() || op.field.IsEmpty())
            return "attribute_edit: target and field required";

        IEntitySource ent = api.FindEntityByName(op.target);
        if (!ent)
            return "attribute_edit: entity not found: " + op.target;

        api.BeginEditSequence(ent);
        bool ok = api.SetVariableValue(ent, null, op.field, op.value);
        api.EndEditSequence(ent);

        if (!ok)
            return "attribute_edit: SetVariableValue failed for " + op.field + " on " + op.target;

        Log("attribute_edit: " + op.target + "." + op.field + " = " + op.value);
        return "";
    }

    // ---- entity_create --------------------------------------------------------
    protected string Op_EntityCreate(WorldEditorAPI api, SCR_AIOp op)
    {
        if (op.class_name.IsEmpty())
            return "entity_create: class required";

        string coords;
        if (op.coords.IsEmpty())
            coords = "0 0 0";
        else
            coords = op.coords;

        IEntitySource newEnt = api.CreateEntity(
            op.class_name,
            op.name,
            op.layer_id,
            null,
            coords.ToVector(),
            Vector(0, 0, 0)
        );

        if (!newEnt)
            return "entity_create: CreateEntity returned null for " + op.class_name;

        foreach (SCR_KVPair kv : op.props)
            api.SetVariableValue(newEnt, null, kv.key, kv.value);

        Log("entity_create: " + op.class_name + " '" + op.name + "' at " + coords);
        return "";
    }

    // ---- entity_delete --------------------------------------------------------
    protected string Op_EntityDelete(WorldEditorAPI api, SCR_AIOp op)
    {
        if (op.target.IsEmpty())
            return "entity_delete: target required";

        IEntitySource ent = api.FindEntityByName(op.target);
        if (!ent)
            return "entity_delete: entity not found: " + op.target;

        api.DeleteEntity(ent);
        Log("entity_delete: " + op.target);
        return "";
    }

    // ---- entity_move ----------------------------------------------------------
    protected string Op_EntityMove(WorldEditorAPI api, SCR_AIOp op)
    {
        if (op.target.IsEmpty() || op.coords.IsEmpty())
            return "entity_move: target and coords required";

        IEntitySource ent = api.FindEntityByName(op.target);
        if (!ent)
            return "entity_move: entity not found: " + op.target;

        api.BeginEditSequence(ent);
        api.SetVariableValue(ent, null, "coords", op.coords);
        api.EndEditSequence(ent);

        Log("entity_move: " + op.target + " -> " + op.coords);
        return "";
    }

    // -------------------------------------------------------------------------
    // JSON parser (Enforce Script string-based, no stdlib JSON)

    protected array<ref SCR_AIOp> ParseOps(string json)
    {
        array<ref SCR_AIOp> result = {};

        int opsStart = json.IndexOf("\"ops\"");
        if (opsStart < 0)
            return result;

        string afterOpsKey = json.Substring(opsStart, json.Length() - opsStart);
        int relArrOpen = afterOpsKey.IndexOf("[");
        int arrOpen;
        if (relArrOpen >= 0)
            arrOpen = opsStart + relArrOpen;
        else
            arrOpen = -1;

        if (arrOpen < 0)
            return result;

        int depth = 0;
        int objStart = -1;
        int i = arrOpen;
        int len = json.Length();
        bool inStr = false;

        while (i < len)
        {
            string ch = json.Get(i);

            if (ch == "\"" && (i == 0 || json.Get(i - 1) != "\\"))
                inStr = !inStr;

            if (!inStr)
            {
                if (ch == "{")
                {
                    if (depth == 0)
                        objStart = i;
                    depth++;
                }
                else if (ch == "}")
                {
                    depth--;
                    if (depth == 0 && objStart >= 0)
                    {
                        string objStr = json.Substring(objStart, i - objStart + 1);
                        SCR_AIOp op = ParseSingleOp(objStr);
                        if (op)
                            result.Insert(op);
                        objStart = -1;
                    }
                }
                else if (ch == "]" && depth == 0)
                    break;
            }
            i++;
        }

        return result;
    }

    protected SCR_AIOp ParseSingleOp(string obj)
    {
        SCR_AIOp op = new SCR_AIOp();
        op.op_type    = ExtractStringField(obj, "op");
        op.target     = ExtractStringField(obj, "target");
        op.field      = ExtractStringField(obj, "field");
        op.value      = ExtractStringField(obj, "value");
        op.class_name = ExtractStringField(obj, "class");
        op.name       = ExtractStringField(obj, "name");
        op.coords     = ExtractStringField(obj, "coords");
        string layerStr = ExtractStringField(obj, "layer_id");
        if (layerStr.IsEmpty())
            op.layer_id = 0;
        else
            op.layer_id = layerStr.ToInt();

        if (op.op_type.IsEmpty())
            return null;

        if (op.op_type == "batch")
        {
            int subStart = obj.IndexOf("\"sub_ops\"");
            if (subStart >= 0)
                op.sub_ops = ParseOps(obj.Substring(subStart, obj.Length() - subStart));
        }
        return op;
    }

    protected string ExtractStringField(string json, string fieldName)
    {
        string needle = "\"" + fieldName + "\"";
        int pos = json.IndexOf(needle);
        if (pos < 0) return "";

        string searchArea1 = json.Substring(pos + needle.Length(), json.Length() - pos - needle.Length());
        int relColon = searchArea1.IndexOf(":");
        int colon;
        if (relColon >= 0)
            colon = pos + needle.Length() + relColon;
        else
            colon = -1;

        if (colon < 0) return "";

        int valStart = colon + 1;
        while (valStart < json.Length() && json.Get(valStart) == " ")
            valStart++;

        if (valStart >= json.Length()) return "";

        if (json.Get(valStart) == "\"")
        {
            string searchArea2 = json.Substring(valStart + 1, json.Length() - valStart - 1);
            int relEnd = searchArea2.IndexOf("\"");
            int end;
            if (relEnd >= 0)
                end = valStart + 1 + relEnd;
            else
                end = -1;

            if (end < 0) return "";
            return json.Substring(valStart + 1, end - valStart - 1);
        }

        int end2 = valStart;
        while (end2 < json.Length())
        {
            string c = json.Get(end2);
            if (c == "," || c == "}" || c == "]" || c == " " || c == "\n" || c == "\r")
                break;
            end2++;
        }
        return json.Substring(valStart, end2 - valStart);
    }

    // -------------------------------------------------------------------------
    // outbox.json writer (takes explicit path for both CLI and menu modes)

    protected void WriteOutbox(string absPath, string status, int appliedCount, array<string> errors)
    {
        string outboxAbsPath = absPath;
        if (outboxAbsPath.IsEmpty())
        {
            if (!Workbench.GetAbsolutePath(DEFAULT_OUTBOX_PATH, outboxAbsPath, false))
                return;
        }

        string errArr = "";
        if (errors && errors.Count() > 0)
        {
            foreach (int idx, string e : errors)
            {
                if (idx > 0) errArr += ",";
                errArr += "\"" + e + "\"";
            }
        }

        string json = string.Format(
            "{\"status\":\"%1\",\"applied_count\":%2,\"errors\":[%3]}",
            status, appliedCount.ToString(), errArr
        );

        FileHandle fh = FileIO.OpenFile(outboxAbsPath, FileMode.WRITE);
        if (fh)
        {
            fh.WriteLine(json);
            fh.Close();
        }
    }

    // -------------------------------------------------------------------------
    // File I/O + logging

    protected bool ReadFile(string absPath, out string content)
    {
        FileHandle fh = FileIO.OpenFile(absPath, FileMode.READ);
        if (!fh) return false;
        string line;
        while (fh.ReadLine(line) >= 0)
            content += line;
        fh.Close();
        return content.Length() > 0;
    }

    protected void Log(string msg)
    {
        Print("[AI_GeneratePlugin] " + msg);
        string absPath;
        if (Workbench.GetAbsolutePath(LOG_PATH, absPath, false))
        {
            FileHandle lf = FileIO.OpenFile(absPath, FileMode.APPEND);
            if (lf) { lf.WriteLine(msg); lf.Close(); }
        }
    }
}

// -------------------------------------------------------------------------
// Data classes

class SCR_AIOp
{
    string op_type;
    string target;
    string field;
    string value;
    string class_name;
    string name;
    string coords;
    int    layer_id;
    ref array<ref SCR_KVPair> props = {};
    ref array<ref SCR_AIOp>   sub_ops = {};
}

class SCR_KVPair
{
    string key;
    string value;
}

#endif // WORKBENCH
