# Kosovo campaign — version 0.6.0

Implemented and deployed to `C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again`. The sibling launcher descriptor points to this folder. `local_deployment.json` lists every verified runtime file and its SHA-256; supplied source artwork is kept outside the playable mod.

## Gameplay changes

The existing final early focus, `MSGA_the_kosovo_question`, immediately loads `MSGA_SER_kosovo_war`. The original 24 focuses retain their rewards and layout. Existing early unlocks also recognize their completion flags because changing trees does not retain nodes absent from the new tree.

The campaign has three seven-day focuses: Plan the Attack, Prepare the Southern Command and Operation Return. Their narrative events grant modest planning rewards and start the war. A fourth, visible but unselectable victory focus completes automatically after scripted resolution verifies Serbian ownership and full control of **both** states. The final event loads `MSGA_SER_post_kosovo`, containing only an unavailable future-chapter placeholder.

The three existing volunteer recruitment decisions now each cost exactly **$2B** from the native TFR treasury and zero PP. The equipment reserve decision costs **$3B** and zero PP. Both use `income_var`, `income_var_temp` and TFR's `add_income`, with affordability checks and costs paid when the decision starts. Recruitment remains 20 days; reserve delivery remains 30 days with the existing equipment quantities. Partner bonuses do not discount these fixed costs.

Kosovo states are **785** and **1305**; Pristina is province **14402**, verified from installed TFR state history. War start adds a state attacker modifier of **-30% attack / -10% movement** to each state. Two independent decisions each charge **25 CP**, take **14 days**, and remove only their own state's penalty on completion. They cannot remove the penalty at purchase time.

The twelve supplied story pictures are used for the General Staff plan, southern mobilisation, Operation Return, emergency address, Pristina mobilisation, NATO restraint, Pristina's fall, Albanian intervention, NATO's distancing, Kosovo's capitulation, the Tirana ceasefire and final Serbian control. Albania receives a separate intervention event; offensive preparation has a completion notification. One hidden observer runs only during this campaign, checking provincial control daily; the state-control hook can detect it sooner.

Albania leaves its actual faction before receiving the intervention event and is checked again before declaring war. The native NATO member array and accession flag are updated. Temporary faction-joining restrictions and removal of relevant defensive guarantees prevent the scripted declarations from automatically involving NATO. Guarantees concerning Serbia and Albania are restored after cleanup. Existing unrelated wars are not ended.

The Kosovo capitulation-immediate hook annexes only Kosovo, transfers states 785 and 1305 to Serbia, white-peaces only the campaign's Albanian intervention, removes temporary mechanics and verifies ownership before completing the victory focus. An early Albanian capitulation also white-peaces Albania instead of permitting conquest. No Albanian state transfer or annexation is scripted. Delayed intervention cannot restart the war after campaign resolution. Completion flags prevent duplicate declarations, annexations and tree transitions.

## Files

New gameplay files are `common/national_focus/MSGA_SER_kosovo_war.txt`, `MSGA_SER_post_kosovo.txt`, `common/decisions/MSGA_SER_kosovo_operations.txt`, `common/ideas/MSGA_SER_kosovo_ideas.txt`, `common/on_actions/MSGA_SER_kosovo_on_actions.txt` and `events/MSGA_SER_kosovo_events.txt`.

Existing early focus, decision, category, trigger, event and scripted-effect files gain the chapter transition, treasury costs, completion-flag fallbacks and campaign effects. `common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt` adds the state penalty. English localisation covers every new focus, idea, decision, event and cost. Both descriptors identify version 0.6.0 and preserve Workshop identity metadata.

`interface/MSGA_kosovo_assets.gfx` registers all **19 supplied DDS files**: four focus icons with completion shines, twelve event pictures and three mechanic icons. Files are copied without pixel changes. TFR and vanilla artwork remain references; their files are not redistributed. The user-supplied package and manifest are retained under `art/kosovo_war_assets/`.

## Validation and limits

Both `tools/validate_phase1.py` and `tools/validate_kosovo.py` pass against the installed runtime. Reports are `local_runtime_validation.json` and `local_kosovo_validation.json`. Checks cover identifiers, script structure, focus durations, localisation, sprites/textures, native TFR references and preservation of early rewards. A model executes the actual parsed campaign effects to check ordering, both-state ownership gates, independent sector preparation, treasury deductions, cleanup, duplicate guards, cancellation of pending intervention and preservation of an unrelated war.

The model is not the HOI4 engine: it does not simulate combat, peace conferences, save/load or UI rendering. Fresh engine load results are recorded separately in `local_engine_validation.json`. The first debug load caught invalid `exists = TAG` guards; they were replaced with the documented `country_exists = TAG` trigger and a regression check was added. Full manual campaign and save/load acceptance remain to be tested in game; static/model success does not certify them.

No further integration, Albanian conquest, Montenegro, Bosnia or wider geopolitical branches are included.
