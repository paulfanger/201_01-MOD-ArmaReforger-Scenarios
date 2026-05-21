; ELOS Workbench reload hotkey trigger
; AutoHotkey v2 script — watches $profile:ELOS\spec.json for changes,
; fires Ctrl+Shift+R into Workbench window when detected.
;
; USAGE:
;   Double-click this file (after winget install AutoHotkey.AutoHotkey -e)
;   Runs in tray. Right-click tray icon → Exit to stop.
;
; PER research/13 — closes the file-watch → reload-hotkey gap that Enforce
; Script can't do natively.

#Requires AutoHotkey v2.0
#SingleInstance Force

specFile := A_UserProfile "\Documents\my games\ArmaReforgerWorkbench\profile\ELOS\spec.json"

; Ensure directory exists (so SetTimer can stat the file)
SplitPath(specFile, &fname, &fdir)
DirCreate(fdir)

lastMtime := 0
TraySetIcon("imageres.dll", 109)
TrayTip("ELOS Reload Watcher", "Watching " specFile, 0)

SetTimer(CheckSpec, 500)  ; 2 Hz polling

CheckSpec(*) {
    global specFile, lastMtime
    if !FileExist(specFile)
        return
    try {
        mtime := FileGetTime(specFile, "M")
    } catch {
        return
    }
    if (mtime <= lastMtime) {
        if (lastMtime = 0) {
            lastMtime := mtime  ; ignore first-run baseline
        }
        return
    }
    lastMtime := mtime

    ; New spec written → bring Workbench to front + fire Ctrl+Shift+R
    if WinExist("ahk_class WindowsForms10.Window.8.app") {
        WinActivate
        Sleep 200
        Send("^+r")
        TrayTip("ELOS", "Plugin reload triggered", 1)
    } else {
        ; Fallback: try by title substring
        if WinExist("Workbench") {
            WinActivate
            Sleep 200
            Send("^+r")
            TrayTip("ELOS", "Plugin reload triggered (fallback)", 1)
        } else {
            TrayTip("ELOS", "Workbench window not found", 1)
        }
    }
}

; Quit hotkey
^!q::ExitApp
