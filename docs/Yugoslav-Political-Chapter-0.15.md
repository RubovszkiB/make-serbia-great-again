# Yugoslav political chapter — 0.15.0

The installed endgame tree continues below `MSGA_a_new_yugoslavia`; its original 29 focus definitions are byte-equivalent as parsed scripts to commit `a182e7944cdd528b540ab9f121c5ccf2e7104fd8`. No additional tree switch, economic/military chapter, borders, cores, annexations, debt, army transfer or division templates were introduced. Albania remains separate.

| Section | Focus IDs | Duration |
| --- | --- | --- |
| Entry | `MSGA_yugoslavia_proclaimed`, `MSGA_future_of_the_federation` | 28 days each |
| Socialist | `MSGA_return_to_socialism`, `MSGA_titos_legacy`, `MSGA_socialist_yugoslavia` | 35 days each |
| Continuity | `MSGA_keep_the_status_quo`, `MSGA_the_vucic_system`, `MSGA_a_stable_federation` | 35 days each |
| National | `MSGA_a_national_yugoslavia`, `MSGA_national_renewal`, `MSGA_national_yugoslavia` | 35 days each |

Entry requires completed `MSGA_a_new_yugoslavia` and the existing Yugoslav path, completed endgame and proclaimed federation flags. The three choices have pairwise focus exclusions and mutually guarded route flags. Every descendant requires its own route and rejects the other routes. All reward callbacks are country-scoped and one-time guarded. Every final focus sets `MSGA_yugoslav_political_settlement_complete`; it opens no unrequested future content.

TFR's localized **Authoritarian Socialist** group is `communist`, with valid `market_socialism` used for the new leader role. Its `nationalist` group (currently displayed as **Despotic** by the installed TFR localization) uses valid `autocrat` for the national route. Native `add_popularity = { popularity = 0.5 }` adds 50 percentage points. From TFR's initial 5% socialist and 10% nationalist support, the deterministic model gives 55% and 60%; an evolved save uses its current support and the engine's normalization/cap. No custom party system exists.

Existing recruited `SER_ivica_dacic` receives a socialist country-leader role and native promotion on the socialist choice. Existing `SER_aleksandar_vucic` receives a nationalist role and promotion on the national choice. No new characters or portraits are defined. Continuity never changes the existing leader, party, popularity or ruling ideology (`conservative` in MSGA's initialization and TFR's Serbia history).

Six events (`MSGA_yugopolitics.1`–`.6`) and six ideas (`MSGA_yp_titos_legacy`, `MSGA_yp_renewed_socialist_federation`, `MSGA_yp_vucic_system`, `MSGA_yp_federal_continuity`, `MSGA_yp_yugoslav_national_renewal`, `MSGA_yp_one_yugoslav_state`) are installed. Each final idea replaces its route's intermediate idea. Existing federation ideas remain as approved formation rewards. Narrative events do not choose routes.

The Red Star event changes cosmetic identity in its immediate effect only after Tito's Legacy on the socialist route. Final socialist completion also rechecks that identity. `SER_MSGA_SOCIALIST_YUGOSLAVIA` has Yugoslavia / Socialist Federal Republic of Yugoslavia / Yugoslav localization and separate RGBA TGA flags at 82×52, 41×26 and 10×7. All three existing `SER_MSGA_YUGOSLAV_FEDERATION` plain flags retain their exact SHA-256. Both other routes retain that cosmetic identity.

All 17 supplied source PNG compositions were inspected. The manifest maps 11 focus DDS (95×85), six event DDS (500×250), and six derived idea DDS (64×64), all DXT5. Red-star artwork is restricted to the socialist focus/event/idea assets. No old artwork was overwritten; no archive instruction or code was executed.

The increment consists of **34 relative runtime paths: 31 new and three changed** (the endgame focus tree and two descriptors), plus the sibling launcher descriptor. `yugoslav_politics_sources.json` records every exact deployed path, source/archive digest, native reference and unchanged normal-flag digest. `yugoslav_politics_sync.json` verifies **559 identical installed/source files** and the preserved Workshop identity `3813570241`.

Checks: `validate_yugoslav_politics.py --mod-root <live folder>` and `validate_endgame.py --mod-root <live folder> --report docs/yugoslav_politics_endgame_regression.json`. The political validator covers three complete routes and ten negative cases, one-time rewards, exclusivity, saved model continuation, character references, popularity commands, flags, DDS/GFX/localization, native APIs and immutable territory/debt/armies. Existing endgame regression covers five formation choices and thirteen negative/concurrency cases. These are static and deterministic model checks, **not engine gameplay validation**. Native leader promotion, evolved-save popularity, event rendering and save/load remain for the user's test; the running game and saves were not touched. Restart HOI4 to load the new files before testing.

Workflow: `implement_yugoslav_politics.py` installs LIVE first and refuses a divergent or already-upgraded baseline. After the two validators pass, `sync_yugoslav_politics.py` synchronizes only the validated increment and uses `deploy_local.py` to confirm all hashes and the active descriptor without another deployment change.
