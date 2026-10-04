# Make Serbia Great Again

Serbia content submod for **Hearts of Iron IV / The Fire Rises**. Script prefix: `MSGA_`.

## Current development state

Phase 1 covers the January 2020 opening through the Kosovo crisis dossier. The current source contains 18 focuses, 11 events, a Streets–Presidency Balance of Power, short COVID decisions, TFR-funded development projects, Business Value, Office Park development, military preparation, resource programmes, and an American-fracture observer.

This is a development build. A Serbia campaign displayed the redesigned tree, but the gameplay acceptance checks are incomplete. The in-game review found that `set_politics` needs `ruling_party` alongside the election setting. That fix and revised health/protest icons are in this repository's source; they had not been synced to the installed mod when testing was interrupted. Economic results, project completion, save/load, and final global progression still require verification.

Phase 2 military operations and war goals are not implemented.

## Requirements and installation

- HOI4 1.19.x; inspected game version: 1.19.3.
- The Fire Rises; inspected Workshop version: 1.0.9.1c, Workshop ID `3350890356`.
- Copy `make_serbia_great_again/` into the HOI4 user `mod/` directory.
- Put `make_serbia_great_again.mod` beside the mod directory and update its `path` for your machine. The source copy currently records the development machine's path.
- Enable TFR and MSGA in the launcher. Yugoslavia Reborn is not required; its folder replacements conflict with an additive co-load.

## Project files

- `make_serbia_great_again/`: mod source and development notes.
- `Phase1-Design.md`: original design and installed-file research; historical proposals can differ from the current implementation.
- `AGENTS.md`: project workflow and ongoing GitHub upload instruction.

Existing TFR and vanilla artwork is referenced by GFX ID. Their assets are not distributed here.

