# SAFETY-WHITELIST — Computer Use Target Windows

> Added PHASE META M.3 — active for all Computer Use sessions.
> The CU host adapter checks this list before every click/key/type action.

---

## Allowed Window Titles (substring match on MainWindowTitle)

```python
WHITELISTED_TITLES = [
    "ArmaReforgerWorkbench",     # Any Workbench variant
    "Enfusion Workbench",        # Workbench alt title
    "Steam",                     # Steam client
    "Windows Terminal",
    "Windows PowerShell",
    "PowerShell",
    "Command Prompt",
    "cmd",
    "Notepad",                   # Smoke tests
    "File Explorer",
    "Explorer",
    "ELOS",                      # ELOS chat window
    "Claude",                    # Claude Code itself
    "Suche",                     # German Windows Search (navigation tool)
    "Search",                    # English Windows Search
    "Start",                     # Windows Start menu
]
```

## Explicitly NOT allowed

Any window NOT in the list above. Specifically:
- Banking / financial sites
- Password managers (1Password, Bitwarden, etc.)
- Social media (Discord, Twitter/X, etc. — unless whitelisted for relay)
- Email clients
- Any window with personal information in title

## Behavior on violation

1. CU refuses the click/type action
2. Logs to `logs/computer-use/<session>/transcript.jsonl` with
   `tool_use: "REFUSED-NonWhitelistedWindow"` and the actual window title
3. Raises `NonWhitelistedWindowError` in run_task.py
4. run_task.py writes blocker to `tasks/STATE.json`, pauses, asks user

## Testing

To verify the whitelist works: temporarily remove a title you need, run a task,
confirm it refuses and logs the refusal, then restore the title.
