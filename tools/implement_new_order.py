"""One-time 0.13 migration: build the approved postwar chapter LIVE first."""
from pathlib import Path
import hashlib,io,json,shutil,zipfile
from PIL import Image
from validate_phase1 import parse,get
from implement_pact_war import ROOT,LIVE,TFR

PACKAGE=Path(r'C:\Users\Balazs\Downloads\MSGA_New_Balkan_Order_TFR_Assets (1).zip')
CLIENTS=[('CRO','croatia','Croatian Administration',7,'the_zagreb_accords'),('SLV','slovenia','Slovenian Administration',8,'the_ljubljana_protocol'),('MNT','montenegro','Montenegro',9,'the_podgorica_settlement'),('MAC','macedonia','Macedonian Administration',10,'the_skopje_agreement'),('ALB','albania','Albanian Administration',11,'the_tirana_arrangement'),('BOS','bosnia','Bosnian Administration',12,'the_sarajevo_framework'),('HRZ','herzegovina','Herzegovinian Administration',17,'the_sarajevo_framework'),('SRP','srpska','Republika Srpska',18,'question_of_republika_srpska')]
FOCUSES=[('count_the_cost','Count the Cost',4,0,1,[]),('begin_reconstruction','Begin Reconstruction',4,1,1,['count_the_cost']),('repair_the_roads_and_railways','Repair the Roads and Railways',0,2,2,['begin_reconstruction']),('restore_serbian_industry','Restore Serbian Industry',4,2,2,['begin_reconstruction']),('restart_serbian_commerce','Restart Serbian Commerce',8,2,2,['begin_reconstruction']),('stabilise_the_new_order','Stabilise the New Order',4,3,2,['repair_the_roads_and_railways','restore_serbian_industry','restart_serbian_commerce']),('the_south_slavic_question','The South Slavic Question',4,4,3,['stabilise_the_new_order']),('south_slavic_unity','South Slavic Unity',4,5,2,['the_south_slavic_question'])]
ECONOMIC=[f[0] for f in FOCUSES[2:5]]
STAGES=['MSGA_cost_of_victory_'+s for s in ['i','ii','iii','iv']]
STAGE_VALUES=[(.30,-.20,-.05,-.05,.10),(.20,-.15,-.03,-.03,.15),(.10,-.10,0,-.02,.10),(.05,-.05,0,0,.05)]
RAILS=[[619,3617,11580,11586],[9602,6634,11583,11586]]
EVENTS={
 1:('victory_in_the_balkan_war','Victory in the Balkan War','The last organised resistance of the Zagreb–Tirana Pact has ended. Governments that once gathered to contain Serbia now stand within Belgrade’s political orbit. From Ljubljana to Skopje and from Zagreb to Tirana, the regional balance has been rewritten.\n\nVictory has come at an extraordinary price. Mobilisation, emergency borrowing and the administration of defeated states have left Serbia with heavy debts and an exhausted civilian economy. Winning the war was only the beginning.','Now we must pay for victory.'),
 2:('the_bill_comes_due','The Bill Comes Due','The first complete financial assessment of the war has reached Belgrade. Emergency procurement, mobilisation, reconstruction loans and military logistics have created obligations far beyond pre-war expectations.\n\nThe military campaign has ended. The financial campaign is only beginning.','There was never going to be a cheap victory.'),
 3:('the_reconstruction_authority','The Reconstruction Authority','The government has established a central Reconstruction Authority to coordinate repairs to roads, railways, industrial facilities, power networks and public infrastructure.\n\nEvery ministry is demanding priority. Belgrade must rebuild the civilian economy while continuing to service the debts created by victory.','Rebuild what the war consumed.'),
 4:('the_arteries_of_serbia','The Arteries of Serbia','The principal road and rail corridors strained by mobilisation are returning to regular service. Freight is moving again, civilian traffic has resumed and the interior is being reconnected to Belgrade.\n\nReconstruction remains incomplete, but the arteries of the Serbian economy are beginning to function again.','Keep the trains moving.'),
 5:('the_furnaces_burn_again','The Furnaces Burn Again','Production lines that spent years supplying the war effort are being repaired and retooled. Serbian steel, machinery and manufacturing are beginning to recover from the strain of mobilisation.\n\nFactories that once supplied the front must now rebuild the country.','Put Serbia back to work.'),
 6:('belgrade_opens_for_business','Belgrade Opens for Business','Commercial banks, logistics companies, insurers and regional firms are returning to normal activity. Belgrade’s business districts are looking beyond the battlefield towards the wider Balkan market.\n\nThe scars of war remain, but Serbian commerce is moving again.','Open the doors.'),
 7:('the_zagreb_accords','The Zagreb Accords','Representatives of Belgrade and the Croatian administration have signed a permanent framework for security, foreign policy and administrative cooperation.\n\nCroatia retains its internal institutions. The independent regional policy that created the Zagreb–Tirana Pact has given way to coordination with Serbia.','Zagreb has found its place in the new order.'),
 8:('the_ljubljana_protocol','The Ljubljana Protocol','The Ljubljana Protocol places Slovenia’s external security and strategic coordination inside the Serbian regional framework. Local institutions retain responsibility for internal administration.\n\nEconomic connections will gradually replace the emergency structures of war.','Cooperation will replace occupation.'),
 9:('the_podgorica_settlement','The Podgorica Settlement','Belgrade and Podgorica have formalised the arrangements that followed Montenegro’s defeat. Local institutions continue to function, while foreign and security policy are coordinated with Serbia.\n\nThe emergency military relationship is becoming an established political one.','Podgorica returns to Belgrade’s orbit.'),
 10:('the_skopje_agreement','The Skopje Agreement','Skopje has accepted a permanent framework of security consultation, economic coordination and Serbian strategic leadership.\n\nNorth Macedonia remains a separate state, with its regional policy now firmly tied to Belgrade.','The Vardar now lies inside our sphere.'),
 11:('the_tirana_arrangement','The Tirana Arrangement','Relations with Albania remain the most difficult part of the new regional order. Belgrade has formalised a client relationship that leaves Albania’s administration and statehood intact.\n\nTirana’s defence and foreign policy operate within Serbian strategic limits. Kosovo remains Serbian; Albania remains outside the South Slavic political project.','Tirana will remain a separate client state.'),
 12:('the_sarajevo_framework','The Sarajevo Framework','The arrangements created after the Bosnian conflict have been incorporated into Serbia’s wider post-war system. Sarajevo’s relationship with Belgrade now rests on an administrative framework rather than emergency measures.\n\nThe existing Bosnian state retains its territory and institutions within the Serbian sphere.','Formalise what victory created.'),
 13:('the_conference_of_belgrade','The Conference of Belgrade','Representatives from every government in Serbia’s regional sphere have assembled in Belgrade. The administrative arrangements created by war have been formalised through separate agreements.\n\nTrade, defence and diplomatic coordination now rest on an established framework. Economic reconstruction must still be completed before the new order can be stabilised.','Order must replace occupation.'),
 14:('the_balkans_stabilise','The Balkans Stabilise','Railways run again, local administrations have established procedures and trade has resumed. The emergency structures of war are being dismantled.\n\nSerbia remains deeply indebted, but the immediate reconstruction crisis has passed. Belgrade can now look beyond recovery and consider what should come next.','Now we decide what victory means.'),
 15:('the_south_slavic_question_returns','The South Slavic Question Returns','For generations, the South Slavic peoples have been divided between competing states, ideologies and visions of unity. Earlier attempts to bring the region together ended in crisis and war.\n\nSerbia now occupies a position Belgrade has not held for decades. Cooperation with Zagreb, Ljubljana, Sarajevo, Podgorica and Skopje can take a new political form. Albania remains a separate Balkan client outside this discussion.','We must decide what comes next.'),
 16:('the_new_balkan_order','The New Balkan Order','The emergency order created by war has survived its first test. Serbia stands at the centre of a regional network stretching from Slovenia to North Macedonia, while the governments of the region coordinate their strategic direction with Belgrade.\n\nThe next question will be political. Serbia has opened the discussion of South Slavic unity; its eventual structure has yet to be decided.','The next chapter begins in Belgrade.'),
 17:('the_sarajevo_framework','The Herzegovinian Framework','Belgrade and the Herzegovinian administration have formalised the client relationship established by the Bosnian settlement. Mostar retains its local institutions within Serbia’s regional framework.\n\nHerzegovina remains separate from Bosnia wherever the earlier settlement preserved that arrangement.','Regularise the administration in Mostar.'),
 18:('question_of_republika_srpska','The Banja Luka Protocol','The Republika Srpska administration has accepted a permanent framework of consultation and administrative cooperation with Belgrade. Its preserved subject status remains intact.\n\nThis agreement regularises the separate client state. It makes no new territorial or constitutional union with Serbia.','Confirm the existing Srpska settlement.'),
}

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
 assert LIVE.resolve(strict=True)==LIVE.absolute()
 before={p.relative_to(LIVE).as_posix():sha(p.read_bytes()) for p in LIVE.rglob('*') if p.is_file()}
 assert before==json.loads((ROOT/'docs/pact_war_sync.json').read_text())['sha256'],'Unreviewed live edits'
 content={};loc={};assets={}
 def put(path,text):
  if path.endswith(('.txt','.gfx')):parse(text)
  content[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
 def l(key,value):assert key not in loc;loc[key]=value
 def read(path):return (LIVE/path).read_text(encoding='utf-8-sig')
 economy_complete=' '.join('has_country_flag = MSGA_completed_'+f for f in ECONOMIC)
 subject_gate=' '.join(f'OR = {{ NOT = {{ {tag} = {{ exists = yes is_subject_of = SER }} }} has_country_flag = MSGA_{stem}_regularised }}' for tag,stem,*_ in CLIENTS)
 triggers=f'''MSGA_new_order_victory_ready = {{ tag = SER has_war = no has_country_flag = MSGA_balkan_coalition_defeated MSGA_pact_all_five_subjects = yes NOT = {{ has_country_flag = MSGA_balkan_war_victory }} }}
MSGA_new_order_clients_regularised = {{ {subject_gate} }}
MSGA_regularisation_free = {{ NOT = {{ has_country_flag = MSGA_regularisation_active }} }}
MSGA_belgrade_conference_ready = {{ tag = SER has_war = no has_country_flag = MSGA_balkan_war_victory has_country_flag = MSGA_completed_begin_reconstruction MSGA_new_order_clients_regularised = yes NOT = {{ has_country_flag = MSGA_serbian_sphere_regularised }} }}
MSGA_new_order_stabilisation_ready = {{ tag = SER has_war = no has_country_flag = MSGA_balkan_war_victory {economy_complete} MSGA_new_order_clients_regularised = yes has_country_flag = MSGA_serbian_sphere_regularised }}
'''
 put('common/scripted_triggers/MSGA_new_order_triggers.txt',triggers)
 effects=['# Entry is deferred until actual five-puppet victory AND Serbian peace.',
 '''MSGA_schedule_new_order_victory = {
 if = { limit = { MSGA_new_order_victory_ready = yes }
  if = { limit = { NOT = { has_country_flag = MSGA_new_order_peace_ready } }
   set_country_flag = MSGA_new_order_peace_ready
   if = { limit = { NOT = { has_country_flag = MSGA_new_order_victory_pending } } set_country_flag = { flag = MSGA_new_order_victory_pending days = 4 } country_event = { id = MSGA_neworder.90 days = 3 } }
  }
  else_if = { limit = { NOT = { has_country_flag = MSGA_new_order_victory_pending } } set_country_flag = { flag = MSGA_new_order_victory_pending days = 4 } country_event = { id = MSGA_neworder.90 days = 1 } }
 }
 else_if = { limit = { tag = SER has_war = yes } clr_country_flag = MSGA_new_order_peace_ready }
}
MSGA_start_new_balkan_order = {
 if = { limit = { MSGA_new_order_victory_ready = yes has_country_flag = { flag = MSGA_new_order_peace_ready days > 2 } }
  set_country_flag = MSGA_balkan_war_victory set_country_flag = MSGA_new_balkan_order_active
  clr_country_flag = MSGA_pact_planning_active clr_country_flag = MSGA_southern_question_active clr_country_flag = MSGA_new_order_victory_pending
  add_stability = 0.10 add_political_power = 100
  # Exact nominal billions: no inflation multiplier and no treasury subtraction.
  set_temp_variable = { var = debt_var_temp value = 15 } add_debt = yes
  set_variable = { var = MSGA_reconstruction_progress value = 0 }
  remove_ideas = MSGA_surprise_attack remove_ideas = MSGA_operation_thunder remove_ideas = MSGA_western_preparation remove_ideas = MSGA_southern_preparation remove_ideas = MSGA_encirclement_reserves remove_ideas = MSGA_pact_logistics_cooperation
  MSGA_refresh_new_order_reconstruction = yes
  load_focus_tree = { tree = MSGA_SER_new_balkan_order keep_completed = yes }
 }
}
MSGA_refresh_new_order_reconstruction = {
 if = { limit = { tag = SER has_country_flag = MSGA_balkan_war_victory }
  # Derive the bounded counter from permanent completion flags. Any order is valid.
  set_variable = { var = MSGA_reconstruction_progress value = 0 }''']
 for f in ECONOMIC:effects += [f'  if = {{ limit = {{ has_country_flag = MSGA_completed_{f} }} add_to_variable = {{ var = MSGA_reconstruction_progress value = 1 }} }}']
 effects += ['  '+' '.join('remove_ideas = '+s for s in STAGES), '  if = { limit = { NOT = { has_country_flag = MSGA_new_balkan_order_stabilised } }']
 for i,stage in [(3,STAGES[3]),(2,STAGES[2]),(1,STAGES[1])]:
  effects += [f'   {"if" if i==3 else "else_if"} = {{ limit = {{ check_variable = {{ var = MSGA_reconstruction_progress value = {i} compare = greater_than_or_equals }} }} add_ideas = {stage} }}']
 effects += [f'   else = {{ add_ideas = {STAGES[0]} }}','  }',' }','}',
 '''MSGA_schedule_belgrade_conference = {
 if = { limit = { MSGA_belgrade_conference_ready = yes NOT = { has_country_flag = MSGA_belgrade_conference_pending } }
  set_country_flag = { flag = MSGA_belgrade_conference_pending days = 3 } country_event = { id = MSGA_neworder.91 days = 2 }
 }
}
MSGA_hold_belgrade_conference = {
 if = { limit = { MSGA_belgrade_conference_ready = yes }
  set_country_flag = MSGA_serbian_sphere_regularised add_stability = 0.05 add_political_power = 50
 }
}
MSGA_resume_new_order = {
 if = { limit = { tag = SER }
  MSGA_schedule_new_order_victory = yes
  if = { limit = { has_country_flag = MSGA_balkan_war_victory NOT = { has_country_flag = MSGA_south_slavic_unity_open } }
   if = { limit = { NOT = { has_country_flag = MSGA_new_balkan_order_active } } set_country_flag = MSGA_new_balkan_order_active clr_country_flag = MSGA_pact_planning_active load_focus_tree = { tree = MSGA_SER_new_balkan_order keep_completed = yes } }
   MSGA_refresh_new_order_reconstruction = yes MSGA_schedule_belgrade_conference = yes
   if = { limit = { has_country_flag = MSGA_completed_the_south_slavic_question NOT = { has_country_flag = MSGA_south_slavic_question_opened } } country_event = { id = MSGA_neworder.15 } }
  }
 }
}''']
 for f,title,x,y,cost,parents in FOCUSES:
  # Flags/rewards are set inside these guards, not before calling them from the focus.
  available='MSGA_new_order_stabilisation_ready = yes' if f=='stabilise_the_new_order' else 'has_country_flag = MSGA_south_slavic_question_opened' if f=='south_slavic_unity' else 'has_country_flag = MSGA_new_balkan_order_stabilised' if f=='the_south_slavic_question' else 'has_country_flag = MSGA_balkan_war_victory'
  effects += [f'MSGA_new_order_{f} = {{',f' if = {{ limit = {{ tag = SER {available} NOT = {{ has_country_flag = MSGA_completed_{f} }} }} set_country_flag = MSGA_completed_{f}']
  if f=='count_the_cost':effects += ['  add_political_power = 25 country_event = { id = MSGA_neworder.2 }']
  if f=='begin_reconstruction':effects += ['  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes add_timed_idea = { idea = MSGA_reconstruction_authority days = 120 }','  country_event = { id = MSGA_neworder.3 } MSGA_schedule_belgrade_conference = yes']
  if f in ECONOMIC:
   effects += ['  set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes']
   if f==ECONOMIC[0]:
    for state in [45,107,1296]:effects += [f'  {state} = {{ if = {{ limit = {{ is_owned_by = SER is_fully_controlled_by = SER infrastructure < 5 }} add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }} }}']
    for state,path in zip([45,1296],RAILS):effects += [f'  if = {{ limit = {{ {state} = {{ is_owned_by = SER is_fully_controlled_by = SER }} 107 = {{ is_owned_by = SER is_fully_controlled_by = SER }} }} build_railway = {{ level = 3 build_only_on_allied = yes path = {{ '+ ' '.join(map(str,path))+' } } }']
   if f in ECONOMIC[1:]:
    buildings=['industrial_complex','arms_factory'] if f==ECONOMIC[1] else ['office_park']
    reward=f'add_extra_state_shared_building_slots = {len(buildings)} '+' '.join(f'add_building_construction = {{ type = {b} level = 1 instant_build = yes }}' for b in buildings)
    effects += [f'  if = {{ limit = {{ 107 = {{ is_owned_by = SER is_fully_controlled_by = SER }} }} 107 = {{ {reward} }} }}',f'  else = {{ random_owned_controlled_state = {{ {reward} }} }}']
    if f==ECONOMIC[2]:effects += ['  add_ideas = MSGA_serbian_commerce_restored']
   effects += [f'  MSGA_refresh_new_order_reconstruction = yes country_event = {{ id = MSGA_neworder.{4+ECONOMIC.index(f)} }}']
  if f=='stabilise_the_new_order':
   effects += ['  set_country_flag = MSGA_new_balkan_order_stabilised','  '+' '.join('remove_ideas = '+s for s in STAGES),'  remove_ideas = MSGA_reconstruction_authority add_ideas = MSGA_a_stabilised_balkan_order',
    '  # This autonomy modifier belongs on the SUBJECT, not on independent Serbia.',
    '  every_subject_country = { limit = { OR = { '+' '.join('tag = '+tag for tag,*_ in CLIENTS)+' } } add_ideas = MSGA_stabilised_client_order }', '  country_event = { id = MSGA_neworder.14 }']
  if f=='the_south_slavic_question':effects += ['  country_event = { id = MSGA_neworder.15 }']
  if f=='south_slavic_unity':effects += ['  add_stability = 0.05 add_political_power = 50 set_country_flag = MSGA_south_slavic_unity_open country_event = { id = MSGA_neworder.16 }']
  effects += [' }','}']
 effects += ['MSGA_open_south_slavic_question = {',' if = { limit = { tag = SER has_country_flag = MSGA_completed_the_south_slavic_question has_country_flag = MSGA_new_balkan_order_stabilised NOT = { has_country_flag = MSGA_south_slavic_question_opened } }','  set_country_flag = MSGA_south_slavic_question_opened add_political_power = 50']
 for tag,*_ in CLIENTS:
  if tag!='ALB':effects += [f'  {tag} = {{ if = {{ limit = {{ exists = yes is_subject_of = SER }} set_country_flag = MSGA_south_slavic_question_participant }} }}']
 effects += [' }','}']
 # Native timed decisions own the 10-day jobs. Eleven-day fallback leases
 # outlive the completion tick; callbacks release them immediately on day ten.
 # a matching per-country lease prevents an old callback unlocking a newer job.
 decisions=['MSGA_consolidate_the_serbian_sphere = {']
 for tag,stem,title,event,image in CLIENTS:
  flag=f'MSGA_{stem}_regularised';lease=f'MSGA_regularising_{stem}';id=f'MSGA_regularise_{stem}'
  eligible=f'{tag} = {{ exists = yes is_subject_of = SER }} NOT = {{ has_country_flag = {flag} }}'
  effects += [f'MSGA_finish_regularising_{stem} = {{',f' if = {{ limit = {{ tag = SER has_country_flag = MSGA_balkan_war_victory {eligible} }}',f'  {tag} = {{ add_stability = 0.10 add_opinion_modifier = {{ target = SER modifier = MSGA_new_order_cooperation }} add_autonomy_score = {{ value = -50 localization = MSGA_regularisation_autonomy_tt }}']
  if tag in ['CRO','SLV','MNT','MAC','ALB']:effects += [f'   remove_ideas = MSGA_{stem}_postwar_recovery']
  effects += ['  }',f'  set_country_flag = {flag} country_event = {{ id = MSGA_neworder.{event} }}',' }',f' MSGA_release_regularisation_{stem} = yes MSGA_schedule_belgrade_conference = yes','}',
   f'MSGA_release_regularisation_{stem} = {{ if = {{ limit = {{ has_country_flag = {lease} }} clr_country_flag = MSGA_regularisation_active clr_country_flag = {lease} }} }}']
  decisions += [f' {id} = {{ icon = GFX_MSGA_decision_consolidate_the_serbian_sphere allowed = {{ tag = SER }}',f'  visible = {{ has_country_flag = MSGA_completed_begin_reconstruction {eligible} }}',f'  available = {{ has_country_flag = MSGA_balkan_war_victory MSGA_regularisation_free = yes {eligible} }}',
   '  cost = 25 days_remove = 10',
   f'  complete_effect = {{ set_country_flag = {{ flag = MSGA_regularisation_active days = 11 }} set_country_flag = {{ flag = {lease} days = 11 }} custom_effect_tooltip = MSGA_regularisation_duration_tt }}',
   f'  cancel_trigger = {{ NOT = {{ {tag} = {{ exists = yes is_subject_of = SER }} }} }} cancel_effect = {{ MSGA_release_regularisation_{stem} = yes MSGA_schedule_belgrade_conference = yes }}',
   f'  remove_effect = {{ MSGA_finish_regularising_{stem} = yes }} ai_will_do = {{ factor = 10 }}',' }']
  name='Regularise '+('the '+title if tag not in ['MNT','SRP'] else title)
  l(id,name);l(id+'_desc',f'Negotiate an administrative framework with {title}. Cost: 25 Political Power. Duration: 10 days. Only one client-state process can run at a time. The country remains a Serbian subject. Completion grants it 10% stability, +25 opinion of Serbia and a modest 50-point autonomy-progress reduction. If the client ceases to exist or leaves Serbian protection, the process is cancelled without rewards or a completion flag.')
 put('common/scripted_effects/MSGA_new_order_effects.txt','\n'.join(effects)+'\n')
 put('common/decisions/MSGA_new_order_decisions.txt','\n'.join(decisions+['}'])+'\n')
 category='''
MSGA_consolidate_the_serbian_sphere = {
 icon = GFX_decision_category_MSGA_consolidate_the_serbian_sphere allowed = { tag = SER }
 visible = { has_country_flag = MSGA_balkan_war_victory has_country_flag = MSGA_completed_begin_reconstruction NOT = { has_country_flag = MSGA_south_slavic_unity_open } }
 priority = 18
}
'''
 put('common/decisions/categories/MSGA_SER_categories.txt',read('common/decisions/categories/MSGA_SER_categories.txt')+category)
 l('MSGA_consolidate_the_serbian_sphere','Consolidate the Serbian Sphere');l('MSGA_consolidate_the_serbian_sphere_desc','Military victory alone cannot create a permanent regional order. Each surviving Balkan client administration must formalise its relationship with Belgrade. Each process costs 25 PP and takes 10 days; only one can run at a time. Existing country borders and subject status are preserved.')
 l('MSGA_regularisation_duration_tt','Administrative negotiations take §Y10 days§!. Other client-state decisions remain unavailable until this process ends.');l('MSGA_regularisation_autonomy_tt','Administrative consolidation');l('MSGA_stabilised_subjects_tt','Relevant Balkan subjects: §G−10%§! autonomy gain. Applied to each subject administration.')
 put('common/opinion_modifiers/MSGA_new_order_opinions.txt','opinion_modifiers = { MSGA_new_order_cooperation = { value = 25 } }\n')
 ideas=['ideas = { country = {']
 for i,(cg,construction,output,income,repair) in enumerate(STAGE_VALUES):
  suffix=['','_ii','_iii','_iv'][i];name='The Cost of Victory'+['',' II',' III',' IV'][i]
  mods=f'consumer_goods_factor = {cg:.2f} production_speed_buildings_factor = {construction:.2f} industrial_capacity_factory = {output:.2f} income_growth_factor = {income:.2f} industry_repair_factor = {repair:.2f}'
  ideas += [f' {STAGES[i]} = {{ picture = MSGA_the_cost_of_victory{suffix} allowed = {{ tag = SER }} removal_cost = -1 modifier = {{ {mods} }} }}']
  l(STAGES[i],name);l(STAGES[i]+'_desc',f'The post-war economy carries the cost of victory. Recovery stage {i+1} of 4. Reconstruction gradually removes the emergency penalties; the additional $15 billion national debt remains.')
 for key,picture,title,mods,extra,desc in [
  ('MSGA_a_stabilised_balkan_order','MSGA_a_stabilised_balkan_order','A Stabilised Balkan Order','stability_factor = 0.05 political_power_factor = 0.05 income_growth_factor = 0.02 custom_modifier_tooltip = MSGA_stabilised_subjects_tt','allowed = { tag = SER }','A functioning Serbian regional framework supports stability, political administration and monthly income growth. Its Balkan client administrations receive a modest autonomy-gain penalty. National debt is unchanged.'),
  ('MSGA_serbian_commerce_restored','MSGA_a_stabilised_balkan_order','Serbian Commerce Restored','business_value_factor = 0.05 income_growth_factor = 0.03','allowed = { tag = SER }','Commercial activity returns to normal operation. Native TFR Business Value increases by 5% and Monthly Income Growth by 3%.'),
  ('MSGA_reconstruction_authority','MSGA_the_cost_of_victory_ii','Reconstruction Authority','industry_repair_factor = 0.10','allowed = { tag = SER }','A temporary 120-day programme coordinates industrial repair. It ends early when the new order is stabilised.'),
  ('MSGA_stabilised_client_order','MSGA_a_stabilised_balkan_order','A Stabilised Client Administration','autonomy_gain_global_factor = -0.10','allowed = { is_subject_of = SER } cancel = { NOT = { is_subject_of = SER } }','The established administrative framework reduces this Balkan subject’s autonomy gain by 10%. It ends if the country ceases to be a Serbian subject.')]:
  ideas += [f' {key} = {{ picture = {picture} {extra} removal_cost = -1 modifier = {{ {mods} }} }}'];l(key,title);l(key+'_desc',desc)
 put('common/ideas/MSGA_new_order_ideas.txt','\n'.join(ideas+['} }'])+'\n')
 tree=['focus_tree = { id = MSGA_SER_new_balkan_order country = { factor = 0 modifier = { add = 300 tag = SER has_country_flag = MSGA_new_balkan_order_active } } default = no reset_on_civilwar = no']
 for f,title,x,y,cost,parents in FOCUSES:
  available='MSGA_new_order_stabilisation_ready = yes' if f=='stabilise_the_new_order' else 'has_country_flag = MSGA_south_slavic_question_opened' if f=='south_slavic_unity' else 'has_country_flag = MSGA_new_balkan_order_stabilised' if f=='the_south_slavic_question' else 'has_country_flag = MSGA_balkan_war_victory'
  tree += [f' focus = {{ id = MSGA_{f} icon = GFX_MSGA_focus_{f} x = {x} y = {y} cost = {cost}']+[f'  prerequisite = {{ focus = MSGA_{parent} }}' for parent in parents]+[f'  available = {{ {available} }} completion_reward = {{ MSGA_new_order_{f} = yes }} ai_will_do = {{ factor = 10 }}',' }']
  descriptions={'count_the_cost':'Assess the cost of victory. The additional $15 billion national debt was charged by the victory event and is not charged again.','begin_reconstruction':'Add five percentage points to native TFR industrial-development progress, establish a temporary repair authority and open the parallel client-state decisions.','repair_the_roads_and_railways':'Restore capped infrastructure in Vojvodina, Belgrade and Sumadija and raise two verified Serbian railway corridors to at least level three. Add five points to TFR industrial-development progress.','restore_serbian_industry':'Add one civilian and one military factory to controlled Serbia, with the required building slots, and five points to TFR industrial-development progress.','restart_serbian_commerce':'Restore native TFR Business Value and Monthly Income Growth, add an Office Park and five points to industrial-development progress.','stabilise_the_new_order':'Complete all three economic programmes and regularise every current Balkan subject. After the Conference of Belgrade, stabilise at peace and remove all Cost of Victory stages. Debt remains.','the_south_slavic_question':'Open the political discussion among the South Slavic administrations around Serbia. Albania remains a separate Balkan client outside this project. No territorial integration occurs.','south_slavic_unity':'Open the gateway to a future political chapter. The eventual structure remains undecided; this focus changes no borders, country tags or subject status.'}
  l('MSGA_'+f,title);l('MSGA_'+f+'_desc',descriptions[f])
 put('common/national_focus/MSGA_SER_new_balkan_order.txt','\n'.join(tree+['}'])+'\n')
 events=['add_namespace = MSGA_neworder']
 for id,(image,title,desc,option) in EVENTS.items():
  condition={1:'MSGA_new_order_victory_ready = yes has_country_flag = { flag = MSGA_new_order_peace_ready days > 2 }',2:'has_country_flag = MSGA_completed_count_the_cost',3:'has_country_flag = MSGA_completed_begin_reconstruction',4:'has_country_flag = MSGA_completed_repair_the_roads_and_railways',5:'has_country_flag = MSGA_completed_restore_serbian_industry',6:'has_country_flag = MSGA_completed_restart_serbian_commerce',13:'MSGA_belgrade_conference_ready = yes',14:'has_country_flag = MSGA_new_balkan_order_stabilised',15:'has_country_flag = MSGA_completed_the_south_slavic_question NOT = { has_country_flag = MSGA_south_slavic_question_opened }',16:'has_country_flag = MSGA_south_slavic_unity_open'}.get(id)
  if condition is None:condition='has_country_flag = MSGA_'+next(c[1] for c in CLIENTS if c[3]==id)+'_regularised'
  reward={1:'MSGA_start_new_balkan_order = yes',13:'MSGA_hold_belgrade_conference = yes',15:'MSGA_open_south_slavic_question = yes'}.get(id,'')
  events += [f'country_event = {{ id = MSGA_neworder.{id} title = MSGA_neworder.{id}.t desc = MSGA_neworder.{id}.d picture = GFX_MSGA_event_{image} is_triggered_only = yes fire_only_once = yes trigger = {{ tag = SER {condition} }} immediate = {{ {reward} }} option = {{ name = MSGA_neworder.{id}.a }} }}']
  for suffix,value in [('t',title),('d',desc),('a',option)]:l(f'MSGA_neworder.{id}.{suffix}',value)
 events += ['''country_event = { id = MSGA_neworder.90 hidden = yes is_triggered_only = yes
 immediate = { clr_country_flag = MSGA_new_order_victory_pending
  if = { limit = { MSGA_new_order_victory_ready = yes has_country_flag = { flag = MSGA_new_order_peace_ready days > 2 } } country_event = { id = MSGA_neworder.1 } }
  else = { MSGA_schedule_new_order_victory = yes }
 }
}
country_event = { id = MSGA_neworder.91 hidden = yes is_triggered_only = yes
 immediate = { clr_country_flag = MSGA_belgrade_conference_pending if = { limit = { MSGA_belgrade_conference_ready = yes } country_event = { id = MSGA_neworder.13 } } }
}''']
 put('events/MSGA_new_order_events.txt','\n'.join(events)+'\n')
 put('common/on_actions/MSGA_new_order_on_actions.txt','''on_actions = {
 on_startup = { effect = { SER = { MSGA_resume_new_order = yes } } }
 on_weekly = { effect = { if = { limit = { tag = SER } MSGA_resume_new_order = yes } } }
 on_peace = { effect = { SER = { MSGA_schedule_new_order_victory = yes MSGA_schedule_belgrade_conference = yes } } }
 on_war = { effect = { if = { limit = { OR = { ROOT = { tag = SER } FROM = { tag = SER } } } SER = { clr_country_flag = MSGA_new_order_peace_ready } } } }
}
''')
 path='common/scripted_effects/MSGA_pact_war_effects.txt';text=read(path);needle='country_event = { id = MSGA_pactwar.11 }';assert text.count(needle)==1
 put(path,text.replace(needle,needle+'\n  MSGA_schedule_new_order_victory = yes'))
 path='common/scripted_effects/MSGA_encirclement_effects.txt';text=read(path)
 needle='has_country_flag = MSGA_belgrade_emergency_done NOT = { has_country_flag = MSGA_pact_planning_active }'
 assert text.count(needle)==1
 put(path,text.replace(needle,needle+' NOT = { has_country_flag = MSGA_balkan_war_victory }'))
 # Keep supplied base definitions byte-identical, adding only engine aliases.
 with zipfile.ZipFile(PACKAGE) as z:
  member=next(n for n in z.namelist() if n.endswith('/interface/MSGA_new_balkan_order_assets.gfx'))
  content['interface/MSGA_new_balkan_order_assets.gfx']=z.read(member);parse(z.read(member).decode('utf-8-sig'))
  for member in z.namelist():
   if member.endswith('.dds') and '/gfx/' in member:
    path='gfx/'+member.split('/gfx/',1)[1];data=z.read(member);content[path]=data
    assets[path]={'zip_member':member,'sha256':sha(data),'size':list(Image.open(io.BytesIO(data)).size)}
 aliases=['spriteTypes = {']
 for f,*_ in FOCUSES:aliases += [f' spriteType = {{ name = "GFX_MSGA_focus_{f}_shine" texturefile = "gfx/interface/goals/MSGA_focus_{f}.dds" }}']
 for stem in ['the_cost_of_victory','the_cost_of_victory_ii','the_cost_of_victory_iii','the_cost_of_victory_iv','a_stabilised_balkan_order']:
  aliases += [f' spriteType = {{ name = "GFX_idea_MSGA_{stem}" texturefile = "gfx/interface/ideas/MSGA_idea_{stem}.dds" }}']
 aliases += [' spriteType = { name = "GFX_decision_category_MSGA_consolidate_the_serbian_sphere" texturefile = "gfx/interface/ideas/MSGA_decision_consolidate_the_serbian_sphere.dds" }','}']
 put('interface/MSGA_new_order_engine_aliases.gfx','\n'.join(aliases)+'\n')
 assert len(assets)==30
 # JSON escaping is decoded to HOI4's literal newline escapes without changing quotes.
 put('localisation/english/MSGA_new_order_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items())+'\n')
 for path in ['descriptor.mod','make_serbia_great_again.mod']:
  assert 'version="0.12.0"' in read(path);put(path,read(path).replace('version="0.12.0"','version="0.13.0"'))
 backup=ROOT/'logs/new_order_013_backup';backup.mkdir(exist_ok=False)
 for path,data in sorted(content.items()):
  target=LIVE/path;assert target.resolve().is_relative_to(LIVE)
  if target.exists():saved=backup/path;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,saved)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 launcher=LIVE.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(LIVE/'make_serbia_great_again.mod',launcher)
 native_paths=['common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt','common/modifier_definitions/00_TFR_economic_modifiers_definition.txt','common/autonomous_states/puppet.txt','map/railways.txt']
 record={'version':'0.13.0','runtime':str(LIVE),'package':str(PACKAGE),'package_sha256':sha(PACKAGE.read_bytes()),'assets':assets,'changed_relative_paths':sorted(content),'deployed_absolute_paths':[str(LIVE/p) for p in sorted(content)]+[str(launcher)],'baseline_sha256':before,'native_sources_sha256':{p:sha((TFR/p).read_bytes()) for p in native_paths},'infrastructure_states':{'45':'Vojvodina','107':'Belgrade','1296':'Sumadija'},'railway_paths':RAILS,'backup':str(backup),'engine_test':'Reserved by user; game window untouched'}
 (ROOT/'docs/new_order_sources.json').write_text(json.dumps(record,indent=2)+'\n')
 print(f'Installed {len(content)} files LIVE 0.13.0, including 30 supplied DDS. Validate before source sync.')

if __name__=='__main__':main()
