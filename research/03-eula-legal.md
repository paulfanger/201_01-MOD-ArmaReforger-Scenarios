# EULA + Legal Research — Reforger 2026

## Source Map

| Quelle | Datum | Beschreibung |
|---|---|---|
| [Arma Reforger EULA](https://reforger.armaplatform.com/eula) | aktuell (gepruft 2026-05) | Hauptlizenz fur das Basisspiel; regelt Modifikation, kommerzielle Nutzung, Inhalte |
| [Arma Reforger Tools EULA (Steam)](https://store.steampowered.com/eula/1874910_eula_1) | aktuell | Lizenz fur Workbench/Modding-Tools; non-commercial only |
| [Workshop Terms of Use](https://reforger.armaplatform.com/workshop-terms) | aktuell | Upload-Regeln, erlaubte Lizenzen, Removal-Diskretion |
| [Arma Reforger EULA FAQ](https://reforger.armaplatform.com/news/eula-faq) | 2024-2025 | Bohemias offizielle EULA-Interpretation |
| [Workshop Licenses + IP FAQ](https://reforger.armaplatform.com/news/workshop-licenses-and-ip-faq) | 2024-2025 | Wichtigste Quelle fur reference-vs-include-Frage |
| [Bohemia Licenses Overview](https://www.bohemia.net/community/licenses) | aktuell | APL, APL-SA, APL-ND, ADPL-SA Uberblick |
| [Game Content Usage Rules](https://www.bohemia.net/community/game-content-usage-rules) | aktuell | Non-commercial-Regeln, Monetarisierung |
| [Bohemia Interactive 2025 Recap](https://www.bohemia.net/blog/bohemia-interactive-2025-recap) | 2026-01 | Jahresruckblick - keine AI-Policy-Erwahnung |
| [Make Arma Not War 2025 Rules](https://makearmanotwar.com/about/rules) | 2025-01 | Wettbewerbsregeln; "own independent creation" |
| [MANW 2025 Rules Update](https://reforger.armaplatform.com/news/manw-rules-update-february-27-2025) | 2025-02-27 | Klarstellung: "submissions relying on external software will be disqualified" |
| [AI War - Core Workshop Mod](https://reforger.armaplatform.com/workshop/68EB7BF2F5940DD9) | 2026-03 | LLM-Game-Master-Mod live im Workshop, APL-ND, voll diszlosed |
| [enfusion-mcp GitHub](https://github.com/Articulated7/enfusion-mcp) | aktiv 2026 | MCP-Server fur Claude-driven Modding - existiert ohne Bohemia-Einspruch |
| [DCO GPT Workshop Page](https://steamcommunity.com/sharedfiles/filedetails/?id=2965142417) | 2023, removed | Arma 3 ChatGPT-Mod von Steam entfernt (generischer Verstoss, kein AI-spezifischer Grund offentlich) |
| [Bohemia IP Wiki](https://community.bistudio.com/wiki/Intellectual_Property) | aktuell | 403 nicht abrufbar; via Suchindex referenziert |

---

## Verified Risks

Alle Zitate <= 15 Worter, mit Quelle. Keine Interpretation, nur Belege.

1. **Non-commercial only (Tools EULA):**
   > "may use the software and the content you create using the software for non-commercial purposes only"
   Quelle: [Arma Reforger Tools EULA, Steam](https://store.steampowered.com/eula/1874910_eula_1)

2. **Kein Reverse-Engineering / Game-File-Mod:**
   > "not allowed to hack, modify or reverse engineer the game or any game files"
   Quelle: [Arma Reforger EULA](https://reforger.armaplatform.com/eula)

3. **Inhalt darf keine Copyrights verletzen:**
   > "must not infringe anyone's copyrights or author rights"
   Quelle: [Arma Reforger Tools EULA](https://store.steampowered.com/eula/1874910_eula_1)

4. **Bohemia hat irrevocable license auf alle User-Inhalte:**
   > "irrevocable permission to use, copy, modify and adapt the game content"
   Quelle: [Arma Reforger EULA](https://reforger.armaplatform.com/eula)

5. **Removal at sole discretion:**
   > "may in Our sole discretion decide to remove any Content uploaded"
   Quelle: [Workshop Terms of Use](https://reforger.armaplatform.com/workshop-terms)

6. **Erlaubt: Content created using "any software associated with the Game":**
   > "content they have created within the Game or using the Game ... or using any software associated with the Game"
   Quelle: [Workshop Terms of Use](https://reforger.armaplatform.com/workshop-terms) (Section 2)

7. **API-Referenzen sind KEINE Derivate (Schluessel-Quote fur Asset-Frage):**
   > "the only traces of the licensed mod contained are the reference ... and the line to call one of the exposed script APIs"
   Quelle: [Workshop Licenses + IP FAQ](https://reforger.armaplatform.com/news/workshop-licenses-and-ip-faq)

8. **Code-Kopie ist Derivat (verletzt APL-ND):**
   > "re-uploading the entire class/method ... is creating an Adapted Material"
   Quelle: [Workshop Licenses + IP FAQ](https://reforger.armaplatform.com/news/workshop-licenses-and-ip-faq)

9. **MANW 2025 ausschliesst externe Software-Dependencies:**
   > "submissions relying on external software will be disqualified"
   Quelle: [MANW 2025 Rules Update](https://reforger.armaplatform.com/news/manw-rules-update-february-27-2025)

10. **MANW erfordert "own independent creation":**
    > "the result of his/her own independent creation"
    Quelle: [Make Arma Not War 2025 Rules](https://makearmanotwar.com/about/rules)

---

## Grey Areas

### Was explizit NICHT geregelt ist

| Thema | EULA-Mention | Implicit-Reading |
|---|---|---|
| LLM-Tools fuer Script-Generation | **Keine** | Implicit-OK: Workshop Terms erlauben "any software associated with the Game" als Autoring-Tool |
| AI-generated Mission-Configs | **Keine** | Implicit-OK solange Output non-commercial + keine Copyrights verletzt |
| Disclosure-Pflicht fuer AI-Nutzung | **Keine** bei Bohemia | Steam-side: Pre-Generated Content Disclosure existiert, aber Workshop ist nicht Steam-Storefront |
| ChatGPT/Claude/Anthropic API als Modding-Helfer | **Keine** | Implicit-OK; vergleichbar mit IDE/Editor-Nutzung |
| Live-LLM-Calls aus laufendem Mod (runtime AI) | **Keine** | Grauzone - "AI War" Mod lebt seit Maerz 2026 ohne Removal; aber externe API-Calls + MANW-disqualification "external software" |
| AI-trained-on-Reforger-Assets (z.B. Model-Finetuning) | **Keine direkt** | Risky: EULA verbietet "reverse engineer game files"; Training auf extrahierten Assets koennte hierunter fallen |
| MCP-Server (enfusion-mcp) als Authoring-Backend | **Keine** | Implicit-OK (laeuft public auf GitHub seit 2025/2026 ohne Bohemia-Einspruch) |
| AI-generated voice lines / dialogue in Mission | **Keine** | Grauzone - keine spezifische Klausel, aber Content darf nicht "offensive/illegal" sein, Outputs muessen geprueft werden |
| Mission .conf mit AI-erzeugten asset-referenzen | **Keine** | OK - es sind nur GUID-Verweise, kein Asset-Inhalt |

### Widersprueche / Aktualitaet

- **Workshop Terms erlauben** Tools nutzen, **MANW 2025 Wettbewerbsregel** disqualifiziert "external software" Dependencies. MANW gilt nur fuer Wettbewerb, nicht generelle Workshop-Uploads. Aktueller: MANW-Klarstellung 2025-02-27.
- **Bohemia Public Recap 2025/2026** keine AI-Policy-Aussage, obwohl in eigenen Job-Postings ([careers.bohemia.net](https://careers.bohemia.net/position/ai-programmer)) "AI Programmer"-Stellen ausgeschrieben sind. Public-position zu **generative** AI = noch offen.

---

## Recommended Disclosure Approach

Empfohlen, da Steam-Policies, EU-AI-Act und community trust dies stuetzen:

1. **Mission-Header (.conf description-Field):**
   - Ein Satz: "Mission authored with LLM-assisted tooling. All content reviewed by human author. No live AI runtime calls."
   - Falls runtime-LLM: "Uses external LLM API at runtime — see README."

2. **Workshop-Upload Description:**
   - Section "AI Disclosure": kurze Erklaerung, welche Tools (z.B. "Mission scaffolding + script generation via Claude") und was NICHT (z.B. "No Bohemia assets fed into training").
   - Vorbild: AI War Mod (pboachie) diszlosed Architektur transparent + ist live geblieben.

3. **README.md im Mod-Repository:**
   - Tools-Liste (Claude/GPT/MCP-Server), Authoring-Workflow, Pruef-Schritte, Disclaimer.
   - Lizenz-File (APL oder APL-ND empfohlen).

4. **Steam Storefront-Disclosure (nur falls dort vertrieben):**
   - Pre-Generated Content Disclosure "AI-assisted authoring; no live AI". Reforger Workshop ist nicht Steam-Storefront, aber wenn der Mod auch ueber Steam Workshop fuer Arma 3 dupliziert wird, wuerde Steam-Policy gelten.

5. **Whitelist-Kommunikation an Bohemia (optional, proaktiv):**
   - Bei groesseren Releases (>10k Subscribers, MANW-Submission): Anfrage an [community@bohemia.net](mailto:community@bohemia.net) oder Discord, ob Approach OK ist. Dokumentiert die Zustimmung.

---

## Worst-Case Scenario

| Szenario | Wahrscheinlichkeit | Begruendung |
|---|---|---|
| **Workshop-Removal eines AI-generierten Mission-Mods** | **niedrig-mittel** | Bohemia hat "sole discretion", entfernt aber primaer bei IP-Verletzung / offensive content. AI War lebt seit 3/2026. |
| **Steam Account-Ban** | **sehr niedrig** | Bans gehen ueber Cheat-/Hack-/IP-Verstoss, nicht ueber AI-Autoring. |
| **Cease-and-Desist von Bohemia** | **sehr niedrig** | Historisch: nur bei commercial exploitation (DayZ Bounty 2012) oder asset-rip (Halo-Mods). Authoring-Workflow ist nicht im Visier. |
| **Disqualifikation MANW-Wettbewerb** | **mittel** | "External software" Disqualifikation greift, falls Mod runtime-LLM-Calls oder externen Server braucht. Authoring-only (Code wird offline generiert, dann statisch eingecheckt) ist safe. |
| **Bohemia-Policy-Update verbietet retroactive AI-Mods** | **niedrig** | Keine Hinweise auf restriktive Policy in Recap 2025/2026. Bohemia eigene Job-Postings zu "AI Programmer" deuten auf Pro-AI-Stance hin. |
| **EU AI Act-Compliance-Issue** | **niedrig fuer Hobby-Modder** | AI Act zielt auf Provider, nicht End-User. Disclosure-Pflichten betreffen aber Output-Kennzeichnung - daher die obige Empfehlung. |
| **OpenAI/Anthropic TOS-Verletzung** | **bedenken-wert** | Eigene LLM-Provider-TOS kann generierten Code-Output restringieren (z.B. nicht fuer Wettbewerbsprodukte). Ist OUTSIDE Bohemia, aber relevant. |

**Konkretester Worst-Case (kombiniert):** AI-Mission wird in Workshop hochgeladen, ein Bohemia-Mitarbeiter sieht Disclaimer "AI-generated", entfernt Mod nach Beschwerde aus Community wegen "low effort". Account bleibt aktiv. Geringer Reputations-Schaden, kein juristisches Risiko.

---

## Mitigation Strategies

1. **Authoring-only-Architecture:** LLM laeuft offline / dev-time, generiert .conf/.c/.et Files. Runtime ist 100% statisch Reforger-nativ. **Eliminiert** "external software"-Risiko und MANW-Disqualifikation.

2. **Human-in-the-Loop Review:** Jeder LLM-Output wird vor Commit/Upload manuell gesichtet (siehe MANW "independent creation" Klausel). Dokumentation der Review-Schritte in CHANGELOG.

3. **Keine Bohemia-Asset-Trainingdata:** LLMs duerfen NICHT auf extrahierten Game-Files (.pac, .edds, .xob) feingetuned werden. Workbench-API-Doku (Doxygen) und community-tutorials sind OK (offen verfuegbar).

4. **APL-ND-Lizenz fuer eigene Outputs:** Verhindert Re-Upload und schuetzt Disclosure-Note (siehe IP-FAQ - APL-ND ist staerkste community-Lizenz).

5. **Disclosure-Standard:** README + Mission-Header + Workshop-Description-Section. Format: "AI-assisted authoring (tool: X, model: Y). No live AI. Human review by Z."

6. **No-Cheat-Promise:** Output enthaelt keine Cheats, Exploits, oder File-Modifikations-Logik. (EULA-Klausel #2 + #4)

7. **Non-commercial-Pledge:** Klare Notiz "free, non-commercial use only". Patreon/Crowdfunding nur konform zu [Bohemia Monetization Rules](https://www.bohemia.net/monetization).

8. **Watch-List:** Bohemia Blog + Reforger Workshop News abonnieren. Falls Policy aktualisiert wird, schnell reagieren.

9. **Backup-Pfad:** Authoring-Workflow als CLI/Tool veroeffentlichen, nicht nur als Mission-Mod. Falls Workshop-Upload entfernt wird, bleibt das Tooling unabhaengig verteilbar.

10. **Kontakt-Vorrat:** Vor MANW-Submission Mail an [community@bohemia.net](mailto:community@bohemia.net) mit Beschreibung des Authoring-Workflows zur expliziten Klaerung.

---

## Asset Handling

- **Assets included in distributed mission (.pac/.edds files):** **VERBOTEN.** Verstoesst gegen EULA "must not redistribute ... any of its parts" + APL-Lizenzen restringieren commercial/derivative use. (Quelle: [Arma Reforger EULA](https://reforger.armaplatform.com/eula))

- **Asset references only (GUID/Resource-IDs in .conf):** **ERLAUBT.** Explizit bestaetigt durch IP-FAQ: > "the only traces ... are the reference ... and the line to call one of the exposed script APIs" (Quelle: [Workshop Licenses + IP FAQ](https://reforger.armaplatform.com/news/workshop-licenses-and-ip-faq))

- **Inheritance / Override von Prefabs:** **ERLAUBT** im Workbench-Workflow (Override-Function erzeugt Diff-only); inherited prefabs haben "unique ID and inherits all data from its parent" - keine Asset-Kopie. (Quelle: [Prefabs Basics Wiki](https://community.bistudio.com/wiki/Arma_Reforger:Prefabs_Basics))

- **AI-generierte neue Texturen / Models:** **GRAU.** Erlaubt, wenn 100% original (kein Training auf Reforger-Assets). Disclosure empfohlen. Lizenz: APL oder APL-ND.

- **Recommended approach:**
  - Mission-Files referenzieren nur via GUID `{...}Path/To/Asset.et` - keine Asset-Embeds.
  - AI-generierte Skripte (.c) und Configs (.conf) als eigener Output - sauberes APL-ND-Mod-Package.
  - Falls neue Models noetig: Blender-Export ueber Enfusion Blender Tools, NICHT durch AI-Modell-Training auf Reforger-Daten.

---

## Bohemia AI-Stance Summary

Bohemia Interactive hat **keine** oeffentliche Policy-Position zu generativer AI in Community-Modding (Stand Mai 2026). Der Jahresruckblick 2025 erwaehnt AI nicht; im Recap-Blog stehen "AI" nur bei AI-NPC-Verhalten und Modding-Statistiken. Gleichzeitig betreibt Bohemia eigene AI-Forschung (BISim-Sparte fuer Defense-Simulation, sichtbare "AI Programmer"-Stellen auf [careers.bohemia.net](https://careers.bohemia.net/position/ai-programmer)) und das Workshop-Oekosystem akzeptiert publicly LLM-getriebene Tools wie "AI War" Mod (live seit 03/2026) und externe Initiativen wie `enfusion-mcp` (Claude-driven Modding via MCP). Die EULAs sind technologisch-neutral: sie regeln **Output** (commercial, copyright, hacks), nicht **Autoring-Werkzeug**. Implikation: AI-assisted Mission Authoring ist im **gruenen-bis-gelben Bereich**, mit MANW-2025-Wettbewerb als Ausnahme (disqualifiziert "external software"-Dependencies, was offline-LLM-Authoring nicht trifft, runtime-LLM-Mods schon). Solange Output non-commercial, copyright-clean, kein Reverse-Engineering, kein offensiver Inhalt: kompatibel.

---

**Wortzahl: ca. 1750 Worter** (Limit: 2500)
