# Final early-Serbia cleanup

## Changes

- Recovery already removed `SER_scars_of_bombings_idea` and no COVID spirits. Its existing rewards and `MSGA_recovery_complete` flag remain unchanged; the custom tooltip now uses the exact display name, **Scars Of The Bombings**, and names the removed penalties.
- Restore Defence Production already grants two military factories in state 1296 with two slots and an exclusive controlled-core fallback. Its focus, helper, event, ideas, decisions, flags and costs remain unchanged.
- Added Vulin to TFR's `theorist_minister` cabinet slot. This is a minister idea using the existing `SER_aleksandar_vulin` identity/availability and `GFX_Aleksandar_Vulin` portrait, matching TFR's idea-based cabinet architecture. No character or portrait was duplicated. The sole gameplay trait effect is `experience_gain_army = 0.10`. Startup appoints him once; replacing him does not cause automatic reappointment. Native slot replacement/removal removes the idea's trait effects.
- Secure Strategic Stocks (`MSGA_procure_equipment`) now grants 3,500 `infantry_equipment_1`, 100 `support_equipment`, 50 `artillery_equipment_1` and 150 `motorized_equipment`, all with `producer = SER`, plus its existing 3 army XP. Its 35 PP, 30 days, inflation-adjusted money cost, Russian discount, visibility, availability and one-time flag are unchanged.
- Consolidate the State retains its existing rewards and adds `add_popularity` for `conservative`, amount `0.20`. It sets TFR's existing `SER_belgrade_blues_off_flag` and removes `SER_sps_opposition_dynamic`. Only the Belgrade Blues category uses this visibility flag; other Serbian categories remain intact. A one-day hidden startup repair handles TFR re-adding the SPS modifier after MSGA startup runs, without replaying popularity or appointing a replaced minister.
- COVID, reopening, all other focuses, events, Chronicle, and Kosovo content are unchanged.

## Sources inspected

Installed TFR:

- `history/countries/SER - Serbia.txt`: starting bombings spirit, existing Vulin recruitment, conservative ruling party and starting popularity.
- `common/ideas/TFR_ideas_SER.txt`: bombings penalties are `war_support_factor = -0.1` and `industrial_capacity_factory = -0.15`.
- `common/ideologies/TFR_ideologies.txt`: real `conservative` ideology.
- `common/ideas/TFR_ideas_USA.txt`, `TFR_ideas_ZZZ_generic.txt`, `common/idea_tags/TFR_idea_tags.txt`: native `theorist_minister` slot, minister ideas and character-gated availability.
- `common/characters/TFR_characters_SER.txt`, `interface/TFR_game_rules_flags.gfx`: existing Vulin identity and portrait sprite, referencing `gfx/leaders/SER/Aleksandar_Vulin.png`.
- `common/country_leader/TFR_traits_military_minister.txt`: verified daily army XP token and 0.1 scale.
- `common/decisions/categories/TFR_decision_categories_SER.txt`, `events/TFR_events_SER.txt`, `common/on_actions/TFR_on_actions_SER.txt`, Serbian scripted effects/dynamic modifiers: native Belgrade Blues end flag and SPS penalties.
- Equipment definitions `infantry.txt`, `support.txt`, `artillery.txt`, `motorized.txt`; `common/technologies/artillery.txt`; English equipment localisation: existing Serbian Zastava M70 and Command Equipment IDs; earliest towed artillery is `_1`, enabled by Serbia's starting `gw_artillery` technology.

The previously downloaded [Austria-Hungary reference](https://github.com/RubovszkiB/HOI4-TFR-Austria-Hungary-reborn) was inspected, especially `AHR_royal_ministers.txt`, `AHR_royal_minister_traits.txt`, `AHR_royal_cabinet_effects.txt`, military staff characters and Hungary history. Its custom minister categories and guarded `add_ideas` appointment pattern are retained here.

## Files

Created:

- `make_serbia_great_again/common/country_leader/MSGA_SER_minister_traits.txt`
- `make_serbia_great_again/events/MSGA_SER_cleanup.txt`
- This report.

Modified: `MSGA_SER_phase1.txt` in national focuses and decisions; `MSGA_SER_ideas.txt`; `MSGA_SER_effects.txt`; `MSGA_SER_on_actions.txt`; English localisation; `tools/validate_phase1.py`; generated `docs/phase1_static_validation.json`.

## Validation and genuine limits

The project validator passes, including source-backed IDs, modifier/portrait checks, unique definitions, localisation, syntax and targeted comparisons against commit `51bc3c4`. Those comparisons verify all unrelated focuses and event/COVID scripts are unchanged, existing country ideas are unchanged, defence restoration is identical, and procurement's non-delivery mechanics are identical. The stockpile package has exactly four entries and retains exactly 3 XP. The consolidation popularity effect is exactly 0.20 and is not replayed by startup repair. `git diff --check` passes.

The existing `error.log` was inspected and contains no MSGA references. It predates these edits and cannot validate this increment. No game was launched or installed copy updated; actual rendering, daily XP activation/removal, factory delivery, stockpile delivery and shutdown after save/load remain unverified in game.

The inspected TFR installation references `SER_sps_influence_mission` from `serbia.21`, but defines neither that mission nor any decisions inside Belgrade Blues. Its category and SPS dynamic penalties are real and are resolved using their native mechanisms. No invented mission cancellation or base decision override was added. TFR calls the earliest artillery **Towed Artillery**, rather than **Early Artillery**; the package uses that verified earliest model.
