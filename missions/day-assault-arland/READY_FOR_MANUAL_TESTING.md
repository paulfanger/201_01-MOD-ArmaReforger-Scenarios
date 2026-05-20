# READY_FOR_MANUAL_TESTING.md

> **Status:** ✅ Alle automatischen Tests bestanden
> **Mission:** day-assault-arland
> **Generiert:** 2026-05-20T02:11:42.997644+00:00

---

## Was wurde generiert?

```
missions/day-assault-arland/output/
  addon.gproj
  Missions/day-assault-arland.conf
  Missions/day-assault-arland.conf.meta
  Worlds/day-assault-arland.ent
  Worlds/day-assault-arland.ent.meta
  Worlds/day-assault-arland_gamemode.layer
  Worlds/day-assault-arland_managers.layer
  Worlds/day-assault-arland_spawnpoints.layer
  Worlds/day-assault-arland_AI.layer
  Worlds/day-assault-arland_tasks.layer
  Worlds/day-assault-arland_triggers.layer
  Worlds/day-assault-arland_environment.layer
```

---

## Nächste Schritte für Manuel-Test (Windows Workbench)

1. **Output-Verzeichnis übertragen:**
   ```
   missions/day-assault-arland/output/  →  Windows PC: C:\ArmaReforger\Addons\day-assault-arland\
   ```

2. **Workbench öffnen:**
   - `ArmaReforgerWorkbench.exe` starten
   - File → Open Workspace → Navigiere zu `addon.gproj`

3. **Mission testen:**
   - Game Launcher: Add Addon → dein Addon
   - Mission auswählen in Mission-Liste
   - Testrun starten

4. **Was prüfen:**
   - [ ] Mission lädt ohne Fehler
   - [ ] Spawnpunkte sind sichtbar auf der Karte
   - [ ] Zeit-/Wettereinstellungen korrekt (02:30 Uhr, klar)
   - [ ] AI-Gruppen spawnen und patrouillieren (wenn encounters.json vorhanden)
   - [ ] Coop-Modus wählbar mit 1-4 Spielern

5. **Bekannte Limitierungen (MVP):**
   - Encounters.json war leer → AI-Gruppen müssen manuell in Workbench platziert werden
   - Keine Scenario Framework Tasks (Phase 2)
   - Plugin nicht aktiv (Phase 2 Feature)

---

## Technische Details

- Addon-GUID: siehe `missions/day-assault-arland/mint-log.json`
- Catalog: 1326 verifizierte Assets, 0 halluzinierte GUIDs
- Validation: Schema ✅ | Cross-file ✅ | GUID-Hallucination ✅

---

## Falls Probleme auftreten

Workbench-Fehler → `WORK_LOG.md` updaten mit Fehlermeldung → bug-fixer triggern.

