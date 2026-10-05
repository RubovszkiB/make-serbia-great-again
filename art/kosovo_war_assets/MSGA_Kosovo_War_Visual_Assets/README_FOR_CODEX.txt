MSGA – Kosovo War Visual Assets
================================

CONTENTS
- preview/: full approved visual preview
- source_png/focus/: 4 separated focus artworks
- source_png/events/: 12 separated event artworks
- source_png/mechanics/: 3 separated war-mechanic icons
- dds_ready/focus_95x95/: game-sized focus DDS assets
- dds_ready/events_474x156/: game-sized event-picture DDS assets
- dds_ready/mechanics_64x64/: mechanic DDS assets
- asset_manifest.json: mapping of filenames to intended usage

IMPORTANT GAMEPLAY UPDATE
The approved preview originally displayed a stronger Unprepared Sector debuff.
The implementation must use the CURRENT value:
    Division Attack: -30%
Do not copy the old -60% number from the preview.

IMPLEMENTATION INTENT
The focus/event artwork is already separated and named. Codex should inspect
the current TFR mod/repository GFX structure before wiring sprite definitions,
rather than assuming vanilla file locations or sprite names.
