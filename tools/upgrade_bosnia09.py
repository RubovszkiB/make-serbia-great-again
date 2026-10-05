"""Apply the 0.9 increment to the explicit primary runtime, before repository sync.

Run once against the installed 0.8 mod. A complete byte backup and deployment
manifest stay in ignored local storage. This never writes to Workshop TFR.
"""
from pathlib import Path
import hashlib, json, re, shutil, zipfile

ROOT = Path(__file__).resolve().parents[1]
LIVE = Path('C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again')
TFR = Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/3350890356')
ZIP = Path('C:/Users/Balazs/Downloads/MSGA_TFR_Bosnia_Kosovo_Event_Assets_70d.zip')
changes = {}

def read(path):
    return (LIVE/path).read_text(encoding='utf-8-sig')

def put(path, text):
    changes[path] = text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')

def block(text, key, replacement):
    start = re.search(r'(?m)^'+re.escape(key)+r'\s*=\s*\{', text).start()
    pos = text.index('{', start); depth = 1; end = pos+1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}'); end += 1
    return text[:start]+replacement.strip()+text[end:]

def event(id, picture, immediate='', options=None, once=True):
    if options is None: options = f'option = {{ name = {id}.a ai_chance = {{ factor = 100 }} }}'
    return f'''country_event = {{
 id = {id}
 title = {id}.t desc = {id}.d
 picture = GFX_MSGA_event_{picture}
 is_triggered_only = yes
 {'fire_only_once = yes' if once else ''}
 immediate = {{ {immediate} }}
 {options}
}}'''

def event_replace(text, id, replacement):
    match = re.search(r'country_event\s*=\s*\{\s*id\s*=\s*'+re.escape(id)+r'\s', text)
    start = match.start(); pos = text.index('{',start); end=pos+1; depth=1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}');end+=1
    return text[:start]+replacement+text[end:]

assert LIVE.resolve(strict=True)==LIVE.absolute()
source=ROOT/'make_serbia_great_again'
diff=[p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file() and (not (LIVE/p.relative_to(source)).exists() or p.read_bytes()!=(LIVE/p.relative_to(source)).read_bytes())]
assert not diff, f'Review existing live/project differences first: {diff}'

path='common/national_focus/MSGA_SER_bosnian_crisis.txt'
s=read(path).replace('military_development_var_temp value = 10','military_development_var_temp value = 0.10')
s=s.replace('add_equipment_to_stockpile = { type = train_equipment_1', 'set_technology = { basic_train = 1 } add_equipment_to_stockpile = { type = train_equipment_1')
s=s.replace('completion_reward = { country_event = { id = MSGA_bosnia.6 } }', 'completion_reward = { MSGA_release_srpska = yes }')
put(path,s)

path='common/scripted_effects/MSGA_bosnia_effects.txt';s=read(path)
s=block(s,'MSGA_release_srpska','''
MSGA_release_srpska = {
 if = { limit = { tag = SER has_country_flag = MSGA_bosnia_propaganda_prepared has_country_flag = MSGA_bosnia_military_prepared country_exists = BOS NOT = { country_exists = SRP } BOS = { has_war = no is_subject = no } 848 = { is_owned_by = BOS is_fully_controlled_by = BOS } 849 = { is_owned_by = BOS is_fully_controlled_by = BOS } 850 = { is_owned_by = BOS is_fully_controlled_by = BOS } }
  BOS = { release = SRP }
  # Current engine documents release as a puppet: independence must precede war.
  if = { limit = { SRP = { is_subject_of = BOS } } BOS = { end_puppet = SRP } }
  if = { limit = { country_exists = SRP SRP = { is_subject = no } }
   SRP = {
    transfer_state = 848 transfer_state = 849 transfer_state = 850
    set_capital = { state = 848 }
    delete_unit = { disband = no }
    set_politics = { ruling_party = social_democrat elections_allowed = no }
    promote_character = SRP_milorad_dodik_char
    load_oob = "MSGA_SRP_guard"
    add_ideas = MSGA_SRP_last_stand add_ideas = MSGA_campaign_isolation
    set_country_flag = MSGA_bosnia_custom_release
   }
   set_country_flag = MSGA_bosnia_story_active set_country_flag = MSGA_srpska_released
   country_event = { id = MSGA_bosnia.6 }
   MSGA_begin_bosnian_war = yes
  }
 }
}''')
s=block(s,'MSGA_begin_bosnian_war','''
MSGA_begin_bosnian_war = {
 if = { limit = { tag = SER has_country_flag = MSGA_srpska_released NOT = { has_country_flag = MSGA_bosnian_war_started } country_exists = BOS country_exists = SRP SRP = { is_subject = no } BOS = { NOT = { has_war_with = SRP } } }
  every_other_country = {
   if = { limit = { has_guaranteed = SRP } set_country_flag = MSGA_restore_SRP_guarantee diplomatic_relation = { country = SRP relation = guarantee active = no } }
  }
  if = { limit = { SRP = { is_in_faction = yes is_faction_leader = no } } SRP = { every_other_country = { limit = { is_in_faction_with = SRP is_faction_leader = yes } remove_from_faction = SRP } } }
  BOS = { declare_war_on = { target = SRP type = annex_everything } }
  if = { limit = { SRP = { has_war_with = BOS } }
   set_country_flag = MSGA_bosnian_war_started
   MSGA_check_bosnian_intervention = yes
   MSGA_schedule_bosnia_observer = yes
  }
 }
}''')
s=block(s,'MSGA_check_bosnian_intervention','''
MSGA_check_bosnian_intervention = {
 if = { limit = { has_country_flag = MSGA_bosnia_story_active has_country_flag = MSGA_bosnian_war_started country_exists = SRP country_exists = BOS SRP = { has_war_with = BOS has_capitulated = no } NOT = { has_war_with = BOS } NOT = { has_country_flag = MSGA_bosnia_intervention_fired } }
  set_country_flag = MSGA_bosnia_intervention_fired
  country_event = { id = MSGA_bosnia.9 days = 1 }
 }
}''')
s=block(s,'MSGA_join_srpska_war','''
MSGA_join_srpska_war = {
 if = { limit = { tag = SER has_country_flag = MSGA_bosnia_intervention_fired NOT = { has_country_flag = MSGA_bosnia_intervened } country_exists = SRP country_exists = BOS SRP = { has_war_with = BOS has_capitulated = no } NOT = { has_war_with = BOS } }
  if = { limit = { is_in_faction = yes }
   if = { limit = { is_faction_leader = yes } dismantle_faction = yes }
   else = { every_other_country = { limit = { is_faction_leader = yes is_in_faction_with = SER } remove_from_faction = SER } }
  }
  create_faction = MSGA_serbian_alliance
  add_to_faction = SRP
  if = { limit = { is_faction_leader = yes SRP = { is_in_faction_with = SER } }
   add_to_war = { targeted_alliance = SRP enemy = BOS hostility_reason = asked_to_join single_target_only = yes }
   if = { limit = { has_war_with = BOS } set_country_flag = MSGA_bosnia_intervened add_war_support = 0.03 }
  }
 }
}''')
s=s.replace('limit = { has_country_flag = MSGA_watched_bosnian_conflict has_country_flag = MSGA_bosnia_story_active','limit = { has_country_flag = MSGA_bosnia_story_active')
s += '''
# Only our local war can enter this settlement. Flag first prevents peace-hook recursion.
MSGA_settle_bosnia = {
 if = { limit = { tag = SER has_country_flag = MSGA_bosnian_war_started has_country_flag = MSGA_bosnia_intervened NOT = { has_country_flag = MSGA_bosnia_settlement_done } country_exists = BOS country_exists = SRP OR = { has_country_flag = MSGA_bosnia_defeated BOS = { has_capitulated = yes } AND = { controls_state = 104 controls_state = 851 } } }
  set_country_flag = MSGA_bosnia_settlement_done
  if = { limit = { has_war_with = BOS } white_peace = BOS }
  SRP = { if = { limit = { has_war_with = BOS } white_peace = BOS } transfer_state = 848 transfer_state = 849 transfer_state = 850 }
  BOS = { transfer_state = 104 set_capital = { state = 104 } }
  # TFR's HRZ tag exists, but its dormant history belongs to an Iranian faction.
  851 = { add_core_of = HRZ }
  HRZ = { transfer_state = 851 set_capital = { state = 851 } set_politics = { ruling_party = authoritarian_democrat elections_allowed = no } }
  set_autonomy = { target = BOS autonomy_state = autonomy_puppet end_wars = no end_civil_wars = no }
  set_autonomy = { target = HRZ autonomy_state = autonomy_puppet end_wars = no end_civil_wars = no }
  set_autonomy = { target = SRP autonomy_state = autonomy_puppet end_wars = no end_civil_wars = no }
  add_to_faction = BOS add_to_faction = HRZ add_to_faction = SRP
  MSGA_cleanup_bosnia_war_modifiers = yes
  country_event = { id = MSGA_bosnia.10 }
  country_event = { id = MSGA_bosnia.11 days = 70 }
  set_country_flag = MSGA_srpska_question_scheduled
 }
}
MSGA_unite_srpska = {
 if = { limit = { tag = SER has_country_flag = MSGA_bosnia_settlement_done country_exists = SRP SRP = { is_subject_of = SER has_war = no } NOT = { has_country_flag = MSGA_srpska_question_resolved } }
  annex_country = { target = SRP transfer_troops = yes }
  set_temp_variable = { var = debt_var_temp value = 1 } add_debt = yes
  set_country_flag = MSGA_srpska_question_resolved set_country_flag = MSGA_srpska_united
 }
}
MSGA_recover_bosnia_chain = {
 if = { limit = { tag = SER has_country_flag = MSGA_bosnian_crisis_active NOT = { has_country_flag = MSGA_bosnia_settlement_done } }
  if = { limit = { has_completed_focus = MSGA_prepare_the_nation_for_war } set_country_flag = MSGA_bosnia_propaganda_prepared }
  if = { limit = { has_completed_focus = MSGA_prepare_for_the_unthinkable } set_country_flag = MSGA_bosnia_military_prepared }
  if = { limit = { has_completed_focus = MSGA_seed_the_rebellion_in_bosnia NOT = { country_exists = SRP } } MSGA_release_srpska = yes }
  if = { limit = { has_country_flag = MSGA_srpska_released country_exists = SRP NOT = { has_country_flag = MSGA_bosnian_war_started } } MSGA_begin_bosnian_war = yes }
  if = { limit = { has_country_flag = MSGA_bosnian_war_started SRP = { has_war_with = BOS } NOT = { has_country_flag = MSGA_bosnia_intervened } }
   # Requeue a consumed old one-shot prompt when upgrading a campaign.
   if = { limit = { has_country_flag = MSGA_bosnia_intervention_fired NOT = { has_country_flag = MSGA_bosnia_intervention_recovered } } set_country_flag = MSGA_bosnia_intervention_recovered country_event = { id = MSGA_bosnia.9 days = 1 } }
   else = { MSGA_check_bosnian_intervention = yes }
  }
 }
}
'''
s=s.replace('if = { limit = { tag = SER has_country_flag = MSGA_campaign_active }','if = { limit = { tag = SER has_country_flag = MSGA_campaign_active }\n  MSGA_recover_bosnia_chain = yes',1)
put(path,s)

path='events/MSGA_bosnia_events.txt';s=read(path)
s=event_replace(s,'MSGA_bosnia.6',event('MSGA_bosnia.6','srpska_uprising',once=False))
s=event_replace(s,'MSGA_bosnia.9',event('MSGA_bosnia.9','serbia_enters_bosnian_war', options='option = { name = MSGA_bosnia.9.a ai_chance = { factor = 100 } MSGA_join_srpska_war = yes }',once=False))
s+='\n'+event('MSGA_bosnia.10','bosnia_capitulation')+'\n'+event('MSGA_bosnia.11','question_of_republika_srpska',options='''
 option = { name = MSGA_bosnia.11.a trigger = { country_exists = SRP SRP = { is_subject_of = SER has_war = no } NOT = { has_country_flag = MSGA_srpska_question_resolved } } ai_chance = { factor = 70 } MSGA_unite_srpska = yes }
 option = { name = MSGA_bosnia.11.b ai_chance = { factor = 30 } set_country_flag = MSGA_srpska_question_resolved }
''')+'\n'
put(path,s)
path='common/on_actions/MSGA_bosnia_on_actions.txt';s=read(path)
s=s.replace('on_actions = {','''on_actions = {
 on_capitulation_immediate = { effect = { if = { limit = { ROOT = { tag = BOS } FROM = { OR = { tag = SER tag = SRP } } SER = { has_country_flag = MSGA_bosnia_intervened } } SER = { set_country_flag = MSGA_bosnia_defeated MSGA_settle_bosnia = yes } } } }
 on_state_control_changed = { effect = { SER = { MSGA_settle_bosnia = yes } } }
''',1)
s=s.replace('MSGA_cleanup_bosnia_war_modifiers = yes } } }','MSGA_recover_bosnia_chain = yes MSGA_settle_bosnia = yes MSGA_cleanup_bosnia_war_modifiers = yes } } }',1)
put(path,s)
# Minimal native-tag corrections; do not copy the large third-party country history.
put('history/countries/HRZ - Herzegovina.txt','''capital = 851
set_research_slots = 2
set_stability = 0.45
set_war_support = 0.20
set_politics = { ruling_party = authoritarian_democrat elections_allowed = no }
set_popularities = { authoritarian_democrat = 100 }
recruit_character = MSGA_herzegovina_council
set_technology = { infantry_weapons1 = 1 infantry_weapons2 = 1 motorised_infantry = 1 basic_train = 1 }
''')
put('common/characters/MSGA_bosnia_characters.txt','''characters = {
 MSGA_herzegovina_council = {
  name = MSGA_herzegovina_council
  country_leader = { ideology = military_democracy }
 }
}
''')

# Two existing focuses retain their previous factories as well as the new rewards.
path='common/scripted_effects/MSGA_SER_post_kosovo_effects.txt';s=read(path)
s=s.replace('  set_country_flag = MSGA_kosovo_reconstruction_done','''  set_country_flag = MSGA_kosovo_reconstruction_done
  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
  MSGA_cleanup_kosovo_campaign = yes
  remove_ideas = SER_rebellion_of_kosovo
  add_timed_idea = { idea = MSGA_kosovo_development_program days = 180 }''')
s=s.replace('  set_country_flag = MSGA_pristina_investment_done','''  set_country_flag = MSGA_pristina_investment_done
  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes''')
s=s.replace('  country_event = { id = MSGA_postkosovo.7 }','''  785 = {
   damage_building = { type = infrastructure damage = -100 }
   damage_building = { type = industrial_complex damage = -100 }
   damage_building = { type = office_park damage = -100 }
   add_dynamic_modifier = { modifier = MSGA_kosovo_reconstruction_state days = 180 }
  }
  country_event = { id = MSGA_postkosovo.7 }''')
s=s.replace('  country_event = { id = MSGA_postkosovo.9 }','''  785 = { if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } }
  country_event = { id = MSGA_postkosovo.9 }''')
s+='''
MSGA_pristina_state_investment = {
 if = { limit = { 785 = { is_owned_by = SER is_fully_controlled_by = SER } NOT = { has_country_flag = MSGA_pristina_path_chosen } check_variable = { var = income_var value = 0.5 compare = greater_than_or_equals } }
  set_temp_variable = { var = income_var_temp value = -0.5 } add_income = yes
  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
  785 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } }
  add_stability = 0.02 set_country_flag = MSGA_pristina_path_chosen
 }
}
MSGA_pristina_private_investment = {
 if = { limit = { 785 = { is_owned_by = SER is_fully_controlled_by = SER } NOT = { has_country_flag = MSGA_pristina_path_chosen } }
  set_temp_variable = { var = industrial_development_var_temp value = 0.03 } add_industrial_development = yes
  785 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = office_park level = 1 instant_build = yes } if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } }
  add_ideas = MSGA_pristina_private_capital set_country_flag = MSGA_pristina_path_chosen
 }
}
MSGA_complete_kosovo_reconstruction = {
 if = { limit = { has_country_flag = MSGA_kosovo_reconstruction_done has_country_flag = MSGA_pristina_investment_done NOT = { has_country_flag = MSGA_kosovo_rebuilt } 785 = { is_owned_by = SER is_fully_controlled_by = SER } check_variable = { var = income_var value = 1 compare = greater_than_or_equals } }
  set_temp_variable = { var = income_var_temp value = -1 } add_income = yes
  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
  785 = { if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } if = { limit = { has_dynamic_modifier = { modifier = MSGA_kosovo_reconstruction_state } } remove_dynamic_modifier = { modifier = MSGA_kosovo_reconstruction_state } } }
  remove_ideas = MSGA_kosovo_development_program remove_ideas = SER_rebellion_of_kosovo
  MSGA_cleanup_kosovo_campaign = yes
  set_country_flag = MSGA_kosovo_rebuilt country_event = { id = MSGA_postkosovo.15 }
 }
}
''';put(path,s)
path='common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt';s=read(path)+'''
MSGA_kosovo_reconstruction_state = {
 enable = { always = yes }
 state_production_speed_buildings_factor = 0.10
 state_repair_speed_infrastructure_factor = 0.20
 state_repair_speed_industrial_complex_factor = 0.20
 state_repair_speed_arms_factory_factor = 0.20
 state_repair_speed_office_park_factor = 0.20
}
''';put(path,s)
put('common/ideas/MSGA_reconstruction_ideas.txt','''ideas = { country = {
 MSGA_kosovo_development_program = { picture = MSGA_prepared_for_war allowed = { tag = SER } removal_cost = -1 modifier = { industrial_development_monthly = 0.005 } }
 MSGA_pristina_private_capital = { picture = MSGA_command_structure allowed = { tag = SER } removal_cost = -1 modifier = { business_value_factor = 0.05 income_growth_factor = 0.02 } }
} }
''')
path='events/MSGA_SER_post_kosovo_events.txt';s=read(path)
s=event_replace(s,'MSGA_postkosovo.7',event('MSGA_postkosovo.7','kosovo_reconstruction_begins','country_event = { id = MSGA_postkosovo.8 days = 2 }'))
s=event_replace(s,'MSGA_postkosovo.9',event('MSGA_postkosovo.9','future_of_pristina','country_event = { id = MSGA_postkosovo.10 days = 2 }',options='''
 option = { name = MSGA_postkosovo.9.a trigger = { check_variable = { var = income_var value = 0.5 compare = greater_than_or_equals } } ai_chance = { factor = 50 } MSGA_pristina_state_investment = yes }
 option = { name = MSGA_postkosovo.9.b ai_chance = { factor = 50 } MSGA_pristina_private_investment = yes }
'''))
s+='\n'+event('MSGA_postkosovo.15','kosovo_rebuilt')+'\n';put(path,s)
path='common/decisions/MSGA_SER_post_kosovo.txt';s=read(path)
s=s.rsplit('}',1)[0]+'''
 MSGA_finish_kosovo_reconstruction = {
  icon = generic_construction
  allowed = { tag = SER }
  visible = { has_country_flag = MSGA_kosovo_reconstruction_done has_country_flag = MSGA_pristina_investment_done NOT = { has_country_flag = MSGA_kosovo_rebuilt } }
  available = { 785 = { is_owned_by = SER is_fully_controlled_by = SER } 1305 = { is_owned_by = SER is_fully_controlled_by = SER } }
  cost = 50 custom_cost_text = MSGA_cost_1B
  custom_cost_trigger = { check_variable = { var = income_var value = 1 compare = greater_than_or_equals } }
  fire_only_once = yes
  complete_effect = { MSGA_complete_kosovo_reconstruction = yes }
  ai_will_do = { factor = 5 }
 }
}
''';put(path,s)
path='common/decisions/MSGA_SER_strategic_review.txt';s=read(path);put(path,s[:s.index('MSGA_kosovo_crisis =')].rstrip()+'\n')
path='common/decisions/categories/MSGA_SER_categories.txt';put(path,block(read(path),'MSGA_kosovo_crisis',''))

locale={
 'MSGA_serbian_alliance':'Serbian Alliance', 'MSGA_herzegovina_council':'Herzegovina Reconstruction Council',
 'MSGA_bosnia.6.t':'The Republika Srpska Uprising',
 'MSGA_bosnia.8.d':'Sarajevo has ordered its forces to restore its authority over Northern Srpska, Eastern Srpska and Brčko. The secession has become an open war.',
 'MSGA_bosnia.9.t':'Serbia Enters the War',
 'MSGA_bosnia.9.d':'Belgrade declares that it cannot remain neutral while Republika Srpska fights for survival. Serbia will establish the Serbian Alliance, admit Srpska and enter its existing war against Sarajevo.',
 'MSGA_bosnia.9.a':'Establish the alliance and enter the war.',
 'MSGA_bosnia.10.t':'The New Order in Bosnia',
 'MSGA_bosnia.10.d':'Sarajevo has accepted defeat. Central Bosnia, Herzegovina and Republika Srpska now retain separate administrations under Serbian protection. The fighting ends as Belgrade assumes responsibility for the settlement.',
 'MSGA_bosnia.10.a':'Three administrations, one settlement.',
 'MSGA_bosnia.11.t':'The Question of Republika Srpska',
 'MSGA_bosnia.11.d':'Seventy days after the settlement, Belgrade must decide whether Srpska should remain a protected republic or unite with Serbia. Unification will add $1B to national debt; it will not create new Serbian cores.',
 'MSGA_bosnia.11.a':'Unite Republika Srpska with Serbia', 'MSGA_bosnia.11.b':'Not Yet',
 'MSGA_postkosovo.7.t':'The Reconstruction of Kosovo Begins',
 'MSGA_postkosovo.7.d':'Road repairs and reconstruction contracts begin in Kosovo. A six-month programme supports local construction and industrial development while damaged buildings are restored.',
 'MSGA_postkosovo.9.t':'The Future of Pristina',
 'MSGA_postkosovo.9.d':'The city has received new public and commercial capacity. Direct state investment costs $0.5B and builds another civilian factory. Private Serbian capital adds an office park, improves business value and raises monthly income growth.',
 'MSGA_postkosovo.9.a':'State-Led Reconstruction', 'MSGA_postkosovo.9.b':'Invite Serbian Private Capital',
 'MSGA_postkosovo.15.t':'Kosovo Rebuilt', 'MSGA_postkosovo.15.d':'The final reconstruction programme has restored local services and expanded Kosovo’s infrastructure. Emergency reconstruction measures can now end.', 'MSGA_postkosovo.15.a':'A new chapter begins.',
 'MSGA_finish_kosovo_reconstruction':'Complete the Reconstruction of Kosovo',
 'MSGA_finish_kosovo_reconstruction_desc':'Spend 50 political power and $1B from the treasury to add 5% industrial development and one infrastructure level, up to the state limit. Both reconstruction focuses must be complete. Emergency reconstruction modifiers are removed.',
 'MSGA_cost_1B':'§Y$1B§!', 'MSGA_kosovo_reconstruction_state':'Kosovo Reconstruction',
 'MSGA_kosovo_development_program':'Kosovo Development Programme', 'MSGA_kosovo_development_program_desc':'A temporary programme adds 0.5% industrial development each month for 180 days.',
 'MSGA_pristina_private_capital':'Serbian Capital in Pristina', 'MSGA_pristina_private_capital_desc':'Commercial investment raises business value by 5% and monthly income growth by 2%.',
}
# Update existing keys in-place and write only genuinely new keys to a new file.
for p in (LIVE/'localisation/english').glob('*.yml'):
    s=p.read_text(encoding='utf-8-sig');changed=False
    for key,value in list(locale.items()):
        pattern=r'(?m)^ '+re.escape(key)+r':\d .*?$'
        if re.search(pattern,s):
            s=re.sub(pattern,lambda _:f' {key}:0 "{value}"',s);del locale[key];changed=True
    if changed:put(p.relative_to(LIVE).as_posix(),s)
put('localisation/english/MSGA_settlement_l_english.yml','l_english:\n'+''.join(f' {k}:0 "{v}"\n' for k,v in locale.items()))

with zipfile.ZipFile(ZIP) as package:
    for name in package.namelist():
        relative='/'.join(name.split('/')[1:])
        if relative.startswith('gfx/event_pictures/') and relative.endswith('.dds') or relative=='interface/MSGA_eventpictures.gfx':changes[relative]=package.read(name)

for path in ['descriptor.mod','make_serbia_great_again.mod']:
    put(path,read(path).replace('version="0.8.0"','version="0.9.0"'))

path='common/national_focus/MSGA_SER_phase1.txt'
s=read(path)
s=re.sub(r'(?m)^\s*unlock_decision_tooltip = MSGA_(commission_kosovo_dossier|assess_kfor|consult_general_staff|contact_regional_partners|map_northern_contingencies)\s*\n','\n',s)
put(path,s)

backup=ROOT/'logs/upgrade09_backup';backup.mkdir(parents=True,exist_ok=True)
assert not (backup/'manifest.json').exists(), 'Already applied; use reviewed incremental repairs instead of rerunning.'
records=[]
for relative,data in changes.items():
    target=LIVE/relative;assert target.resolve().is_relative_to(LIVE)
    before=target.read_bytes() if target.exists() else None
    if before==data:continue
    if before is not None:
        dest=backup/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(before)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    records.append({'file':str(target),'relative':relative,'before_sha256':hashlib.sha256(before).hexdigest() if before else None,'after_sha256':hashlib.sha256(data).hexdigest()})
launcher=LIVE.parent/'make_serbia_great_again.mod'
shutil.copyfile(LIVE/'make_serbia_great_again.mod',launcher)
(backup/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
(ROOT/'docs/upgrade09_deployment.json').write_text(json.dumps({'runtime_target':str(LIVE),'files':records,'launcher_descriptor':str(launcher),'repo_sync':'pending live validation'},indent=2)+'\n')
print(f'Applied {len(records)} files to {LIVE}; descriptor updated; local backup: {backup}')
