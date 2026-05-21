"""
ELOS Live Mission Editor — floating chat window for Arma Reforger Workbench.

Mirror of Blender-MCP's external-chat architecture:
- Floating window on right side of screen
- User types prompt → window writes spec.json + posts to Claude
- Plugin in Workbench picks up spec.json + applies changes to 3D viewport
- Plugin writes outbox.json → window reads + appends to history

PRE-FLIGHT:
  pip install --user anthropic pillow
  $env:ANTHROPIC_API_KEY = "sk-ant-..."

USAGE:
  python elos_chat.py
  (window opens, ready for prompts)
"""

import json
import os
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import font as tkfont
from tkinter import scrolledtext

from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Paths (Workbench profile location, per CHEATSHEET-PC §File-paths)
USER_PROFILE = Path(os.environ["USERPROFILE"])
PROFILE_DIR = USER_PROFILE / "Documents" / "my games" / "ArmaReforgerWorkbench" / "profile"
ELOS_DIR = PROFILE_DIR / "ELOS"
ELOS_DIR.mkdir(parents=True, exist_ok=True)
INBOX = ELOS_DIR / "inbox.json"
SPEC = ELOS_DIR / "spec.json"
OUTBOX = ELOS_DIR / "outbox.json"

# Repo path for narrative-context
REPO = Path(r"C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios")
DEFAULT_MISSION = "night-recon-everon"

client = Anthropic()

# ---------------------------------------------------------------------------
# Colors (matching the S5 visual treatment)
COLORS = {
    "bg_deep":    "#05060c",
    "bg_mid":     "#0d1018",
    "bg_card":    "#16192a",
    "line":       "#25304a",
    "accent":     "#ff7a3d",
    "green":      "#6dd49e",
    "text_bright":"#fafaf0",
    "text_mid":   "#aaada0",
    "text_dim":   "#545862",
}


def load_mission_context(mission_id: str) -> str:
    """Load narrative.json + asset-manifest.json for the active mission."""
    narrative_path = REPO / "missions" / mission_id / "narrative.json"
    manifest_path = REPO / "missions" / mission_id / "asset-manifest.json"
    parts = []
    if narrative_path.exists():
        parts.append(f"# narrative.json\n{narrative_path.read_text(encoding='utf-8')}")
    if manifest_path.exists():
        parts.append(f"# asset-manifest.json\n{manifest_path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def build_system_prompt(mission_id: str) -> str:
    """System prompt for the LLM — translates user revision prompts into
    JSON-Patch operations (RFC 6902) against narrative.json + WorldEditorAPI ops.
    """
    return f"""You are ELOS — a live mission editor assistant for Arma Reforger.

User types natural-language revision prompts in German or English. You translate
them into a JSON-Patch document that updates the active mission's narrative.json
AND produces a WorldEditorAPI ops list for the live viewport refresh.

ACTIVE MISSION: {mission_id}
SCHEMA: see playbook/SCHEMA_MAPPING.md in repo (loaded as context if available).

OUTPUT FORMAT (mandatory JSON):
{{
  "summary": "1-sentence what you're doing",
  "narrative_patch": [
    {{"op": "replace", "path": "/weather/fog_density", "value": 0.7}}
  ],
  "world_editor_ops": [
    {{"op": "attribute_edit", "target": "weatherManager", "field": "m_fFogDensity", "value": 0.7}}
  ],
  "confidence": 0.95
}}

If confidence < 0.7 OR the prompt is ambiguous: ask ONE clarifying question
instead of acting, formatted as {{"clarification_needed": "your question"}}.

Keep responses tight. Match user's language (German if prompt is German)."""


def call_claude(prompt: str, mission_id: str, history: list[dict]) -> dict:
    """Make API call. Returns parsed response dict."""
    context = load_mission_context(mission_id)
    system = build_system_prompt(mission_id) + "\n\n# Mission Context\n" + context

    messages = list(history) + [{"role": "user", "content": prompt}]

    # Stable prefix (mission context) caching — 90% input-cost reduction on hits
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=[
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}},
        ],
        messages=messages,
    )

    text = "".join(c.text for c in response.content if c.type == "text")

    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "model returned non-JSON", "raw": text}


# ---------------------------------------------------------------------------
class ELOSChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ELOS · Live Mission Editor")
        # Right side of typical 1920 screen
        self.geometry("520x820+1380+50")
        self.configure(bg=COLORS["bg_deep"])
        self.minsize(420, 600)

        self.history = []  # conversation memory
        self.mission_id = DEFAULT_MISSION

        self._build_ui()
        self._add_system_message(
            f"ELOS connected. Active mission: {self.mission_id}\n"
            "Type a revision prompt below. Press Enter to send.\n"
            "Examples: 'fog dichter', 'phase 3 auf 5 min kürzen', 'add MG-team south'"
        )

    def _build_ui(self):
        # Title bar
        title_bar = tk.Frame(self, bg=COLORS["bg_card"], height=44)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        title_bar.pack_propagate(False)

        title_dot = tk.Label(
            title_bar, text="●", fg=COLORS["accent"], bg=COLORS["bg_card"],
            font=("Segoe UI", 14),
        )
        title_dot.pack(side=tk.LEFT, padx=(14, 6))

        title_label = tk.Label(
            title_bar,
            text="ELOS · LIVE EDITOR",
            fg=COLORS["text_bright"],
            bg=COLORS["bg_card"],
            font=("Consolas", 9),
        )
        title_label.pack(side=tk.LEFT)

        mission_label = tk.Label(
            title_bar,
            text=f"mission: {self.mission_id}",
            fg=COLORS["text_dim"],
            bg=COLORS["bg_card"],
            font=("Consolas", 8),
        )
        mission_label.pack(side=tk.RIGHT, padx=14)

        # History (scrollable)
        self.history_box = scrolledtext.ScrolledText(
            self,
            bg=COLORS["bg_deep"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["accent"],
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=14,
            pady=14,
            state=tk.DISABLED,
        )
        self.history_box.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Configure text tags
        self.history_box.tag_configure("user", foreground=COLORS["text_bright"], font=("Segoe UI", 10, "bold"))
        self.history_box.tag_configure("ai", foreground=COLORS["accent"])
        self.history_box.tag_configure("applied", foreground=COLORS["green"], font=("Consolas", 9))
        self.history_box.tag_configure("system", foreground=COLORS["text_dim"], font=("Consolas", 9))
        self.history_box.tag_configure("error", foreground="#e07171")

        # Input
        input_frame = tk.Frame(self, bg=COLORS["bg_card"], height=70)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        input_frame.pack_propagate(False)

        arrow = tk.Label(
            input_frame, text="✦", fg=COLORS["accent"], bg=COLORS["bg_card"],
            font=("Segoe UI", 14),
        )
        arrow.pack(side=tk.LEFT, padx=(14, 8), pady=(0, 4))

        self.input_box = tk.Text(
            input_frame,
            height=2,
            bg=COLORS["bg_deep"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["accent"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=10,
            pady=8,
        )
        self.input_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 14), pady=12)
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)
        self.input_box.focus_set()

    # ---- chat operations ---------------------------------------------------
    def _on_enter(self, event):
        # Shift+Enter = newline (default behavior), plain Enter = send
        if event.state & 0x0001:  # shift held
            return None
        prompt = self.input_box.get("1.0", tk.END).strip()
        if not prompt:
            return "break"
        self.input_box.delete("1.0", tk.END)
        self._add_user_message(prompt)
        threading.Thread(target=self._process_prompt, args=(prompt,), daemon=True).start()
        return "break"

    def _process_prompt(self, prompt: str):
        try:
            self._add_system_message(f"thinking...")
            result = call_claude(prompt, self.mission_id, self.history)
        except Exception as e:
            self._add_message("error", f"API error: {e}")
            return

        if "error" in result:
            self._add_message("error", f"{result['error']}\n\nraw: {result.get('raw','')[:300]}")
            return
        if "clarification_needed" in result:
            self._add_ai_message(f"? {result['clarification_needed']}")
            return

        # Show summary
        summary = result.get("summary", "(no summary)")
        self._add_ai_message(summary)

        # Write spec.json (triggers plugin via AHK file-watch)
        spec_payload = {
            "mission_id": self.mission_id,
            "version": datetime.now().isoformat(),
            "ops": result.get("world_editor_ops", []),
            "narrative_patch": result.get("narrative_patch", []),
        }
        SPEC.write_text(json.dumps(spec_payload, indent=2), encoding="utf-8")

        # Show applied summary
        ops_count = len(spec_payload["ops"])
        self._add_applied(
            f"✓ {ops_count} ops written to spec.json\n"
            f"  waiting for plugin response..."
        )

        # Poll outbox.json for plugin response (max 10 sec)
        wait_start = time.time()
        plugin_response = None
        while time.time() - wait_start < 10:
            if OUTBOX.exists():
                try:
                    plugin_response = json.loads(OUTBOX.read_text(encoding="utf-8"))
                    # Consume + delete so next iteration starts clean
                    OUTBOX.unlink()
                    break
                except json.JSONDecodeError:
                    pass
            time.sleep(0.2)

        if plugin_response:
            latency = time.time() - wait_start
            status = plugin_response.get("status", "?")
            applied = plugin_response.get("applied_count", 0)
            errors = plugin_response.get("errors", [])
            self._add_applied(
                f"✓ Plugin: {status} · {applied} ops applied · {latency:.2f}s end-to-end"
            )
            if errors:
                self._add_message("error", "Errors:\n" + "\n".join(f"  - {e}" for e in errors))
        else:
            self._add_message("error", "(no plugin response in 10s — check Workbench + file-watcher)")

        # Append to history (for next turn context)
        self.history.append({"role": "user", "content": prompt})
        self.history.append(
            {"role": "assistant", "content": json.dumps(result, ensure_ascii=False)}
        )
        # Keep history bounded
        if len(self.history) > 20:
            self.history = self.history[-20:]

    # ---- message rendering -------------------------------------------------
    def _add_user_message(self, text: str):
        self._add_message("user", text)

    def _add_ai_message(self, text: str):
        self._add_message("ai", text)

    def _add_applied(self, text: str):
        self._add_message("applied", text)

    def _add_system_message(self, text: str):
        self._add_message("system", text)

    def _add_message(self, tag: str, text: str):
        self.history_box.configure(state=tk.NORMAL)
        prefix = {
            "user": "\nYou\n",
            "ai": "\n✦ ELOS\n",
            "applied": "\n",
            "system": "\n",
            "error": "\n⚠ error\n",
        }.get(tag, "\n")
        self.history_box.insert(tk.END, prefix, tag)
        self.history_box.insert(tk.END, text + "\n", tag)
        self.history_box.see(tk.END)
        self.history_box.configure(state=tk.DISABLED)


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        return 2
    app = ELOSChat()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
