# Make Serbia Great Again

Serbia campaign submod for **Hearts of Iron IV / The Fire Rises**. Version **0.6.0**, script prefix `MSGA_`.

## Current build

24 early focuses, four Kosovo campaign focuses and one intentionally unavailable post-war shell focus. The Kosovo Question immediately replaces the early tree with the campaign chapter; confirmed ownership of both Kosovo states completes the victory focus and leads to the post-war tree. Continuous early progression finishes Watch the Western Shield after 756 focus-days; Kosovo availability still depends on the actual TFR collapse signal.

- 24 custom 95×95 DDS focus icons with base and completion-shine sprites; four supplied 60×68 spirit icons.
- Permanent Productive Capital uses TFR Business Value and income growth; recovery removes TFR's Scars of Bombings spirit.
- Belgrade gains five slots, two civilian factories and an Office Park; Morava gains two infrastructure levels where capacity allows.
- Three one-time COVID decisions delay a pending outbreak by 120, 130 and 150 days. Vaccination becomes available on 1 January 2021, takes 20 days and permanently cancels a pending outbreak. Reopening proceeds independently.
- Internal Investment adds exactly $2B nominal debt, two civilian factories in Vojvodina and the native monthly development modifier. Infrastructure respects TFR's level-five cap: the 2020 starting level of three can gain two effective levels. A 30-day southern investment adds $1B debt, two slots and one civilian factory in the Niš state.
- New political focuses halve the emigration penalties, add a 75-day organisation penalty and conclude with National Consensus.
- The exact volunteer screenshot template supplies four one-time formations through a focus and three 20-day decisions. The exact armoured-mechanised screenshot template is available at startup without a free division or equipment.
- Government and army spirits upgrade through their existing branches; defence adds factories, equipment and strategic reserves.
- Chronicle stories use a 120–210-day delayed dispatcher with quiet weight and cooldowns; Western monitoring uses a 30-day observer that stops after reporting collapse.
- Two strategic and five Kosovo studies record one-time findings for later crisis policy.
- Three 7-day campaign preparations lead through the General Staff, southern mobilisation and Operation Return events. Both Kosovo states start with a -30% attacker penalty and -10% movement; separate 25 CP, 14-day decisions remove each state's penalty.
- Actual control of Pristina triggers independent Albanian intervention after Albania leaves NATO. Kosovo capitulation immediately annexes Kosovo, transfers states 785 and 1305 to Serbia, white-peaces the campaign's Albanian opponent and removes temporary mechanics. No conquest of Albania is required.
- The three volunteer recruitment decisions cost exactly $2B each from TFR's treasury; the equipment reserve package costs $3B. These four decisions cost zero political power. Existing equipment quantities and recruitment durations are preserved.
- Twelve supplied event pictures, four campaign focus icons and three mechanic icons are integrated through additive sprite definitions.

The primary runtime is `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`. See [deployment inventory](docs/local_deployment.json), [exact changed runtime paths](docs/kosovo_files_deployed.json), [installed early validation](docs/local_runtime_validation.json), [installed campaign validation](docs/local_kosovo_validation.json), [fresh engine load](docs/local_engine_validation.json) and [Kosovo implementation report](docs/Kosovo-Campaign-0.6.md). Static and script-flow tests do not certify gameplay or save/load.

## Requirements and installation

- HOI4 1.19.x; inspected version 1.19.3.
- The Fire Rises 1.0.9.1c, Workshop ID `3350890356`.
- Copy `make_serbia_great_again/` into the HOI4 user `mod/` directory.
- Place `make_serbia_great_again.mod` beside that directory and edit its `path` for your machine. The source descriptor records the development installation path.
- Enable TFR and MSGA. Yugoslavia Reborn is not a dependency and its replacements conflict with an additive co-load.
- Start a new Serbia campaign to receive every revised focus reward. Already completed focuses do not rerun their rewards in an old save.

For development, deploy with `tools/deploy_local.py`, then run both `tools/validate_phase1.py` and `tools/validate_kosovo.py` with `--mod-root "C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again"`. Local deployment and validation precede GitHub commits and pushes. The deployment script preserves the existing Workshop identity, checks the descriptor path and verifies source/runtime SHA-256 hashes.

## Artwork and development

Runtime artwork is in `make_serbia_great_again/gfx/interface/`. Original user-supplied assets are retained in `art/focus_icons/MSGA_TFR_focus_icons/` and `art/new_early_assets/MSGA_new_assets_pack/`, including both authoritative division screenshots. Runtime DDS pixels match the supplied PNGs. Existing TFR/vanilla art is referenced by ID and is not redistributed.

`tools/prepare_focus_icons.py` reproduces the lossless conversion; `tools/validate_phase1.py` checks the scripts, IDs, topology, localisation, sprites, textures and progression guards. Both use Python and Pillow.

`Phase1-Design.md` is the historical design/research proposal. `AGENTS.md` records the ongoing commit/push workflow.
