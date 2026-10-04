# MSGA — Phase 1 Design & Research

**Status:** design proposal, not implementation. **Research snapshot:** installed TFR 1.0.9.1c and TFR: Yugoslavia Reborn 0.6.3 (both declare HOI4 1.19.*). The installed files are authoritative for the findings below; Steam workshop files are mutable, so verify these hooks against the version used for implementation.

## Scope and confidence

This document fully scopes the Serbian 2020 opening through the first Kosovo Crisis unlock. Kosovo's war, Republika Srpska, Bosnia, Greater Serbia, Yugoslavia, and European endgame receive architectural notes only. **Verified** means present in the inspected install. **Proposed** means a design decision requiring in-game validation. No mod files were created.

# Part A — Research findings

## TFR Serbia skeleton

| Area | Verified implementation | Design consequence |
|---|---|---|
| Tag/start | `SER`; `history/countries/SER - Serbia.txt`; capital state 107, OOB `SER_2020`, stability 0.65, three research slots. Politics starts `conservative`, last election `2017.1.1`, election frequency 48 months, elections enabled. | Retain tag, order of battle, tech, characters and economic setup. Do not replace country history wholesale. State 107 is Belgrade; its TFR filename is misleading. |
| Leader | `common/characters/TFR_characters_SER.txt`: `SER_aleksandar_vucic`, ideology `right_populism`, permanent expiry (`1.1.1.1`), ID -1. | Keep this character and ensure elections never promote a different leader for the intended campaign. |
| National spirits | `common/ideas/TFR_ideas_SER.txt`: starting ideas include `SER_gdp_fix`, `SER_scars_of_bombings_idea`, `SER_massive_emigration_problem`, `SER_policy_of_pragmatism`, `SER_emerging_economy`, `SER_rebellion_of_kosovo`, `SER_between_two_spheres_idea`, cabinet characters, `medium_poverty`, and `low_conscription`. Other defined ideas include `SER_Enforced_Isolation`, `SER_Serbian_Rejuvenation`, `SER_Reformed_UCK_Terrorism`, `SER_reconstructing_yugoslavia*`, and `SER_Hegemon_of_Balkans`. | Assess and evolve existing ideas rather than clone or stack near-duplicates. Early scenario starts with pragmatic/economic context; future-stage ideas are not Phase 1 rewards. |
| Serbian decisions | `common/decisions/TFR_decisions_SER.txt`, category `common/decisions/categories/TFR_decision_categories_SER.txt`; includes `SER_belgrade_blues` chain, Kosovo-failure gated choices, and event scheduling (`serbia.3`, `.15`, `.18`, `.16`). | Preserve unrelated TFR content. The election/protest sequence is coupled to event and decision triggers, so a replacement must account for the whole chain, not just one event. |
| Events/elections | `events/TFR_events_SER.txt`, namespace `serbia`. Elections/protests span `serbia.16`–`.27`; `serbia.22` is labelled 2020 parliamentary election. Events set `elections_allowed`, `last_election`, and `election_frequency`; some also change ruling party/leader. | Elections are not one isolated timer. Avoid global election changes or a replace-path. Suppress Serbia-only election entry points and test related protest decisions. Exact final suppression mechanism should be chosen after a focused trigger audit in the target TFR build. |
| On-actions | `common/on_actions/TFR_on_actions_SER.txt`: `on_startup` initializes `SER_government_support_var=.26`, left `.08`, right `.10`, SPS variables, and applies `SER_sps_opposition_dynamic`. | Avoid competing startup initializers. Initialize MSGA mechanic once with an idempotent flag and avoid reusing YR variables. |
| Existing BoP | `common/bop/TFR_bop_SER.txt`: `SER_milosevic_titoist_balance`, initial `-.05`, range `[-1,1]`, custom balance category. Left/Milosevic and right/Titoist ranges, modifiers, and decision category belong to existing ideological Yugoslavia content. | The player's Presidency/Streets axis has a different meaning. Do not repurpose this BoP: create a separate MSGA BoP and ensure both do not compete for a single UI/decision category or initialize unexpectedly. Exact coexistence needs an in-game test. |
| Scripted mechanics | `common/scripted_effects/TFR_scripted_effects_SER.txt`: variable-based support shifts; `common/dynamic_modifiers/TFR_dynamic_modifiers_SER.txt`: dynamic ideas consume Serbian vars, including `SER_reconstructing_yugoslavia_dynamic`. | Use a uniquely namespaced `MSGA_` set of variables, effects, flags, ideas and event namespace. |
| Focus tree | No TFR file matching Serbian focus tree in its `common/national_focus` directory; TFR YR supplies `SER_yugoslavia_reborn.txt` plus shared/path files. | MSGA can add a dedicated tree for SER without overwriting an existing TFR Serbia tree in this version. Must verify tree assignment and compatibility when TFR updates. |
| Cosmetic/formable content | TFR `common/countries/cosmetic.txt` has SER cosmetic tags including Yugoslav variants; Serbian decisions/events include Balkan and Kosovo/R.S. skeleton content. | Do not reuse names or cosmetic tags for early Phase 1 states. Reserve future cosmetic/formable integration for later phases. |

**Safe to reuse:** existing leader/characters, TFR Serbia ideas where appropriate, TFR economy actions and interface, state/OOB history, event art, localization conventions. **Override cautiously:** elections only via Serbia-specific triggers/events once mapped; focus-tree assignment only if YR is also active. **Do not override:** whole `events`, `common/decisions`, or `common/on_actions` directories.

## TFR economy — verified mechanics and boundaries

TFR implements its macroeconomy with scripted variables, dynamic modifiers, state buildings, and UI—not just vanilla factory count. Relevant local entry points:

| Need | Local implementation / observed pattern |
|---|---|
| Economic actions | `common/scripted_effects/00_TFR_scripted_effects_ZZZ_economic_actions.txt`: effects `print_money_economic_action_effect`, `quantitative_tightening_economic_action_effect`, `war_taxes_economic_action_effect`, `develop_state_economic_action_effect`. |
| Macro ledger | `common/scripted_effects/TFR_scripted_effects_ZZZ_economy_ledger.txt`: `TFR_economic_ledger_calculation_debt`, GDP/revenue/debt calculation families and display variables; scorer-backed calculations. `debt_var` is ledger output; it is not a debt-payment effect or safe direct investment currency. |
| Dynamic economy | `common/dynamic_modifiers/TFR_dynamic_modifiers_ZZZ_economic.txt`, hidden economic ideas, and `common/modifier_definitions/00_TFR_economic_modifiers_definition.txt`. Verified modifier names in Serbian ideas include `business_value_factor`, `tax_business_rate`, `tax_personal_rate`, `industrial_capacity_factory`, `poverty_development_monthly`, and `society_development_monthly`. |
| Office Parks | TFR/HOI building key `office_park`; examples use `type = office_park` in scripted focus/state effects (e.g. `TFR_national_focus_CHI.txt` around 527–535). State building, not national spirit. Increase through `add_building_construction` pattern after verifying allowed building/effects in installed game. |
| Civilian/Military Investment | TFR investment choices are implemented through its decisions/economic-action effects and variables, not vanilla `civilian_investment` or `military_investment` effects. Treat the phrases as TFR economy concepts, not script tokens. Prefer exposing TFR's own investment decision/actions; do not invent variable names. |
| Business Value | Serbian ideas prove modifier `business_value_factor` is supported and used. It affects TFR's Business Value accounting through its dynamic modifier/calculation pipeline; it is not itself an instant cash effect. Use modest percentages and measure in UI. |
| GDP, government revenue, debt/GDP | TFR's ledger computes/displays these via script variables and scorers; don't directly write the calculated output variables. No verified direct native `add_gdp` / `pay_debt` effect. Build economic decisions around existing TFR actions, modifiers, tax factors and actual state buildings. |

**Verified result:** Serbia's existing ideas use significant business value modifiers (+.10, +.20, +.05, -.15 examples), and `industrial_capacity_factory` modifiers. **Unverified:** a safe direct investment API that lets a submod add to TFR's investment queue or debt principal. Therefore Phase 1 focuses/decisions should modify existing business value/tax/industrial capacity modifiers and unlock/use TFR's own investment actions; avoid pretending an investment decision necessarily constructs an Office Park unless its installed effect is directly reused. Any TFR effect call must be confirmed against exact `00_TFR_scripted_effects_ZZZ_economic_actions.txt` body and cost/availability conditions at implementation.

**Starting economy/state facts:** TFR country history applies `SER_gdp_fix`, `SER_emerging_economy`, `SER_policy_of_pragmatism` and other ideas; it does not set GDP/debt ledger values there. The inspected state history shows state 1296 (`Sumadija and Western Serbia`) starts with 45 steel, 2 civilian factories, and 1 arms factory. State 107 is Belgrade, as confirmed by province 11586 and TFR English localization despite its misleading filename. Avoid state-specific effects until the relevant construction/map mechanics are validated.

## Global event hook

The installed United States path uses several stages, not one generic “America collapsed” flag. `events/TFR_events_USA.txt` event at line ~265 sets `USA_civil_war_flag` and global `USA_shattered_union_global`; `common/on_actions/TFR_on_actions_USA.txt` checks global `USA_american_civil_war_global`. Other flags such as `USA_gop_collapse_flag` describe party/government crises, not complete state collapse. **No Serbia-specific “US collapse” hook was found in TFR's `TFR_events_SER.txt`.**

**Proposal:** treat `has_global_flag = USA_shattered_union_global` as the robust world signal for a fractured United States, and require `USA_american_civil_war_global` only if implementation audit confirms it is set reliably in every route and its exact semantics are desired. Better: a new MSGA country event checks the verified TFR global flag by daily/weekly pulse, sets `MSGA_US_ORDER_COLLAPSED`, fires once, and opens the final focus. Fallback: a visible decision “Assess the New European Balance” becomes available if the global flag exists but the event did not fire. Do not key to GOP collapse or ideology. Serbia's Phase 1 tree must also remain completable if US collapse is late or never occurs; the final focus waits, while player can finish side branches.

## TFR conventions and research gaps

Use `SER` scope and TFR's custom ideology/economy system. Focus effects frequently use `add_ideas`/`swap_ideas`, state construction, decisions, scripted effects, and custom tooltips. TFR content often chains short event follow-ups and variable-backed dynamic ideas; MSGA should retain feedback but favor visible flags, explicit outcomes, and idempotent effects. No external documentation was used to infer undocumented TFR effect names. Serbia state/resource data and election trigger chain should be rechecked during implementation from the game's active TFR load order.

# Part B — Existing Serbia assessment

| Action | Contents | Rationale |
|---|---|---|
| Keep | `SER`, Vucic `SER_aleksandar_vucic`, baseline ideas/characters, 2020 OOB, tech, TFR macroeconomy, map states and unrelated TFR decisions. | Retains the TFR scenario and character continuity. |
| Modify/evolve | Start ideas through additive/submod spirits or controlled `swap_ideas`; use existing TFR Serbia economy strengths as starting values. | Avoid stacking multiple permanent economic boosts. |
| Disable | Election route outcome and election replacement events for Serbia only; prevent TFR Serbia election chain from changing leader. | Meets campaign constraint without changing other tags. Implement only after auditing all sources of `elections_allowed = yes` and `promote_character`/government changes. |
| Replace | Focus-tree content only if YR isn't loaded; with YR loaded, avoid duplicate trees and require explicit compatibility policy. | YR declares replace_path for the whole `common/national_focus` folder, so simple additive focus definitions may be suppressed by load order. A standalone TFR submod can add a new tree; YR compatibility is a real conflict. |
| Extend | MSGA BoP, COVID crisis, focused decisions, military/economy branches, collapse reaction. | New named content without rewriting TFR's large files. |

**Least-invasive election recommendation:** first inspect the country history/election on-actions and all `serbia.16`–`.27` call sites. Preferred submod approach is to prevent Serbia-only election events at their own entry points with an additive event/decision trigger guard only if TFR exposes one; if the entry points are hardcoded in `TFR_events_SER.txt`, a narrow same-ID event definition may be needed, but duplicate-ID precedence is load-order fragile. A Serbia-only `on_action` that restores Vucic after promotion is a last-resort safety net, not the primary design, because a replacement may occur for a tick and side effects remain. Do not claim a safe exact hook until in-game test. Plan a small compatibility patch keyed to exact TFR version and document the affected event IDs; do not replace the whole file or use global `replace_path`.

# Part C — Yugoslavia Reborn assessment

Installed YR 0.6.3 has a polished breadth of Serbia concepts and extensive art, but its `descriptor.mod` declares dozens of `replace_path` entries, including `common/national_focus`, `events`, decisions, ideas, characters, on_actions, history and map. This is **not** a harmless Serbia-only dependency: it replaces whole TFR folders for all countries and must remain optional.

| Worth adapting | Rebuild / avoid |
|---|---|
| Layered Serbia economic development: `SER_YR_balkan_tiger`, `SER_YR_jadar_lithium`, `SER_YR_corridor_ten`, `SER_YR_regional_powerhouse`; alternative Chinese capital vs European funds; investment tradeoff. | YR's large replacement footprint; never require it for MSGA and do not copy its replace_path strategy. |
| Early national debate and choice architecture; use meaningful choices to express economic/diplomatic tradeoffs, not leader replacement. | Broad ideological routes conflict with fixed Vucic canon and dilute intended campaign. |
| Resource and transport concepts (Jadar lithium, Corridor X) as research leads. | Tying critical progress to long chain of focuses or unverified economic variables; use investment decisions with clear costs/results and contingency. |
| Art direction, banners, portrait and custom decision UI; one-focus-to-decisions mechanic. | Event chains whose delayed hidden follow-ups rely on changing tags, owners, or targets without rechecking triggers. `yr_serbia_events.txt` contains many delayed events and cross-country scopes; every transfer/wargoal/trigger needs revalidation. |
| Dynamic modifiers for multi-variable stateful themes. | Reuse of generic/overloaded variable names or dynamic effects with many unbounded dimensions. MSGA needs small, bounded variables and one central update effect. |

YR `SER_yugoslavia_reborn.txt`, `SER_yr_shared_focuses.txt`, `yr_decisions_SER.txt`, `yr_scripted_effects_SER.txt`, `yr_ideas_SER.txt`, `yr_on_actions_SER.txt`, `TFR_bop_SER.txt`, `yr_serbia_events.txt` are good concept references, not source dependencies. Its tree includes 3-day event-triggering focuses and economic branches; MSGA should use 35/42-day strategic focus cadence and move repeatable investment into decisions.

# Part D — Phase 1 design pillars

1. One canonical Vučić campaign; no leader route divergence.
2. Five to seven strategic focuses per major story beat; no filler modifiers.
3. Focuses unlock repeatable, optional decisions; decisions carry ongoing management.
4. Political stability is a tradeoff tracked on a visible Streets–Presidency BoP.
5. Use the existing TFR economy's real modifiers and actions; never counterfeit GDP/debt changes.
6. Build a plausible regional military, not a Balkan superpower before Kosovo.
7. Global collapse is a late gate with fallback and no race softlock.
8. Every delayed event has one-shot flags, visible feedback, and a recovery path.
9. Reuse base state/resource facts; no unsupported strategic resource fantasy.

# Part E — Complete Phase 1 focus tree (proposed)

**Tree size: 17 focuses.** Standard duration 35 days; capstone/major economic investment 42 days. Prerequisites are AND unless stated OR. No mutually exclusive routes: the meaningful branch is order and decision strategy. Start is one political opener; four parallel branches converge on collapse response. Focuses give one-time outcomes and unlock repeatable actions.

| Internal ID / display | Days; prerequisites | Effects / decisions / purpose |
|---|---|---|
| `MSGA_serbia_in_the_new_decade` — A New Decade | 35; start | Establish MSGA state flag and BoP; +50 PP, +2% stability; unlock COVID response decisions; event `MSGA.1`. Campaign opener. Description: Belgrade enters a decade of uncertainty. Icon: parliament. |
| `MSGA_contain_the_outbreak` — Contain the Outbreak | 35; A New Decade | Add temporary `MSGA_covid_pressure` spirit; unlock Public Health Response decisions; start COVID stage; no factories. Delivers immediate crisis choices. Icon: medical cross. |
| `MSGA_protect_the_workforce` — Protect the Workforce | 35; Contain the Outbreak | Improve COVID trajectory; small Streets→Presidency movement; unlock targeted relief decision; avoid economic bonus stacking. Icon: workers/mask. |
| `MSGA_reopen_on_serbian_terms` — Reopen on Serbian Terms | 35; Protect the Workforce | Remove/upgrade COVID spirit if stage resolved; one-time modest stability; opens economic recovery branch. Icon: bridge/road. |
| `MSGA_consolidate_the_state` — Consolidate the State | 35; A New Decade | Unlock governance decisions; +25 PP; small Presidency movement; no elections. Icon: assembly. |
| `MSGA_manage_the_streets` — Manage the Streets | 35; Consolidate the State | Resolve initial protest pressure through a choice event; unlock protest response decision category; consequence tradeoff: authority or public concessions. Icon: crowd. |
| `MSGA_presidential_mandate` — A Presidential Mandate | 35; Manage the Streets | Complete initial stabilization; Presidency +.04; stability +2%; prerequisite for industrial and Kosovo readiness branches. Icon: podium. |
| `MSGA_attract_productive_capital` — Attract Productive Capital | 35; Reopen on Serbian Terms | Add `business_value_factor +0.05` temporary or gated permanent; unlock capital investment decision. Measured TFR effect, not cash. Icon: factory/coins. |
| `MSGA_upgrade_belgrade_services` — Modernise Belgrade Services | 35; Attract Productive Capital | Add one Office Park level in Serbia's verified Belgrade state only after confirming the target map state and open slots/capacity; Business Value +0.03 via temporary idea; purpose is a concrete civilian growth choice. Icon: office block. |
| `MSGA_develop_the_morava_corridor` — Develop the Morava Corridor | 35; Attract Productive Capital | Unlock transport/industrial investment decisions in states 107/108; optionally one infrastructure level, no direct free civ factory. Icon: rail. |
| `MSGA_restore_defence_production` — Restore Defence Production | 42; A Presidential Mandate AND Attract Productive Capital | Add 1 military factory, unlock Defence Industry decisions, small factory output bonus +.05 for 180 days. Key industrial choice. Icon: machine works. |
| `MSGA_modernise_the_army` — Modernise the Army | 35; Restore Defence Production | Army experience +10; modest planning/entrenchment or land doctrine cost reduction; unlock equipment procurement decisions, no free divisions. Icon: soldier/gear. |
| `MSGA_arms_for_an_uncertain_world` — Arms for an Uncertain World | 35; Modernise the Army | One additional military factory only if player chose military industrial investment decision, otherwise 100 PP/army XP; add small temporary production efficiency cap. Icon: rifle. |
| `MSGA_secure_supply_lines` — Secure the Supply Lines | 35; Modernise the Army | Infrastructure/supply node improvement only if map confirms state; unlock logistical readiness decision; supports territorial defense, not offensive war. Icon: truck. |
| `MSGA_independent_resource_policy` — An Independent Resource Policy | 35; Attract Productive Capital | Unlock prospecting decisions for lithium/copper only where verified deposits/state capacities support them; do not grant raw resources until state ID and existing quantity confirmed. Icon: ore. |
| `MSGA_watch_the_western_shield` — Watch the Western Shield | 35; Presidential Mandate AND Modernise the Army | Arms/geopolitical briefing; hidden pulse flag detection plus visible journal-style event; no US-collapse dependency to complete earlier tree. Icon: map/eye. |
| `MSGA_the_kosovo_question` — The Kosovo Question | 42; Watch the Western Shield AND Presidential Mandate AND `MSGA_US_ORDER_COLLAPSED` | Set `MSGA_kosovo_phase_unlocked`; fire event summarizing crisis; enable Phase 2 hook/decisions only (placeholder category hidden until Phase 2 exists). End of Phase 1. Icon: Kosovo map/document. |

**Economy key:** Focuses should preferably unlock decisions that call verified TFR economic action effects. Above numerical modifiers are design ceilings, not final effect script values. Avoid permanently stacking the +.10/+ .20 class of existing Serbian national ideas; prefer timed 180–365 day modifiers or decision-funded state construction. Direct civilian factory grants are excluded from the economic branch.

# Part F — Visual layout

ASCII sketch (x grows right, y grows down):

```text
                           [A New Decade]
                 ┌─────────────┼────────────┐
          [Contain Outbreak] [Consolidate]
                 │              │
        [Protect Workforce] [Manage Streets]
                 │              │
        [Reopen on Terms] [Presidential Mandate]────┐
                 │                                  │
    [Attract Productive Capital]                    │
      ├──────────┼──────────┐                       │
 [Belgrade] [Morava] [Resource Policy]              │
      └──────────┬──────────┘                       │
          [Restore Defence Production]◄─────────────┘
                     │
             [Modernise Army]
              ├──────┴──────┐
 [Arms for Uncertain World] [Secure Supply Lines]
              └──────┬──────┘
           [Watch Western Shield]
                     │ + US signal
            [The Kosovo Question]
```

Approximate positions: `A New Decade (4,0)`; COVID column x=2, y=1–3; governance x=6, y=1–3; economy x=2–4, y=4–5; military x=5, y=4–7; resource at (1,5); signal/capstone x=5, y=8–9. The three columns retain whitespace, with only two convergences and no long zig-zagging dependencies. Exact focus coordinates depend on tree grid conventions and portrait/art dimensions. **State-ID audit correction:** state 107 is Belgrade; `history/states/107-Kosavo.txt` contains Belgrade province 11586 and TFR English localization maps `STATE_107` to “Belgrade.” The misleading filename caused earlier uncertainty; `capital = 107` is consistent.

# Part G — Phase 1 pacing

Focus completion days assume sequential 35-day focuses and no focus-time bonuses: minimum required chain A New Decade→Consolidate→Manage Streets→Mandate→Watch Shield→Kosovo Question = 35+35+35+35+35+42 = **217 focus days**. If the military focuses are chosen (Restore, Modernise, then Watch, capstone), a practical mandatory route becomes **287 days**. Full 17-focus tree if played sequentially = 35×14 + 42×3 = **616 days**; branches run concurrently only in tree access, not time.

| Milestone | Earliest focus completion from start | Approximate campaign timing |
|---|---:|---|
| COVID response begins | Day 35 | Early game |
| First outbreak control | Day 70 | Early game |
| Government stabilisation | Day 140 | Early-mid |
| Economic recovery unlocked | Day 140 (if COVID line completed) | Player can invest immediately |
| Major rearmament | Day 210–280 | Requires productive economy and military line |
| US shield monitoring | Day 245–315 | Conditions readiness, not collapse |
| Kosovo unlock | 217 days absolute political route; ~287 with practical military readiness | Earliest calendar date depends on US flag; suggested not earlier than 2021 in normal progression |

The focus calendar is not the crisis calendar: COVID decisions should advance on monthly/quarterly beats independent of focus completion. If TFR US events arrive late, the player continues decisions and optional branches. The final focus remains visible and displays the missing condition; fallback assessment decision appears once verified TFR signal exists. No hidden timeout or fail-state.

# Part H — Balance of Power

**Name:** The Streets ↔ The Presidency. Center is contested politics; right means administrative control/confidence; left means organized public anger. Use TFR-compatible BoP definitions. Range `-1.00` Streets to `+1.00` Presidency; start `-0.10` (slight public pressure). Initialization only once.

| Position | Proposed effect (tuning target) |
|---|---|
| Streets dominant `-0.60…-0.25` | Stability -3%, construction speed -3% |
| Streets crisis `-1…-0.60` | Stability -8%, factory output -5%, war support -5%; trigger one protest event per threshold crossing, not repeated daily |
| Center `-0.25…+0.25` | No modifier; remains a viable tradeoff position |
| Presidency dominant `+0.25…+0.60` | Stability +3%, political power gain +3% |
| Presidential control `+0.60…+1` | Stability +5%, factory output +3%; political power gain -2% (centralization cost) |

**Movement sources:** public health response and transparent relief +.03…+.06; coercive protest response +.05 Presidency but add temporary unrest/long-term penalty; delayed COVID or harsh austerity -.03…-.08; successful TFR economy investment +.02; war casualties/exhaustion later -.05 per significant loss event. Cap individual focus/event swings at .10. Put recurring choices on decisions with PP and TFR-economy cost, not repeated focuses.

**Future territory hook:** define a single scripted effect `MSGA_apply_territorial_loss_pressure` called by later peace/state-loss events; use `add_to_variable`/BoP movement only after verifying syntax. Recommended delta -0.08 per strategically meaningful loss, -0.03 per minor loss; no per-state daily loop. BoP movement is a future contract, not active in Phase 1.

# Part I — Economic design

| System | MSGA implementation proposal | Compatibility guard |
|---|---|---|
| Business Value | Temporary +.05–.08 `business_value_factor` after investment/recovery, replaced by an evolved national spirit. | TFR supports modifier; measure UI and tax revenue effects. Don't treat it as cash. |
| Office Parks | Add max one level in the verified Belgrade/capital state via a funded decision, unlocked by focus. Cost 50 PP + TFR print-money / other verified economic action equivalent; 90-day duration. | Verify capital/state mapping, open slot, building cap, and construction speed interaction. If invalid, fallback to unlock TFR develop-state action. |
| Civilian investment | Unlock existing TFR action `develop_state_economic_action_effect` after reading its full implementation. | Never call an assumed “civilian investment” token. Use TFR decision's exact effect and gate. |
| Military investment | MSGA decision funds one mil factory or assigns a TFR-recognized investment action; cost 75 PP plus a tracked economic cost only if exact variable is verified. | If no safe budget cost exists, use PP plus timed output penalty; do not mutate ledger `debt_var`. |
| Debt | Let TFR ledger update naturally. Offer decisions that improve tax/base productivity; no false direct debt reduction. | Ledger-calculated `debt_var` isn't principal. Avoid editing its output. |
| GDP/revenue | Improve underlying business value, factory capacity, state development, or applicable TFR modifier. | Do not directly set derived GDP/revenue variables. |
| Government finances | Optional choices: immediate PP/war readiness versus timed business value/tax base. Use TFR tax/business modifiers only after confirming category and budget reporting. | Check TFR monthly accounting and UI to avoid double counting. |

New mechanics recommendation: only COVID stage variable (0–3), BoP, and a one-shot US-collapse flag. Avoid creating a parallel debt/GDP ledger.

# Part J — Military industry

Current Serbia already starts with modern equipment and a developed regional force (from `SER_2020` OOB and modern tech). Phase 1 should add **one guaranteed military factory** (`Restore Defence Production`) and **one conditional factory** through paid investment or player choice. Cap total free expansion at two factories. No free divisions, no sweeping +20% production buff; one timed +5% output/efficiency benefit and army XP ~10. Re-armament should be a 2–3 year project and leave Serbia stronger defensively but still constrained in a sustained war with NATO-backed neighbors. Do not add civilian factories via focuses; use real TFR economy for industrial base growth.

# Part K — Resources

**Research conclusion:** TFR/YR reference Jadar lithium (`SER_YR_jadar_lithium`) and regional mining concepts, but mod ideas are not proof of actual deposits or state assignment. The inspected TFR history files did not yield a verified resource assignment for Serbia's owned states; exact state names/IDs and amounts remain an implementation research item. Check active `history/states` and map data before changing resource values. Serbia's factual candidates for development are copper (Bor/Majdanpek area), lithium/borates in Jadar (politically contested and not a production mine in the 2020 start), and coal/lignite.

Proposal: no new starting resources. Add only an unlockable prospecting decision after `An Independent Resource Policy`; lithium should be a **prospective deposit**, not immediately exploitable mine, with modest eventual strategic resource (e.g. 2–4 units after a long 180-day project) only if map ID and TFR resource balance validate. Copper/coal development should preferably use existing deposits and TFR local-resources modifier. Don't add rare earths/oil absent evidence. Candidate regions: Jadar/Rađevina in western Serbia; Bor/east Serbia for copper; lignite fields in Kolubara/Kostolac only if target map states make that accurate. IDs deferred pending exact state audit.

# Part L — Decisions

Costs below are proposals; any TFR economic-action effects must use verified current prerequisites and costs.

| Category/decision | Cost / duration / cooldown | Requirements and effects |
|---|---|---|
| Public Health — Targeted Testing | 35 PP / 60 days / once per stage | COVID stage 0–1; reduce stage pressure, small Streets -.02 movement toward center. |
| Public Health — Protect Essential Workers | 50 PP / 90 days / once | COVID active; improve recovery, timed industry penalty avoided; creates small fiscal pressure. |
| Public Health — Accelerated Reopening | 25 PP / immediate / 180 days | COVID stage ≤1; remove disruption sooner, but -2% stability or BoP -.03. |
| Governance — Convene the National Dialogue | 35 PP / 30 days / once | A New Decade; BoP +.04, stability +1%. |
| Governance — Emergency Public Order Measures | 25 PP / 30 days / 120 days | Protests active; BoP +.06 now; Streets penalty -2% stability for 180 days. Choice with visible warning. |
| Governance — Publish the Recovery Plan | 40 PP / 60 days / once | Reopen focus; BoP +.03, unlock recovery decisions. |
| Economy — Facilitate New Capital | TFR's verified development action; duration per TFR | Attract Capital focus; route through TFR `develop_state_economic_action_effect`; +temporary business-value idea only if action succeeds. |
| Economy — Belgrade Office Park Project | 50 PP and verified TFR action / 90 days / once | Belgrade Services focus, valid capital state; completes one `office_park` level, +.02 Business Value for 1 year. Fallback: TFR's develop-state action. |
| Economy — Morava Corridor Works | 50 PP / 120 days / once | Morava focus; state construction/supply improvements, no free civ factory. |
| Industry — Expand Defence Production | 75 PP plus explicit choice of 1 mil factory vs timed economic penalty / 120 days / once | Defence focus; factory only on completion; no repeated purchase. |
| Industry — Secure Strategic Stocks | 35 PP / 90 days / 180-day cooldown | Army Modernisation; equipment stockpile/army XP, cost shown in tooltip. |
| Resources — Jadar Survey | 50 PP / 180 days / once | Resource focus; completion grants no resource if state/evidence check fails, and explains reason; otherwise 2–4 strategic resource units after verification. |
| Geopolitics — Assess the New European Balance | 25 PP / immediate / once | Active verified US signal; fallback if event pulse missed; sets readiness flag, shows Kosovo focus condition. |

No repeated “send X” future proxy actions are active in Phase 1. Cooldowns should use decision cooldown fields and completion flags, never recurring hidden event loops.

# Part M — Events

New namespace `MSGA`. Events: `MSGA.1` opening (player-facing; start flags); `MSGA.2` outbreak status after first response choice; `MSGA.3` reopening decision consequence; `MSGA.4` protest escalation (threshold crossing once); `MSGA.5` recovery plan summary; `MSGA.6` TFR U.S. shattered-union response (one shot, sets flag); `MSGA.7` Kosovo Question capstone briefing (Phase 2 unlocked). Every event must explain the selected effect and next available action. Avoid delayed 200/360-day hidden chains from TFR Serbia unless they are explicitly visible to player.

# Part N — National spirits

Keep existing TFR Serbia spirits as baseline. MSGA only needs three evolving ideas:

| ID / concept | Effects (proposed) | Lifecycle |
|---|---|---|
| `MSGA_covid_disruption` — Pandemic Disruption | Factory output -5%, construction speed -5%; no excessive consumer-goods effects. | 180-day timed or stage-upgraded; removed at reopening milestone. |
| `MSGA_recovery_program` — Recovery Program | Business Value +.05; industrial factory capacity +.03; lasts 365 days. | Added by recovery decisions; replace/evolve once to avoid stacking. |
| `MSGA_defence_rearmament` — Defence Reorientation | Factory output +.05 only for arms; consumer goods/tax costs not simulated unless TFR can represent them. | Added on first industry focus; evolves after Kosovo unlock in later phase, not now. |

BoP modifiers belong in BoP ranges, not duplicate national spirits. COVID event choices can select one of two named temporary spirits if clearer than hidden modifiers.

# Part O — Technical architecture

Proposed submod structure (MSGA files only):

```text
descriptor.mod
common/national_focus/MSGA_SER_phase1.txt
common/bop/MSGA_SER_bop.txt
common/ideas/MSGA_SER_ideas.txt
common/decisions/categories/MSGA_SER_categories.txt
common/decisions/MSGA_SER_phase1.txt
common/scripted_effects/MSGA_SER_effects.txt
common/scripted_triggers/MSGA_SER_triggers.txt
common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt  # only if needed
common/on_actions/MSGA_SER_on_actions.txt               # additive, narrow
events/MSGA_SER_events.txt
common/ai_strategy/MSGA_SER_ai.txt                       # optional
localisation/english/MSGA_phase1_l_english.yml
gfx/interface/goals/MSGA_*.dds
gfx/interface/ideas/MSGA_*.png
```

Prefix every new ID/variable/flag with `MSGA_`; namespace `MSGA`. Depend on TFR by descriptor dependency and declare supported TFR/HOI4 versions. Do not use `replace_path`. Existing TFR BoP is `SER_milosevic_titoist_balance`; new BoP ID `MSGA_SER_streets_presidency`. TFR YR has whole-folder replace paths; compatibility should be explicit (not declared compatible unless tested). Focus tree assignment strategy and TFR election compatibility patch require final decision after load-order test. Keep TFR-owned IDs unmodified except an isolated election patch if necessary.

# Part P — Global event integration

Signal: TFR event `TFR_events_USA.txt` sets `USA_shattered_union_global` on the fracturing path; `USA_american_civil_war_global` is separately read by USA on-actions. Use the former as primary signal for “shield fallen,” subject to confirming all intended branches. `USA_gop_collapse_flag` is a party-level event and must not unlock geopolitical content. Poll a cheap trigger on existing periodic pulse / country on-action without rewriting TFR; when true, set `MSGA_US_ORDER_COLLAPSED`, fire `MSGA.6`, and one-shot `MSGA_kosovo_ready`. Fallback decision catches missed event. Expose a visible focus tooltip: “Requires the United States to have fractured.” Do not trigger war, annexations, or Balkan war in Phase 1.

# Part Q — Reliability / softlock prevention

| Progression | Trigger | Effect | Fallback / feedback / debug |
|---|---|---|---|
| Start | `tag = SER`, `NOT = { has_country_flag = MSGA_initialized }` | Initialize BoP/variables and set flag. | Startup idempotence. Debug via console inspect flag/BoP. |
| COVID advance | stage 0–3 plus focus/decision completion | Increment once, cap at 3, show event. | Completion event and stage tooltip; daily pulse can repair missing event from stage flag. |
| Election lock | Serbia election entry point triggers under TFR conditions | Prevent only player route changes; retain Vucic. | Test each election entry and protest chain; restore leader is emergency fallback. |
| BoP thresholds | BoP crosses range | Modifier activates; threshold event flag avoids repeat. | Visible range names; debug console `effect`/`eval` not required for player. |
| Economy action | TFR action's own valid trigger/effect | Call verified effect; MSGA bonus only if action completed successfully. | If no action success flag exists, use own decision completion with explicit construction check; UI validation. |
| Office Park | state 107 valid, remaining building capacity | Add one level. | If cap/invalid: offer TFR develop-state action and explain fallback. |
| U.S. fracture | global `USA_shattered_union_global` | Set local signal, one event. | Assessment decision fallback; debug via `set_global_flag USA_shattered_union_global` in test. |
| Kosovo unlock | Capstone prerequisites plus local US signal | Set `MSGA_kosovo_phase_unlocked` once. | Decision mirrors unmet conditions; one-shot briefing; never require TFR Serbia event. |
| Save/load | initialized flags/vars persist | No reapply duplicate BoP or bonuses. | Save immediately before/after each event; reload and inspect. |

# Part R — Test plan

1. Descriptor dependency/load order; test MSGA+TFR alone and with optional YR.
2. SER alone receives correct tree and no other country receives MSGA content.
3. Vucic remains country leader through each election date/event path; no global election effects.
4. BoP initializes once, displays correct sides/ranges, modifiers only at intended thresholds.
5. Every COVID choice can complete all stages; no event softlock after reload.
6. TFR economy actions have valid triggers, spend the displayed cost, and update intended TFR UI values; Office Park state/cap validated.
7. Factory construction completes once; no repeat decision, ownership/state valid.
8. Resource prospecting validates owner/state/amount; aborts safely if unavailable.
9. U.S. fracture signal checked in each US route; fallback decision catches a missed pulse.
10. Kosovo unlock occurs only after all gates; focus and next-phase feedback are explicit.
11. All decisions/events work before and after save/load.
12. Check `error.log` for missing IDs, duplicate focus IDs, invalid triggers/modifiers, localization errors, and spam. Confirm no unintended TFR or YR content disappears.

# Part S — Implementation milestones

| Milestone | Scope / acceptance |
|---|---|
| P1.0 | Descriptor + dependency + unique IDs; loads beside TFR. |
| P1.1 | Focus tree shell and localization; SER only. |
| P1.2 | Election route suppression audit and Vucic persistence test. |
| P1.3 | BoP with range modifiers and safe initialization. |
| P1.4 | COVID staged decisions/events and recovery. |
| P1.5 | TFR economy action integration and Office Park test. |
| P1.6 | Military industry and resource decision gates. |
| P1.7 | US flag pulse/fallback and one-shot event. |
| P1.8 | Kosovo capstone, local unlock flag, Phase 2 interface hook only. |
| P1.9 | Full test matrix, balance, GFX/localization polish and save/load. |

# Part T — Short future roadmap

**Phase 2:** consume `MSGA_kosovo_phase_unlocked` as the sole entry contract; create a transparent crisis escalation with clear de-escalation choices, then a separately gated war. Keep Albanian intervention and white peace as recoverable outcomes, not hidden automatic scripts.

**Phase 3:** support mechanic and RS crisis should use state/ownership triggers, explicit player-facing events, and verified capitulation outcomes. Bosnia should be a prepared opponent; treat puppet/integration as peace settlement stages, not guaranteed post-war effects.

**Phase 4:** after RS outcome, cosmetic name/state updates only on verified ownership/control conditions. A regional war requires opponents with coherent guarantees/AI and a defensive preparation window.

**Phase 5:** portray the occupation cost through existing TFR resistance/economy mechanics and offer negotiated settlement into Yugoslavia, preserving Vučić. Keep outcome based on player policy and stability, not a forced reversal.

**Phase 6:** integrate with explicit TFR European endgame flags/events discovered at implementation time; no guessed future event IDs or automatic alliance membership.

# Part U — Designer recommendations and proposed changes

1. **Simplify early Serbia content.** Focus on pandemic response, public legitimacy, recovery, and limited readiness. Keep the main tree at roughly 17 nodes and make repeatable spending decisions meaningful.
2. **Don't equate Presidency BoP with public anger alone.** Public-health choices can improve regime legitimacy or increase state coercion; preserve the possibility of an authoritarian short-term win that makes later crises costly.
3. **Do not use Serbian elections as cosmetic events with fake alternate leaders.** Disable the branch precisely, preserve non-election TFR events where possible, and test the entire `serbia.16`–`.27` chain.
4. **Avoid free “investment” rewards.** A factory is expensive; focus should unlock the choice, while TFR economy actions and PP costs provide tradeoffs. An Office Park is a real state asset, not a Business Value button.
5. **Keep Jadar prospective.** A resource focus granting lithium instantly misrepresents the 2020 start and risks strategic-resource imbalance. Make it a long, optional decision with a modest outcome.
6. **Time the Kosovo unlock after the US fracture and readiness.** The USA civil war is variable and may be late; do not force every player to wait idly. Complete Phase 1 branches while watching for the signal.
7. **Do not copy YR's compatibility model.** Its whole-folder replacement paths conflict directly with MSGA's standalone-submod requirement and future TFR updates. Copy concepts and art conventions, rewrite trigger/effect flows.
8. **Most technically fragile items:** patching Serbia's election event IDs; TFR/YR focus-tree replacement and load order; direct use of an economic scripted effect without its guards; Office Park state caps; assuming a single US flag means collapse. Resolve these with exact-version integration tests before content expansion.
9. **Improve TFR authenticity:** make the player use TFR's office parks, business value, investment and fiscal UI, rather than adding an MSGA economy sidebar or directly manipulating ledger outputs.
10. **Make first year fun:** two short decision windows with visible outcomes, one domestic legitimacy choice, one capital-vs-defence allocation, then an external geopolitical event. This introduces the core systems early without delaying the campaign behind a long focus chain.

**Core identity retained:** Vučić remains leader; future arc stays Serbia → Greater Serbian State → pragmatic Yugoslavia. The recommendation replaces a linear war-first opening with a focused state-capacity phase and an optional, legible readiness economy.

## Explicit answers to the 20 research questions

1. **Tag:** `SER`.
2. **Files to override:** no existing TFR Serbia focus tree was found; election integration may need a narrow patch after auditing `events/TFR_events_SER.txt`; otherwise add uniquely named files. YR's broad `replace_path` creates a separate conflict.
3. **Election trigger:** events `serbia.16`–`.27` hold election/protest/coup consequences; `.16` explicitly promotes the army character and disables elections, while other options set politics and election rules. `.22` is a triggered-only 2020 parliamentary event. The entry point and call sites need audit; no single timer was verified as sole trigger.
4. **Safest Vucic preservation:** suppress Serbia-only election replacement entry points in the target TFR build; don't globally disable elections. Post-promotion correction is only a backup.
5. **Economic modifiers:** yes. `TFR_ideas_SER.txt` uses `business_value_factor`, `tax_business_rate`, `tax_personal_rate`, and `industrial_capacity_factory`. No explicit GDP/debt variables were found in the inspected SER country history.
6. **Business Value:** TFR supports `business_value_factor`; it flows through economy modifier/accounting logic and is not immediate cash/PP.
7. **Office Parks:** building key `office_park`; TFR focus examples construct it via state effects. State 107 is Belgrade; `107-Kosavo.txt` is a misleading filename, while its province and English localization confirm the capital.
8. **Civilian/Military Investment:** not vanilla script effects under those names. TFR generic actions include effects such as `develop_state_economic_action_effect`; inspect and call the installed decision/action logic, don't invent names.
9. **GDP, Business Value, revenue:** verified levers include Business Value, tax modifiers and factory capacity. GDP/revenue are ledger outputs; no direct grant effect verified. State 1296 begins with 45 steel, two civs and one mil.
10. **Debt:** ledger uses `debt_var` and scorers to calculate/display amounts; do not write calculated output as principal.
11. **Current Serbia resources:** exact owned-state allocations were not verified in this research pass; inspect state history/map before changes.
12. **Real candidates:** Jadar lithium/borates as prospective, Bor/Majdanpek copper, and lignite/coal; mapping and balance remain to validate.
13. **Serbia after American collapse:** no Serbia-specific reaction found in TFR Serbia events. U.S. fracture has a global flag and USA-side on-action checks.
14. **Signal:** `USA_shattered_union_global` for a fractured U.S. route; `USA_american_civil_war_global` is related but separate. `USA_gop_collapse_flag` is not the signal.
15. **BoP reference:** vanilla Italy for concept/UI; local Serbia reference is `SER_milosevic_titoist_balance` in `common/bop/TFR_bop_SER.txt`. MSGA should have a separate BoP.
16. **Territorial loss:** one future scripted effect called on significant peace/state loss, bounded once per event; no daily loop.
17. **Focus layout:** compact TFR country trees; YR `SER_yugoslavia_reborn.txt` and `SER_yr_shared_focuses.txt` are local art/naming references, not dependencies.
18. **Duration:** recommend 35-day standard and 42-day capstone. YR's 3/5-day event-launch focuses aren't an appropriate strategic cadence.
19. **YR ideas:** economic development, capital-source tradeoffs, corridor investment, Jadar as a prospective resource question, and choices that unlock decisions.
20. **YR patterns to avoid:** broad folder `replace_path`, hidden delayed event chains, ambiguous cross-country scope, fragile transfer/wargoal outcomes, alternate leader routes, and unclear player feedback.
