"""
Windows host adapter for Anthropic Computer Use.

Implements screenshot + click + type + key + scroll + wait actions
against the local Windows desktop via pyautogui + mss.

PRE-FLIGHT (PC sprint will install these):
  pip install --user anthropic pyautogui mss pygetwindow pillow

USAGE (called from run_task.py loop):
  from windows_computer import execute_action
  result = execute_action("screenshot", {})
  result = execute_action("left_click", {"coordinate": [500, 300]})
  result = execute_action("type", {"text": "hello"})
  result = execute_action("key", {"text": "ctrl+shift+r"})

Per research/12-computer-use-windows-host.md — this is the ~200 LOC host
adapter Anthropic's docs say users must build for Windows (their Linux Docker
demo doesn't work natively on Windows).
"""

import base64
import io
import time
from pathlib import Path

import mss
import pyautogui
from PIL import Image

try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

# ---------------------------------------------------------------------------
# Safety: pyautogui will move mouse to corner on Ctrl+C; we don't want that
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1  # 100ms between actions for stability

# Default screenshot resolution per Anthropic guidance (1024x768 to 1280x800)
SCREENSHOT_W = 1280
SCREENSHOT_H = 800


def take_screenshot(target_path: Path | None = None) -> dict:
    """Capture primary monitor, resize to 1280x800 (Anthropic vision-tool limit),
    return base64-encoded PNG.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

    # Resize for vision API (high-bicubic)
    if img.width != SCREENSHOT_W or img.height != SCREENSHOT_H:
        img = img.resize((SCREENSHOT_W, SCREENSHOT_H), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    png_bytes = buf.getvalue()

    if target_path:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(png_bytes)

    b64 = base64.b64encode(png_bytes).decode("ascii")
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/png", "data": b64},
    }


def left_click(coordinate: list[int]) -> dict:
    """Click left mouse button at coordinate [x, y]."""
    x, y = coordinate
    # Coordinates are in 1280x800 space — scale to native
    real_w, real_h = pyautogui.size()
    real_x = int(x * real_w / SCREENSHOT_W)
    real_y = int(y * real_h / SCREENSHOT_H)
    pyautogui.click(real_x, real_y)
    return {"type": "text", "text": f"clicked ({real_x},{real_y})"}


def right_click(coordinate: list[int]) -> dict:
    x, y = coordinate
    real_w, real_h = pyautogui.size()
    real_x = int(x * real_w / SCREENSHOT_W)
    real_y = int(y * real_h / SCREENSHOT_H)
    pyautogui.rightClick(real_x, real_y)
    return {"type": "text", "text": f"right-clicked ({real_x},{real_y})"}


def double_click(coordinate: list[int]) -> dict:
    x, y = coordinate
    real_w, real_h = pyautogui.size()
    real_x = int(x * real_w / SCREENSHOT_W)
    real_y = int(y * real_h / SCREENSHOT_H)
    pyautogui.doubleClick(real_x, real_y)
    return {"type": "text", "text": f"double-clicked ({real_x},{real_y})"}


def type_text(text: str) -> dict:
    """Type a string with small interval to avoid race-conditions."""
    pyautogui.typewrite(text, interval=0.02)
    return {"type": "text", "text": f"typed: {text!r}"}


def key(combo: str) -> dict:
    """Press a key combination like 'ctrl+shift+r' or 'enter'."""
    parts = combo.lower().split("+")
    # Map common synonyms
    parts = [{"return": "enter", "esc": "escape"}.get(p, p) for p in parts]
    pyautogui.hotkey(*parts)
    return {"type": "text", "text": f"pressed: {combo}"}


def scroll(coordinate: list[int], direction: str, amount: int = 5) -> dict:
    """Scroll up/down N clicks at coordinate."""
    x, y = coordinate
    real_w, real_h = pyautogui.size()
    real_x = int(x * real_w / SCREENSHOT_W)
    real_y = int(y * real_h / SCREENSHOT_H)
    pyautogui.moveTo(real_x, real_y)
    clicks = -amount if direction == "down" else amount
    pyautogui.scroll(clicks)
    return {"type": "text", "text": f"scrolled {direction} {amount} at ({real_x},{real_y})"}


def wait(seconds: float) -> dict:
    time.sleep(min(seconds, 30.0))
    return {"type": "text", "text": f"waited {seconds}s"}


def cursor_position() -> dict:
    x, y = pyautogui.position()
    # Return in 1280x800 space
    real_w, real_h = pyautogui.size()
    return {
        "type": "text",
        "text": f"cursor at ({int(x * SCREENSHOT_W / real_w)},{int(y * SCREENSHOT_H / real_h)})",
    }


def list_windows() -> dict:
    """Return list of visible window titles."""
    if not HAS_PYGETWINDOW:
        return {"type": "text", "text": "pygetwindow not installed"}
    titles = [t for t in gw.getAllTitles() if t.strip()]
    return {"type": "text", "text": "\n".join(titles)}


def activate_window(title_substring: str) -> dict:
    """Bring window matching title to foreground."""
    if not HAS_PYGETWINDOW:
        return {"type": "text", "text": "pygetwindow not installed"}
    matches = [w for w in gw.getAllWindows() if title_substring.lower() in w.title.lower()]
    if not matches:
        return {"type": "text", "text": f"no window matching {title_substring!r}"}
    win = matches[0]
    try:
        win.activate()
        time.sleep(0.3)
        return {"type": "text", "text": f"activated: {win.title}"}
    except Exception as e:
        return {"type": "text", "text": f"activate failed: {e}"}


# ---------------------------------------------------------------------------
# Anthropic Computer Use tool dispatch — call from run_task.py sampling loop


def execute_action(action: str, params: dict) -> dict:
    """Dispatch an Anthropic Computer Use tool action to the underlying Windows
    primitive. Returns the tool_result content dict.
    """
    if action == "screenshot":
        return take_screenshot()
    if action == "left_click":
        return left_click(params["coordinate"])
    if action == "right_click":
        return right_click(params["coordinate"])
    if action == "double_click":
        return double_click(params["coordinate"])
    if action == "type":
        return type_text(params["text"])
    if action == "key":
        return key(params["text"])
    if action == "scroll":
        return scroll(
            params["coordinate"],
            params.get("direction", "down"),
            params.get("amount", 5),
        )
    if action == "wait":
        return wait(params.get("duration", 1))
    if action == "cursor_position":
        return cursor_position()
    if action == "list_windows":
        return list_windows()
    if action == "activate_window":
        return activate_window(params["text"])
    return {"type": "text", "text": f"unknown action: {action}"}


if __name__ == "__main__":
    # Smoke test
    print("=== windows_computer.py smoke test ===")
    out = Path(__file__).parent / "smoke-screenshot.png"
    res = take_screenshot(target_path=out)
    print(f"Screenshot saved to {out}")
    print(f"Base64 length: {len(res['source']['data'])}")
    print(f"Native res: {pyautogui.size()}")
    print(f"Target res: {SCREENSHOT_W}x{SCREENSHOT_H}")
    if HAS_PYGETWINDOW:
        titles = [t for t in gw.getAllTitles() if t.strip()][:5]
        print(f"Top 5 visible windows: {titles}")
