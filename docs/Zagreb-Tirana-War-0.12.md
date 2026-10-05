# Zagreb–Tirana Pact wartime events — 0.12.0

Implemented into the live HOI4 mod first, then validated there and synchronized
back to the repository. Installation is complete. Engine campaign acceptance is
pending the user's test; their running game was not accessed or restarted.

## 1. Files changed and deployment

Primary installed root:
`C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`.

Exactly 22 mod files plus the sibling launcher descriptor were deployed.
[Source manifest](pact_war_sources.json) lists every absolute installed path,
baseline hash, asset ZIP member and native-handler upstream hash.
[Sync inventory](pact_war_sync.json) verifies all 279 source/runtime files and
the launcher descriptor, preserving Workshop ID `3813570241` and the exact live
folder path. No runtime-only files are present.

Changed/added paths under the installed root:

```text
common/ideas/MSGA_pact_war_ideas.txt
common/on_actions/MSGA_pact_war_on_actions.txt
common/on_actions/TFR_on_actions_ZZZ_peace.txt
common/scripted_effects/MSGA_encirclement_effects.txt
common/scripted_effects/MSGA_pact_war_effects.txt
common/scripted_triggers/MSGA_pact_war_triggers.txt
common/technologies/MSGA_pact_war_technologies.txt
events/MSGA_pact_war_events.txt
interface/MSGA_balkan_war_eventpictures.gfx
localisation/english/MSGA_pact_war_l_english.yml
gfx/event_pictures/MSGA_event_podgorica_has_fallen.dds
gfx/event_pictures/MSGA_event_podgorica_submits.dds
gfx/event_pictures/MSGA_event_skopje_has_fallen.dds
gfx/event_pictures/MSGA_event_skopje_accepts_terms.dds
gfx/event_pictures/MSGA_event_tirana_has_fallen.dds
gfx/event_pictures/MSGA_event_tirana_accepts_new_order.dds
gfx/event_pictures/MSGA_event_ljubljana_has_fallen.dds
gfx/event_pictures/MSGA_event_ljubljana_seeks_terms.dds
gfx/event_pictures/MSGA_event_zagreb_has_fallen.dds
gfx/event_pictures/MSGA_event_croatia_capitulates.dds
descriptor.mod
make_serbia_great_again.mod
```

Also deployed:
`C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again.mod`.
Recoverable pre-edit files are ignored under `logs/pact_war_012_backup`.
No TFR/other-mod files or game saves were edited. All seven focus layouts,
existing divisions, equipment, previous rewards and the 100-day Srpska question
remain unchanged. Repository additions include the installer, live-to-source
sync helper, eighth validator, three existing-validator extensions and reports.

## 2–4. Events, tags and verified native capitals

Namespace: `MSGA_pactwar`. The country's real TFR history capital, state owner,
core, province membership and positive victory-point entry were all inspected.
Slovenia uses `SLV`; `SLO` is not used.

| Country | Tag | Capital | State / province | Capital event | Capitulation event |
|---|---|---|---|---|---|
| Montenegro | MNT | Podgorica | 105 / 9809 | `.1` Podgorica Has Fallen | `.2` Podgorica Submits |
| North Macedonia | MAC | Skopje | 106 / 3882 | `.3` Skopje Has Fallen | `.4` Skopje Accepts Serbian Terms |
| Albania | ALB | Tirana | 44 / 9914 | `.5` Tirana Has Fallen | `.6` Tirana Accepts the New Order |
| Slovenia | SLV | Ljubljana | 102 / 9627 | `.7` Ljubljana Has Fallen | `.8` Ljubljana Seeks Terms |
| Croatia | CRO | Zagreb | 109 / 11581 | `.9` Zagreb Has Fallen | `.10` The Leader of the Pact Falls |

`.11` is The Balkan Coalition Defeated; `.90` is a hidden active-war observer.
All visible events are once-only and use two short, geographically distinct
English paragraphs. Notifications contain no delayed, click-dependent puppet
effects: control rewards and actual settlement are applied when detected.

## 5. Capital detection and resistance

Serbia must have opened the approved campaign and still be at war with the
target. The target must exist, be an approved participant and not have
capitulated. Its native capital province must be controlled by Serbia, a Serbian
subject fighting that target, or a faction ally sharing Serbia's war. A neutral
or unrelated occupying country cannot fire these events. Province control,
rather than ownership, is checked.

State-control changes scan immediately. A one-day hidden observer catches VP
captures that do not change the whole state's controller. Startup/weekly hooks
resume an existing campaign; a pending flag prevents duplicate observer queues.
It runs only with a remaining hostile participant or recorded pending surrender,
and stops after victory or external peace without pending surrender.

The Serbian once-only flags are `MSGA_podgorica_fallen`, `MSGA_skopje_fallen`,
`MSGA_tirana_fallen`, `MSGA_ljubljana_fallen` and `MSGA_zagreb_fallen`.
Recapture does not grant rewards twice. Capital effects never call autonomy,
peace, surrender, annexation, faction withdrawal or victory effects.

| Country | Serbian reward | Target penalty | Capital spirit / days | Recovery spirit / days |
|---|---|---|---|---|
| MNT | +5% WS, 10 army XP | −10% stability/WS | Resistance in the Highlands / 30 | Post-War Administration / 90 |
| MAC | +5% WS, 10 army XP | −10% stability/WS | Defend What Remains / 30 | Government Under Serbian Protection / 90 |
| ALB | +5% stability/WS, 15 army XP | −10% stability, −15% WS | War in the Highlands / 45 | A Defeated Albania / 120 |
| SLV | +3% WS, 10 army XP | −10% stability/WS | Retreat to the Alps / 30 | Government of National Recovery / 90 |
| CRO | +5% stability, +10% WS, 20 army XP | −15% stability/WS | Fight Beyond Zagreb / 45 | The Defeated Coalition Leader / 120 |

The requested spirit modifiers use verified engine/TFR keys. There is no valid
country-wide `mountain_defence_factor` in the installed engine. The three
highland spirits instead enable an effect-only hidden technology applying
`mountain = { defence = 0.10 }` to the 77 actual TFR land battalion types.
This mirrors native TFR terrain technology syntax. The spirit's `on_remove`
removes the technology on expiry or capitulation; it has no research-tree folder.

## 6. Real capitulation detection

The existing local copy of `TFR_on_actions_ZZZ_peace.txt` normally includes
annexation/default peace handling. Its first `on_capitulation` effect now has
one narrow `if/else` wrapper. In this native callback, ROOT is the capitulated
loser and FROM the actual winner, as confirmed by TFR's native implementation.

Fresh settlements require the five approved tags, the participant flag,
`has_capitulated = yes`, Serbia's opened campaign without final victory,
a Serbian-side actual victor and no existing Serbian subject status. The branch records
`MSGA_pact_real_capitulation` on the loser before any transition. Mere capital
control and arbitrary callbacks fail the guard. A country can normally
capitulate without receiving its capital event; settlement does not depend on it.
Already-recorded Serbian subjects remain in the custom no-op handler for repeated
callbacks, even after the engine clears their capitulation boolean or final
victory fires. They must not fall back into native annexation. The model checks
this explicitly for every defeat order and all three winner variants.

The `else` contains the exact previous 0.11 native body. Validators reconstruct
its AST and check parity with both that baseline and the installed upstream
after removing the known guards. Other native capitulation hooks were inspected:
the generic hook targets unrelated countries and the map-mode hook refreshes UI.
No installed TFR file was modified. Rebase this override if the recorded upstream
hash changes.

## 7–8. Conversion order and autonomy

1. Record real capitulation in the native callback.
2. If the loser leads the Pact, promote a surviving, non-capitulated enemy in
   the same faction before withdrawing the loser. Selection imposes no required
   defeat order.
3. Leave the Pact and remove its temporary capital-resistance spirit.
4. In Serbia's scope, call `set_autonomy` targeting this country with
   `autonomy_state = autonomy_puppet`, `freedom_level = 0.5`, `end_wars = yes`
   and `end_civil_wars = no`. This documented API cancels that target's normal
   war relations while establishing Serbian overlordship.
5. Verify actual subject status and absence of a hostile war with Serbia.
6. Leave any implicitly assigned faction, set the temporary call-decline rule,
   add military neutrality and the requested recovery spirit.
7. Remove only the mandatory-major marker introduced by this module; restore
   Serbian-side occupation control of states still owned by the target.
8. Set the corresponding Serbia-side defeat flag and notify Serbia.

Ownership and cores are never reassigned. In particular, the owned-state guard
cannot return Serbian Kosovo states 785 or 1305 to Albania. The country is never
annexed or deleted. No divisions are transferred to Serbia or respawned; actual
combat losses and normal capitulation internments remain engine mechanics.
Recorded but incomplete settlements retry through the observer/weekly recovery.

## 9. Preventing automatic reentry

Defeated puppets remain politically under Serbia but outside both wartime
factions. `MSGA_pact_postwar_neutrality` sets native AI call/join desire factors
to −1. A scoped country rule overrides the native puppet prohibition on declining
calls: `can_decline_call_to_war = yes`. There is no automatic `add_to_war`.
Former Pact members cannot issue faction calls to the withdrawn country.

Only after all five settlements does the module remove neutrality/call overrides.
Serbian faction admission is then allowed only if Serbia has no war. If Serbia
is in another war, the new puppets stay outside the faction; they remain Serbian
subjects. Actual AI/engine call behaviour still requires the user's engine test.

## 10. Keeping remaining enemies fighting

At war opening, each non-major participant becomes a mandatory major with a
marker recording this temporary change. Existing majors are not demoted later.
This prevents the engine's all-majors surrender rule from treating Croatia alone
as the whole coalition. No surrender thresholds or progress are changed.
Leadership passes before a defeated leader leaves. The conversion effect touches
only its target's wars; it does not peace out the remaining members. All 120
defeat orders, including Croatia first, pass the script model.

## 11–12. Defeat flags and final trigger

The five Serbia-side flags are:

```text
MSGA_montenegro_defeated
MSGA_macedonia_defeated
MSGA_albania_defeated
MSGA_slovenia_defeated
MSGA_croatia_defeated
```

Each is written only after the corresponding real-capitulation record and
successful Serbian puppet transition. Final success requires all five flags
AND all five countries still existing as Serbian subjects, with real
capitulation evidence and no hostile war with Serbia. It then sets
`MSGA_balkan_coalition_defeated` and queues `.11` once. Capital flags, Croatia
alone, three defeats or loss of Pact leadership cannot satisfy it. The final
check runs through the active observer, normally within one day of the last
capitulation. No subsequent focus tree is created.

## 13. Artwork

The ten exact 474×178 DDS and the supplied
`interface/MSGA_balkan_war_eventpictures.gfx` were installed from
`MSGA_Balkan_War_Capital_and_Capitulation_Event_Assets.zip` without conversion or
generic substitutions. The manifest records ZIP member names and SHA-256 hashes.
Each country's capital and surrender event resolves to its correct supplied
sprite. `.11` reuses the supplied Croatian capitulation picture. Pillow decodes
all textures; sprite existence, dimensions, DDS headers and asset hashes pass.
Actual event-window rendering and absence of pink textures await the engine test.

## 14. Installed validation results

All eight validators ran against the actual runtime folder:

| Validator | Report | Result |
|---|---|---|
| Phase 1/global scripts, IDs, localisation, DDS | [phase1](pact_war_regression_phase1.json) | Passed |
| Kosovo campaign | [kosovo](pact_war_regression_kosovo.json) | Passed |
| Reconstruction/vehicles | [post_kosovo](pact_war_regression_post_kosovo.json) | Passed |
| Bosnia/native guards | [bosnia](pact_war_regression_bosnia.json) | Passed |
| Kosovo→Bosnia transition | [transition](pact_war_regression_transition.json) | Passed |
| Post-Bosnia/100-day choice | [post_bosnia](pact_war_regression_post_bosnia.json) | Passed; 24 scenarios |
| Pre-war Pact | [encirclement](pact_war_regression_encirclement.json) | Passed; 96 scenarios |
| New wartime events | [pact_war](pact_war_validation.json) | Passed; 526 scenarios |

The new model executes the installed AST, covering 120 capitulation orders ×
three Serbian-side winners, 120 capital orders with recapture/expiry, unrelated
occupiers, already-capitulated targets, missing campaign/proof, duplicate
callbacks, unrelated-war preservation, observer recovery, capitulation without
capital events, external-peace observer termination and strict final subjects.
Ownership, cores and model surviving armies are unchanged. Normal capitulation
is supplied as an external input; this is not a combat or peace-conference
simulation. The runtime descriptor and all 279 file hashes match the repository.

## 15. Technical limits and the reserved engine test

- The installed engine's targeted autonomy API cancels **all non-civil wars of
  the converted country**, rather than one selected war ID. It leaves all other
  countries' unrelated wars intact. The approved war begins with peaceful
  candidates; this limitation matters if an enemy starts another war later.
- Engine restoration of a capitulated puppet, all-majors peace-conference timing,
  auto-call behaviour, surviving-unit internment, rendering and serialized save
  recovery are not certified by the script model. These are the priority checks
  for the user's controlled wartime test.
- A small country's capital may naturally account for enough victory points to
  produce a normal engine capitulation. The system does not prevent or force
  that outcome just to show a separate capital popup. If it is already
  capitulated when scanned, only the surrender notification is appropriate.
- A previously annexed/deleted Pact member from the old native handler cannot be
  repaired without introducing ownership reconstruction outside this task.
  Use a pre-capitulation save or a fresh campaign for the full chain.
- The inspected `game.log`/`error.log` came from the 19:17–19:23 game launch,
  before the 20:53 live deployment on 2026-10-05. They contain no entries for
  the new namespace/assets, but cannot certify a fresh error-free 0.12 launch.
  No logs were cleared or copied into Git.
- The running game still has its already-loaded scripts. Restart manually when
  ready to test; the user explicitly reserved gameplay and the active campaign
  was left untouched.
