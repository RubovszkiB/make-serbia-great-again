# Installed 0.9 increment — awaiting user gameplay test

Primary runtime: `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`.

The user stopped Computer Use with Escape during engine loading, then explicitly took over the gameplay test. No automated input, game restart, or game shutdown followed. On 2026-10-05 the user requested GitHub upload before testing later. The installed 0.9 changes and subsequent transition repair were copied back to source: all 172 files and the sibling launcher descriptor match. The five installed static/script-model validators passed. In-game validation remains pending; source synchronization does not certify gameplay.

## Source-level failure points repaired

The old release effect set its success flag before attempting release, while its one-shot event could be consumed even if its guard prevented any uprising. The installed engine documentation describes `release` as creating a puppet, but the old code did not explicitly make Srpska independent before Bosnia declared war. The old war waited another 15 days; intervention also required a 70-day observation focus and greater than 2% Srpska surrender progress. A completed preparation tree alone therefore could not guarantee the requested intervention. These are identified code paths, not a confirmed reproduction of the user's earlier save.

The existing focus/effects/events were repaired rather than duplicated. Seed completion executes release directly. Only confirmed independent Srpska receives the success flag; states 848, 849 and 850 explicitly transfer to SRP. Native Dodik, cores, technology and the existing three militia divisions are retained. BOS declares a real war on SRP immediately. The intervention prompt follows after one day; Serbia creates `MSGA_serbian_alliance` (Serbian Alliance), adds SRP, then uses `add_to_war` targeting SRP's existing alliance against BOS. No separate Serbian declaration was added. Completed-focus recovery guards support the stalled earlier chapter without regranting units or economy rewards.

## Settlement and delayed choice

Native tags are BOS (central Bosnia, state 104), HRZ (Herzegovina, state 851), and SRP (states 848, 849, 850). TFR's dormant HRZ history contains capital 229 and an Iranian character; MSGA supplies a minimal country-history override with capital 851 and an authoritarian-democrat reconstruction council using TFR's `military_democracy` subtype. No new country tag is created.

Bosnia's defeat is captured in `on_capitulation_immediate` before the ordinary peace conference. A guarded state-control fallback also recognizes Serbian control of central Bosnia and Herzegovina. The once-only settlement ends the local BOS–SER/SRP war, restores the designated successor borders, and makes all three `autonomy_puppet` subjects of Serbia. The early-capitulation hook records defeat before checking the settlement, avoiding dependence on when the engine sets `has_capitulated`. The existing native story guards remain unchanged.

The settlement schedules `MSGA_bosnia.11` with `days = 70`. The primary option annexes Serbia's peaceful SRP puppet, transfers its territory and adds exactly 1 to native `debt_var` through `debt_var_temp` and `add_debt`. It neither subtracts treasury nor grants Serbian cores. “Not Yet” resolves the question with SRP still a puppet and no debt change. The event does not repeat.

## Reconstruction, train and scaling changes

Both existing economic focus rewards retain their prior civilian factories. Rebuild Kosovo adds one capped infrastructure level, repairs local infrastructure/civilian/office buildings, adds 5% native industrial-development progress, clears the campaign penalties/native rebellion idea, and applies a 180-day state construction bonus of 10% and building repair bonuses of 20%. A separate 180-day country idea supplies 0.5% monthly native industrial-development progress, because TFR's development system is country-scoped.

Invest in Pristina adds its civilian factory and office park, one capped infrastructure level and 5% industrial-development progress. The event offers $0.5B state investment (+1 civilian factory, infrastructure, 5% development and 2% stability) or private capital (+1 office park, infrastructure, 3% development, 5% business value and 2% monthly income growth). Each choice applies once. One final decision requires both focus rewards, costs 50 PP and $1B treasury, adds 5% development and infrastructure, removes temporary reconstruction measures, and fires Kosovo Rebuilt. The existing militia integration decision is retained.

Five unapproved Kosovo preparation decisions, their category and their focus unlock tooltips are removed. The two unrelated strategic-review decisions remain. The six Bosnia development rewards use `0.10`, correcting their old `10` (+1000%) values. Logistics researches verified `basic_train` before granting the existing 15 `train_equipment_1`, retaining its 150 utility vehicles.

All seven supplied DDS files and `interface/MSGA_eventpictures.gfx` are byte-identical to the user's ZIP. Events use its actual `GFX_MSGA_event_*` keys. The images' authored size is 474×178; they have not been regenerated or resized. In-game display remains for the user's visual check.

## Verification boundaries

Installed-file validators cover the earlier content, native compatibility guards, exact states and unit locations, train unlock ordering, fractional development, supplier purchases, faction-before-join ordering, all three subjects, exact 70-day scheduling, both annexation outcomes, untouched treasury/cores on annexation, both Pristina options, insufficient funds, decision gating, infrastructure cap, once-only rewards and DDS hashes. Their state models do not simulate combat or the engine's peace conference.

The initial engine load reported obsolete decision unlocks and redundant runtime character recruitment. Those references were removed from the installed scripts. They remain in that old log because the process was not restarted after the corrections. A fully restarted fresh Serbia game is needed for the user's test; end-to-end war/peace behavior, actual debt display, save/load and event rendering are not yet certified.

The later Kosovo-to-Bosnia repair removes delayed narrative flags from chapter availability and checks approved war, integration and reconstruction completion through The Serbian Question directly. The final paid reconstruction decision is optional. Startup and weekly retries recover eligible stalled saves without replaying economic rewards. See [transition diagnosis](Kosovo-Bosnia-Transition.md).

Initial installed changed paths and SHA-256 hashes: `docs/upgrade09_deployment.json`; subsequent transition changes: `docs/transition_deployment.json`. The current complete source/runtime inventory is `docs/github_runtime_sync.json`, with current results in `docs/github_validate_*.json`. Earlier `docs/runtime09_validate_*.json` reports precede the transition repair. Keep all game logs, backups and saves out of GitHub.
