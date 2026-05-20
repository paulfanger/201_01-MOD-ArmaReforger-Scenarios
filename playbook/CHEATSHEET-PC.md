# PC Cheatsheet — Arma Reforger Mission Authoring

> **Empirisches Wissen aus 6 Loop-Turns auf diesem PC (2026-05-20).**
> Alles hier ist direkt verifiziert oder falsifiziert. Keine Theorie, kein Wiki-Copy-Paste.
> Pflege: nach jedem Task der neues Wissen bringt — Sektion updaten, Datum notieren.

---

## ✅ Verified Working

### Steam-CLI

```powershell
# Arma Reforger Tools installieren (AppID 1874910)
Start-Process "steam://install/1874910"

# Arma Reforger Game starten
Start-Process "steam://run/1874880"
```

> AppID 1874910 = Tools (verified Task 002). AppID 1874880 = Game. Beides public auf Account.

### Pfade (empirisch verifiziert, 2026-05-20)

```powershell
# Workbench-Diag (im Subfolder, Diag-Suffix, Version 1.6.0.119)
$diag = "C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe"

# Addon-Ziel (NICHT %LOCALAPPDATA%!)
$addonsRoot = "$env:USERPROFILE\Documents\my games\ArmaReforger\addons"

# Workbench-AppData (Logs + Profile)
$wbDocs = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench"

# Workbench-Logs (nach jedem Run)
$wbLogs = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\logs"

# Vanilla-Junctions-Target (Workbench-Addons-Scan-Path)
$wbAddons = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons"
```

### Vanilla-Junctions (muss einmalig angelegt sein)

```powershell
# scripts/pc-setup.ps1 idempotent ausführen (New-Item -ItemType Junction, kein cmd)
powershell -ExecutionPolicy Bypass -File "$repo\scripts\pc-setup.ps1"
# Output wenn ok: [skip] x2 + "Done. Workbench-Diag kann jetzt Vanilla-Deps resolven."
```

Junctions landen in `%USERPROFILE%\Documents\my games\ArmaReforgerWorkbench\addons\`:
- `_vanilla_core` → `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\core`
- `_vanilla_data` → `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data`

**Ohne diese Junctions:** Engine wirft `Game addon '58D0FB3206B6F859' not found` (dep-cascade-fail).

### Validate-CLI (Compile-Gate)

```powershell
# PFLICHT: immer -wbSilent sonst öffnet sich GUI-Dialog bei Errors
$proc = Start-Process -FilePath $diag -ArgumentList @(
    "-gproj", "`"$gproj`"",
    "-validate",
    "-wbSilent",
    "-exitAfterInit",
    "-logsDir", "`"$logDir`""
) -PassThru -NoNewWindow

# Timeout 30s (validate läuft 4-8s bei clean config)
$waited = 0
while (-not $proc.HasExited -and $waited -lt 30) { Start-Sleep -Seconds 2; $waited += 2 }
if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
```

**Pass/Fail-Heuristik (log-pattern, NICHT exit-code):**
```powershell
$content = Get-Content "$logDir\console.log" -Raw
$fatals = ([regex]::Matches($content, "(?m)^\s*\S+\s+\(F\):")).Count
$errors = ([regex]::Matches($content, "(?m)^\s*\S+\s+\(E\):")).Count
$passed = ($fatals -eq 0) -and ($errors -eq 0)
```

> Validate prüft nur Script-Compile. Läuft ~4-8s. **Stabil CI-Gate** — 3/3 PASS seit Task 005.

### Addon.gproj Minimal-Schema (Enfusion-valide)

```
GameProject {
 ID "addonid"
 GUID "{XXXXXXXXXXXXXXXX}"
 TITLE "Human Title"
 Dependencies {
  "58D0FB3206B6F859"
 }
}
```

Nur diese Keys. Kein `Author`, kein `Version`, keine Extras — Enfusion kennt sie nicht.

### Screenshot (PS-native, kein Install)

```powershell
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
$gfx.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bmp.Save("C:\path\screenshot.png", [System.Drawing.Imaging.ImageFormat]::Png)
$gfx.Dispose(); $bmp.Dispose()
```

---

## ❌ Disconfirmed Empirically

### AppID 1874881 existiert nicht
`Start-Process "steam://install/1874881"` → Error-Toast, kein Download. **Korrekte ID: 1874910.**

### `Author "..."` in addon.gproj
Mac-Side hatte `Author "AI-Native Mission Authoring System"` im Template. Workbench-Diag:
```
INIT (E): Unknown keyword/data 'Author' at offset 104(0x68)
```
Enfusion-Schema kennt `Author` nicht. Fix: Zeile entfernen, Attribution in DISCLOSURE.md.

### `-load $A:Worlds/X.ent` mit `-wbSilent` triggert keinen World-Load
Laut research/06 Sektion B sollte das einen World-Load smoketest machen. **FALSCH für 1.6.0.119.**
Workbench exited sauber nach Engine-Init (~5s), "Entities load"-Pattern erscheint nie.
Auch getestet ohne `-exitAfterInit` — gleiches Ergebnis.
> Workaround: GUI-Smoke (Task 008) oder Workbench-Plugin (Backlog).

### Exit-Code ist immer empty
`$proc.ExitCode` ist leer nach dem Workbench-Diag Exit (sowohl bei Fehler als auch Erfolg).
**Nur log-pattern nutzen** — nicht exit-code.

### `%LOCALAPPDATA%\Bohemia Interactive\ArmaReforger` existiert nicht
Ältere Docs/Wikis nennen diesen Pfad. Auf diesem PC (Account hatte Arma Reforger schon 2024):
**Echter Pfad: `%USERPROFILE%\Documents\my games\ArmaReforger\`**

### Vanilla-Junction in `my games\ArmaReforger\addons\` hilft nicht
Strategy A (Task 003): Junction `_vanilla_data` im User-Addons-Parent angelegt.
Engine scannt nicht parent-Level, nur `addons\ai_<mission>\` + Workbench-AppData-Addons + `./addons`.
**Workaround: Junction in Workbench-AppData-Addons** (Strategy C, das Funktionierende).

---

## ⚠️ PowerShell Pitfalls

### Variable vor Colon → Drive-Var-Bug

```powershell
# ❌ FALSCH — PS5 interpretiert "$mission:" als Drive-Qualifier
Write-Output "[revalidate] $mission: status=$status"

# ✅ RICHTIG — explizite Variable oder Sub-Expression
$ms = $mission
Write-Output "[revalidate] ${mission}: status=$status"
Write-Output "[revalidate] $($mission): status=$status"
```

### cmd.exe-Quoting für Junction-Erstellung

```powershell
# ❌ FALSCH — Quoting-Chaos mit Pfaden mit Leerzeichen
cmd /c mklink /J "`"$linkPath`"" "`"$target`""  # stolpert bei Pfaden mit Spaces

# ✅ RICHTIG — PowerShell-native
New-Item -ItemType Junction -Path $linkPath -Target $target -Force | Out-Null
```

### Backtick-n in Double-Quoted Strings

```powershell
# ❌ FALSCH — kann in PS5 Parse-Error auslösen (pc-setup.ps1 Line-49-Bug)
Write-Output "`nDone. Something here."

# ✅ RICHTIG — explizite Leerzeile
Write-Output ""
Write-Output "Done. Something here."
```

### PSCustomObject Property-Addition

```powershell
# ❌ FALSCH — $obj.newProp = X wirft Exception wenn Property nicht existiert
$state = Get-Content "file.json" | ConvertFrom-Json
$state.finished_at = (Get-Date -Format "...")  # Exception: property not found

# ✅ RICHTIG — Property bei Erstellung inkludieren ODER Add-Member nutzen
$state | Add-Member -NotePropertyName "finished_at" -NotePropertyValue (Get-Date -Format "...") -Force
# ODER direkt beim json-Aufbau die Property einschließen
```

### `Start-Sleep` direkt im Tool (nicht in run_in_background)

Lang-laufende `Start-Sleep`-Blöcke (>30s) im synchronen Tool-Call werden blockiert.
**Lösung:** `run_in_background=true` verwenden, oder kurze Sleep-Werte (<30s) mit Polling-Loop.

---

## 🛟 Recovery / Cleanup

### Alle Workbench-Prozesse killen (schnell)

```powershell
Get-Process -Name "ArmaReforgerWorkbench*" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
```

### Game-Prozesse killen

```powershell
Get-Process -Name "ArmaReforger*" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3
```

### Junctions entfernen (Cleanup)

```powershell
# cmd /c rmdir ist nötig — Remove-Item auf Junctions kann das Target löschen!
$wbAddons = "$env:USERPROFILE\Documents\my games\ArmaReforgerWorkbench\addons"
cmd /c rmdir "$wbAddons\_vanilla_core"
cmd /c rmdir "$wbAddons\_vanilla_data"
# Strategy-A-Junction (nutzlos aber harmlos):
cmd /c rmdir "$env:USERPROFILE\Documents\my games\ArmaReforger\addons\_vanilla_data"
```

### DRY-Recopy (Standard für Mission-Reset)

```powershell
# DRY-Plan berechnen → hash sichern → execute
$src = "$repo\missions\$mission\output"
$dst = "$addonsRoot\ai_$mission"
Remove-Item -Path $dst -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path $src -Destination $dst -Recurse -Force
```

### Git-Rebase bei Merge-Konflikt in PC_RESULT.md

```powershell
# Konflikt-Marker aus PC_RESULT.md entfernen (Mac-WAITING vs PC-RESULT)
# Behalte immer den PC-Content (der ist der vollständige Bericht)
# Mac-Version ist nur ein WAITING-Placeholder
git add tasks/PC_RESULT.md
git -c user.name="pfofa-pc-agent" -c user.email="duemm.fanger@gmail.com" rebase --continue
```

---

## 📊 Quickref: Steam App IDs

| App | ID |
|---|---|
| Arma Reforger (Game) | 1874880 |
| Arma Reforger Tools (Workbench) | 1874910 |

## 📊 Quickref: Important GUIDs

| What | GUID |
|---|---|
| ArmaReforger vanilla base (mandatory dep) | `58D0FB3206B6F859` |
| Enfusion core data | `5614BBCCBB55ED1C` |

## 📊 Validate-Erwartungen

| Situation | Erwartetes Ergebnis |
|---|---|
| Addons ok + Junctions ok + gproj clean | 0 fatals, 0 errors, 4-8s runtime |
| Junctions fehlen | `ENGINE (E): Game addon '58D0FB3206B6F859' not found` |
| `Author` im gproj | `INIT (E): Unknown keyword/data 'Author'` |
| Workbench-Version mismatch | `ENGINE (E): Addon '...' dependency '...' can't be added` |
| CS parallel + -wbSilent | OK — headless, kein Focus-Steal, kein GPU-Konflikt |
