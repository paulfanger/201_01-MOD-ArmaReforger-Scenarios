# Asset Catalog — Validated, Read-Only during Mission Building

Dieser Catalog ist die einzige Quelle der Wahrheit für Asset-IDs. Jeder asset_id, der von einer Mission referenziert wird, MUSS hier existieren — sonst Halluzinations-Block durch `asset-curator`.

## Status: PLACEHOLDER

Reforger Tools sind nicht auf diesem Mac installiert. Der Catalog ist im MVP ein Placeholder mit Vanilla-Defaults, die aus der Bohemia Reforger Wiki entnommen werden (siehe `research/02-mission-format.md`).

**Vor erstem Mission-Build:** `/sync-catalog` ausführen (sobald Sonnet 4.6 den Command implementiert hat).

## Struktur

```
catalog/
├── factions/
│   ├── us-army.json       # ENF_FactionCallsign_US, Loadouts, etc.
│   ├── fia.json           # FIA Independent
│   └── ussr.json          # USSR
├── vehicles/
│   ├── m151a2.json        # US Jeep
│   ├── uaz469.json        # USSR Jeep
│   └── ...
├── weapons/
│   ├── m16a2.json         # US Rifle
│   ├── ak74.json          # USSR Rifle
│   └── ...
├── prefabs/               # Buildings, Props
│   └── ...
├── maps/
│   ├── everon.json        # Bohemia Everon-Map mit Bounding-Box, Bekannten Orten
│   └── arland.json
└── INDEX.md
```

## Asset-File Schema (Beispiel `us-army.json`)

```json
{
  "asset_id": "ENF_Faction_US",
  "type": "faction",
  "displayName": "US Army",
  "factionKey": "US",
  "loadouts": [
    {"id": "ENF_Loadout_US_Rifleman", "role": "rifleman"},
    {"id": "ENF_Loadout_US_AT", "role": "anti_tank"}
  ],
  "vehicles_allowed": ["m151a2", "m998_humvee"],
  "source": "https://community.bistudio.com/wiki/...",
  "verified_at": "2026-05-20",
  "verified_by": "manual|catalog-sync"
}
```

## Sync-Strategy

Wenn der User später Reforger Tools auf einem Windows-Rechner verfügbar macht:

```bash
/sync-catalog --reforger-path /c/Program\ Files/.../Arma\ Reforger\ Tools/
```

Der Sync-Command (vom Sonnet 4.6 implementiert) scannt:
- `addons/` Folder nach Prefabs
- `.gproj` Files nach Faction-Definitions
- Map-Files nach Map-Metadata

Output: katalog-Files updaten, mit verified_at-Timestamp.

## Halluzinations-Schutz

`asset-curator` Subagent prüft VOR jeder Mission-Generation:

1. Lese alle asset_id-Referenzen in narrative.json + encounters.json
2. Resolve gegen catalog/
3. Bei nicht-existent: BLOCK + Halt-Briefing für User

Dieser Check ist HEILIG. Niemand darf ihn überspringen (auch nicht bug-fixer).
