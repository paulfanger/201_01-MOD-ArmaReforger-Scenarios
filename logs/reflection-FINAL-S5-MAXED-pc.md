# FINAL-S5-MAXED Sprint Reflection (PC-side)

## What went well
- **CU roundtrip proved**: Notepad demo 18 turns, reliable screenshot+click.
- **Plugin in Workbench menu**: ELOS > AI Generate Mission confirmed via CU (F.4). 6 attempts to debug Enforce Script syntax — each one taught something concrete.
- **Plugin executes + reads spec.json**: FileIO works, outbox.json written. The pipeline EXISTS.
- **Computer Use is a real capability**: Not perfect, but Sonnet 4.6 navigating Workbench menus reliably.

## What failed (and why)
- **WorldEditorAPI unavailable**: Plugin ran but WorldEditor module wasn't active. Requires user to open WorldEditor from Editors menu — or start with .ent file.
- **Enforce Script compile discrepancies**: -validate headless PASSES even with errors that live Workbench rejects. Next sprint should use ONLY live Workbench for compile verification.
- **AHK A_UserProfile variable error**: Triggered in some contexts. Needs investigation.
- **wbModules: {"WorldEditor"} restriction**: Plugin invisible without WorldEditor active. Switched to WorkbenchPlugin base class — correct fix.

## Key Enforce Script learnings
- NO ternary `? :`
- NO `string.ToLower()` or `string.Contains()`
- NO `IndexOf(str, startPos)` — 1 param only
- `WorldEditorPlugin` vs `WorkbenchPlugin` — different visibility scope

## Carry to S3
- User opens WorldEditor in Workbench, plugin fires, fog dichter works
- Fix AHK A_UserProfile: use `A_AppData` or hard-code path as fallback
- Consider: write elos-reload-test.ahk that just shows a dialog on file-change (simple proof before the Ctrl+Shift+R part)
