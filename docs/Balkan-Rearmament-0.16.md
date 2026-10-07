# Balkan rearmament implementation — 0.16.0

The primary installed mod was upgraded and checked before source synchronization. The 45-path increment adds 43 new paths and updates only the two existing descriptors; all 557 other previously installed files retain their hashes. The sibling launcher descriptor is also updated and retains Workshop identity 3813570241. All 602 installed/source files match. No game window or save was touched.

## 1. Local playable files and GitHub mirror

These exact relative game paths were installed into `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again` and then copied unchanged to the repository game folder. Absolute paths and SHA-256 hashes are in `balkan_rearmament_sources.json`; all-file equality is in `balkan_rearmament_sync.json`.

- `common/ai_templates/MSGA_CRO_light_infantry.txt`
- `common/decisions/MSGA_balkan_procurement.txt`
- `common/decisions/categories/MSGA_balkan_procurement_categories.txt`
- `common/ideas/MSGA_balkan_rearmament_ideas.txt`
- `common/national_focus/MSGA_ALB_rearmament.txt`
- `common/national_focus/MSGA_CRO_rearmament.txt`
- `common/on_actions/MSGA_balkan_rearmament_on_actions.txt`
- `common/scripted_effects/MSGA_balkan_rearmament_effects.txt`
- `common/scripted_triggers/00_TFR_scripted_triggers_ZZZ_generic.txt`
- `common/scripted_triggers/MSGA_balkan_rearmament_triggers.txt`
- `descriptor.mod`
- `gfx/interface/goals/MSGA_rearm_ALB_a_vulnerable_nation.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_armed_albania.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_domestic_ammunition.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_empty_the_old_depots.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_expand_military_workshops.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_look_to_ankara.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_open_the_surplus_markets.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_secure_foreign_stockpiles.dds`
- `gfx/interface/goals/MSGA_rearm_ALB_weapons_for_every_battalion.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_a_stable_croatia.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_aggressive_rearmament.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_armoured_modernisation.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_business_as_usual.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_croatia_rearmed.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_emergency_defence_budget.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_expand_hs_produkt.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_export_contracts.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_maintain_readiness.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_mass_arms_production.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_modernise_the_army.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_prepare_the_reserves.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_reactivate_duro_dakovic.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_secure_slavonia.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_support_hs_produkt.dds`
- `gfx/interface/goals/MSGA_rearm_CRO_western_procurement.dds`
- `gfx/interface/ideas/MSGA_rearm_ALB_armed_albania_spirit.dds`
- `gfx/interface/ideas/MSGA_rearm_ALB_surplus_procurement_network.dds`
- `gfx/interface/ideas/MSGA_rearm_CRO_croatia_rearmed_spirit.dds`
- `gfx/interface/ideas/MSGA_rearm_CRO_croatian_arms_exports.dds`
- `history/states/109-Eastern Croatia.txt`
- `history/units/CRO_2020.txt`
- `interface/MSGA_balkan_rearmament_assets.gfx`
- `localisation/english/MSGA_balkan_rearmament_l_english.yml`
- `make_serbia_great_again.mod`

The sibling `make_serbia_great_again.mod` launcher points to the primary runtime. GitHub additionally receives the installer, validator, synchronizer, these reports and AGENTS workflow entry; `validation_history.py` recognizes exact approved hashes. `validate_bosnia.py` now unwraps existing decision-presentation wrappers before its old comparison, using the existing normalizer. No Bosnia gameplay file changed.

## 2–3. Focus IDs

| Country | Focus ID | Days | Prerequisites |
| --- | --- | --- | --- |
| ALB | `MSGA_ALB_a_vulnerable_nation` | 21 |  |
| ALB | `MSGA_ALB_open_the_surplus_markets` | 28 | `MSGA_ALB_a_vulnerable_nation` |
| ALB | `MSGA_ALB_empty_the_old_depots` | 28 | `MSGA_ALB_open_the_surplus_markets` |
| ALB | `MSGA_ALB_expand_military_workshops` | 35 | `MSGA_ALB_a_vulnerable_nation` |
| ALB | `MSGA_ALB_domestic_ammunition` | 35 | `MSGA_ALB_expand_military_workshops` |
| ALB | `MSGA_ALB_weapons_for_every_battalion` | 35 | `MSGA_ALB_empty_the_old_depots`, `MSGA_ALB_domestic_ammunition` |
| ALB | `MSGA_ALB_look_to_ankara` | 35 | `MSGA_ALB_weapons_for_every_battalion` |
| ALB | `MSGA_ALB_secure_foreign_stockpiles` | 35 | `MSGA_ALB_weapons_for_every_battalion` |
| ALB | `MSGA_ALB_armed_albania` | 35 | `MSGA_ALB_look_to_ankara`, `MSGA_ALB_secure_foreign_stockpiles` |
| CRO | `MSGA_CRO_business_as_usual` | 35 |  |
| CRO | `MSGA_CRO_support_hs_produkt` | 35 | `MSGA_CRO_business_as_usual` |
| CRO | `MSGA_CRO_export_contracts` | 35 | `MSGA_CRO_support_hs_produkt` |
| CRO | `MSGA_CRO_maintain_readiness` | 35 | `MSGA_CRO_business_as_usual` |
| CRO | `MSGA_CRO_modernise_the_army` | 35 | `MSGA_CRO_maintain_readiness` |
| CRO | `MSGA_CRO_a_stable_croatia` | 28 | `MSGA_CRO_export_contracts`, `MSGA_CRO_modernise_the_army` |
| CRO | `MSGA_CRO_aggressive_rearmament` | 21 |  |
| CRO | `MSGA_CRO_emergency_defence_budget` | 28 | `MSGA_CRO_aggressive_rearmament` |
| CRO | `MSGA_CRO_expand_hs_produkt` | 35 | `MSGA_CRO_emergency_defence_budget` |
| CRO | `MSGA_CRO_mass_arms_production` | 35 | `MSGA_CRO_expand_hs_produkt` |
| CRO | `MSGA_CRO_reactivate_duro_dakovic` | 35 | `MSGA_CRO_emergency_defence_budget` |
| CRO | `MSGA_CRO_armoured_modernisation` | 35 | `MSGA_CRO_reactivate_duro_dakovic` |
| CRO | `MSGA_CRO_western_procurement` | 35 | `MSGA_CRO_mass_arms_production`, `MSGA_CRO_armoured_modernisation` |
| CRO | `MSGA_CRO_prepare_the_reserves` | 28 | `MSGA_CRO_western_procurement` |
| CRO | `MSGA_CRO_secure_slavonia` | 28 | `MSGA_CRO_western_procurement` |
| CRO | `MSGA_CRO_croatia_rearmed` | 35 | `MSGA_CRO_prepare_the_reserves`, `MSGA_CRO_secure_slavonia` |

Both countries previously selected TFR’s empty generic tree. New country-scored mini-trees preserve that generic definition and every unrelated country tree. Existing saves still on `generic_focus` receive the appropriate tree on startup with completed focuses kept. Existing special focus contexts are not forcibly replaced. Each focus has an authored reward tooltip and a guarded real reward or concrete contract unlock; there are no placeholder focuses. Croatian peaceful and emergency phases are independent roots, allowing the AI to pivot without first completing the peaceful programme.

## 4. National spirit IDs

| ID | Name | Modifiers |
| --- | --- | --- |
| `MSGA_ALB_surplus_procurement_network` | Surplus Procurement Network | `income_growth_factor = 0.01`, `business_value_factor = 0.02`, `industrial_capacity_factory = 0.02` |
| `MSGA_ALB_armed_albania` | Armed Albania | `army_defence_factor = 0.05`, `army_org_factor = 0.05`, `mobilization_speed = 0.05` |
| `MSGA_ALB_workshop_expansion` | Military Workshop Expansion | `production_speed_arms_factory_factor = 0.05` |
| `MSGA_ALB_domestic_ammunition` | Domestic Ammunition | `industrial_capacity_factory = 0.05` |
| `MSGA_ALB_battalion_readiness` | Weapons for Every Battalion | `army_org_factor = 0.05`, `land_reinforce_rate = 0.05` |
| `MSGA_CRO_business_confidence` | Business Confidence | `income_growth_factor = 0.01` |
| `MSGA_CRO_hs_produkt_support` | Support for HS Produkt | `industrial_capacity_factory = 0.02` |
| `MSGA_CRO_arms_exports` | Croatian Arms Exports | `industrial_capacity_factory = 0.03`, `income_growth_factor = 0.02`, `business_value_factor = 0.05` |
| `MSGA_CRO_training_readiness` | Training Readiness | `training_time_army_factor = -0.05` |
| `MSGA_CRO_stable_industry` | A Stable Croatia | `industrial_capacity_factory = 0.03` |
| `MSGA_CRO_emergency_construction` | Emergency Defence Construction | `production_speed_arms_factory_factor = 0.05` |
| `MSGA_CRO_western_procurement_support` | Western Procurement Support | `income_growth_factor = 0.01` |
| `MSGA_CRO_reserve_preparation` | Reserve Preparation | `recruitable_population_factor = 0.05`, `mobilization_speed = 0.1` |
| `MSGA_CRO_rearmed` | Croatia Rearmed | `industrial_capacity_factory = 0.075`, `army_org_factor = 0.05`, `army_defence_factor = 0.05`, `production_factory_max_efficiency_factor = 0.05` |

Workshop expansion, Albanian ammunition, Croatian business confidence, emergency construction and Western procurement support are exactly 180 days. Armed Albania replaces Battalion Readiness, retaining +5% organisation rather than stacking another +5%; final defence and mobilisation bonuses remain modest. Four supplied national-spirit compositions are reused for fourteen coherent programme icons.

## 5, 10–11. One-time contracts and exact equipment

| Decision ID | Treasury $B | Days | Required focus | Exact delivery (type / amount / producer) |
| --- | --- | --- | --- | --- |
| `MSGA_ALB_purchase_old_eastern_rifles` | 0.4 | 10 | `MSGA_ALB_a_vulnerable_nation` | `infantry_equipment_1` / 1800 / SOV |
| `MSGA_ALB_acquire_old_mortars` | 0.5 | 14 | `MSGA_ALB_open_the_surplus_markets` | `artillery_equipment_1` / 60 / SOV; `support_equipment_1` / 40 / ALB |
| `MSGA_ALB_buy_used_military_trucks` | 0.6 | 14 | `MSGA_ALB_open_the_surplus_markets` | `motorized_equipment_1` / 120 / SOV |
| `MSGA_ALB_turkish_small_arms_contract` | 0.9 | 21 | `MSGA_ALB_look_to_ankara` | `infantry_equipment_3` / 1600 / TUR; `support_equipment_1` / 60 / TUR |
| `MSGA_ALB_acquire_modern_at_weapons` | 1.1 | 21 | `MSGA_ALB_secure_foreign_stockpiles` | `anti_tank_equipment_2` / 120 / TUR |
| `MSGA_ALB_purchase_turkish_armoured_vehicles` | 1.4 | 30 | `MSGA_ALB_look_to_ankara` | `light_mechanized_equipment_2` / 60 / TUR |
| `MSGA_CRO_nato_small_arms_package` | 1.2 | 21 | `MSGA_CRO_western_procurement` | `infantry_equipment_3` / 1800 / USA; `support_equipment_1` / 80 / USA |
| `MSGA_CRO_european_artillery_contract` | 1.4 | 24 | `MSGA_CRO_western_procurement` | `artillery_equipment_2` / 96 / GER |
| `MSGA_CRO_american_ifv_package` | 2.4 | 35 | `MSGA_CRO_armoured_modernisation` | `mechanized_equipment_2` / 70 / USA |
| `MSGA_CRO_german_armour_contract` | 2.8 | 45 | `MSGA_CRO_armoured_modernisation` | `modern_tank_equipment_3` / 40 / GER |
| `MSGA_CRO_modern_at_package` | 1.1 | 21 | `MSGA_CRO_western_procurement` | `anti_tank_equipment_2` / 120 / USA |

**German DLC adaptation:** with No Step Back, the German contract delivers 40 `modern_tank_chassis_1`, producer GER, `variant_name = "Leopard 2A5"`, referring to the already existing TFR German design. Without NSB it delivers 40 `modern_tank_equipment_3`. Germany must exist at start and delivery; disappearance cancels/refunds the pending contract. The native `variant_name` stockpile syntax is also used in the installed game’s Ethiopian equipment-delivery event. No variant or equipment ID was invented.

Each start callback checks Treasury, focus completion, country status, the completed marker and a shared pending-shipment lock before reserving `income_var_temp = -cost` through native `add_income`. Persistent pending flags survive model serialization. Delivery requires that pending flag and absence of the completed flag, adds equipment once, sets a permanent completed marker and releases reservations. Cancellation refunds once and permits a fresh attempt; completing a purchase permanently hides it and prevents any subsequent charge/reward. There are no cooldown purchases or repeatable contracts. Cost is Treasury rather than PP (native decision `cost = 0`). Tooltips state price, days, equipment, unlock requirements and one-time nature.

Direct focus deliveries:

- `MSGA_ALB_empty_the_old_depots`: 1500 `infantry_equipment_1` (SOV), 60 `artillery_equipment_1` (SOV), 75 `support_equipment_1` (ALB).
- `MSGA_ALB_domestic_ammunition`: 25 `support_equipment_1` (ALB).
- `MSGA_CRO_modernise_the_army`: 50 `support_equipment_1` (CRO).
- `MSGA_CRO_expand_hs_produkt`: 1200 `infantry_equipment_2` (CRO).
- `MSGA_CRO_mass_arms_production`: 2200 `infantry_equipment_2`, 120 `support_equipment_1`, 60 `artillery_equipment_1` (all CRO).

## 6–8. Starting industry and Croatian template

Croatia Proper is state **109**, despite its native filename `109-Eastern Croatia.txt`. It originally has **0** MIL. Its history now has **2** MIL; the existing **1** MIL in Dalmatia (103) is retained, giving **3 nationally**. No factory is moved. Ownership, cores, infrastructure, civilian/office buildings, slots and every other state-history field are preserved. Factories are not granted by startup logic and cannot duplicate on reload. Albania retains exactly **1 starting MIL**, its native country/state history and its original two formations. These starting-history/OOB changes require a fresh campaign.

The internal and displayed new template name is **Croatian Light Infantry**; the English localization reference is `MSGA_CRO_light_infantry`. Its exact definition is:

```hoi4
division_template = { name = "Croatian Light Infantry" regiments = { infantry = { x = 0 y = 0 } infantry = { x = 0 y = 1 } artillery_brigade = { x = 1 y = 0 } } support = { } }
```

Native battalion keys: `infantry` at (0,0) and (0,1), and `artillery_brigade` at (1,0). `infantry` belongs to the native infantry regiment group and `category_light_infantry`; Croatia’s existing `infantry_weapons1` technology enables it. The artillery uses the native artillery regiment. The support block is empty. The original OOB definitions and original two armoured/mechanised divisions are unchanged; no extra unit is spawned. A moderate Croatian-only native AI template entry uses role `infantry`, 2+1 target regiments, no support, high match requirement and no in-field upgrade, supporting affordable recruitment while retaining the original formations. Equipment/manpower availability still governs actual training. Separate screenshot files were not supplied; the task’s explicit composition and native state data were the implementation references.

## 9. Bosnian-war unlock

`MSGA_croatian_bosnia_escalation = { SER = { has_country_flag = MSGA_bosnia_intervened } }`. Existing `MSGA_join_srpska_war` sets that flag only after native same-war intervention succeeds and `has_war_with = BOS` becomes true. It is not the earlier `MSGA_bosnian_war_started` uprising flag. The intervention marker persists through scripted settlement, so the Croatian branch does not vanish when the Bosnia war ends. Every emergency focus requires this marker. Before intervention the branch is unavailable. After intervention emergency AI weights are 550–1000 and peaceful weights drop by a factor of 0.01; peaceful focuses remain accessible. No Serbia/Bosnia event or settlement was altered.

## 12–18. Actual production lock, native files, override and safeguards

TFR’s `common/on_actions/00_TFR_on_actions_ZZZ_startup.txt` selects AI countries with `is_relavent_tag = no` and executes three restrictions: `add_ideas = ai_disabled_production`, `country_lock_all_division_template = yes`, and `set_research_slots = 0`. The hidden idea is in `common/ideas/TFR_ideas_ZZZ_mishmash.txt`: construction speed, military output and dockyard output are each -9999; consumer goods factor is +10 and conscription is -1. Removing its label alone would change nothing.

The relevance trigger is defined in `common/scripted_triggers/00_TFR_scripted_triggers_ZZZ_generic.txt`. MSGA overrides that one file with only seven extra tag clauses in the existing relevance OR. All other trigger definitions are identical to upstream. This prevents the startup triple lock and enables native low-factory AI and economic decision/strategy systems in `common/ai_strategy/TFR_ai_strategy_ZZZ.txt` and `common/on_actions/00_TFR_on_actions_ZZZ_money.txt`, without altering other tags. No original TFR installation file was edited.

Exact whitelist: **SLV** Slovenia; **CRO** Croatia; **BOS** Bosnia and Herzegovina; **MNT** Montenegro; **KOS** Kosovo; **ALB** Albania; **MAC** Macedonia. HRZ is a separate native tag and is not silently added to the requested whitelist.

For an existing save, country-scoped startup cleanup removes the real hidden idea, clears the country-level template lock using the same native command with `no`, and restores the native 3/4 research slots only if the current count is zero. Existing extra research slots are retained. A weekly guard acts only if the restriction exists again or the one-time restoration flag is absent. There is no daily polling and no factory/army grant in cleanup.

The installed TFR search finds production-lock additions only in generic startup and `common/decisions/TFR_decisions_ISR.txt`; the latter is scoped to Israel/Middle Eastern countries, not the seven tags. Country-template lock paths in generic/US startup, USA effects, the English/Syrian events and French victory are country-specific and were inspected; no later Balkan-specific relock path was found. Weekly restoration removes any renewed hidden production idea. The targeted validator checks the exact native override, all startup commands, all current production-idea application paths, every tag’s restoration, retention of acquired research slots, eight modeled weeks and unrelated tag preservation.

**Capability confirmed statically:** the script restrictions on production, construction, conscription and recruitment are absent for the whitelist, the native AI strategy systems are available, and Croatia/Albania’s existing production technologies and templates are retained. This permits factory assignment, lines, construction, training and reinforcement through normal native AI. **Actual engine assignment, construction ticks, recruitment and reinforcement have not been observed**; they remain the user’s test, not a claimed campaign result.

## 19. Native mechanics and location adaptations

- Treasury uses native `income_var_temp`/`add_income`, not a fake treasury command, PP substitution or debt. Albanian assistance is $1B at entry and $0.5B at foreign-stockpile access; total support cannot fund all $4.9B contracts immediately.
- Income Growth uses `income_growth_factor`; Business Value uses `business_value_factor`, not the native development-law-only `business_value` field.
- Contracts have the requested fixed negotiated prices instead of an unsupported generic purchase-cost modifier. AI requires an additional $0.25B Albanian / $0.5B Croatian reserve and favors cheap purchases; one shared shipment reservation prevents simultaneous purchases.
- Modest general output replaces an unproven equipment-specific production bonus. Research bonuses use native `infantry_weapons` and `armor` categories, one use at 50%.
- Direct factory rewards use native shared slots, instant construction, before/after `building_level@arms_factory` counters and rejection logging; introduced slots are rolled back on rejection. State ownership/control and capacity must hold. The final Croatian programme adds three more MIL, giving six nationally in the model; Albania’s workshops give two nationally.
- Slavonia is represented within state 109 in this TFR map. Province **3627** is the easternmost native province by actual province-map centroid. It receives two bunker levels, not random forts elsewhere. State 109 receives one infrastructure level up to the native maximum. Membership and real map geometry are recorded and checked.
- Supplied 25 focus and four national-spirit PNGs are converted to established MSGA canvases (95×85 focus, 64×64 idea), DXT5 DDS, using inspected current installed examples. TFR itself uses varied PNG/DDS canvases. Focus and shine sprites are declared; fourteen ideas reuse the four supplied spirit images. Native military/support/truck/tank decision and military-operation category icons are reused. No custom decision graphic or added yellow ring was generated.

## 20. Validation and smoke result

Passed on the actual installed mod:

- `validate_balkan_rearmament.py`: syntax, references, localization, 25 focus prerequisites/durations/tooltips/AI factors, 11 one-time contracts, 14 ideas/modifiers, 29 DDS/GFX, native equipment IDs/DLC design, states, immutable original OOB, factories, exact AI override and producer-lock application paths.
- Short deterministic smoke: both full country focus routes; 12 contract/DLC delivery models; 26 negative cases including insufficient Treasury, cancellation/refund/retry, concurrent purchases, missing German supplier, lost state control and native construction rejection.
- `validate_phase1.py`: existing shared installed-content checks passed.
- `validate_bosnia.py`: existing intervention/settlement regression passed after its pre-existing presentation-only comparison was normalized. Gameplay remains unchanged.

The smoke test executes actual parsed scripts in a deterministic model; it is **not a HOI4 engine run**. No long campaign, game-window automation, game restart or save edit was performed. Actual AI focus timing/production/construction/recruitment, NSB tank delivery usability, rendering and engine save/load remain untested. Restart the game and use a fresh campaign for starting factories/template verification. No requested script feature remains intentionally unimplemented.
