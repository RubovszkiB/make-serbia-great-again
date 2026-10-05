# Make Serbia Great Again

Serbia campaign submod for **Hearts of Iron IV / The Fire Rises**. Version **0.11.0**, script prefix `MSGA_`.

## Current build

24 early focuses, four Kosovo campaign focuses, seven post-Kosovo focuses, thirteen pre-Bosnia/Bosnian war focuses and twelve post-Bosnia focuses. The Kosovo Question replaces the early tree with the campaign chapter; confirmed ownership of both Kosovo states leads to integration and reconstruction. Completing The Serbian Question loads the Bosnia preparation tree once the approved war, integration and reconstruction requirements are met. Three narrative events continue independently; neither these events nor the optional final reconstruction decision blocks Bosnia. Successful Bosnia settlement loads the postwar chapter directly. Continuous early progression finishes Watch the Western Shield after 756 focus-days; Kosovo availability still depends on the actual TFR collapse signal.

- 24 custom 95×95 DDS focus icons with base and completion-shine sprites; four supplied 60×68 spirit icons.
- Permanent Productive Capital uses TFR Business Value and income growth; recovery removes TFR's Scars of Bombings spirit.
- Belgrade gains five slots, two civilian factories and an Office Park; Morava gains two infrastructure levels where capacity allows.
- Three one-time COVID decisions delay a pending outbreak by 120, 130 and 150 days. Vaccination becomes available on 1 January 2021, takes 20 days and permanently cancels a pending outbreak. Reopening proceeds independently.
- Internal Investment adds exactly $2B nominal debt, two civilian factories in Vojvodina and the native monthly development modifier. Infrastructure respects TFR's level-five cap: the 2020 starting level of three can gain two effective levels. A 30-day southern investment adds $1B debt, two slots and one civilian factory in the Niš state.
- New political focuses halve the emigration penalties, add a 75-day organisation penalty and conclude with National Consensus.
- The exact volunteer screenshot template supplies four one-time formations through a focus and three 20-day decisions. The exact armoured-mechanised screenshot template is available at startup without a free division or equipment.
- Government and army spirits upgrade through their existing branches; defence adds factories, equipment and strategic reserves.
- Chronicle stories use a 120–210-day delayed dispatcher with quiet weight and cooldowns; Western monitoring uses a 30-day observer that stops after reporting collapse.
- Two strategic-review decisions remain. The five unapproved Kosovo preparation studies have been removed.
- Three 7-day campaign preparations lead through the General Staff, southern mobilisation and Operation Return events. Both Kosovo states start with a -30% attacker penalty and -10% movement; separate 25 CP, 14-day decisions remove each state's penalty.
- Actual control of Pristina triggers independent Albanian intervention after Albania leaves NATO. Kosovo capitulation immediately annexes Kosovo, transfers states 785 and 1305 to Serbia, white-peaces the campaign's Albanian opponent and removes temporary mechanics. No conquest of Albania is required.
- The three volunteer recruitment decisions cost exactly $2B each from TFR's treasury; the equipment reserve package costs $3B. These four decisions cost zero political power. Existing equipment quantities and recruitment durations are preserved.
- Twelve supplied event pictures, four campaign focus icons and three mechanic icons are integrated through additive sprite definitions.
- Postwar integration cores northern state 1305 first and adds exactly $1B nominal government debt before coring the remaining state 785. Consolidation removes TFR's actual `SER_rebellion_of_kosovo` spirit.
- Both reconstruction focuses preserve their civilian factories, add capped infrastructure and 5% native industrial-development progress each. Rebuilding repairs local buildings and applies 180-day construction, repair and monthly development bonuses; Pristina retains its Office Park. Its event offers paid state investment or private capital. Both focuses are required for A Lasting Peace. The optional final reconstruction decision costs 50 PP and $1B treasury and ends temporary measures.
- One $2B, zero-PP decision creates the 16-width Kosovska Mehanizovana Brigada with native equipment requirements, including 14 reserve T-55A tanks; equipment is supplied directly to the formation without a duplicate stockpile package.
- Serbia starts with a saved, producible M-84A using legal starting modules (base cost 8.51), plus BVP M-80A and BTR-80A variants. Country-specific localisation names later IFV/APC models BVP M-80AB1 and Lazar 3.
- Seven supplied postwar focus icons, fourteen event pictures and one decision icon accompany reconstruction.
- Bosnia preparation branches join after public mobilisation and six native 10% Military Development grants (`0.10` each). Rearmament lasts 200 days; both aircraft procurement offers charge TFR's treasury and final preparations require actual delivery. Logistics unlocks basic trains before granting its 15 trains and 150 utility vehicles.
- Territorial Defence and Srpska Guard are editable templates with exactly three plain militia battalions. Belgrade receives one formation; five paid regional decisions cost $0.5B and deliver one formation after 14 days.
- Srpska uses native tag `SRP`, Milorad Dodik and native core states 848/849/850. Its three militia divisions face Bosnia's unchanged four regular divisions. Bosnia declares war immediately after independent release. Serbia receives the intervention event after one day, creates the Serbian Alliance, adds SRP and joins its existing war with `add_to_war`.
- Dedicated Kosovo/Srpska Last Stand spirits target a capped 99% surrender threshold. Bosnia's defeat triggers a guarded settlement with BOS (104), HRZ (851) and SRP (848/849/850) as Serbian puppets. Exactly 100 days later, Serbia can annex peaceful SRP for $1B additional national debt without treasury cost or new Serbian cores, or preserve it as a puppet with no debt change. Old queued 70-day prompts become hidden dispatchers that respect the new deadline.
- 24 supplied Bosnia DDS textures and seven additional reconstruction/war/settlement event pictures are used directly. Four local copies of native TFR scripts/history gate conflicting chains or replace only the obsolete Srpska OOB; validation compares them to their installed upstream source. A minimal HRZ history override corrects its capital and leader. Workshop TFR files remain untouched.

- The post-Bosnia chapter has twelve 14-day focuses (168 focus-days), a three-focus opening and military/political/economic columns. Completing all three final focuses automatically triggers Serbia: A Regional Power.
- Two one-time decisions each charge 25 PP and $0.25B treasury for two three-militia territorial brigades. Their Bosnian/Herzegovinian identity is retained, while Serbia owns and commands all four divisions.
- Srpska Territorial Defence costs $0.5B treasury and zero PP. Its 16-width template and tank/IFV/APC package reuse the Kosovo brigade implementation. Serbian command preserves it across Srpska annexation; the native Srpska army also transfers with `transfer_troops = yes`.
- Postwar rewards include bounded $0.5B debt relief, two civilian factories, an office park, capped western infrastructure, native development progress, the existing presidency BOP shift and fractional political/economic spirits. Subject cooperation skips annexed Srpska safely.
- Twelve supplied focus icons, sixteen event pictures and three decision icons are integrated byte-for-byte from the 100-day package; the shared Srpska question sprite has one definition.

The Regional Power milestone opens the two-focus Southern Question tree. Both rejections lead, after three days, to the Calculation Failed and an independent Croatia-led Zagreb–Tirana Pact (CRO/ALB/SLV/MAC/MNT). One day later, the Pact receives 22 emergency formations and Belgrade receives two militia and a military factory. Only then does the ten-focus planning tree appear. Its western, southern and reserve branches merge into Operation Thunder and Break the Ring. Serbia opens one shared war against all five members, with a ten-day Surprise Attack. There are no later-war mechanics in this increment; existing Kosovo, Bosnia and post-Bosnia content remains intact.

The primary runtime is `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`. The [current sync inventory](docs/encirclement_sync.json) verifies 261 identical project/runtime files and the launcher descriptor. All seven installed validators passed. The [pre-war report](docs/encirclement_validation.json) covers 96 scenarios, and six [regression reports](docs/Balkan-Encirclement-0.11.md) preserve the earlier campaign, including the 100-day Srpska question. [Native map adjacency](docs/encirclement_map_validation.json) verifies the Kosovo border-fort locations. The user reserved in-game testing for later. No fresh engine playthrough, clean engine log, event rendering or engine save/load is certified for 0.11.

## Requirements and installation

- HOI4 1.19.x; inspected version 1.19.3.
- The Fire Rises 1.0.9.1c, Workshop ID `3350890356`.
- Copy `make_serbia_great_again/` into the HOI4 user `mod/` directory.
- Place `make_serbia_great_again.mod` beside that directory and edit its `path` for your machine. The source descriptor records the development installation path.
- Enable TFR and MSGA. Yugoslavia Reborn is not a dependency and its replacements conflict with an additive co-load.
- Start a new Serbia campaign to receive every revised focus reward. Already completed focuses do not rerun their rewards in an old save.

For development, deploy with `tools/deploy_local.py`, then run `tools/validate_phase1.py`, `tools/validate_kosovo.py`, `tools/validate_post_kosovo.py`, `tools/validate_bosnia.py`, `tools/validate_transition.py`, `tools/validate_post_bosnia.py` and `tools/validate_encirclement.py` with `--mod-root "C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again"`. Local deployment and validation precede GitHub commits and pushes. The deployment script preserves the existing Workshop identity, checks the descriptor path and verifies source/runtime SHA-256 hashes. See [0.11 technical report](docs/Balkan-Encirclement-0.11.md), [0.10 implementation notes](docs/Post-Bosnia-0.10.md), [transition diagnosis](docs/Kosovo-Bosnia-Transition.md) and [native source/asset mapping](docs/bosnia_sources.json).

## Artwork and development

Runtime artwork is in `make_serbia_great_again/gfx/interface/` and `make_serbia_great_again/gfx/event_pictures/`. Original user-supplied assets are retained in `art/focus_icons/MSGA_TFR_focus_icons/` and `art/new_early_assets/MSGA_new_assets_pack/`, including both authoritative division screenshots. Converted DDS pixels match the supplied PNGs; the seven new event DDS files match the supplied ZIP bytes directly. Existing TFR/vanilla art is referenced by ID and is not redistributed.

`tools/prepare_focus_icons.py` reproduces the lossless conversion; `tools/validate_phase1.py` checks the scripts, IDs, topology, localisation, sprites, textures and progression guards. Both use Python and Pillow.

`Phase1-Design.md` is the historical design/research proposal. `AGENTS.md` records the ongoing commit/push workflow.
