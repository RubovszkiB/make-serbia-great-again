"""One-time 0.12 migration. Install into the primary runtime before source sync.

Only verified 0.11 installations are accepted. The existing TFR peace handler is
wrapped, not replaced: unrelated capitulations retain its exact original body.
"""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
from validate_phase1 import parse,get,TOKEN
from implement_encirclement import LIVE,TFR,ROOT

PACKAGE=Path(r'C:\Users\Balazs\Downloads\MSGA_Balkan_War_Capital_and_Capitulation_Event_Assets.zip')
# tag, state, VP province, flag stem, city stem, image stems, temporary durations
COUNTRIES=[
 ('MNT',105,9809,'montenegro','podgorica','podgorica_submits',30,90),
 ('MAC',106,3882,'macedonia','skopje','skopje_accepts_terms',30,90),
 ('ALB',44,9914,'albania','tirana','tirana_accepts_new_order',45,120),
 ('SLV',102,9627,'slovenia','ljubljana','ljubljana_seeks_terms',30,90),
 ('CRO',109,11581,'croatia','zagreb','croatia_capitulates',45,120),
]
SIDE='OR = { tag = SER is_subject_of = SER AND = { is_in_faction_with = SER has_war_together_with = SER } }'
PEACE='common/on_actions/TFR_on_actions_ZZZ_peace.txt'

def capitulation_context():
 # Keep already settled callbacks inside our no-op handler, including after
 # final victory. Otherwise a duplicate could fall through to native annexation.
 settled='has_country_flag = MSGA_pact_real_capitulation is_subject_of = SER'
 winner=f'OR = {{ tag = SER is_subject_of = SER AND = {{ is_in_faction_with = SER OR = {{ has_war_together_with = SER ROOT = {{ {settled} }} }} }} }}'
 return 'MSGA_pact_capitulation_context = { has_country_flag = MSGA_pact_campaign_participant OR = { '+ ' '.join('tag = '+c[0] for c in COUNTRIES)+f' }} OR = {{ AND = {{ has_capitulated = yes NOT = {{ is_subject_of = SER }} }} AND = {{ {settled} }} }} SER = {{ has_country_flag = MSGA_pact_war_opened }} OR = {{ SER = {{ NOT = {{ has_country_flag = MSGA_balkan_coalition_defeated }} }} AND = {{ {settled} }} }} FROM = {{ {winner} }} }}'

def sha(data):return hashlib.sha256(data).hexdigest()

def wrap_native(text):
 """Locate only the first on_capitulation effect using comment-aware tokens."""
 tokens=[t for t in TOKEN.finditer(text) if not t.group().startswith('#')]
 i=next(i for i,t in enumerate(tokens) if t.group()=='on_capitulation')
 i=next(j for j in range(i,len(tokens)) if tokens[j].group()=='effect')+2
 assert tokens[i].group()=='{'
 depth=1;j=i+1
 while depth:
  depth+=(tokens[j].group()=='{')-(tokens[j].group()=='}');j+=1
 start=tokens[i].end();end=tokens[j-1].start()
 wrapper='\n\t\t\t# MSGA: only real capitulations in the approved five-country war.\n\t\t\tif = { limit = { MSGA_pact_capitulation_context = yes } MSGA_handle_pact_capitulation = yes }\n\t\t\telse = {'
 return text[:start]+wrapper+text[start:end].rstrip()+'\n\t\t\t}\n\t\t'+text[end:]

def main():
 assert LIVE.resolve(strict=True)==LIVE.absolute()
 baseline=json.loads((ROOT/'docs/encirclement_sync.json').read_text())['sha256']
 before={p.relative_to(LIVE).as_posix():sha(p.read_bytes()) for p in LIVE.rglob('*') if p.is_file()}
 assert before==baseline,'Runtime changed since approved 0.11; review before migration'
 content={};loc={};assets={}
 def put(path,text):
  if path.endswith(('.txt','.gfx')):parse(text)
  content[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
 def read(path):return (LIVE/path).read_text(encoding='utf-8-sig')
 def l(key,text):assert key not in loc;loc[key]=text

 # Make each still-fighting member count for the engine's all-majors rule.
 # Restore only the mandatory-major status introduced by this module.
 effects=['# Capital loss does not execute capitulation or settlement effects.',
 'MSGA_prepare_pact_campaign = {',
 ' if = { limit = { tag = SER has_country_flag = MSGA_pact_war_opened NOT = { has_country_flag = MSGA_balkan_coalition_defeated } }']
 for tag,*_ in COUNTRIES:
  effects += [f'  {tag} = {{ if = {{ limit = {{ exists = yes NOT = {{ is_subject_of = SER }} }} set_country_flag = MSGA_pact_campaign_participant',
   '   if = { limit = { is_major = no } set_major = yes set_country_flag = MSGA_pact_temporary_major }', '  } }']
 effects+=[' }','}', 'MSGA_start_pact_observer = {',
 ' if = { limit = { tag = SER has_country_flag = MSGA_pact_war_opened NOT = { has_country_flag = MSGA_balkan_coalition_defeated } NOT = { has_country_flag = MSGA_pact_observer_pending } MSGA_pact_has_unresolved_enemies = yes }',
 '  set_country_flag = MSGA_pact_observer_pending country_event = { id = MSGA_pactwar.90 days = 1 }',' }','}']
 triggers=[capitulation_context(),
 'MSGA_pact_has_unresolved_enemies = { OR = { '+ ' '.join(f'{tag} = {{ exists = yes has_country_flag = MSGA_pact_campaign_participant NOT = {{ is_subject_of = SER }} OR = {{ has_war_with = SER has_country_flag = MSGA_pact_real_capitulation }} }}' for tag,*_ in COUNTRIES)+' } }',
 'MSGA_pact_all_five_subjects = { '+ ' '.join(f'has_country_flag = MSGA_{stem}_defeated {tag} = {{ exists = yes is_subject_of = SER NOT = {{ has_war_with = SER }} has_country_flag = MSGA_pact_real_capitulation }}' for tag,s,p,stem,*_ in COUNTRIES)+' }']
 effects+=['MSGA_scan_pact_capitals = {',' if = { limit = { tag = SER has_country_flag = MSGA_pact_war_opened NOT = { has_country_flag = MSGA_balkan_coalition_defeated } }']
 capital_mods=['army_defence_factor = 0.05 max_dig_in_factor = 0.05','army_defence_factor = 0.05 army_org_factor = 0.05 army_org_regain = 0.05','max_dig_in_factor = 0.05 supply_consumption_factor = -0.05','army_org_factor = 0.05 supply_consumption_factor = -0.05','army_defence_factor = 0.075 army_org_factor = 0.05 army_org_regain = 0.05']
 recovery_mods=['stability_factor = 0.10 training_time_army_factor = 0.20 recruitable_population_factor = -0.20 army_attack_factor = -0.10','stability_factor = 0.10 war_support_factor = -0.10 training_time_army_factor = 0.15 army_attack_factor = -0.10','stability_factor = 0.10 war_support_factor = -0.20 recruitable_population_factor = -0.15 army_attack_factor = -0.10 army_defence_factor = -0.05','stability_factor = 0.10 production_speed_buildings_factor = 0.05 army_attack_factor = -0.10 mobilization_speed = -0.15','stability_factor = 0.15 war_support_factor = -0.20 army_attack_factor = -0.10 army_org_factor = -0.05 mobilization_speed = -0.20']
 cap_names=['Resistance in the Highlands','Defend What Remains','War in the Highlands','Retreat to the Alps','Fight Beyond Zagreb']
 rec_names=['Post-War Administration','Government Under Serbian Protection','A Defeated Albania','Government of National Recovery','The Defeated Coalition Leader']
 ideas=['ideas = { country = {']
 for i,(tag,state,province,stem,city,image,cd,rd) in enumerate(COUNTRIES):
  triggers += [f'MSGA_{city}_capital_eligible = {{ tag = SER has_country_flag = MSGA_pact_war_opened NOT = {{ has_country_flag = MSGA_{city}_fallen }} has_war_with = {tag} {tag} = {{ exists = yes has_country_flag = MSGA_pact_campaign_participant has_capitulated = no }} any_country = {{ controls_province = {province} has_war_with = {tag} {SIDE} }} }}']
  ws=[.05,.05,.05,.03,.10][i];xp=[10,10,15,10,20][i];st=.05 if tag in ('ALB','CRO') else 0
  enemy_ws=-.15 if tag in ('ALB','CRO') else -.10;enemy_st=-.15 if tag=='CRO' else -.10
  high=tag in ('MNT','ALB','SLV')
  effects += [f'  if = {{ limit = {{ MSGA_{city}_capital_eligible = yes }} set_country_flag = MSGA_{city}_fallen',
   f'   add_war_support = {ws:.2f} army_experience = {xp}'+(f' add_stability = {st:.2f}' if st else ''),
   f'   {tag} = {{ add_stability = {enemy_st:.2f} add_war_support = {enemy_ws:.2f} add_timed_idea = {{ idea = MSGA_{stem}_capital_resistance days = {cd} }}'+(' set_technology = { MSGA_highland_resistance_tech = 1 popup = no }' if high else '')+' }',
   f'   country_event = {{ id = MSGA_pactwar.{i*2+1} }}','  }']
  for kind,name,mods in [('capital_resistance',cap_names[i],capital_mods[i]),('postwar_recovery',rec_names[i],recovery_mods[i])]:
   key=f'MSGA_{stem}_{kind}'
   extra=' on_remove = { hidden_effect = { set_technology = { MSGA_highland_resistance_tech = 0 popup = no } } }' if high and kind=='capital_resistance' else ''
   tooltip=' custom_modifier_tooltip = MSGA_highland_defence_tt' if extra else ''
   ideas += [f' {key} = {{ picture = MSGA_prepared_for_war removal_cost = -1{extra} modifier = {{ {mods}{tooltip} }} }}']
   l(key,name);l(key+'_desc',f'{cd if kind=="capital_resistance" else rd}-day '+('defensive response after the loss of the capital. It does not change surrender conditions.' if kind=='capital_resistance' else 'recovery programme under Serbian protection. Existing territory and military formations remain with this country.'))
 effects+=[' }','}']
 ideas+=[' MSGA_pact_postwar_neutrality = { picture = MSGA_prepared_for_war removal_cost = -1 modifier = { ai_join_ally_desire_factor = -1 ai_call_ally_desire_factor = -1 } }','} }']
 l('MSGA_pact_postwar_neutrality','Recovering Outside the War');l('MSGA_pact_postwar_neutrality_desc','This Serbian subject remains outside the ongoing war against its former Pact allies. Faction admission is deferred until the campaign has ended.')
 l('MSGA_pact_decline_calls','Postwar military recovery');l('MSGA_highland_defence_tt','Mountain defence: §G+10%§! for land battalions.');l('MSGA_highland_resistance_tech','Highland Resistance');l('MSGA_highland_resistance_tech_desc','Temporary mountain defence attached to the capital-loss spirit. Removed when that spirit expires or the country capitulates.')

 # The native callback records proof, then dispatches a typed country effect.
 effects+=['# ROOT = actual capitulated country; FROM = victorious country in on_capitulation.',
 'MSGA_handle_pact_capitulation = {',' if = { limit = { NOT = { has_country_flag = MSGA_pact_real_capitulation } } set_country_flag = MSGA_pact_real_capitulation }']
 for tag,s,p,stem,*_ in COUNTRIES:effects+=[f' if = {{ limit = {{ tag = {tag} }} SER = {{ MSGA_settle_pact_{stem} = yes }} }}']
 effects+=['}','MSGA_retry_pact_settlements = {']
 for tag,s,p,stem,*_ in COUNTRIES:effects+=[f' MSGA_settle_pact_{stem} = yes']
 effects+=[' MSGA_finish_pact_campaign = yes','}']
 for i,(tag,s,p,stem,city,image,cd,rd) in enumerate(COUNTRIES):
  effects += [f'MSGA_settle_pact_{stem} = {{',
   f' if = {{ limit = {{ tag = SER has_country_flag = MSGA_pact_war_opened NOT = {{ has_country_flag = MSGA_{stem}_defeated }} {tag} = {{ exists = yes has_country_flag = MSGA_pact_campaign_participant has_country_flag = MSGA_pact_real_capitulation }} }}',
   f'  {tag} = {{',
   '   # Transfer faction leadership before leaving; the remaining members keep fighting.',
   '   if = { limit = { is_faction_leader = yes }']
  first=True
  for other,*_ in COUNTRIES:
   if other==tag:continue
   effects += [f'    {"if" if first else "else_if"} = {{ limit = {{ {other} = {{ exists = yes is_in_faction_with = {tag} has_capitulated = no has_war_with = SER NOT = {{ is_subject_of = SER }} }} }} {other} = {{ set_faction_leader = yes }} }}'];first=False
  effects+=['   }','   if = { limit = { is_in_faction = yes } leave_faction = yes }',
   f'   remove_ideas = MSGA_{stem}_capital_resistance',
   '  }',
   '  # Documented API: ends ONLY this target\'s non-civil war relations.',
   f'  set_autonomy = {{ target = {tag} autonomy_state = autonomy_puppet freedom_level = 0.5 end_wars = yes end_civil_wars = no }}',
   f'  if = {{ limit = {{ {tag} = {{ is_subject_of = SER NOT = {{ has_war_with = SER }} }} }}',
   f'   {tag} = {{',
   '    # Do not share Serbia\'s wartime faction: no automatic former-ally calls.',
   '    if = { limit = { is_in_faction = yes } leave_faction = yes }',
   '    set_rule = { can_decline_call_to_war = yes desc = MSGA_pact_decline_calls }',
   f'    add_ideas = MSGA_pact_postwar_neutrality add_timed_idea = {{ idea = MSGA_{stem}_postwar_recovery days = {rd} }}',
   '    if = { limit = { has_country_flag = MSGA_pact_temporary_major } set_major = no clr_country_flag = MSGA_pact_temporary_major }',
   '   }',
   '   # Restore occupied HOME states, never ownership, cores or Kosovo.',
   f'   every_state = {{ limit = {{ is_owned_by = {tag} controller = {{ {SIDE} }} }} set_state_controller_to = {tag} }}',
   f'   set_country_flag = MSGA_{stem}_defeated',
   f'   country_event = {{ id = MSGA_pactwar.{i*2+2} }}','  }',' }','}']
 effects+=['MSGA_finish_pact_campaign = {',
 ' if = { limit = { tag = SER has_country_flag = MSGA_pact_war_opened NOT = { has_country_flag = MSGA_balkan_coalition_defeated } MSGA_pact_all_five_subjects = yes }',
 '  set_country_flag = MSGA_balkan_coalition_defeated clr_country_flag = MSGA_pact_observer_pending']
 for tag,*_ in COUNTRIES:
  effects += [f'  {tag} = {{ remove_ideas = MSGA_pact_postwar_neutrality clear_rule = {{ can_decline_call_to_war = yes }} }}',
   f'  if = {{ limit = {{ has_war = no is_in_faction = yes }} every_country = {{ limit = {{ is_faction_leader = yes is_in_faction_with = SER }} add_to_faction = {tag} }} }}']
 effects+=['  country_event = { id = MSGA_pactwar.11 }',' }','}']
 put('common/scripted_effects/MSGA_pact_war_effects.txt','\n'.join(effects)+'\n')
 put('common/scripted_triggers/MSGA_pact_war_triggers.txt','\n'.join(triggers)+'\n')
 put('common/ideas/MSGA_pact_war_ideas.txt','\n'.join(ideas)+'\n')

 # The terrain effect is verified hidden-technology syntax used by native TFR.
 units={}
 for file in (TFR/'common/units').glob('*.txt'):
  for k,o,v in parse(file.read_text(encoding='utf-8-sig',errors='replace')):
   if k=='sub_units':
    for name,o,unit in v:
     categories=next((b for a,o,b in unit if a=='categories'),[])
     if any(a=='category_army' for a,o,b in categories):units[name]=unit
 assert 'infantry' in units and 'militia' in units and 'motorized' in units
 put('common/technologies/MSGA_pact_war_technologies.txt','technologies = { MSGA_highland_resistance_tech = { allow = { always = no } research_cost = 1 start_year = 1936 show_effect_as_desc = yes\n'+'\n'.join(f' {name} = {{ mountain = {{ defence = 0.10 }} }}' for name in sorted(units))+'\n} }\n')

 narratives=[
 ('Podgorica Has Fallen','Serbian forces have taken Podgorica, displacing Montenegro’s government and disrupting command across the coastal approaches. The loss of the capital has shaken public confidence.\\n\\nMontenegrin formations are withdrawing into the interior. Mountain roads and prepared positions still offer space for resistance; the country remains at war.','The mountains remain.'),
 ('Podgorica Submits','Montenegro’s armed resistance has ended in a formal capitulation. The administration in Podgorica has accepted Serbian protection, and Montenegro leaves the war as a separate state under Belgrade’s authority.\\n\\nRecovery takes precedence over another campaign. Its surviving forces remain Montenegrin, while the other Pact members continue their own resistance.','Establish the post-war administration.'),
 ('Skopje Has Fallen','The fall of Skopje has broken the government’s hold on the central Vardar corridor. Communications with the southern defensive line are under increasing pressure.\\n\\nNorth Macedonian units continue to defend the remaining routes and towns. The capital’s loss is a serious setback, but no surrender has been agreed.','The Vardar front remains active.'),
 ('Skopje Accepts Serbian Terms','North Macedonia has capitulated after the collapse of organised resistance. Skopje has accepted a government under Serbian protection and withdrawn from the Zagreb–Tirana Pact’s war.\\n\\nThe country retains its administration, territory and surviving military formations. Belgrade will supervise recovery while the remaining enemy governments continue fighting.','Secure the southern settlement.'),
 ('Tirana Has Fallen','Tirana has fallen to the Serbian side. Albania’s leadership has lost its principal political centre, as the campaign along the Kosovo frontier places further pressure on its remaining positions.\\n\\nAlbanian units are falling back towards the highlands. The war continues beyond the capital, and Serbia’s control of Kosovo remains unchanged.','The highlands still hold resistance.'),
 ('Tirana Accepts the New Order','Albania has formally capitulated. The authorities in Tirana have accepted Serbian overlordship, ending Albania’s participation in the Pact’s war without dissolving the Albanian state.\\n\\nIts surviving forces and home territory remain Albanian. Reconstruction will proceed under Serbian protection, while Kosovo remains under Serbian ownership and control.','Confirm the new administration.'),
 ('Ljubljana Has Fallen','Ljubljana has been occupied, severing the Slovenian government from its main administrative centre. The northern front now turns towards the approaches to the Alps.\\n\\nSlovenian formations are regrouping along mountain routes and defensive positions. The government has lost its capital, but the country has not yet capitulated.','The northern front continues.'),
 ('Ljubljana Seeks Terms','Slovenia’s remaining resistance has ended in capitulation. Ljubljana has accepted Serbian protection, leaving the enemy alliance and its active war participation.\\n\\nA government of national recovery will retain Slovenia’s territory and surviving forces. The Alpine settlement does not end the campaigns against the remaining Pact members.','Begin national recovery.'),
 ('Zagreb Has Fallen','Zagreb, the political centre of the Zagreb–Tirana Pact, has fallen. The occupation has dealt a major blow to Croatian command and to the coalition’s confidence.\\n\\nCroatian forces continue fighting beyond the capital. The Pact’s remaining members are still in the field; taking Zagreb has settled neither Croatia’s surrender nor the wider war.','The Pact’s capital has fallen. The war has not.'),
 ('The Leader of the Pact Falls','Croatia has capitulated and accepted Serbian overlordship. The government that led the Zagreb–Tirana Pact leaves the coalition’s war, while the Croatian state and its surviving forces remain in place.\\n\\nCroatia enters a period of supervised recovery. Any Pact members still resisting Serbia continue their campaigns independently; the coalition is defeated only when all five have submitted.','Place Croatia under Serbian protection.'),
 ('The Balkan Coalition Defeated','All five Zagreb–Tirana Pact governments have capitulated and entered Serbian subject status. No member remains in the coalition’s war against Serbia.\\n\\nBelgrade now oversees five separate administrations across the region. Recovery begins within the existing settlement; this announcement creates no territorial annexation or new political programme.','Confirm the end of the coalition war.'),
 ]
 events=['add_namespace = MSGA_pactwar']
 for id,(title,desc,option) in enumerate(narratives,1):
  if id==11:image='croatia_capitulates';condition='has_country_flag = MSGA_balkan_coalition_defeated'
  else:
   tag,s,p,stem,city,capimage,cd,rd=COUNTRIES[(id-1)//2]
   image=city+'_has_fallen' if id%2 else capimage
   condition='has_country_flag = MSGA_'+(city+'_fallen' if id%2 else stem+'_defeated')
  events += [f'country_event = {{ id = MSGA_pactwar.{id} title = MSGA_pactwar.{id}.t desc = MSGA_pactwar.{id}.d picture = GFX_MSGA_event_{image}',
   f' is_triggered_only = yes fire_only_once = yes trigger = {{ tag = SER {condition} }}',f' option = {{ name = MSGA_pactwar.{id}.a }}','}']
  for suffix,value in [('t',title),('d',desc),('a',option)]:l(f'MSGA_pactwar.{id}.{suffix}',value)
 events+=['# Active-war observer only. State control hooks alone can miss VP captures.',
 'country_event = { id = MSGA_pactwar.90 hidden = yes is_triggered_only = yes',
 ' immediate = { clr_country_flag = MSGA_pact_observer_pending if = { limit = { tag = SER has_country_flag = MSGA_pact_war_opened NOT = { has_country_flag = MSGA_balkan_coalition_defeated } }',
 '  MSGA_scan_pact_capitals = yes MSGA_retry_pact_settlements = yes MSGA_start_pact_observer = yes',' } }','}']
 put('events/MSGA_pact_war_events.txt','\n'.join(events)+'\n')
 put('common/on_actions/MSGA_pact_war_on_actions.txt','''on_actions = {
 on_startup = { effect = { SER = { MSGA_prepare_pact_campaign = yes MSGA_retry_pact_settlements = yes MSGA_start_pact_observer = yes } } }
 on_weekly = { effect = { SER = { MSGA_prepare_pact_campaign = yes MSGA_retry_pact_settlements = yes MSGA_start_pact_observer = yes } } }
 on_state_control_changed = { effect = { SER = { MSGA_scan_pact_capitals = yes } } }
}
''')
 original=read('common/scripted_effects/MSGA_encirclement_effects.txt')
 needle='set_country_flag = MSGA_pact_war_opened';assert original.count(needle)==1
 original=original.replace(needle,needle+'\n  MSGA_prepare_pact_campaign = yes')
 needle='country_event = { id = MSGA_encirclement.12 }';assert original.count(needle)==1
 put('common/scripted_effects/MSGA_encirclement_effects.txt',original.replace(needle,needle+'\n  MSGA_start_pact_observer = yes'))
 put(PEACE,wrap_native(read(PEACE)))
 # Preserve the attachment's exact ready-to-use GFX and ten DDS files.
 with zipfile.ZipFile(PACKAGE) as z:
  gfx=next(n for n in z.namelist() if n.endswith('/interface/MSGA_balkan_war_eventpictures.gfx'))
  put('interface/MSGA_balkan_war_eventpictures.gfx',z.read(gfx).decode('utf-8-sig'))
  for member in z.namelist():
   if '/gfx/event_pictures/' in member and member.endswith('.dds'):
    path='gfx/event_pictures/'+member.rsplit('/',1)[1];data=z.read(member)
    content[path]=data;assets[path]={'zip_member':member,'sha256':sha(data)}
 assert len(assets)==10
 # json.dumps escapes actual newlines; the game expects literal backslash-n.
 put('localisation/english/MSGA_pact_war_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False).replace('\\\\n','\\n') for k,v in loc.items())+'\n')
 for path in ['descriptor.mod','make_serbia_great_again.mod']:
  assert 'version="0.11.0"' in read(path)
  put(path,read(path).replace('version="0.11.0"','version="0.12.0"'))
 backup=ROOT/'logs/pact_war_012_backup';backup.mkdir(exist_ok=False)
 for path,data in sorted(content.items()):
  target=LIVE/path;assert target.resolve().is_relative_to(LIVE)
  if target.exists():
   saved=backup/path;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,saved)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 launcher=LIVE.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(LIVE/'make_serbia_great_again.mod',launcher)
 report={'version':'0.12.0','runtime':str(LIVE),'package':str(PACKAGE),'package_sha256':sha(PACKAGE.read_bytes()),'assets':assets,'changed_relative_paths':sorted(content),'deployed_absolute_paths':[str(LIVE/p) for p in sorted(content)]+[str(launcher)],'baseline_sha256':before,'backup':str(backup),'capitals':{tag:{'state':s,'province':p} for tag,s,p,*_ in COUNTRIES},'land_units_with_terrain_bonus':sorted(units),'native_guard_override':{'path':PEACE,'upstream_sha256':sha((TFR/PEACE).read_bytes()),'previous_local_sha256':before[PEACE]},'gameplay_test':'Reserved by user; no game window accessed'}
 (ROOT/'docs/pact_war_sources.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'Installed {len(content)} files into LIVE 0.12.0; source sync follows installed validation.')

if __name__=='__main__':main()
