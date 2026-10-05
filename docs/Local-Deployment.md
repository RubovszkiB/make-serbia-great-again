# Local MSGA deployment

The primary local HOI4 installation was updated from 0.3.0 to 0.5.0 on 2026-10-05. This deploys the implemented early-Serbia expansion from commit `870257c`; gameplay scripts were not redesigned.

Runtime folder: `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`

Launcher descriptor: `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again.mod`

The initial comparison found 23 missing project files, 11 stale files and no runtime-only files. Deployment copied those 34 files plus the sibling launcher descriptor. All 57 project files now match the runtime copy by SHA-256, including unchanged files. Both descriptors are version 0.5.0; the launcher descriptor points to the runtime folder above. The existing `remote_file_id="3813570241"` was preserved in the installed and project descriptors.

The exact **35 absolute paths copied**, all verified relative paths and their SHA-256 hashes are recorded in [local_deployment.json](local_deployment.json). This includes every new focus/decision/event/idea/effect/localisation/interface/DDS/template file, the minister trait, Chronicle, cleanup and early reward events, and both runtime descriptors.

The deployed `common/national_focus/MSGA_SER_phase1.txt` contains all six requested focus IDs. The existing validator was extended to accept `--mod-root`, then run against the actual installed folder, using the project's original PNG assets and Git baselines for comparison. [local_runtime_validation.json](local_runtime_validation.json) records a passing result: 24 focuses, 52 sprites, four new spirit textures, 25 script files, 31 events, 30 decisions, both exact division templates and no Phase 2 war effects. Descriptor paths and full source/runtime identity are checked separately by the deployment script.

The existing `dlc_load.json` enables `mod/make_serbia_great_again.mod` alongside TFR (`3350890356`) and its music addon (`3350892196`). No conflicting Yugoslavia Reborn entry or alternate MSGA entry was present in that saved enabled-mod list. Neither HOI4 nor its launcher was running during the comparison. No other mod files, saves or launcher settings were changed.

No game was launched, so this is deployed-file and static validation, not an in-game acceptance test. A later launcher session could select another playset; the local MSGA entry must remain enabled. An already-loaded game needs a restart to read changed scripts, and a new Serbia campaign is the reliable check for the revised tree and startup templates. Existing saves do not replay completed focus rewards. There is no remaining missing-file or descriptor-path discrepancy in the inspected local installation.

The permanent local-first workflow is recorded in `AGENTS.md`: deploy and validate the actual game installation before committing or pushing GitHub updates.
