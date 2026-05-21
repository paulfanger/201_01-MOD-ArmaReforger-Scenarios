// AI_GeneratePlugin.c — ELOS Live Mission Editor Plugin
// Sprint FINAL-S5-MAXED (F.3) — Full implementation with 5 op-types
//
// Architecture:
//   elos_chat.py → writes spec.json → AHK detects change → Ctrl+Shift+R
//   → Workbench reloads WB Scripts → this plugin's Run() executes
//   → reads spec.json → applies WorldEditorAPI ops → writes outbox.json
//   → elos_chat.py reads outbox.json → shows confirmation + latency
//
// Spec.json schema:
//   { "mission_id": "...", "version": "ISO8601", "ops": [...], "narrative_patch": [...] }
//
// Op schema:
//   attribute_edit: { "op": "attribute_edit", "target": "entityName|className", "field": "varName", "value": "strValue" }
//   entity_create:  { "op": "entity_create", "class": "ClassName", "name": "entName", "coords": "x y z", "layer_id": 0 }
//   entity_delete:  { "op": "entity_delete", "target": "entityName" }
//   entity_move:    { "op": "entity_move", "target": "entityName", "coords": "x y z" }
//   batch:          { "op": "batch", "sub_ops": [...] }
//
// Sources: Arma-Reforger-Script-Diff WorldEditorAPI.c, WorldExporterPlugin.c, SampleWorldEditorPlugin.c

#ifdef WORKBENCH

[WorkbenchPluginAttribute(
    name: "AI Generate Mission",
    description: "ELOS Live Editor - reads spec.json, applies ops, writes outbox.json",
    category: "ELOS",
    shortcut: "Ctrl+Shift+G"
)]
class AI_GeneratePlugin : WorkbenchPlugin
{
    // -------------------------------------------------------------------------
    // Paths

    static const string SPEC_PATH   = "$profile:ELOS/spec.json";
    static const string OUTBOX_PATH = "$profile:ELOS/outbox.json";
    static const string LOG_PATH    = "$profile:ELOS/plugin-log.txt";

    // -------------------------------------------------------------------------
    // Entry Point

    override void Run()
    {
        Log("AI_GeneratePlugin.Run() - reading spec");

        WorldEditor worldEditor = Workbench.GetModule(WorldEditor);
        if (!worldEditor)
        {
            WriteOutbox("error", 0, {"WorldEditor module unavailable"});
            return;
        }
        WorldEditorAPI api = worldEditor.GetApi();
        if (!api)
        {
            WriteOutbox("error", 0, {"WorldEditorAPI unavailable"});
            return;
        }

        // Load spec.json
        string specAbsPath;
        if (!Workbench.GetAbsolutePath(SPEC_PATH, specAbsPath, false))
        {
            WriteOutbox("error", 0, {"spec.json path not resolvable: " + SPEC_PATH});
            return;
        }
        string specContent;
        if (!ReadFile(specAbsPath, specContent) || specContent.Length() == 0)
        {
            WriteOutbox("error", 0, {"spec.json empty or unreadable: " + specAbsPath});
            return;
        }
        Log("spec.json loaded (" + specContent.Length().ToString() + " chars)");

        // Parse ops array from spec JSON
        // Enforce Script JSON: use string parsing (no stdlib JSON)
        array<ref SCR_AIOp> ops = ParseOps(specContent);
        if (!ops || ops.Count() == 0)
        {
            WriteOutbox("ok", 0, {});
            Log("No ops in spec - nothing to do");
            return;
        }

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
                errors.Insert(err);
        }
        api.EndEntityAction("ELOS-batch");

        string status;
        if (errors.Count() == 0)
            status = "ok";
        else
            status = "partial";
        WriteOutbox(status, applied, errors);
        Log("Done: " + applied.ToString() + " applied, " + errors.Count().ToString() + " errors");
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

    // ---- attribute_edit ------------------------------------------------------
    // Sets a named variable on an entity.
    // target: entity name in scene (e.g. "WeatherManager", "weatherManager_0")
    // field:  variable name (e.g. "m_fFogDensity")
    // value:  string representation (e.g. "0.7" or "true")
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

    // ---- entity_create -------------------------------------------------------
    // Creates a new entity of given class at given world coords.
    // class:    Enforce class name (e.g. "GenericEntity", "SCR_AIGroupEntity")
    // name:     display name for the new entity
    // coords:   "x y z" world-space
    // layer_id: sub-scene layer (0 = root)
    protected string Op_EntityCreate(WorldEditorAPI api, SCR_AIOp op)
    {
        if (op.class_name.IsEmpty())
            return "entity_create: class required";

        string coords;
        if (op.coords.IsEmpty())
            coords = "0 0 0";
        else
            coords = op.coords;
        int layerId = op.layer_id;

        IEntitySource newEnt = api.CreateEntity(
            op.class_name,
            op.name,
            layerId,
            null,   // no parent
            coords.ToVector(),
            Vector(0, 0, 0)
        );

        if (!newEnt)
            return "entity_create: CreateEntity returned null for " + op.class_name;

        // Apply extra props if given (key=value pairs)
        foreach (SCR_KVPair kv : op.props)
        {
            api.SetVariableValue(newEnt, null, kv.key, kv.value);
        }

        Log("entity_create: " + op.class_name + " '" + op.name + "' at " + coords);
        return "";
    }

    // ---- entity_delete -------------------------------------------------------
    // Deletes the entity by name.
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

    // ---- entity_move ---------------------------------------------------------
    // Moves entity to new world coords.
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
    // Minimal JSON op parser — extracts ops array from spec.json
    // Real JSON parsing in Enforce Script requires ScriptConvert (available in runtime)
    // For Workbench plugin: use string tokenisation on known schema

    protected array<ref SCR_AIOp> ParseOps(string json)
    {
        array<ref SCR_AIOp> result = {};

        // Find "ops": [ ... ]
        int opsStart = json.IndexOf("\"ops\"");
        if (opsStart < 0)
            return result;

        // Find the opening [ of the ops array
        string afterOpsKey = json.Substring(opsStart, json.Length() - opsStart);
        int relArrOpen = afterOpsKey.IndexOf("[");
        int arrOpen;
        if (relArrOpen >= 0)
            arrOpen = opsStart + relArrOpen;
        else
            arrOpen = -1;
        if (arrOpen < 0)
            return result;

        // Extract each { ... } object from the ops array
        // Handles 1-level nesting (batch sub_ops parsed separately)
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
                    break;  // end of ops array
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

        // batch: recursively parse sub_ops
        if (op.op_type == "batch")
        {
            int subStart = obj.IndexOf("\"sub_ops\"");
            if (subStart >= 0)
                op.sub_ops = ParseOps(obj.Substring(subStart, obj.Length() - subStart));
        }
        return op;
    }

    // Extract the string value of a JSON field (handles both string and number values)
    protected string ExtractStringField(string json, string fieldName)
    {
        string needle = "\"" + fieldName + "\"";
        int pos = json.IndexOf(needle);
        if (pos < 0) return "";

        string searchArea1 = json.Substring(pos + needle.Length(), json.Length() - pos - needle.Length());
        int relIdx1 = searchArea1.IndexOf(":");
        int colon;
        if (relIdx1 >= 0)
            colon = pos + needle.Length() + relIdx1;
        else
            colon = -1;
        if (colon < 0) return "";

        // Skip whitespace
        int valStart = colon + 1;
        while (valStart < json.Length() && json.Get(valStart) == " ")
            valStart++;

        if (valStart >= json.Length()) return "";

        // String value (quoted)
        if (json.Get(valStart) == "\"")
        {
            string searchArea2 = json.Substring(valStart + 1, json.Length() - valStart - 1);
            int relIdx2 = searchArea2.IndexOf("\"");
            int end;
            if (relIdx2 >= 0)
                end = valStart + 1 + relIdx2;
            else
                end = -1;
            if (end < 0) return "";
            return json.Substring(valStart + 1, end - valStart - 1);
        }

        // Number / bool — read until delimiter
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
    // Write outbox.json (consumed by elos_chat.py)

    protected void WriteOutbox(string status, int appliedCount, array<string> errors)
    {
        string outboxAbsPath;
        if (!Workbench.GetAbsolutePath(OUTBOX_PATH, outboxAbsPath, false))
            return;

        string errArr = "";
        if (errors && errors.Count() > 0)
        {
            foreach (int i, string e : errors)
            {
                if (i > 0) errArr += ",";
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
    // File utilities

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
    string op_type;    // attribute_edit | entity_create | entity_delete | entity_move | batch
    string target;     // entity name or class-search term
    string field;      // attribute_edit: variable name
    string value;      // attribute_edit: new value (as string)
    string class_name; // entity_create: Enforce class
    string name;       // entity_create: display name
    string coords;     // entity_create/move: "x y z"
    int    layer_id;   // entity_create: sub-scene layer
    ref array<ref SCR_KVPair> props = {};   // entity_create: extra key=value props
    ref array<ref SCR_AIOp>   sub_ops = {}; // batch: nested ops
}

class SCR_KVPair
{
    string key;
    string value;
}

#endif // WORKBENCH
