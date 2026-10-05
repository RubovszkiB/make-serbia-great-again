# Bosnia chapter — 0.8.0

Implemented and deployed to `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`. The sibling launcher descriptor points to that folder and preserves Workshop identity `3813570241`. The project and installed mod contain the same 160 files; the exact changed absolute paths are in [bosnia_files_deployed.json](bosnia_files_deployed.json).

## Progression and rewards

The existing Kosovo integration/reconstruction transition now loads a 13-focus Bosnia chapter. The opening event explicitly attributes its geopolitical claims to the government's revanchist propaganda. Eleven focuses last 35 days, Seed the Rebellion lasts 42 days, and Watch the Conflict lasts 70 days. The final focus provides observation and event routing rather than a statistical reward.

| Focus | Reward / result |
|---|---|
| Start Making Serbia Great Again | Narrative event; +10 PP |
| Start Mobilising Our People | +50 PP, +5% stability; event grants +5% war support |
| Strengthen the National Narrative | +50 PP, +5% stability; narrative event |
| One People Across the Drina | +5% war support, +1% recruitable population |
| Prepare the Nation for War | +5% war support, +10% core division defence; propaganda-ready flag |
| Establish the Territorial Defence | +10 native Military Development, editable template, one Belgrade militia, regional decisions |
| Start the Army Buildup | +10 Military Development; 200-day Rearmament spirit |
| Buy Equipment for the Serbian Air Force | +10 Military Development; paid supplier choice |
| Spend Money on the Command Structure | +10 Military Development; +10% Command Power gain |
| Prepare the Logistics Network | +10 Military Development; 15 trains, 150 utility vehicles |
| Prepare for the Unthinkable | +10 Military Development; +10% war support, Prepared for War; military-ready flag |
| Seed the Rebellion in Bosnia | Both branch endings required; native independent SRP release and three weak militia divisions |
| Watch the Conflict | Requires active BOS–SRP war; opens the territorial-loss intervention monitor after 70 days |

The six military focuses call native `add_military_development` using `military_development_var_temp = 10`: +60 total. Money is charged using native `income_var_temp` and `add_income`, in billions, with treasury checks and zero PP substitution.

Rearmament reduces production cost by 25% for `infantry_equipment`, `light_mechanized_equipment` (APCs), `mechanized_equipment` (IFVs), and `modern_tank_chassis`. The last archetype also covers TFR's legacy `modern_tank_equipment_1`; there is no separate `modern_tank_equipment` archetype. Economic penalties use native `expense_growth_factor = 0.15` and `military_factory_upkeep_factor = 0.05`.

Prepared for War uses `war_stability_factor = 0.06`: the inspected base war penalty changes from -20% to -14%, a 30% reduction. TFR's separate war-support-scaled penalty is preserved. Other modifiers are `max_planning`, `breakthrough_factor`, and `army_attack_factor`, each +5%.

## Territorial Defence and map

Both **Territorial Defence Militia** and **Srpska Guard** start with exactly three plain `militia` battalions, no supports, and no template lock. The references are artwork only; neither template inherits their illustrated tanks or vehicles.

| TFR state | Formation province | Delivery |
|---|---:|---|
| 107 — Belgrade | 11586 | One division from the establishing focus; no repeat decision |
| 45 — Vojvodina | 3617 | $0.5B, 14 days, one-time |
| 108 — Eastern Serbia | 11887 | $0.5B, 14 days, one-time |
| 1296 — Šumadija and Western Serbia | 6998 | $0.5B, 14 days, one-time |
| 785 — Kosovo | 14402 | $0.5B, 14 days, requires completed integration/core |
| 1305 — Northern Kosovo | 14400 | $0.5B, 14 days, requires Serbian core and control |

Decisions require Serbian ownership, core status and complete control. Delivery rechecks those conditions; loss of control refunds the payment instead of spawning outside Serbia. Pending/completed flags prevent repeated delivery or repeated refunds. All provinces were checked against actual TFR state definitions. No map or state-history files were changed and no Hungarian territory is assigned to Serbia.

## Air purchases

| Supplier | Treasury debit | Equipment |
|---|---:|---|
| Russian | $15B | 50 Su-30, 25 Su-24, 50 Mi-24 |
| Chinese | $10B | 40 J-16, 30 Z-10 |

With By Blood Alone, the Su-30 is TFR's existing `ARM` Su-30 variant on `small_plane_airframe_1`: Russia's own starting file labels its Su-30 group as a Su-27 variant, so that mislabeled design is not used. Su-24 uses the existing `SOV` variant on the engine-derived `small_plane_cas_airframe_0`. J-16 uses `PRC`'s existing Shenyang J-16 on `small_plane_airframe_1`. Helicopters use `attack_helicopter_equipment_1` with SOV/PRC provenance, whose native country names are Mi-24P-1M and Changhe Z-10.

Without the aircraft designer DLC, purchases use existing legacy equipment types; named Su-30/J-16 variants identify the corresponding imported fighter platforms. No new equipment definitions are introduced. Insufficient funds allow deferral and a decision to reopen offers. A completed purchase cannot be charged or delivered again. Final military preparation requires the procurement-completed flag.

## Srpska and intervention

Native `BOS = { release = SRP }` releases the existing Srpska core states **848, 849, 850**. Native Milorad Dodik is promoted in the existing social-democratic leader group. The native country history, technologies, characters, capital and politics remain available; only its obsolete `SER_2000` OOB is replaced with an empty custom OOB. The release clears inherited units before loading exactly three supplied Guard formations at 6983, 11741 and 11574, with full basic starting equipment/manpower and low experience.

Bosnia's original four regular divisions include motorised infantry, artillery, APCs/IFVs and a tank formation. They are left unchanged. A deterministic hidden event queues Bosnia's declaration on SRP **15 days after release**. SRP's campaign isolation prevents ordinary faction joining; defensive guarantees on SRP are suspended for the conflict and restored when appropriate.

After Watch the Conflict, a guarded daily hidden observer checks `SRP surrender_progress > 0.02`, an ongoing BOS–SRP war, SRP existence/non-capitulation and Serbia not already fighting Bosnia. The event flag is set before queuing **ANSWER THE CALL OF THE SERBIAN MOTHERLAND**. Its option, **The Drina will no longer divide us.**, calls `add_to_war` with `targeted_alliance = SRP`, `enemy = BOS`, `single_target_only = yes`. No separate Serbian declaration, annexation or puppet is created.

Kosovo and SRP receive dedicated Last Stand ideas: `surrender_limit = 0.24`, `max_surrender_limit_offset = 0.01`. Inspected base surrender limit is 0.80 and TFR's largest low-war-support penalty is -0.05. The resulting threshold is capped at 99% across 0–100% war support, without combat buffs or an unattainable threshold above 100%. Pristina alone is below this threshold when other meaningful Kosovo territory remains. Kosovo's idea is removed by existing campaign cleanup; SRP's is removed on conflict cleanup, peace hooks or startup/weekly recovery. The formula is validated against installed scripts; actual combat capitulation behaviour has not been manually measured.

The custom storyline stops after Serbia joins the war. It contains no Bosnia settlement, partition, integration, annexation or occupation chapter.

## Native compatibility and supplied visuals

Four same-basename overrides live inside MSGA, with no `replace_path` and no physical Workshop edits:

- `events/TFR_events_SER.txt`: gate conflicting native `serbia.3–12`, `15–20`, `23–27`. Domestic/civilian events 13, 14, 21, 22 and Croatia's 28 remain unchanged.
- `common/decisions/TFR_decisions_SER.txt`: gate only the native second-Kosovo-war category and its effect callbacks. Cancel its pending mission on MSGA startup without running conflicting native rewards.
- `common/on_actions/TFR_on_actions_ZZZ_peace.txt`: gate exactly the SRP-vs-BOS, SER-vs-BOS and BOS-vs-SER scripted settlements. All other world-war branches remain unchanged.
- `history/countries/SRP - Republika Srpska.txt`: replace only the starting OOB reference.

These gates use `MSGA_native_balkan_story_allowed`, based on the existing Serbian campaign flag. Native source hashes and asset mappings are recorded in [bosnia_sources.json](bosnia_sources.json). Validation strips only the new guards and compares the remaining AST to installed TFR; a changed upstream hash requires rebasing these overrides.

The supplied archive's manifest, template specification, DDS/PNG files and full preview were inspected. **24 supplied DDS files** are deployed byte-for-byte: thirteen focus icons, four spirit icons, two decision textures and five event pictures. All focus icons include completion-shine definitions. The extra Mobilise the Nation image remains in the source package rather than creating a filler focus.

The requested [Austria-Hungary reference project](https://github.com/RubovszkiB/HOI4-TFR-Austria-Hungary-reborn) was inspected, including its scripted effects, on_actions and European-war events. Its native-war join and scoped restoration patterns informed the checks; its unrelated state assignments and artwork were not copied.

## Validation boundary

All four validators pass against the actual installed mod. Checks cover prior rewards, duplicate IDs, localisations, textures, native API references, state/province scope, exact militia templates/counts, payments, DLC procurement paths, timers, once-only intervention, native guard-only changes and cleanup. The script model tests the actual parsed effects; it does not simulate combat or certify engine save/load.

A fresh HOI4 debug load is recorded in [local_engine_validation.json](local_engine_validation.json). The first load caught a redundant invalid tank bonus; it was removed and the corrected installation was reloaded without new Bosnia parser errors. Existing upstream TFR errors in preserved native scripts are reported separately. The live Serbia campaign then exposed earlier Kosovo effects trying to remove Albania when absent from the NATO member array and removing already-cleared state modifiers during repeated cleanup. Documented `is_in_array` and `has_dynamic_modifier` guards were deployed and checked, including duplicate/absent cases. The user asked to keep the active campaign running, so those last repairs were not verified in another engine restart. The game log confirms Kosovo war, Albanian intervention and Kosovo capitulation, but full Bosnia combat pacing, rendered UI, province spawn placement and engine save/load remain unverified.

Restart HOI4 after deployment. The new tree loads after the existing final post-Kosovo narrative; it is not displayed at the start of an early Serbia campaign. Previously completed focus rewards do not rerun in an old save. Starting a new campaign is the most reliable way to receive every earlier revised reward.
