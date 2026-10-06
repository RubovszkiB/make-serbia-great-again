# Serbian Economic Cooperation and Energy Development — installed 2026-10-06

The active HOI4 mod contains 19 permanent projects, 18 repeatable programmes and eight narrative milestones. They unlock with **A Recovery Made in Serbia** (`MSGA_serbian_recovery` or its existing completion flag); the unlock persists across later focus-tree transitions. Existing campaign files, focus layout, rewards and artwork were not changed by this additive increment. Bor and Jadar each award **+3 steel and +2 tungsten**, as requested, using real native resource IDs.

The two exact category IDs are `MSGA_serbian_economic_cooperation` and `MSGA_serbian_energy_development`. Programme names identify domestic, Chinese, Russian or European cooperation. No additional currency, focus tree, GUI, influence system or diplomatic minigame was introduced.

## Permanent projects

Each completes once. Costs are paid on activation; ownership/control loss or an invalid native building condition cancels and refunds the paid cost exactly once. **The targeted 2026-10-06 bugfix replaced expiring project reservations with persistent pending/busy flags, explicitly released on completion or cancellation.** Completion uses separate final safety triggers, grants rewards before setting done, and logs building commands with `[MSGA ECON]`. Cancelled projects may be retried. Only native 2020 Serbian states **45, 107, 108 and 1296** qualify; later conquests and subjects never expand that whitelist.

| Decision ID | State | Treasury ($B) | PP | Days | Native reward / prerequisite |
|---|---:|---:|---:|---:|---|
| `MSGA_expand_bor_mining_complex` | 108 | 0.5 | 0 | 120 | +3 Steel, +2 Tungsten; +1 Infrastructure below level 5 (otherwise +1 shared building slot); Industrial Development +0.05. |
| `MSGA_develop_jadar_mining_project` | 1296 | 0.5 | 0 | 120 | +3 Steel, +2 Tungsten, +1 shared building slot and Industrial Development +0.05. |
| `MSGA_serbian_mineral_processing_expansion` | 1296 | 0.5 | 0 | 120 | +1 Civilian Factory and +1 shared building slot; Industrial Development +0.03. |
| `MSGA_central_serbian_industrial_park` | 1296 | 0.5 | 0 | 90 | +1 Civilian Factory and +1 shared building slot around Kragujevac; Industrial Development +0.03. |
| `MSGA_southern_serbian_industrial_development` | 108 | 0.5 | 0 | 90 | +1 shared building slot and Industrial Development +0.03 around Nis. Complements the earlier southern factory investment. |
| `MSGA_morava_logistics_development` | 1296 | 0.4 | 0 | 120 | +1 Infrastructure and +1 shared building slot; Industrial Development +0.025. Requires room below the native infrastructure cap of 5. |
| `MSGA_modernise_serbian_power_grid` | 107 | 0.4 | 0 | 60 | +1 Infrastructure below level 5 (otherwise +1 shared building slot); Industrial Development +0.025. For 180 days: Construction Speed +5%, Power Plant and Infrastructure Construction Speed +10%. |
| `MSGA_modernise_nikola_tesla_complex` | 1296 | 0.5 | 0 | 90 | +1 Power Plant and +1 shared building slot in the Obrenovac region; Industrial Development +0.025. |
| `MSGA_expand_kostolac_energy_complex` | 108 | 0.5 | 0 | 90 | +1 Power Plant and +1 shared building slot; Industrial Development +0.025. Native TFR rules make this incompatible with Bor renewable generation in Morava. |
| `MSGA_upgrade_djerdap_power_system` | 108 | 0.4 | 0 | 75 | +2 native Energy resource from existing hydroelectric generation; +1 Infrastructure below level 5 (otherwise +1 shared building slot); Industrial Development +0.025. No additional Energy Farm is granted. |
| `MSGA_develop_bor_renewable_complex` | 108 | 0.5 | 0 | 120 | +1 Energy Farm and +1 shared building slot; Industrial Development +0.03. Native TFR rules make this incompatible with a Kostolac Power Plant in Morava. |
| `MSGA_expand_bor_renewable_complex` | 108 | 0.6 | 0 | 120 | +1 additional Energy Farm and +1 shared building slot; Industrial Development +0.025. This is the final scripted Energy Farm. Requires `MSGA_develop_bor_renewable_complex`. |
| `MSGA_establish_serbian_solar_manufacturing` | 45 | 0.5 | 0 | 90 | +1 Civilian Factory and +1 shared building slot in Vojvodina; Industrial Development +0.03. No Energy Farm is granted. |
| `MSGA_develop_grid_scale_storage` | 107 | 0.4 | 0 | 90 | Permanent Factory Energy Consumption -3%; Industrial Development +0.025. Uses native efficiency rather than a new storage currency. |
| `MSGA_seek_russian_nuclear_expertise` | country | 0.2 | 50 | 60 | One 50% nuclear research bonus; Academic Development +0.05. Unlocks the nuclear programme and technical assistance; grants no reactor. |
| `MSGA_establish_serbian_nuclear_programme` | country | 0.5 | 0 | 120 | One 50% nuclear research bonus; Academic Development +0.05; Research Speed +3% for 365 days. Unlocks workforce training; grants no reactor. Requires `MSGA_seek_russian_nuclear_expertise`. |
| `MSGA_train_serbian_nuclear_workforce` | country | 0.3 | 0 | 90 | One 50% nuclear research bonus; Academic Development +0.05. Unlocks construction after native reactor technology is researched. Requires `MSGA_establish_serbian_nuclear_programme`. |
| `MSGA_first_serbian_nuclear_power_plant` | 45 | 1.5 | 0 | 180 | +1 Nuclear Reactor and +1 shared building slot in Vojvodina; Industrial Development +0.05. Requires $nuclear_reactors$ technology and no incompatible energy building. Requires `MSGA_train_serbian_nuclear_workforce`. Requires `nuclear_reactors`. |
| `MSGA_expand_serbian_nuclear_programme` | 45 | 1.5 | 0 | 180 | +1 additional Nuclear Reactor and +1 shared building slot in Vojvodina; Industrial Development +0.025. Requires $nuclear_reactors2$ technology; this is the final scripted reactor. Requires `MSGA_first_serbian_nuclear_power_plant`. Requires `nuclear_reactors2`. |

## Repeatable programmes

All benefits last **180 days**, followed by a **70-day gap**: renewal is possible on day 250. The same programme cannot stack with itself. Each activation costs **$0.2B**, except European Development Grants, which costs **50 PP and no Treasury**. Foreign partners must exist and be at peace with Serbia. Nuclear technical assistance additionally requires Russian nuclear expertise. AI programmes require a Treasury reserve; native Energy shortage increases energy-project priority.

| Decision ID | Partner | Native modifiers |
|---|---|---|
| `MSGA_industrial_efficiency_programme` | domestic | `production_factory_efficiency_gain_factor = 0.075`, `industrial_capacity_factory = 0.025` |
| `MSGA_subsidise_serbian_manufacturers` | domestic | `industrial_capacity_factory = 0.05` |
| `MSGA_infrastructure_investment_programme` | domestic | `production_speed_buildings_factor = 0.05`, `production_speed_infrastructure_factor = 0.1` |
| `MSGA_support_serbian_businesses` | domestic | `business_value_factor = 0.04`, `income_growth_factor = 0.005` |
| `MSGA_chinese_industrial_cooperation` | china | `industrial_capacity_factory = 0.05`, `production_speed_industrial_complex_factor = 0.05` |
| `MSGA_chinese_mining_expertise` | china | `local_resources_factor = 0.1`, `industrial_development_monthly = 0.0025` |
| `MSGA_chinese_infrastructure_cooperation` | china | `production_speed_buildings_factor = 0.075`, `production_speed_infrastructure_factor = 0.1` |
| `MSGA_chinese_technology_transfer` | china | `research_speed_factor = 0.03`, `industrial_development_monthly = 0.0025` |
| `MSGA_russian_energy_cooperation` | russia | `factory_energy_consumption = -0.03`, `industrial_capacity_factory = 0.03` |
| `MSGA_russian_heavy_industry_cooperation` | russia | `production_factory_efficiency_gain_factor = 0.05`, `production_speed_arms_factory_factor = 0.05` |
| `MSGA_russian_technological_assistance` | russia | `research_speed_factor = 0.02`, `industrial_development_monthly = 0.0025` |
| `MSGA_european_development_grants` | europe | `business_value_factor = 0.025`, `society_development_monthly = 0.002`, `industrial_development_monthly = 0.002` |
| `MSGA_european_industrial_standards` | europe | `production_factory_efficiency_gain_factor = 0.05`, `industrial_capacity_factory = 0.03` |
| `MSGA_european_technology_partnership` | europe | `research_speed_factor = 0.03`, `academic_development_monthly = 0.0025` |
| `MSGA_european_business_cooperation` | europe | `business_value_factor = 0.05`, `income_growth_factor = 0.005` |
| `MSGA_chinese_renewable_technology_transfer` | china | `production_speed_energy_farm_factor = 0.125`, `production_speed_buildings_factor = 0.03`, `industrial_development_monthly = 0.0025` |
| `MSGA_renewable_energy_subsidies` | domestic | `production_speed_energy_farm_factor = 0.15`, `industrial_development_monthly = 0.0025` |
| `MSGA_russian_nuclear_technical_assistance` | russia | `production_speed_nuclear_reactor_factor = 0.125`, `research_speed_factor = 0.02`, `academic_development_monthly = 0.0025` |

## Native implementation and deliberate fallbacks

Installed TFR scripts are authoritative. Treasury uses `income_var_temp` with `add_income`; development uses `industrial_development_var_temp` / `academic_development_var_temp` and their corresponding native effects. No inflation or national debt is added by this system.

Physical buildings are `infrastructure` (native cap 5), `industrial_complex`, `power_plant` (cap 4), `energy_farm` (cap 4) and `nuclear_reactor` (cap 2). Each granted shared-slot building also grants one slot. Energy projects call `update_power_plants_effect`. There are at most **two scripted grants of each energy building type** across the system. Nuclear stages use native `nuclear` research bonuses and require `nuclear_reactors` / `nuclear_reactors2` for the first / second actual reactor.

The installed map places Bor, Kostolac, Djerdap and Nis together in Morava (108); Jadar, Obrenovac and Kragujevac are in Sumadija (1296). Belgrade is 107 and Vojvodina is 45. **As the user selected, Kostolac thermal generation and Bor renewables remain native alternatives in state 108.** Conflicting energy types are blocked before payment and checked again on completion, preserving TFR's existing exclusivity rather than deleting a completed alternative.

There is no separate native copper/lithium resource; the latest user instruction selects steel/tungsten instead. Djerdap upgrades existing hydro output with **+2 native `coal`**, displayed by TFR as Energy, without adding a third Energy Farm or a custom hydro building. Grid storage uses permanent **`factory_energy_consumption = -0.03`** rather than a new meter/building. Infra projects at cap use an explicit shared-slot fallback where specified; Morava logistics requires room under the cap. Neither France nor a French nuclear branch was added.

## Milestones and supplied images

All eight events are narrative only, with one option and persistent queued/seen flags; project effects hold the rewards. Industrial Revival follows any three of the six permanent economic projects.

| Event | Title | Supplied image |
|---|---|---|
| `MSGA_econ.1` | A New Economic Strategy for Serbia | `MSGA_event_infrastructure_strategy_meeting.dds` |
| `MSGA_econ.2` | The Morava Corridor Takes Shape | `MSGA_event_highway_rail_renaissance.dds` |
| `MSGA_econ.3` | The Bor Expansion | `MSGA_event_mining_expansion.dds` |
| `MSGA_econ.4` | Serbian Industrial Revival | `MSGA_event_industrial_revival.dds` |
| `MSGA_energy.1` | Powering Serbia's Future | `MSGA_event_energy_modernisation_briefing.dds` |
| `MSGA_energy.2` | A Renewable Partnership with China | `MSGA_event_chinese_renewable_partnership.dds` |
| `MSGA_energy.3` | The Nuclear Question | `MSGA_event_russian_nuclear_briefing.dds` |
| `MSGA_energy.4` | Serbia Enters the Nuclear Age | `MSGA_event_first_serbian_nuclear_plant.dds` |

The supplied `MSGA_Economic_Energy_Visuals.zip` provides all artwork. Individual illustrated motifs were cropped from the two concept boards, excluding printed board labels and numbers. Exports follow inspected installed formats: 37 decision DDS at 52×45 DXT5, 21 spirit DDS at 64×64 DXT5, two category DDS at 52×40 DXT5 and eight event DDS at 500×250 DXT3. Event images are fitted/cropped without stretching. All 68 textures have unique resolved sprites; no generic replacement/fallback image is used. Exported icon and event contact sheets were visually inspected. Existing user artwork remains byte-identical.

## Deployment and validation

The targeted lifecycle/icon correction is recorded in `economic_energy_bugfix_sync.json`, with current installed hashes and 40 changed runtime paths. Only `validate_economic_energy.py` was rerun for that correction; it verifies parsed commands, persistent flags, release/refund, 19 delayed callbacks, 13 reachable building/infrastructure grants and icon formats/paths. The older ten-suite results below describe the initial increment. Actual engine building delivery still requires the user's test. Category, spirit and event textures remain unchanged; 37 decision crops were tightened and centred with aspect preserved inside the existing 52×45 DXT5 canvas. The generator reproduces this composition.

Primary installation: `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`. Its sibling launcher descriptor points to this exact directory and retains Workshop identity **3813570241**. All **397** source/runtime files match byte-for-byte; all previous **320** runtime files are unchanged by this increment.

All ten installed-mod validators passed: phase1, Kosovo, post-Kosovo, Bosnia, transition, post-Bosnia, encirclement, Pact war, New Balkan Order and the new economic/energy validator. These check parsed syntax, external IDs/modifiers/localisation, supplied artwork, source/runtime preservation, cost/timing, both mining resource grants, chain/technology gates, cancellation/refund/retry, native energy alternatives and building ceilings, and milestone idempotency. They do **not** certify engine gameplay, decision rendering or save/load. The user explicitly reserved the game test; no game window or save was touched.

Historical validation expectations were updated for the previously approved visual pack and already-installed peace/progression fixes, using exact approved digests/archive bytes in `approved_runtime_changes.json`. The game implementations of those prior fixes were not changed by this increment. Old historical source/deployment records retain their original meaning.

Exact native sources, artwork crops/formats/hashes, all project/programme values and all **77 newly installed paths** are in `economic_energy_sources.json`. All absolute runtime paths and 397 hashes, descriptor checks and ten validator report paths are in `economic_energy_sync.json`.

## New runtime files

- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\decisions\MSGA_economic_energy_decisions.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\decisions\categories\MSGA_economic_energy_categories.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\ideas\MSGA_economic_energy_ideas.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\on_actions\MSGA_economic_energy_on_actions.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\scripted_effects\MSGA_economic_energy_effects.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\common\scripted_triggers\MSGA_economic_energy_triggers.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\events\MSGA_economic_energy_events.txt`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_chinese_renewable_partnership.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_energy_modernisation_briefing.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_first_serbian_nuclear_plant.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_highway_rail_renaissance.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_industrial_revival.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_infrastructure_strategy_meeting.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_mining_expansion.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\event_pictures\MSGA_event_russian_nuclear_briefing.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_central_serbian_industrial_park.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_chinese_industrial_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_chinese_infrastructure_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_chinese_mining_expertise.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_chinese_renewable_technology_transfer.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_chinese_technology_transfer.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_develop_bor_renewable_complex.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_develop_grid_scale_storage.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_develop_jadar_mining_project.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_development_category_0.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_development_category_1.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_establish_serbian_nuclear_programme.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_establish_serbian_solar_manufacturing.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_european_business_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_european_development_grants.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_european_industrial_standards.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_european_technology_partnership.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_expand_bor_mining_complex.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_expand_bor_renewable_complex.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_expand_kostolac_energy_complex.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_expand_serbian_nuclear_programme.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_first_serbian_nuclear_power_plant.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_industrial_efficiency_programme.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_infrastructure_investment_programme.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_modernise_nikola_tesla_complex.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_modernise_serbian_power_grid.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_morava_logistics_development.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_renewable_energy_subsidies.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_russian_energy_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_russian_heavy_industry_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_russian_nuclear_technical_assistance.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_russian_technological_assistance.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_seek_russian_nuclear_expertise.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_serbian_mineral_processing_expansion.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_southern_serbian_industrial_development.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_subsidise_serbian_manufacturers.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_support_serbian_businesses.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_train_serbian_nuclear_workforce.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\decisions\MSGA_upgrade_djerdap_power_system.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_chinese_industrial_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_chinese_infrastructure_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_chinese_mining_expertise.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_chinese_renewable_technology_transfer.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_chinese_technology_transfer.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_european_business_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_european_development_grants.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_european_industrial_standards.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_european_technology_partnership.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_grid_modernisation_bonus.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_grid_scale_storage_network.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_industrial_efficiency_programme.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_infrastructure_investment_programme.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_nuclear_programme_research.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_renewable_energy_subsidies.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_russian_energy_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_russian_heavy_industry_cooperation.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_russian_nuclear_technical_assistance.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_russian_technological_assistance.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_subsidise_serbian_manufacturers.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\gfx\interface\ideas\MSGA_support_serbian_businesses.dds`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\interface\MSGA_economic_energy_assets.gfx`
- `C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again\localisation\english\MSGA_economic_energy_l_english.yml`
