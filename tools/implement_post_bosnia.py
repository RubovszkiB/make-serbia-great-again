"""Install the authorized 0.10 chapter into the live MSGA mod first.

One-time migration from b4d79a4. Never writes to Workshop TFR or game saves.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import shutil
import subprocess
import zipfile
from PIL import Image
from validate_phase1 import parse

ROOT = Path(__file__).resolve().parents[1]
LIVE = Path(r'C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again')
TFR = Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
PACKAGE = Path(r'C:\Users\Balazs\Downloads\MSGA_Post_Bosnia_TFR_Assets_100d.zip')

# Stem, title, position, prerequisite, reward. Three opening + three in each branch.
FOCUSES = [
 ('victory_in_bosnia','Victory in Bosnia',4,0,None,'add_stability = 0.05 add_political_power = 25 MSGA_cleanup_bosnia_war_modifiers = yes country_event = { id = MSGA_postbosnia.1 }'),
 ('rebuild_the_west','Rebuild the West',4,1,'victory_in_bosnia','MSGA_rebuild_western_regions = yes country_event = { id = MSGA_postbosnia.2 }'),
 ('new_serbian_era','A New Serbian Era',4,2,'rebuild_the_west','add_political_power = 25 country_event = { id = MSGA_postbosnia.3 }'),
 ('lessons_bosnian_war','Lessons of the Bosnian War',0,3,'new_serbian_era','army_experience = 25 add_doctrine_cost_reduction = { name = MSGA_bosnian_lessons_bonus cost_reduction = 0.25 uses = 1 category = cat_old_land_doctrine } add_timed_idea = { idea = MSGA_bosnian_war_lessons days = 180 } country_event = { id = MSGA_postbosnia.4 }'),
 ('arm_new_serbian_sphere','Arm the New Serbian Sphere',0,4,'lessons_bosnian_war','set_country_flag = MSGA_protectorate_militias_unlocked unlock_decision_tooltip = MSGA_organise_bosnian_territorial_militias unlock_decision_tooltip = MSGA_organise_herzegovinian_territorial_militias'),
 ('serbian_defence_network','The Serbian Defence Network',0,5,'arm_new_serbian_sphere','set_country_flag = MSGA_srpska_td_unlocked unlock_decision_tooltip = MSGA_form_srpska_territorial_defence'),
 ('consolidate_victory','Consolidate the Victory',4,3,'new_serbian_era','add_stability = 0.05 add_political_power = 50 if = { limit = { has_power_balance = { id = MSGA_SER_streets_presidency } } add_power_balance_value = { id = MSGA_SER_streets_presidency value = 0.10 } } country_event = { id = MSGA_postbosnia.8 }'),
 ('bind_new_protectorates','Bind the New Protectorates',4,4,'consolidate_victory','MSGA_bind_balkan_protectorates = yes country_event = { id = MSGA_postbosnia.9 }'),
 ('serbian_sphere','The Serbian Sphere',4,5,'bind_new_protectorates','add_ideas = MSGA_serbian_sphere_spirit MSGA_integrate_balkan_subjects = yes country_event = { id = MSGA_postbosnia.14 }'),
 ('repair_war_economy','Repair the War Economy',8,3,'new_serbian_era','MSGA_repair_postwar_economy = yes country_event = { id = MSGA_postbosnia.10 }'),
 ('serbian_industrial_consolidation','Serbian Industrial Consolidation',8,4,'repair_war_economy','MSGA_consolidate_postwar_industry = yes country_event = { id = MSGA_postbosnia.11 }'),
 ('economic_heart_balkans','The Economic Heart of the Balkans',8,5,'serbian_industrial_consolidation','add_ideas = MSGA_economic_heart_spirit country_event = { id = MSGA_postbosnia.15 }'),
]

EVENTS = {
 1: ('victory_in_bosnia','Victory in Bosnia','Bosnia has accepted defeat. Republika Srpska survives under Serbian protection, while Bosnia and Herzegovina enter the new settlement. Victory now brings a responsibility to rebuild.','A new chapter begins.'),
 2: ('cost_of_victory','The Cost of Victory','Roads, factories and public services bear the cost of the war. Engineers are repairing the western regions and the protectorates. A six-month reconstruction programme will support their recovery.','We will rebuild.'),
 3: ('new_serbian_era','A New Serbian Era','Kosovo and Bosnia have changed Serbia’s position. The army must learn, the government must consolidate and the economy must recover. All three tasks now stand before Belgrade.','Begin the transformation.'),
 4: ('lessons_written_in_blood','Lessons Written in Blood','Staff officers examine the fighting across the Drina. Better planning and cooperation will matter more than another victory parade. The lessons will guide training and doctrine.','Learn from the campaign.'),
 5: ('bosnian_territorial_militias','Territorial Militias for Bosnia','Two Bosnian territorial brigades have been organised for local security and service alongside the Serbian army. Their equipment is simple; their mission is to hold roads, settlements and supply routes.','Place them under Serbian command.'),
 6: ('herzegovinian_territorial_militias','Territorial Militias for Herzegovina','Two Herzegovinian territorial brigades have entered service. They retain their regional names and serve directly under Serbian command, allowing Belgrade to coordinate their deployment.','Secure the western approaches.'),
 7: ('srpska_territorial_defence','The Srpska Territorial Defence','The new Srpska formation follows the Kosovo brigade model: mobile militia, mechanised troops, APCs and a small reserve tank support element. Serbian command will retain the unit whatever Srpska’s constitutional future.','A lasting investment in defence.'),
 8: ('victory_strengthens_belgrade','Victory Strengthens Belgrade','Victory has strengthened the presidency’s position. The government seeks to turn public confidence into stable institutions and lasting authority.','Consolidate the victory.'),
 9: ('bind_new_protectorates','Bind the New Protectorates','Belgrade and the remaining protectorates establish common political and commercial arrangements. These agreements concern the subjects that still exist; Srpska’s annexation will not interrupt them.','Build dependable ties.'),
 10: ('from_war_to_reconstruction','From War to Reconstruction','Emergency spending gives way to economic recovery. Debt relief, industrial development and a modest income programme begin the transition to a sustainable peace.','Restore the war economy.'),
 11: ('factories_for_peace','Factories for Peace','New civilian factories and an office park turn wartime mobilisation toward employment and commerce. Their value will be measured in production and reliable livelihoods.','Build for peace.'),
 13: ('one_serbian_state','One Serbian State','Republika Srpska has joined Serbia. Its territory and military formations pass to Belgrade, alongside one billion dollars of additional national debt. Administrative integration will take time.','One state, with new responsibilities.'),
 14: ('serbian_sphere','Belgrade at the Centre','Political cooperation, trade and security now tie the remaining protectorates to Belgrade. Serbia’s influence rests on these practical connections.','Strengthen the Serbian sphere.'),
 15: ('economic_heart_of_balkans','The Economic Heart of the Balkans','Industrial recovery and commercial investment have strengthened Serbia’s economy. Belgrade aims to become the region’s dependable centre for production and trade.','Prosperity must sustain our influence.'),
 16: ('regional_power','Serbia: A Regional Power','The military, political and economic programmes are complete. Serbia has emerged from the wars with a stronger state and a wider regional role. The task now is to sustain that position.','A new regional power.'),
}

def main():
    assert LIVE.resolve(strict=True) == LIVE.absolute()
    assert not subprocess.check_output(['git','status','--porcelain','--','make_serbia_great_again'],cwd=ROOT).strip()
    expected=json.loads((ROOT/'docs/github_runtime_sync.json').read_text())['sha256']
    current={p.relative_to(LIVE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in LIVE.rglob('*') if p.is_file()}
    assert current==expected, 'Unreviewed live changes: inspect before installing'
    content={}
    def put(path,text):
        if path.endswith(('.txt','.gfx')):parse(text)
        content[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
    def read(path):return (LIVE/path).read_text(encoding='utf-8-sig')
    # No additional subjects or narrative flags can block a completed settlement.
    tree=['focus_tree = {',' id = MSGA_SER_post_bosnia',' country = { factor = 0 modifier = { add = 250 tag = SER has_country_flag = MSGA_post_bosnia_active } }',' default = no',' reset_on_civilwar = no']
    for stem,title,x,y,parent,reward in FOCUSES:
        tree += [' focus = {',f'  id = MSGA_{stem}',f'  icon = GFX_MSGA_focus_{stem}',f'  x = {x} y = {y} cost = 2']
        if parent:tree += [f'  prerequisite = {{ focus = MSGA_{parent} }}']
        tree += ['  available = { has_country_flag = MSGA_bosnia_settlement_done }','  ai_will_do = { factor = 10 }',f'  completion_reward = {{ set_country_flag = MSGA_completed_{stem} {reward} MSGA_check_regional_power = yes }}',' }']
    put('common/national_focus/MSGA_SER_post_bosnia.txt','\n'.join(tree+['}'])+'\n')
    put('common/scripted_effects/MSGA_post_bosnia_effects.txt','''# All effects are scoped to Serbia; the settlement flag owns chapter progression.
MSGA_open_post_bosnia = {
 if = { limit = { tag = SER has_country_flag = MSGA_bosnia_settlement_done NOT = { has_country_flag = MSGA_post_bosnia_started } }
  set_country_flag = MSGA_post_bosnia_started set_country_flag = MSGA_post_bosnia_active
  clr_country_flag = MSGA_bosnian_crisis_active
  load_focus_tree = { tree = MSGA_SER_post_bosnia keep_completed = yes }
 }
}
MSGA_check_srpska_question = {
 if = { limit = { tag = SER has_country_flag = { flag = MSGA_bosnia_settlement_done days > 99 } NOT = { has_country_flag = MSGA_srpska_question_resolved } NOT = { has_country_flag = MSGA_srpska_question_delivered } }
  country_event = { id = MSGA_postbosnia.12 }
 }
}
MSGA_rebuild_western_regions = {
 set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
 1296 = { if = { limit = { is_owned_by = SER is_fully_controlled_by = SER infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } }
 every_state = { limit = { OR = { state = 1296 state = 104 state = 851 state = 848 state = 849 state = 850 } OR = { AND = { is_owned_by = SER is_fully_controlled_by = SER } AND = { owner = { is_subject_of = SER } is_fully_controlled_by = OWNER } } }
  damage_building = { type = infrastructure damage = -100 }
  damage_building = { type = industrial_complex damage = -100 }
  damage_building = { type = arms_factory damage = -100 }
  damage_building = { type = office_park damage = -100 }
  add_dynamic_modifier = { modifier = MSGA_western_reconstruction days = 180 }
 }
}
MSGA_bind_balkan_protectorates = {
 every_subject_country = { limit = { OR = { tag = BOS tag = HRZ tag = SRP } }
  add_ideas = MSGA_bound_protectorate
  add_opinion_modifier = { target = SER modifier = MSGA_postwar_cooperation }
 }
}
MSGA_integrate_balkan_subjects = {
 every_subject_country = { limit = { OR = { tag = BOS tag = HRZ tag = SRP } }
  remove_ideas = MSGA_bound_protectorate add_ideas = MSGA_integrated_protectorate
 }
}
MSGA_repair_postwar_economy = {
 if = { limit = { check_variable = { var = debt_var value = 0.5 compare = greater_than_or_equals } }
  set_temp_variable = { var = debt_var_temp value = -0.5 } add_debt = yes
 }
 else_if = { limit = { check_variable = { var = debt_var value = 0 compare = greater_than } }
  set_temp_variable = { var = debt_var_temp value = debt_var }
  multiply_temp_variable = { var = debt_var_temp value = -1 } add_debt = yes
 }
 set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
 add_timed_idea = { idea = MSGA_postwar_income_recovery days = 180 }
}
MSGA_consolidate_postwar_industry = {
 set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
 if = { limit = { 107 = { is_owned_by = SER is_fully_controlled_by = SER } }
  107 = { add_extra_state_shared_building_slots = 3 add_building_construction = { type = industrial_complex level = 2 instant_build = yes } add_building_construction = { type = office_park level = 1 instant_build = yes } }
 }
 else = { random_owned_controlled_state = { add_extra_state_shared_building_slots = 3 add_building_construction = { type = industrial_complex level = 2 instant_build = yes } add_building_construction = { type = office_park level = 1 instant_build = yes } } }
}
MSGA_check_regional_power = {
 if = { limit = { tag = SER has_country_flag = MSGA_post_bosnia_started has_country_flag = MSGA_completed_serbian_defence_network has_country_flag = MSGA_completed_serbian_sphere has_country_flag = MSGA_completed_economic_heart_balkans NOT = { has_country_flag = MSGA_regional_power_achieved } }
  set_country_flag = MSGA_regional_power_achieved
  add_stability = 0.05 add_war_support = 0.05
  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes
  add_ideas = MSGA_regional_power_prestige remove_ideas = MSGA_postwar_income_recovery
  every_state = { limit = { has_dynamic_modifier = { modifier = MSGA_western_reconstruction } } remove_dynamic_modifier = { modifier = MSGA_western_reconstruction } }
  country_event = { id = MSGA_postbosnia.16 }
 }
}
''')
    # Both subject militia decisions create Serbian-command auxiliary formations.
    # Spawning at Belgrade avoids invalid foreign-territory ownership/control scopes.
    auxiliaries=[]
    for tag,stem,event,region in [('BOS','bosnian',5,'Bosnian'),('HRZ','herzegovinian',6,'Herzegovinian')]:
        auxiliaries.append(f'''MSGA_raise_{stem}_militias = {{
 if = {{ limit = {{ tag = SER has_country_flag = MSGA_protectorate_militias_unlocked country_exists = {tag} {tag} = {{ is_subject_of = SER }} SER = {{ controls_province = 11586 }} 107 = {{ is_owned_by = SER }} check_variable = {{ var = income_var value = 0.25 compare = greater_than_or_equals }} NOT = {{ has_country_flag = MSGA_{stem}_militias_raised }} }}
  set_temp_variable = {{ var = income_var_temp value = -0.25 }} add_income = yes
  load_oob = MSGA_{tag}_auxiliary_militias set_country_flag = MSGA_{stem}_militias_raised
  country_event = {{ id = MSGA_postbosnia.{event} }}
 }}
}}
''')
        template=f'{region} Territorial Brigade'
        oob=f'division_template = {{ name = "{template}" regiments = {{ militia = {{ x = 0 y = 0 }} militia = {{ x = 0 y = 1 }} militia = {{ x = 0 y = 2 }} }} }}\nunits = {{\n'
        for index in [1,2]:oob+=f' division = {{ name = "{index}. {region} Territorial Brigade" location = 11586 division_template = "{template}" start_equipment_factor = 1 start_manpower_factor = 1 start_experience_factor = 0.1 }}\n'
        put(f'history/units/MSGA_{tag}_auxiliary_militias.txt',oob+'}\n')
    auxiliaries.append('''MSGA_raise_srpska_territorial_defence = {
 if = { limit = { tag = SER has_country_flag = MSGA_srpska_td_unlocked OR = { AND = { country_exists = SRP SRP = { is_subject_of = SER } } has_country_flag = MSGA_srpska_united } SER = { controls_province = 11586 } 107 = { is_owned_by = SER } check_variable = { var = income_var value = 0.5 compare = greater_than_or_equals } NOT = { has_country_flag = MSGA_srpska_td_raised } }
  set_temp_variable = { var = income_var_temp value = -0.5 } add_income = yes
  MSGA_initialize_serbian_vehicles = yes
  load_oob = MSGA_SER_srpska_td_template
  if = { limit = { has_dlc = "No Step Back" } load_oob = MSGA_SER_srpska_td }
  else = { load_oob = MSGA_SER_srpska_td_legacy }
  set_country_flag = MSGA_srpska_td_raised country_event = { id = MSGA_postbosnia.7 }
 }
}
''')
    put('common/scripted_effects/MSGA_post_bosnia_auxiliaries.txt',''.join(auxiliaries))
    for suffix in ['_template','','_legacy']:
        original=read('history/units/MSGA_SER_kosovo_brigade'+suffix+'.txt')
        put('history/units/MSGA_SER_srpska_td'+suffix+'.txt',original.replace('Kosovska Mehanizovana Brigada','Srpska Teritorijalna Odbrana').replace('location = 14400','location = 11586'))
    put('common/ideas/MSGA_post_bosnia_ideas.txt','''ideas = { country = {
 MSGA_bosnian_war_lessons = { picture = MSGA_prepared_for_war allowed = { tag = SER } removal_cost = -1 modifier = { planning_speed = 0.05 } }
 MSGA_serbian_sphere_spirit = { picture = MSGA_command_structure allowed = { tag = SER } removal_cost = -1 modifier = { political_power_factor = 0.05 stability_factor = 0.03 trade_opinion_factor = 0.10 } }
 MSGA_bound_protectorate = { picture = MSGA_command_structure allowed = { OR = { tag = BOS tag = HRZ tag = SRP } } removal_cost = -1 modifier = { autonomy_gain_global_factor = -0.10 trade_opinion_factor = 0.05 } }
 MSGA_integrated_protectorate = { picture = MSGA_command_structure allowed = { OR = { tag = BOS tag = HRZ tag = SRP } } removal_cost = -1 modifier = { autonomy_gain_global_factor = -0.10 autonomy_gain_trade_factor = -0.10 trade_opinion_factor = 0.10 } }
 MSGA_postwar_income_recovery = { picture = MSGA_serbian_rearmament_program allowed = { tag = SER } removal_cost = -1 modifier = { income_growth_factor = 0.01 } }
 MSGA_economic_heart_spirit = { picture = MSGA_serbian_rearmament_program allowed = { tag = SER } removal_cost = -1 modifier = { consumer_goods_factor = -0.02 industrial_capacity_factory = 0.05 business_value_factor = 0.05 income_growth_factor = 0.02 } }
 MSGA_regional_power_prestige = { picture = MSGA_command_structure allowed = { tag = SER } removal_cost = -1 modifier = { trade_opinion_factor = 0.05 } }
} }
'''.replace('picture = MSGA_command_structure','picture = MSGA_prepared_for_war'))
    put('common/opinion_modifiers/MSGA_post_bosnia_opinion.txt','opinion_modifiers = { MSGA_postwar_cooperation = { value = 25 } }\n')
    put('common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt',read('common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt')+'''\nMSGA_western_reconstruction = {
 enable = { always = yes }
 state_production_speed_buildings_factor = 0.10
 state_repair_speed_infrastructure_factor = 0.20
 state_repair_speed_industrial_complex_factor = 0.20
 state_repair_speed_arms_factory_factor = 0.20
 state_repair_speed_office_park_factor = 0.20
}
''')
    put('common/decisions/categories/MSGA_SER_categories.txt',read('common/decisions/categories/MSGA_SER_categories.txt')+'''\nMSGA_post_bosnia_auxiliaries = {
 icon = GFX_decision_category_generic_political_actions
 allowed = { tag = SER }
 visible = { has_country_flag = MSGA_post_bosnia_started }
 priority = 8
}
''')
    decision=['MSGA_post_bosnia_auxiliaries = {']
    for stem,tag,cost,treasury,unlock in [('organise_bosnian_territorial_militias','BOS',25,'0.25','MSGA_protectorate_militias_unlocked'),('organise_herzegovinian_territorial_militias','HRZ',25,'0.25','MSGA_protectorate_militias_unlocked'),('form_srpska_territorial_defence','SRP',0,'0.5','MSGA_srpska_td_unlocked')]:
        region='bosnian' if tag=='BOS' else 'herzegovinian' if tag=='HRZ' else 'srpska_td'
        effect=f'MSGA_raise_{region}_militias' if tag!='SRP' else 'MSGA_raise_srpska_territorial_defence'
        flag=f'MSGA_{region}_militias_raised' if tag!='SRP' else 'MSGA_srpska_td_raised'
        target=f'country_exists = {tag} {tag} = {{ is_subject_of = SER }}' if tag!='SRP' else 'OR = { AND = { country_exists = SRP SRP = { is_subject_of = SER } } has_country_flag = MSGA_srpska_united }'
        decision+= [f' MSGA_{stem} = {{',f'  icon = GFX_MSGA_decision_{stem}','  allowed = { tag = SER }',f'  visible = {{ has_country_flag = {unlock} NOT = {{ has_country_flag = {flag} }} }}',f'  available = {{ {target} 107 = {{ is_owned_by = SER }} SER = {{ controls_province = 11586 }} }}',f'  cost = {cost} custom_cost_text = MSGA_cost_{"quarter" if tag!="SRP" else "half"}_billion',f'  custom_cost_trigger = {{ check_variable = {{ var = income_var value = {treasury} compare = greater_than_or_equals }} }}','  fire_only_once = yes',f'  complete_effect = {{ {effect} = yes }}','  ai_will_do = { factor = 5 }',' }']
    put('common/decisions/MSGA_post_bosnia_decisions.txt','\n'.join(decision+['}'])+'\n')
    events=['add_namespace = MSGA_postbosnia']
    for number,(image,title,description,option) in EVENTS.items():
        events += ['country_event = {',f' id = MSGA_postbosnia.{number}',f' title = MSGA_postbosnia.{number}.t desc = MSGA_postbosnia.{number}.d',f' picture = GFX_MSGA_event_{image}',' is_triggered_only = yes',' fire_only_once = yes',f' option = {{ name = MSGA_postbosnia.{number}.a ai_chance = {{ factor = 100 }} }}','}']
    events+= ['''country_event = {
 id = MSGA_postbosnia.12
 title = MSGA_postbosnia.12.t desc = MSGA_postbosnia.12.d
 picture = GFX_MSGA_event_question_of_republika_srpska
 is_triggered_only = yes fire_only_once = yes
 trigger = { tag = SER has_country_flag = { flag = MSGA_bosnia_settlement_done days > 99 } NOT = { has_country_flag = MSGA_srpska_question_resolved } }
 immediate = { set_country_flag = MSGA_srpska_question_delivered }
 option = { name = MSGA_postbosnia.12.a trigger = { country_exists = SRP SRP = { is_subject_of = SER has_war = no } NOT = { has_country_flag = MSGA_srpska_question_resolved } } ai_chance = { factor = 70 } MSGA_unite_srpska = yes }
 option = { name = MSGA_postbosnia.12.b ai_chance = { factor = 30 } set_country_flag = MSGA_srpska_question_resolved }
}''']
    put('events/MSGA_post_bosnia_events.txt','\n'.join(events)+'\n')
    # Old scheduled 70-day prompts become harmless dispatchers; weekly recovery
    # uses the dated settlement flag and only opens the new question at day 100.
    old=read('events/MSGA_bosnia_events.txt');start=old.index('country_event = {\n id = MSGA_bosnia.11')
    put('events/MSGA_bosnia_events.txt',old[:start]+'''country_event = {
 id = MSGA_bosnia.11 hidden = yes is_triggered_only = yes fire_only_once = yes
 immediate = { MSGA_check_srpska_question = yes }
}
''')
    effects=read('common/scripted_effects/MSGA_bosnia_effects.txt').replace('country_event = { id = MSGA_bosnia.11 days = 70 }','country_event = { id = MSGA_postbosnia.12 days = 100 }')
    effects=effects.replace('  set_country_flag = MSGA_srpska_question_scheduled','  set_country_flag = MSGA_srpska_question_scheduled\n  MSGA_open_post_bosnia = yes')
    effects=effects.replace('  annex_country = { target = SRP transfer_troops = yes }','  # Auxiliaries already serve under SER. Native SRP units/equipment transfer too.\n  SRP = { remove_ideas = MSGA_bound_protectorate remove_ideas = MSGA_integrated_protectorate remove_ideas = MSGA_SRP_last_stand remove_ideas = MSGA_campaign_isolation }\n  annex_country = { target = SRP transfer_troops = yes }')
    effects=effects.replace('  set_country_flag = MSGA_srpska_question_resolved set_country_flag = MSGA_srpska_united','  set_country_flag = MSGA_srpska_question_resolved set_country_flag = MSGA_srpska_united\n  country_event = { id = MSGA_postbosnia.13 }')
    put('common/scripted_effects/MSGA_bosnia_effects.txt',effects)
    put('common/on_actions/MSGA_post_bosnia_on_actions.txt','''on_actions = {
 on_startup = { effect = { SER = { MSGA_open_post_bosnia = yes MSGA_check_srpska_question = yes MSGA_check_regional_power = yes } } }
 on_weekly = { effect = { if = { limit = { tag = SER has_country_flag = MSGA_bosnia_settlement_done } MSGA_open_post_bosnia = yes MSGA_check_srpska_question = yes MSGA_check_regional_power = yes } } }
}
''')
    locale=['l_english:']
    descriptions={
     'victory_in_bosnia':'Consolidate the victory with 5% stability and 25 political power. Temporary local war measures end.',
     'rebuild_the_west':'Add 5% industrial-development progress and capped infrastructure in western Serbia. Eligible western and protectorate states receive 180 days of 10% construction and 20% building repair bonuses.',
     'new_serbian_era':'Gain 25 political power and open the military, political and economic programmes.',
     'lessons_bosnian_war':'Gain 25 army experience, one 25% land-doctrine cost reduction and 180 days of 5% planning speed.',
     'arm_new_serbian_sphere':'Unlock two Bosnian and two Herzegovinian territorial brigades. Each regional decision costs 25 PP and $0.25B treasury. All formations serve directly under Serbian command.',
     'serbian_defence_network':'Unlock the Srpska Territorial Defence: one mobile formation based on the Kosovo brigade, costing $0.5B treasury and no PP. It remains under Serbian command before and after Srpska annexation.',
     'consolidate_victory':'Gain 5% stability and 50 political power. Move the existing balance of power 10% toward the presidency.',
     'bind_new_protectorates':'Improve the remaining BOS, HRZ and SRP subjects’ opinion by 25 and reduce autonomy growth by 10%. Annexed Srpska is safely skipped.',
     'serbian_sphere':'Gain 5% political power, 3% stability and 10% trade opinion. Remaining Balkan protectorates receive 10% lower autonomy and trade-autonomy growth.',
     'repair_war_economy':'Reduce national debt by up to $0.5B without creating negative debt. Add 5% industrial-development progress and a temporary 1% income growth bonus.',
     'serbian_industrial_consolidation':'Build two civilian factories and one office park in Belgrade, with a controlled Serbian state as fallback. Add 5% industrial-development progress.',
     'economic_heart_balkans':'Gain 2% lower consumer goods factor, 5% factory output, 5% business value and 2% monthly income growth. Complete all three branches to become a regional power.'}
    for stem,title,*_ in FOCUSES:locale += [f' MSGA_{stem}:0 "{title}"',f' MSGA_{stem}_desc:0 "{descriptions[stem]}"']
    for number,(_,title,description,option) in EVENTS.items():locale += [f' MSGA_postbosnia.{number}.t:0 "{title}"',f' MSGA_postbosnia.{number}.d:0 "{description}"',f' MSGA_postbosnia.{number}.a:0 "{option}"']
    for key,value in {
     'MSGA_postbosnia.12.t':'The Question of Republika Srpska',
     'MSGA_postbosnia.12.d':'One hundred days after the settlement, Belgrade must choose Srpska’s future. Unification transfers its territory and military forces to Serbia and adds $1B national debt. It grants no new Serbian cores.',
     'MSGA_postbosnia.12.a':'Unite Republika Srpska with Serbia','MSGA_postbosnia.12.b':'Preserve the Current Arrangement',
     'MSGA_post_bosnia_auxiliaries':'Territorial Forces of the Serbian Sphere',
     'MSGA_post_bosnia_auxiliaries_desc':'Organise regional territorial troops under Serbian command. Each formation can be raised once; the Srpska formation remains available after approved unification.',
     'MSGA_organise_bosnian_territorial_militias':'Organise Bosnian Territorial Militias',
     'MSGA_organise_bosnian_territorial_militias_desc':'Spend 25 PP and $0.25B treasury to organise two three-battalion Bosnian militia brigades. They muster in Belgrade under Serbian command. Bosnia must remain a Serbian subject.',
     'MSGA_organise_herzegovinian_territorial_militias':'Organise Herzegovinian Territorial Militias',
     'MSGA_organise_herzegovinian_territorial_militias_desc':'Spend 25 PP and $0.25B treasury to organise two three-battalion Herzegovinian militia brigades. They muster in Belgrade under Serbian command. Herzegovina must remain a Serbian subject.',
     'MSGA_form_srpska_territorial_defence':'Form the Srpska Territorial Defence',
     'MSGA_form_srpska_territorial_defence_desc':'Spend $0.5B treasury and no PP to form Srpska Teritorijalna Odbrana. The formation has the Kosovo brigade’s mobile militia, IFV/APC and tank-support structure. Serbia commands it and keeps it after annexation. Available while Srpska is a Serbian puppet or after its approved unification.',
     'MSGA_cost_quarter_billion':'§Y$0.25B§!','MSGA_cost_half_billion':'§Y$0.5B§!',
     'MSGA_bosnian_lessons_bonus':'Lessons of the Bosnian War','MSGA_bosnian_war_lessons':'Lessons Written in Blood',
     'MSGA_serbian_sphere_spirit':'The Serbian Sphere','MSGA_bound_protectorate':'Bound to Belgrade','MSGA_integrated_protectorate':'The Serbian Sphere',
     'MSGA_postwar_income_recovery':'Postwar Income Recovery','MSGA_economic_heart_spirit':'Economic Heart of the Balkans',
     'MSGA_regional_power_prestige':'A Regional Power','MSGA_western_reconstruction':'Western Reconstruction','MSGA_postwar_cooperation':'Postwar Cooperation'
    }.items():locale.append(f' {key}:0 "{value}"')
    for key in ['MSGA_bosnian_war_lessons','MSGA_serbian_sphere_spirit','MSGA_bound_protectorate','MSGA_integrated_protectorate','MSGA_postwar_income_recovery','MSGA_economic_heart_spirit','MSGA_regional_power_prestige']:locale.append(f' {key}_desc:0 "The postwar programme strengthens cooperation, recovery and regional influence."')
    put('localisation/english/MSGA_post_bosnia_l_english.yml','\n'.join(locale)+'\n')
    old_locale=read('localisation/english/MSGA_settlement_l_english.yml').replace('Seventy days after the settlement','One hundred days after the settlement').replace('MSGA_bosnia.11.b:0 "Not Yet"','MSGA_bosnia.11.b:0 "Preserve the Current Arrangement"')
    put('localisation/english/MSGA_settlement_l_english.yml',old_locale)
    # Ready-made art is copied exactly. Move the one shared sprite registration
    # out of the earlier GFX file so the full supplied new GFX can remain intact.
    gfx=read('interface/MSGA_eventpictures.gfx')
    gfx=re.sub(r'    spriteType = \{\s*name = "GFX_MSGA_event_question_of_republika_srpska"\s*texturefile = "[^"]+"\s*\}\n','',gfx)
    put('interface/MSGA_eventpictures.gfx',gfx)
    asset_records={}
    with zipfile.ZipFile(PACKAGE) as package:
        for name in package.namelist():
            if name.startswith(('gfx/','interface/')) and not name.endswith('/'):
                data=package.read(name)
                if name.endswith('.dds'):
                    image=Image.open(io.BytesIO(data)).convert('RGBA')
                    expected_size=(474,178) if '/event_pictures/' in name else (95,85) if '/goals/' in name else (64,64)
                    assert image.size==expected_size and image.getchannel('A').getextrema()[1]>0
                else:parse(data.decode('utf-8-sig'))
                content[name]=data
                asset_records[name]={'sha256':hashlib.sha256(data).hexdigest(),'package_entry':name}
        # Completion shines reuse the supplied focus texture, with the native
        # animation convention already used by this project; no new art generated.
        # A simple completion sprite is valid and preserves the original DDS.
        shines='spriteTypes = {\n'+''.join(f' SpriteType = {{ name = "GFX_MSGA_focus_{stem}_shine" texturefile = "gfx/interface/goals/MSGA_focus_{stem}.dds" }}\n' for stem,*_ in FOCUSES)+'}\n'
        put('interface/MSGA_post_bosnia_focus_shine.gfx',shines)
    for name in ['descriptor.mod','make_serbia_great_again.mod']:put(name,read(name).replace('version="0.9.0"','version="0.10.0"'))
    backup=ROOT/'logs/post_bosnia_backup';records=[]
    for relative,data in content.items():
        target=LIVE/relative;assert target.resolve().is_relative_to(LIVE)
        before=target.read_bytes() if target.exists() else None
        if before==data:continue
        if before is not None:
            dest=backup/relative;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(before)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        records.append({'relative':relative,'before_sha256':hashlib.sha256(before).hexdigest() if before is not None else None,'after_sha256':hashlib.sha256(data).hexdigest()})
    shutil.copyfile(LIVE/'make_serbia_great_again.mod',LIVE.parent/'make_serbia_great_again.mod')
    report={'version':'0.10.0','runtime_target':str(LIVE),'files':records,'focus_ids':['MSGA_'+v[0] for v in FOCUSES],'focus_days':14,'total_focus_days':168,'Srpska_question_days':100,'actual_game_validation':'pending user test; user explicitly reserved gameplay testing'}
    (ROOT/'docs/post_bosnia_deployment.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'docs/post_bosnia_sources.json').write_text(json.dumps({'package':str(PACKAGE),'package_sha256':hashlib.sha256(PACKAGE.read_bytes()).hexdigest(),'assets':asset_records,'native_tags':{'BOS':'104','HRZ':'851','SRP':'848/849/850'},'auxiliary_control':'Serbian-owned divisions; regional identity preserved; existing SRP army transfers on annexation'},indent=2)+'\n')
    print(f'Installed {len(records)} files into {LIVE}; source not yet synchronized.')

if __name__=='__main__':main()
