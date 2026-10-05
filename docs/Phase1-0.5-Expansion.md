# Early Serbia expansion — 0.5.0

Six focuses extend the existing early tree to 24. All original focus costs and rewards remain, except that Contain unlocks the new COVID decisions and Reopen loses its vaccination availability gate. The previous recovery, two-factory defence reward, Vulin minister, procurement rebalance and Belgrade Blues cleanup remain intact. Chronicle, strategic studies, Western Shield monitoring and the Kosovo endpoint retain their existing effects.

| Focus | Days | Role |
|---|---:|---|
| Internal Investment Drive | 28 | Third mandatory economic investment |
| Settle the Old Political Accounts | 14 | 35 PP, one stability point |
| Secure the National Assembly | 14 | 50 PP, two stability points |
| Send the Migrants Back | 21 | Halved emigration penalties, political tradeoff |
| Serbia Stands United | 21 | Political capstone and National Consensus |
| Reconstitute the Serbian Volunteer Guard | 70 | Third mandatory military preparation |

The six costs add 168 mandatory days. A recursive ancestor check confirms 721 days before selecting Watch the Western Shield, and 756 through its completion. No hardcoded collapse or Kosovo date was added. All three middle economic investments, both political fork focuses and all three military preparations are required at their respective merges. Existing branch coordinates are retained; the political chain and final convergence move down only as needed.

## COVID

The installed German `GER_coronavirus_timer` mission provides the architecture and initial 104-day duration. `MSGA_pending_outbreak` activates once after Contain; one-time 10/15/20 PP decisions call `add_days_mission_timeout` with exactly 120/130/150 days. They disappear after use, outbreak or permanent resolution. The timer expires once, adding native `low_covid_cases` only if no generic case spirit already exists. There is no repeating escalation timer.

Vaccination is independent of hospital support and reopening, appears from 2021-01-01 and delivers after 20 days for 75 PP. `MSGA_end_covid` removes all five native case spirits, legacy MSGA pandemic ideas and the pending mission; it sets the permanent resolution flag. Both initialization and timeout guard against resolved/vaccinated countries. Startup cleans any resolved-save case spirits without replaying rewards. An older save with an existing active COVID system keeps that state and can vaccinate; no duplicate pending timer is initialized. Old unused hospital event/idea definitions remain for save compatibility but are no longer awarded by the COVID decisions.

## Native economic and migration APIs

- `add_debt` with `debt_var_temp = 2.0` adds exactly $2B nominal debt; the southern project uses `1.0`. The inflation-scaled variant was deliberately avoided because it changes the specified nominal amount. TFR updates derived debt and GDP through its own API.
- State **45** is Vojvodina, with Novi Sad province **3617** and starting infrastructure **3**. It receives two civilian factories, with only zero, one or two extra slots as needed.
- **Genuine map limitation:** TFR infrastructure has `state_max = 5`. The three-level award is capped at remaining capacity; a new campaign gains **two effective levels**, ending at five. Neither TFR's building definition nor the starting state was overridden to conceal this conflict.
- `industrial_development_monthly = 0.05` is a percentage modifier displayed as +5.0%. TFR's monthly development update adds it to `industrial_development_var`; it is not a construction bonus or five complete industrial-level upgrades. `income_growth_factor = -0.05`, `business_value_factor = 0.10` and `industrial_capacity_factory = 0.02` complete the permanent campaign spirit.
- The Austria-Hungary reference was inspected at `8e4e35f8093f826dc21fafbccb82e3e1cd3eb18e`. Its `AHR_add_one_industrial_development` confirms the separate one-off `add_industrial_development` API, which is not the requested monthly modifier. No debt helper was found there; installed TFR supplies the authoritative debt API. No reference assets or scripts are copied.
- State **108** contains Niš province **11887**. The 20 PP, 30-day southern investment adds exactly two slots and one civilian factory only on delivery. Loss of ownership/control refunds the nominal debt and PP once, without placing factories in a foreign state or re-enabling the decision.
- Native `SER_massive_emigration_problem` uses `monthly_population = -0.2` and `research_speed_factor = -0.1`. Completion removes it before adding the easing spirit at `-0.10/-0.05`. Stability falls five points, war support rises five points, and `army_org_factor = -0.05` lasts exactly 75 days.
- National Consensus uses `stability_factor`, `political_power_factor` and existing `mobilization_speed`, each `0.05`.

## Exact division references

The supplied screenshots were inspected directly and checked against installed unit definitions, including combat width and strength. Both templates have no optional support companies.

| Template | Grid | Native width / strength |
|---|---|---|
| Srpska dobrovoljačka garda | Column 0: `infantry` rows 0–2, `artillery_brigade` row 3 | 12 / 75.6 |
| Oklopno-mehanizovana brigada | `modern_armor` column 0, `mechanized` column 1, `light_mechanized` column 2; rows 0–1 in each | 24 / 164 |

The locked regimental-support row shown in the volunteer designer is a UI control, not another battalion. The calculated strength of 75.6 matches the screenshot without adding a unit there. The armoured template's 100 tanks, 100 IFVs and 90 APCs match the screenshot's equipment families. Serbia's installed `SER_2020` already uses these three active battalions and equipment families; no technology grant is added.

Template-only `MSGA_` OOBs are loaded through guarded startup/focus effects, without overriding Serbia's country history or base OOB. The armoured OOB contains no deployed units and awards no equipment. The volunteer template is locked to preserve its screenshot composition, and the engine's documented `set_division_template_cap` sets its cap to four.

One guarded focus grant deploys **Arkan's Tigers**. Three separate 25 PP, 20-day, one-time decisions deploy **The Scorpions**, **White Eagles** and **Serbian Guard**. All use the same template, `count = 1`, `start_equipment_factor = 1` and `start_manpower_factor = 1`, following native runtime spawn patterns. No spare equipment dump or living Arkan character is added. These are the only four scripted volunteer grants; the cap and lock still need in-game verification.

## Assets and validation

Six new focus DDS files and four spirit DDS files are copied unchanged from the user-supplied pack. Base/shine focus sprites and spirit sprites are in separate additive gfx files. The full supplied source/reference pack is retained. The validator checks all 52 sprite definitions for duplicates, runtime texture existence, explicit RGBA8 headers and pixel identity to supplied PNGs; six new focus icons are 95×95 and four spirit icons are 60×68.

`tools/validate_phase1.py` passes the updated graph, pacing, localization, native modifier/API/state/equipment references, exact template grids and preservation checks against the previous cleanup commit. It checks one-time delivery guards and pending-mission cancellation. `git diff --check` also passes. Static results are recorded in `docs/phase1_static_validation.json`.

No game was launched and no installed mod copy was updated. Runtime mission delays, spawned equipment/manpower, template lock/cap, startup ordering, save/load and game error logs therefore remain unverified. A new Serbia campaign is recommended for all new focus rewards; already-completed focuses do not replay. Phase 2 war effects remain absent.
