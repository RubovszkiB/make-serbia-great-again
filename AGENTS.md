# MSGA project workflow

The actual local HOI4 installation is primary; GitHub is source control and backup. The primary runtime folder is `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`, with the sibling `make_serbia_great_again.mod` descriptor. Every implementation increment must be deployed to this folder and validated there before syncing, committing and pushing to `origin`. A repository-only update is incomplete. Use `tools/deploy_local.py`, then run `tools/validate_phase1.py --mod-root <runtime folder> --report docs/local_runtime_validation.json` and verify descriptor paths and source/runtime file hashes. Preserve the installed Workshop identity metadata and do not modify other mods or game saves.

The user requests ongoing GitHub uploads after local deployment and validation. This authorization persists across turns. Do not request upload permission again for ordinary project updates.

Before pushing, review the diff for unrelated files, credentials, game logs, saves, and copied third-party assets. Keep validation claims accurate, including interrupted or unfinished checks. Do not force-push, rewrite published history, or overwrite unrelated user work.

Use the installed TFR scripts as the authoritative source for tokens and economic APIs. Prefix new game objects with `MSGA_`. Do not modify TFR or Yugoslavia Reborn files or introduce `replace_path`. Current development stops at the Kosovo Question unlock; Phase 2 operations require a separate user instruction.
