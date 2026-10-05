# Post-Kosovo Serbia — 0.7.0

Deployed to the primary playable folder `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`. The sibling launcher descriptor points to that folder and retains the existing Workshop identity. All 116 runtime files match the project. Exact changed paths are in `post_kosovo_files_deployed.json`; all file hashes are in `local_deployment.json`.

## Progression

Successful Kosovo resolution and the final victory event load the existing postwar tree ID, now containing seven real focuses. Opening event 1 fires once. Focus durations are **14, 7, 14, 21, 21, 14 and 7 days**. Rebuild Kosovo and Invest in Pristina branch from consolidation; both are prerequisites for A Lasting Peace. The Cost of Integration is event 3, never a focus.

Restore Order reaffirms Serbia's core on **1305, Kosovska Mitrovica**. Installed TFR already gives Serbia that northern core at the 2020 start: this effect is intentionally safe and idempotent. It does not core Pristina. Review Administration fires the integration event; accepting its option adds exactly **1 nominal billion** through `debt_var_temp = 1` and native `add_debt`, then cores **785, Kosovo/Pristina** and records full integration. It does not debit treasury. Native TFR maintains its derived debt/GDP values.

Consolidate Serbian Authority removes the actual starting penalty **`SER_rebellion_of_kosovo`**, adds two stability points and performs safe campaign cleanup. Reconstruction adds one infrastructure level in state 785, capped at five, and one civilian factory with a shared slot. Investment adds one civilian factory and one native **Office Park**, with two shared slots. Rewards are ownership-gated and recorded once; either branch order gives the same result. No parallel state-development or income variables are introduced.

All fourteen supplied narrative events are implemented. The final focus starts events 12, 13 and 14 in sequence, separated by two days. Only the last event loads **`MSGA_SER_bosnian_crisis`** after verifying the required flags and retained Kosovo ownership. That tree contains one unavailable root. No Bosnian war, annexation, uprising or wider territorial operation exists in this increment.

## Brigade and vehicles

The one-time militia decision requires successful resolution, both owned and controlled Kosovo states, both Serbian cores, full integration and at least **$2B treasury**. It costs **zero PP**. A guarded native treasury debit funds one **Kosovska Mehanizovana Brigada**, spawned at Mitrovica with full initial personnel/equipment and low experience. No separate stockpile reward is added.

The 16-width template has two `mot_militia`, one `mechanized` and one `light_mechanized` battalion, supported by `mbt_company`, engineers and logistics. Installed unit definitions give its initial requirements:

| Equipment | Quantity |
| --- | ---: |
| Infantry equipment | 925 |
| Command/support equipment | 115 |
| Trucks | 110 |
| BVP M-80A IFVs | 50 |
| BTR-80A APCs | 45 |
| Reserve T-55A tanks | 14 |

The 14 tanks come from TFR's actual `mbt_company` requirement. The supplied division screenshot guides the mixture, while the native definitions determine counts. `force_equipment_variants`, as used in TFR's British and French OOBs, selects the reserve tank and named IFV/APC variants. Existing stockpiles are not wiped or replaced. A separate legacy OOB handles installations without No Step Back.

Startup creates **M-84A**, **T-55A**, **BVP M-80A** and **BTR-80A** variants once. With No Step Back, the M-84A uses `modern_tank_chassis_1`, a high-velocity cannon, the three-man turret, torsion bars, cast armour, gasoline engine and optical sight. These coarse game modules prioritise affordable gameplay and are all enabled by Serbia's existing start technologies; no extra technology is granted. There are no engine/armour upgrades, active protection or advanced optics. Calculated base cost is **8.51**, armour **30**, reliability **75%**, soft attack **11**, hard attack **20**, and piercing **85**, before country/technology modifiers. The T-55A uses cheaper riveted armour, costs **5.92** at base and is marked obsolete so it remains a reserve design rather than the preferred new production model. No free tank production line is created.

Serbia-specific localisation provides BVP M-80AB1 for the next IFV model and Lazar 3 for the next APC model. It does not rename international equipment or add duplicate technologies.

## Files and visuals

New files include the postwar decisions, effects, events and startup hook, vehicle effects, three brigade OOB files, the Bosnian shell, separate English localisation and `MSGA_post_kosovo_assets.gfx`. The existing postwar tree is replaced; the previous victory transition gains the opening-event call and a guard against returning from Bosnia. Early and wartime gameplay files otherwise retain their committed behavior.

All **22 supplied DDS candidates** are integrated: seven 95×95 focus icons with completion shines, fourteen 474×156 event pictures, and one 60×60 decision icon. Their DXT5 data is preserved exactly, sizes match the existing conventions and alpha is valid/visible. Source art, original screenshots, manifest and generated reference boards remain in `art/post_kosovo_assets/`; reference mockups are not playable assets. No TFR files or artwork are copied into the mod.

## Validation

All three validators pass against the actual installed version. Reports: `local_runtime_validation.json`, `local_kosovo_validation.json`, and `local_post_kosovo_validation.json`. Tests cover prior-content preservation, correct core targets, debt versus treasury, ownership gates, once-only costs and spawning, independent branch order, native equipment quantities, exact artwork copies, legal modules/slots, conservative tank stats, event/localisation references and the Bosnian transition without war.

A fresh debug engine load reached the 2020 startup without log entries naming MSGA or the new variants. The first load caught an incorrect core-effect scope; it was fixed to native state-scoped `add_core_of`, redeployed and reloaded. `local_engine_validation.json` records the fresh check without copying game logs into source control. Base-game/TFR errors remain outside this submod.

The script model checks a serialized flag checkpoint but does **not** certify engine save/load. In-game UI rendering, actual brigade equipment assignment, production-screen availability and a complete played postwar campaign still require manual acceptance testing because native UI automation is unavailable. These limitations are recorded separately from the passing parser/static/model checks.
