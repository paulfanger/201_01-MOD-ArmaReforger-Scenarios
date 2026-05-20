# READY_FOR_MANUAL_TESTING.md

> **Status:** ✅ Alle automatischen Tests bestanden
> **Mission:** night-recon-everon
> **Generiert:** 2026-05-20T02:11:42.942512+00:00

---

## Was wurde generiert?

```
missions/night-recon-everon/output/
  addon.gproj
  Missions/night-recon-everon.conf
  Missions/night-recon-everon.conf.meta
  Worlds/night-recon-everon.ent
  Worlds/night-recon-everon.ent.meta
  Worlds/night-recon-everon_gamemode.layer
  Worlds/night-recon-everon_managers.layer
  Worlds/night-recon-everon_spawnpoints.layer
  Worlds/night-recon-everon_AI.layer
  Worlds/night-recon-everon_tasks.layer
  Worlds/night-recon-everon_triggers.layer
  Worlds/night-recon-everon_environment.layer
```

---

## Nächste Schritte für Manuel-Test (Windows Workbench)

1. **Output-Verzeichnis übertragen:**
   ```
   missions/night-recon-everon/output/  →  Windows PC: C:\ArmaReforger\Addons\night-recon-everon\
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

- Addon-GUID: siehe `missions/night-recon-everon/mint-log.json`
- Catalog: 1326 verifizierte Assets, 0 halluzinierte GUIDs
- Validation: Schema ✅ | Cross-file ✅ | GUID-Hallucination ✅

---

## Falls Probleme auftreten

Workbench-Fehler → `WORK_LOG.md` updaten mit Fehlermeldung → bug-fixer triggern.

