# MSGA development notes

## Current build: Phase 1 0.4.0

The original 18-focus layout, prerequisites, costs, names and custom artwork are preserved. Vaccination now gates reopening, the Western monitoring focus can precede collapse, and the resulting report gates Kosovo. Updated rewards, two COVID decisions, seven Chronicle stories and source evidence are documented in `docs/Phase1-0.4-Implementation.md`. Static checks pass; see `docs/phase1_static_validation.json`. This increment has not been installed or tested in a running game.

The sections below are historical P1.0–P1.3 notes and do not certify current gameplay acceptance. Consult the current report for runtime validation and limitations.

## Earlier P1.0–P1.3 audit

## Environment verified

- HOI4 install: `C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV`.
- HOI4 version from `Documents/Paradox Interactive/Hearts of Iron IV/logs/system.log`: Operation Postern v1.19.3.0.c01a (ef41), build Sep 9 2026.
- User mod root: `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod`.
- TFR Workshop folder: `C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/3350890356`.
- TFR descriptor: `name="The Fire Rises"`, version `1.0.9.1c`, supported version `1.19.*`; dependency string uses that exact name.
- YR is present at workshop ID 3770452759 but is not a dependency.

## Serbia audit and election call-flow

- Tag/leader: `SER` / `SER_aleksandar_vucic`; TFR `history/countries/SER - Serbia.txt` starts as conservative and allows elections, with `last_election = 2017.1.1`, 48-month frequency.
- TFR startup (`common/on_actions/TFR_on_actions_SER.txt`) separately initializes support variables and `SER_sps_opposition_dynamic`. MSGA initialization is additive and does not change these variables.
- TFR startup action in `common/on_actions/00_TFR_on_actions_ZZZ_startup.txt` schedules `serbia.21` after 20 days. That event activates `SER_sps_influence_mission`; it is retained as domestic political flavor.
- `serbia.22` is a triggered-only event labelled the 2020 parliamentary election; no call-site was found. It has no political effect.
- `serbia.16` is scheduled by the TFR generic peace on-action after Serbia loses to BOS/KOS/CRO and by timeout of `SER_take_kosovo_mission`. Its original effect promotes `SER_milan_mojsilovic_char` and sets nationalist government; this violates MSGA's Vučić constraint.
- `SER_take_kosovo_mission` cancellation schedules `serbia.18` after 30 days. TFR `serbia.18` retains Kosovo-terrorism spirits/modifiers, then uses `SER_election` game-rule outcomes to schedule `serbia.17`, `.19`, or `.20` 90 days later. `.17` is socialist leadership, `.20` alternative right leadership; `.19` retains Vucic. This path is post-Kosovo failure, not an ordinary election timer.
- `.23` is Croatia-specific; `.24`–`.27` are Macedonia/Croatia/Balkan consequences and are not MSGA election entry points. They are unmodified.

### Election suppression choice

At startup, MSGA sets `elections_allowed = no` for SER only, preventing the vanilla election timer while preserving party popularity, ruling party, Vucic character and TFR protest/SPS events. No TFR event IDs are overridden. `serbia.16` and `.18` are post-defeat consequences tied to Kosovo/Bosnia/Croatia war outcomes, not routine election-date entry points; they are outside P1.0–P1.3 because Kosovo gameplay is explicitly deferred. Phase 2 must integrate these defeat outcomes with the fixed-Vucic canon before enabling those war outcomes. This avoids fragile duplicate event IDs and does not use a leader-restoration safety net.

## Focus shell

- Dedicated `MSGA_SER_phase1`, `default = no`, country factor only for `SER`; generic tree remains the vanilla fallback for other tags.
- Sixteen visible focuses. The planned `Protect the Workforce` focus is omitted and documented for conversion to a P1.4 decision.
- HOI focus `cost` unit is 7 days: 4 = 28d, 5 = 35d, 6 = 42d.
- Each focus has only a one-shot completion flag. COVID/economy/military/resource/Kosovo gameplay is not implemented.
- Placeholder icons use vanilla `GFX_goal_generic_*`; no YR art copied.

| Focus | Placeholder |
|---|---|
| A New Decade | `GFX_goal_generic_political_pressure` |
| Contain the Outbreak | `GFX_goal_generic_national_unity` |
| Reopen on Serbian Terms | `GFX_goal_generic_consumer_goods` |
| Consolidate the State | `GFX_goal_generic_political_pressure` |
| Manage the Streets | `GFX_goal_generic_political_pressure` |
| A Presidential Mandate | `GFX_goal_generic_national_unity` |
| Attract Productive Capital | `GFX_goal_generic_production` |
| Modernise Belgrade Services | `GFX_goal_generic_construct_civ_factory` |
| Develop the Morava Corridor | `GFX_goal_generic_construct_infrastructure` |
| An Independent Resource Policy | `GFX_goal_generic_construction` |
| Restore Defence Production | `GFX_goal_generic_construct_mil_factory` |
| Modernise the Army | `GFX_goal_generic_army_doctrines` |
| Arms for an Uncertain World | `GFX_goal_generic_production2` |
| Secure the Supply Lines | `GFX_goal_generic_army_motorized` |
| Watch the Western Shield | `GFX_goal_generic_intelligence_exchange` |
| The Kosovo Question | `GFX_goal_generic_forceful_treaty` |

## Balance of Power

- Separate id `MSGA_SER_streets_presidency`; TFR `SER_milosevic_titoist_balance` untouched.
- New-game startup checks SER and `NOT = { has_country_flag = MSGA_bop_initialized }`; adds `-0.10` once and sets the guard. TFR `on_startup` logic remains intact.
- Center has no modifier. Range modifiers use `stability_factor`, `war_support_factor`, TFR-verified `industrial_capacity_factory`, `production_speed_buildings_factor`, and TFR-verified `political_power_gain`.
- Two 50 PP decisions move the balance ±0.05 with 120-day cooldown. Public grievances also add +1% stability. AI use disabled for test/early human campaign.
- BOP side art currently reuses existing TFR Serbia BOP sprites as placeholders; replace with MSGA art later.
- Future effect contract `MSGA_apply_territorial_loss_pressure` is not implemented/called; later loss hooks should move -0.03/-0.08.

## State 107 / Belgrade

The apparent mismatch is resolved. The TFR file is unfortunately named `history/states/107-Kosavo.txt`, but its only province is 11586, localized as Belgrade; TFR English replacement localization explicitly maps `STATE_107` to “Belgrade.” It owns the province containing Belgrade and is consistent with `capital = 107`. The filename is stale/misleading. No state-specific effects are included in P1.0–P1.3.

## Compatibility and remaining work

- YR is deliberately not supported as a co-load target: its descriptor includes `replace_path = "common/national_focus"` and broad directory replacement.
- TFR update risks: event 16/18 implementations or focus syntax may change; re-audit exact event IDs and game version after updates.
- P1.4 TODO: convert Protect the Workforce to a decision, implement COVID, and test transition choices.
- Future focus milestone: add the US-collapse gate only with exact TFR flag integration.
- Do not add Office Park, economic investments, resources, factories, Kosovo war, or later phases in P1.0–P1.3.

## Validation record

- Static source verification: passed for 16 unique focuses, localization coverage, icon keys, balanced braces, descriptor/dependency fields, and absence of `replace_path`.
- Bounded HOI4 launch using TFR + MSGA reached graphics initialization and continued through no-date parsing. The launch output contained no MSGA-attributed parser errors. Existing errors reported in the same pass point to vanilla/TFR files (for example `common/technologies/hidden.txt`, `common/ideas/00_TFR_laws_economic.txt`, `common/decisions/TFR_decisions_ATW.txt`, and `TFR_decisions_GER.txt`).
- The game process remained open after the 45-second observation window; the launcher DLC selection file was restored exactly. This was a parser smoke check, not a verified main-menu or campaign test.
- New Serbia start, focus assignment, decision interaction, save/load, and non-Serbia regression remain unverified because no in-game UI control was available in this session. Existing user `error.log` contains baseline TFR/HOI4 warnings; compare only new MSGA-attributed errors after a full campaign test.
