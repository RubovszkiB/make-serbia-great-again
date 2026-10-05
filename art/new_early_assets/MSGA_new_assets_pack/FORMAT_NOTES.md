# HOI4/TFR graphics format notes

Checked against the current `make-serbia-great-again` GitHub project.

## Focuses
The existing MSGA focus pipeline stores runtime focus icons under:

`gfx/interface/goals/`

The current repository uses:
- **95 × 95 px**
- `.dds`
- uncompressed **RGBA8**
- explicit alpha
- matching `SpriteType` entries in `interface/*.gfx`

This pack follows that same 95×95 DDS convention.

## National spirits
HOI4's politics UI uses national-spirit slots sized **60 × 68 px**.
This pack stores the new national-spirit icons under:

`gfx/interface/ideas/`

as **60 × 68 DDS RGBA** images and includes a ready-to-merge `.gfx` sprite file.

## Source/previews
PNG copies are included only for inspection/editing. Runtime should use the DDS files.
