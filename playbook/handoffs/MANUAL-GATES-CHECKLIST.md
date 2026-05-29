# Manual Gates Checklist — User-Present Session
## Alles was du am PC manuell freigeben/klicken musst, in der richtigen Reihenfolge

**Du bist:** am PC, Wach, kannst klicken + UAC bestätigen + Browser öffnen.
**Ich bin:** Mac Claude Code, coach dich step-by-step. Sag mir was du siehst, ich sag dir was als nächstes kommt.
**Voice Companion:** nicht aktiv (deine Wahl) — wir machen's per Mac-Chat.

---

## ⚡ Quick Status (so geht's los)

Bevor du anfängst, **tipp im Mac-Chat:** `"PC ready, los"` — ich schau git status, sage dir wo wir genau stehen + welcher Gate als nächstes dran ist.

---

## 🎯 Priority Order — was du wann machst

```
P1  S5 Close: 25% Gap zumachen (viewport actually changes)         ~30-45 min
P2  Plugin Pattern Fix (wenn P1 scheitert)                          ~20 min
P3  API Key rotieren (Sicherheit — Key war in Chat)                ~5 min
P4  Workshop Publishing Setup (optional, nur wenn du willst)        ~15 min
P5  pc-requirements.toml anlegen (next sprint nicht blocked)         ~5 min
```

**Wenn du gestresst bist:** mach NUR P1. Rest ist optional / nicht-blocking.

---

## P1 — S5 Close (das Hauptziel)

**Was:** Plugin läuft schon, ist im Workbench ELOS-Menü, schreibt `outbox.json`. **Aber:** noch nie verifiziert dass die Welt sich tatsächlich ändert (fog dichter im Viewport). Das holen wir nach.

### P1.1 — Setup Check (~2 min)

**Du:** öffne PowerShell auf PC.
**Tipp ein:**
```powershell
# Workbench-EXE finden
Get-ChildItem -Path "C:\Program Files (x86)\Steam\steamapps\common" `
  -Recurse -Filter "ArmaReforgerWorkbenchSteam*.exe" `
  -ErrorAction SilentlyContinue | Select-Object FullName

# Plugin-Datei prüfen
Test-Path "C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios\workbench-plugin\AI_GeneratePlugin.c"

# spec.json prüfen (sollte aus letzter Sprint-Iteration existieren)
Get-ChildItem "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\profile\ELOS\" 2>$null
```

**Erwartung:**
- ✅ Workbench-EXE-Pfad ausgegeben (notier den, brauchen wir gleich)
- ✅ Plugin-Datei: True
- ⚠️ spec.json: existiert vielleicht, vielleicht nicht — beides ok

**Sag mir im Chat:** den EXE-Pfad + ob spec.json existiert.

---

### P1.2 — Plugin manuell testen (Option A: as-is) (~15 min)

**Das ist der Try-Current-Plugin-First Ansatz. 50/50 ob's klappt.**

**Du:**
1. **Doppelklick** auf den Workbench-EXE-Pfad ODER aus Steam Library → "Arma Reforger Tools" → Play
2. Workbench öffnet sich
3. Falls Project-Dialog kommt: wähle dein Mission-Addon (`night-recon-everon` oder `ai_night-recon-everon`)
4. **Wechsle in den WorldEditor:** oben Menü → Editors → World Editor
5. Öffne eine Mission-World: File → Open → `night-recon-everon.ent`
6. **WARTE bis Welt geladen** (du siehst 3D-Viewport mit Karte)
7. Schau ins **Plugins-Menü** oben → suche **"ELOS"** Untermenü → **"AI Generate Mission"** klicken
8. Plugin sollte sich öffnen + ausführen

**Was sollte passieren:**
- Status-Window oder Dialog kurz sichtbar
- `outbox.json` neu geschrieben in `Documents\my games\ArmaReforgerWorkbench\profile\ELOS\`
- **Viewport zeigt fog dichter** (das ist das was wir testen wollen)

**Tipp mir im Chat:** was du siehst.

**Wenn viewport SICH ÄNDERT:** 🎉 P1 done, geh weiter zu P1.5 (Snapshot).
**Wenn viewport SICH NICHT ÄNDERT:** sag mir was outbox.json sagt + ob's Errors gab. Wahrscheinlich Postmortem Section 4.A. Wir gehen zu P2 (Plugin Fix).

---

### P1.3 — outbox.json checken (immer machen)

```powershell
Get-Content "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\profile\ELOS\outbox.json" | ConvertFrom-Json
```

**Erwartung:** `{ "success": true, "applied": {...}, "errors": [] }`

**Was sagt der Output?** sag mir:
- success: true/false
- applied: was ist drin
- errors: leer oder welche

Falls `success: true` aber `applied: {}` → das ist die "Plugin ran but didn't actually do anything"-Diagnose. Postmortem #1 confirmed.

---

### P1.4 — Bei Failures: Section 4.A Walkthrough (~10 min)

**Wenn outbox sagt success aber viewport unverändert:**

1. **Title-Bar Check:** Workbench-Fenster oben — steht da "WorldEditor"? Falls nein → falsche Module aktiv, geh zu P2 (Plugin Fix mit `-wbmodule=` CLI).
2. **Script-Editor öffnen:** Tools → Script Editor → schau ob `AI_GeneratePlugin.c` aufgelistet ist → klick drauf → checke ob **rote squiggles** auf `SetVariableValue` oder `GetModule` Zeilen sind.
3. **Falls rote squiggles:** das ist Postmortem #1 confirmed (validate-grün, live-rot). Sag mir welche Zeilen, ich gebe dir den Fix.
4. **Falls keine squiggles aber kein viewport change:** Entity-Properties prüfen — World-Entity (oben in Hierarchy) auswählen, rechts Properties suchen "fog density" oder ähnlich. Wert anzeigen? Falls Wert ist 0.8 aber viewport nicht updated → F5 drücken (Viewport refresh).

**Sag mir im Chat was du siehst.**

---

### P1.5 — Snapshot + Commit (wenn P1 success)

```powershell
# In Mac Claude Code chat (nicht auf PC):
/snapshot S5-CLOSED-live-verified
/stage
```

**Auf PC:** nix mehr — Mac übernimmt commit.

---

## P2 — Plugin Pattern Fix (NUR wenn P1 scheitert)

**Was:** Plugin nutzt aktuell das alte Pattern (`WorkbenchPluginAttribute` + Runtime-`GetModule()`). Postmortem hat das als **Failure #4** identifiziert — das funktioniert ohne aktive WorldEditor-Module nicht.

**Fix:** Umstellen auf das **dokumentierte Bohemia-Pattern**:
- `[WorkbenchToolAttribute(name="AI Generate Mission", category="ELOS", wbModules:{"WorldEditor"})]`
- `override void RunCommandline()` statt `Run()`
- CLI-Aufruf: `ArmaReforgerWorkbenchSteam.exe -wbmodule=WorldEditor -plugin=AI_GeneratePlugin -autoclose=1 -- input=spec.json output=outbox.json`

**Wie du das machst:**

### P2.1 — Du sagst mir "P2 go"

Mac-Chat: `"P2 go"` → ich update `workbench-plugin/AI_GeneratePlugin.c` auf das documented Pattern, commit, push.

### P2.2 — Du pullst auf PC

```powershell
cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
git pull --rebase
```

### P2.3 — Workbench schließen + CLI-Launch (NEUER Weg)

```powershell
# Schließe ALLE Workbench-Instances
Get-Process | Where-Object {$_.ProcessName -like "*Workbench*"} | Stop-Process -Force

# Wechsle in mission folder (so spec.json ist relativ findbar)
cd "$env:USERPROFILE\Documents\my games\ArmaReforger\addons\ai_night-recon-everon"

# Launch mit dokumentiertem Pattern
& "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteam.exe" `
  -wbmodule=WorldEditor `
  -plugin=AI_GeneratePlugin `
  -autoclose=1 `
  -- input=spec.json output=outbox.json
```

**Was passiert:** Workbench öffnet sich → WorldEditor direkt aktiv → Plugin läuft → schreibt outbox.json → schließt sich automatisch.

**Beobachten:** Fenster popt kurz auf, dann zu. Outbox check wie P1.3.

**Wenn das klappt:** Viewport-Verify im normalen Workbench-Start (dann manuell öffnen + spec sehen).

---

## P3 — API Key rotieren (Security, 5 min)

**Warum:** Du hast den Anthropic-Key am 21.5. in Chat geteilt. Best-Practice = rotieren.

### Schritte:
1. **Browser:** [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. **Find** den Key der mit prefix beginnt: `obVZ9DdmYOX...`
3. **Revoke** klicken
4. **Create new key** → Name z.B. `elos-pc-v2`
5. Copy neuen key
6. **In PC PowerShell (User Env Var setzen):**
   ```powershell
   [System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-api03-DEIN-NEUER-KEY", "User")
   ```
7. **PowerShell neu öffnen** (alte Sessions haben noch alten Key)
8. **Verify:**
   ```powershell
   $env:ANTHROPIC_API_KEY = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
   python -c "import os; from anthropic import Anthropic; client = Anthropic(); r = client.messages.create(model='claude-haiku-4-5', max_tokens=10, messages=[{'role':'user','content':'ok'}]); print(r.content[0].text)"
   ```
   Erwartung: "ok" Response.

**Sag mir im Chat:** "Key rotated" → ich mach mir Notiz.

---

## P4 — Workshop Publishing Setup (OPTIONAL, ~15 min)

**Nur machen wenn:** du planst dein Mission/Plugin auf Steam Workshop zu publishen. Sonst skip.

### P4.1 — Bohemia Account verlinken (einmalig)

1. Workbench öffnen (nicht über CLI, normaler Doppelklick)
2. Tools-Menü → "Link Bohemia Account" (oder ähnlich)
3. Browser öffnet sich → Login auf bohemia.net (Account erstellen falls keiner)
4. Authentication callback → Workbench bestätigt "Linked"

### P4.2 — Workshop ToS Akzeptieren (einmalig)

Beim ersten Publish-Versuch → Dialog mit Terms → "Accept".

### P4.3 — Test-Publish (optional)

Wenn alles linked: rechtsklick auf Addon im File-Browser → "Publish to Workshop"
- Preview Image wählen (PNG, irgendeine Mission-Szene)
- Tags (mind. 1 — z.B. "Mission" oder "Coop")
- Visibility: **Private** (für ersten Test! NICHT public)
- Submit

**Sag mir im Chat was passiert** — Workshop-Errors sind unique.

---

## P5 — pc-requirements.toml (Next Sprint Future-Proof, 5 min)

**Was:** Postmortem #3 — Classifier blockt `winget install <X>` außer der Package in repo manifest steht. Wir legen das jetzt an damit nächste Sprints nicht stallen.

### Mac-side (ich mache das):

**Du tippst:** `"P5 go"` im Mac-Chat → ich erstelle:
- `pc-requirements.toml` mit allen winget-Tools + pip-Packages die overnight gebraucht wurden
- Commit + push

### PC-side (du machst das):

```powershell
cd C:\Users\pfofa\Desktop\000_Projekte\201_01-MOD-ArmaReforger-Scenarios
git pull --rebase
Get-Content pc-requirements.toml
```

**Verify:** liest Datei + bestätigt im Chat.

Damit ist next sprint nicht mehr classifier-blocked auf installs.

---

## 🆘 Wenn was schiefgeht — Recovery Patterns

| Was du siehst | Postmortem-Section | Move |
|---|---|---|
| Plugin im ELOS-Menü, klick — nix passiert | Failure #4 (Module activation) | → P2 |
| outbox.json says success, viewport unchanged | Failure #1 (validate vs live) | P1.4 walkthrough |
| Workbench crasht beim Open | Plugin compile error live | → P2 + Script Editor red squiggles checken |
| "Cannot find ArmaReforgerWorkbench*" | Doc assumption wrong | P1.1 recursive search |
| AHK / SendKeys errors | Failure #5 (wrong channel) | **Don't fix AHK — use CLI re-invocation (P2)** |
| Classifier blocked install | Failure #3 | External PowerShell, dann P5 für future |

**Wenn alles eskaliert:** sag mir im Chat `"audit"` → ich pull git, schau mir alles an, sag dir was los ist + nächster Move.

---

## ⏱️ Realistische Time-Estimates

| Wenn… | Total Zeit |
|---|---|
| P1 Option A (plugin as-is) klappt direkt | **~30 min** |
| P1 fails → P2 needed | ~60 min |
| P1 + P2 + P3 (Key rotate) | ~75 min |
| Komplett P1-P5 | ~120 min |

**Mein Vorschlag für heute Abend:** P1 angehen, wenn klappt direkt P3 (5min Key), Rest morgen oder skip.

---

## 🎬 Wie wir starten

**Du im Mac-Chat:** `"PC ready, los"` → ich check git state + sag dir genau welcher Step als nächstes.

**Oder:** wenn du gleich loslegen willst ohne Check, geh direkt zu **P1.1 — Setup Check** und tipp mir den Output von den 3 PowerShell-Befehlen.

🎯 Let's close S5.
