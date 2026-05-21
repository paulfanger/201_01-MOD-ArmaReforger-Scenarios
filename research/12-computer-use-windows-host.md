# Computer Use on Windows — The Real Path to Autonomy

> Stand: 2026-05-21
> Source: Research Agent abdd16f9 (Anthropic Computer Use + Windows)
> Purpose: kill the "user manually clicks Steam EULA at 02:00" problem permanently

---

## ✅ Anthropic Computer Use IS Available

- **GA-Beta**, models: `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-opus-4-5`
- Tool type: `computer_20251124` (with zoom action)
- Beta header: `anthropic-beta: computer-use-2025-11-24`
- **Sonnet 4.6 is more click-precise than Opus 4.6**, Opus 4.7 matches at higher resolution
- **Cost: standard pricing** + ~1100-1600 tokens per screenshot (1024×768)
- Docs: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
- Reference: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo (Linux Docker)

## ⚠️ Windows Native: NOT supported by Anthropic

Anthropic's reference implementation = Linux X11 + Xvfb + Mutter in Docker.
On Windows: **roll your own host adapter** (~200 LOC Python).

The API is **host-agnostic** — we provide the tools, it makes the decisions.

---

## What Steam + Reforger + Workbench Look Like to Automation

| Surface | UI Accessibility Tree? | Pixel-based works? |
|---|---|---|
| Steam UI (CEF/custom paint) | ❌ opaque to UIA | ✅ |
| Arma Reforger Game (DirectX) | ❌ opaque | ✅ |
| Workbench (custom in-engine) | ❌ empty UIA tree | ✅ |
| Notepad / Win32 native | ✅ accessible | ✅ |

**Verdict: Pixel + Coordinate control is the only path.** PyAutoGUI driven by Claude vision.

---

## Realistic Path: Hybrid AHK + Computer Use

| Layer | Tool | Use For |
|---|---|---|
| **L1 Known hotkeys** | AutoHotkey v2 | `Ctrl+Shift+R` Workbench reload, `Alt+F4`, window-switching |
| **L2 Steam UI / EULA dialogs** | Custom Computer Use loop (PyAutoGUI + mss + Claude vision) | "Click Install in Steam library", "Accept EULA", "Wait for download" |
| **L3 Game UI navigation** | Custom Computer Use loop | "Open scenarios menu", "Click night-recon" |
| **L4 Workbench plugin loading** | AHK hotkey + file-drop bridge | Claude writes spec.json → AHK presses Ctrl+Shift+R → plugin applies |

---

## Hard Limits (Accept These)

These **cannot** be automated, even with Computer Use:
- **Steam 2FA mobile approval** — needs your phone
- **UAC prompts** — secure desktop, NO automation
- **Windows Defender SmartScreen** — same
- **Captchas** — same

**Mitigation:** pre-login Steam once manually, disable 2FA OR mark machine as trusted, accept UAC during PSA (the audit we already designed catches this).

---

## 30-Minute Recipe to Get Started

```powershell
# Install deps
winget install Python.Python.3.12 Git.Git AutoHotkey.AutoHotkey
python -m pip install anthropic pyautogui mss pygetwindow pillow

# Set API key (one-time per session OR persistent via system env)
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

Then ~200 LOC `windows_computer.py`:

```python
import mss, pyautogui, base64, io
from PIL import Image
from anthropic import Anthropic

client = Anthropic()

def take_screenshot():
    with mss.mss() as s:
        img = Image.frombytes("RGB",
            (s.monitors[1]["width"], s.monitors[1]["height"]),
            s.grab(s.monitors[1]).rgb)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()

def execute_tool(tool_name, tool_input):
    if tool_name == "computer":
        action = tool_input["action"]
        if action == "screenshot":
            return {"type": "image", "source": {"type": "base64",
                    "media_type": "image/png", "data": take_screenshot()}}
        elif action == "left_click":
            pyautogui.click(*tool_input["coordinate"])
            return {"type": "text", "text": "clicked"}
        elif action == "type":
            pyautogui.typewrite(tool_input["text"], interval=0.02)
            return {"type": "text", "text": "typed"}
        elif action == "key":
            pyautogui.hotkey(*tool_input["text"].split("+"))
            return {"type": "text", "text": "pressed"}
        # ... etc for scroll, drag, wait, zoom

# Sampling loop per Anthropic quickstart
def run_task(task_description):
    messages = [{"role": "user", "content": task_description}]
    while True:
        response = client.beta.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=[{"type": "computer_20251124", "name": "computer",
                    "display_width_px": 1920, "display_height_px": 1080}],
            messages=messages,
            betas=["computer-use-2025-11-24"]
        )
        # Parse tool_use, execute, append tool_result, repeat
        # Until response.stop_reason == "end_turn"
```

---

## What This Unlocks

### Immediate (the failed-overnight problem):
- "Install Arma Reforger Server (AppID 1874900) via Steam Library"
- "Accept EULA dialogs"
- "Wait for download, then verify executable exists"

### Mid-term (S2 autonomous):
- "Launch Workbench with mission X"
- "Click 'Reload Scripts'"
- "Verify mission entities visible in viewport"

### Long-term (Phase 4+ live editor):
- File-drop bridge: spec.json → file-watch → AHK Ctrl+Shift+R → plugin applies
- Computer Use does the BOOTSTRAP, plugin does the LIVE-EDIT
- ~1-2 sec latency achievable

---

## Mirror of Blender-MCP for Reforger

User's reference: [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)

**Blender-MCP architecture:** Blender addon = TCP socket server on `localhost:9876` ↔ MCP server (`uvx blender-mcp`) ↔ Claude tool calls → addon executes via `bpy` (Blender Python API).

**Reforger reality:** Enforce Script has **NO HTTP/socket primitives**, only file I/O + CLI `-plugin=`.

**Realistic mirror = file-drop bridge:**
1. MCP server (or just Claude Code) writes JSON spec to watched folder
2. Workbench plugin (Enforce Script) polls/loads on `Ctrl+Shift+R`
3. Plugin reads spec → applies WorldEditorAPI ops → viewport repaints

This is **already 80% built** (we have AI_GeneratePlugin.c refactored with real API + file-watcher scaffold).

**What's left:**
- Fill the 2 TODOs in AI_GeneratePlugin.c (JSON parse + ops loop)
- Wire chokidar/PowerShell-watcher → AHK Ctrl+Shift+R
- Verify plugin compiles + loads

---

## New Approach Summary

**Forget the "fully autonomous overnight" fantasy without Computer Use.**

Instead: **3 layers, hybrid**:

1. **Bootstrap (Computer Use):** install missing tools (Server EXE), accept EULAs, configure Steam
2. **Build (Sonnet + sub-agents):** plugin implementation, golden tests, validate-loop (already mostly done)
3. **Live-Edit (plugin + file-drop):** Claude writes spec, plugin applies in <2s

All three are achievable today. We have everything we need.

---

## Cost Math (per task)

- Computer Use Steam install task: ~30-80 screenshots = ~50-100k tokens = $1-3 per install
- Plugin build (Sonnet): ~$5-15 per sprint
- Live-edit per prompt (Sonnet vision + plugin): ~$0.05-0.20 per revision

Compared to pure manual: **invaluable time savings** (you don't lose nights).

---

## Sources

- [Computer Use Tool Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [anthropic-quickstarts/computer-use-demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
- [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)
- [mss](https://github.com/BoboTiG/python-mss)
- [pygetwindow](https://github.com/asweigart/PyGetWindow)
- [AutoHotkey v2](https://www.autohotkey.com/)
