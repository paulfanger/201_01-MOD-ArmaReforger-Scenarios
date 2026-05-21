# Sprint S3 — User-at-PC Fallback (~10-15 min)

> Stand: 2026-05-21 · Model: Sonnet 4.6
> User-state: AM PC, kann klicken + judgment-pass machen
> Source: research/10-3-stage-sprint-design.md
> Trigger: Sprint S2 hat escalated ODER Phase-3-Game-Test + Workshop-Publish ist gewünscht

---

<sprint>

<context>
  <goal>
    Handle ALL irreducible user-actions: (a) Stage-2 escalations falls vorhanden,
    (b) creative-judgment-pass, (c) Workshop-publish-Gates wenn gewünscht.
    Minimize user-clicks to the absolute necessary set.
  </goal>

  <success_criteria>
    <criterion id="sc-1">Stage-2 escalations resolved (oder bestätigt akzeptiert)</criterion>
    <criterion id="sc-2">User hat 60s im Workbench/Editor probegespielt + bewertet (Fun/Atmosphere/Balance)</criterion>
    <criterion id="sc-3">Falls Workshop-Publish: BI-Account verlinkt + ToS accept + Preview + Tags + Visibility done</criterion>
    <criterion id="sc-4">Subjective ratings (1-5) captured in result</criterion>
    <criterion id="sc-5">User-Feedback flows zurück (entweder approve oder revision-request für Sprint S1 again)</criterion>
    <criterion id="sc-6">Final approval snapshot + git push</criterion>
  </success_criteria>

  <constraints>
    <constraint>User-actions klar nummeriert in Checklist (deutsche Sprache)</constraint>
    <constraint>Agent NIEMALS clicks für user — nur instruieren + verifizieren</constraint>
    <constraint>Creative judgment (fun, atmosphere, balance) ALLEIN user-decision</constraint>
    <constraint>NIE automation gegen BattlEye-protected MP scenarios</constraint>
  </constraints>

  <env>
    <workbench_diag>C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe</workbench_diag>
    <game_exe>C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\ArmaReforgerSteam.exe</game_exe>
  </env>
</context>

---

## STAGE 3.0 — Pre-Flight + Context Load

<stage id="3.0" name="preflight">

  <action>
    1. ⚙️ DO Phase A: User confirms "ich bin am PC, kann klicken"
    2. cd repo, git pull --rebase
    3. Read previous artifacts:
       - playbook/handoffs/final-paper-sprint-S2-*.md (if exists)
       - logs/reflection-turn-S2-pc.md
       - tasks/STATE.json (was Sprint S2 blocked? at which stage?)
    4. Determine flow:
       - Falls Sprint S2 PASS → user only does creative-judgment + optional Workshop
       - Falls Sprint S2 BLOCKED → user does manual fallback for the failed stage + judgment
    5. STATE.json update: turn_id=S3, owner=pc, phase=PHASE_C_EXEC
  </action>

  <done_when>
    - User confirmed presence
    - Previous artifacts read
    - Flow decided (PASS-path or BLOCKED-path)
  </done_when>

</stage>

---

## STAGE 3.1 — Resolve Stage-2 Escalations (conditional)

<stage id="3.1" name="resolve_S2_blockers">

  <skip_if>Sprint S2 PASS (no escalations to resolve)</skip_if>

  <action>
    For each blocker logged in Sprint S2:

    1. Display blocker + evidence to user (1 sentence + screenshot reference)
    2. Provide proposed-options (per bug-fixer always-propose rule):
       Example for "Dedi server fails to start":
       ```
       Sprint S2 blocked at Stage 2.1 (Dedi server start). Mögliche Ursachen:
         (A) Mission GUID nicht im Addon-Folder → bitte Workbench öffnen, schauen
             ob ai_night-recon-everon listed ist
         (B) Port 2001 belegt → bitte netstat -an im cmd, sag was du siehst
         (C) Server-config Schema falsch → ich generier neue config

       Welche soll ich versuchen? (A/B/C/Other)
       ```
    3. User picks option → execute the chosen path
    4. Verify resolution
    5. Optional: re-run failed Stage-2 sub-stage manually
  </action>

  <done_when>
    - All Stage-2 blockers either resolved or explicitly accepted as deferred
    - User comfortable with current state
  </done_when>

  <on_failure>
    - Cannot resolve a critical blocker → defer to Mac (escalate)
  </on_failure>

</stage>

---

## STAGE 3.2 — Live Game Manual Test (alle Pfade)

<stage id="3.2" name="manual_game_test">

  <action>
    Wenn Sprint S2 GUI smoke schon PASSED + InGame state confirmed: user kann optional skippen,
    sonst run this stage.

    ⚙️ USER ACTION request:
    ```
    Bitte:
    1. Öffne Arma Reforger Game über Steam (NICHT Workbench)
       ✅ A: Game startet ohne Crash
    2. Game Menü → Scenarios → finde "ai_night-recon-everon"
       ✅ B: Mission ist in der Liste sichtbar
    3. Klick Play, warte bis Mission lädt
       ✅ C: Mission lädt ohne Crash innerhalb 30s
    4. Im Spiel checken:
       ✅ D: Spawn-Point sichtbar (du spawnst irgendwo)
       ✅ E: Bewegung funktioniert (WASD reagiert)
       ✅ F: Time/Weather matchen narrative.json
          (night-recon: dunkel mit fog · day-assault: hellichter Tag · fog-ambush: 06:00 nebelig)
       ✅ G: AI-Gegner irgendwo da (wenn Phase 2 encounters active — bei MVP optional)
    5. Spiel mindestens 60 Sekunden
    6. Tipp zurück: "A:✓ B:✓ C:✓ D:✓ E:✓ F:✓ G:-" (oder issue: <was>)
    ```

    User antwortet → Agent capturt response in logs/manual-game-test-S3.json
  </action>

  <done_when>
    - User reported all 7 Erfolgsmesser (A-G) with ✓/✗/- per criterion
    - sc-2 met
    - logs/manual-game-test-S3.json captured
  </done_when>

  <on_failure>
    - User reports issue: bug-fixer with details + proposed fixes
    - User aborts: document state, escalate
  </on_failure>

</stage>

---

## STAGE 3.3 — Creative Judgment Pass

<stage id="3.3" name="creative_judgment">

  <action>
    🧠 USER PROMPT batch via AskUserQuestion (or chat):

    ```
    Creative Judgment auf night-recon-everon — bewerte 1-5:

    Q1: Wie ist der "Fun-Factor" der Mission?
       1=langweilig, 3=okay, 5=super spaß
    Q2: Wie fühlt sich die Atmosphäre an?
       1=unpassend, 3=okay, 5=perfekt nightly-recon
    Q3: Wie fühlt sich die Balance an (Spieler vs AI)?
       1=trivial, 3=ausgewogen, 5=zu schwer
    Q4: Welche EINE Sache würdest du sofort ändern? (free-text, oder "nichts")
    ```

    User antwortet → Agent capturt in logs/creative-judgment-S3.json

    Falls Q4 != "nichts":
    Agent fragt: "Soll ich das als Sprint S1 revise-request einleiten? (ja/nein)"
    - Bei "ja": agent generates revision-spec, pusht zu Mac for next iteration
    - Bei "nein": logs as future-work item
  </action>

  <done_when>
    - User-ratings captured (sc-4 met)
    - Q4 feedback either processed (revise-request) or filed as future-work
    - sc-5 met
  </done_when>

</stage>

---

## STAGE 3.4 — Workshop Publish (OPTIONAL)

<stage id="3.4" name="workshop_publish">

  <skip_if>User says "nicht jetzt publish" or sprint focus is internal-test-only</skip_if>

  <action>
    🧠 ANSWER: User wants to publish to Steam Workshop? (ja/nein/später)

    Wenn JA:

    ⚙️ DO checklist (first-time gates):
    ```
    Bitte führ aus (~6 clicks first-time, ~3 subsequent):

    1. ☐ Falls BI-Account noch nicht verlinkt:
       Workbench öffnen → Tools menu → "Link Bohemia Account"
       (One-time per BI account)
    2. ☐ Falls Workshop ToS noch nicht akzeptiert:
       Bei erstem Publish-Versuch erscheint ToS dialog → Accept
       (One-time per BI account)
    3. ☐ Preview-Image für die Mission auswählen:
       (320x180 px PNG empfohlen)
       Pfad: <generated-or-asked>
    4. ☐ Tags wählen (Agent schlägt vor):
       [SP-Scenario] [MP-Coop] [AI-Generated] [Night-Mission]
       User confirms or modifies (multi-select)
    5. ☐ Visibility wählen:
       (Public / Friends-only / Private)
    6. ☐ Klick "Publish"

    Workbench triggert ISteamUGC upload. Status im Workbench-Statusbar.
    Sag mir wenn done (z.B. "publish ok" oder "issue: X").
    ```

    Agent monitorisiert keine Steam-API (kein direkter API-Access), wartet auf User-Bestätigung.
  </action>

  <done_when>
    - User confirms publish done OR explicitly skipped
    - sc-3 met (if publish chosen)
    - Workshop URL captured in result (if publish chosen)
  </done_when>

  <on_failure>
    - User reports publish-error: log error message, escalate to Mac for analysis
  </on_failure>

</stage>

---

## STAGE 3.5 — Final Approval + Snapshot + Push

<stage id="3.5" name="final_approval">

  <action>
    1. Aggregate all S3 outcomes into logs/sprint-S3-summary.json
    2. Generate playbook/handoffs/final-paper-sprint-S3-<TS>.md:
       - Sprint S2 status (PASS / partial-resolved / abandoned)
       - Manual game test results (Erfolgsmesser A-G)
       - Creative judgment ratings (Q1-Q4)
       - Workshop publish status (if done) + URL
       - User's revision-request (if any, queued for Sprint S1)
       - Final approval flag
    3. Write logs/reflection-turn-S3-pc.md
    4. log_episode for each stage
    5. Snapshot the approval state:
       ```
       Save current narrative.json + output/ + Workshop URL as
       missions/<id>/snapshots/N_user_approved.json
       ```
    6. Update tasks/STATE.json: phase=PHASE_D_RETURN, sprint_S3_complete=true,
       user_approved=true
    7. git pull --rebase, add -A, commit, push
    8. Output to chat: "Sprint S3 complete. User-approved. Mission ist live (Workshop: <url> wenn publish'd) OR ready for next iteration (revision queued: <yes/no>)."
  </action>

  <done_when>
    - Final paper generated
    - reflection-turn-S3-pc.md written
    - episodic.jsonl updated
    - Snapshot saved
    - All commits pushed
    - Loop closed for this iteration
  </done_when>

</stage>

---

<escalation_triggers>
  - User reports critical issue Mac can solve faster than PC
  - User wants to add a complex revision (multi-field changes) → kick to Sprint S1
  - Workshop publish error message Mac should debug
  - Token budget > 80% (unlikely, sprint is short)
</escalation_triggers>

<sub_agents_enabled>
  <agent role="logger" always_on="true"/>
  <agent role="auditor" pre_push="true" model="sonnet"/>
  <agent role="bug-fixer" on_failure="true" model="sonnet"/>
  <!-- No ui-tester/dep-installer needed — user does the GUI -->
</sub_agents_enabled>

<token_budgets>
  <per_stage_max>20000</per_stage_max>
  <total_max>100000</total_max>
  <escalate_at>80000</escalate_at>
</token_budgets>

<hard_guards>
  - max_retries_per_step = 3
  - step_time_budget = 15 min (user-paced)
  - sprint_time_budget = 30 min total
  - DRY marker for any snapshot/destructive op
</hard_guards>

</sprint>

---

## Wrapper Prompt (paste in PC chat when user at PC, after S2 done or to handle escalation)

```
Du bist PC-Executor. User ist AM PC. Sprint S3 — Manual Fallback + Creative Judgment.
Sonnet 4.6. ~10-15 min, user-paced.

Lies in dieser Reihenfolge:
1. playbook/handoffs/PROJECT_STATE_2026-05-21.md
2. playbook/RELAY_PROTOCOL.md
3. PC_AGENT_BRIEF.md
4. playbook/handoffs/final-paper-sprint-S2-*.md (most recent — read what was achieved/blocked)
5. playbook/handoffs/sprint-S3-user-fallback.md ← THIS PLAN

Conditional flow:
- Falls Sprint S2 ALLES PASS → Skip Stage 3.1 (resolve blockers), gehe direkt zu 3.2-3.5
- Falls Sprint S2 escalations → resolve in Stage 3.1, dann 3.2-3.5

Stages 3.0 → 3.5 strictly per plan.

Two-Phase Reception:
- Phase A: ⚙️ DO = "User confirms 'ich bin am PC, kann klicken + judgment-pass machen'"
- Phase B: Verify Stage-2-result-files exist + flow decided
- Phase C: Stages 3.0-3.5 (user-paced)
- Phase D: Final paper + reflection-turn-S3-pc.md

Format alle User-Action-Gates als nummerierte checklist (deutsche Sprache).
Agent INSTRUIERT, klickt NIEMALS für user.
Creative judgment (Stage 3.3): User-only.

Sub-agents: logger always-on, auditor pre-push, bug-fixer on-fail.

Final Paper: playbook/handoffs/final-paper-sprint-S3-<TS>.md
Push continuously.

Start with Stage 3.0 (Pre-Flight + Context Load).
```
