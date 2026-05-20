---
name: sync-catalog
description: "Re-bootstrapped den Asset-Catalog aus den OSS-Referenz-Repos. Nötig wenn neue Assets oder Repos hinzugekommen sind. Führt bootstrap.py aus."
---

# /sync-catalog

Aktualisiert `catalog/INDEX.json` und alle `catalog/{type}/{guid}.json` Files aus den Referenz-Repos.

## Wann nötig?

- Vor dem ersten `/new-mission` (wenn Catalog noch nicht bootstrapped)
- Nach Reforger-Major-Update (neue Assets können GUIDs ändern)
- Wenn `asset-curator` persistente Misses meldet
- Wenn neue Referenz-Repos hinzugefügt wurden

## Ausführung

```bash
# Repos neu klonen (wenn nicht aktuell):
cd /tmp/reforger-research
git clone --depth 1 https://github.com/exocs/Reforger-Sample-Coop.git --force 2>/dev/null || git -C Reforger-Sample-Coop pull
git clone --depth 1 https://github.com/BohemiaInteractive/Arma-Reforger-Samples.git --force 2>/dev/null || git -C Arma-Reforger-Samples pull
git clone --depth 1 https://github.com/Kexanone/CombatOpsEnhanced_AR.git --force 2>/dev/null || git -C CombatOpsEnhanced_AR pull
git clone --depth 1 https://github.com/gruppe-adler/GRAD-COOP-Template-Reforger.git --force 2>/dev/null || git -C GRAD-COOP-Template-Reforger pull

# Catalog neu bauen:
cd /Users/paulfanger/Documents/ELOS/201_01-MOD-ArmaReforger-Scenarios
python3 backend/catalog/bootstrap.py

# Ergebnis prüfen:
python3 -c "import json; idx=json.load(open('catalog/INDEX.json')); print(f'Catalog: {idx[\"total_assets\"]} assets, {len(idx[\"by_type\"])} types')"
```

## Was passiert dabei?

1. Alle Referenz-Repos werden aktualisiert (shallow clone)
2. GUID-Pattern-Parser läuft über alle `.layer`, `.conf`, `.ent`, `.gproj` Files
3. Deduplizierung nach GUID (reichste Entry gewinnt)
4. Neue `catalog/INDEX.json` + `catalog/{type}/{guid}.json` werden geschrieben
5. Bestehende Entries werden überschrieben wenn aktueller

## Nach Sync

- Mission-Validator-Cache wird automatisch geleert (lädt frischen INDEX beim nächsten Call)
- Laufende Missions-Generierungen sind nicht betroffen (sie nutzen ihre eigene mint-log.json)
- Empfehlung: Neues Snapshot nach Sync wenn Mission bereits in Arbeit

## Dry-Run (nur anzeigen, nicht schreiben)

```bash
python3 backend/catalog/bootstrap.py --dry-run
```
