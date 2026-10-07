# Greater Serbia / Yugoslav Federation, 0.14.0

The active HOI4 installation received this chapter before the repository was synchronized. It adds 29 focuses, 31 one-time timed decisions, three optional peaceful diplomatic decisions and 31 visible events. The earlier campaign, focus layouts, division templates and balance remain unchanged. The only campaign-script edit adds `MSGA_try_start_endgame` after the existing South Slavic Unity completion.

The transition requires the existing `MSGA_south_slavic_unity_open`, `MSGA_new_balkan_order_stabilised` and `MSGA_balkan_war_victory` flags. A one-shot startup/weekly check also admits campaigns that already completed the old gateway. `MSGA_SER_endgame` becomes the active tree; its two choices are mutually exclusive and their decision/effect flags also exclude the other route.

## Implemented outcomes

| Route | Integration | Remaining clients | Native additional debt |
| --- | --- | --- | --- |
| Greater Serbia | Montenegro and Macedonia; Kosovo and previously annexed Srpska remain Serbian | Croatia, Slovenia, Bosnia, Herzegovina and Albania | $10B with all 13 decisions and the two financial events |
| Yugoslav Federation | Croatia, Slovenia, Bosnia, Herzegovina, Montenegro and Macedonia join existing Serbia | Albania | $11.75B with all 18 decisions and the Croatian financial event |

Both routes retain the underlying `SER` country and its existing leader. No replacement leader, country tag, OOB, duplicate army, new war or country-history file is created.

`SER_MSGA_GREATER_SERBIA` has short name **Greater Serbia**, formal name **Greater Serbian State**, adjective **Greater Serbian**. `SER_MSGA_YUGOSLAV_FEDERATION` has short name **Yugoslavia**, formal name **Federal Republic of Yugoslavia**, adjective **Yugoslav**. Every installed TFR ideology receives the corresponding name/DEF/ADJ keys. Actual renaming is wired through `set_cosmetic_tag`, exercised in the executable AST model; engine rendering is pending the user's test. The cosmetics inherit Serbia's native map colour, avoiding a global country-colour override.

Greater Serbia reuses the actual TFR Serbian flag bytes in all three required sizes. Yugoslavia has an emblem-free, horizontal blue–white–red tricolour, generated directly rather than through image generation. Its six installed flag paths are:

- `gfx/flags/SER_MSGA_GREATER_SERBIA.tga` — 82×52 RGBA
- `gfx/flags/medium/SER_MSGA_GREATER_SERBIA.tga` — 41×26 RGBA
- `gfx/flags/small/SER_MSGA_GREATER_SERBIA.tga` — 10×7 RGBA
- `gfx/flags/SER_MSGA_YUGOSLAV_FEDERATION.tga` — 82×52 RGBA
- `gfx/flags/medium/SER_MSGA_YUGOSLAV_FEDERATION.tga` — 41×26 RGBA
- `gfx/flags/small/SER_MSGA_YUGOSLAV_FEDERATION.tga` — 10×7 RGBA

## Integration and cost safety

The native cost command is `set_temp_variable = { var = debt_var_temp value = X } add_debt = yes`. This uses actual TFR `debt_var`, with no treasury subtraction or inflation multiplier. `MSGA_endgame_integration_obligations` records only this chapter's net commitments for the single +$5B Price of Victory notification. It is not a second currency or debt system. Cancellation uses the native negative-debt refund plus the PP refund, guarded by a persistent pending flag. Released callbacks cannot borrow, refund or deliver again. Accepted financial event costs have their own one-shot event and resolution guards.

Each dependent administration has a persistent busy flag. Start and finish validate the required route, focus, earlier agreements, peaceful Serbian subject relationship, owned/controlled territory and absence of unrelated target conquests. A cancellation returns the decision's costs and releases its reservation; completed decisions remain hidden. Different countries can negotiate in parallel. The final federal decision checks the entire framework again before any annexation, preventing a partial union after late loss of a subject or territory.

Only the native approved territories may be integrated: MNT 105; MAC 106; CRO 103/109/1306/163/736; SLV 102/900; BOS 104/848/849/850; HRZ 851. Cores are added only on whitelisted Serbian-owned, fully controlled states and only when absent. Native `annex_country = { target = TAG transfer_troops = yes }` transfers the existing forces and stockpiles; there is no manual equipment copy or respawn. Regional auxiliaries already under Serbian command remain untouched.

The assumed starting situation includes the earlier, successful `MSGA_srpska_united` annexation. This chapter does not invent another Srpska chain. The default Bosnia event retains states 848/849/850 in the Serbian constituent republic. The optional alternative transfers only those three already annexed and currently controlled states to the protected BOS country, improving reconciliation with a small Serbian stability penalty. Both options lead to the same six-republic federation. Kosovo stays within Serbia; Albania is never annexed or cored.

The constitution requires all five ready flags and the completed conference. The conference resolves the presidency, one federal army and Belgrade capital before ratification. The two presidential options produce different small spirits; they do not introduce further focus branches. Temporary project, protectorate and transition ideas are removed at their corresponding integration step. Final spirits replace earlier progression rewards to limit stacking; subject autonomy/contribution modifiers run on the subjects.

Native building rewards target Podgorica 105, Skopje 106, Belgrade 107, Zagreb 109, Ljubljana 102 and Sarajevo 104. Shared slots precede construction, with before/after `building_level@TYPE` checks and rollback of the introduced slot on rejection. Infrastructure respects level five. Native rejection is logged rather than represented as a delivered building. Political integration is independent of an engine-rejected supplementary building. Actual building delivery needs the user's engine test.

## Artwork and deployed files

The supplied source archive and all manifest compositions were inspected. 112 DDS comprise 29 focus images at 95×85, 31 decision images at 52×45 with the existing dark frame, 30 event images at the inspected native 500×250 format, 19 idea images at 64×64, and three category images at 52×40; all are DXT5. Captions and unrelated panels were cropped from sheet fragments. The additional Brotherhood event derives from its approved focus image; the One People event shares the talks picture. No yellow focus rings or socialist symbols were introduced.

The four inaccurate map compositions are rebuilt from the installed TFR province pixels, definitions and state province lists. These native geometric boundaries replace the imagined borders; package composition hashes and map bounding boxes remain recorded. Actual rendered DDS were inspected outside the game. The supplied art's small source resolution limits detail when expanded into event pictures.

133 relative paths were deployed: 130 new files and three updated files. The sibling launcher descriptor was updated too. `docs/endgame_sources.json` gives every exact absolute deployed path, original baseline hash, generated asset/source digest and native source digest; `docs/endgame_sync.json` gives all 528 matching source/runtime hashes and the preserved launcher/Workshop identity. The main authored files are:

- `common/national_focus/MSGA_SER_endgame.txt`
- `common/decisions/MSGA_endgame_decisions.txt`
- `common/decisions/categories/MSGA_endgame_categories.txt`
- `common/scripted_effects/MSGA_endgame_effects.txt`
- `common/scripted_triggers/MSGA_endgame_triggers.txt`
- `common/scripted_effects/MSGA_new_order_effects.txt` — existing hand-off only
- `common/ideas/MSGA_endgame_ideas.txt`
- `common/on_actions/MSGA_endgame_on_actions.txt`
- `common/scripted_localisation/MSGA_endgame_scripted_localisation.txt`
- `common/opinion_modifiers/MSGA_endgame_opinions.txt`
- `events/MSGA_endgame_events.txt`
- `interface/MSGA_endgame_assets.gfx`
- `localisation/english/MSGA_endgame_l_english.yml`
- `descriptor.mod`, `make_serbia_great_again.mod` — version 0.14.0
- the 112 DDS and six TGA files listed individually in the deployment ledger.

## Validation and test boundary

`tools/validate_endgame.py` passed against LIVE: five complete route/choice scenarios, thirteen targeted negative/concurrency/cancellation checks, exact PP/debt/duration checks, mutual exclusion, hand-off preservation, target/core whitelists, native token references, sprite/localisation resolution, archive-derived art and all six flags. Models verify +$10B/+11.75B debt, unchanged treasury, retained leader/capital, Albania exclusion and army/stockpile totals without duplication. They do not certify engine behavior.

Installed New Balkan Order (96 scenarios plus 49 negative cases), Pact War (526 scenarios), Post-Bosnia, economic/energy and phase1 regressions passed. Their validators now understand the already approved decision UX wrappers/category removal, exact later hashes and native scripted localisation; historical ledgers/reports remain intact. `docs/endgame_regression_*.json` contains the current checks.

The game window and saves were not accessed. In-game cosmetic display, flag rendering, native timer timing, army/stockpile transfers, supplementary construction, AI and actual save/load remain for the user's test. Reload HOI4 before testing, because an already running game retains its previously loaded scripts. No console command is part of progression. Future content beyond these endgame outcomes requires a separate request.
