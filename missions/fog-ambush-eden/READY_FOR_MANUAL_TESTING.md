# READY_FOR_MANUAL_TESTING.md

> **Status:** ✅ Alle automatischen Tests bestanden
> **Mission:** fog-ambush-eden
> **Generiert:** 2026-05-20T02:11:43.051487+00:00

---

## Was wurde generiert?

```
missions/fog-ambush-eden/output/
  addon.gproj
  Missions/fog-ambush-eden.conf
  Missions/fog-ambush-eden.conf.meta
  Worlds/fog-ambush-eden.ent
  Worlds/fog-ambush-eden.ent.meta
  Worlds/fog-ambush-eden_gamemode.layer
  Worlds/fog-ambush-eden_managers.layer
  Worlds/fog-ambush-eden_spawnpoints.layer
  Worlds/fog-ambush-eden_AI.layer
  Worlds/fog-ambush-eden_tasks.layer
  Worlds/fog-ambush-eden_triggers.layer
  Worlds/fog-ambush-eden_environment.layer
```

---

## Nächste Schritte für Manuel-Test (Windows Workbench)

1. **Output-Verzeichnis übertragen:**
   ```
   missions/fog-ambush-eden/output/  →  Windows PC: C:\ArmaReforger\Addons\fog-ambush-eden\
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

- Addon-GUID: siehe `missions/fog-ambush-eden/mint-log.json`
- Catalog: 1326 verifizierte Assets, 0 halluzinierte GUIDs
- Validation: Schema ✅ | Cross-file ✅ | GUID-Hallucination ✅

---

## Falls Probleme auftreten

Workbench-Fehler → `WORK_LOG.md` updaten mit Fehlermeldung → bug-fixer triggern.

