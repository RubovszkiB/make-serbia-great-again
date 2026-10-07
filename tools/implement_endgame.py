"""Author the approved endgame into LIVE first. Validate before source sync.

The archive supplies artwork only. Native TFR states, debt and annexation APIs
are authoritative. Never run archive instructions, edit TFR or touch saves.
"""
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
import argparse, hashlib, io, json, re, shutil
from PIL import Image, ImageOps, ImageDraw, ImageEnhance
from validate_phase1 import parse, get

ROOT=Path(__file__).resolve().parents[1]
LIVE=Path(r'C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again')
SOURCE=ROOT/'make_serbia_great_again'
TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
PACK=Path(r'C:\Users\Balazs\Downloads\MSGA_Endgame_Visuals_SourcePack_v1 (1).zip')
STATES={'MNT':[105],'MAC':[106],'CRO':[103,109,1306,163,736],'SLV':[102,900],'BOS':[104,848,849,850],'HRZ':[851],'SER':[45,107,108,1296,785,1305,848,849,850]}
ALL_FEDERAL=sorted(set(sum(STATES.values(),[])))
LOC={};FILES={};ASSETS={};EFFECTS=[];TRIGGERS=[];EVENTS=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def loc(key,text):
 assert key not in LOC,key
 LOC[key]=text
def put(path,text):
 parse(text) if not path.endswith('.yml') else None
 FILES[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
def flag(stem):return 'MSGA_eg_'+stem+'_done'
def pending(stem):return 'MSGA_eg_'+stem+'_pending'
def completed(stem):return 'has_country_flag = MSGA_eg_focus_'+stem
def debt(value):
 # Obligations is ONLY a one-shot story threshold; native debt_var is the debt.
 return f'set_temp_variable = {{ var = debt_var_temp value = {value:g} }} add_debt = yes add_to_variable = {{ var = MSGA_endgame_integration_obligations value = {value:g} }}'
def effect(name,body):EFFECTS.append(f'{name} = {{\n {body}\n}}')
def trigger(name,body):TRIGGERS.append(f'{name} = {{\n {body}\n}}')
def scope_states(states,body,owners='SER'):
 return '\n'.join(f'{s} = {{ if = {{ limit = {{ is_owned_by = {owners} is_fully_controlled_by = {owners} }} {body} }} }}' for s in states)
def improve(tag,amount=10):
 states=STATES[tag];owner=tag
 return scope_states(states,f'add_compliance = {amount} add_resistance = -5',owner)+f'\n{tag} = {{ add_autonomy_score = {{ value = -50 localization = MSGA_eg_autonomy_tt }} add_timed_idea = {{ idea = MSGA_endgame_reconciliation days = 365 }} }}'
def infra(state,owner='SER'):
 return scope_states([state],'if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }',owner)
def building(state,kind,owner='SER'):
 # Use the previous native before/after delivery pattern. No blind success claim.
 return scope_states([state],f'''if = {{ limit = {{ {kind} < 20 }}
 set_temp_variable = {{ var = MSGA_eg_before value = building_level@{kind} }}
 add_extra_state_shared_building_slots = 1
 add_building_construction = {{ type = {kind} level = 1 instant_build = yes }}
 set_temp_variable = {{ var = MSGA_eg_after value = building_level@{kind} }}
 if = {{ limit = {{ check_variable = {{ var = MSGA_eg_after value = MSGA_eg_before compare = greater_than }} }} log = "[MSGA ENDGAME] {kind} granted in state {state}" }}
 else = {{ add_extra_state_shared_building_slots = -1 log = "[MSGA ENDGAME] native {kind} grant rejected in state {state}" }}
 }}''',owner)
def cleanup(tag):
 recovery=f'remove_ideas = MSGA_{dict(MNT="montenegro",MAC="macedonia",CRO="croatia",SLV="slovenia")[tag]}_postwar_recovery' if tag in ['MNT','MAC','CRO','SLV'] else ''
 guarantee='remove_ideas = MSGA_slovenian_federal_guarantee' if tag=='SLV' else ''
 return f'{tag} = {{ remove_ideas = MSGA_endgame_reconciliation remove_ideas = MSGA_bound_protectorate remove_ideas = MSGA_integrated_protectorate remove_ideas = MSGA_stabilised_client_order remove_ideas = MSGA_campaign_isolation {recovery} {guarantee} }}'
def annex(tag,states=None):
 states=states or STATES[tag]
 return f'''if = {{ limit = {{ country_exists = {tag} }} {cleanup(tag)} annex_country = {{ target = {tag} transfer_troops = yes }} }}
 '''+scope_states(states,'if = { limit = { NOT = { is_core_of = SER } } add_core_of = SER }')
STORIES={
 'The Serbian Century':('Belgrade has chosen a Serbian national project after the defeat of the Zagreb–Tirana Pact. The government will negotiate direct integration with Montenegro and Macedonia while retaining Croatia, Slovenia, Albania and the other protected administrations as separate states.','The campaign begins with a temporary programme of political mobilisation, industrial coordination and administrative confidence. The existing leader remains in office. Kosovo and the already annexed Republika Srpska form part of Serbia; no new Srpska annexation process is opened.'),
 'Belgrade and Podgorica Open Union Talks':('Representatives from Belgrade and Podgorica have opened negotiations over a common state. The first agreements concern public administration, security responsibilities and the status of local services during the transition.','Union will require separate administrative and military agreements before Montenegro can be integrated. The talks improve confidence and reduce dependence on the remaining protectorate institutions. Montenegro continues to exist until the final timed agreement is completed.'),
 'The Montenegrin Army Takes the Serbian Oath':('The Montenegrin command has accepted a common military chain of responsibility. Training and staff procedures will be coordinated with Belgrade, and the existing formations will retain their identity within the enlarged force.','The political oath prepares integration rather than creating new units. At the final union, the native annexation system will transfer the surviving army and its stockpile. The same formations will not be spawned a second time.'),
 'Montenegro Joins Serbia':('The final union agreement has entered into force. Montenegro’s administration and surviving armed forces have been integrated with Serbia, and its native territory is recognised as part of the common state.','Podgorica receives an industrial expansion through the native building system. The government celebrates a completed political settlement with renewed stability and public confidence. The integration chain is closed, so its rewards and borrowing cannot be collected again.'),
 'Belgrade Arrives in Skopje':('The Vardar administration has opened in Skopje. Serbian and Macedonian officials are coordinating public services and security while the country remains a separate protected state during negotiations.','Confidence in the southern programme improves, but the economic and military agreements still lie ahead. A lasting integration must connect transport, support local industry and reconcile the command structures before the final territorial union.'),
 "Skopje's Security Apparatus Answers to Belgrade":('Skopje’s security institutions have accepted a common framework under Belgrade’s strategic authority. Local officials will retain their administrative knowledge while sharing intelligence and coordinating public order.','The agreement reduces resistance to the transition and improves stability. It does not itself annex Macedonia. The army still requires its own command agreement before the final integration decision can complete the Vardar programme.'),
 'One Southern Command':('The Macedonian military has agreed to place strategic command under Belgrade. Common staff work and training now connect the Vardar formations to the wider Serbian defence system.','The surviving army and equipment remain intact. Their transfer is reserved for the final native integration, avoiding duplicate formations or stockpiles. Staff experience gained through the agreement will support the eventual unified command.'),
 'The Vardar Is Integrated':('Macedonia’s complete administrative, economic, security and military programme has finished. The Vardar territory and its surviving forces now form part of Serbia under the final union agreement.','Skopje receives a military-industrial expansion through the native building system. Stability and war support rise as the government presents the southern integration as a lasting settlement. Montenegro and Macedonia can now be consolidated within the Greater Serbian State.'),
 'The Serbian Question Settled':('The Montenegro and Macedonia programmes have reached their conclusion. Serbia now combines its existing lands, Kosovo and the previously annexed Republika Srpska with the two newly integrated territories.','Temporary project institutions give way to a unified Serbian administration. The government can now proclaim the formal identity of the Greater Serbian State, while the remaining Balkan protectorates continue to exist outside its borders.'),
 'The Yugoslav Idea':('Belgrade has chosen a constitutional Yugoslav project. Serbia will negotiate with Croatia, Slovenia, Bosnia and Herzegovina, Montenegro and Macedonia to create six constituent republics within a common state.','Local legislatures, cultural administration and negotiated economic guarantees will coexist with federal defence and foreign policy. The existing leader remains in office. This is a modern political settlement without socialist institutions; Albania remains a separate client beyond the federation.'),
 'Ljubljana Accepts the Federation':('Ljubljana has accepted constituent republic status after receiving guarantees of economic autonomy. Slovenian institutions will participate in a common market while retaining a meaningful role in local economic administration.','The agreement records Slovenia as ready for the constitutional conference. It does not yet annex the republic: all five partner administrations must be prepared, and the federal constitution must be ratified before the final proclamation.'),
 'Montenegro Chooses Yugoslavia':('Podgorica has accepted the Yugoslav project after negotiations over Montenegrin statehood. Montenegro will enter the common state as a constituent republic, rather than first being annexed through the Serbian national integration route.','The republic is now ready for the constitutional settlement. Its existing army and equipment will transfer once, during the final federal proclamation. Local identity and administration will remain recognised within the common constitutional framework.'),
 'Skopje Accepts the Yugoslav Project':('Skopje’s delegates have accepted a federal settlement that guarantees Macedonian identity and republic status. The agreement recognises local cultural and administrative institutions alongside common defence and foreign policy.','Macedonia is now ready for the federal constitution. It remains a separate protected administration until the joint proclamation, when the surviving armed forces and equipment will be integrated through the native transfer system.'),
 'The Federal Capital':('The conference has confirmed Belgrade as the capital of the new federation. Federal institutions will operate from the existing Serbian capital while each constituent republic maintains its local administration and legislature.','With the presidency and common army settled, the conference can close. The capital receives development capacity and the constitutional decision becomes available once its focus is complete. No alternate capital or change of national leader is introduced.'),
 'One People, One State':('The Montenegrin political programme has affirmed the principle of one common administration. Belgrade presents the negotiations as a union of institutions and communities rather than a continuing wartime occupation.','Where Montenegro remains under Serbian protection, confidence and administrative cooperation improve. The final territorial integration still follows the approved timed decision chain, with its full financial obligations and safe transfer of the surviving army.'),
 'One Yugoslav Army':('The republic formations now serve within a single federal army. Their surviving units and stockpiles transferred at the proclamation, preserving regional experience while establishing one strategic command.','The next programmes will unify the staff structures and expand the federal arsenal. No second army or replacement stockpile is created by this announcement; the command reform develops the forces the federation already possesses.')}
def ev(num,name,option,body='',picture=None,desc=None,second=None):
 id=f'MSGA_endgame.{num}'
 if picture is None:picture='GFX_MSGA_endgame_event_'+re.sub('[^a-z0-9]+','_',name.lower()).strip('_')
 loc(id+'.t',name)
 loc(id+'.d',desc or '\n\n'.join(STORIES[name]))
 loc(id+'.a',option)
 guarded=f'if = {{ limit = {{ tag = SER NOT = {{ has_country_flag = MSGA_eg_event_{num}_resolved }} }} {body} set_country_flag = MSGA_eg_event_{num}_resolved }}'
 options=f'option = {{ name = {id}.a ai_chance = {{ factor = 95 }} hidden_effect = {{ {guarded} }} }}'
 if second:
  text,effect_body,condition=second;loc(id+'.b',text)
  options+=f'\n option = {{ name = {id}.b ai_chance = {{ factor = 5 }} trigger = {{ {condition} }} hidden_effect = {{ if = {{ limit = {{ tag = SER NOT = {{ has_country_flag = MSGA_eg_event_{num}_resolved }} }} {effect_body} set_country_flag = MSGA_eg_event_{num}_resolved }} }} }}'
 EVENTS.append(f'country_event = {{ id = {id} title = {id}.t desc = {id}.d picture = {picture} is_triggered_only = yes fire_only_once = yes {options} }}')
 return 'country_event = { id = '+id+' }'

# Key, days, x/y, predecessors, availability. Coordinates keep the two routes apart.
FOCUS=[
 ('future_of_the_south_slavs',28,12,0,[],''),
 ('a_serbian_century',35,5,1,['future_of_the_south_slavs'],'NOT = { has_country_flag = MSGA_yugoslavia_path }'),
 ('one_serbian_state',28,5,2,['a_serbian_century'],''),
 ('montenegrin_question',28,2,3,['one_serbian_state'],''),
 ('one_people_one_state',28,2,4,['montenegrin_question'],''),
 ('integrate_montenegro',21,2,5,['one_people_one_state'],'has_country_flag = MSGA_montenegro_integrated'),
 ('macedonian_question',28,8,3,['one_serbian_state'],''),
 ('secure_the_vardar',28,8,4,['macedonian_question'],''),
 ('integrate_macedonia',28,8,5,['secure_the_vardar'],'has_country_flag = MSGA_macedonia_integrated'),
 ('consolidate_serbian_lands',35,5,6,['integrate_montenegro','integrate_macedonia'],'MSGA_eg_serbian_lands_ready = yes'),
 ('the_greater_serbian_state',35,5,7,['consolidate_serbian_lands'],'MSGA_eg_serbian_lands_ready = yes'),
 ('belgrades_sphere',28,5,8,['the_greater_serbian_state'],''),
 ('serbian_hegemony',35,5,9,['belgrades_sphere'],''),
 ('the_yugoslav_idea',35,19,1,['future_of_the_south_slavs'],'NOT = { has_country_flag = MSGA_greater_serbia_path }'),
 ('a_common_homeland',28,19,2,['the_yugoslav_idea'],''),
 ('reconcile_the_republics',35,16,3,['a_common_homeland'],''),
 ('conference_of_belgrade',35,16,4,['reconcile_the_republics'],'MSGA_eg_republics_ready = yes'),
 ('draft_a_federal_model',35,22,3,['a_common_homeland'],''),
 ('the_federal_constitution',35,22,4,['draft_a_federal_model'],'MSGA_eg_republics_ready = yes has_country_flag = MSGA_eg_conference_finished'),
 ('proclaim_the_federation',35,19,5,['conference_of_belgrade','the_federal_constitution'],'has_country_flag = MSGA_yugoslav_constitution_ready MSGA_eg_federal_territory_ready = yes'),
 ('federal_yugoslavia',28,19,6,['proclaim_the_federation'],'has_country_flag = MSGA_yugoslav_federation_proclaimed'),
 ('one_yugoslav_army',28,16,7,['federal_yugoslavia'],'has_country_flag = MSGA_eg_federal_army_agreed'),
 ('integrate_the_commands',28,16,8,['one_yugoslav_army'],''),
 ('arsenal_of_yugoslavia',28,16,9,['integrate_the_commands'],''),
 ('one_yugoslav_economy',28,22,7,['federal_yugoslavia'],''),
 ('rebuild_the_common_market',28,22,8,['one_yugoslav_economy'],''),
 ('yugoslav_development_plan',35,22,9,['rebuild_the_common_market'],''),
 ('brotherhood_reforged',35,19,10,['arsenal_of_yugoslavia','yugoslav_development_plan'],''),
 ('a_new_yugoslavia',35,19,11,['brotherhood_reforged'],'')]

# ID, name, PP, debt B, duration, country, route, previous step, required focus.
DECISIONS=[
 ('begin_montenegrin_integration','Begin the Montenegrin Integration',25,.5,20,'MNT','gs',None,'montenegrin_question'),
 ('merge_state_administrations','Merge the State Administrations',30,.75,25,'MNT','gs','begin_montenegrin_integration','montenegrin_question'),
 ('unify_montenegrin_armed_forces','Unify the Armed Forces',25,.5,20,'MNT','gs','merge_state_administrations','montenegrin_question'),
 ('complete_union_montenegro','Complete the Union with Montenegro',50,1.5,30,'MNT','gs','unify_montenegrin_armed_forces','montenegrin_question'),
 ('establish_vardar_administration','Establish the Vardar Administration',30,.75,25,'MAC','gs',None,'macedonian_question'),
 ('connect_macedonian_economy','Connect the Macedonian Economy',35,1,30,'MAC','gs','establish_vardar_administration','macedonian_question'),
 ('integrate_macedonian_security','Integrate the Macedonian Security Services',30,.5,25,'MAC','gs','connect_macedonian_economy','macedonian_question'),
 ('place_macedonian_army_under_serbian_command','Place the Macedonian Army Under Serbian Command',35,.75,25,'MAC','gs','integrate_macedonian_security','macedonian_question'),
 ('integrate_macedonia_decision','Integrate Macedonia',60,2,35,'MAC','gs','place_macedonian_army_under_serbian_command','macedonian_question'),
 ('bind_croatia_to_belgrade','Bind Croatia to Belgrade',25,.25,20,'CRO','gs',None,'belgrades_sphere'),
 ('integrate_slovenian_market','Integrate the Slovenian Market',25,.25,20,'SLV','gs',None,'belgrades_sphere'),
 ('secure_albanias_loyalty','Secure Albania\'s Loyalty',25,.25,20,'ALB','gs',None,'belgrades_sphere'),
 ('coordinate_balkan_protectorates','Coordinate the Balkan Protectorates',50,.5,30,None,'gs',None,'belgrades_sphere'),
 ('open_federal_talks_zagreb','Open Federal Talks with Zagreb',25,.25,20,'CRO','yug',None,'reconcile_the_republics'),
 ('restore_croatian_civil_administration','Restore Croatian Civil Administration',30,.5,25,'CRO','yug','open_federal_talks_zagreb','reconcile_the_republics'),
 ('recognise_republic_croatia','Recognise the Republic of Croatia',40,.5,25,'CRO','yug','restore_croatian_civil_administration','reconcile_the_republics'),
 ('ljubljana_federal_talks','Ljubljana Federal Talks',25,.25,20,'SLV','yug',None,'reconcile_the_republics'),
 ('guarantee_slovenian_economic_autonomy','Guarantee Slovenian Economic Autonomy',25,.5,20,'SLV','yug','ljubljana_federal_talks','reconcile_the_republics'),
 ('recognise_republic_slovenia','Recognise the Republic of Slovenia',35,.5,20,'SLV','yug','guarantee_slovenian_economic_autonomy','reconcile_the_republics'),
 ('open_sarajevo_question','Open the Sarajevo Question',25,.25,20,'BOS','yug',None,'reconcile_the_republics'),
 ('guarantee_bosnia_federal_status','Guarantee Bosnia\'s Federal Status',35,.75,30,'BOS','yug','open_sarajevo_question','reconcile_the_republics'),
 ('recognise_republic_bosnia_herzegovina','Recognise the Republic of Bosnia and Herzegovina',40,.75,30,'BOS','yug','guarantee_bosnia_federal_status','reconcile_the_republics'),
 ('invite_podgorica_federation','Invite Podgorica to the Federation',20,.25,15,'MNT','yug',None,'reconcile_the_republics'),
 ('guarantee_montenegrin_statehood','Guarantee Montenegrin Statehood',25,.5,20,'MNT','yug','invite_podgorica_federation','reconcile_the_republics'),
 ('recognise_republic_montenegro','Recognise the Republic of Montenegro',30,.5,20,'MNT','yug','guarantee_montenegrin_statehood','reconcile_the_republics'),
 ('open_federal_talks_skopje','Open Federal Talks with Skopje',25,.25,20,'MAC','yug',None,'reconcile_the_republics'),
 ('guarantee_macedonian_identity','Guarantee Macedonian Identity',30,.5,25,'MAC','yug','open_federal_talks_skopje','reconcile_the_republics'),
 ('guarantee_macedonian_republic','Guarantee the Macedonian Republic',35,.5,25,'MAC','yug','guarantee_macedonian_identity','reconcile_the_republics'),
 ('recognise_republic_macedonia','Recognise the Republic of Macedonia',40,.75,30,'MAC','yug','guarantee_macedonian_republic','reconcile_the_republics'),
 ('ratify_federal_constitution','Ratify the Federal Constitution',75,1,30,None,'yug',None,'the_federal_constitution'),
 ('proclaim_federal_republic_yugoslavia','Proclaim the Federal Republic of Yugoslavia',100,3,35,None,'yug','ratify_federal_constitution','proclaim_the_federation')]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
 assert LIVE.resolve(strict=True)==LIVE.absolute()
 before={p.relative_to(LIVE).as_posix():sha(p.read_bytes()) for p in LIVE.rglob('*') if p.is_file()}
 assert all((SOURCE/p).exists() and sha((SOURCE/p).read_bytes())==v for p,v in before.items()),'Start from synced LIVE; preserve user changes'
 trigger('MSGA_eg_entry_ready','tag = SER has_country_flag = MSGA_south_slavic_unity_open has_country_flag = MSGA_new_balkan_order_stabilised has_country_flag = MSGA_balkan_war_victory')
 effect('MSGA_try_start_endgame','''if = { limit = { MSGA_eg_entry_ready = yes NOT = { has_country_flag = MSGA_endgame_choice_active } }
 set_country_flag = MSGA_endgame_choice_active clr_country_flag = MSGA_new_balkan_order_active
 load_focus_tree = { tree = MSGA_SER_endgame keep_completed = yes }
 }''')
 # Territorial checks are explicit whitelists. Targets cannot smuggle unrelated conquests into an annexation.
 for tag,states in STATES.items():
  if tag=='SER':continue
  country=f'{tag} = {{ exists = yes is_subject_of = SER has_war = no NOT = {{ any_owned_state = {{ NOT = {{ OR = {{ '+ ' '.join(f'state = {s}' for s in states)+' } } } } }'
  owned=scope=' '.join(f'{s} = {{ OR = {{ AND = {{ is_owned_by = {tag} is_fully_controlled_by = {tag} }} AND = {{ is_owned_by = SER is_fully_controlled_by = SER }} }} }}' for s in states)
  if tag=='BOS':
   owned='104 = { is_owned_by = BOS is_fully_controlled_by = BOS } '
   # Srpska belongs to Serbia until the OPTIONAL border decision, never a mandatory transfer.
   owned+=' '.join(f'{s} = {{ OR = {{ AND = {{ is_owned_by = BOS is_fully_controlled_by = BOS }} AND = {{ is_owned_by = SER is_fully_controlled_by = SER }} }} }}' for s in [848,849,850])
  trigger('MSGA_eg_safe_'+tag,'tag = SER has_war = no '+country+' '+owned)
 trigger('MSGA_eg_safe_bosnian_framework','MSGA_eg_safe_BOS = yes OR = { AND = { country_exists = HRZ MSGA_eg_safe_HRZ = yes } AND = { NOT = { country_exists = HRZ } 851 = { is_owned_by = SER is_fully_controlled_by = SER } } }')
 trigger('MSGA_eg_serbian_lands_ready','has_country_flag = MSGA_montenegro_integrated has_country_flag = MSGA_macedonia_integrated has_country_flag = MSGA_srpska_united NOT = { country_exists = SRP } '+' '.join(f'{s} = {{ is_owned_by = SER is_fully_controlled_by = SER }}' for s in [105,106,785,1305,848,849,850]))
 ready=' '.join(f'has_country_flag = MSGA_{s}_federal_ready' for s in ['croatia','slovenia','bosnia','montenegro','macedonia'])
 trigger('MSGA_eg_republics_ready',ready)
 trigger('MSGA_eg_federal_territory_ready','tag = SER has_war = no MSGA_eg_republics_ready = yes has_country_flag = MSGA_srpska_united NOT = { country_exists = SRP } MSGA_eg_safe_CRO = yes MSGA_eg_safe_SLV = yes MSGA_eg_safe_MNT = yes MSGA_eg_safe_MAC = yes MSGA_eg_safe_bosnian_framework = yes 107 = { is_owned_by = SER is_fully_controlled_by = SER } 785 = { is_owned_by = SER is_fully_controlled_by = SER } 1305 = { is_owned_by = SER is_fully_controlled_by = SER }')
 effect('MSGA_eg_check_obligations','''if = { limit = { tag = SER check_variable = { var = MSGA_endgame_integration_obligations value = 5 compare = greater_than_or_equals } NOT = { has_country_flag = MSGA_eg_price_notified } }
 set_country_flag = MSGA_eg_price_notified country_event = { id = MSGA_endgame.14 }
 }''')
 loc('MSGA_eg_autonomy_tt','Common administration and command')
 ev(1,'The Future of the South Slavs','We must choose the shape of the new order.',desc='The Balkan war and the first reconstruction programme are over. Belgrade now governs a regional system of Serbian lands and protected neighbours, but victory has left the constitutional question unanswered.\n\nA consolidated Serbian state would unite Montenegro and Macedonia with Serbia, Kosovo and the already integrated Republika Srpska. A Yugoslav federation would instead establish six constituent republics under a common presidency and army. Albania remains outside either political union.')
 ev(2,'The Serbian Century','One Serbian state, one Serbian future.')
 ev(3,'Belgrade and Podgorica Open Union Talks','There will be one state.')
 ev(4,'The Cost of Union','Belgrade will pay the bill.',debt(.25)+improve('MNT',5)+' MSGA_eg_check_obligations = yes',desc='The negotiators have agreed on union, but municipal payrolls, pensions and public services do not merge themselves. Montenegro’s obligations must be recognised before Belgrade can assume responsibility for its administration.\n\nThe transition requires another $0.25 billion in national debt. The commitment funds administrative continuity and reassurance for local communities; it is additional to the integration decision’s borrowing.')
 ev(5,'The Montenegrin Army Takes the Serbian Oath','One command. One army.')
 ev(6,'Montenegro Joins Serbia','The union is complete.','add_stability = 0.05 add_political_power = 50')
 ev(7,'Belgrade Arrives in Skopje','Establish the Vardar administration.')
 ev(8,'The Price of the Southern Integration','Investment today, unity tomorrow.',debt(.25)+improve('MAC',5)+' MSGA_eg_check_obligations = yes',desc='Macedonia’s economy faces years of deferred maintenance and incompatible administrative procedures. The southern integration cannot succeed through proclamations alone; it must connect transport, taxation and public services.\n\nA further $0.25 billion of national debt will finance the transition. This commitment is separate from the economic decision’s cost, and local confidence will rise as the programme becomes tangible.')
 ev(9,"Skopje's Security Apparatus Answers to Belgrade",'One security framework for the Vardar.')
 ev(10,'One Southern Command','The army will answer to Belgrade.')
 ev(11,'The Vardar Is Integrated','The southern integration is complete.','add_stability = 0.05 add_war_support = 0.05')
 ev(12,'The Serbian Question Settled','Consolidate the Serbian lands.')
 ev(13,'The Greater Serbian State','A greater Serbian state has been proclaimed.',desc='Montenegro and Macedonia have completed their integration programmes. Kosovo and the previously annexed Republika Srpska remain within Serbia, and the unified administration now covers the lands promised by the Serbian national project.\n\nThe country takes the formal name Greater Serbian State. Aleksandar Vučić remains its leader and Belgrade its capital. Croatia, Slovenia, Albania and the remaining protectorates retain their separate administrations outside the enlarged state.')
 ev(14,'The Price of Victory','We knew victory would not be cheap.','add_stability = -0.02',desc='At least $5 billion in new integration obligations has been incurred since the South Slavic project began. National debt has risen through the ordinary TFR budget system, and every agreement now competes for administrative capacity.\n\nVictory created political opportunities; implementing them carries a lasting price. The public is beginning to feel that burden. This reckoning changes neither the treasury nor the debt already recorded, and it will not be repeated.')
 ev(15,'The Yugoslav Idea','A common state for the South Slavs.')
 ev(16,'The Croatian Delegation Arrives in Belgrade','Guarantee Croatian Federal Rights.',debt(.25)+improve('CRO',5)+' MSGA_eg_check_obligations = yes',desc='The Croatian delegation has arrived with a demand for more than a new name above the same protectorate administration. Zagreb asks for a constituent republic, a local legislature and guarantees of cultural autonomy.\n\nBelgrade will accept these federal rights. Implementing the agreement adds $0.25 billion in national debt beyond the talks’ initial cost, and improves confidence in the federal project.')
 ev(17,'Zagreb Demands Guarantees','Accept the Croatian federal guarantees.','set_country_flag = MSGA_eg_croatian_rights_guaranteed',desc='Zagreb’s representatives insist that the federation must recognise Croatian cultural life and permit an elected local legislature. Defence and foreign policy may be federal, but everyday civil administration must belong to the republic.\n\nBelgrade accepts these terms. The agreement recognises Croatia as a constituent republic rather than an occupied district, providing the legal foundation for the next stage of federal reconciliation.')
 ev(18,'Ljubljana Accepts the Federation','Protect Slovenian economic autonomy.')
 borderguard='has_country_flag = MSGA_yugoslavia_path has_country_flag = MSGA_srpska_united MSGA_eg_safe_bosnian_framework = yes '+' '.join(f'{s} = {{ is_owned_by = SER is_fully_controlled_by = SER }}' for s in [848,849,850])
 bordertransfer='set_country_flag = MSGA_eg_bosnian_borders_restored add_stability = -0.02 '+improve('BOS',15)+' BOS = { transfer_state = 848 transfer_state = 849 transfer_state = 850 }'
 ev(19,'The Borders of Bosnia','Srpska Remains With Serbia','set_country_flag = MSGA_eg_srpska_constituent_serbia add_stability = 0.02 '+improve('BOS',-5),second=('Restore the Old Bosnian Borders',bordertransfer,borderguard),desc='Sarajevo’s delegates have raised the boundaries of the future Bosnian republic. Republika Srpska’s three native territories were already annexed into Serbia under the earlier settlement. Their position must now be written into the federal arrangement.\n\nThe preferred settlement keeps these territories in the Serbian constituent republic. Alternatively, Belgrade may return only those previously annexed territories to Bosnia and Herzegovina, gaining stronger reconciliation at the cost of nationalist support. Neither option transfers unrelated Serbian land.')
 ev(20,'Montenegro Chooses Yugoslavia','Guarantee Montenegrin statehood.')
 ev(21,'Skopje Accepts the Yugoslav Project','Recognise Macedonia as a constituent republic.')
 ev(22,'The Belgrade Conference','The delegations will establish the federal settlement.','country_event = { id = MSGA_endgame.23 }',desc='Delegations from Serbia, Croatia, Slovenia, Bosnia and Herzegovina, Montenegro and Macedonia have gathered in Belgrade. Their negotiated guarantees have created the foundation for a state that can replace the wartime protectorate system.\n\nThe conference will determine the strength of the presidency, confirm one federal army and establish the capital. Kosovo remains within Serbia, and Republika Srpska follows the border settlement already chosen. Albania is not a constituent republic.')
 ev(23,'How Strong Should Belgrade Be?','A Strong Federal Presidency','set_country_flag = MSGA_strong_federal_presidency add_ideas = MSGA_strong_presidency every_country = { limit = { is_subject_of = SER OR = { tag = CRO tag = SLV tag = BOS tag = HRZ tag = MNT tag = MAC } } add_autonomy_score = { value = -50 localization = MSGA_eg_autonomy_tt } } country_event = { id = MSGA_endgame.24 }',second=('A Balanced Federation','set_country_flag = MSGA_balanced_federation add_ideas = MSGA_balanced_federal_order country_event = { id = MSGA_endgame.24 }','has_country_flag = MSGA_yugoslavia_path'),desc='The constitutional committee agrees on a common state but differs over its centre. A strong federal presidency would leave Belgrade with a clear mandate over defence, diplomacy and strategic finance.\n\nA balanced federation would provide greater space for republic institutions and local administration. Both choices preserve Aleksandar Vučić as the national leader and keep the country united; they establish different guarantees within the same six-republic framework.')
 ev(24,'One Army or Six?','The Army Must Be Federal','army_experience = 15 set_country_flag = MSGA_eg_federal_army_agreed country_event = { id = MSGA_endgame.25 }',desc='A federation cannot retain six rival chains of military command. The delegates will preserve regional identities within a common force while placing defence planning, mobilisation and strategic procurement under federal authority.\n\nExisting formations and equipment will pass through the native integration process. No duplicate armies will be created, and no republic will field an independent force outside the federal command.')
 ev(25,'The Federal Capital','Belgrade Shall Remain the Capital','set_capital = { state = 107 } add_political_power = 25 '+scope_states([107],'add_extra_state_shared_building_slots = 1')+' set_country_flag = MSGA_eg_conference_finished')
 ev(26,'The Constitution of the New Yugoslavia','Six republics, one federal constitution.','set_country_flag = MSGA_eg_constitution_ratified',desc='The constitution recognises the republics of Serbia, Croatia, Slovenia, Bosnia and Herzegovina, Montenegro and Macedonia. Local legislatures and cultural administration coexist with common foreign policy, defence, strategic industry and federal finance.\n\nKosovo remains within Serbia and is not a separate republic. Republika Srpska follows the earlier border agreement and normally remains within the Serbian constituent republic. The federation is a contemporary constitutional project, without socialist institutions or symbolism.')
 ev(27,'A New Yugoslavia Is Born','Proclaim the Federal Republic of Yugoslavia.','add_stability = 0.10 add_political_power = 100',desc='The negotiated integration of the five partner republics is complete. Their surviving armies, equipment, factories and territories are incorporated through the native transfer system, and the six-republic constitution now applies to a single federal state.\n\nThe country becomes the Federal Republic of Yugoslavia, under Aleksandar Vučić, with Belgrade as capital and a plain blue-white-red flag. Kosovo remains within Serbia; Albania survives as a separate Serbian client outside the federation.')
 ev(28,'Brotherhood Reforged','Reconciliation will be built in everyday life.',desc='The federal settlement is moving from treaties into schools, workplaces and public services. Communities that fought against one another must now learn to trust common institutions without surrendering their cultural identities.\n\nBrotherhood here means civic reconciliation among the South Slavic peoples. It carries no socialist programme: regional identities remain recognised, public administration serves all six republics, and the federal army provides a common guarantee of security.')
 ev(29,'A Yugoslavia for a New Era','The federation has found its future.',desc='The military command has been unified and the common market rebuilt. Investment is reaching the major regions of the federation, and the constitutional guarantees negotiated in Belgrade now support a functioning common state.\n\nThe Federal Republic of Yugoslavia enters a new era under its existing leadership. The plain blue-white-red tricolour represents a modern federation of six republics, with Albania outside its borders and no further war imposed by this settlement.')
 # A short focus event is separate from the debt-bearing talks event.
 ev(30,'One People, One State','The political union will become a common administration.',picture='GFX_MSGA_endgame_event_belgrade_and_podgorica_open_union_talks')
 ev(31,'One Yugoslav Army','One federal army, one common command.')
 effect('MSGA_eg_bosnian_progress',improve('BOS',10)+' if = { limit = { HRZ = { exists = yes is_subject_of = SER } } '+improve('HRZ',10)+' }')
 effect('MSGA_eg_strengthen_subjects','''every_country = { limit = { is_subject_of = SER OR = { tag = CRO tag = SLV tag = ALB tag = BOS tag = HRZ } }
 remove_ideas = MSGA_stabilised_client_order add_ideas = MSGA_endgame_subject_coordination
 add_autonomy_score = { value = -100 localization = MSGA_eg_autonomy_tt }
 }''')
 rewards={
 'future_of_the_south_slavs':'add_political_power = 50 add_stability = 0.05 country_event = { id = MSGA_endgame.1 }',
 'a_serbian_century':'set_country_flag = MSGA_greater_serbia_path add_political_power = 100 add_war_support = 0.10 add_stability = 0.05 add_timed_idea = { idea = MSGA_serbian_national_project_spirit days = 365 } country_event = { id = MSGA_endgame.2 }',
 'one_people_one_state':'if = { limit = { MSGA_eg_safe_MNT = yes } '+improve('MNT',10)+' } country_event = { id = MSGA_endgame.30 }',
 'integrate_montenegro':'add_stability = 0.03',
 'secure_the_vardar':infra(106,'MAC')+' '+infra(106)+' '+scope_states([106],'add_extra_state_shared_building_slots = 1','MAC')+' '+scope_states([106],'add_extra_state_shared_building_slots = 1')+' set_temp_variable = { var = industrial_development_var_temp value = 0.02 } add_industrial_development = yes',
 'integrate_macedonia':'add_stability = 0.03',
 'consolidate_serbian_lands':'remove_ideas = MSGA_serbian_national_project_spirit add_ideas = MSGA_unified_serbian_state country_event = { id = MSGA_endgame.12 }',
 'the_greater_serbian_state':'set_cosmetic_tag = SER_MSGA_GREATER_SERBIA remove_ideas = MSGA_unified_serbian_state add_ideas = MSGA_serbian_state_reborn set_country_flag = MSGA_greater_serbian_state_proclaimed country_event = { id = MSGA_endgame.13 }',
 'belgrades_sphere':'add_ideas = MSGA_belgrades_sphere_spirit MSGA_eg_strengthen_subjects = yes',
 'serbian_hegemony':'remove_ideas = MSGA_serbian_state_reborn remove_ideas = MSGA_belgrades_sphere_spirit remove_ideas = MSGA_a_stabilised_balkan_order add_ideas = MSGA_hegemon_balkans MSGA_eg_strengthen_subjects = yes set_country_flag = MSGA_endgame_greater_serbia_complete',
 'the_yugoslav_idea':'set_country_flag = MSGA_yugoslavia_path add_political_power = 75 add_stability = 0.05 add_war_support = 0.05 add_timed_idea = { idea = MSGA_yugoslav_project days = 365 } country_event = { id = MSGA_endgame.15 }',
 'reconcile_the_republics':'if = { limit = { MSGA_eg_safe_CRO = yes } '+improve('CRO',5)+' } if = { limit = { MSGA_eg_safe_SLV = yes } '+improve('SLV',5)+' } if = { limit = { MSGA_eg_safe_bosnian_framework = yes } MSGA_eg_bosnian_progress = yes }',
 'conference_of_belgrade':'country_event = { id = MSGA_endgame.22 }',
 'draft_a_federal_model':'add_timed_idea = { idea = MSGA_federal_transition days = 365 }',
 'federal_yugoslavia':'remove_ideas = MSGA_yugoslav_project remove_ideas = MSGA_federal_transition remove_ideas = MSGA_serbian_sphere_spirit remove_ideas = MSGA_a_stabilised_balkan_order add_ideas = MSGA_yugoslav_federation',
 'one_yugoslav_army':'add_ideas = MSGA_unified_federal_command army_experience = 15 country_event = { id = MSGA_endgame.31 }',
 'integrate_the_commands':'army_experience = 25',
 'arsenal_of_yugoslavia':building(107,'arms_factory')+' '+building(109,'arms_factory')+' add_ideas = MSGA_federal_arsenal',
 'one_yugoslav_economy':'add_ideas = MSGA_federal_market',
 'rebuild_the_common_market':infra(102)+' '+infra(104)+' '+infra(106)+' add_stability = 0.03',
 'yugoslav_development_plan':building(102,'office_park')+' '+building(109,'industrial_complex')+' '+building(104,'industrial_complex')+' '+building(106,'arms_factory')+' '+scope_states([102,109,104,105,106], 'if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } }')+' set_temp_variable = { var = industrial_development_var_temp value = 0.05 } add_industrial_development = yes',
 'brotherhood_reforged':'add_stability = 0.10 '+scope_states(ALL_FEDERAL,'add_compliance = 10 add_resistance = -10')+' country_event = { id = MSGA_endgame.28 }',
 'a_new_yugoslavia':'remove_ideas = MSGA_yugoslav_federation remove_ideas = MSGA_federal_market remove_ideas = MSGA_federal_arsenal add_ideas = MSGA_federation_reborn set_country_flag = MSGA_endgame_yugoslavia_complete country_event = { id = MSGA_endgame.29 }'}
 focus_names={a[0]:a[0].replace('_',' ').title() for a in FOCUS}
 focus_names.update({'belgrades_sphere':"Belgrade's Sphere",'one_people_one_state':'One People, One State'})
 bodies=[]
 for stem,days,x,y,parents,avail in FOCUS:
  route='' if stem=='future_of_the_south_slavs' else ('has_country_flag = MSGA_greater_serbia_path' if x<=8 else 'has_country_flag = MSGA_yugoslavia_path')
  if stem in ['a_serbian_century','the_yugoslav_idea']:route=''
  prerequisites=' '.join(f'prerequisite = {{ focus = MSGA_{p} }}' for p in parents)
  exclusive=f'mutually_exclusive = {{ focus = MSGA_{"the_yugoslav_idea" if stem=="a_serbian_century" else "a_serbian_century"} }}' if stem in ['a_serbian_century','the_yugoslav_idea'] else ''
  factor=10 if stem=='a_serbian_century' else 3 if stem=='the_yugoslav_idea' else 5
  body=rewards.get(stem,'')
  effect('MSGA_eg_focus_'+stem,f'if = {{ limit = {{ tag = SER has_country_flag = MSGA_endgame_choice_active NOT = {{ {completed(stem)} }} {route} {avail} }} {body} set_country_flag = MSGA_eg_focus_{stem} }}')
  bodies.append(f'focus = {{ id = MSGA_{stem} icon = GFX_MSGA_endgame_focus_{stem} x = {x} y = {y} cost = {days/7:g} {prerequisites} {exclusive} available = {{ tag = SER has_country_flag = MSGA_endgame_choice_active {route} {avail} }} ai_will_do = {{ factor = {factor} }} completion_reward = {{ MSGA_eg_focus_{stem} = yes }} }}')
  loc('MSGA_'+stem,focus_names[stem]);loc('MSGA_'+stem+'_desc',{'future_of_the_south_slavs':'The New Balkan Order is stable. Choose between a consolidated Serbian state and a six-republic Yugoslav federation. Albania remains outside both unions.','the_greater_serbian_state':'Proclaim the Greater Serbian State after the Montenegro and Macedonia programmes are complete and Kosovo and the previously annexed Republika Srpska are securely held. Aleksandar Vučić remains the leader.','proclaim_the_federation':'Open the final federal proclamation after ratification and the conference. The timed decision integrates the five partner republics with their existing armies and equipment. Albania remains separate.','integrate_the_commands':'The republic armies and stockpiles transferred during the proclamation already belong to the federal state. Merge their command structures and train a common staff without spawning duplicate divisions.','yugoslav_development_plan':'Invest in the actual Ljubljana, Zagreb, Sarajevo, Podgorica and Skopje regions through native building and industrial-development effects.','serbian_hegemony':'Consolidate Serbian leadership with a permanent endgame spirit and coordinated protectorates. Open peaceful future influence opportunities toward Bulgaria, Romania and Greece.'}.get(stem,focus_names[stem]+'. '+('Advance the Serbian national project while keeping the remaining protectorates independent within Belgrade’s sphere.' if x<=8 else 'Advance the constitutional federation while preserving local identity within common civilian and military institutions.')))
 put('common/national_focus/MSGA_SER_endgame.txt','focus_tree = { id = MSGA_SER_endgame default = no reset_on_civilwar = no country = { factor = 0 modifier = { add = 500 tag = SER has_country_flag = MSGA_endgame_choice_active } } '+'\n'.join(bodies)+'\n}\n')
 # Borrowing event costs must be accepted before a chain can advance/annex.
 event_gates={'unify_montenegrin_armed_forces':'has_country_flag = MSGA_eg_event_4_resolved','integrate_macedonian_security':'has_country_flag = MSGA_eg_event_8_resolved','restore_croatian_civil_administration':'has_country_flag = MSGA_eg_event_16_resolved','recognise_republic_croatia':'has_country_flag = MSGA_eg_croatian_rights_guaranteed','guarantee_bosnia_federal_status':'has_country_flag = MSGA_eg_event_19_resolved','ratify_federal_constitution':'MSGA_eg_republics_ready = yes has_country_flag = MSGA_eg_conference_finished','proclaim_federal_republic_yugoslavia':'has_country_flag = MSGA_eg_constitution_ratified MSGA_eg_federal_territory_ready = yes'}
 finish={
 'begin_montenegrin_integration':improve('MNT')+' country_event = { id = MSGA_endgame.3 }',
 'merge_state_administrations':improve('MNT')+' country_event = { id = MSGA_endgame.4 }',
 'unify_montenegrin_armed_forces':'army_experience = 15 MNT = { add_autonomy_score = { value = -50 localization = MSGA_eg_autonomy_tt } } country_event = { id = MSGA_endgame.5 }',
 'complete_union_montenegro':annex('MNT')+' '+scope_states([105],'add_extra_state_shared_building_slots = 1')+' '+building(105,'industrial_complex')+' '+building(105,'arms_factory')+' set_country_flag = MSGA_montenegro_integrated country_event = { id = MSGA_endgame.6 }',
 'establish_vardar_administration':improve('MAC')+' country_event = { id = MSGA_endgame.7 }',
 'connect_macedonian_economy':infra(106,'MAC')+' '+building(106,'industrial_complex','MAC')+' set_temp_variable = { var = industrial_development_var_temp value = 0.02 } add_industrial_development = yes country_event = { id = MSGA_endgame.8 }',
 'integrate_macedonian_security':improve('MAC')+' add_stability = 0.02 country_event = { id = MSGA_endgame.9 }',
 'place_macedonian_army_under_serbian_command':'army_experience = 20 MAC = { add_autonomy_score = { value = -75 localization = MSGA_eg_autonomy_tt } } country_event = { id = MSGA_endgame.10 }',
 'integrate_macedonia_decision':annex('MAC')+' '+building(106,'arms_factory')+' set_country_flag = MSGA_macedonia_integrated country_event = { id = MSGA_endgame.11 }',
 'bind_croatia_to_belgrade':'CRO = { add_autonomy_score = { value = -100 localization = MSGA_eg_autonomy_tt } add_ideas = MSGA_endgame_subject_coordination } add_ideas = MSGA_endgame_croatian_access',
 'integrate_slovenian_market':'SLV = { add_autonomy_score = { value = -100 localization = MSGA_eg_autonomy_tt } add_ideas = MSGA_endgame_subject_coordination } add_ideas = MSGA_endgame_slovenian_access',
 'secure_albanias_loyalty':'ALB = { add_autonomy_score = { value = -100 localization = MSGA_eg_autonomy_tt } add_ideas = MSGA_endgame_subject_coordination }',
 'coordinate_balkan_protectorates':'MSGA_eg_strengthen_subjects = yes',
 'open_federal_talks_zagreb':improve('CRO')+' country_event = { id = MSGA_endgame.16 }',
 'restore_croatian_civil_administration':improve('CRO')+' country_event = { id = MSGA_endgame.17 }',
 'recognise_republic_croatia':'set_country_flag = MSGA_croatia_federal_ready '+improve('CRO'),
 'ljubljana_federal_talks':improve('SLV'),
 'guarantee_slovenian_economic_autonomy':improve('SLV')+' SLV = { add_timed_idea = { idea = MSGA_slovenian_federal_guarantee days = 365 } }',
 'recognise_republic_slovenia':'set_country_flag = MSGA_slovenia_federal_ready country_event = { id = MSGA_endgame.18 }',
 'open_sarajevo_question':'country_event = { id = MSGA_endgame.19 }',
 'guarantee_bosnia_federal_status':'MSGA_eg_bosnian_progress = yes',
 'recognise_republic_bosnia_herzegovina':'set_country_flag = MSGA_bosnia_federal_ready MSGA_eg_bosnian_progress = yes',
 'invite_podgorica_federation':improve('MNT'),
 'guarantee_montenegrin_statehood':improve('MNT'),
 'recognise_republic_montenegro':'set_country_flag = MSGA_montenegro_federal_ready country_event = { id = MSGA_endgame.20 }',
 'open_federal_talks_skopje':improve('MAC'),
 'guarantee_macedonian_identity':improve('MAC'),
 'guarantee_macedonian_republic':improve('MAC'),
 'recognise_republic_macedonia':'set_country_flag = MSGA_macedonia_federal_ready country_event = { id = MSGA_endgame.21 }',
 'ratify_federal_constitution':'set_country_flag = MSGA_yugoslav_constitution_ready country_event = { id = MSGA_endgame.26 }',
 'proclaim_federal_republic_yugoslavia':' '.join(annex(t) for t in ['CRO','SLV','BOS','HRZ','MNT','MAC'])+' '+scope_states(ALL_FEDERAL,'if = { limit = { NOT = { is_core_of = SER } } add_core_of = SER }')+' set_cosmetic_tag = SER_MSGA_YUGOSLAV_FEDERATION set_capital = { state = 107 } set_country_flag = MSGA_yugoslav_federation_proclaimed country_event = { id = MSGA_endgame.27 }'}
 decision_bodies={'gs':[],'yug':[]}
 for stem,name,pp,borrow,days,tag,route,previous,focus in DECISIONS:
  pathflag='MSGA_greater_serbia_path' if route=='gs' else 'MSGA_yugoslavia_path'
  safe=('MSGA_eg_safe_bosnian_framework = yes' if tag=='BOS' else f'MSGA_eg_safe_{tag} = yes') if tag else ('MSGA_eg_federal_territory_ready = yes' if route=='yug' else 'has_war = no')
  if tag=='ALB':safe='ALB = { exists = yes is_subject_of = SER has_war = no } has_war = no'
  prev=f'has_country_flag = {flag(previous)}' if previous else ''
  allowed=f'tag = SER has_country_flag = {pathflag} {completed(focus)} {prev} {safe} {event_gates.get(stem,"")} NOT = {{ has_country_flag = {flag(stem)} }}'
  trigger('MSGA_eg_conditions_'+stem,allowed)
  # Single process per dependent administration; persistent owner flag outlives timer.
  busy='MSGA_eg_busy_'+(tag or ('federal' if route=='yug' else 'sphere'))
  effect('MSGA_eg_start_'+stem,f'if = {{ limit = {{ MSGA_eg_conditions_{stem} = yes NOT = {{ has_country_flag = {pending(stem)} }} NOT = {{ has_country_flag = {busy} }} }} set_country_flag = {pending(stem)} set_country_flag = {busy} {debt(borrow)} MSGA_eg_check_obligations = yes }}')
  effect('MSGA_eg_release_'+stem,f'if = {{ limit = {{ has_country_flag = {pending(stem)} }} clr_country_flag = {pending(stem)} clr_country_flag = {busy} }}')
  effect('MSGA_eg_cancel_'+stem,f'if = {{ limit = {{ tag = SER has_country_flag = {pending(stem)} NOT = {{ has_country_flag = {flag(stem)} }} }} add_political_power = {pp} {debt(-borrow)} MSGA_eg_release_{stem} = yes log = "[MSGA ENDGAME] {stem} cancelled and refunded" }}')
  effect('MSGA_eg_finish_'+stem,f'if = {{ limit = {{ tag = SER has_country_flag = {pending(stem)} MSGA_eg_conditions_{stem} = yes }} {finish[stem]} set_country_flag = {flag(stem)} MSGA_eg_release_{stem} = yes log = "[MSGA ENDGAME] {stem} completed" }} else = {{ MSGA_eg_cancel_{stem} = yes }}')
  tt='MSGA_eg_'+stem+'_requirements_tt';loc(tt,'The preceding agreements and required focus are complete; the relevant territories and administrations remain peacefully under Serbian protection.')
  loc('MSGA_'+stem if stem!='integrate_macedonia_decision' else 'MSGA_'+stem,name)
  loc('MSGA_'+stem+'_desc',f'Cost: §Y{pp} Political Power§!, §Y+${borrow:g}B National Debt§!\nDuration: §Y{days} days§!\n\n'+name+'. '+('The final agreement integrates only the approved republic territories and transfers the existing armies and equipment through the native annexation system.' if stem in ['complete_union_montenegro','integrate_macedonia_decision','proclaim_federal_republic_yugoslavia'] else 'Complete the next administrative agreement. The one-time commitment uses TFR national debt and does not deduct money from the treasury.')+' If the agreement becomes impossible, its decision cost is refunded and it can be retried.')
  loc('MSGA_eg_'+stem+'_start_tt',f'Borrow §Y${borrow:g}B§! through TFR national debt. Begin the §Y{days}-day§! process.')
  decision_bodies[route].append(f'''MSGA_{stem} = {{ icon = MSGA_endgame_decision_{stem} cost = {pp} days_remove = {days}
 visible = {{ tag = SER has_country_flag = {pathflag} {completed(focus)} NOT = {{ has_country_flag = {flag(stem)} }} }}
 available = {{ custom_trigger_tooltip = {{ tooltip = {tt} MSGA_eg_conditions_{stem} = yes NOT = {{ has_country_flag = {pending(stem)} }} NOT = {{ has_country_flag = {busy} }} }} }}
 cancel_trigger = {{ NOT = {{ MSGA_eg_conditions_{stem} = yes }} }}
 complete_effect = {{ custom_effect_tooltip = MSGA_eg_{stem}_start_tt hidden_effect = {{ MSGA_eg_start_{stem} = yes }} }}
 remove_effect = {{ hidden_effect = {{ MSGA_eg_finish_{stem} = yes }} }} cancel_effect = {{ hidden_effect = {{ MSGA_eg_cancel_{stem} = yes }} }}
 ai_will_do = {{ factor = 10 }} }}''')
 # Future influence is optional diplomacy, not an extra annexation or war chain.
 for tag,title in [('BUL','Bulgaria'),('ROM','Romania'),('GRE','Greece')]:
  stem='open_endgame_dialogue_'+tag.lower();loc('MSGA_'+stem,'Open Dialogue with '+title);loc('MSGA_'+stem+'_desc','Cost: 25 Political Power\n\nOpen peaceful diplomatic contacts with '+title+'. No territorial change or war is created.')
  decision_bodies.setdefault('influence',[]).append(f'MSGA_{stem} = {{ icon = MSGA_endgame_decision_coordinate_balkan_protectorates cost = 25 visible = {{ country_exists = {tag} NOT = {{ has_country_flag = {flag(stem)} }} }} available = {{ custom_trigger_tooltip = {{ tooltip = MSGA_eg_dialogue_tt has_war = no {tag} = {{ has_war = no }} }} }} complete_effect = {{ hidden_effect = {{ set_country_flag = {flag(stem)} {tag} = {{ add_opinion_modifier = {{ target = SER modifier = MSGA_endgame_dialogue }} }} }} }} ai_will_do = {{ factor = 1 }} }}')
 loc('MSGA_eg_dialogue_tt','Both countries are at peace.')
 put('common/decisions/MSGA_endgame_decisions.txt','\n'.join(f'{cat} = {{\n'+ '\n'.join(decision_bodies[route])+'\n}' for route,cat in [('gs','MSGA_serbian_national_project'),('yug','MSGA_building_yugoslav_federation'),('influence','MSGA_future_regional_influence')])+'\n')
 categories=[]
 for stem,name,condition,concept in [('serbian_national_project','The Serbian National Project','has_country_flag = MSGA_greater_serbia_path '+completed('one_serbian_state'),'one_serbian_state'),('building_yugoslav_federation','Building the Yugoslav Federation','has_country_flag = MSGA_yugoslavia_path '+completed('a_common_homeland'),'common_homeland'),('future_regional_influence','Future Regional Influence','has_country_flag = MSGA_endgame_greater_serbia_complete','belgrades_sphere')]:
  loc('MSGA_'+stem,name)
  desc='Negotiate the next political agreements. Completed agreements are recorded permanently. '\
       + ('The five republics must be ready before constitutional ratification; the final proclamation integrates them with Serbia. Albania remains outside.' if 'yugoslav' in stem else 'The national project integrates Montenegro and Macedonia. Other countries remain separate protectorates.' if stem=='serbian_national_project' else 'Optional peaceful contacts with Bulgaria, Romania and Greece. No further war is imposed.')
  if 'yugoslav' in stem:
   desc+='\n\nCroatia: [MSGA_eg_croatia_progress]\nSlovenia: [MSGA_eg_slovenia_progress]\nBosnia and Herzegovina: [MSGA_eg_bosnia_progress]\nMontenegro: [MSGA_eg_montenegro_progress]\nMacedonia: [MSGA_eg_macedonia_progress]\nConstitution: [MSGA_eg_constitution_progress]'
  loc('MSGA_'+stem+'_desc',desc)
  categories.append(f'MSGA_{stem} = {{ icon = MSGA_endgame_category_{stem} allowed = {{ tag = SER }} visible = {{ {condition} }} }}')
 put('common/decisions/categories/MSGA_endgame_categories.txt','\n'.join(categories)+'\n')
 progress=[]
 for stem in ['croatia','slovenia','bosnia','montenegro','macedonia','constitution']:
  f='MSGA_'+stem+'_federal_ready' if stem!='constitution' else 'MSGA_yugoslav_constitution_ready'
  progress.append(f'defined_text = {{ name = MSGA_eg_{stem}_progress text = {{ trigger = {{ has_country_flag = {f} }} localization_key = MSGA_eg_ready }} text = {{ localization_key = MSGA_eg_pending }} }}')
 loc('MSGA_eg_ready','§GReady§!');loc('MSGA_eg_pending','§YPending§!')
 put('common/scripted_localisation/MSGA_endgame_scripted_localisation.txt','\n'.join(progress)+'\n')
 put('common/opinion_modifiers/MSGA_endgame_opinions.txt','opinion_modifiers = { MSGA_endgame_dialogue = { value = 25 decay = 0 } }\n')
 # Common spirit keys are not route flags or categories; no accidental duplicate objects.
 ideas={
 'serbian_national_project_spirit':('The Serbian National Project','political_power_factor = 0.10 stability_factor = 0.05 industrial_capacity_factory = 0.05 army_org_factor = 0.05 compliance_growth_on_our_occupied_states = 0.10','serbian_century'),
 'unified_serbian_state':('A Unified Serbian State','stability_factor = 0.10 industrial_capacity_factory = 0.05 recruitable_population_factor = 0.10 production_speed_buildings_factor = 0.05 resistance_target_on_our_occupied_states = -0.10','consolidate_serbian_lands'),
 'serbian_state_reborn':('The Serbian State Reborn','political_power_factor = 0.10 industrial_capacity_factory = 0.075 production_speed_buildings_factor = 0.05 recruitable_population_factor = 0.10 stability_factor = 0.10','greater_serbian_state'),
 'belgrades_sphere_spirit':("Belgrade's Sphere",'political_power_factor = 0.05 industrial_capacity_factory = 0.05 income_growth_factor = 0.05','belgrades_sphere'),
 'hegemon_balkans':('Hegemon of the Balkans','stability_factor = 0.10 war_support_factor = 0.10 political_power_factor = 0.10 industrial_capacity_factory = 0.075 production_speed_buildings_factor = 0.05 income_growth_factor = 0.05 army_attack_factor = 0.05 army_defence_factor = 0.05','serbian_hegemony'),
 'endgame_subject_coordination':('Balkan Protectorate Coordination','autonomy_gain_global_factor = -0.25 cic_to_overlord_factor = 0.10 mic_to_overlord_factor = 0.10 extra_trade_to_overlord_factor = 0.10','coordinate_protectorates'),
 'endgame_croatian_access':('Croatian Economic Access','business_value_factor = 0.02 income_growth_factor = 0.005','coordinate_protectorates'),
 'endgame_slovenian_access':('Slovenian Market Access','business_value_factor = 0.02 income_growth_factor = 0.005','slovenian_reconciliation'),
 'yugoslav_project':('The Yugoslav Project','political_power_factor = 0.10 compliance_growth_on_our_occupied_states = 0.10 resistance_target_on_our_occupied_states = -0.10 stability_factor = 0.05 production_speed_buildings_factor = 0.05','yugoslav_idea'),
 'federal_transition':('The Federal Transition','stability_factor = -0.05 compliance_growth_on_our_occupied_states = 0.15 resistance_target_on_our_occupied_states = -0.10 political_power_factor = 0.10','draft_federal_model'),
 'yugoslav_federation':('The Yugoslav Federation','stability_factor = 0.10 industrial_capacity_factory = 0.05 production_speed_buildings_factor = 0.05 compliance_growth_on_our_occupied_states = 0.10 resistance_target_on_our_occupied_states = -0.10 political_power_factor = 0.05','federal_yugoslavia'),
 'federation_reborn':('Federation Reborn','stability_factor = 0.15 industrial_capacity_factory = 0.10 production_speed_buildings_factor = 0.10 income_growth_factor = 0.05 recruitable_population_factor = 0.10 compliance_growth_on_our_occupied_states = 0.15 resistance_target_on_our_occupied_states = -0.10','new_yugoslavia'),
 'strong_presidency':('A Strong Federal Presidency','political_power_factor = 0.05 stability_factor = 0.05','yugoslav_idea'),
 'balanced_federal_order':('A Balanced Federation','compliance_growth_on_our_occupied_states = 0.10 resistance_target_on_our_occupied_states = -0.05 stability_factor = 0.05','reconcile_republics'),
 'unified_federal_command':('One Federal Command','army_org_factor = 0.03 supply_consumption_factor = -0.05','one_yugoslav_army'),
 'federal_arsenal':('The Federal Arsenal','industrial_capacity_factory = 0.03 production_factory_efficiency_gain_factor = 0.05','one_yugoslav_economy'),
 'federal_market':('The Common Federal Market','consumer_goods_factor = -0.03 business_value_factor = 0.05 income_growth_factor = 0.02','yugoslav_development_plan'),
 'endgame_reconciliation':('Administrative Reconciliation','stability_factor = 0.03 resistance_target_on_our_occupied_states = -0.10 compliance_growth_on_our_occupied_states = 0.10','reconcile_republics'),
 'slovenian_federal_guarantee':('Slovenian Economic Autonomy','business_value_factor = 0.05 stability_factor = 0.03','slovenian_reconciliation')}
 ib=[]
 for stem,(name,mod,concept) in ideas.items():
  loc('MSGA_'+stem,name);loc('MSGA_'+stem+'_desc',name+' supports the negotiated constitutional settlement and its common administration.')
  cancel='cancel = { NOT = { is_subject_of = SER } }' if stem=='endgame_subject_coordination' else ''
  ib.append(f'MSGA_{stem} = {{ picture = MSGA_endgame_idea_{stem} allowed = {{ always = no }} allowed_civil_war = {{ always = yes }} removal_cost = -1 {cancel} modifier = {{ {mod} }} }}')
 put('common/ideas/MSGA_endgame_ideas.txt','ideas = { country = { '+'\n'.join(ib)+' } }\n')
 put('events/MSGA_endgame_events.txt','add_namespace = MSGA_endgame\n'+'\n'.join(EVENTS)+'\n')
 put('common/scripted_triggers/MSGA_endgame_triggers.txt','\n'.join(TRIGGERS)+'\n')
 put('common/scripted_effects/MSGA_endgame_effects.txt','\n'.join(EFFECTS)+'\n')
 put('common/on_actions/MSGA_endgame_on_actions.txt','on_actions = { on_startup = { effect = { SER = { MSGA_try_start_endgame = yes } } } on_weekly = { effect = { if = { limit = { tag = SER } MSGA_try_start_endgame = yes } } } }\n')
 path='common/scripted_effects/MSGA_new_order_effects.txt';old=(LIVE/path).read_text(encoding='utf-8-sig')
 needle='set_country_flag = MSGA_south_slavic_unity_open country_event = { id = MSGA_neworder.16 }'
 assert old.count(needle)==1
 put(path,old.replace(needle,needle+'\n  MSGA_try_start_endgame = yes'))
 # Identity is cosmetic only: no new real tag, history, leader or OOB.
 for tag,short,long,adj in [('SER_MSGA_GREATER_SERBIA','Greater Serbia','Greater Serbian State','Greater Serbian'),('SER_MSGA_YUGOSLAV_FEDERATION','Yugoslavia','Federal Republic of Yugoslavia','Yugoslav')]:
  loc(tag,short);loc(tag+'_DEF',long);loc(tag+'_ADJ',adj)
  for p in (TFR/'common/ideologies').glob('*.txt'):
   ideologies=get(parse(p.read_text(encoding='utf-8-sig')),'ideologies')
   for ideology,o,b in ideologies:
    if tag+'_'+ideology in LOC:continue
    loc(tag+'_'+ideology,short);loc(tag+'_'+ideology+'_DEF',long);loc(tag+'_'+ideology+'_ADJ',adj)
 # Cosmetics inherit SER's map colour; no upstream global colors override is needed.
 put('localisation/english/MSGA_endgame_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in LOC.items())+'\n')
 create_art(ideas)
 for path in ['descriptor.mod','make_serbia_great_again.mod']:
  old=(LIVE/path).read_text(encoding='utf-8-sig');assert 'version="0.13.0"' in old
  put(path,old.replace('version="0.13.0"','version="0.14.0"'))
 # Native libraries read only. Validate input signatures and all generated syntax before runtime writes.
 natives=['common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt','common/scripted_effects/TFR_scripted_effects_FRA.txt','common/ideologies/00_ideologies.txt','map/provinces.bmp','map/definition.csv']
 native={p:sha((TFR/p).read_bytes()) for p in natives if (TFR/p).exists()}
 record={'version':'0.14.0','runtime':str(LIVE),'package':str(PACK),'package_sha256':sha(PACK.read_bytes()),'baseline_sha256':before,'changed_relative_paths':sorted(FILES),'assets':ASSETS,'native_states':STATES,'native_sources_sha256':native,'focus_count':len(FOCUS),'decisions':DECISIONS,'focuses':FOCUS,'event_count':len(EVENTS),'engine_test':'Reserved by user; game and saves untouched'}
 if args.prepare_only:
  stage=ROOT/'logs/endgame_prepared'
  for path,data in FILES.items():p=stage/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  (ROOT/'logs/endgame_prepared_record.json').write_text(json.dumps(record,indent=2)+'\n')
  print(f'Prepared {len(FILES)} files, {len(FOCUS)} focuses, {len(DECISIONS)+3} decisions, {len(EVENTS)} events. LIVE untouched.');return
 backup=ROOT/'logs'/('endgame_backup_'+datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(exist_ok=False)
 for path,data in sorted(FILES.items()):
  target=LIVE/path;assert target.resolve().is_relative_to(LIVE)
  if target.exists():b=backup/path;b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,b)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 launcher=LIVE.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(LIVE/'make_serbia_great_again.mod',launcher)
 record.update(backup=str(backup),deployed_absolute_paths=[str(LIVE/p) for p in sorted(FILES)]+[str(launcher)],deployed_sha256={p:sha(data) for p,data in FILES.items()})
 (ROOT/'docs/endgame_sources.json').write_text(json.dumps(record,indent=2)+'\n')
 print(f'Installed {len(FILES)} files LIVE. Validate LIVE before source sync.')

def create_art(ideas):
 """Convert supplied PNGs; replace inaccurate maps from native province geometry."""
 import numpy as np
 with ZipFile(PACK) as z:
  prefix=next(n.rsplit('/',1)[0]+'/' for n in z.namelist() if n.endswith('/ASSET_MANIFEST.json'))
  manifest=json.loads(z.read(prefix+'ASSET_MANIFEST.json'))
  if isinstance(manifest,dict):manifest=manifest.get('assets',manifest.get('entries'))
  images={};members={}
  for a in manifest:
   im=Image.open(io.BytesIO(z.read(prefix+a['source_file']))).convert('RGBA')
   images.setdefault(a['source_concept'],im);members.setdefault(a['source_concept'],prefix+a['source_file'])
  def source(concept):
   im=images[concept].copy()
   # Sheet fragments must be cropped to ONE scene, never include caption bars or other tiles.
   boxes={'federal_constitution':(0,0,144,69),'proclaim_federation':(0,0,144,69),'federal_yugoslavia':(0,0,144,68),'one_yugoslav_army':(0,0,144,68),'one_yugoslav_economy':(0,0,142,69),'price_of_victory':(0,0,137,69)}
   if concept in boxes:im=im.crop(boxes[concept])
   return im
  # Real TFR province pixels and state lists establish exact political-map boundaries.
  states={}
  for p in (TFR/'history/states').glob('*.txt'):
   a=get(parse(p.read_text(encoding='utf-8-sig',errors='replace')),'state');states[int(get(a,'id'))]=[int(k) for k,o,v in get(a,'provinces')]
  rgb=np.asarray(Image.open(TFR/'map/provinces.bmp').convert('RGB'))
  packed=(rgb[:,:,0].astype(np.uint32)<<16)|(rgb[:,:,1].astype(np.uint32)<<8)|rgb[:,:,2]
  lut=np.zeros(1<<24,dtype=np.uint16);water=np.zeros(1<<24,dtype=np.bool_)
  colors={}
  for line in (TFR/'map/definition.csv').read_text(encoding='utf-8-sig').splitlines():
   a=line.split(';')
   if len(a)<5:continue
   try:pid=int(a[0]);color=(int(a[1])<<16)|(int(a[2])<<8)|int(a[3])
   except ValueError:continue
   colors[pid]=color;water[color]=a[4]!='land'
  for sid,provinces in states.items():
   for pid in provinces:
    if pid in colors:lut[colors[pid]]=sid
  sidmap=lut[packed]
  selection=np.isin(sidmap,ALL_FEDERAL+[44,886]);yy,xx=np.nonzero(selection)
  box=(max(0,int(xx.min())-30),max(0,int(yy.min())-30),int(xx.max())+31,int(yy.max())+31)
  small=sidmap[box[1]:box[3],box[0]:box[2]];sea=water[packed[box[1]:box[3],box[0]:box[2]]]
  shape=small.shape;edge=np.zeros(shape,dtype=bool);edge[1:,:]|=small[1:,:]!=small[:-1,:];edge[:,1:]|=small[:,1:]!=small[:,:-1]
  maps={}
  for concept,red,blue in [('future_balkans',STATES['SER'],sum([STATES[t] for t in ['CRO','SLV','BOS','HRZ','MNT','MAC']],[])),('one_serbian_state',STATES['SER']+[105,106],[]),('consolidate_serbian_lands',STATES['SER']+[105,106],[]),('common_homeland',[],ALL_FEDERAL)]:
   out=np.zeros((*shape,4),dtype=np.uint8);out[:]=[92,88,78,255];out[sea]=[24,49,64,255];out[np.isin(small,blue)]=[75,108,155,255];out[np.isin(small,red)]=[166,62,65,255];out[edge&~sea]=[175,164,136,255]
   maps[concept]=Image.fromarray(out,'RGBA');images[concept]=maps[concept]
  preview=ROOT/'logs/endgame_native_map.png';maps['future_balkans'].resize((600,500)).save(preview)
  sprites=[]
  def save(path,im,size,concept,sprite,frame=0):
   canvas=Image.new('RGBA',size,(0,0,0,0));inner=(size[0]-frame*2,size[1]-frame*2)
   if path.startswith('gfx/event_pictures/'):
    fitted=ImageOps.fit(im,inner,method=Image.Resampling.LANCZOS)
   else:fitted=ImageOps.contain(im,inner,method=Image.Resampling.LANCZOS)
   canvas.alpha_composite(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2))
   if frame:ImageDraw.Draw(canvas).rectangle((0,0,size[0]-1,size[1]-1),outline=(22,24,27,255),width=frame)
   buf=io.BytesIO();canvas.save(buf,format='DDS',pixel_format='DXT5');data=buf.getvalue();assert data[84:88]==b'DXT5'
   FILES[path]=data;ASSETS[path]={'source_member':members[concept],'source_sha256':sha(z.read(members[concept])),'sha256':sha(data),'size':list(size),'compression':'DXT5','crop':'single scene; contain on transparent native canvas' if not path.startswith('gfx/event') else 'single scene, native event crop','native_map_geometry':concept in maps,'map_bbox':list(box) if concept in maps else None}
   sprites.append(f'spriteType = {{ name = "{sprite}" texturefile = "{path}" }}')
   return sprite
  # Manifest order is the approved focus order; IDs differ slightly from suggested artwork stems.
  assets_by_type={kind:[a for a in manifest if a['type']==kind] for kind in ['focus','decision','event']}
  assert [len(assets_by_type[k]) for k in ['focus','decision','event']]==[29,31,29]
  focus_art={}
  for (stem,*_),a in zip(FOCUS,assets_by_type['focus']):
   concept=a['source_concept'];focus_art[stem]=concept
   save('gfx/interface/goals/MSGA_endgame_'+stem+'.dds',source(concept),(95,85),concept,'GFX_MSGA_endgame_focus_'+stem)
   sprites.append(f'spriteType = {{ name = "GFX_MSGA_endgame_focus_{stem}_shine" texturefile = "gfx/interface/goals/MSGA_endgame_{stem}.dds" }}')
  # Focus list layout differs from archive order: match by normalized requested names.
  def normalized(s):return re.sub('[^a-z0-9]','',s.lower().replace('the ','').replace('a ',''))
  for stem,*_ in FOCUS:
   names={'future_of_the_south_slavs':'The Future of the South Slavs','montenegrin_question':'The Montenegrin Question','macedonian_question':'The Macedonian Question','the_greater_serbian_state':'The Greater Serbian State','a_serbian_century':'A Serbian Century','a_common_homeland':'A Common Homeland','one_people_one_state':'One People One State'}
   match=next(a for a in assets_by_type['focus'] if normalized(a['name'])==normalized(names.get(stem,stem.replace('_',' '))))
   concept=match['source_concept'];path='gfx/interface/goals/MSGA_endgame_'+stem+'.dds'
   # Replace the earlier slot association, keep exactly one definition per sprite.
   sprites[:]=[s for s in sprites if f'name = "GFX_MSGA_endgame_focus_{stem}"' not in s and f'name = "GFX_MSGA_endgame_focus_{stem}_shine"' not in s]
   save(path,source(concept),(95,85),concept,'GFX_MSGA_endgame_focus_'+stem)
   sprites.append(f'spriteType = {{ name = "GFX_MSGA_endgame_focus_{stem}_shine" texturefile = "{path}" }}')
  for (stem,name,*_),a in zip(DECISIONS,assets_by_type['decision']):
   concept=a['source_concept'];save('gfx/interface/decisions/MSGA_endgame_'+stem+'.dds',source(concept),(52,45),concept,'GFX_decision_MSGA_endgame_decision_'+stem,3)
  for a in assets_by_type['event']:
   stem=re.sub('[^a-z0-9]+','_',a['name'].lower()).strip('_');concept=a['source_concept']
   save('gfx/event_pictures/MSGA_endgame_'+stem+'.dds',source(concept),(500,250),concept,'GFX_MSGA_endgame_event_'+stem)
  save('gfx/event_pictures/MSGA_endgame_brotherhood_reforged.dds',source('brotherhood_reforged'),(500,250),'brotherhood_reforged','GFX_MSGA_endgame_event_brotherhood_reforged')
  for stem,(name,mod,concept) in ideas.items():save('gfx/interface/ideas/MSGA_endgame_'+stem+'.dds',source(concept),(64,64),concept,'GFX_idea_MSGA_endgame_idea_'+stem)
  for stem,concept in [('serbian_national_project','one_serbian_state'),('building_yugoslav_federation','common_homeland'),('future_regional_influence','belgrades_sphere')]:save('gfx/interface/decisions/MSGA_endgame_category_'+stem+'.dds',source(concept),(52,40),concept,'GFX_decision_category_MSGA_endgame_category_'+stem)
  put('interface/MSGA_endgame_assets.gfx','spriteTypes = {\n'+'\n'.join(sprites)+'\n}\n')
  for folder,size in [('',(82,52)),('medium/',(41,26)),('small/',(10,7))]:
   native=TFR/('gfx/flags/'+folder+'SER.tga');data=native.read_bytes()
   FILES['gfx/flags/'+folder+'SER_MSGA_GREATER_SERBIA.tga']=data
   im=Image.new('RGBA',size)
   draw=ImageDraw.Draw(im)
   for i,color in enumerate([(0,56,147,255),(255,255,255,255),(216,30,43,255)]):draw.rectangle((0,round(size[1]*i/3),size[0]-1,round(size[1]*(i+1)/3)-1),fill=color)
   buf=io.BytesIO();im.save(buf,format='TGA');FILES['gfx/flags/'+folder+'SER_MSGA_YUGOSLAV_FEDERATION.tga']=buf.getvalue()

if __name__=='__main__':main()
