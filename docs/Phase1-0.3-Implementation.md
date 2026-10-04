# Phase 1 0.3.0 implementation

## Scope

The 18 focus IDs, titles, coordinates, costs, prerequisites and American-fracture gate are unchanged. The sole terminal focus remains `MSGA_the_kosovo_question`. No war goal, annexation, occupation, core or territorial transfer was added.

## Files

Created:

- `make_serbia_great_again/interface/MSGA_focus_icons.gfx`: 18 base sprites and 18 completion-shine sprites.
- `make_serbia_great_again/gfx/interface/goals/`: 18 runtime DDS images.
- `make_serbia_great_again/common/decisions/MSGA_SER_strategic_review.txt`: two strategic and five Kosovo preparatory reviews.
- `art/focus_icons/MSGA_TFR_focus_icons/`: supplied originals, both PNG sizes, atlas, mapping and conversion manifest.
- `tools/prepare_focus_icons.py`, `tools/validate_phase1.py`, this report and `docs/phase1_static_validation.json`.

Modified: the focus tree, ideas, dynamic modifiers, scripted effects, economic/health/defence decisions, domestic decisions, decision categories, events, English localisation, both version descriptors, README and development notes. Existing on-actions, scripted triggers and BoP ranges are retained.

## Artwork

All 18 focuses reference their matching `GFX_goal_MSGA_*` sprite. The supplied DDS files were RGB24, 95×95, with no alpha channel. Runtime files are uncompressed RGBA8 DDS with opaque alpha. Their decoded pixels match both the original DDS and the supplied PNG95 exactly. No artwork was regenerated, cropped, resized or replaced. The original composition is rectangular and is preserved.

Base definitions follow TFR `interface/TFR_goals.gfx`. Completion variants follow `interface/TFR_goals_shine.gfx`, including the existing shader, shine overlay and animation masks. TFR assets are referenced, not redistributed.

## Focus rewards

| Focus | Primary reward | Secondary reward | System affected |
|---|---|---|---|
| A New Decade | Guarded initialization; activates BoP and reveals Domestic Affairs | +35 PP, +1% stability; introductory event | Politics |
| Contain the Outbreak | Pandemic Disruption; four health decisions | Outbreak event | Public health |
| Reopen on Serbian Terms | Prepared, underprepared or accelerated reopening outcomes | Stability/BoP consequences; accelerated 30-day strain | Public health/politics |
| Attract Productive Capital | Recovery Programme: +5% Business Value, 365 days | Partnership decision and investment event | Economy |
| Modernise Belgrade Services | +1 shared slot in Belgrade; funded Office Park unlock | +10 PP; recovery fallback if Belgrade is unavailable | State 107/economy |
| Develop the Morava Corridor | Immediate +1 infrastructure; funded further works unlock | Recovery fallback if construction is impossible | State 1296/economy |
| An Independent Resource Policy | Bor, Kolubara and Jadar project unlocks | Feasibility follows the completed survey | Resources/economy |
| A Recovery Made in Serbia | Removes remaining MSGA pandemic strain; +3 Business Value points, capped at +10%; renews programme | +2% stability, Presidency +0.03; enterprise unlock | Economy/public health |
| Consolidate the State | Coordinated Government: +5% PP gain; authority decision | +20 PP, Presidency +0.03 | Politics |
| Manage the Streets | Order/backlash or paid national dialogue event | Public-grievance decision; dialogue halves later backlash | Politics |
| A Presidential Mandate | Government upgrades to Presidential Administration: +5% PP gain, +3% stability | +15 PP, +2% stability, Presidency +0.04; public-order/enterprise access | Politics |
| Restore Defence Production | Immediate MIL and slot; +5% factory output programme | Defence event; paid second MIL unlock | Military industry |
| Modernise the Army | +5% planning and +5% organisation recovery | +10 Army XP; renews programme | Army |
| Arms for an Uncertain World | +5% efficiency growth | Paid procurement unlock; renews programme | Production |
| Secure the Supply Lines | +1 infrastructure in Eastern Serbia; −5% supply consumption | +5 XP fallback if construction is impossible | State 108/logistics |
| Ready for the Uncertain | Planning reaches +10% total; previous defence improvements retained | +5 Army XP; renews programme | Army |
| Watch the Western Shield | Strategic Vigilance for 180 days; strategic review decisions and briefing | +3% war support | Strategic preparation |
| The Kosovo Question | Crisis category, guarded counter and five preparatory studies | Kosovo briefing; retained findings for future policy | Crisis preparation |

## Progression and costs

- Recovery starts at +5%, economic capstone adds +3 percentage points, and projects add +1 point each; Europe adds +2. The total is clamped to +10%. Refresh removes the current modifier before adding a fresh 365-day instance.
- Defence retains separate variables for output +5%, efficiency growth +5%, supply −5%, organisation recovery +5% and final planning +10%. Assigning final planning does not add a second +10% bonus. Each military milestone renews the 365-day programme.
- Politics uses a two-stage government spirit. Strategic Vigilance is temporary: planning +5%, army intelligence +5%. Accelerated reopening adds a 30-day stability/business strain. Existing pandemic and investment-commitment ideas remain.
- Health measures are one-time; response count is capped at four. Two completed measures swap Disruption to Easing. Prepared managed reopening removes it; underprepared managed reopening retains timed Easing for 60 days.
- All seven major projects share one active investment slot and require Serbian ownership/full control. Building projects also check capacity. Cancellation returns PP and the exact treasury amount recorded at activation, through the TFR API. Construction commitment ends on delivery or cancellation.
- Treasury costs remain Belgrade 0.25, Morava 0.20, defence 0.35, Bor 0.15, coal 0.10, Jadar survey 0.05 and feasibility 0.20 billion, multiplied by current inflation factor. Morava completion now also upgrades recovery by one point.
- Procurement remains 35 PP and 30 days for 500 infantry equipment, 50 support equipment and 3 XP. Russian cooperation now charges the quoted 0.075 billion instead of the previous inconsistent 0.07.
- Dialogue costs 25 PP and records a lasting negotiation channel; subsequent public-order backlash falls from −2% stability/−0.04 BoP to −1%/−0.02. Firm order retains the full delayed penalty. No leader or faction change is introduced.
- Strategic reviews: NATO readiness, 25 PP/14 days/+5 XP; border intelligence, 35 PP/0.03 billion/30 days/180-day vigilance renewal. Both are one-time.
- Kosovo reviews: dossier 30 PP/21 days; KFOR 25 PP/14 days; general staff 25 PP/14 days/+5 XP; regional partners 25 PP/21 days/10 PP returned on completion; northern contingencies 30 PP/21 days/+3 XP. All are one-time, advance a capped 0–5 counter and retain completion flags for future crisis content.

## Events

`MSGA.3` adds accelerated reopening strain. `MSGA.4` records dialogue and uses PP as its payment. `MSGA.11` checks that dialogue when applying delayed backlash. New `MSGA.12` delivers the strategic briefing. The remaining events retain their roles; there are 12 events total.

## Installed TFR evidence

| Path | Implementation pattern used |
|---|---|
| `interface/TFR_goals.gfx`, `TFR_goals_shine.gfx` | Base texture sprites and completion animations |
| `common/national_focus/TFR_national_focus_APA.txt` | `swap_ideas`, `unlock_decision_tooltip`, state slots, Office Park construction, `set_power_balance`, modifier removal |
| `common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt` | `add_income_with_inflation`, `add_debt_with_inflation`; no MSGA writes to derived GDP/debt |
| `common/dynamic_modifiers/TFR_dynamic_modifiers_SER.txt` | Variable-backed `business_value_factor` |
| `common/dynamic_modifiers/TFR_dynamic_modifiers_APA.txt` | Variable-backed `army_org_regain` |
| `common/ideas/TFR_ideas_FRA.txt` | `army_intel_factor` |
| `common/abilities/TFR_generic_leader_abilities.txt` | `divide_temp_variable` for exact refund normalization |
| `history/states/107-Kosavo.txt` | State 107: Serbia-owned Belgrade, province 11586; misleading filename |
| `history/states/108-Eastern Serbia.txt` | State 108: Serbia-owned Eastern Serbia |
| `history/states/1296 - Sumadija and Western Serbia.txt` | State 1296: Serbia-owned Šumadija/Western Serbia, Kruševac/Čačak |

The current doctrine system was not certified for the old doctrine-category discount examples, so modernisation uses verified organisation recovery instead. No unsupported state modifier or invented strategic resource was introduced.

## Validation and limitations

Static validation passes: braces; unique focus/idea/event/decision/category/sprite definitions; references; localisation and UTF-8 BOM; texture existence and decoded pixel identity; original topology and titles; acyclic prerequisites; Kosovo as sole terminal focus; variable definitions; recovery cap; final planning; one-time review guards; guarded refundable projects; absence of Phase 2 war effects. Counts: 18 focuses, 36 sprites, 12 events, 25 decisions, six categories, seven idea definitions, two dynamic modifiers and 195 localisation keys.

The build was installed locally. TFR+MSGA reached the main menu and a fresh test campaign. Initial load exposed 18 missing completion-shine definitions; all were added and installed. A restart was initiated, and the current error-log scan contains no MSGA references. The original launcher mod selection was restored byte-for-byte after both launches.

**The user stopped Computer Use before the Serbia tree inspection.** All 18 icons in the actual tree, focus tooltip rendering, timed decision delivery, economic before/after values and save/load remain unverified. The restart/log scan and static checks do not certify full gameplay acceptance. No further Computer Use was performed after the interruption.

Start a new Serbia campaign for all revised focus rewards. Old saves do not rerun completed focus effects. Kosovo review flags are implemented preparation contracts; Phase 2 operations remain absent.
