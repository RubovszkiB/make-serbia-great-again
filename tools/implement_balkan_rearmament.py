"""Install the approved Balkan mini-trees in LIVE, preserving every prior file."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageOps
import hashlib, io, json, re, shutil
from deploy_local import ROOT, SOURCE, TARGET, inventory
from validate_phase1 import parse, get
TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV')
PACK=Path(r'C:\Users\Balazs\Downloads\Balkan_Rearmament_TFR_Assets.zip')
TAGS={'SLV':4,'CRO':4,'BOS':3,'MNT':3,'KOS':3,'ALB':3,'MAC':3}
NATIVE_TRIGGER='common/scripted_triggers/00_TFR_scripted_triggers_ZZZ_generic.txt'
ALB=[
 ('a_vulnerable_nation','A Vulnerable Nation',21,5,0,[],100),
 ('open_the_surplus_markets','Open the Surplus Markets',28,3,1,['a_vulnerable_nation'],90),
 ('empty_the_old_depots','Empty the Old Depots',28,3,2,['open_the_surplus_markets'],70),
 ('expand_military_workshops','Expand Military Workshops',35,7,1,['a_vulnerable_nation'],80),
 ('domestic_ammunition','Domestic Ammunition',35,7,2,['expand_military_workshops'],60),
 ('weapons_for_every_battalion','Weapons for Every Battalion',35,5,3,['empty_the_old_depots','domestic_ammunition'],60),
 ('look_to_ankara','Look to Ankara',35,3,4,['weapons_for_every_battalion'],55),
 ('secure_foreign_stockpiles','Secure Foreign Stockpiles',35,7,4,['weapons_for_every_battalion'],50),
 ('armed_albania','Armed Albania',35,5,5,['look_to_ankara','secure_foreign_stockpiles'],50)]
CRO=[
 ('business_as_usual','Business as Usual',35,3,0,[],60),
 ('support_hs_produkt','Support HS Produkt',35,1,1,['business_as_usual'],55),
 ('export_contracts','Export Contracts',35,1,2,['support_hs_produkt'],50),
 ('maintain_readiness','Maintain Readiness',35,5,1,['business_as_usual'],45),
 ('modernise_the_army','Modernise the Army',35,5,2,['maintain_readiness'],40),
 ('a_stable_croatia','A Stable Croatia',28,3,3,['export_contracts','modernise_the_army'],35),
 ('aggressive_rearmament','Aggressive Rearmament',21,13,0,[],1000),
 ('emergency_defence_budget','Emergency Defence Budget',28,13,1,['aggressive_rearmament'],950),
 ('expand_hs_produkt','Expand HS Produkt',35,11,2,['emergency_defence_budget'],900),
 ('mass_arms_production','Mass Arms Production',35,11,3,['expand_hs_produkt'],850),
 ('reactivate_duro_dakovic','Reactivate Đuro Đaković',35,15,2,['emergency_defence_budget'],800),
 ('armoured_modernisation','Armoured Modernisation',35,15,3,['reactivate_duro_dakovic'],750),
 ('western_procurement','Western Procurement',35,13,4,['mass_arms_production','armoured_modernisation'],700),
 ('prepare_the_reserves','Prepare the Reserves',28,11,5,['western_procurement'],650),
 ('secure_slavonia','Secure Slavonia',28,15,5,['western_procurement'],600),
 ('croatia_rearmed','Croatia Rearmed',35,13,6,['prepare_the_reserves','secure_slavonia'],550)]
# tag, ID stem, title, native billion-unit Treasury, days, required focus, deliveries(type,amount,producer), native decision icon
CONTRACTS=[
 ('ALB','purchase_old_eastern_rifles','Purchase Old Eastern Rifles',.4,10,'a_vulnerable_nation',[('infantry_equipment_1',1800,'SOV')],'generic_military'),
 ('ALB','acquire_old_mortars','Acquire Old Mortars',.5,14,'open_the_surplus_markets',[('artillery_equipment_1',60,'SOV'),('support_equipment_1',40,'ALB')],'generic_military_support'),
 ('ALB','buy_used_military_trucks','Buy Used Military Trucks',.6,14,'open_the_surplus_markets',[('motorized_equipment_1',120,'SOV')],'generic_trucks'),
 ('ALB','turkish_small_arms_contract','Turkish Small Arms Contract',.9,21,'look_to_ankara',[('infantry_equipment_3',1600,'TUR'),('support_equipment_1',60,'TUR')],'generic_military'),
 ('ALB','acquire_modern_at_weapons','Acquire Modern AT Weapons',1.1,21,'secure_foreign_stockpiles',[('anti_tank_equipment_2',120,'TUR')],'generic_military_support'),
 ('ALB','purchase_turkish_armoured_vehicles','Purchase Turkish Armoured Vehicles',1.4,30,'look_to_ankara',[('light_mechanized_equipment_2',60,'TUR')],'generic_tank'),
 ('CRO','nato_small_arms_package','NATO Small Arms Package',1.2,21,'western_procurement',[('infantry_equipment_3',1800,'USA'),('support_equipment_1',80,'USA')],'generic_military'),
 ('CRO','european_artillery_contract','European Artillery Contract',1.4,24,'western_procurement',[('artillery_equipment_2',96,'GER')],'generic_military_support'),
 ('CRO','american_ifv_package','American IFV Package',2.4,35,'armoured_modernisation',[('mechanized_equipment_2',70,'USA')],'generic_tank'),
 ('CRO','german_armour_contract','German Armour Contract',2.8,45,'armoured_modernisation',[('modern_tank_equipment_3',40,'GER')],'generic_tank'),
 ('CRO','modern_at_package','Modern AT Package',1.1,21,'western_procurement',[('anti_tank_equipment_2',120,'USA')],'generic_military_support')]
IDEAS={
 'ALB_surplus_procurement_network':('Surplus Procurement Network','ALB_surplus_procurement_network',{'income_growth_factor':.01,'business_value_factor':.02,'industrial_capacity_factory':.02}),
 'ALB_armed_albania':('Armed Albania','ALB_armed_albania_spirit',{'army_defence_factor':.05,'army_org_factor':.05,'mobilization_speed':.05}),
 'ALB_workshop_expansion':('Military Workshop Expansion','ALB_surplus_procurement_network',{'production_speed_arms_factory_factor':.05}),
 'ALB_domestic_ammunition':('Domestic Ammunition','ALB_surplus_procurement_network',{'industrial_capacity_factory':.05}),
 'ALB_battalion_readiness':('Weapons for Every Battalion','ALB_armed_albania_spirit',{'army_org_factor':.05,'land_reinforce_rate':.05}),
 'CRO_business_confidence':('Business Confidence','CRO_croatian_arms_exports',{'income_growth_factor':.01}),
 'CRO_hs_produkt_support':('Support for HS Produkt','CRO_croatian_arms_exports',{'industrial_capacity_factory':.02}),
 'CRO_arms_exports':('Croatian Arms Exports','CRO_croatian_arms_exports',{'industrial_capacity_factory':.03,'income_growth_factor':.02,'business_value_factor':.05}),
 'CRO_training_readiness':('Training Readiness','CRO_croatia_rearmed_spirit',{'training_time_army_factor':-.05}),
 'CRO_stable_industry':('A Stable Croatia','CRO_croatian_arms_exports',{'industrial_capacity_factory':.03}),
 'CRO_emergency_construction':('Emergency Defence Construction','CRO_croatian_arms_exports',{'production_speed_arms_factory_factor':.05}),
 'CRO_western_procurement_support':('Western Procurement Support','CRO_croatian_arms_exports',{'income_growth_factor':.01}),
 'CRO_reserve_preparation':('Reserve Preparation','CRO_croatia_rearmed_spirit',{'recruitable_population_factor':.05,'mobilization_speed':.10}),
 'CRO_rearmed':('Croatia Rearmed','CRO_croatia_rearmed_spirit',{'industrial_capacity_factory':.075,'army_org_factor':.05,'army_defence_factor':.05,'production_factory_max_efficiency_factor':.05})}
DESCS={
 'a_vulnerable_nation':'Albania cannot match its neighbours through prestige projects. Limited Treasury assistance and access to old equipment will support a small, defensible army.',
 'open_the_surplus_markets':'A modest procurement network will seek affordable equipment in old depots. Each negotiated contract can be purchased once.',
 'empty_the_old_depots':'Old rifles, artillery and support equipment will fill the gaps in our battalions without an expensive programme of modernisation.',
 'expand_military_workshops':'Expand our existing workshops with one military factory and an additional shared building slot. Construction support lasts 180 days.',
 'domestic_ammunition':'Ammunition production will support the army with a temporary output programme and a small delivery of support equipment.',
 'weapons_for_every_battalion':'Organise the available stock around complete battalions, improving readiness and opening the next stage of procurement.',
 'look_to_ankara':'Negotiate one-time Turkish small-arms and armoured-vehicle contracts. Equipment must be paid for and arrives after the agreed delivery period.',
 'secure_foreign_stockpiles':'Modest financial assistance and access to foreign stores will make a later anti-tank contract possible.',
 'armed_albania':'Consolidate a modest defensive army. Albania will rely on organised battalions and steady mobilisation rather than ambitious offensive programmes.',
 'business_as_usual':'Croatia will maintain ordinary government and stable economic relations while the regional situation remains calm.',
 'support_hs_produkt':'Support our arms manufacturer with additional industrial space and a modest production programme.',
 'export_contracts':'Croatian arms exports will support industrial output, income growth and business confidence.',
 'maintain_readiness':'Maintain staff experience, public readiness and efficient training without an emergency mobilisation.',
 'modernise_the_army':'Supply the existing army and support one round of infantry-weapons research.',
 'a_stable_croatia':'A stable government and a modest industrial programme provide a peaceful foundation for Croatia.',
 'aggressive_rearmament':'Serbia has entered the Bosnian conflict. Croatia must begin serious military preparation in response to that escalation.',
 'emergency_defence_budget':'Establish one military factory and two shared building slots, supported by a 180-day military-construction programme.',
 'expand_hs_produkt':'Expand military manufacture and deliver 1,200 service rifles for Croatia’s own formations.',
 'mass_arms_production':'A concentrated delivery of rifles, support equipment and artillery will supply the growing army.',
 'reactivate_duro_dakovic':'Reactivate defence manufacture with one military factory and a single research bonus for armour.',
 'armoured_modernisation':'Open one-time contracts for American infantry fighting vehicles and German armour, preserving our existing formations.',
 'western_procurement':'Negotiate fixed-price Western small-arms, artillery and anti-tank contracts. A modest economic support programme lasts 180 days.',
 'prepare_the_reserves':'Prepare the reserves through measured recruitment and improved mobilisation, without spawning free formations.',
 'secure_slavonia':'Improve infrastructure in Croatia Proper and build two fort levels in its eastern Slavonian frontier province.',
 'croatia_rearmed':'Croatia’s rearmament programme strengthens industrial output, organisation, defence and production efficiency.'}
REWARD_TEXT={
 'ALB_a_vulnerable_nation':'+5% War Support, +25 Political Power, +5 Army Experience and $1B Treasury assistance. Opens early procurement.',
 'ALB_open_the_surplus_markets':'Adds Surplus Procurement Network: +1% Income Growth, +2% Business Value and +2% Factory Output.',
 'ALB_empty_the_old_depots':'Receive 1,500 older rifles, 60 older artillery and 75 Support Equipment.',
 'ALB_expand_military_workshops':'Add one Military Factory and one shared building slot in Albania. +5% Military Factory Construction Speed for 180 days.',
 'ALB_domestic_ammunition':'+5% Factory Output for 180 days. Receive 25 Support Equipment.',
 'ALB_weapons_for_every_battalion':'+5% Division Organisation and +5 percentage points Reinforce Rate until Armed Albania replaces this programme.',
 'ALB_look_to_ankara':'Open the one-time Turkish small-arms and armoured-vehicle contracts.',
 'ALB_secure_foreign_stockpiles':'+$0.5B Treasury assistance and access to a one-time modern anti-tank contract.',
 'ALB_armed_albania':'Replace Battalion Readiness with Armed Albania: +5% Division Defence, +5% Organisation and +5% Mobilisation Speed.',
 'CRO_business_as_usual':'+40 Political Power, +2% Stability and +1% Income Growth for 180 days.',
 'CRO_support_hs_produkt':'+1 shared building slot in Croatia Proper and +2% Factory Output.',
 'CRO_export_contracts':'Adds Croatian Arms Exports: +3% Factory Output, +2% Income Growth and +5% Business Value.',
 'CRO_maintain_readiness':'+5 Army Experience, +2.5% War Support and 5% shorter army training time.',
 'CRO_modernise_the_army':'Receive 50 Support Equipment and one 50% research bonus for Infantry Weapons.',
 'CRO_a_stable_croatia':'+5% Stability and +3% Factory Output.',
 'CRO_aggressive_rearmament':'+10% War Support. Opens the emergency military branch after Serbia enters the Bosnian war.',
 'CRO_emergency_defence_budget':'+1 Military Factory and +2 shared building slots in Croatia Proper. +5% Military Factory Construction Speed for 180 days.',
 'CRO_expand_hs_produkt':'+1 Military Factory in Croatia Proper. Receive 1,200 service rifles.',
 'CRO_mass_arms_production':'Receive 2,200 service rifles, 120 Support Equipment and 60 Artillery.',
 'CRO_reactivate_duro_dakovic':'+1 Military Factory in Croatia Proper and one 50% research bonus for Armour.',
 'CRO_armoured_modernisation':'Open the one-time American IFV and German Armour contracts.',
 'CRO_western_procurement':'Open fixed-price Western procurement contracts. +1% Income Growth for 180 days.',
 'CRO_prepare_the_reserves':'+5% Recruitable Population Factor and +10% Mobilisation Speed.',
 'CRO_secure_slavonia':'+1 Infrastructure in Croatia Proper, up to its native maximum, and +2 land-fort levels in eastern Slavonia.',
 'CRO_croatia_rearmed':'Adds Croatia Rearmed: +7.5% Factory Output, +5% Organisation, +5% Division Defence and +5% Production Efficiency Cap.'}

def sha(data):return hashlib.sha256(data).hexdigest()
def treasury(value):return f'set_temp_variable = {{ var = income_var_temp value = {value:g} }} add_income = yes'
def equipment(items):return ' '.join(f'add_equipment_to_stockpile = {{ type = {typ} amount = {amount} producer = {producer} }}' for typ,amount,producer in items)
def identity(tag,stem):return 'MSGA_'+tag+'_'+stem
def focusflag(tag,stem):return identity(tag,stem)+'_done'
def factory(state,tag,slots=0):
 return f'''{state} = {{ if = {{ limit = {{ is_owned_by = {tag} is_fully_controlled_by = {tag} arms_factory < 20 }}
 set_temp_variable = {{ var = MSGA_rearm_build_before value = building_level@arms_factory }}
 set_temp_variable = {{ var = MSGA_rearm_build_expected value = MSGA_rearm_build_before }} add_to_temp_variable = {{ var = MSGA_rearm_build_expected value = 1 }}
 {'add_extra_state_shared_building_slots = '+str(slots) if slots else ''}
 if = {{ limit = {{ free_building_slots = {{ building = arms_factory size > 0 include_locked = yes }} }} add_building_construction = {{ type = arms_factory level = 1 instant_build = yes }} }}
 set_temp_variable = {{ var = MSGA_rearm_build_after value = building_level@arms_factory }}
 if = {{ limit = {{ check_variable = {{ var = MSGA_rearm_build_after value = MSGA_rearm_build_expected compare = equals }} }} log = "[MSGA REARM] {tag} military factory verified in state {state}" }}
 else = {{ {'add_extra_state_shared_building_slots = -'+str(slots) if slots else ''} log = "[MSGA REARM] {tag} military factory rejected in state {state}" }} }} }}'''

def main():
 baseline=inventory(TARGET);assert baseline==inventory(SOURCE) and len(baseline)==559
 assert 'version="0.15.0"' in (TARGET/'descriptor.mod').read_text()
 files={};loc={};effects=[];sprites=[];assets={};focus_records=[]
 def put(path,text):
  text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
  if not path.endswith(('.yml','.mod')):parse(text)
  files[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
 def idea(name,days=None):return f'add_timed_idea = {{ idea = MSGA_{name} days = {days} }}' if days else 'add_ideas = MSGA_'+name
 # Relevance is the actual switch used by TFR startup and native low-factory AI.
 native=(TFR/NATIVE_TRIGGER).read_text(encoding='utf-8-sig')
 old='\t\thas_content_tag = yes\n\t\thas_skeleton_tag = yes';assert native.count(old)==1
 added='\n'.join('\t\ttag = '+tag for tag in TAGS)
 put(NATIVE_TRIGGER,native.replace(old,old+'\n\t\t# MSGA: only these Balkan countries use normal native production AI.\n'+added,1))
 trigger='MSGA_balkan_ai_target = { OR = { '+' '.join('tag = '+tag for tag in TAGS)+' } }\nMSGA_croatian_bosnia_escalation = { SER = { has_country_flag = MSGA_bosnia_intervened } }\n'
 put('common/scripted_triggers/MSGA_balkan_rearmament_triggers.txt',trigger)
 restores=[]
 for tag,slots in TAGS.items():restores.append(f'if = {{ limit = {{ tag = {tag} amount_research_slots = 0 }} set_research_slots = {slots} }}')
 effects.append('MSGA_restore_balkan_ai = { if = { limit = { MSGA_balkan_ai_target = yes OR = { has_idea = ai_disabled_production NOT = { has_country_flag = MSGA_balkan_ai_restored } } } remove_ideas = ai_disabled_production country_lock_all_division_template = no '+' '.join(restores)+' set_country_flag = MSGA_balkan_ai_restored } }')
 starts=' '.join(f'{tag} = {{ if = {{ limit = {{ exists = yes }} MSGA_restore_balkan_ai = yes }} }}' for tag in TAGS)
 trees=' '.join(f'{tag} = {{ if = {{ limit = {{ exists = yes has_focus_tree = generic_focus }} load_focus_tree = {{ tree = MSGA_{tag}_rearmament keep_completed = yes }} }} }}' for tag in ['ALB','CRO'])
 put('common/on_actions/MSGA_balkan_rearmament_on_actions.txt',f'on_actions = {{ on_startup = {{ effect = {{ {starts} {trees} }} }} on_weekly = {{ effect = {{ MSGA_restore_balkan_ai = yes }} }} }}')
 # Starting factories are in state history only, never in startup cleanup.
 state='history/states/109-Eastern Croatia.txt';state_native=(TFR/state).read_text();assert 'arms_factory' not in state_native
 put(state,state_native.replace('industrial_complex = 1','industrial_complex = 1\n\t\t\tarms_factory = 2',1))
 template='division_template = { name = "Croatian Light Infantry" regiments = { infantry = { x = 0 y = 0 } infantry = { x = 0 y = 1 } artillery_brigade = { x = 1 y = 0 } } support = { } }'
 put('history/units/CRO_2020.txt',(TFR/'history/units/CRO_2020.txt').read_text()+'\n# Additional template only; existing units are unchanged.\n'+template)
 loc['MSGA_CRO_light_infantry']='Croatian Light Infantry'
 put('common/ai_templates/MSGA_CRO_light_infantry.txt','MSGA_CRO_light_infantry = { available_for = { CRO } role = infantry upgrade_prio = { factor = 5 modifier = { factor = 2 num_of_military_factories < 8 } } MSGA_CRO_light_infantry_target = { upgrade_prio = { factor = 5 } can_upgrade_in_field = { always = no } target_template = { regiments = { infantry = 2 artillery_brigade = 1 } support = { } } target_min_match = 0.9 } }')
 rewards={
 'ALB_a_vulnerable_nation':'add_war_support = 0.05 add_political_power = 25 army_experience = 5 '+treasury(1),
 'ALB_open_the_surplus_markets':idea('ALB_surplus_procurement_network'),
 'ALB_empty_the_old_depots':equipment([('infantry_equipment_1',1500,'SOV'),('artillery_equipment_1',60,'SOV'),('support_equipment_1',75,'ALB')]),
 'ALB_expand_military_workshops':factory(44,'ALB',1)+' '+idea('ALB_workshop_expansion',180),
 'ALB_domestic_ammunition':idea('ALB_domestic_ammunition',180)+' '+equipment([('support_equipment_1',25,'ALB')]),
 'ALB_weapons_for_every_battalion':idea('ALB_battalion_readiness'),
 'ALB_look_to_ankara':'',
 'ALB_secure_foreign_stockpiles':treasury(.5),
 'ALB_armed_albania':'remove_ideas = MSGA_ALB_battalion_readiness '+idea('ALB_armed_albania'),
 'CRO_business_as_usual':'add_political_power = 40 add_stability = 0.02 '+idea('CRO_business_confidence',180),
 'CRO_support_hs_produkt':'109 = { add_extra_state_shared_building_slots = 1 } '+idea('CRO_hs_produkt_support'),
 'CRO_export_contracts':idea('CRO_arms_exports'),
 'CRO_maintain_readiness':'army_experience = 5 add_war_support = 0.025 '+idea('CRO_training_readiness'),
 'CRO_modernise_the_army':equipment([('support_equipment_1',50,'CRO')])+' add_tech_bonus = { name = MSGA_CRO_infantry_research bonus = 0.5 uses = 1 category = infantry_weapons }',
 'CRO_a_stable_croatia':'add_stability = 0.05 '+idea('CRO_stable_industry'),
 'CRO_aggressive_rearmament':'add_war_support = 0.10',
 'CRO_emergency_defence_budget':factory(109,'CRO',2)+' '+idea('CRO_emergency_construction',180),
 'CRO_expand_hs_produkt':factory(109,'CRO')+' '+equipment([('infantry_equipment_2',1200,'CRO')]),
 'CRO_mass_arms_production':equipment([('infantry_equipment_2',2200,'CRO'),('support_equipment_1',120,'CRO'),('artillery_equipment_1',60,'CRO')]),
 'CRO_reactivate_duro_dakovic':factory(109,'CRO')+' add_tech_bonus = { name = MSGA_CRO_armour_research bonus = 0.5 uses = 1 category = armor }',
 'CRO_armoured_modernisation':'',
 'CRO_western_procurement':idea('CRO_western_procurement_support',180),
 'CRO_prepare_the_reserves':idea('CRO_reserve_preparation'),
 'CRO_secure_slavonia':'109 = { if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } add_building_construction = { type = bunker level = 2 province = 3627 instant_build = yes } }',
 'CRO_croatia_rearmed':idea('CRO_rearmed')}
 grants={'ALB_expand_military_workshops':44,'CRO_emergency_defence_budget':109,'CRO_expand_hs_produkt':109,'CRO_reactivate_duro_dakovic':109}
 state_rewards={'CRO_support_hs_produkt':109,'CRO_secure_slavonia':109}|grants
 for tag,rows in [('ALB',ALB),('CRO',CRO)]:
  blocks=[]
  for index,(stem,title,days,x,y,parents,weight) in enumerate(rows):
   id=identity(tag,stem);condition=f'tag = {tag} has_capitulated = no'
   if tag=='CRO' and index>=6:condition+=' MSGA_croatian_bosnia_escalation = yes'
   if tag+'_'+stem in state_rewards:
    st=state_rewards[tag+'_'+stem];condition+=f' {st} = {{ is_owned_by = {tag} is_fully_controlled_by = {tag}'
    if tag+'_'+stem in grants:condition+=' arms_factory < 20'
    if tag+'_'+stem in ['CRO_expand_hs_produkt','CRO_reactivate_duro_dakovic']:condition+=' free_building_slots = { building = arms_factory size > 0 include_locked = yes }'
    condition+=' }'
   unlocks=[r[2] for r in CONTRACTS if r[0]==tag and r[5]==stem]
   loc[id+'_reward_tt']=REWARD_TEXT[tag+'_'+stem];tooltip='custom_effect_tooltip = '+id+'_reward_tt'
   if unlocks:
    key=id+'_contracts_tt';loc[key]='Unlocks one-time contracts: '+', '.join(unlocks)+'.';tooltip+=' custom_effect_tooltip = '+key
   if stem=='weapons_for_every_battalion':loc[id+'_tier_tt']='Opens the second stage of Albanian procurement.';tooltip+=' custom_effect_tooltip = '+id+'_tier_tt'
   body=rewards[tag+'_'+stem]
   assert body or tooltip, 'Every focus delivers a reward or concrete contracts'
   parent_conditions=' '.join('has_completed_focus = '+identity(tag,p) for p in parents)
   effects.append(f'{id}_reward = {{ if = {{ limit = {{ {condition} {parent_conditions} NOT = {{ has_country_flag = {focusflag(tag,stem)} }} }} set_country_flag = {focusflag(tag,stem)} {body} }} }}')
   ai=f'factor = {weight}'
   if tag=='CRO' and index<6:ai+=' modifier = { factor = 0.01 MSGA_croatian_bosnia_escalation = yes }'
   blocks.append(f'focus = {{ id = {id} icon = GFX_MSGA_rearm_focus_{tag}_{stem} x = {x} y = {y} cost = {days/7:g} '+' '.join('prerequisite = { focus = '+identity(tag,p)+' }' for p in parents)+f' available = {{ {condition} }} cancel_if_invalid = yes continue_if_invalid = no ai_will_do = {{ {ai} }} completion_reward = {{ {tooltip} hidden_effect = {{ {id}_reward = yes }} }} }}')
   loc[id]=title;loc[id+'_desc']=DESCS[stem];focus_records.append({'id':id,'tag':tag,'days':days,'parents':[identity(tag,p) for p in parents],'native_direct_reward':body,'contracts_unlocked':unlocks})
  put(f'common/national_focus/MSGA_{tag}_rearmament.txt',f'focus_tree = {{ id = MSGA_{tag}_rearmament country = {{ factor = 0 modifier = {{ add = 100 tag = {tag} }} }} default = no reset_on_civilwar = no\n'+'\n'.join(blocks)+'\n}')
 # Persistent reservations: pay once at start, deliver once at the exact completion tick.
 categories=[]
 for tag in ['ALB','CRO']:
  rows=[];cat=identity(tag,'procurement');loc[cat]=('Albanian' if tag=='ALB' else 'Croatian')+' Military Procurement';loc[cat+'_desc']='One-time equipment contracts. Treasury is reserved immediately; delivery occurs after the stated period. Only one shipment can be pending at a time. Cancelled shipments are refunded.'
  for ctag,stem,title,cost,days,focus,items,icon in CONTRACTS:
   if ctag!=tag:continue
   id=identity(tag,stem);pending=id+'_pending';done=id+'_completed';busy=identity(tag,'procurement_busy')
   seller=' country_exists = GER' if stem=='german_armour_contract' else ''
   safe=f'tag = {tag} has_capitulated = no'+seller
   available=f'{safe} has_completed_focus = {identity(tag,focus)} NOT = {{ has_country_flag = {busy} }} NOT = {{ has_country_flag = {done} }} check_variable = {{ var = income_var value = {cost:g} compare = greater_than_or_equals }}'
   cancel=f'OR = {{ has_capitulated = yes'+(' NOT = { country_exists = GER }' if seller else '')+' }'
   delivery=equipment(items)
   if stem=='german_armour_contract':delivery='if = { limit = { has_dlc = "No Step Back" } add_equipment_to_stockpile = { type = modern_tank_chassis_1 amount = 40 producer = GER variant_name = "Leopard 2A5" } } else = { '+delivery+' }'
   effects.append(f'{id}_start = {{ if = {{ limit = {{ {available} NOT = {{ has_country_flag = {pending} }} }} {treasury(-cost)} set_country_flag = {pending} set_country_flag = {busy} }} }}')
   effects.append(f'{id}_cancel = {{ if = {{ limit = {{ has_country_flag = {pending} }} {treasury(cost)} clr_country_flag = {pending} clr_country_flag = {busy} }} }}')
   effects.append(f'{id}_finish = {{ if = {{ limit = {{ has_country_flag = {pending} NOT = {{ has_country_flag = {done} }} {safe} }} {delivery} set_country_flag = {done} clr_country_flag = {pending} clr_country_flag = {busy} }} else = {{ {id}_cancel = yes }} }}')
   desc=f'Treasury: ${cost:g}B. Delivery: {days} days. One-time only. '+', '.join(str(n)+' '+typ.replace('_equipment_',' equipment Mk ').replace('_',' ') for typ,n,prod in items)+'.'
   if stem=='german_armour_contract':desc+=' With No Step Back: 40 German Leopard 2A5 tanks, using the existing TFR design.'
   loc[id]=title;loc[id+'_desc']=desc;loc[id+'_available_tt']=f'Requires {next(r[1] for r in (ALB if tag=="ALB" else CRO) if r[0]==focus)}, ${cost:g}B Treasury, no other pending shipment, and a country that has not capitulated.'+(' Germany must exist.' if seller else '')
   loc[id+'_start_tt']=f'Reserve ${cost:g}B Treasury for a one-time {days}-day shipment. Cancellation refunds this amount.';loc[id+'_finish_tt']='Receive '+', '.join(str(n)+' '+typ.replace('_equipment_',' equipment Mk ').replace('_',' ') for typ,n,prod in items)+'. This contract is permanently completed.'
   cheap=cost<=.6;buffer=.25 if tag=='ALB' else .5
   ai=f'factor = {30 if cheap else 8 if cost<=1.4 else 2} modifier = {{ factor = 0 NOT = {{ check_variable = {{ var = income_var value = {cost+buffer:g} compare = greater_than_or_equals }} }} }}'
   rows.append(f'''{id} = {{ icon = {icon} cost = 0 days_remove = {days}
    visible = {{ tag = {tag} has_completed_focus = {identity(tag,focus)} NOT = {{ has_country_flag = {done} }} }}
    available = {{ custom_trigger_tooltip = {{ tooltip = {id}_available_tt {available} }} }}
    complete_effect = {{ custom_effect_tooltip = {id}_start_tt hidden_effect = {{ {id}_start = yes }} }}
    remove_effect = {{ custom_effect_tooltip = {id}_finish_tt hidden_effect = {{ {id}_finish = yes }} }}
    cancel_trigger = {{ hidden_trigger = {{ {cancel} }} }} cancel_effect = {{ hidden_effect = {{ {id}_cancel = yes }} }}
    ai_will_do = {{ {ai} }} }}''')
  categories.append(cat+' = {\n'+'\n'.join(rows)+'\n}')
 put('common/decisions/MSGA_balkan_procurement.txt','\n'.join(categories))
 put('common/decisions/categories/MSGA_balkan_procurement_categories.txt','\n'.join(identity(tag,'procurement')+' = { icon = military_operation allowed = { original_tag = '+tag+' } visible = { tag = '+tag+' has_country_flag = '+focusflag(tag,'a_vulnerable_nation' if tag=='ALB' else 'aggressive_rearmament')+' } }' for tag in ['ALB','CRO']))
 put('common/scripted_effects/MSGA_balkan_rearmament_effects.txt','\n'.join(effects))
 idea_blocks=[]
 for stem,(title,art,mods) in IDEAS.items():
  id='MSGA_'+stem;loc[id]=title;loc[id+'_desc']='A modest '+('Albanian' if stem.startswith('ALB') else 'Croatian')+' programme supporting '+title.lower()+'.'
  idea_blocks.append(id+' = { picture = MSGA_rearm_idea_'+art+' allowed = { original_tag = '+stem[:3]+' } removal_cost = -1 modifier = { '+' '.join(f'{k} = {v:g}' for k,v in mods.items())+' } }')
 put('common/ideas/MSGA_balkan_rearmament_ideas.txt','ideas = { country = {\n'+'\n'.join(idea_blocks)+'\n} }')
 loc['MSGA_CRO_infantry_research']='Croatian Infantry Modernisation';loc['MSGA_CRO_armour_research']='Đuro Đaković Armour Research'
 put('localisation/english/MSGA_balkan_rearmament_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))
 with ZipFile(PACK) as z:
  def art(member,path,size,sprite):
   raw=z.read('Balkan_Rearmament_TFR_Assets/'+member);im=Image.open(io.BytesIO(raw)).convert('RGBA');fitted=ImageOps.contain(im,size,Image.Resampling.LANCZOS)
   canvas=Image.new('RGBA',size,(0,0,0,0));canvas.alpha_composite(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2));b=io.BytesIO();canvas.save(b,format='DDS',pixel_format='DXT5');blob=b.getvalue();assert blob[84:88]==b'DXT5';files[path]=blob
   sprites.append(f'spriteType = {{ name = "{sprite}" texturefile = "{path}" }}');assets[path]={'source_member':'Balkan_Rearmament_TFR_Assets/'+member,'source_sha256':sha(raw),'sha256':sha(blob),'size':list(size),'compression':'DXT5'}
  for tag,rows,folder in [('ALB',ALB,'Albania'),('CRO',CRO,'Croatia')]:
   for stem,*_ in rows:
    path=f'gfx/interface/goals/MSGA_rearm_{tag}_{stem}.dds';art(f'{folder}/focus/{tag}_{stem}.png',path,(95,85),f'GFX_MSGA_rearm_focus_{tag}_{stem}');sprites.append(f'spriteType = {{ name = "GFX_MSGA_rearm_focus_{tag}_{stem}_shine" texturefile = "{path}" }}')
  for name in sorted({v[1] for v in IDEAS.values()}):art('National_Spirits/'+name+'.png','gfx/interface/ideas/MSGA_rearm_'+name+'.dds',(64,64),'GFX_idea_MSGA_rearm_idea_'+name)
 put('interface/MSGA_balkan_rearmament_assets.gfx','spriteTypes = {\n'+'\n'.join(sprites)+'\n}')
 for name in ['descriptor.mod','make_serbia_great_again.mod']:put(name,(TARGET/name).read_text().replace('version="0.15.0"','version="0.16.0"'))
 backup=ROOT/'logs/balkan_rearmament_backup';backup.mkdir(parents=True,exist_ok=True)
 for path,blob in files.items():
  out=TARGET/path;assert out.resolve().is_relative_to(TARGET.resolve())
  if out.exists():p=backup/path;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(out,p)
  out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
 launcher=TARGET.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(TARGET/'make_serbia_great_again.mod',launcher)
 native_files=[NATIVE_TRIGGER,'common/ideas/TFR_ideas_ZZZ_mishmash.txt','common/on_actions/00_TFR_on_actions_ZZZ_startup.txt','common/on_actions/00_TFR_on_actions_ZZZ_money.txt','common/ai_strategy/TFR_ai_strategy_ZZZ.txt','common/ai_templates/generic.txt','common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt','common/modifier_definitions/00_TFR_economic_modifiers_definition.txt','history/states/109-Eastern Croatia.txt','history/states/103-Dalmatia.txt','history/states/44-Albania.txt','history/units/CRO_2020.txt','history/units/ALB_2000.txt','history/countries/GER - Germany.txt','common/units/equipment/infantry.txt','common/units/equipment/artillery.txt','common/units/equipment/anti_tank.txt','common/units/equipment/mechanized.txt','common/units/equipment/motorized.txt','common/units/equipment/support.txt','common/units/equipment/x_tank_chassis.txt','common/units/infantry.txt','common/units/artillery.txt','common/technologies/infantry.txt','common/technology_tags/00_technology.txt','common/country_tags/00_countries.txt','interface/TFR_interface_decisions.gfx','interface/decisions.gfx','map/definition.csv','map/provinces.bmp']
 native_files+=[str(p.relative_to(TFR)).replace('\\','/') for p in (TFR/'history/countries').glob('*.txt') if p.name[:3] in TAGS]
 record={'version':'0.16.0','runtime':str(TARGET),'baseline_sha256':baseline,'deployed_sha256':{p:sha(b) for p,b in files.items()},'changed_relative_paths':sorted(files),'deployed_absolute_paths':[str(TARGET/p) for p in sorted(files)]+[str(launcher)],'package':str(PACK),'package_sha256':sha(PACK.read_bytes()),'native_sources_sha256':{p:sha((TFR/p).read_bytes()) for p in native_files},'assets':assets,'focuses':focus_records,'contracts':CONTRACTS,'ideas':IDEAS,'AI_target_research_slots':TAGS,'AI_native_trigger_addition':added,'Croatia_Proper_state':109,'native_factory_in_Croatia_Proper':0,'new_factories_in_Croatia_Proper':2,'national_starting_factories':3,'Slavonia_fort_province':3627,'Slavonia_geometry':json.loads((ROOT/'logs/rearmament_provinces.json').read_text()),'CRO_template':{'internal_name':'Croatian Light Infantry','localisation_key':'MSGA_CRO_light_infantry','definition':template,'free_divisions_spawned':0},'contract_NSBack_armour':{'type':'modern_tank_chassis_1','variant_name':'Leopard 2A5','producer':'GER','amount':40},'native_API_adaptations':{'Treasury':'income_var_temp / add_income','Monthly_income':'income_growth_factor','Business_value':'business_value_factor','purchase_discount':'fixed negotiated contract prices; no unsupported generic discount','specific_production':'modest general output rather than unproven equipment-specific modifiers'},'actual_engine_validation':'NOT RUN: game/saves reserved by user. Static/model smoke checks only.'}
 (ROOT/'docs/balkan_rearmament_sources.json').write_text(json.dumps(record,indent=2)+'\n');print(f'LIVE 0.16 installed: {len(files)} paths; 25 focuses, 11 contracts, 14 ideas, 29 DDS. Validate before source sync.')

if __name__=='__main__':main()
