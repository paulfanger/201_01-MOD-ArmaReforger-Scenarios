# Chat Panel Architecture — FINAL Decision

> Stand: 2026-05-21
> Source: research agent a1290d64 (Enforce Script UI + Blender-MCP reality check)
> **Verdict: Option B (plugin spawns floating chat window). Mirrors Blender-MCP exactly.**

---

## 🎯 The Reality Check

**Blender-MCP DOESN'T have chat inside Blender.** Verified:
- Blender N-panel "BlenderMCP" tab → only a "Connect" button + Poly-Haven checkbox
- Chat happens in Claude Desktop or Cursor (EXTERNAL)
- Blender acts as MCP server (socket on localhost) — drives editor from outside

Same pattern in:
- Unity-MCP variants
- Unreal-MCP variants
- All shipping LLM-in-editor projects

**There is NO production reference for "LLM chat literally rendered inside 3D editor".**
Our perceived target was actually a misunderstanding of how Blender-MCP works.

---

## ✅ Option B = Mirrors Blender-MCP Architecture

| Blender-MCP | ELOS-Reforger (Option B) |
|---|---|
| Blender addon = TCP socket server | Reforger plugin = file-watch + RunProcess |
| User chats in Claude Desktop (external window) | User chats in floating Tk/PyWebView window (external) |
| Blender renders changes in 3D viewport | Reforger renders changes in Workbench viewport |
| Chat-to-render latency: 1-3 sec | Chat-to-render latency: 1-2 sec (target) |
| "Feels integrated" because side-by-side | "Feels integrated" because side-by-side |

**Visually identical UX.** Architecturally: editor = renderer, chat = external client.

---

## Architecture (Option B detail)

```
┌─────────────────────┐         ┌──────────────────────────┐
│  Chat Window        │         │  Reforger Workbench      │
│  (Tk/PyWebView)     │ <──────>│  + AI_GeneratePlugin     │
│  500x800px floating │  files  │  + WorldEditorAPI        │
│  Claude API client  │         │  + 3D Viewport           │
└─────────────────────┘         └──────────────────────────┘
        ↑                                    ↑
        │  user types                        │  viewport updates
        │  "fog dichter"                     │  ↑
        │                                    │  fog density now 0.7
        └────────────────────────────────────┘
                 file-drop bridge
        $profile:ELOS/inbox-<ts>.json    →    spec.json applied
        $profile:ELOS/outbox-<ts>.json   ←    plugin response
```

### Flow

1. User types in chat window: "fog dichter"
2. Chat window's Python helper writes `$profile:ELOS/inbox-<ts>.json` with prompt
3. Python helper calls Claude API (Sonnet 4.6) with mission context → gets JSON-Patch
4. Python helper writes `$profile:ELOS/spec.json` with the patch
5. AHK / chokidar detects spec.json change → fires Ctrl+Shift+R into Workbench
6. Workbench reloads scripts → AI_GeneratePlugin.Run() executes
7. Plugin reads spec.json → calls WorldEditorAPI to apply ops (e.g. SetVariableValue fog_density 0.7)
8. Viewport refreshes — fog visibly denser
9. Plugin writes `$profile:ELOS/outbox-<ts>.json` with "OK" + summary
10. Python helper reads outbox → appends to chat window history

**Total cycle: ~1-2 sec.** Matches Blender-MCP latency.

---

## Code Sketch — Chat Window (Python ~150 LOC)

```python
# scripts/chat-window/elos_chat.py
import tkinter as tk
from tkinter import scrolledtext
import json, time, threading, os
from pathlib import Path
from anthropic import Anthropic

INBOX = Path(os.path.expandvars(r"%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\profile\ELOS\inbox.json"))
OUTBOX_DIR = INBOX.parent
SPEC = OUTBOX_DIR / "spec.json"
client = Anthropic()

class ELOSChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ELOS · Live Mission Editor")
        self.geometry("500x800+1420+50")  # right side of typical 1920 screen
        self.configure(bg="#0d1018")

        # History (scrollable)
        self.history = scrolledtext.ScrolledText(self, bg="#16192a", fg="#fafaf0",
            insertbackground="#ff7a3d", font=("Inter", 10), wrap=tk.WORD)
        self.history.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Input
        self.input = tk.Text(self, height=3, bg="#1f2438", fg="#fafaf0",
            insertbackground="#ff7a3d", font=("Inter", 11))
        self.input.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.input.bind("<Return>", self.on_send)

    def on_send(self, event=None):
        prompt = self.input.get("1.0", tk.END).strip()
        if not prompt:
            return "break"
        self.input.delete("1.0", tk.END)
        self._add_msg("user", prompt)
        threading.Thread(target=self._process, args=(prompt,), daemon=True).start()
        return "break"

    def _process(self, prompt):
        # 1. Call Claude API with mission context + prompt
        # 2. Parse JSON-Patch response
        # 3. Write spec.json (triggers plugin via file-watch + AHK)
        # 4. Wait for outbox response
        # 5. Display result in history
        # ...implementation...

    def _add_msg(self, role, text):
        self.history.insert(tk.END, f"\n[{role}] {text}\n")
        self.history.see(tk.END)

if __name__ == "__main__":
    ELOSChat().mainloop()
```

---

## Plugin Skeleton (Enforce Script ~80 LOC)

Already mostly done in `workbench-plugin/AI_GeneratePlugin.c` (per MEGA-A). Adds:

```c
[WorkbenchPluginAttribute(
  name: "ELOS · Load Spec",
  category: "ELOS",
  shortcut: "Ctrl+Shift+R",
  wbModules: {"WorldEditor"}
)]
class ELOS_LoadSpecPlugin : WorldEditorPlugin {
  override void Run() {
    string spec = "$profile:ELOS/spec.json";
    if (!FileIO.FileExists(spec)) return;

    // Read + parse JSON
    string content = ReadFile(spec);
    SCR_AISpec aiSpec = new SCR_AISpec();
    JsonSerializer.Deserialize(aiSpec, content);

    // Apply ops via WorldEditorAPI
    foreach (SCR_AIOp op : aiSpec.ops) {
      ApplyOp(op);
    }

    // Write response
    WriteFile("$profile:ELOS/outbox.json", "{\"status\":\"OK\",\"count\":" + aiSpec.ops.Count() + "}");
  }
  // ... ApplyOp, ReadFile, WriteFile helpers ...
}
```

---

## Why This Is BETTER Than In-Workbench Modal Dialog

| Aspect | Option A (modal in Workbench) | Option B (floating window) |
|---|---|---|
| UX feel | "ChatGPT 2022 settings dialog" | "Cursor Composer side-panel" |
| Streaming | Impossible (Enforce no async UI) | Native (Python threads) |
| Multi-line response | Cramped | Comfortable |
| Persistent history | Limited to dialog lifetime | Full session |
| Future features | Limited | Wide open (voice input, image attach, etc.) |
| Looks like Workbench? | Yes | No (separate window) |
| Looks like Cursor/Blender-MCP? | No | **Yes** |

User's actual desire: "live in-editor LLM integration." Option B delivers that BETTER than Option A, with the same plugin backend doing the actual mission changes.

---

## Recommendation: Phase Plan

| Phase | Target | Effort | Cumulative |
|---|---|---|---|
| **MVP (Sprint PIVOT)** | Plugin TODOs filled + bridge.py + Tk chat window basic | 3-4 days | 3-4 d |
| **Phase 5.1 polish** | PyWebView replaces Tk (HTML/CSS-styled chat) | +1 day | 4-5 d |
| **Phase 6 streaming** | Server-Sent Events from Claude API for live token streaming | +1 day | 5-6 d |
| **Phase 7 voice** | Whisper STT integration | +2 days | 7-8 d |

---

## Decision: Update Sprint PIVOT

The PIVOT sprint (`sprint-PIVOT-computer-use-direct-to-S5.md`) needs ONE adjustment:

**Stage P.5 — First End-to-End Live Edit Test** should produce:
- The Tk chat window (basic, ~150 LOC Python)
- Bridge.py that calls Claude API
- AI_GeneratePlugin.c with TODOs filled (already 80% done from MEGA-A)
- File-watch wiring (already scaffolded)

End state: floating chat window on right side of screen, type "fog dichter", see fog
denser in Workbench viewport within ~2 seconds. **THAT is S5 MVP.**

---

## Sources

- Research agent a1290d64 (in-Workbench chat panel feasibility)
- [Bohemia Samples — WorkbenchPlugin Tutorial](https://community.bistudio.com/wiki/Arma_Reforger:Workbench_Plugin_Tutorial)
- [SampleResourceManagerPlugin.c](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/main/SampleMod_WorkbenchPlugin/Scripts/WorkbenchGame/SamplePlugins/SampleResourceManagerPlugin.c)
- [DiscordRP file-watch reference](https://github.com/NarcoMarshDev/Enforce-Script-Extensions/blob/master/scripts/WorkbenchGame/DiscordRP/DiscordRP.c)
- [Blender-MCP](https://github.com/ahujasid/blender-mcp) — confirmed external-chat architecture
- [UIWidgets Reference](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceUIWidgets.html)
