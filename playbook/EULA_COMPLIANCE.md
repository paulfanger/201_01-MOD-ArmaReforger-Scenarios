# EULA Compliance Playbook

> **Referenz:** `research/03-eula-legal.md` — Risk-Assessment GREEN für offline-Authoring
> **Stand:** 2026-05-20, post-Research

---

## Zusammenfassung

AI-assistiertes Mission-Authoring für Arma Reforger ist **EULA-konform** wenn:
1. Keine Bohemia-Assets direkt eingebettet werden (nur GUID-Refs)
2. Disclosure im Mission-Header vorhanden ist
3. Keine Runtime-LLM-Calls in der Mission stattfinden
4. APL-ND Lizenz für distributable Outputs verwendet wird

**Status: 🟢 GREEN** für das aktuelle ELOS-System.

---

## Pflicht-Disclosure

Jede generierte Mission muss diesen Text im `m_sDescription` Feld enthalten:

```
AI-assisted authoring. Human-reviewed. No live AI calls during gameplay.
```

**Automatisch injiziert durch `backend/exporters/conf.py`** — `generate_mission_header()` appended dies immer.

Für Workshop-Uploads: Zusätzlich in die Workshop-Beschreibung:

```
Diese Mission wurde mit KI-Werkzeugen erstellt (Claude by Anthropic).
Das Briefing, Asset-Layout und die Encounter-Struktur wurden KI-assistiert entworfen.
Alle Inhalte wurden durch einen menschlichen Creative Director (ELOS) überprüft.
Keine KI-Aufrufe finden während des Spielens statt.
```

---

## Verbotene Handlungen (EULA-Grenzlinie)

| Aktion | Status | Grund |
|--------|--------|-------|
| Bohemia-Assets (.edds, .pak) einbetten | 🔴 VERBOTEN | APL-ND § Asset-Nutzung |
| Runtime-LLM-Calls in Mission-Scripts | 🔴 VERBOTEN | EULA-YELLOW + MANW-Disqualifikation |
| LLM-Training auf Reforger-Assets | 🔴 VERBOTEN | Explicit EULA-Prohibition |
| Automatischer Workshop-Upload ohne Disclosure | 🔴 VERBOTEN | Transparency-Requirement |
| GUID-Refs auf nicht-existente Assets | 🟡 HALLUCINATION-RISK | mission-validator blockiert das |
| Offline-Authoring mit Disclosure | 🟢 ERLAUBT | Bestätigt durch Research |
| Mods für Singleplayer mit AI-Authoring | 🟢 ERLAUBT | Allgemein akzeptiert |
| Workshop-Publish mit Disclosure | 🟢 ERLAUBT | Precedents vorhanden (AI War Mod) |

---

## Precedents (Stand 2026-05-20)

- **AI War Mod** (live seit 03/2026): AI-generierte Encounter-Configs, APL-ND, Community-akzeptiert
- **enfusion-mcp** (public repo): MCP-Integration für Enfusion-Engine, keine Reforger-Reaktion
- **Bohemia Position:** Tech-neutral — keine explizite AI-Prohibition für Authoring-Tools

*Quellen: `research/03-eula-legal.md` Section "Precedents"*

---

## APL-ND Lizenz-Anforderungen

**Arma Public License — No Derivatives**

Für jede verteilte Mission (Workshop, andere):
1. ✅ Missions-Files müssen `m_sAuthor` korrekt setzen
2. ✅ `m_sDescription` muss Disclosure enthalten
3. ✅ Keine Bohemia-Asset-Embedding
4. ✅ Keine Weiterverteilung ohne Bohemia-Quellenangabe

**LICENSE.md** enthält den vollständigen APL-ND Text.

---

## MANW-Wettbewerb (Make Arma Not War)

Falls Submission für MANW 2025:
- ❌ KEIN: External Software Claims ohne Disclosure
- ❌ KEIN: Live-AI-Calls während Demo
- ✅ OK: Offline-KI-Authoring-Tool, Mission ist vollständig self-contained
- ✅ OK: Disclosure in Submission-Details

**Stage 7 (Runtime AI Director) ist strikt verboten für MANW** — kein Code dafür im MVP.

---

## Monitoring / Policy-Change-Protokoll

Wenn Bohemia EULA-Änderung veröffentlicht:

1. Prüfe: `https://community.bohemia.net` + `wiki.bohemia.net/Arma_Reforger:Mission_Making`
2. Wenn restriktiver: Workshop-Upload SOFORT pausieren
3. `DECISIONS.md` neuer Eintrag: EULA-Observation mit Datum + Diff
4. Research-Update triggern: `research/03-eula-legal.md` updaten
5. User (Paul) benachrichtigen

**Risk-Watch-Cadence:** Monatlich (oder bei Reforger-Major-Updates).

---

## Auto-Disclosure-Template (für Workshop-Beschreibungen)

Wenn `/publish` Command implementiert wird (Phase 3), nutzt dieser dieses Template:

```
[AI-ASSISTED]
Dieses Mission-Szenario wurde mit dem ELOS AI-Native Mission Authoring System erstellt.

🤖 Tool: Claude by Anthropic (Offline-Authoring, keine Runtime-AI)
👤 Director: Paul Fanger (ELOS)
⚔️ Modus: PvE Coop, {{ player_count }} Spieler
🗺️ Karte: {{ map_name }}

Alle Spielinhalte wurden menschlich überprüft.
Keine KI-Aufrufe erfolgen während des Spielens.
Lizenz: APL-ND (Arma Public License - No Derivatives)
```

---

## Verantwortlichkeit

- **Technische Compliance:** ELOS AI-Native Mission Authoring System (automatisch)
- **Inhaltliche Compliance:** Paul Fanger (Creative Director)
- **EULA-Beobachtung:** ELOS / Paul Fanger (manuell, monatlich)
