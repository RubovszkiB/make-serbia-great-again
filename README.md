# Make Serbia Great Again

Serbia Phase 1 submod for **Hearts of Iron IV / The Fire Rises**. Version **0.3.0**, script prefix `MSGA_`.

## Current build

18 focuses with supplied custom artwork, the original tree layout and story progression, evolving recovery and defence programmes, Streets–Presidency politics, health measures, funded development, and preparatory Kosovo crisis decisions. Phase 1 ends at **The Kosovo Question**. No Phase 2 war operations are included.

- 18 custom 95×95 DDS icons with base and completion-shine sprites.
- Recovery starts at +5% Business Value; the economic capstone adds +3 points; project upgrades are capped at +10%.
- Belgrade gains a building slot; Morava gains immediate infrastructure; paid projects add Office Park, infrastructure, coal and a second military factory.
- Government progresses from Coordinated Government to Presidential Administration.
- Defence progresses through output, efficiency, planning, organisation recovery and lower supply consumption.
- Two strategic and five Kosovo studies record one-time findings for later crisis policy.

See [implementation report](docs/Phase1-0.3-Implementation.md) and [static validation](docs/phase1_static_validation.json). Runtime validation status is recorded separately in the report; static checks do not certify a full campaign.

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
