"""
Anthropic Computer Use loop runner — Windows version.

USAGE:
  python run_task.py "Open Notepad, type 'hello ELOS', close without saving"
  python run_task.py --task-file mytask.txt
  python run_task.py --model claude-opus-4-7 "Complex visual task"

PRE-FLIGHT:
  $env:ANTHROPIC_API_KEY = "sk-ant-..."
  pip install --user anthropic pyautogui mss pygetwindow pillow

Per research/12 — uses beta header 'computer-use-2025-11-24' + tool type
'computer_20251124'. Default model claude-sonnet-4-6 (more click-precise than
opus-4-6 per Anthropic).

M.2 FORENSIC LOGGING (added PHASE META):
  Each session gets its own subdirectory: logs/computer-use/cu-<ts>-session/
    - screenshot-<turn>.png  (before each action)
    - transcript.jsonl       ({turn, screenshot_path, action, decision_reasoning})
    - summary.md             (first 5 + last 5 turns + outcome)
  Goal: any CU session is replay-able for debugging.
"""

import argparse
import io
import json
import os
import sys
import time

# Force UTF-8 stdout so emoji in Claude responses don't crash on Windows CP1252 console
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

# Add scripts/computer-use to path
sys.path.insert(0, str(Path(__file__).parent))
from windows_computer import execute_action, take_screenshot, SCREENSHOT_W, SCREENSHOT_H, NonWhitelistedWindowError

BETA_HEADER = "computer-use-2025-11-24"
TOOL_TYPE = "computer_20251124"
DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TURNS = 80
MAX_TOKENS = 1024  # Tight loop: 1024 for snappy turns (was 4096)
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "computer-use"

# System prompt for tight-loop CU: act → screenshot → assess → act
CU_SYSTEM_PROMPT = (
    "You are a Computer Use agent controlling a Windows desktop. "
    "RULES FOR SPEED:\n"
    "1. Take a screenshot after EVERY single action — no exceptions.\n"
    "2. Never batch multiple clicks before taking a screenshot.\n"
    "3. Act → screenshot → assess → act. Tight loop.\n"
    "4. Keep text responses SHORT (1-2 sentences max). Save tokens.\n"
    "5. If an action worked: confirm in 1 sentence, then take next action.\n"
    "6. If an action failed: state what failed in 1 sentence, try alternative immediately.\n"
    "Do NOT write long explanations. Speed > verbosity."
)


def run_task(task: str, model: str = DEFAULT_MODEL, max_turns: int = MAX_TURNS) -> dict:
    """Execute a task autonomously using Computer Use loop. Returns final
    {turns, success, last_message, log_path, forensic_dir}.

    M.2: Each session logs to a per-session forensic directory for replay.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"cu-{ts}.jsonl"

    # M.2: Per-session forensic directory
    forensic_dir = LOG_DIR / f"cu-{ts}-session"
    forensic_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = forensic_dir / "transcript.jsonl"
    turn_log: list[dict] = []  # accumulate for summary.md

    client = Anthropic()  # uses ANTHROPIC_API_KEY env var
    messages = [{"role": "user", "content": task}]
    turns = 0
    success = False
    last_message = None

    print(f"[CU] Task: {task[:100]}...")
    print(f"[CU] Model: {model}")
    print(f"[CU] Log: {log_path}")
    print(f"[CU] Forensic: {forensic_dir}")

    with log_path.open("a") as logf, transcript_path.open("a") as trf:
        logf.write(json.dumps({"event": "start", "task": task, "model": model, "ts": ts}) + "\n")

        while turns < max_turns:
            turns += 1

            # M.2: Screenshot BEFORE every turn (what agent sees at decision time)
            screenshot_path = forensic_dir / f"screenshot-{turns:03d}.png"
            try:
                take_screenshot(target_path=screenshot_path)
            except Exception as e:
                print(f"[CU] forensic screenshot failed turn {turns}: {e}")
                screenshot_path = None

            try:
                response = client.beta.messages.create(
                    model=model,
                    max_tokens=MAX_TOKENS,
                    system=CU_SYSTEM_PROMPT,
                    tools=[
                        {
                            "type": TOOL_TYPE,
                            "name": "computer",
                            "display_width_px": SCREENSHOT_W,
                            "display_height_px": SCREENSHOT_H,
                        }
                    ],
                    messages=messages,
                    betas=[BETA_HEADER],
                )
            except Exception as e:
                print(f"[CU] API error turn {turns}: {e}")
                logf.write(json.dumps({"event": "api_error", "turn": turns, "error": str(e)}) + "\n")
                break

            # Append assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Log this turn
            text_parts = [c.text for c in response.content if c.type == "text"]
            tool_uses = [c for c in response.content if c.type == "tool_use"]
            logf.write(
                json.dumps(
                    {
                        "event": "turn",
                        "turn": turns,
                        "text": text_parts,
                        "tool_calls": [
                            {"name": tu.name, "input": tu.input} for tu in tool_uses
                        ],
                        "stop_reason": response.stop_reason,
                    }
                )
                + "\n"
            )

            # M.2: Transcript entry
            for tu in tool_uses:
                action = tu.input.get("action", "screenshot")
                trf_entry = {
                    "turn": turns,
                    "screenshot_path": str(screenshot_path) if screenshot_path else None,
                    "prompt_preview": text_parts[0][:300] if text_parts else "",
                    "tool_use": action,
                    "tool_params": {k: v for k, v in tu.input.items() if k != "action"},
                    "decision_reasoning": text_parts[0][:500] if text_parts else "",
                }
                trf.write(json.dumps(trf_entry) + "\n")
                turn_log.append(trf_entry)

            if text_parts:
                print(f"[CU] turn {turns} say: {text_parts[0][:200]}")

            # Stop?
            if response.stop_reason == "end_turn":
                success = True
                last_message = " ".join(text_parts)
                print(f"[CU] end_turn after {turns} turns")
                break

            if not tool_uses:
                # No tool calls + no end_turn = stuck
                print(f"[CU] turn {turns}: no tool calls, no end_turn — stopping")
                break

            # Execute tool calls + append tool_result
            tool_results = []
            for tu in tool_uses:
                params = tu.input
                action = params.get("action", "screenshot")
                # Computer Use tool params have action + others
                inner_params = {k: v for k, v in params.items() if k != "action"}
                print(f"[CU] turn {turns} action: {action} {inner_params}")
                try:
                    result_content = execute_action(action, inner_params)
                except NonWhitelistedWindowError as wl_err:
                    # M.3: Refuse action, log it, surface blocker
                    refusal_msg = str(wl_err)
                    print(f"[CU] WHITELIST REFUSED: {refusal_msg}")
                    logf.write(json.dumps({
                        "event": "whitelist_refusal",
                        "turn": turns,
                        "action": action,
                        "reason": refusal_msg,
                    }) + "\n")
                    result_content = {"type": "text", "text": f"REFUSED: {refusal_msg}"}
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": [result_content],
                    }
                )
                logf.write(
                    json.dumps(
                        {
                            "event": "action_exec",
                            "turn": turns,
                            "action": action,
                            "params": inner_params,
                            "result_type": result_content.get("type"),
                        }
                    )
                    + "\n"
                )

            messages.append({"role": "user", "content": tool_results})

        logf.write(
            json.dumps({"event": "end", "turns": turns, "success": success, "last": last_message})
            + "\n"
        )

    # M.2: Write session summary.md
    _write_forensic_summary(forensic_dir, task, ts, turns, success, last_message, turn_log)

    return {
        "turns": turns,
        "success": success,
        "last_message": last_message,
        "log_path": str(log_path),
        "forensic_dir": str(forensic_dir),
    }


def _write_forensic_summary(
    forensic_dir: Path,
    task: str,
    ts: str,
    turns: int,
    success: bool,
    last_message: str | None,
    turn_log: list[dict],
) -> None:
    """M.2: Write human-readable summary.md for session replay."""
    summary_path = forensic_dir / "summary.md"
    first5 = turn_log[:5]
    last5 = turn_log[-5:] if len(turn_log) > 5 else []

    lines = [
        f"# CU Session Summary — {ts}",
        f"",
        f"**Task:** {task[:200]}",
        f"**Turns:** {turns}",
        f"**Outcome:** {'SUCCESS' if success else 'FAILED'}",
        f"**Last message:** {(last_message or '')[:300]}",
        f"",
        f"## First 5 turns",
        f"",
    ]
    for t in first5:
        lines.append(f"### Turn {t['turn']} — `{t['tool_use']}`")
        lines.append(f"- Screenshot: `{t['screenshot_path']}`")
        lines.append(f"- Reasoning: {t['decision_reasoning'][:200]}")
        lines.append(f"")

    if last5:
        lines.append(f"## Last 5 turns")
        lines.append(f"")
        for t in last5:
            lines.append(f"### Turn {t['turn']} — `{t['tool_use']}`")
            lines.append(f"- Screenshot: `{t['screenshot_path']}`")
            lines.append(f"- Reasoning: {t['decision_reasoning'][:200]}")
            lines.append(f"")

    lines.append(f"## Replay")
    lines.append(f"Screenshots: `{forensic_dir}/*.png`")
    lines.append(f"Transcript: `{forensic_dir}/transcript.jsonl`")

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Anthropic Computer Use task runner (Windows)")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--task-file", help="Read task from file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Anthropic model")
    parser.add_argument("--max-turns", type=int, default=MAX_TURNS)
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(2)

    if args.task_file:
        task = Path(args.task_file).read_text(encoding="utf-8").strip()
    elif args.task:
        task = args.task
    else:
        print("ERROR: provide task or --task-file")
        sys.exit(2)

    result = run_task(task, model=args.model, max_turns=args.max_turns)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
