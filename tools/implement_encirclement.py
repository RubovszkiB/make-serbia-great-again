"""One-time 0.11 migration: build and install the authorized pre-war chapter LIVE first."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
from validate_phase1 import parse,get,descend
ROOT=Path(__file__).resolve().parents[1]
LIVE=Path(r'C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again')
TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
PACKAGE=Path(r'C:\Users\Balazs\Downloads\MSGA_Balkan_Encirclement_TFR_Assets.zip')
MEMBERS={'CRO':(109,11581,5,2),'ALB':(44,9914,3,2),'SLV':(102,9627,3,1),'MAC':(106,3882,3,0),'MNT':(105,9809,3,0)}
FOCUSES=[
 ('pressure_podgorica','Pressure Podgorica',2,0,2,[], 'country_event = { id = MSGA_encirclement.1 }'),
 ('pressure_skopje','Pressure Skopje',6,0,2,[], 'country_event = { id = MSGA_encirclement.2 }'),
 ('balkans_close_ranks','The Balkans Close Ranks',4,0,1,[],'add_political_power = 25 army_experience = 10'),
 ('prepare_western_front','Prepare the Western Front',0,1,1,['balkans_close_ranks'],'army_experience = 10 add_timed_idea = { idea = MSGA_western_preparation days = 120 }'),
 ('secure_drina_corridor','Secure the Drina Corridor',0,2,1,['prepare_western_front'],'MSGA_secure_drina_supply = yes country_event = { id = MSGA_encirclement.8 }'),
 ('prepare_southern_front','Prepare the Southern Front',4,1,1,['balkans_close_ranks'],'army_experience = 10 add_timed_idea = { idea = MSGA_southern_preparation days = 120 }'),
 ('fortify_kosovo','Fortify Kosovo',4,2,1,['prepare_southern_front'],'MSGA_fortify_kosovo_front = yes country_event = { id = MSGA_encirclement.9 }'),
 ('call_up_reserves','Call Up the Reserves',8,1,1,['balkans_close_ranks'],'add_war_support = 0.05 add_timed_idea = { idea = MSGA_encirclement_reserves days = 120 } country_event = { id = MSGA_encirclement.10 }'),
 ('stockpile_continental_war','Stockpile for a Continental War',8,2,1,['call_up_reserves'],'add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 5000 producer = SER } add_equipment_to_stockpile = { type = motorized_equipment_1 amount = 300 producer = SER } add_equipment_to_stockpile = { type = support_equipment_1 amount = 150 producer = SER } add_equipment_to_stockpile = { type = artillery_equipment_1 amount = 100 producer = SER } add_fuel = 10000'),
 ('coordinate_protectorates','Coordinate the Protectorates',4,3,1,['secure_drina_corridor','fortify_kosovo','stockpile_continental_war'],'army_experience = 10 MSGA_coordinate_existing_protectorates = yes country_event = { id = MSGA_encirclement.11 }'),
 ('serbian_war_plan','The Serbian War Plan',4,4,2,['coordinate_protectorates'],'add_timed_idea = { idea = MSGA_operation_thunder days = 120 }'),
 ('break_the_ring','Break the Ring',4,5,1,['serbian_war_plan'],'MSGA_open_pact_war = yes'),
]
EVENTS={
 1:('podgorica_rejects_belgrade','Podgorica Rejects Belgrade','Montenegro rejects Belgrade’s demands. Its government insists that sovereignty cannot be bargained away under regional pressure.','They have rejected our approach.'),
 2:('skopje_refuses_serbian_demands','Skopje Refuses Serbian Demands','North Macedonia refuses Serbia’s demands and seeks partners who share its concern over the changing regional balance.','Skopje has made its choice.'),
 3:('calculation_failed','The Calculation Failed','Neither Podgorica nor Skopje has yielded. Pressure has brought neighbouring governments closer together, while Belgrade must reconsider the assumptions behind its policy.','Prepare for the consequences.'),
 4:('balkan_states_break_with_brussels','The Balkan States Break with Brussels','Regional governments no longer consider the Atlantic security framework sufficient to contain the changing Balkan balance. Zagreb, Tirana, Ljubljana, Skopje and Podgorica seek an independent security arrangement.','The region is closing ranks.'),
 5:('zagreb_tirana_pact','The Zagreb–Tirana Pact','Croatia and Albania have founded a defensive regional alliance with Slovenia, North Macedonia and Montenegro. The Pact pledges to preserve national sovereignty and contain further Serbian expansion.','They have chosen confrontation.'),
 6:('pact_mobilises','The Pact Mobilises','All five Pact governments mobilise emergency forces. Motorized formations reinforce Croatia, Albania and Slovenia, while territorial militias prepare to defend each member’s home territory.','The ring is taking shape.'),
 7:('emergency_measures_belgrade','Emergency Measures in Belgrade','Belgrade expands military production and organises two emergency territorial brigades. Serbia now faces a regional bloc and must prepare its western approaches, southern frontier and home front.','Belgrade will be ready.'),
 8:('western_shield','The Western Shield','Roads across the Drina and through the existing protectorates support the western theatre. These preparations use the settlement already established by Serbia.','Keep the western routes open.'),
 9:('kosovo_front_line','Kosovo: The Front Line','Infrastructure and limited border fortifications prepare Kosovo for a wider regional confrontation. The existing Kosovo brigade remains part of the Serbian force.','Secure the southern approaches.'),
 10:('serbia_mobilises','Serbia Mobilises','Reservists return to training as Belgrade prepares for a continental struggle. Mobilisation supports the existing army rather than creating an unlimited reserve of men.','Prepare the reserves.'),
 11:('allies_take_positions','The Allies Take Their Positions','Serbian command coordinates the existing Bosnian and Herzegovinian territorial formations. Their regional identities remain intact; no duplicate formations are raised. Remaining protectorates align their logistics with Belgrade.','Coordinate the forces already at our disposal.'),
 12:('first_blow','The First Blow','Operation Thunder opens against the Zagreb–Tirana Pact. Serbia’s preparations may give the army a brief advantage in the first ten days. What follows will depend on the campaign itself.','Begin Operation Thunder.'),
}
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 assert LIVE.resolve(strict=True)==LIVE.absolute()
 baseline=json.loads((ROOT/'docs/post_bosnia_sync.json').read_text())
 before={p.relative_to(LIVE).as_posix():sha(p.read_bytes()) for p in LIVE.rglob('*') if p.is_file()}
 expected=baseline.get('sha256',baseline.get('sha256_by_relative_path'))
 if expected is None:
  expected={p.relative_to(ROOT/'make_serbia_great_again').as_posix():sha(p.read_bytes()) for p in (ROOT/'make_serbia_great_again').rglob('*') if p.is_file()}
 assert before==expected, 'Review untracked runtime changes before migration'
 content={};loc={};assets={};native={}
 def put(path,text):
  if path.endswith(('.txt','.gfx')):parse(text)
  content[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
 def read(path):return (LIVE/path).read_text(encoding='utf-8-sig')
 def l(key,value):loc[key]=value
 # Milestone recovery works for both new campaigns and saves already at regional power.
 put('common/scripted_effects/MSGA_encirclement_effects.txt','''# Serbia-only chapter entry; no earlier chapter is skipped.
MSGA_open_southern_question = {
 if = { limit = { tag = SER has_country_flag = MSGA_regional_power_achieved NOT = { has_country_flag = MSGA_encirclement_started } }
  set_country_flag = MSGA_encirclement_started set_country_flag = MSGA_southern_question_active clr_country_flag = MSGA_post_bosnia_active
  load_focus_tree = { tree = MSGA_SER_southern_question keep_completed = yes }
 }
}
MSGA_schedule_calculation_failed = {
 if = { limit = { tag = SER has_country_flag = MSGA_montenegro_rejected has_country_flag = MSGA_macedonia_rejected NOT = { has_country_flag = MSGA_calculation_scheduled } }
  set_country_flag = MSGA_calculation_scheduled country_event = { id = MSGA_encirclement.3 days = 3 }
 }
}
MSGA_try_pact_realignment = {
 if = { limit = { tag = SER has_country_flag = MSGA_calculation_failed NOT = { has_country_flag = MSGA_zagreb_tirana_pact_formed } MSGA_pact_candidates_ready = yes }
  MSGA_detach_pact_candidates = yes
  CRO = { create_faction = MSGA_zagreb_tirana_pact add_to_faction = ALB add_to_faction = SLV add_to_faction = MAC add_to_faction = MNT }
  set_country_flag = MSGA_zagreb_tirana_pact_formed
  country_event = { id = MSGA_encirclement.4 }
  country_event = { id = MSGA_encirclement.5 }
  country_event = { id = MSGA_encirclement.6 days = 1 }
 }
}
MSGA_open_pact_planning = {
 if = { limit = { tag = SER has_country_flag = MSGA_zagreb_tirana_pact_formed has_country_flag = MSGA_pact_mobilised has_country_flag = MSGA_belgrade_emergency_done NOT = { has_country_flag = MSGA_pact_planning_active } }
  clr_country_flag = MSGA_southern_question_active set_country_flag = MSGA_pact_planning_active
  load_focus_tree = { tree = MSGA_SER_pact_war_planning keep_completed = yes }
 }
}
MSGA_secure_drina_supply = {
 every_state = { limit = { OR = { state = 1296 state = 104 state = 851 state = 848 state = 849 state = 850 } OR = { AND = { is_owned_by = SER is_fully_controlled_by = SER } AND = { owner = { is_subject_of = SER } is_fully_controlled_by = OWNER } } infrastructure < 5 }
  add_building_construction = { type = infrastructure level = 1 instant_build = yes }
 }
}
MSGA_fortify_kosovo_front = {
 785 = { if = { limit = { is_owned_by = SER is_fully_controlled_by = SER }
  if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }
  add_building_construction = { type = bunker level = 1 province = 9849 instant_build = yes }
 } }
 1305 = { if = { limit = { is_owned_by = SER is_fully_controlled_by = SER }
  if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }
  add_building_construction = { type = bunker level = 1 province = 14401 instant_build = yes }
 } }
}
MSGA_coordinate_existing_protectorates = {
 every_subject_country = { limit = { OR = { tag = BOS tag = HRZ tag = SRP } }
  add_timed_idea = { idea = MSGA_pact_logistics_cooperation days = 120 }
 }
}
MSGA_open_pact_war = {
 if = { limit = { tag = SER has_country_flag = MSGA_pact_planning_active NOT = { has_country_flag = MSGA_pact_war_opened } MSGA_pact_ready_for_war = yes }
  MSGA_remove_external_pact_guarantees = yes
  set_country_flag = MSGA_pact_war_opened
  declare_war_on = { target = CRO type = annex_everything }
  ALB = { add_to_war = { targeted_alliance = CRO enemy = SER hostility_reason = asked_to_join single_target_only = yes } }
  SLV = { add_to_war = { targeted_alliance = CRO enemy = SER hostility_reason = asked_to_join single_target_only = yes } }
  MAC = { add_to_war = { targeted_alliance = CRO enemy = SER hostility_reason = asked_to_join single_target_only = yes } }
  MNT = { add_to_war = { targeted_alliance = CRO enemy = SER hostility_reason = asked_to_join single_target_only = yes } }
  add_timed_idea = { idea = MSGA_surprise_attack days = 10 }
  country_event = { id = MSGA_encirclement.12 }
 }
}
''')
 # Existing capstone triggers entry immediately; weekly/startup recovery handles older saves.
 path='common/scripted_effects/MSGA_post_bosnia_effects.txt'
 old=read(path);needle='country_event = { id = MSGA_postbosnia.16 }'
 assert old.count(needle)==1
 put(path,old.replace(needle,needle+'\n  MSGA_open_southern_question = yes'))
 candidates=' '.join(f'{tag} = {{ exists = yes is_subject = no has_war = no is_faction_leader = no }}' for tag in MEMBERS)
 spawns=' '.join(f'{state} = {{ is_owned_by = {tag} is_fully_controlled_by = {tag} is_core_of = {tag} }} {tag} = {{ controls_province = {province} }}' for tag,(state,province,mi,mo) in MEMBERS.items())
 ready=' '.join(f'{tag} = {{ exists = yes '+('is_in_faction = yes' if tag=='CRO' else 'is_in_faction_with = CRO')+' is_subject = no has_war = no }' for tag in MEMBERS)
 ready+=' NOT = { any_other_country = { is_in_faction_with = CRO NOT = { OR = { tag = CRO tag = ALB tag = SLV tag = MAC tag = MNT } } } }'
 put('common/scripted_triggers/MSGA_encirclement_triggers.txt',f'''# Do not dismantle an unrelated faction or change a subject's overlord.
MSGA_pact_candidates_ready = {{ {candidates} }}
MSGA_pact_safe_mobilisation = {{ {spawns} 107 = {{ is_owned_by = SER is_fully_controlled_by = SER is_core_of = SER }} SER = {{ controls_province = 11586 }} }}
MSGA_pact_ready_for_war = {{ tag = SER has_war = no has_country_flag = MSGA_pact_mobilised has_country_flag = MSGA_belgrade_emergency_done CRO = {{ is_faction_leader = yes }} {ready} }}
''')
 diplomacy=['# Only the five approved Pact candidates are realigned. No other diplomacy is changed.','MSGA_detach_pact_candidates = {']
 for tag in MEMBERS:
  diplomacy += [f' every_other_country = {{ limit = {{ is_faction_leader = yes is_in_faction_with = {tag} }} remove_from_faction = {tag} }}',f' USA = {{ if = {{ limit = {{ is_in_array = {{ array = USA_nato_members value = {tag} }} }} remove_from_array = {{ array = USA_nato_members value = {tag} }} }} }}',f' {tag} = {{ set_country_flag = left_NATO clr_country_flag = has_joined_NATO_by_event clr_country_flag = NATO_current_leader set_country_flag = MSGA_independent_pact_member add_ideas = MSGA_pact_diplomatic_independence', '  '+' '.join('remove_ideas = NATO_unity_'+str(i) for i in range(1,6)), ' }']
 diplomacy+=[' MSGA_remove_external_pact_guarantees = yes','}','MSGA_remove_external_pact_guarantees = {',' every_other_country = { limit = { NOT = { OR = { tag = CRO tag = ALB tag = SLV tag = MAC tag = MNT } } }']
 for tag in MEMBERS:diplomacy += [f'  if = {{ limit = {{ has_guaranteed = {tag} }} diplomatic_relation = {{ country = {tag} relation = guarantee active = no }} }}']
 diplomacy+=[' }','}']
 put('common/scripted_effects/MSGA_pact_diplomacy.txt','\n'.join(diplomacy)+'\n')
 # TFR's queued invitation/acceptance events ignore left_NATO; guard their actual entry points.
 path='events/TFR_events_ZZZ_NATO.txt';data=(TFR/path).read_bytes();text=data.decode('utf-8-sig').replace('\r\n','\n')
 for id,condition in [('nato.1','NOT = { has_country_flag = MSGA_independent_pact_member }'),('nato.2','NOT = { FROM = { has_country_flag = MSGA_independent_pact_member } }'),('nato.4','NOT = { FROM = { has_country_flag = MSGA_independent_pact_member } }')]:
  needle='id = '+id+'\n\ttitle';assert text.count(needle)==1
  text=text.replace(needle,'id = '+id+'\n\ttrigger = { '+condition+' }\n\ttitle')
 put(path,'\n'.join(line.rstrip() for line in text.splitlines())+'\n');native[path]={'upstream_sha256':sha(data),'guards':['nato.1','nato.2','nato.4'],'purpose':'Cancel pending NATO invitations/applications for approved Pact members only'}
 put('common/on_actions/MSGA_encirclement_on_actions.txt','''on_actions = {
 on_startup = { effect = { SER = { MSGA_open_southern_question = yes MSGA_schedule_calculation_failed = yes MSGA_try_pact_realignment = yes MSGA_recover_pact_mobilisation = yes MSGA_open_pact_planning = yes } } }
 on_weekly = { effect = { if = { limit = { tag = SER } MSGA_open_southern_question = yes if = { limit = { has_country_flag = MSGA_encirclement_started NOT = { has_country_flag = MSGA_pact_war_opened } } MSGA_schedule_calculation_failed = yes MSGA_try_pact_realignment = yes MSGA_recover_pact_mobilisation = yes MSGA_open_pact_planning = yes } } } }
}
''')
 mobilisation=['MSGA_recover_pact_mobilisation = {',' if = { limit = { tag = SER has_country_flag = { flag = MSGA_zagreb_tirana_pact_formed days > 0 } NOT = { has_country_flag = MSGA_pact_mobilised } MSGA_pact_safe_mobilisation = yes } MSGA_mobilise_pact = yes country_event = { id = MSGA_encirclement.6 } }',' if = { limit = { tag = SER has_country_flag = MSGA_pact_mobilised NOT = { has_country_flag = MSGA_belgrade_emergency_done } 107 = { is_owned_by = SER is_fully_controlled_by = SER is_core_of = SER } controls_province = 11586 } MSGA_belgrade_emergency = yes country_event = { id = MSGA_encirclement.7 } }','}','MSGA_mobilise_pact = {',' if = { limit = { tag = SER has_country_flag = MSGA_zagreb_tirana_pact_formed NOT = { has_country_flag = MSGA_pact_mobilised } MSGA_pact_safe_mobilisation = yes }']
 for tag,(state,province,mil,mot) in MEMBERS.items():
  required=mil*3000+mot*4800
  mobilisation += [f'  {tag} = {{ if = {{ limit = {{ has_manpower < {required} }} add_manpower = {required} }} load_oob = MSGA_{tag}_pact_emergency }}']
 mobilisation+=['  set_country_flag = MSGA_pact_mobilised country_event = { id = MSGA_encirclement.7 }',' }','}','MSGA_belgrade_emergency = {',' if = { limit = { tag = SER has_country_flag = MSGA_pact_mobilised NOT = { has_country_flag = MSGA_belgrade_emergency_done } 107 = { is_owned_by = SER is_fully_controlled_by = SER is_core_of = SER } controls_province = 11586 }','  107 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = arms_factory level = 1 instant_build = yes } }','  if = { limit = { has_manpower < 6000 } add_manpower = 6000 } load_oob = MSGA_SER_pact_emergency','  set_country_flag = MSGA_belgrade_emergency_done MSGA_open_pact_planning = yes',' }','}']
 put('common/scripted_effects/MSGA_pact_mobilisation.txt','\n'.join(mobilisation)+'\n')
 for tag,(state,province,mil,mot) in {**MEMBERS,'SER':(107,11586,2,0)}.items():
  text=[]
  for battalion,n,name in [('militia',3,'Territorial Militia'),('motorized',4,'Emergency Motorized')]:
   if battalion=='motorized' and mot==0:continue
   text += [f'division_template = {{ name = "MSGA {tag} {name}" regiments = {{ '+' '.join(f'{battalion} = {{ x = 0 y = {y} }}' for y in range(n))+' } }']
  text+=['units = {']
  for name,count in [('Territorial Militia',mil),('Emergency Motorized',mot)]:
   for i in range(1,count+1):text+=[f' division = {{ name = "{i}. {tag} {name}" location = {province} division_template = "MSGA {tag} {name}" start_equipment_factor = 1 start_manpower_factor = 1 start_experience_factor = 0.1 }}']
  put(f'history/units/MSGA_{tag}_pact_emergency.txt','\n'.join(text+['}'])+'\n')
 for name,subset,flag in [('southern_question',FOCUSES[:2],'MSGA_southern_question_active'),('pact_war_planning',FOCUSES[2:],'MSGA_pact_planning_active')]:
  tree=['focus_tree = {',f' id = MSGA_SER_{name}',f' country = {{ factor = 0 modifier = {{ add = 300 tag = SER has_country_flag = {flag} }} }}',' default = no reset_on_civilwar = no']
  for stem,title,x,y,cost,parents,reward in subset:
   tree+=[f' focus = {{ id = MSGA_{stem} icon = GFX_MSGA_focus_{stem} x = {x} y = {y} cost = {cost}']
   tree += [f'  prerequisite = {{ focus = MSGA_{parent} }}' for parent in parents]
   available='MSGA_pact_ready_for_war = yes' if stem=='break_the_ring' else f'has_country_flag = {flag}'
   tree += [f'  available = {{ {available} }} ai_will_do = {{ factor = 10 }}',f'  completion_reward = {{ set_country_flag = MSGA_completed_{stem} {reward} }}',' }']
   l('MSGA_'+stem,title);l('MSGA_'+stem+'_desc',{'break_the_ring':'Begin Operation Thunder against all five Zagreb–Tirana Pact members. The opening advantage lasts ten days; later campaign events are outside this chapter.','coordinate_protectorates':'Coordinate the existing Bosnian and Herzegovinian territorial brigades under Serbian command and the logistics of remaining protectorates. No duplicate units will be raised.'}.get(stem,title+'. Prepare Serbia for the regional confrontation.'))
  put(f'common/national_focus/MSGA_SER_{name}.txt','\n'.join(tree+['}'])+'\n')
 ev=['add_namespace = MSGA_encirclement']
 for id,(stem,title,desc,option) in EVENTS.items():
  trigger={1:'has_country_flag = MSGA_completed_pressure_podgorica NOT = { has_country_flag = MSGA_montenegro_rejected }',2:'has_country_flag = MSGA_completed_pressure_skopje NOT = { has_country_flag = MSGA_macedonia_rejected }',3:'has_country_flag = MSGA_montenegro_rejected has_country_flag = MSGA_macedonia_rejected NOT = { has_country_flag = MSGA_calculation_failed }',6:'has_country_flag = MSGA_zagreb_tirana_pact_formed MSGA_pact_safe_mobilisation = yes',7:'has_country_flag = MSGA_pact_mobilised 107 = { is_owned_by = SER is_fully_controlled_by = SER is_core_of = SER } controls_province = 11586'}.get(id,'has_country_flag = MSGA_encirclement_started')
  reward={1:'add_political_power = -10 add_war_support = 0.02 set_country_flag = MSGA_montenegro_rejected MSGA_schedule_calculation_failed = yes',2:'add_political_power = -10 add_war_support = 0.02 set_country_flag = MSGA_macedonia_rejected MSGA_schedule_calculation_failed = yes',3:'add_stability = -0.05 add_war_support = 0.05 set_country_flag = MSGA_calculation_failed MSGA_try_pact_realignment = yes',6:'MSGA_mobilise_pact = yes',7:'MSGA_belgrade_emergency = yes'}.get(id,'')
  ev += [f'country_event = {{ id = MSGA_encirclement.{id} title = MSGA_encirclement.{id}.t desc = MSGA_encirclement.{id}.d picture = GFX_MSGA_event_{stem}',f' is_triggered_only = yes fire_only_once = yes trigger = {{ tag = SER {trigger} }}',f' immediate = {{ {reward} }}',f' option = {{ name = MSGA_encirclement.{id}.a }}','}']
  l(f'MSGA_encirclement.{id}.t',title);l(f'MSGA_encirclement.{id}.d',desc);l(f'MSGA_encirclement.{id}.a',option)
 put('events/MSGA_encirclement_events.txt','\n'.join(ev)+'\n')
 ideas=[('pact_diplomatic_independence','Independent Pact Diplomacy','The Pact conducts its own security policy. Atlantic invitations and AI alliance requests cannot reverse this alignment.','MSGA_prepared_for_war','', 'rule = { can_join_factions = no }'),('western_preparation','Western Front Preparations','Temporary staff preparation for the western front.','MSGA_prepared_for_war','planning_speed = 0.03',''),('southern_preparation','Southern Front Preparations','Temporary staff preparation for the southern front.','MSGA_prepared_for_war','planning_speed = 0.03',''),('encirclement_reserves','Reservists in Training','A limited programme accelerates mobilisation and reserve training.','MSGA_prepared_for_war','mobilization_speed = 0.05 training_time_army_factor = -0.05',''),('pact_logistics_cooperation','Protectorate Logistics Coordination','Existing protectorate forces coordinate supply with Serbian command.','MSGA_prepared_for_war','supply_consumption_factor = -0.03',''),('operation_thunder','Operation Thunder','Staff planning supports the opening operation without granting a permanent attack bonus.','MSGA_prepared_for_war','planning_speed = 0.10 max_planning = 0.05 supply_consumption_factor = -0.05',''),('surprise_attack','Surprise Attack','The initial operational advantage lasts only ten days.','MSGA_surprise_attack','army_attack_factor = 0.05 army_speed_factor = 0.05 breakthrough_factor = 0.05','')]
 text=['ideas = { country = {']
 for stem,title,desc,picture,mod,rule in ideas:
  text += [f' MSGA_{stem} = {{ picture = {picture} removal_cost = -1 {rule} modifier = {{ {mod} }} }}']
  l('MSGA_'+stem,title);l('MSGA_'+stem+'_desc',desc)
 put('common/ideas/MSGA_encirclement_ideas.txt','\n'.join(text+['} }'])+'\n')
 l('MSGA_zagreb_tirana_pact','Zagreb–Tirana Pact')
 put('localisation/english/MSGA_encirclement_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items())+'\n')
 with zipfile.ZipFile(PACKAGE) as z:
  gfx=['spriteTypes = {']
  paths=[('GFX_MSGA_focus_'+f[0],f'gfx/interface/goals/MSGA_focus_{f[0]}.dds') for f in FOCUSES]
  paths += [('GFX_MSGA_event_'+event[0],f'gfx/event_pictures/MSGA_event_{event[0]}.dds') for event in EVENTS.values()]
  # The package's supplied spirit sprite and the engine's idea-picture alias use the same DDS.
  paths += [('GFX_MSGA_spirit_surprise_attack','gfx/interface/ideas/MSGA_spirit_surprise_attack.dds'),('GFX_idea_MSGA_surprise_attack','gfx/interface/ideas/MSGA_spirit_surprise_attack.dds')]
  for sprite,path in paths:
   member=next(n for n in z.namelist() if n.endswith('/'+path) or n==path)
   data=z.read(member);content[path]=data;assets[path]={'zip_member':member,'sha256':sha(data)}
   gfx += [f' spriteType = {{ name = "{sprite}" texturefile = "{path}" }}']
   if sprite.startswith('GFX_MSGA_focus_'):gfx += [f' spriteType = {{ name = "{sprite}_shine" texturefile = "{path}" }}']
  put('interface/MSGA_balkan_encirclement_assets.gfx','\n'.join(gfx+['}'])+'\n')
 for path in ['descriptor.mod','make_serbia_great_again.mod']:put(path,read(path).replace('version="0.10.0"','version="0.11.0"'))
 # Save a recoverable live backup before any installed file is overwritten.
 backup=ROOT/'logs/encirclement_011_backup';backup.mkdir(exist_ok=False)
 changed=[]
 for path,data in sorted(content.items()):
  target=LIVE/path;assert target.resolve().is_relative_to(LIVE)
  if target.exists():
   saved=backup/path;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,saved)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);changed.append(path)
 launcher=LIVE.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(LIVE/'make_serbia_great_again.mod',launcher)
 report={'version':'0.11.0','runtime':str(LIVE),'package':str(PACKAGE),'package_sha256':sha(PACKAGE.read_bytes()),'assets':assets,'native_guard_overrides':native,'changed_relative_paths':changed,'deployed_absolute_paths':[str(LIVE/p) for p in changed]+[str(launcher)],'spawn_locations':{tag:{'state':v[0],'province':v[1],'militia':v[2],'motorized':v[3]} for tag,v in MEMBERS.items()},'backup':str(backup),'gameplay_test':'reserved by user; no game window accessed'}
 (ROOT/'docs/encirclement_sources.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'Installed {len(changed)} files LIVE; 25 authorized DDS; no later-war content. Source sync follows validation.')
if __name__=='__main__':main()
