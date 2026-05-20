# Open Question 1: Linux Dedicated Server Direct-Load

> **Status:** DEFERRED — kein Linux-Dedi verfügbar auf dieser Maschine (macOS M1)
> **Impact:** HIGH — wenn bestätigt, wäre ein vollständiger Mac-Workflow ohne Windows möglich
> **Stand:** 2026-05-20

---

## Frage

Kann ein Arma Reforger Linux Dedicated Server ein **unpacked addon-tree** (kein .pak) direkt laden?

Bekannte CLI-Flags:
```bash
reforger-dedi \
  -addonsDir /path/to/missions/{id}/output \
  -mission "{ADDON_GUID}Missions/{id}.conf" \
  -maxFPS 30 \
  -profile /tmp/reforger-profile
```

## Was wäre der Beweis?

**Erfolg:** Server-Log zeigt `Mission loaded: {id}` und keine Asset-Resolution-Errors.
**Fehlschlag:** `Cannot load unpacked addon` oder ähnlicher Error.

## Reproduktions-Plan (wenn Linux-Dedi verfügbar)

### Option A: VPS / dedizierter Server

```bash
# 1. Output-Tree auf den Server übertragen
rsync -avz missions/test-mission-pipeline-check/output/ user@your-server:/tmp/test-addon/

# 2. Reforger-Dedi starten
ssh user@your-server "
  reforger-dedi \
    -addonsDir /tmp/test-addon \
    -mission '{ADDON_GUID}Missions/test-mission-pipeline-check.conf' \
    -maxFPS 15 \
    -profile /tmp/reforger-profile-test \
    -log /tmp/reforger-test.log \
    2>&1 &
  sleep 30
  cat /tmp/reforger-test.log | grep -E '(Mission|Error|Warning|addon)'
"
```

### Option B: Docker (wenn Reforger-Image verfügbar)

```bash
docker pull bohemiainteractive/arma-reforger-dedi:latest  # hypothetical
docker run --rm \
  -v $(pwd)/missions/test-mission-pipeline-check/output:/addon \
  bohemiainteractive/arma-reforger-dedi:latest \
  -addonsDir /addon \
  -mission "{ADDON_GUID}Missions/test-mission-pipeline-check.conf"
```

## GUID für den Test

Der `ADDON_GUID` für test-mission-pipeline-check befindet sich in:
```
missions/test-mission-pipeline-check/mint-log.json (Index 0 = addon_guid)
```

Oder lass via:
```bash
python3 -c "import json; print(json.load(open('missions/test-mission-pipeline-check/mint-log.json'))[0])"
```

## Ergebnis-Log

Wenn du den Test durchführst, trage hier ein:

```
Datum: ___________
Server: ___________
Reforger-Version: ___________
Ergebnis: [ ] Erfolg / [ ] Fehlschlag
Log-Auszug:
___________
```

Und schreibe das Ergebnis in `research/04-linux-dedi-test.md`.

---

## Fallback (aktuell aktiv)

Mode-B: User überträgt `missions/{id}/output/` manuell auf Windows-PC.
Workbench öffnet `addon.gproj` → Mission spielbar.

Dokumentation in: `missions/test-mission-pipeline-check/READY_FOR_MANUAL_TESTING.md`
