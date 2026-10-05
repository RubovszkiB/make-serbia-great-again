# New Balkan Order — 0.13.0 implementation and installed validation

Implemented directly in the primary runtime, then checked there before source sync. The user's running HOI4 campaign was left untouched. This report records script/static and deterministic-model results; engine acceptance remains pending the user's test.

## 1. Changed and deployed files

Primary runtime: `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again`. Exactly 46 mod files were written: 41 additions and five existing-file updates, plus the sibling launcher descriptor. Existing updates are the decision-category append, the single Pact-victory scheduling hook, the single old-planning-entry guard, and both mod descriptors. Existing focus layouts, history, division templates, native guard copies and TFR files remain unchanged. The full absolute deployment list is below; hashes and original 0.12 baselines are in [new_order_sources.json](new_order_sources.json). Backups are ignored under `logs/new_order_013_backup`.

```text
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\decisions\MSGA_new_order_decisions.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\decisions\categories\MSGA_SER_categories.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\ideas\MSGA_new_order_ideas.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\national_focus\MSGA_SER_new_balkan_order.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\on_actions\MSGA_new_order_on_actions.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\opinion_modifiers\MSGA_new_order_opinions.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\scripted_effects\MSGA_encirclement_effects.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\scripted_effects\MSGA_new_order_effects.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\scripted_effects\MSGA_pact_war_effects.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\scripted_triggers\MSGA_new_order_triggers.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\descriptor.mod
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\events\MSGA_new_order_events.txt
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_belgrade_opens_for_business.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_arteries_of_serbia.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_balkans_stabilise.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_bill_comes_due.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_conference_of_belgrade.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_furnaces_burn_again.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_ljubljana_protocol.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_new_balkan_order.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_podgorica_settlement.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_reconstruction_authority.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_sarajevo_framework.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_skopje_agreement.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_south_slavic_question_returns.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_tirana_arrangement.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_the_zagreb_accords.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_victory_in_the_balkan_war.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_begin_reconstruction.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_count_the_cost.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_repair_the_roads_and_railways.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_restart_serbian_commerce.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_restore_serbian_industry.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_south_slavic_unity.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_stabilise_the_new_order.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\goals\MSGA_focus_the_south_slavic_question.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_decision_consolidate_the_serbian_sphere.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_idea_a_stabilised_balkan_order.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_idea_the_cost_of_victory.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_idea_the_cost_of_victory_ii.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_idea_the_cost_of_victory_iii.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_idea_the_cost_of_victory_iv.dds
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\interface\MSGA_new_balkan_order_assets.gfx
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\interface\MSGA_new_order_engine_aliases.gfx
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\localisation\english\MSGA_new_order_l_english.yml
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\make_serbia_great_again.mod
C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again.mod
```

## 2. Events

Namespace: `MSGA_neworder`. All 18 visible events are triggered only and fire once. `.90` revalidates delayed victory; `.91` revalidates the conference. Both hidden dispatchers can retry.

| Event ID | Title | Picture |
|---|---|---|
| `MSGA_neworder.1` | Victory in the Balkan War | `GFX_MSGA_event_victory_in_the_balkan_war` |
| `MSGA_neworder.2` | The Bill Comes Due | `GFX_MSGA_event_the_bill_comes_due` |
| `MSGA_neworder.3` | The Reconstruction Authority | `GFX_MSGA_event_the_reconstruction_authority` |
| `MSGA_neworder.4` | The Arteries of Serbia | `GFX_MSGA_event_the_arteries_of_serbia` |
| `MSGA_neworder.5` | The Furnaces Burn Again | `GFX_MSGA_event_the_furnaces_burn_again` |
| `MSGA_neworder.6` | Belgrade Opens for Business | `GFX_MSGA_event_belgrade_opens_for_business` |
| `MSGA_neworder.7` | The Zagreb Accords | `GFX_MSGA_event_the_zagreb_accords` |
| `MSGA_neworder.8` | The Ljubljana Protocol | `GFX_MSGA_event_the_ljubljana_protocol` |
| `MSGA_neworder.9` | The Podgorica Settlement | `GFX_MSGA_event_the_podgorica_settlement` |
| `MSGA_neworder.10` | The Skopje Agreement | `GFX_MSGA_event_the_skopje_agreement` |
| `MSGA_neworder.11` | The Tirana Arrangement | `GFX_MSGA_event_the_tirana_arrangement` |
| `MSGA_neworder.12` | The Sarajevo Framework | `GFX_MSGA_event_the_sarajevo_framework` |
| `MSGA_neworder.13` | The Conference of Belgrade | `GFX_MSGA_event_the_conference_of_belgrade` |
| `MSGA_neworder.14` | The Balkans Stabilise | `GFX_MSGA_event_the_balkans_stabilise` |
| `MSGA_neworder.15` | The South Slavic Question Returns | `GFX_MSGA_event_the_south_slavic_question_returns` |
| `MSGA_neworder.16` | The New Balkan Order | `GFX_MSGA_event_the_new_balkan_order` |
| `MSGA_neworder.17` | The Herzegovinian Framework | `GFX_MSGA_event_the_sarajevo_framework` |
| `MSGA_neworder.18` | The Banja Luka Protocol | `GFX_MSGA_event_question_of_republika_srpska` |

## 3. Focus IDs and layout

One compact eight-focus tree, `MSGA_SER_new_balkan_order`, totals 105 focus-days. Count → Begin → three independent economic focuses → Stabilise → Question → Unity. Each economic prerequisite of Stabilise is a separate prerequisite block, requiring all three.

| Focus ID | Days |
|---|---:|
| `MSGA_count_the_cost` | 7 |
| `MSGA_begin_reconstruction` | 7 |
| `MSGA_repair_the_roads_and_railways` | 14 |
| `MSGA_restore_serbian_industry` | 14 |
| `MSGA_restart_serbian_commerce` | 14 |
| `MSGA_stabilise_the_new_order` | 14 |
| `MSGA_the_south_slavic_question` | 21 |
| `MSGA_south_slavic_unity` | 14 |

Entry requires `MSGA_balkan_coalition_defeated`, `MSGA_pact_all_five_subjects`, Serbian peace and no previous new-order victory. The existing all-five trigger verifies every individual defeat flag, real-capitulation proof, existence and Serbian subject status. The victory event follows three days of qualifying peace. A new war clears the readiness timestamp; queued events revalidate. Startup/weekly/peace callbacks recover missed scheduling. No capital-capture shortcut exists.

The previous `MSGA_open_pact_planning` effect lacked a terminal guard: clearing its active flag on postwar entry could reopen the old tree during startup. Its limit now additionally requires `NOT = { has_country_flag = MSGA_balkan_war_victory }`. Exact AST comparison verifies that this is its only change.

## 4. Native TFR debt mechanism

Installed `common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt` defines `add_debt`: it adds `debt_var_temp` to `debt_var`, calls native GDP checks and updates displayed debt units. Native localisation labels the temporary value in billions. This API adds nominal debt directly. The separate inflation-adjusted API is intentionally unused.

## 5. Exact additional $15B

```text
set_temp_variable = { var = debt_var_temp value = 15 }
add_debt = yes
```

`MSGA_start_new_balkan_order` sets `MSGA_balkan_war_victory` before rewards, blocking duplicates. It grants +10% stability and 100 PP, loads the new tree and removes only six MSGA wartime Serbian spirits. Treasury is unchanged. Count the Cost grants 25 PP and its narrative event, without charging debt again. Later recovery/stabilisation never repays this debt; ordinary TFR economy ticks can still change it.

## 6. Cost of Victory stages

Each stage has exactly these five modifiers. Fractions are native engine/TFR values, e.g. `0.30`, not `30`. Zero values are explicit.

| Spirit ID | Consumer goods factor | Construction speed | Factory output | Native monthly income growth | Industrial repair |
|---|---:|---:|---:|---:|---:|
| `MSGA_cost_of_victory_i` | +30% | -20% | -5% | -5% | +10% |
| `MSGA_cost_of_victory_ii` | +20% | -15% | -3% | -3% | +15% |
| `MSGA_cost_of_victory_iii` | +10% | -10% | +0% | -2% | +10% |
| `MSGA_cost_of_victory_iv` | +5% | -5% | +0% | +0% | +5% |

Modifier keys: `consumer_goods_factor`, `production_speed_buildings_factor`, `industrial_capacity_factory`, `income_growth_factor`, `industry_repair_factor`.

## 7. Reconstruction progress

`MSGA_reconstruction_progress` is initialised to zero and recomputed from the three permanent `MSGA_completed_<economic-focus>` flags. `MSGA_refresh_new_order_reconstruction` removes all four stages before adding the appropriate one. Stable status prevents reintroduction. Begin plus each of the three economic focuses uses native `industrial_development_var_temp = 0.05` with `add_industrial_development = yes`: 20 total percentage points of native progress, subject to TFR's own level/cap logic.

## 8. Order independence and economic rewards

All six permutations were tested. Zero/one/two/three economic completions select I/II/III/IV; rewards are guarded against duplicates.

- Begin: +5 progress points and +10% repair authority for 120 days, ending early at stabilisation.
- Roads: capped +1 infrastructure in native Serbian states 45 Vojvodina, 107 Belgrade and 1296 Sumadija, only when owned and fully controlled; two existing Serbian rail paths rise to at least level three. Paths are `619 3617 11580 11586` and `9602 6634 11583 11586`, verified in native `map/railways.txt`. Higher levels are preserved.
- Industry: one `industrial_complex`, one `arms_factory` and two shared slots in controlled Belgrade, with controlled-Serbian-state fallback.
- Commerce: one native `office_park`, one slot and permanent `business_value_factor = 0.05`, `income_growth_factor = 0.03`.

## 9. Subject decisions

The category opens after Begin Reconstruction. Each decision is visible only for a current existing Serbian client without its completion flag. Native `remove_effect` applies rewards after ten days. A departed/deleted target cancels without rewards or completion; the initial administrative PP cost is retained. Completing a decision permanently hides it through its flag.

| Client | Decision | Serbian completion flag | Event |
|---|---|---|---|
| `CRO` | `MSGA_regularise_croatia` | `MSGA_croatia_regularised` | `MSGA_neworder.7` |
| `SLV` | `MSGA_regularise_slovenia` | `MSGA_slovenia_regularised` | `MSGA_neworder.8` |
| `MNT` | `MSGA_regularise_montenegro` | `MSGA_montenegro_regularised` | `MSGA_neworder.9` |
| `MAC` | `MSGA_regularise_macedonia` | `MSGA_macedonia_regularised` | `MSGA_neworder.10` |
| `ALB` | `MSGA_regularise_albania` | `MSGA_albania_regularised` | `MSGA_neworder.11` |
| `BOS` | `MSGA_regularise_bosnia` | `MSGA_bosnia_regularised` | `MSGA_neworder.12` |
| `HRZ` | `MSGA_regularise_herzegovina` | `MSGA_herzegovina_regularised` | `MSGA_neworder.17` |
| `SRP` | `MSGA_regularise_srpska` | `MSGA_srpska_regularised` | `MSGA_neworder.18` |

## 10. Only one process at a time

All eight decisions require `MSGA_regularisation_free`, checking shared `MSGA_regularisation_active`. Activation sets that shared flag and an owner-specific `MSGA_regularising_<client>` lease. Completion/cancellation releases the shared lock only while the matching owner lease exists. An old callback therefore cannot release a newer country's lock. Fallback leases last eleven days, deliberately outliving the native ten-day completion tick; ordinary completion still unlocks exactly on day ten. A lost native job cannot leave a permanent lock.

## 11. Exact price and duration

Every decision has `cost = 25` and `days_remove = 10`. PP is charged by the native decision system once on activation; the script adds no second charge. Eleven-day fallback leases are safety expiry, not decision duration.

## 12. Regularisation flags

All flags listed in section 9 belong to Serbia, never the subject. Each subject's stability/opinion/autonomy effects are scoped explicitly to that subject's tag. They grant +10% stability, +25 opinion of Serbia and a 50-point autonomy-score reduction.

## 13. Dynamic Bosnia/Herzegovina

`BOS` and `HRZ` each require their own process while they exist as Serbian subjects. A combined Bosnian state with no separate HRZ requires only Bosnia. Nonexistent or no-longer-Serbian subjects do not block the gate. The system preserves the existing territory and tags; it does not construct a new combined state.

## 14. Srpska

An existing Serbian `SRP` subject receives its own Banja Luka process and event, reusing the approved Srpska question picture. Previously annexed Srpska is skipped. The existing 100-day question/annexation mechanism, templates and Serbian-command regional formations remain unchanged.

## 15. Native autonomy APIs

Regularisation executes `add_autonomy_score = { value = -50 localization = MSGA_regularisation_autonomy_tt }` in the subject country. Current shipped engine documentation and native game examples define this API. It does not change autonomy tier, annex a tag or transfer territory. Stabilisation additionally applies `autonomy_gain_global_factor = -0.10` through `MSGA_stabilised_client_order` on each relevant subject. The modifier belongs on subjects; placing it solely on independent Serbia would not reduce their gain. The helper cancels if the administration stops being a Serbian subject.

## 16. Conference of Belgrade

`MSGA_belgrade_conference_ready` requires Serbian peace, victory, Begin Reconstruction, every current client's completed process and no previous sphere-regularisation flag. A hidden dispatcher delays the event by two days and checks again. The event grants +5% stability, 50 PP and `MSGA_serbian_sphere_regularised`.

The request's dedicated automatic-conference section schedules it 1–2 days after all client processes. That specific rule is followed even when economic reconstruction is still running. The later combined economic/political gate remains on Stabilise; political completion cannot bypass it.

## 17. Stabilise gate

`MSGA_new_order_stabilisation_ready` requires victory, Serbian peace, all three economic completion flags, all current-client flags and `MSGA_serbian_sphere_regularised`. It does not depend on Kosovo filler decisions, optional reconstruction decisions, old delayed narratives or unrelated countries. Both economic and political completion orders were tested.

## 18. Stable-order effects

`MSGA_a_stabilised_balkan_order` provides `stability_factor = 0.05`, `political_power_factor = 0.05` and `income_growth_factor = 0.02`. All four penalty stages and the temporary repair authority are removed. Existing commerce benefits remain. Relevant subject administrations receive the -10% autonomy-gain helper; Serbia receives an explanatory custom tooltip. The Balkans Stabilise event fires. Debt remains.

## 19. South Slavic Question

The 21-day focus queues `MSGA_neworder.15`, which sets `MSGA_south_slavic_question_opened`, grants 50 PP and marks each existing Serbian subject among CRO, SLV, MNT, MAC, BOS, HRZ and SRP with `MSGA_south_slavic_question_participant`. Serbia remains the centre. No country is annexed, united, renamed or given cores.

## 20. Albania

ALB participates in client regularisation and receives stable-client administration. It is excluded from all South Slavic candidate flags and remains a separate Serbian client. Both its event and the Question narrative state this boundary.

## 21. Final gateway

The 14-day South Slavic Unity focus requires the Question event's opened flag, grants +5% stability and 50 PP, sets `MSGA_south_slavic_unity_open`, and fires The New Balkan Order (`MSGA_neworder.16`). Implementation stops there. No political-union mechanics, new tags, federation, annexation, core grants or future wars were added.

## 22. Assets and GFX

The supplied ZIP contributes exactly 30 DDS: eight focus icons, five spirit icons, one decision/category icon and sixteen event pictures. All runtime DDS and supplied base GFX are byte-identical to the package. A separate GFX file supplies eight focus shine aliases, five engine national-spirit aliases and one category alias. Eighteen events use the sixteen new pictures plus approved reuses for Herzegovina/Srpska. No ZIP, source sheet, oversized PNG, game log or save is committed.

## 23. Validation and synchronisation

Nine validators passed against the primary installed runtime. [new_order_validation.json](new_order_validation.json) contains 96 complete progression models: all six economic permutations, combined/separate Bosnia-Herzegovina, annexed/separate Srpska, politics-first/economics-first and forward/reverse client ordering. Another 49 negative/timing/cancellation checks cover missing victory proof, war interruption, cost/duration/serial lock, orphan expiry, wrong scope, every missing client flag, building fallback/caps, queued-conference cancellation and preserved debt/territory/armies/subject status.

Eight [new_order_regression_*.json](new_order_regression_pact_war.json) reports preserve earlier content, including 526 Pact-war cases, 96 pre-war cases and 24 post-Bosnia cases. [new_order_sync.json](new_order_sync.json) records all 320 source/runtime files and launcher-path/Workshop-identity equality. Canonical deployment verification and [local_runtime_validation.json](local_runtime_validation.json) follow source sync.

## 24. Technical limitations and user gameplay test

No fresh engine playthrough or clean engine log is certified. Existing logs were inspected read-only: error.log last wrote 2026-10-05 19:23:38 local, game.log 19:22:48; neither contains the new namespace/paths. They predate this chapter's installation and cannot validate it. The user's active campaign was not automated, closed or restarted.

When ready, restart HOI4 manually to load the new scripts. Test normal Pact capitulation and peace → delayed victory/debt → eight-focus recovery, alternate economic orders and parallel ten-day client processes → conference → stabilisation → Question → Unity. Verify UI/DDS rendering, native debt/income/development ticks, actual timer ordering, subject autonomy display and engine save/reload. Already completed old-save focuses do not replay rewards; missing or previously annexed Pact countries are not fabricated to recover an incompatible old save. Native API/AST models establish the scripted dependencies, not engine acceptance.
