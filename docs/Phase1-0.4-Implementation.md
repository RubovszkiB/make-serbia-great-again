# Serbia early rewards — 0.4.0

## Implemented scope

All 18 existing focus IDs, names, positions, costs, prerequisites and artwork remain intact. Reopening now requires completed vaccination; Watch the Western Shield can be completed before American collapse; The Kosovo Question requires the resulting collapse report. No war, territorial transfer, ultimatum or later Yugoslavia tree was added.

The project retains its established `MSGA_` object prefix and `MSGA` event IDs to avoid collisions with TFR Serbia and preserve existing references. New event groups are `MSGA_covid`, `MSGA_economy`, `MSGA_politics`, `MSGA_military`, `MSGA_geopolitics` and `MSGA_chronicle`.

## Focus audit

| Existing focus | Completed reward |
|---|---|
| A New Decade | 25 PP, 2% stability, early-game flag, domestic systems, introduction event (5 PP) |
| Contain the Outbreak | Existing generic TFR COVID spirit, response flags, two decisions, arrival event |
| Reopen on Serbian Terms | Vaccination gate; 3% stability, income 30 through TFR API, 180-day output/business surge, Chronicle activation, reopening event |
| Attract Productive Capital | Permanent −2% consumer goods factor, +2% output, +5% Business Value, +2% income growth; event income 12; retained funded projects |
| Modernise Belgrade Services | State 107: five slots, two CIVs, one Office Park; skyline event |
| Develop the Morava Corridor | State 1296: up to two infrastructure levels; event income 12 |
| An Independent Resource Policy | State 107: 10 steel, 5 tungsten, 6 chromium; resource-policy flag; retained mining projects |
| A Recovery Made in Serbia | Removes `SER_scars_of_bombings_idea`; 3% stability, recovery flag, conclusion event |
| Consolidate the State | Permanent +5% PP gain, +3% stability; consolidation flag |
| Manage the Streets | Event choice: measured (+3% stability, −25 PP; 180-day +2% stability/−3% PP gain) or firm (+5% war support, +25 PP; 180-day +5% PP gain/−2% stability) |
| A Presidential Mandate | Upgrades government to +10% PP gain/+5% stability; 50 PP, mandate flag, event |
| Restore Defence Production | Two MILs and slots in 1296; 365-day +5% output/+5% MIL construction; event |
| Modernise the Army | 25 army XP; one 50% doctrine cost discount; permanent +3% organisation/−5% training time |
| Arms for an Uncertain World | 3,000 `infantry_equipment_2`, 400 `support_equipment`, 250 `motorized_equipment`; 10 XP, procurement event |
| Secure the Supply Lines | State 1296 fuel silo and up to one infrastructure; 15,000 fuel; 180-day +5% fuel gain/−5% supply consumption |
| Ready for the Uncertain | Upgrades modernisation to +5% organisation/−5% training time/+10% mobilisation; 5% war support, readiness flag, council event |
| Watch the Western Shield | Monitoring flag, immediate check, then one country-scoped hidden event every 30 days until the report is queued |
| The Kosovo Question | Crisis unlock, existing preparatory studies, opening event and phase-start flag |

State rewards require Serbian ownership and full control. Belgrade/resource/Morava rewards substitute a modest treasury payment when their intended state is unavailable; defence factories use another controlled Serbian core as fallback. Infrastructure additions respect remaining capacity. Funded project decisions remain separate additional investments with their existing ownership/capacity guards and exact refunds.

## Pandemic

Two decisions replace the four custom response measures. Hospital support costs 50 PP and delivers after 35 days: hospital-completion flag, 1% stability, 100-day Emergency Hospital Capacity and `MSGA_covid.2`. Vaccination costs 75 PP, requires completed hospital support and a date after 1 December 2020, and delivers after 35 days: removal of all five generic TFR case spirits, 2% stability, completion flag and `MSGA_covid.3`. Starting a decision records commitment; it does not satisfy the completion gate.

TFR exposes generic case spirits and stepwise `increase_corona`/`decrease_corona` effects, but the inspected Serbia content has no country-specific epidemic escalation timer suitable for a safe 100-day extension. Hospital mitigation therefore uses verified output/construction/stability modifiers for 100 days. It does not edit global epidemic schedules. Containment adds `low_covid_cases` only if no generic case spirit exists and the base spirit's pre-2023 availability window is open. Starting containment after that window still exposes the response sequence without adding an expired spirit.

## Chronicle and Western monitoring

`MSGA_chronicle.1` follows AHR's delayed selector architecture: a pending-timer flag, hidden dispatcher, 120 days plus up to 90 random days, a quiet weight of 35, seven weights of 10, zero-weight eligibility exclusions and 360-day per-story cooldowns. Cooldowns are reserved at selection, before the one-day delayed visible event. Each event rechecks its eligibility before presentation. Recurring stories do not use `fire_only_once`. The dispatcher reschedules only while active. With all seven eligible, the quiet probability is 35/105; with fewer eligible it rises.

Stories cover Belgrade construction, investors (income or timed business bonus), Morava freight, defence exports, student marches (two choices), energy prices (two choices), and a Kosovo boundary incident. The incident only adds 1.5% war support.

The Western observer uses the verified `USA_shattered_union_global`, `USA_american_civil_war_global` and `USA_american_civil_war_over_global` signals. The latter two preserve detection after TFR clears its shattered-union flag. `MSGA_west_event_fired` is set before queuing the visible report, stopping the observer while the option awaits selection. The option grants 5% war support and sets `MSGA_western_shield_cracked`, opening the Kosovo focus. No suitable dedicated global-collapse on-action was found; the 30-day delayed fallback avoids unrestricted daily polling. Existing daily quote updates were moved to weekly updates; project charging/refunds continue to use TFR's inflation API.

Startup restores missing Chronicle/observer scheduling for completed focuses, guarded by saved timer flags. It converts an unfinished legacy custom pandemic to the new response system. Completed focus rewards are not replayed. Old custom ideas, dynamic modifiers and legacy event IDs remain defined for saved queues and ongoing project effects. A new campaign is recommended for the full 0.4 reward sequence.

## Reference evidence

The explicitly requested [Austria-Hungary repository](https://github.com/RubovszkiB/HOI4-TFR-Austria-Hungary-reborn) was inspected at commit `8e4e35f8093f826dc21fafbccb82e3e1cd3eb18e`.

| Reference | Reused pattern |
|---|---|
| AHR `events/AHR_chronicle_events.txt` | Hidden weighted dispatcher, quiet weight, eligibility exclusions, timed cooldowns, rescheduling |
| AHR `common/on_actions/AHR_on_actions.txt` | Startup-only compatibility and pending-timer guards |
| AHR `events/AHR_european_war_events.txt` | Event-driven war detection and limited delayed fallbacks; Serbia uses a delayed collapse observer because its signal is a global flag |
| AHR `common/national_focus/AHR_hungary_focus.txt` | State construction/slots/resources, treasury effects, fuel reserve, doctrine rewards and spirit upgrades |
| AHR `common/ideas/AHR_imperial_ideas.txt`, `AHR_chronicle_ideas.txt` | Business Value, consumer-goods and temporary flavour modifiers |
| AHR `common/scripted_effects/AHR_scripted_effects.txt` | Scripted reward composition and era-appropriate equipment stockpiles |
| AHR development and European-war decisions, triggers, Hungary/war/super events and English localisation | Cost/delivery separation, conditional event chains, guards and visible-text patterns; no unrelated war systems or assets copied |
| TFR `history/countries/SER - Serbia.txt`, `common/ideas/TFR_ideas_SER.txt` | Starting technologies and `SER_scars_of_bombings_idea` |
| TFR states `107-Kosavo.txt`, `1296 - Sumadija and Western Serbia.txt` | Belgrade despite misleading filename; central industrial towns Čačak/Kruševac and infrastructure baseline |
| TFR `common/ideas/TFR_ideas_ZZZ_generic.txt` | Five existing COVID case spirits; confirmed `income_growth_factor` |
| TFR generic scripted effects/triggers | `add_income_with_inflation`, `add_debt_with_inflation`, generic COVID detection and severity effects |
| TFR USA/CAC/USB events and USA scripted effects | American-collapse flags and their clearing/continuation behaviour |
| TFR equipment `infantry.txt`, `support.txt`, `motorized.txt` | Confirmed stockpile IDs; Serbia starts with technologies supporting this package |
| TFR focus API examples including APA/ATW/FPR | `add_doctrine_cost_reduction`, 0.5 reduction, `cat_old_land_doctrine` category |
| TFR ideas AST/BAY/economic laws/gamerules and other idea files | Training, mobilisation, fuel, organisation, supply and construction modifier tokens |

No Serbia-specific MIO was found in the installed organization definitions; no new MIO was introduced. AHR's technology-era doctrine research bonus was adapted to the doctrine cost-discount API present in installed TFR. The engine still documents that effect, but application to the new mastery interface requires in-game verification. Income values use the requested magnitudes directly through TFR's treasury API (its accounting unit is billions); no additional scaling or derived-income writes are introduced.

## Changed files and validation

Created: `common/decisions/MSGA_SER_covid.txt`, `events/MSGA_SER_early_rewards.txt`, `events/MSGA_SER_chronicle.txt`, and this report.

Modified: existing focus, ideas, effects, on-actions, response/development decisions, domestic decisions, events, English localisation, both version descriptors, development notes, README, validator and generated static-validation report. Artwork, TFR and Yugoslavia Reborn files were not modified.

`tools/validate_phase1.py` passes: balanced parse, unique IDs, all event/script/idea/decision references, namespace declarations, localisation and BOM, unchanged artwork pixels, focus graph/layout/cost/title preservation, new availability gates, exact decision completion stages, Chronicle weights/cooldowns/interval, major event one-shot guards, external TFR idea/equipment/building/modifier/global-flag references, Serbian state ownership, guarded refundable projects, and absence of daily polling or Phase 2 war effects.

Validation is static and source-backed. No game was launched for this increment. Actual tooltip rendering, timed delivery, economy accounting, doctrine discount application and save/reload behaviour remain unverified in a live campaign. No installed mod directory was updated.
