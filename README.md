# Make Serbia Great Again

Serbia Phase 1 submod for **Hearts of Iron IV / The Fire Rises**. Version **0.4.0**, script prefix `MSGA_`.

## Current build

18 focuses with supplied custom artwork and the original layout, meaningful TFR rewards, focus events, two timed COVID decisions, Streets–Presidency politics, funded development and a recurring Serbian Chronicle. Phase 1 ends at **The Kosovo Question** and its crisis-category unlock.

- 18 custom 95×95 DDS icons with base and completion-shine sprites.
- Permanent Productive Capital uses TFR Business Value and income growth; recovery removes TFR's Scars of Bombings spirit.
- Belgrade gains five slots, two civilian factories and an Office Park; Morava gains two infrastructure levels where capacity allows.
- Hospital support and mass vaccination each take 35 days; reopening follows vaccination.
- Government and army spirits upgrade through their existing branches; defence adds factories, equipment and strategic reserves.
- Chronicle stories use a 120–210-day delayed dispatcher with quiet weight and cooldowns; Western monitoring uses a 30-day observer that stops after reporting collapse.
- Two strategic and five Kosovo studies record one-time findings for later crisis policy.

See [implementation report](docs/Phase1-0.4-Implementation.md) and [static validation](docs/phase1_static_validation.json). No game was launched or local installation updated for this increment. Runtime tooltips, decision delivery, doctrine discount and save/load remain unverified.

## Requirements and installation

- HOI4 1.19.x; inspected version 1.19.3.
- The Fire Rises 1.0.9.1c, Workshop ID `3350890356`.
- Copy `make_serbia_great_again/` into the HOI4 user `mod/` directory.
- Place `make_serbia_great_again.mod` beside that directory and edit its `path` for your machine. The source descriptor records the development installation path.
- Enable TFR and MSGA. Yugoslavia Reborn is not a dependency and its replacements conflict with an additive co-load.
- Start a new Serbia campaign to receive every revised focus reward. Already completed focuses do not rerun their rewards in an old save.

## Artwork and development

Runtime artwork is in `make_serbia_great_again/gfx/interface/goals/`. Original user-supplied DDS/PNG assets, atlas and mapping are retained in `art/focus_icons/MSGA_TFR_focus_icons/`. The RGB24 source images are packaged as uncompressed RGBA8 DDS without cropping or changing a decoded pixel. Existing TFR/vanilla spirit and event art is referenced by ID and is not redistributed.

`tools/prepare_focus_icons.py` reproduces the lossless conversion; `tools/validate_phase1.py` checks the scripts, IDs, topology, localisation, sprites, textures and progression guards. Both use Python and Pillow.

`Phase1-Design.md` is the historical design/research proposal. `AGENTS.md` records the ongoing commit/push workflow.
