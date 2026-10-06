"""Check installed pre-war chapter and execute actual scripts in a deterministic model.

This does not certify HOI4 combat, rendering, event UI, faction UI or engine saves.
"""
from pathlib import Path
from collections import Counter
import argparse,copy,hashlib,itertools,json,re,subprocess,zipfile
from PIL import Image
from validation_history import check_current_art
from validate_phase1 import ROOT,parse,get,descend,unique
from validate_post_bosnia import PostBosniaModel
from validate_bosnia import TFR,GAME
from implement_encirclement import MEMBERS,FOCUSES,EVENTS

class EncirclementModel(PostBosniaModel):
 def __init__(self,scripts,mod,leader='GER',mixed=False,low_manpower=True):
  super().__init__(scripts,mod)
  self.manpower={};self.manpower_added=Counter();self.fuel=0;self.direct_equipment=Counter();self.direct_manpower=Counter()
  self.majors={'CRO'}
  for tag in list(MEMBERS)+['ENG','FRA']:
   self.flags.setdefault(tag,set());self.ideas.setdefault(tag,set());self.factions.setdefault(tag,None);self.exists.add(tag)
  self.factions.update({'USA':'NATO','GER':'NATO','ENG':'NATO','FRA':'NATO'});self.faction_leader['NATO']=leader
  for tag,(state,province,mi,mo) in MEMBERS.items():
   self.factions[tag]='NATO' if not mixed or tag in ('CRO','SLV') else None
   self.states[state]=self.controllers[state]=tag;self.cores[state]={tag};self.provinces[province]=tag
   self.buildings[state]={'infrastructure':2};self.extra_slots[state]=0;self.modifiers[state]=set()
   self.ideas[tag].add('NATO_unity_2');self.flags[tag].add('has_joined_NATO_by_event')
  self.nato_members=set(MEMBERS)|{'GER','ENG','FRA'}
  self.manpower={t:0 if low_manpower else 100000 for t in self.flags}
  self.guarantees|={(g,t) for g in ('USA','GER','ENG') for t in MEMBERS}|{('FRA','SER'),('GER','BOS')}
  self.subjects={'BOS':'SER','HRZ':'SER'};self.exists.add('HRZ')
  for s,t in [(104,'BOS'),(851,'HRZ')]:self.states[s]=self.controllers[s]=t
  self.flags['SER'].add('MSGA_post_bosnia_started');self.tree='MSGA_SER_post_bosnia'
  self.focuses={'MSGA_the_serbian_question'}

 def condition(self,ast,scope='SER'):
  for k,o,v in ast:
   if k=='has_manpower':ok=self.manpower[scope]<float(v) if o=='<' else self.manpower[scope]>=float(v)
   elif k=='is_faction_leader':ok=(self.factions[scope] is not None and self.faction_leader.get(self.factions[scope])==scope)==(v=='yes')
   elif k=='any_other_country':ok=any(self.condition(v,c) for c in self.flags if c!=scope)
   elif k=='is_major':ok=(scope in self.majors)==(v=='yes')
   else:ok=super().condition([(k,o,v)],scope)
   if not ok:return False
  return True

 def execute(self,ast,scope='SER'):
  branch=False
  for k,o,v in ast:
   if k in ('if','else_if','else'):
    if k=='if':branch=False
    if not branch and (k=='else' or self.condition(get(v,'limit'),scope)):
     self.execute([x for x in v if x[0]!='limit'],scope);branch=True
    continue
   if k=='add_manpower':self.manpower[scope]+=int(v);self.manpower_added[scope]+=int(v)
   elif k=='set_major':
    if v=='yes':self.majors.add(scope)
    else:self.majors.discard(scope)
   elif k=='declare_war_on':
    assert scope=='SER' and get(v,'target')=='CRO' and get(v,'type')=='annex_everything'
    assert self.faction_leader[self.factions['CRO']]=='CRO' and not any(t in MEMBERS for g,t in self.guarantees)
    self.wars.add(frozenset(('SER','CRO')));self.trace.append(('declare','SER','CRO'))
   elif k=='add_to_war':
    assert frozenset(('SER','CRO')) in self.wars
    assert get(v,'targeted_alliance')=='CRO' and get(v,'enemy')=='SER' and get(v,'single_target_only')=='yes'
    assert self.factions[scope]==self.factions['CRO'] and self.faction_leader[self.factions['CRO']]=='CRO'
    self.wars.add(frozenset((scope,'SER')));self.trace.append(('join_pact_war',scope))
   elif k=='load_oob':
    super().execute([(k,o,v)],scope)
    body=parse((self.mod/'history/units'/f'{v}.txt').read_text())
    for a,_,unit in descend(body):
     if a!='division':continue
     template=self.templates[(scope,get(unit,'division_template'))]
     for battalion,_,pos in get(template,'regiments'):
      n=self.unit_types[battalion]
      self.direct_manpower[scope]+=int(get(n,'manpower'))
      for eq,_,amount in get(n,'need'):self.direct_equipment[(scope,eq)]+=int(amount)
   elif k=='add_fuel':self.fuel+=float(v)
   elif k=='add_building_construction':
    kind=get(v,'type');amount=int(get(v,'level'));self.buildings[scope][kind]=self.buildings[scope].get(kind,0)+amount
   else:super().execute([(k,o,v)],scope)

def main():
 cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,default=ROOT/'make_serbia_great_again');cli.add_argument('--report',type=Path,default=ROOT/'docs/encirclement_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
 sources=json.loads((ROOT/'docs/encirclement_sources.json').read_text())
 unit_types=get(parse((TFR/'common/units/infantry.txt').read_text()),'sub_units')
 EncirclementModel.unit_types={k:v for k,_,v in unit_types}
 assert get(EncirclementModel.unit_types['militia'],'combat_width')=='3' and get(EncirclementModel.unit_types['motorized'],'combat_width')=='3'
 tech=get(get(parse((TFR/'common/technologies/infantry.txt').read_text()),'technologies'),'motorised_infantry')
 assert ('enable_subunits','=',parse('motorized')) in tech
 for tag,(state,province,mi,mo) in {**MEMBERS,'SER':(107,11586,2,0)}.items():
  file=next((TFR/'history/countries').glob(tag+'*.txt'));country=parse(file.read_text(encoding='utf-8-sig',errors='replace'))
  assert get(country,'capital')==str(state)
  native=get(parse(next((TFR/'history/states').glob(str(state)+'-*')).read_text(encoding='utf-8-sig',errors='replace')),'state')
  assert ('add_core_of','=',tag) in get(native,'history') and ('owner','=',tag) in get(native,'history')
  assert any(k==str(province) for k,o,v in get(native,'provinces'))
  enabled={k for a,o,v in country if a=='set_technology' for k,o,v in v if v=='1'}
  assert 'infantry_weapons1' in enabled and (not mo or 'motorised_infantry' in enabled)
  oob=scripts[f'history/units/MSGA_{tag}_pact_emergency.txt'];templates={get(v,'name'):v for k,_,v in oob if k=='division_template'}
  units=[b for k,o,b in descend(oob) if k=='division'];assert len(units)==mi+mo
  for name,body in templates.items():
   motorized='Motorized' in name;n=4 if motorized else 3;battalion='motorized' if motorized else 'militia'
   assert get(body,'regiments')==parse(' '.join(f'{battalion} = {{ x = 0 y = {y} }}' for y in range(n)))
   assert not any(k=='support' for k,o,v in body)
  counts=Counter('motorized' if 'Motorized' in get(u,'division_template') else 'militia' for u in units)
  assert counts==Counter({'militia':mi,'motorized':mo})
  assert all(get(u,'location')==str(province) and get(u,'start_equipment_factor')=='1' and get(u,'start_manpower_factor')=='1' for u in units)
 # No unrelated native event changes: removing exactly three guards must reconstruct the native AST.
 for path,record in sources['native_guard_overrides'].items():
  data=(TFR/path).read_bytes();assert hashlib.sha256(data).hexdigest()==record['upstream_sha256']
  before=parse(data.decode('utf-8-sig'));after=copy.deepcopy(scripts[path])
  for k,o,v in after:
   if k=='country_event' and get(v,'id') in record['guards']:
    id=get(v,'id');expected=parse('NOT = { has_country_flag = MSGA_independent_pact_member }' if id=='nato.1' else 'NOT = { FROM = { has_country_flag = MSGA_independent_pact_member } }')
    assert get(v,'trigger')==expected;v.remove(('trigger','=',expected))
  assert after==before
 ai=(TFR/'common/ai_strategy/TFR_ai_strategy_USA_nato.txt').read_text();assert 'left_NATO' in ai
 native_effects=(TFR/'common/scripted_effects/TFR_scripted_effects_USA.txt').read_text();assert 'USA.USA_nato_members = THIS' in native_effects
 # Engine APIs in all new triggers/available/limits are real; nested data fields are not triggers.
 trigger_docs=(GAME/'documentation/triggers_documentation.md').read_text()
 known=set(re.findall(r'^## (\w+)',trigger_docs,re.M))
 # The engine generates state building-count triggers from registered building IDs.
 known.update(k for p in (TFR/'common/buildings').glob('*.txt') for a,o,v in parse(p.read_text(encoding='utf-8-sig')) if a=='buildings' for k,o,v in v)
 custom={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
 def check_conditions(body):
  for k,o,v in body:
   if k in ('AND','OR','NOT','owner','any_other_country') or k.isdigit() or k in MEMBERS or k=='SER':check_conditions(v)
   elif k in custom:continue
   else:assert k in known,(k,'undocumented trigger')
 for p,ast in scripts.items():
  if 'encirclement' in p or p.endswith(('MSGA_pact_diplomacy.txt','MSGA_pact_mobilisation.txt','MSGA_SER_southern_question.txt','MSGA_SER_pact_war_planning.txt')):
   if p.startswith('common/scripted_triggers/'):
    for k,o,v in ast:check_conditions(v)
   for k,o,v in descend(ast):
    if k in ('limit','available','trigger'):check_conditions(v)
 trees={get(v,'id'):v for p,a in scripts.items() if p.startswith('common/national_focus/') for k,o,v in a if k=='focus_tree'}
 southern={get(v,'id'):v for k,o,v in trees['MSGA_SER_southern_question'] if k=='focus'}
 planning={get(v,'id'):v for k,o,v in trees['MSGA_SER_pact_war_planning'] if k=='focus'}
 assert set(southern)=={'MSGA_pressure_podgorica','MSGA_pressure_skopje'} and len(planning)==10
 for stem,title,x,y,cost,parents,reward in FOCUSES:
  body={**southern,**planning}['MSGA_'+stem];assert get(body,'cost')==str(cost)
  actual=[get(b,'focus') for k,o,b in body if k=='prerequisite'];assert actual==['MSGA_'+p for p in parents]
  assert not any(k in ('bypass','mutually_exclusive','allow_branch') for k,o,v in body)
 all_new='\n'.join((mod/p).read_text(encoding='utf-8-sig') for p in sources['changed_relative_paths'] if p.endswith(('.txt','.gfx')) and not p.startswith('events/TFR_'))
 assert not any(word in all_new for word in ['cohesion','pact_collapses','cracks_in_pact','counteroffensive','element_of_surprise_lost','tirana_strikes_back','hold_vardar_line'])
 for path,record in sources['assets'].items():
  if check_current_art(mod/path,path):continue
  data=(mod/path).read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256']
  with zipfile.ZipFile(sources['package']) as z:assert data==z.read(record['zip_member'])
  assert Image.open(mod/path).size==((474,178) if '/event_pictures/' in path else (95,85) if '/goals/' in path else (60,68))
 assert len(sources['assets'])==25
 # Keep previous approved layouts, rewards and regional auxiliary templates byte-identical.
 for p in ['common/national_focus/MSGA_SER_post_bosnia.txt','history/units/MSGA_BOS_auxiliary_militias.txt','history/units/MSGA_HRZ_auxiliary_militias.txt','common/scripted_effects/MSGA_post_bosnia_auxiliaries.txt']:
  before=subprocess.check_output(['git','show','3b40283:make_serbia_great_again/'+p],cwd=ROOT);assert parse(before.decode('utf-8-sig'))==scripts[p]
 tested=[]
 def effect(m,name):m.execute(m.effects[name])
 def complete(m,body):
  assert m.condition(get(body,'available'))
  assert all(get(v,'focus') in m.focuses for k,o,v in body if k=='prerequisite')
  m.focuses.add(get(body,'id'));m.execute(get(body,'completion_reward'));m.advance(0)
 ideas={k:v for a,o,b in scripts['common/ideas/MSGA_encirclement_ideas.txt'] for c,o,d in b for k,o,v in d}
 assert get(ideas['MSGA_operation_thunder'],'modifier')==parse('planning_speed = 0.10 max_planning = 0.05 supply_consumption_factor = -0.05')
 assert get(ideas['MSGA_surprise_attack'],'modifier')==parse('army_attack_factor = 0.05 army_speed_factor = 0.05 breakthrough_factor = 0.05')
 assert get(ideas['MSGA_pact_diplomatic_independence'],'rule')==parse('can_join_factions = no')
 branches=[['prepare_western_front','secure_drina_corridor'],['prepare_southern_front','fortify_kosovo'],['call_up_reserves','stockpile_continental_war']]
 for order,leader,mixed,low,branch_order in itertools.product(itertools.permutations(southern),['USA','GER'],[False,True],[False,True],itertools.permutations(branches)):
  m=EncirclementModel(scripts,mod,leader,mixed,low)
  effect(m,'MSGA_open_southern_question');assert m.tree=='MSGA_SER_post_bosnia'
  m.flags['SER'].add('MSGA_regional_power_achieved');effect(m,'MSGA_open_southern_question')
  assert m.tree=='MSGA_SER_southern_question' and 'MSGA_the_serbian_question' in m.focuses
  complete(m,southern[order[0]]);m.advance(5);assert 'MSGA_calculation_failed' not in m.flags['SER']
  complete(m,southern[order[1]]);effect(m,'MSGA_schedule_calculation_failed');m.advance(2)
  assert m.tree=='MSGA_SER_southern_question' and 'MSGA_calculation_failed' not in m.flags['SER']
  m.advance(1);assert 'MSGA_calculation_failed' in m.flags['SER'] and not m.units
  assert all(m.factions[t]=='MSGA_zagreb_tirana_pact' for t in MEMBERS) and m.faction_leader['MSGA_zagreb_tirana_pact']=='CRO'
  assert all(m.factions[t]=='NATO' for t in ('USA','GER','ENG','FRA')) and m.faction_leader['NATO']==leader
  assert not(m.nato_members & set(MEMBERS)) and all('left_NATO' in m.flags[t] and 'has_joined_NATO_by_event' not in m.flags[t] and 'NATO_unity_2' not in m.ideas[t] for t in MEMBERS)
  assert {('FRA','SER'),('GER','BOS')} <= m.guarantees and not any(t in MEMBERS for g,t in m.guarantees)
  m.advance(1);assert m.tree=='MSGA_SER_pact_war_planning'
  assert Counter(t for t,n,p in m.units)==Counter({'CRO':7,'ALB':5,'SLV':4,'MAC':3,'MNT':3,'SER':2})
  assert m.buildings[107]['arms_factory']==1 and m.direct_manpower['SER']==6000
  assert sum(m.direct_manpower[t] for t in MEMBERS)==75000
  assert sum(m.direct_equipment[t,'infantry_equipment'] for t in MEMBERS)==15200
  assert sum(m.direct_equipment[t,'motorized_equipment'] for t in MEMBERS)==800
  assert sum(m.direct_equipment[t,'support_equipment'] for t in MEMBERS)==655
  assert not m.stock and not m.wars
  expected_added={t:mi*3000+mo*4800 for t,(s,p,mi,mo) in MEMBERS.items()}|{'SER':6000}
  assert all(m.manpower_added[t]==(amount if low else 0) for t,amount in expected_added.items())
  # Model a save that already raised the approved regional auxiliaries.
  m.execute(parse('load_oob = MSGA_BOS_auxiliary_militias load_oob = MSGA_HRZ_auxiliary_militias'))
  assert len([1 for t,n,p in m.units if t=='SER'])==6
  units=m.units[:]
  for name in ('MSGA_recover_pact_mobilisation','MSGA_belgrade_emergency','MSGA_mobilise_pact','MSGA_open_pact_planning'):effect(m,name)
  m.advance(0);assert m.units==units and m.buildings[107]['arms_factory']==1
  # Complete all three branches in dependency order, then merge and open the war.
  execution=['balkans_close_ranks']+[f for b in branch_order for f in b]+['coordinate_protectorates','serbian_war_plan','break_the_ring']
  for stem in execution:
   if stem=='break_the_ring':
    assert not m.wars and ('MSGA_operation_thunder',120) in m.timed and not any(i=='MSGA_surprise_attack' for i,d in m.timed)
    m.factions['GER']='MSGA_zagreb_tirana_pact';assert not m.condition(get(planning['MSGA_break_the_ring'],'available'))
    effect(m,'MSGA_open_pact_war');assert not m.wars
    m.factions['GER']='NATO'
   complete(m,planning['MSGA_'+stem])
  assert m.pp==105 and m.xp==40 and abs(m.support-.14)<.00001 and m.stability==-.05
  assert m.units==units and m.stock==Counter({'infantry_equipment_1':5000,'motorized_equipment_1':300,'support_equipment_1':150,'artillery_equipment_1':100}) and m.fuel==10000
  assert all(frozenset(('SER',t)) in m.wars for t in MEMBERS) and len(m.wars)==5
  assert ('MSGA_surprise_attack',10) in m.timed and ('MSGA_operation_thunder',120) in m.timed
  old=copy.deepcopy((m.wars,m.units,m.stock,m.timed,m.queue));effect(m,'MSGA_open_pact_war');assert old==(m.wars,m.units,m.stock,m.timed,m.queue)
  assert len([x for x in m.delivered if x[2]=='MSGA_encirclement.12'])==1 and not any(x[0]=='white_peace' for x in m.trace)
  tested.append({'rejection_order':list(order),'planning_branch_order':[b[0] for b in branch_order],'NATO_leader':leader,'mixed_actual_membership':mixed,'low_manpower':low,'result':'passed'})
 # Recovery after temporarily unsafe spawn locations, missing countries or external leadership.
 for reason in ['control','core','province','subject','leader','missing','war']:
  m=EncirclementModel(scripts,mod);m.flags['SER']|={'MSGA_regional_power_achieved','MSGA_calculation_failed'}
  effect(m,'MSGA_open_southern_question')
  if reason=='subject':m.subjects['CRO']='GER'
  if reason=='leader':m.faction_leader['NATO']='CRO'
  if reason=='missing':m.exists.discard('CRO')
  if reason=='war':m.wars.add(frozenset(('CRO','SOV')))
  if reason in ['subject','leader','missing','war']:
   effect(m,'MSGA_try_pact_realignment');assert 'MSGA_zagreb_tirana_pact_formed' not in m.flags['SER'] and m.factions['ALB']=='NATO'
   continue
  effect(m,'MSGA_try_pact_realignment')
  if reason=='control':m.controllers[109]='SOV'
  elif reason=='core':m.cores[109].clear()
  else:m.provinces[11581]='SOV'
  m.advance(1);assert not m.units and m.tree=='MSGA_SER_southern_question'
  m.controllers[109]='CRO';m.cores[109]={'CRO'};m.provinces[11581]='CRO'
  effect(m,'MSGA_recover_pact_mobilisation');m.advance(0);assert len(m.units)==24 and m.tree=='MSGA_SER_pact_war_planning'
 # Native pending invitations fail only for an independently realigned Pact member.
 native_events={get(v,'id'):v for k,o,v in scripts['events/TFR_events_ZZZ_NATO.txt'] if k=='country_event'}
 m=EncirclementModel(scripts,mod);assert m.condition(get(native_events['nato.1'],'trigger'),'CRO')
 m.flags['CRO'].add('MSGA_independent_pact_member');assert not m.condition(get(native_events['nato.1'],'trigger'),'CRO')
 for id in ['nato.2','nato.4']:
  trigger=get(native_events[id],'trigger');assert trigger==parse('NOT = { FROM = { has_country_flag = MSGA_independent_pact_member } }')
  # Substitute concrete FROM scope for this model; native script uses the real event sender.
  concrete=[(k,o,[(('CRO' if a=='FROM' else a),b,c) for a,b,c in v]) for k,o,v in trigger]
  assert not m.condition(concrete,'GER')
 # Incomplete prerequisites cannot start the war; no global unlock and no unrelated fighting.
 m=EncirclementModel(scripts,mod);effect(m,'MSGA_open_pact_war');assert not m.wars
 m=EncirclementModel(scripts,mod);m.flags['SER'].add('MSGA_regional_power_achieved')
 weekly=get(get(scripts['common/on_actions/MSGA_encirclement_on_actions.txt'],'on_actions'),'on_weekly')
 m.execute(get(weekly,'effect'));assert m.tree=='MSGA_SER_southern_question'
 for s in [785,1305]:m.buildings[s]['infrastructure']=5
 effect(m,'MSGA_fortify_kosovo_front');assert all(m.buildings[s]['infrastructure']==5 for s in [785,1305])
 report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'version':'0.11.0','trees':['MSGA_SER_southern_question','MSGA_SER_pact_war_planning'],'focus_count':12,'pressure_focus_days':14,'planning_focus_days':[7,7,7,7,7,7,7,7,14,7],'scenarios':tested,'additional_negative_and_recovery_cases':7,'NATO_cleanup':'actual faction leader, USA metadata, left_NATO, event guards, five unity spirits, only external guarantees of the five targets','spawns':sources['spawn_locations'],'total_Pact_units':22,'Serbian_emergency_units':2,'native_battalions':{'militia':3,'motorized':4},'native_widths':{'militia':9,'motorized':12},'full_OOB_equipment':{'Pact_infantry':15200,'Pact_motorized':800,'Pact_support':655,'Serbia_infantry':1200,'Serbia_support':30},'full_OOB_manpower':{'Pact':75000,'Serbia':6000},'free_stockpile_for_spawned_units':0,'safe_core_ownership_and_control_guards':'passed with blocked spawn and recovery','first_blow':True,'surprise_attack_days':10,'surprise_attack_modifiers':{'army_attack_factor':.05,'army_speed_factor':.05,'breakthrough_factor':.05},'later_war_or_postwar_content':False,'assets':25,'prior_auxiliary_units':'already Serbian owned; no duplicates in the model','gameplay_validation':'pending user; no engine test or fresh clean engine log certified'}
 report['version']=get(parse((mod/'descriptor.mod').read_text()),'version').strip('"')
 report['validation_scope']='0.11 pre-war chapter regression; later wartime content has its own validator'
 report['later_war_or_postwar_content_in_prewar_chapter']=report.pop('later_war_or_postwar_content')
 args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='scenarios'},indent=2));print(f'{len(tested)} full pre-war models passed; report: {args.report}')
if __name__=='__main__':main()
