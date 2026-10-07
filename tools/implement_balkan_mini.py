"""Install the user-approved BOS/MAC/MNT increment into LIVE first."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageOps
import hashlib, io, json, shutil
from deploy_local import ROOT, SOURCE, TARGET, inventory
from validate_phase1 import parse, get
from implement_balkan_rearmament import TFR, GAME, treasury, equipment, factory

PACK=Path(r'C:\Users\Balazs\Downloads\Balkan_Mini_Rearmament_Individual_Assets.zip')
TAGS={'BOS':104,'MAC':106,'MNT':105}
FOLDERS={'BOS':'Bosnia','MAC':'North_Macedonia','MNT':'Montenegro'}
# stem, days, x, y, parents; the first six are the independent peacetime tree.
ROWS={
'BOS':[
 ('a_fragile_peace',28,3,0,[]),('sarajevo_business_confidence',35,1,1,['a_fragile_peace']),('support_domestic_industry',35,1,2,['sarajevo_business_confidence']),
 ('maintain_the_armed_forces',28,5,1,['a_fragile_peace']),('territorial_defence_planning',28,5,2,['maintain_the_armed_forces']),('hold_the_balance',28,3,3,['support_domestic_industry','territorial_defence_planning']),
 ('emergency_mobilisation',21,13,0,[]),('open_the_old_depots',21,11,1,['emergency_mobilisation']),('emergency_defence_budget',28,15,1,['emergency_mobilisation']),
 ('foreign_arms_purchases',28,11,2,['open_the_old_depots']),('expand_war_industry',35,15,2,['emergency_defence_budget']),('search_for_old_armour',28,11,3,['foreign_arms_purchases']),
 ('defend_central_bosnia',28,13,4,['search_for_old_armour','expand_war_industry']),('defend_the_federation',35,13,5,['defend_central_bosnia'])],
'MAC':[
 ('business_as_usual',28,3,0,[]),('support_skopje_industry',35,1,1,['business_as_usual']),('improve_the_vardar_corridor',35,1,2,['support_skopje_industry']),
 ('maintain_readiness',28,5,1,['business_as_usual']),('secure_army_supplies',28,5,2,['maintain_readiness']),('a_quiet_republic',28,3,3,['improve_the_vardar_corridor','secure_army_supplies']),
 ('balkan_alarm',21,13,0,[]),('search_old_infantry_reserves',28,11,1,['balkan_alarm']),('reopen_the_depots',28,15,1,['balkan_alarm']),
 ('emergency_defence_budget',28,11,2,['search_old_infantry_reserves']),('expand_skopje_workshops',35,15,2,['reopen_the_depots']),
 ('start_mobilising_our_reserve_soldiers',28,13,3,['emergency_defence_budget','expand_skopje_workshops']),('defend_the_vardar',28,13,4,['start_mobilising_our_reserve_soldiers']),('armed_macedonia',35,13,5,['defend_the_vardar'])],
'MNT':[
 ('business_as_usual',28,3,0,[]),('tourism_and_services',35,1,1,['business_as_usual']),('develop_the_port_of_bar',35,1,2,['tourism_and_services']),
 ('maintain_basic_readiness',28,5,1,['business_as_usual']),('stock_the_armouries',28,5,2,['maintain_basic_readiness']),('a_stable_small_state',28,3,3,['develop_the_port_of_bar','stock_the_armouries']),
 ('the_balkans_are_burning',21,13,0,[]),('search_old_infantry_reserves',28,11,1,['the_balkans_are_burning']),('arm_the_reserves',28,15,1,['the_balkans_are_burning']),
 ('emergency_defence_fund',28,11,2,['search_old_infantry_reserves']),('start_mobilising_our_reserve_soldiers',28,15,2,['arm_the_reserves']),
 ('secure_the_mountain_passes',28,11,3,['emergency_defence_fund']),('prepare_territorial_defence',35,15,3,['start_mobilising_our_reserve_soldiers']),('montenegro_prepared',35,13,4,['secure_the_mountain_passes','prepare_territorial_defence'])]}
CONTRACTS=[
 ('BOS','purchase_regional_surplus_arms',.6,14,'foreign_arms_purchases',[('infantry_equipment_1',1000,'SOV'),('support_equipment_1',40,'BOS')],'generic_military'),
 ('BOS','acquire_emergency_artillery_stocks',.8,18,'foreign_arms_purchases',[('artillery_equipment_1',60,'SOV'),('support_equipment_1',30,'BOS')],'generic_military_support'),
 ('BOS','purchase_used_military_vehicles',.75,18,'foreign_arms_purchases',[('motorized_equipment_1',100,'SOV')],'generic_trucks'),
 ('BOS','foreign_anti_tank_assistance',1.,21,'foreign_arms_purchases',[('anti_tank_equipment_1',80,'SOV')],'generic_military_support'),
 ('BOS','purchase_yugoslav_t55_reserves',1.4,30,'search_for_old_armour',[('modern_tank_equipment_1',100,'SER')],'MSGA_mini_BOS_t55_contract'),
 ('MAC','purchase_yugoslav_reserve_rifles',.3,10,'balkan_alarm',[('infantry_equipment_1',700,'SOV')],'generic_military'),
 ('MAC','acquire_balkan_artillery_stocks',.45,14,'balkan_alarm',[('artillery_equipment_1',35,'SOV'),('support_equipment_1',25,'MAC')],'generic_military_support'),
 ('MAC','buy_used_army_trucks',.4,14,'balkan_alarm',[('motorized_equipment_1',70,'SOV')],'generic_trucks'),
 ('MAC','emergency_anti_tank_purchase',.65,21,'balkan_alarm',[('anti_tank_equipment_1',45,'SOV')],'generic_military_support'),
 ('MNT','search_former_yugoslav_stockpiles',.25,10,'the_balkans_are_burning',[('infantry_equipment_1',500,'SOV')],'generic_military'),
 ('MNT','purchase_surplus_heavy_weapons',.4,14,'the_balkans_are_burning',[('artillery_equipment_1',25,'SOV'),('support_equipment_1',25,'MNT')],'generic_military_support'),
 ('MNT','acquire_used_military_vehicles',.45,14,'the_balkans_are_burning',[('motorized_equipment_1',50,'SOV'),('support_equipment_1',20,'MNT')],'generic_trucks'),
 ('MNT','emergency_anti_tank_shipment',.6,21,'the_balkans_are_burning',[('anti_tank_equipment_1',40,'SOV')],'generic_military_support')]
# title, supplied main-spirit image, native modifiers, duration (0 = permanent)
IDEAS={
'BOS_peace_assistance':('Peacetime Assistance','BOS_fragile_federation_spirit',{'income_growth_factor':.01},180),
'BOS_business_confidence':('Sarajevo Business Confidence','BOS_fragile_federation_spirit',{'business_value_factor':.05,'income_growth_factor':.01},0),
'BOS_domestic_industry':('Domestic Industry','BOS_fragile_federation_spirit',{'industrial_capacity_factory':.03},0),
'BOS_territorial_planning':('Territorial Defence Planning','BOS_bosnia_mobilised_spirit',{'army_defence_factor':.05,'training_time_army_factor':-.1},0),
'BOS_fragile_federation':('Fragile Federation','BOS_fragile_federation_spirit',{'stability_factor':.03,'army_defence_factor':.03,'land_reinforce_rate':.05},0),
'BOS_emergency_mobilisation':('Emergency Mobilisation','BOS_bosnia_mobilised_spirit',{'mobilization_speed':.1},0),
'BOS_emergency_construction':('Emergency Defence Construction','BOS_bosnia_mobilised_spirit',{'production_speed_arms_factory_factor':.05},180),
'BOS_war_industry':('War Industry','BOS_bosnia_mobilised_spirit',{'industrial_capacity_factory':.05},180),
'BOS_bosnia_mobilised':('Bosnia Mobilised','BOS_bosnia_mobilised_spirit',{'army_defence_factor':.075,'army_org_factor':.05,'land_reinforce_rate':.1,'training_time_army_factor':-.1},0),
'MAC_peace_assistance':('Peacetime Assistance','MAC_quiet_republic_spirit',{'income_growth_factor':.01},180),
'MAC_skopje_industry':('Skopje Industry','MAC_quiet_republic_spirit',{'business_value_factor':.05,'industrial_capacity_factory':.02},0),
'MAC_vardar_development':('Vardar Development','MAC_quiet_republic_spirit',{'income_growth_factor':.005},180),
'MAC_quiet_republic':('A Quiet Republic','MAC_quiet_republic_spirit',{'stability_factor':.03,'training_time_army_factor':-.05},0),
'MAC_emergency_construction':('Emergency Defence Construction','MAC_armed_macedonia_spirit',{'production_speed_arms_factory_factor':.05},180),
'MAC_skopje_workshops':('Skopje Workshops','MAC_armed_macedonia_spirit',{'industrial_capacity_factory':.05,'production_factory_max_efficiency_factor':.05},0),
'MAC_reserve_mobilisation':('Reserve Mobilisation','MAC_armed_macedonia_spirit',{'conscription_factor':.03,'mobilization_speed':.1},0),
'MAC_armed_macedonia':('Armed Macedonia','MAC_armed_macedonia_spirit',{'army_defence_factor':.05,'army_org_factor':.05,'land_reinforce_rate':.05},0),
'MNT_peace_assistance':('Peacetime Assistance','MNT_stable_small_state_spirit',{'income_growth_factor':.01},180),
'MNT_tourism_services':('Tourism and Services','MNT_stable_small_state_spirit',{'business_value_factor':.05,'income_growth_factor':.02},0),
'MNT_stable_small_state':('Stable Small State','MNT_stable_small_state_spirit',{'stability_factor':.05,'industrial_capacity_factory':.02},0),
'MNT_reserve_mobilisation':('Reserve Mobilisation','MNT_montenegro_prepared_spirit',{'conscription_factor':.02,'mobilization_speed':.1},0),
'MNT_territorial_training':('Territorial Defence Training','MNT_montenegro_prepared_spirit',{'training_time_army_factor':-.1},0),
'MNT_montenegro_prepared':('Montenegro Prepared','MNT_montenegro_prepared_spirit',{'army_defence_factor':.075,'army_org_factor':.05,'land_reinforce_rate':.05},0)}
FORTS={'BOS':[(11899,2),(6799,1)],'MAC':[(3882,1),(907,1)],'MNT':[(11858,1),(6913,1)]}
ARMOUR='Bosnian Armoured Brigade'
MNT_TEMPLATE='MSGA MNT Territorial Militia'
ARMOUR_DEF='division_template = { name = "Bosnian Armoured Brigade" regiments = { modern_armor = { x = 0 y = 0 } motorized = { x = 1 y = 0 } motorized = { x = 1 y = 1 } motorized = { x = 1 y = 2 } } support = { engineer = { x = 0 y = 0 } artillery = { x = 0 y = 1 } } }'
MNT_DEF='division_template = { name = "MSGA MNT Territorial Militia" regiments = { militia = { x = 0 y = 0 } militia = { x = 0 y = 1 } militia = { x = 0 y = 2 } } }'
def ident(tag,stem):return 'MSGA_'+tag+'_'+stem
def sha(data):return hashlib.sha256(data).hexdigest()
def title(stem):return stem.replace('_',' ').title().replace('T55','T-55').replace('Our Reserve','Our Reserve')
def main():
 baseline=inventory(TARGET);assert baseline==inventory(SOURCE) and len(baseline)==602
 assert 'version="0.16.0"' in (TARGET/'descriptor.mod').read_text()
 files={};loc={};effects=[];sprites=[];assets={};focus_records=[]
 def put(path,text):
  text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
  if path.endswith(('.txt','.gfx')):parse(text)
  files[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
 def idea(stem):
  days=IDEAS[stem][3]
  return f'add_timed_idea = {{ idea = MSGA_{stem} days = {days} }}' if days else 'add_ideas = MSGA_'+stem
 def fortify(tag):
  return str(TAGS[tag])+' = { if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } '+' '.join(f'if = {{ limit = {{ free_building_slots = {{ building = bunker province = {p} size > {n-1} }} }} add_building_construction = {{ type = bunker level = {n} province = {p} instant_build = yes }} }}' for p,n in FORTS[tag])+' }'
 # Direct native building additions are bounded and guarded by state ownership/control.
 rewards={
 'BOS_a_fragile_peace':'add_political_power = 30 add_stability = .03 '+idea('BOS_peace_assistance'),
 'BOS_sarajevo_business_confidence':'104 = { add_extra_state_shared_building_slots = 1 } '+idea('BOS_business_confidence'),
 'BOS_support_domestic_industry':'104 = { add_extra_state_shared_building_slots = 1 } '+idea('BOS_domestic_industry'),
 'BOS_maintain_the_armed_forces':'army_experience = 5 add_war_support = .025 '+equipment([('support_equipment_1',25,'BOS')]),
 'BOS_territorial_defence_planning':idea('BOS_territorial_planning'), 'BOS_hold_the_balance':idea('BOS_fragile_federation'),
 'BOS_emergency_mobilisation':'add_war_support = .1 army_experience = 5 '+idea('BOS_emergency_mobilisation'),
 'BOS_open_the_old_depots':equipment([('infantry_equipment_1',1200,'SOV'),('artillery_equipment_1',60,'SOV'),('support_equipment_1',75,'BOS')]),
 'BOS_emergency_defence_budget':factory(104,'BOS',2)+' '+idea('BOS_emergency_construction'),
 'BOS_foreign_arms_purchases':'', 'BOS_expand_war_industry':factory(104,'BOS')+' '+idea('BOS_war_industry'),
 'BOS_search_for_old_armour':'army_experience = 5', 'BOS_defend_central_bosnia':fortify('BOS'),
 'BOS_defend_the_federation':'remove_ideas = MSGA_BOS_territorial_planning '+idea('BOS_bosnia_mobilised'),
 'MAC_business_as_usual':'add_political_power = 30 add_stability = .03 '+idea('MAC_peace_assistance'),
 'MAC_support_skopje_industry':'106 = { add_extra_state_shared_building_slots = 1 } '+idea('MAC_skopje_industry'),
 'MAC_improve_the_vardar_corridor':'106 = { if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } } '+idea('MAC_vardar_development'),
 'MAC_maintain_readiness':'army_experience = 5 add_war_support = .025',
 'MAC_secure_army_supplies':equipment([('infantry_equipment_1',500,'SOV'),('support_equipment_1',25,'MAC')]),'MAC_a_quiet_republic':idea('MAC_quiet_republic'),
 'MAC_balkan_alarm':'add_war_support = .075',
 'MAC_search_old_infantry_reserves':equipment([('infantry_equipment_1',900,'SOV'),('artillery_equipment_1',35,'SOV'),('support_equipment_1',40,'MAC')]),
 'MAC_reopen_the_depots':equipment([('infantry_equipment_1',350,'SOV'),('motorized_equipment_1',80,'SOV')]),
 'MAC_emergency_defence_budget':factory(106,'MAC',1)+' '+idea('MAC_emergency_construction'), 'MAC_expand_skopje_workshops':idea('MAC_skopje_workshops'),
 'MAC_start_mobilising_our_reserve_soldiers':idea('MAC_reserve_mobilisation'), 'MAC_defend_the_vardar':fortify('MAC'), 'MAC_armed_macedonia':idea('MAC_armed_macedonia'),
 'MNT_business_as_usual':'add_political_power = 30 add_stability = .03 '+idea('MNT_peace_assistance'), 'MNT_tourism_and_services':idea('MNT_tourism_services'),
 'MNT_develop_the_port_of_bar':'105 = { add_extra_state_shared_building_slots = 1 if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } }',
 'MNT_maintain_basic_readiness':'army_experience = 5 add_war_support = .025',
 'MNT_stock_the_armouries':equipment([('infantry_equipment_1',450,'SOV'),('support_equipment_1',25,'MNT')]),'MNT_a_stable_small_state':idea('MNT_stable_small_state'),
 'MNT_the_balkans_are_burning':'add_war_support = .1',
 'MNT_search_old_infantry_reserves':equipment([('infantry_equipment_1',650,'SOV'),('artillery_equipment_1',30,'SOV'),('support_equipment_1',30,'MNT')]),
 'MNT_arm_the_reserves':equipment([('infantry_equipment_1',300,'SOV'),('motorized_equipment_1',60,'SOV')]),'MNT_emergency_defence_fund':factory(105,'MNT',1),
 'MNT_start_mobilising_our_reserve_soldiers':idea('MNT_reserve_mobilisation'),'MNT_secure_the_mountain_passes':fortify('MNT'),
 'MNT_prepare_territorial_defence':f'if = {{ limit = {{ NOT = {{ has_template = "{MNT_TEMPLATE}" }} }} {MNT_DEF} }} '+idea('MNT_territorial_training'), 'MNT_montenegro_prepared':idea('MNT_montenegro_prepared')}
 rewards_text={
 'BOS_a_fragile_peace':'+30 Political Power, +3% Stability; +1% Income Growth for 180 days.',
 'BOS_sarajevo_business_confidence':'+1 shared building slot in Central Bosnia, +5% Business Value and +1% Income Growth.',
 'BOS_support_domestic_industry':'+1 shared building slot in Central Bosnia and +3% Factory Output.',
 'BOS_maintain_the_armed_forces':'+5 Army Experience, +2.5% War Support and 25 Support Equipment.',
 'BOS_territorial_defence_planning':'+5% Division Defence and 10% shorter army training time. Supports the existing territorial brigades; creates no new units.',
 'BOS_hold_the_balance':'Fragile Federation: +3% Stability, +3% Division Defence and +5 percentage points Reinforce Rate.',
 'BOS_emergency_mobilisation':'+10% War Support, +10% Mobilisation Speed and +5 Army Experience.',
 'BOS_open_the_old_depots':'Receive 1,200 older rifles, 60 older Artillery and 75 Support Equipment.',
 'BOS_emergency_defence_budget':'+1 Military Factory and +2 shared building slots in Central Bosnia; +5% Military Factory Construction Speed for 180 days.',
 'BOS_foreign_arms_purchases':'Open four one-time foreign equipment contracts.',
 'BOS_expand_war_industry':'+1 Military Factory in Central Bosnia and +5% Factory Output for 180 days.',
 'BOS_search_for_old_armour':'+5 Army Experience. Open the one-time purchase of 100 existing Serbian T-55A tanks and the Bosnian Armoured Brigade template.',
 'BOS_defend_central_bosnia':'+1 Infrastructure up to its native maximum. +2 fort levels at Sarajevo and +1 on its northern approach.',
 'BOS_defend_the_federation':'Replace Territorial Defence Planning with Bosnia Mobilised: +7.5% Defence, +5% Organisation, +10 percentage points Reinforce Rate; retain 10% shorter training time.',
 'MAC_business_as_usual':'+30 Political Power, +3% Stability; +1% Income Growth for 180 days.',
 'MAC_support_skopje_industry':'+1 shared building slot, +5% Business Value and +2% Factory Output.',
 'MAC_improve_the_vardar_corridor':'+1 Infrastructure up to its native maximum; +0.5% Income Growth for 180 days.',
 'MAC_maintain_readiness':'+5 Army Experience and +2.5% War Support.',
 'MAC_secure_army_supplies':'Receive 500 older rifles and 25 Support Equipment.',
 'MAC_a_quiet_republic':'A Quiet Republic: +3% Stability and 5% shorter army training time.',
 'MAC_balkan_alarm':'+7.5% War Support. Open four small, one-time procurement contracts.',
 'MAC_search_old_infantry_reserves':'Receive 900 older rifles, 35 older Artillery and 40 Support Equipment.',
 'MAC_reopen_the_depots':'Receive 350 older rifles and 80 used military trucks.',
 'MAC_emergency_defence_budget':'+1 Military Factory and +1 shared building slot; +5% Military Factory Construction Speed for 180 days.',
 'MAC_expand_skopje_workshops':'+5% Factory Output and +5% Production Efficiency Cap.',
 'MAC_start_mobilising_our_reserve_soldiers':'+3% Recruitable Population Factor and +10% Mobilisation Speed. Mobilises national manpower; creates no divisions.',
 'MAC_defend_the_vardar':'+1 Infrastructure up to its native maximum. Add one fort level on each of two northern approaches.',
 'MAC_armed_macedonia':'Armed Macedonia: +5% Defence, +5% Organisation and +5 percentage points Reinforce Rate.',
 'MNT_business_as_usual':'+30 Political Power, +3% Stability; +1% Income Growth for 180 days.',
 'MNT_tourism_and_services':'+5% Business Value and +2% Income Growth.',
 'MNT_develop_the_port_of_bar':'+1 Infrastructure up to its native maximum and +1 shared building slot.',
 'MNT_maintain_basic_readiness':'+5 Army Experience and +2.5% War Support.',
 'MNT_stock_the_armouries':'Receive 450 older rifles and 25 Support Equipment.',
 'MNT_a_stable_small_state':'Stable Small State: +5% Stability and +2% Factory Output.',
 'MNT_the_balkans_are_burning':'+10% War Support. Open four small, one-time surplus equipment contracts.',
 'MNT_search_old_infantry_reserves':'Receive 650 older rifles, 30 older Artillery and 30 Support Equipment.',
 'MNT_arm_the_reserves':'Receive 300 older rifles and 60 used military trucks.',
 'MNT_emergency_defence_fund':'+1 Military Factory and +1 shared building slot.',
 'MNT_start_mobilising_our_reserve_soldiers':'+2% Recruitable Population Factor and +10% Mobilisation Speed. Mobilises national manpower; creates no divisions.',
 'MNT_secure_the_mountain_passes':'+1 Infrastructure up to its native maximum and one fort level at each of two northern mountain approaches.',
 'MNT_prepare_territorial_defence':'Unlock the existing three-battalion Territorial Militia template for normal recruitment; 10% shorter training time. Creates no free divisions.',
 'MNT_montenegro_prepared':'Montenegro Prepared: +7.5% Defence, +5% Organisation and +5 percentage points Reinforce Rate.'}
 # The only new trigger is the actual persistent campaign state, never Srpska's uprising.
 put('common/scripted_triggers/MSGA_balkan_mini_triggers.txt','MSGA_mini_kosovo_started = { SER = { has_country_flag = MSGA_kosovo_war_started } }\nMSGA_mini_rearmament_unlocked = { OR = { has_country_flag = MSGA_mini_rearmament_unlocked MSGA_mini_kosovo_started = yes } }')
 effects.append('MSGA_mini_unlock_rearmament = { if = { limit = { OR = { tag = BOS tag = MAC tag = MNT } MSGA_mini_kosovo_started = yes NOT = { has_country_flag = MSGA_mini_rearmament_unlocked } } set_country_flag = MSGA_mini_rearmament_unlocked } }')
 effects.append('MSGA_mini_unlock_all = { '+' '.join(tag+' = { if = { limit = { exists = yes } MSGA_mini_unlock_rearmament = yes } }' for tag in TAGS)+' }')
 starts=' '.join(tag+' = { if = { limit = { exists = yes } MSGA_mini_unlock_rearmament = yes if = { limit = { has_focus_tree = generic_focus } load_focus_tree = { tree = MSGA_'+tag+'_mini keep_completed = yes } } } }' for tag in TAGS)
 put('common/on_actions/MSGA_balkan_mini_on_actions.txt','on_actions = { on_startup = { effect = { '+starts+' } } on_declare_war = { effect = { if = { limit = { ROOT = { tag = SER has_country_flag = MSGA_kosovo_war_started } FROM = { tag = KOS } } MSGA_mini_unlock_all = yes } } } on_weekly = { effect = { MSGA_mini_unlock_rearmament = yes } } }')
 # BOS history only: preserve the native OOB; reuse auxiliary definitions, relocating Serbia's recruitment site to Sarajevo.
 native_oob=(TFR/'history/units/BOS_2020.txt').read_text(encoding='utf-8-sig')
 auxiliary=(TARGET/'history/units/MSGA_BOS_auxiliary_militias.txt').read_text()
 put('history/units/BOS_2020.txt',native_oob+'\n# Existing territorial forces at game start, not a reload event.\n'+auxiliary.replace('location = 11586','location = 11899'))
 loc['MSGA_BOS_territorial_brigade']='Bosnian Territorial Brigade';loc['MSGA_BOS_armoured_brigade']=ARMOUR;loc['MSGA_MNT_territorial_militia']='Montenegrin Territorial Militia'
 physical={stem for stem,body in rewards.items() if 'add_building_construction' in body or 'add_extra_state_shared_building_slots' in body}
 factories={'BOS_emergency_defence_budget','BOS_expand_war_industry','MAC_emergency_defence_budget','MNT_emergency_defence_fund'}
 for tag,rows in ROWS.items():
  focuses=[]
  for i,(stem,days,x,y,parents) in enumerate(rows):
   id=ident(tag,stem);key=tag+'_'+stem;condition=f'tag = {tag} has_capitulated = no'
   if i>=6:condition+=' MSGA_mini_rearmament_unlocked = yes'
   if key in physical:
    condition+=f' {TAGS[tag]} = {{ is_owned_by = {tag} is_fully_controlled_by = {tag} is_core_of = {tag}'
    if key in factories:condition+=' arms_factory < 20'
    if key=='BOS_expand_war_industry':condition+=' free_building_slots = { building = arms_factory size > 0 include_locked = yes }'
    condition+=' }'
   unlocks=[title(c[1]) for c in CONTRACTS if c[0]==tag and c[4]==stem]
   tt=id+'_reward_tt';loc[tt]=rewards_text[key]
   parentconds=' '.join('has_completed_focus = '+ident(tag,p) for p in parents)
   effects.append(f'{id}_reward = {{ if = {{ limit = {{ {condition} {parentconds} NOT = {{ has_country_flag = {id}_done }} }} set_country_flag = {id}_done {rewards[key]} }} }}')
   ai=f'factor = {1000-i*35 if i>=6 else 60-i*3}'
   if i<6:ai+=' modifier = { factor = .01 MSGA_mini_rearmament_unlocked = yes }'
   focuses.append(f'focus = {{ id = {id} icon = GFX_MSGA_mini_focus_{tag}_{stem} x = {x} y = {y} cost = {days/7:g} '+' '.join('prerequisite = { focus = '+ident(tag,p)+' }' for p in parents)+f' available = {{ {condition} }} cancel_if_invalid = yes continue_if_invalid = no ai_will_do = {{ {ai} }} completion_reward = {{ custom_effect_tooltip = {tt} hidden_effect = {{ {id}_reward = yes }} }} }}')
   loc[id]=title(stem);loc[id+'_desc']=('Preserve a modest, peaceful economy and maintain existing national forces. ' if i<6 else 'The actual Serbian war in Kosovo has made regional escalation a credible threat. Prepare a limited defensive force without provoking the later Bosnian conflict. ')+rewards_text[key]
   focus_records.append({'id':id,'tag':tag,'days':days,'parents':[ident(tag,p) for p in parents],'phase':'peace' if i<6 else 'Kosovo-triggered','native_direct_reward':rewards[key],'contracts_unlocked':unlocks})
  put(f'common/national_focus/MSGA_{tag}_mini.txt',f'focus_tree = {{ id = MSGA_{tag}_mini country = {{ factor = 0 modifier = {{ add = 100 tag = {tag} }} }} default = no reset_on_civilwar = no\n'+'\n'.join(focuses)+'\n}')
 # All shipments share one national reservation and use persistent completion state.
 decision_blocks=[];cats=[]
 for tag in TAGS:
  cat=ident(tag,'mini_procurement');cats.append(cat+' = { icon = '+('MSGA_mini_BOS_kosovo_alarm' if tag=='BOS' else 'military_operation')+' allowed = { original_tag = '+tag+' } visible = { tag = '+tag+' MSGA_mini_rearmament_unlocked = yes } }')
  loc[cat]={'BOS':'Bosnian','MAC':'Macedonian','MNT':'Montenegrin'}[tag]+' Defensive Procurement';loc[cat+'_desc']='One-time Treasury contracts for a small defensive force. One shipment at a time; cancellations refund the reserved Treasury.'
  decisions=[]
  for ctag,stem,cost,days,focus,items,icon in CONTRACTS:
   if ctag!=tag:continue
   id=ident(tag,stem);pending=id+'_pending';done=id+'_completed';busy=ident(tag,'mini_procurement_busy');tank=stem=='purchase_yugoslav_t55_reserves'
   safe=f'tag = {tag} has_capitulated = no'+(' country_exists = SER SER = { has_country_flag = MSGA_serbian_vehicles_initialized }' if tank else '')
   ready=f'{safe} MSGA_mini_rearmament_unlocked = yes has_completed_focus = {ident(tag,focus)} NOT = {{ has_country_flag = {busy} }} NOT = {{ has_country_flag = {done} }} check_variable = {{ var = income_var value = {cost:g} compare = greater_than_or_equals }}'
   delivery=equipment(items)
   if tank:
    delivery='if = { limit = { has_dlc = "No Step Back" } add_equipment_to_stockpile = { type = modern_tank_chassis_1 amount = 100 producer = SER variant_name = "T-55A" } } else = { add_equipment_to_stockpile = { type = modern_tank_equipment_1 amount = 100 producer = SER variant_name = "T-55A" } } '+f'if = {{ limit = {{ NOT = {{ has_template = "{ARMOUR}" }} }} {ARMOUR_DEF} }} set_division_template_cap = {{ division_template = "{ARMOUR}" division_cap = 1 }} set_country_flag = MSGA_BOS_armoured_brigade_unlocked'
   effects.extend([f'{id}_start = {{ if = {{ limit = {{ {ready} NOT = {{ has_country_flag = {pending} }} }} {treasury(-cost)} set_country_flag = {pending} set_country_flag = {busy} }} }}',
    f'{id}_cancel = {{ if = {{ limit = {{ has_country_flag = {pending} }} {treasury(cost)} clr_country_flag = {pending} clr_country_flag = {busy} }} }}',
    f'{id}_finish = {{ if = {{ limit = {{ has_country_flag = {pending} NOT = {{ has_country_flag = {done} }} {safe} }} {delivery} set_country_flag = {done} clr_country_flag = {pending} clr_country_flag = {busy} }} else = {{ {id}_cancel = yes }} }}'])
   received='100 existing Serbian T-55A tanks; unlock the Bosnian Armoured Brigade template (one formation maximum)' if tank else ', '.join(str(n)+' '+{'infantry_equipment_1':'older rifles','support_equipment_1':'Support Equipment','artillery_equipment_1':'older Artillery','motorized_equipment_1':'used military trucks','anti_tank_equipment_1':'older anti-tank weapons'}[typ] for typ,n,prod in items)
   loc[id]=title(stem);loc[id+'_desc']=f'Treasury: ${cost:g}B. Delivery: {days} days. ONE-TIME ONLY. Receive {received}. Cancelled deliveries refund the reservation.'
   loc[id+'_available_tt']=f'Requires {title(focus)}, ${cost:g}B Treasury, no pending shipment and a country that has not capitulated.'+(' Serbia must exist with its original T-55A design initialized.' if tank else '')
   loc[id+'_start_tt']=f'Reserve ${cost:g}B Treasury for a {days}-day shipment. One-time only; cancellation refunds the cost.';loc[id+'_finish_tt']='Receive '+received+'. Permanently completes this contract.'
   ai=f'factor = {35 if "rifles" in stem or "surplus_arms" in stem or "stockpiles" in stem else 22 if "artillery" in stem or "heavy_weapons" in stem else 12 if "vehicles" in stem or "trucks" in stem else 6} modifier = {{ factor = 0 NOT = {{ check_variable = {{ var = income_var value = {cost+.25:g} compare = greater_than_or_equals }} }} }}'
   if tank:ai+=' modifier = { factor = 5 NOT = { has_equipment = { modern_tank_chassis > 149 } } check_variable = { var = income_var value = 2 compare = greater_than_or_equals } }'
   cancel='OR = { has_capitulated = yes'+(' NOT = { country_exists = SER }' if tank else '')+' }'
   decisions.append(f'{id} = {{ icon = {icon} cost = 0 days_remove = {days} visible = {{ tag = {tag} MSGA_mini_rearmament_unlocked = yes has_completed_focus = {ident(tag,focus)} NOT = {{ has_country_flag = {done} }} }} available = {{ custom_trigger_tooltip = {{ tooltip = {id}_available_tt {ready} }} }} complete_effect = {{ custom_effect_tooltip = {id}_start_tt hidden_effect = {{ {id}_start = yes }} }} remove_effect = {{ custom_effect_tooltip = {id}_finish_tt hidden_effect = {{ {id}_finish = yes }} }} cancel_trigger = {{ hidden_trigger = {{ {cancel} }} }} cancel_effect = {{ hidden_effect = {{ {id}_cancel = yes }} }} ai_will_do = {{ {ai} }} }}')
  decision_blocks.append(cat+' = {\n'+'\n'.join(decisions)+'\n}')
 put('common/decisions/MSGA_balkan_mini_procurement.txt','\n'.join(decision_blocks));put('common/decisions/categories/MSGA_balkan_mini_categories.txt','\n'.join(cats))
 put('common/scripted_effects/MSGA_balkan_mini_effects.txt','\n'.join(effects))
 idea_blocks=[]
 for stem,(name,art,mods,days) in IDEAS.items():
  id='MSGA_'+stem;loc[id]=name;loc[id+'_desc']='A modest national programme supporting '+name.lower()+'.'
  idea_blocks.append(id+' = { picture = MSGA_mini_idea_'+art+' allowed = { original_tag = '+stem[:3]+' } removal_cost = -1 modifier = { '+' '.join(k+' = '+str(v) for k,v in mods.items())+' } }')
 put('common/ideas/MSGA_balkan_mini_ideas.txt','ideas = { country = {\n'+'\n'.join(idea_blocks)+'\n} }')
 # Native battalion requirements: 50 tanks; 3 motorized need 120 trucks/750 rifles/60 support.
 # Engineers add 25 rifles/50 support/200 men; support artillery adds 12 guns/300 men.
 training='has_country_flag = MSGA_BOS_armoured_brigade_unlocked has_template = "Bosnian Armoured Brigade" has_manpower > 4549 '+ ' '.join('has_equipment = { '+kind+' > '+str(n-1)+' }' for kind,n in [('modern_tank_chassis',50),('motorized_equipment',120),('infantry_equipment',775),('support_equipment',110),('artillery_equipment',12)])
 put('common/scripted_triggers/MSGA_balkan_mini_training.txt','MSGA_BOS_can_train_armoured_brigade = { '+training+' }\nMSGA_MNT_can_train_territorial = { has_completed_focus = MSGA_MNT_prepare_territorial_defence has_template = "MSGA MNT Territorial Militia" has_manpower > 2999 has_equipment = { infantry_equipment > 599 } has_equipment = { support_equipment > 14 } }')
 ai=[]
 for tag,name,role,reg,sup,guard in [('BOS','armoured_brigade','armor','modern_armor = 1 motorized = 3','engineer = 1 artillery = 1','MSGA_BOS_can_train_armoured_brigade'),('MNT','territorial_training','infantry','militia = 3','','MSGA_MNT_can_train_territorial')]:
  ai.append(f'MSGA_{tag}_{name}_ai = {{ available_for = {{ {tag} }} role = {role} upgrade_prio = {{ factor = 0 modifier = {{ add = 80 {guard} = yes }} }} MSGA_{tag}_{name}_target = {{ upgrade_prio = {{ factor = 80 }} can_upgrade_in_field = {{ always = no }} target_template = {{ regiments = {{ {reg} }} support = {{ {sup} }} }} target_min_match = .99 }} }}')
 put('common/ai_templates/MSGA_balkan_mini_training.txt','\n'.join(ai))
 put('common/ai_strategy/MSGA_balkan_mini_training.txt','\n'.join(f'MSGA_{tag}_mini_training = {{ allowed = {{ original_tag = {tag} }} enable = {{ {guard} = yes }} abort_when_not_enabled = yes ai_strategy = {{ type = unit_ratio id = {unit} value = {ratio} }} }}' for tag,guard,unit,ratio in [('BOS','MSGA_BOS_can_train_armoured_brigade','modern_armor',15),('MNT','MSGA_MNT_can_train_territorial','militia',60)]))
 # Source crops contain a few preview-caption fragments above the actual art; trim these, never repaint.
 crops={'BOS_fragile_federation_spirit':(22,20,241,136),'BOS_open_the_old_depots':(14,14,220,148),'BOS_expand_war_industry':(0,22,228,169),'BOS_defend_central_bosnia':(14,22,236,169),'BOS_defend_the_federation':(0,22,249,169)}
 with ZipFile(PACK) as z:
  def art(member,path,size,sprite):
   member='Balkan_Mini_Rearmament_Individual_Assets/'+member;raw=z.read(member);im=Image.open(io.BytesIO(raw)).convert('RGBA');crop=crops.get(Path(member).stem)
   if crop:im=im.crop(crop)
   fitted=ImageOps.contain(im,size,Image.Resampling.LANCZOS);canvas=Image.new('RGBA',size,(0,0,0,0));canvas.alpha_composite(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2));b=io.BytesIO();canvas.save(b,format='DDS',pixel_format='DXT5');blob=b.getvalue();assert blob[84:88]==b'DXT5';files[path]=blob
   sprites.append(f'spriteType = {{ name = "{sprite}" texturefile = "{path}" }}');assets[path]={'source_member':member,'source_sha256':sha(raw),'sha256':sha(blob),'size':list(size),'compression':'DXT5','crop':crop}
  for tag,rows in ROWS.items():
   for stem,*_ in rows:
    src=f'{FOLDERS[tag]}/focus/{tag}_{stem}.png'
    if tag=='BOS' and stem=='emergency_defence_budget':src='Bosnia/focus/BOS_expand_war_industry.png'
    if tag=='MAC' and stem=='armed_macedonia':src='National_Spirits/MAC_armed_macedonia_spirit.png'
    if tag=='MNT' and stem=='the_balkans_are_burning':src='Montenegro/focus/MNT_kosovo_war_alarm.png'
    if tag=='MNT' and stem=='montenegro_prepared':src='National_Spirits/MNT_montenegro_prepared_spirit.png'
    path=f'gfx/interface/goals/MSGA_mini_{tag}_{stem}.dds';sprite=f'GFX_MSGA_mini_focus_{tag}_{stem}';art(src,path,(95,85),sprite);sprites.append(f'spriteType = {{ name = "{sprite}_shine" texturefile = "{path}" }}')
  for name in sorted({v[1] for v in IDEAS.values()}):art('National_Spirits/'+name+'.png','gfx/interface/ideas/MSGA_mini_'+name+'.dds',(64,64),'GFX_idea_MSGA_mini_idea_'+name)
  art('Bosnia/focus/BOS_kosovo_war_begins.png','gfx/interface/decisions/MSGA_mini_BOS_kosovo_alarm.dds',(100,100),'GFX_decision_category_MSGA_mini_BOS_kosovo_alarm')
  art('Bosnia/focus/BOS_purchase_yugoslav_t55_reserves.png','gfx/interface/decisions/MSGA_mini_BOS_t55_contract.dds',(52,45),'GFX_decision_MSGA_mini_BOS_t55_contract')
 put('interface/MSGA_balkan_mini_assets.gfx','spriteTypes = {\n'+'\n'.join(sprites)+'\n}')
 put('localisation/english/MSGA_balkan_mini_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
 for name in ['descriptor.mod','make_serbia_great_again.mod']:put(name,(TARGET/name).read_text().replace('version="0.16.0"','version="0.17.0"'))
 backup=ROOT/'logs/balkan_mini_backup';backup.mkdir(parents=True,exist_ok=True)
 for path,blob in files.items():
  out=TARGET/path;assert out.resolve().is_relative_to(TARGET.resolve())
  if out.exists():p=backup/path;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(out,p)
  out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
 launcher=TARGET.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(TARGET/'make_serbia_great_again.mod',launcher)
 native_files=['history/units/BOS_2020.txt','history/countries/BOS - Bosnia.txt','history/countries/MAC - Macedonia.txt','history/countries/MNT - Montenegro.txt','common/units/modern_armor.txt','common/units/infantry.txt','common/units/engineer.txt','common/units/artillery.txt','common/units/equipment/x_tank_chassis.txt','common/units/equipment/tank_chassis.txt','common/units/equipment/anti_tank.txt','common/ai_templates/generic.txt','common/ai_strategy/TFR_ai_strategy_ZZZ.txt','common/on_actions/00_TFR_on_actions_ZZZ_gamerules.txt','common/modifier_definitions/00_TFR_economic_modifiers_definition.txt','common/ideas/00_TFR_laws_economic.txt','map/definition.csv','map/provinces.bmp','history/states/104-Bosnia.txt','history/states/105-Montenegro.txt','history/states/106-Macedonia.txt']
 record={'version':'0.17.0','runtime':str(TARGET),'baseline_sha256':baseline,'deployed_sha256':{p:sha(b) for p,b in files.items()},'changed_relative_paths':sorted(files),'deployed_absolute_paths':[str(TARGET/p) for p in sorted(files)]+[str(launcher)],'package':str(PACK),'package_sha256':sha(PACK.read_bytes()),'native_sources_sha256':{p:sha((TFR/p).read_bytes()) for p in native_files},'assets':assets,'focuses':focus_records,'contracts':CONTRACTS,'ideas':IDEAS,'forts':FORTS,'geometry_and_graphics':json.loads((ROOT/'logs/mini_rearmament_inspection.json').read_text()),'armoured_template':ARMOUR_DEF,'armoured_requirements':{'modern_tank_chassis':50,'motorized_equipment':120,'infantry_equipment':775,'support_equipment':110,'artillery_equipment':12,'manpower':4550},'T55':'Exact existing SER T-55A; modern_tank_chassis_1 with NSB, modern_tank_equipment_1 without; no new variant created','art_adaptations':'Missing BOS budget uses supplied BOS industry art; missing MAC/MNT final focus images use their supplied final spirit art. Individual crops only, no generated art.','engine_validation':'NOT RUN; user game/saves untouched. Static/model validation required before source sync.'}
 (ROOT/'docs/balkan_mini_sources.json').write_text(json.dumps(record,indent=2)+'\n');print(f'LIVE 0.17 installed: {len(files)} paths; 42 focuses, 13 one-time contracts, 23 ideas, 50 DDS. Validate before source sync.')

if __name__=='__main__':main()
