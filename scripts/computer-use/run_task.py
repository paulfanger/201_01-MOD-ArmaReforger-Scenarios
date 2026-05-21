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
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

# Add scripts/computer-use to path
sys.path.insert(0, str(Path(__file__).parent))
from windows_computer import execute_action, SCREENSHOT_W, SCREENSHOT_H

BETA_HEADER = "computer-use-2025-11-24"
TOOL_TYPE = "computer_20251124"
DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TURNS = 80
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "computer-use"


def run_task(task: str, model: str = DEFAULT_MODEL, max_turns: int = MAX_TURNS) -> dict:
    """Execute a task autonomously using Computer Use loop. Returns final
    {turns, success, last_message, log_path}.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"cu-{ts}.jsonl"

    client = Anthropic()  # uses ANTHROPIC_API_KEY env var
    messages = [{"role": "user", "content": task}]
    turns = 0
    success = False
    last_message = None

    print(f"[CU] Task: {task[:100]}...")
    print(f"[CU] Model: {model}")
    print(f"[CU] Log: {log_path}")

    with log_path.open("a") as logf:
        logf.write(json.dumps({"event": "start", "task": task, "model": model, "ts": ts}) + "\n")

        while turns < max_turns:
            turns += 1
            try:
                response = client.beta.messages.create(
                    model=model,
                    max_tokens=4096,
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
                result_content = execute_action(action, inner_params)
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

    return {
        "turns": turns,
        "success": success,
        "last_message": last_message,
        "log_path": str(log_path),
    }


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
