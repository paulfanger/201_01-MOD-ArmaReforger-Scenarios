# A.S2 Final Result — Dedi-Server-Trick Analysis

**Status:** BLOCKED — architecture mismatch, not a simple config error
**Root Cause:** Local unpacked addons cannot be loaded by ArmaReforger dedicated server
**Debugging depth:** 8 server launch attempts, 4 config iterations

---

## What was discovered (empirically valuable for Mac-side)

### Config format fixes (verified):
1. **No BOM encoding** — dedi-config.json must be UTF-8 without BOM (`New-Object System.Text.UTF8Encoding($false)`)
2. **scenarioId format**: `{ADDON_GUID}Path/to/scenario.conf` — NOT just the GUID
3. **`playerCountLimit`** not allowed in `game` object (schema strict)
4. **`mods`** is for Workshop-Mods only (BI platform lookup) — triggers "Addon not found on workshop" for local addons
5. **`publicAddress` + `publicPort`** not allowed in top-level (schema strict)

### Why local unpacked addons won't load via dedi server:
- Server scans `./addons` (server-relative) + `Documents\My Games\ArmaReforger\addons`
- Finds our addon in Available (`guid: '{8B56608D5A651540}'`)
- Does NOT load it into "Loaded addons" — dependency `58D0FB3206B6F859` (vanilla) apparently can't be satisfied without a valid server-side vanilla install OR the addon needs to be in a different format
- Using `mods: [{modId: "8B56608D5A651540"}]` triggers Workshop API lookup → fails (no Workshop ID)

**Conclusion:** The Dedi-Server-Trick works for Workshop mods. For LOCAL unpackaged development addons, we need either:
- **Option A:** Publish to BI Workshop (get real Workshop modId) — permanent solution
- **Option B:** Run the retail game client directly + Vision-loop through menus + click on local scenario in "Game Master" editor (Workbench)
- **Option C:** Use Workbench GUI with `-gproj` (our AI_GeneratePlugin) as the "game test" — validates mission opens in WorldEditor without needing Server

## Working server config (valid schema, fails on addon load):
```json
{
  "bindAddress": "127.0.0.1",
  "bindPort": 2001,
  "game": {
    "name": "ELOS AI Test",
    "scenarioId": "{8B56608D5A651540}Missions/night-recon-everon.conf",
    "gameProperties": {
      "battlEye": false,
      "fastValidation": true
    }
  }
}
```

## Recommended path for Mac-side (in order of effort):
1. **SHORT TERM:** Open Workbench GUI → load `ai_night-recon-everon/addon.gproj` → mission is "tested" in WorldEditor (visual confirm sc-14)
2. **MEDIUM TERM:** Publish one mission to BI Workshop (gets Workshop ID) → Server test with Workshop ID works
3. **LONG TERM:** Sprint S3 user-gate — Paul opens the game, navigates to local scenario via UI, visual confirm
