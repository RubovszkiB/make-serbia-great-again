"""Validate LIVE chapter AST, native APIs and deterministic progression, not HOI4 gameplay."""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,math,re,subprocess,zipfile
from PIL import Image
from validation_history import expected_hash, check_current_art, approved_script
from validate_phase1 import ROOT,parse,get,descend,decision_presentation
from validate_pact_war import WarModel,COUNTRIES
from validate_encirclement import EncirclementModel
from validate_bosnia import TFR,GAME
from implement_new_order import CLIENTS,FOCUSES,ECONOMIC,STAGES,STAGE_VALUES,RAILS

class NewOrderModel(WarModel):
 def __init__(self,scripts,mod,separate_hrz=True,separate_srp=True):
  super().__init__(scripts,mod)
  self.variables={};self.flag_expirations={};self.jobs={};self.autonomy={};self.railways={tuple(p):2 for p in RAILS}
  self.wars=set();self.pp=1000;self.debt=4;self.money=10
  for tag,stem,*_ in CLIENTS:
   self.exists.add(tag);self.subjects[tag]='SER';self.autonomy[tag]=500
  for tag,state,province,stem,*_ in COUNTRIES:
   self.flags[tag].add('MSGA_pact_real_capitulation');self.flags['SER'].add('MSGA_'+stem+'_defeated')
  self.flags['SER'].add('MSGA_balkan_coalition_defeated')
  self.flags['SER']|={'MSGA_operation_thunder','MSGA_western_preparation','MSGA_southern_preparation'}
  self.ideas['SER']|={'MSGA_operation_thunder','MSGA_surprise_attack','native_economy','MSGA_serbian_commerce_restored_prior'}
  for tag,separate in [('HRZ',separate_hrz),('SRP',separate_srp)]:
   if not separate:self.exists.discard(tag);self.subjects.pop(tag,None)
  self.focus_ast={get(b,'id'):b for k,o,b in scripts['common/national_focus/MSGA_SER_new_balkan_order.txt'][0][2] if k=='focus'}
  self.decisions={k:b for k,o,b in scripts['common/decisions/MSGA_new_order_decisions.txt'][0][2]}

 def condition(self,ast,scope='SER'):
  for k,o,v in ast:
   if k=='check_variable' and get(v,'var').startswith('MSGA_'):
    value=self.variables.get((scope,get(v,'var')),0);target=float(get(v,'value'));cmp=get(v,'compare')
    ok=value>=target if cmp=='greater_than_or_equals' else value>target
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
   if k in ('set_variable','add_to_variable'):
    key=(scope,get(v,'var'));amount=float(get(v,'value'))
    self.variables[key]=amount if k=='set_variable' else self.variables.get(key,0)+amount
   elif k=='set_country_flag':
    name=get(v,'flag') if isinstance(v,list) else v
    self.flags[scope].add(name);self.flag_dates[(scope,name)]=self.day
    if isinstance(v,list):self.flag_expirations[(scope,name)]=self.day+int(get(v,'days'))
   elif k=='clr_country_flag':
    self.flags[scope].discard(v);self.flag_expirations.pop((scope,v),None)
   elif k=='add_autonomy_score':self.autonomy[scope]+=float(get(v,'value'))
   elif k=='build_railway':
    path=tuple(int(k) for k,o,v in get(v,'path'));assert path in self.railways
    self.railways[path]=max(self.railways[path],int(get(v,'level')))
   else:super().execute([(k,o,v)],scope)

 def effect(self,name):self.execute(self.effects[name])
 def ready(self,name):return self.condition(self.triggers[name])
 def focus_available(self,name):
  body=self.focus_ast['MSGA_'+name]
  return 'MSGA_'+name not in self.focuses and all(get(v,'focus') in self.focuses for k,o,v in body if k=='prerequisite') and self.condition(get(body,'available'))
 def focus(self,name):
  assert self.focus_available(name),('blocked focus',name,self.day)
  self.focuses.add('MSGA_'+name);self.execute(get(self.focus_ast['MSGA_'+name],'completion_reward'));self.advance(0)
 def start(self,stem):
  id='MSGA_regularise_'+stem;body=self.decisions[id]
  if id in self.jobs or not self.condition(get(body,'visible')) or not self.condition(get(body,'available')) or self.pp<float(get(body,'cost')):return False
  self.pp-=float(get(body,'cost'));self.jobs[id]=self.day+int(get(body,'days_remove'));self.execute(get(body,'complete_effect'));return True
 def advance(self,days):
  end=self.day+days
  while True:
   # Native cancel triggers are external existence/subject-state inputs.
   for id in list(self.jobs):
    if self.condition(get(self.decisions[id],'cancel_trigger')):
     self.jobs.pop(id);self.execute(get(self.decisions[id],'cancel_effect'))
   dates=[t[0] for t in self.queue]+list(self.expirations.values())+list(self.flag_expirations.values())+list(self.jobs.values())
   if not dates or min(dates)>end:break
   self.day=max(self.day,min(dates))
   # Leases outlive day-ten native completion; expire stale/orphan leases first.
   for (tag,flag),date in list(self.flag_expirations.items()):
    if date<=self.day:self.flags[tag].discard(flag);self.flag_expirations.pop((tag,flag))
   for (tag,idea),date in list(self.expirations.items()):
    if date<=self.day:self.execute(parse('remove_ideas = '+idea),tag)
   for id,date in list(self.jobs.items()):
    if date<=self.day:self.jobs.pop(id);self.execute(get(self.decisions[id],'remove_effect'))
   for item in sorted(list(self.queue)):
    if item not in self.queue or item[0]>self.day:continue
    self.queue.remove(item);date,scope,id=item;body=self.event_ast[id]
    if id in self.once_events or not self.condition(next((b for a,o,b in body if a=='trigger'),[]),scope):continue
    self.delivered.append(item)
    if ('fire_only_once','=','yes') in body:self.once_events.add(id)
    self.execute(next((b for a,o,b in body if a=='immediate'),[]),scope)
  self.day=end
 def victory(self):
  self.effect('MSGA_schedule_new_order_victory');self.advance(2);assert self.debt==4
  self.advance(1);assert self.debt==19 and self.tree=='MSGA_SER_new_balkan_order'
 def setup(self):self.victory();self.focus('count_the_cost');self.focus('begin_reconstruction')
 def recover(self,order):
  for i,stem in enumerate(order,1):
   self.focus(stem);assert set(STAGES)&self.ideas['SER']=={STAGES[i]}
   assert self.variables[('SER','MSGA_reconstruction_progress')]==i
 def clients(self,reverse=False):
  current=[c for c in CLIENTS if c[0] in self.exists and self.subjects.get(c[0])=='SER']
  for tag,stem,*_ in current[::(-1 if reverse else 1)]:
   pp=self.pp;assert self.start(stem) and self.pp==pp-25
   assert all(not self.start(s) for t,s,*_ in CLIENTS)
   self.advance(9);assert 'MSGA_'+stem+'_regularised' not in self.flags['SER']
   self.advance(1);assert 'MSGA_'+stem+'_regularised' in self.flags['SER']
   assert math.isclose(self.metrics[tag]['stability'],.10) and self.autonomy[tag]==450
   assert self.opinions[(tag,'SER')]=='MSGA_new_order_cooperation' and not self.start(stem)

def main():
 cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,required=True);cli.add_argument('--report',type=Path,default=ROOT/'docs/new_order_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
 scripts={p:decision_presentation(a) if p.startswith('common/decisions/') else a for p,a in scripts.items()}
 sources=json.loads((ROOT/'docs/new_order_sources.json').read_text());changed=set(sources['changed_relative_paths'])
 for path,digest in sources['baseline_sha256'].items():
  if path not in changed:assert hashlib.sha256((mod/path).read_bytes()).hexdigest()==expected_hash(path,digest),path
 for path,digest in sources['native_sources_sha256'].items():assert hashlib.sha256((TFR/path).read_bytes()).hexdigest()==digest,path
 cats='common/decisions/categories/MSGA_SER_categories.txt';pact='common/scripted_effects/MSGA_pact_war_effects.txt'
 prior=lambda p:parse(subprocess.check_output(['git','show','26a1e41:make_serbia_great_again/'+p],cwd=ROOT).decode('utf-8-sig'))
 assert scripts[cats][:-1]==[t for t in prior(cats) if t[0]!='MSGA_economic_development'] and scripts[cats][-1][0]=='MSGA_consolidate_the_serbian_sphere'
 assert hashlib.sha256((mod/cats).read_bytes()).hexdigest()==expected_hash(cats,'')
 def unhook(body):return [(k,o,unhook(v) if isinstance(v,list) else v) for k,o,v in body if k!='MSGA_schedule_new_order_victory']
 if approved_script(pact):
  assert hashlib.sha256((mod/pact).read_bytes()).hexdigest()==expected_hash(pact,'')
  assert [x for x in unhook(scripts[pact]) if x[0]!='MSGA_handle_pact_capitulation']==[x for x in prior(pact) if x[0]!='MSGA_handle_pact_capitulation']
 else:assert unhook(scripts[pact])==prior(pact)
 encirclement='common/scripted_effects/MSGA_encirclement_effects.txt'
 guarded=copy.deepcopy(scripts[encirclement]);opening=get(get(guarded,'MSGA_open_pact_planning'),'if');limit=get(opening,'limit')
 assert limit.count(('NOT','=',parse('has_country_flag = MSGA_balkan_war_victory')))==1
 limit.remove(('NOT','=',parse('has_country_flag = MSGA_balkan_war_victory')))
 assert guarded==prior(encirclement),'Other prewar effects changed'
 WarModel.native_state_cores={}
 EncirclementModel.unit_types=get(parse((TFR/'common/units/infantry.txt').read_text()),'sub_units');EncirclementModel.unit_types={k:v for k,o,v in EncirclementModel.unit_types}
 tree=scripts['common/national_focus/MSGA_SER_new_balkan_order.txt'][0][2];focuses={get(b,'id'):b for k,o,b in tree if k=='focus'}
 assert set(focuses)=={'MSGA_'+f[0] for f in FOCUSES};assert sum(int(get(b,'cost'))*7 for b in focuses.values())==105
 for stem,title,x,y,cost,parents in FOCUSES:
  b=focuses['MSGA_'+stem];assert [get(v,'focus') for k,o,v in b if k=='prerequisite']==['MSGA_'+p for p in parents]
  assert (get(b,'x'),get(b,'y'),get(b,'cost'))==tuple(map(str,(x,y,cost)))
 ideas={k:v for a,o,b in scripts['common/ideas/MSGA_new_order_ideas.txt'] for a,o,d in b for k,o,v in d}
 keys=['consumer_goods_factor','production_speed_buildings_factor','industrial_capacity_factory','income_growth_factor','industry_repair_factor']
 for stage,values in zip(STAGES,STAGE_VALUES):assert {k:float(v) for k,o,v in get(ideas[stage],'modifier')}==dict(zip(keys,values))
 assert float(get(get(ideas['MSGA_stabilised_client_order'],'modifier'),'autonomy_gain_global_factor'))==-.10
 assert get(get(ideas['MSGA_serbian_commerce_restored'],'modifier'),'business_value_factor')=='0.05'
 assert get(get(ideas['MSGA_serbian_commerce_restored'],'modifier'),'income_growth_factor')=='0.03'
 for k,o,b in scripts['common/decisions/MSGA_new_order_decisions.txt'][0][2]:
  assert get(b,'cost')=='25' and get(b,'days_remove')=='10'
  assert [get(v,'days') for k,o,v in get(b,'complete_effect') if k=='set_country_flag']==['11','11']
 assert not any(k=='autonomy_gain_global_factor' for k,o,v in get(ideas['MSGA_a_stabilised_balkan_order'],'modifier'))
 opinion=scripts['common/opinion_modifiers/MSGA_new_order_opinions.txt'];assert get(get(get(opinion,'opinion_modifiers'),'MSGA_new_order_cooperation'),'value')=='25'
 # Resolve all condition names and national-spirit modifiers against installed engine/TFR.
 known={kind:set(re.findall(r'^## (\w+)',(GAME/'documentation'/f'{kind}_documentation.md').read_text(),re.M)) for kind in ['triggers','effects','modifiers']}
 known['triggers'].add('infrastructure')
 custom={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
 native_mods={k for k,o,v in parse((TFR/'common/modifier_definitions/00_TFR_economic_modifiers_definition.txt').read_text())}
 def conditions(body):
  for k,o,v in body:
   if k in ('AND','OR','NOT','ROOT','FROM') or k in [c[0] for c in CLIENTS]+['SER'] or k.isdigit():conditions(v)
   else:assert k in known['triggers']|custom,(k,'invalid condition')
 for p,a in scripts.items():
  if 'new_order' not in p:continue
  if p.startswith('common/scripted_triggers/'):
   for k,o,v in a:conditions(v)
  for k,o,v in descend(a):
   if k in ('limit','available','visible','trigger','cancel_trigger','allowed','cancel'):conditions(v)
   if k=='modifier' and p.startswith('common/ideas/'):
    for name,o,value in v:assert name in known['modifiers']|native_mods|{'custom_modifier_tooltip'},name
 assert 'add_autonomy_score' in known['effects'] and 'build_railway' in known['effects']
 generic=parse((TFR/'common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt').read_text(encoding='utf-8-sig'))
 assert ('add_to_variable','=',parse('var = debt_var value = debt_var_temp')) in get(generic,'add_debt')
 assert ('add_to_variable','=',parse('var = industrial_development_var value = industrial_development_var_temp')) in get(generic,'add_industrial_development')
 assert all('2 4 '+' '.join(map(str,path)) in (TFR/'map/railways.txt').read_text() for path in RAILS)
 tokens={k for p,a in scripts.items() if 'new_order' in p for k,o,v in descend(a)}
 assert not tokens&{'annex_country','add_core_of','set_state_owner','transfer_state','delete_unit','load_oob','declare_war_on','create_faction','set_autonomy','add_income','add_debt_with_inflation','has_active_decision','replace_path'}
 with zipfile.ZipFile(sources['package']) as z:
  assert (mod/'interface/MSGA_new_balkan_order_assets.gfx').read_bytes()==z.read(next(n for n in z.namelist() if n.endswith('/interface/MSGA_new_balkan_order_assets.gfx')))
  for path,record in sources['assets'].items():
   if check_current_art(mod/path,path):continue
   data=(mod/path).read_bytes();assert data==z.read(record['zip_member']);assert hashlib.sha256(data).hexdigest()==record['sha256']
   with Image.open(mod/path) as image:assert list(image.size)==record['size'];image.load()
 assert len(sources['assets'])==30
 events={get(v,'id'):v for k,o,v in scripts['events/MSGA_new_order_events.txt'] if k=='country_event'}
 assert set(events)=={f'MSGA_neworder.{i}' for i in list(range(1,19))+[90,91]}
 sprites={get(v,'name').strip('"'):get(v,'texturefile').strip('"') for p,a in scripts.items() if p.startswith('interface/') for k,o,b in a if k=='spriteTypes' for k,o,v in b if k.lower()=='spritetype'}
 for id,body in events.items():
  if ('hidden','=','yes') in body:continue
  assert get(body,'picture') in sprites and (mod/sprites[get(body,'picture')]).is_file()
 loc=(mod/'localisation/english/MSGA_new_order_l_english.yml').read_text(encoding='utf-8-sig')
 for i in range(1,19):assert next(l for l in loc.splitlines() if l.startswith(f' MSGA_neworder.{i}.d:')).count('\\n\\n')==1
 cases=[]
 # All six recovery orders, dynamic Bosnia/Srp configurations and parallel activity orders.
 for order,hrz,srp,politics_first,reverse in itertools.product(itertools.permutations(ECONOMIC),[False,True],[False,True],[False,True],[False,True]):
  m=NewOrderModel(scripts,mod,hrz,srp);preserved=(m.states.copy(),copy.deepcopy(m.cores),m.units.copy(),m.subjects.copy())
  m.setup();assert m.money==10 and m.debt==19 and set(STAGES)&m.ideas['SER']=={STAGES[0]}
  assert 'native_economy' in m.ideas['SER'] and 'MSGA_operation_thunder' not in m.ideas['SER']
  if politics_first:
   m.clients(reverse);m.advance(1);assert 'MSGA_serbian_sphere_regularised' not in m.flags['SER']
   m.advance(1);assert 'MSGA_serbian_sphere_regularised' in m.flags['SER'] and not m.focus_available('stabilise_the_new_order');m.recover(order)
  else:
   m.recover(order);assert not m.focus_available('stabilise_the_new_order');m.clients(reverse)
   assert not m.focus_available('stabilise_the_new_order');m.advance(2)
  assert math.isclose(m.development,.20) and m.debt==19
  assert m.buildings[107]['industrial_complex']==m.buildings[107]['arms_factory']==m.buildings[107]['office_park']==1
  assert all(m.buildings[s]['infrastructure']==3 for s in [45,107,1296]) and set(m.railways.values())=={3}
  rewards=(copy.deepcopy(m.buildings),m.development,m.pp,m.debt)
  for stem in ['count_the_cost','begin_reconstruction']+list(order):m.effect('MSGA_new_order_'+stem)
  assert rewards==(m.buildings,m.development,m.pp,m.debt)
  checkpoint=copy.deepcopy(m);checkpoint.effect('MSGA_resume_new_order');assert checkpoint.focus_available('stabilise_the_new_order')
  checkpoint.flags['SER']|={'MSGA_zagreb_tirana_pact_formed','MSGA_pact_mobilised','MSGA_belgrade_emergency_done'}
  checkpoint.flags['SER'].discard('MSGA_pact_planning_active');checkpoint.effect('MSGA_open_pact_planning')
  assert checkpoint.tree=='MSGA_SER_new_balkan_order','Old startup must not reopen the planning tree'
  m.wars.add(frozenset(('SER','GER')));assert not m.focus_available('stabilise_the_new_order');m.wars.clear()
  m.focus('stabilise_the_new_order');assert not set(STAGES)&m.ideas['SER'] and 'MSGA_reconstruction_authority' not in m.ideas['SER']
  assert 'MSGA_a_stabilised_balkan_order' in m.ideas['SER']
  assert all('MSGA_stabilised_client_order' in m.ideas[t] for t in m.subjects)
  m.focus('the_south_slavic_question');assert m.focus_available('south_slavic_unity')
  assert 'MSGA_south_slavic_question_participant' not in m.flags['ALB']
  assert all('MSGA_south_slavic_question_participant' in m.flags[t] for t in m.subjects if t!='ALB')
  m.focus('south_slavic_unity');assert 'MSGA_south_slavic_unity_open' in m.flags['SER']
  assert 'MSGA_neworder.16' in m.once_events and preserved==(m.states,m.cores,m.units,m.subjects)
  m.effect('MSGA_resume_new_order');assert m.debt==19 and not set(STAGES)&m.ideas['SER']
  cases.append({'order':order,'separate_HRZ':hrz,'separate_SRP':srp,'politics_first':politics_first,'reverse_clients':reverse})
 # Entry must require each real defeat, subject relationship and engine-capitulation proof.
 for tag,state,province,stem,*_ in COUNTRIES:
  for missing in ['defeat','subject','proof']:
   m=NewOrderModel(scripts,mod)
   if missing=='defeat':m.flags['SER'].discard('MSGA_'+stem+'_defeated')
   elif missing=='subject':m.subjects.pop(tag)
   else:m.flags[tag].discard('MSGA_pact_real_capitulation')
   m.effect('MSGA_schedule_new_order_victory');m.advance(10);assert m.debt==4 and 'MSGA_balkan_war_victory' not in m.flags['SER']
 # War interrupt: queued victory never bypasses a fresh three-day peace interval.
 m=NewOrderModel(scripts,mod);m.wars.add(frozenset(('SER','GER')));m.effect('MSGA_resume_new_order');m.advance(10);assert m.debt==4
 m.wars.clear();m.effect('MSGA_schedule_new_order_victory');m.advance(2);m.wars.add(frozenset(('SER','GER')))
 m.execute(parse('clr_country_flag = MSGA_new_order_peace_ready'));m.advance(1);assert m.debt==4
 m.wars.clear();m.effect('MSGA_schedule_new_order_victory');m.advance(2);assert m.debt==4;m.advance(1);assert m.debt==19
 m.effect('MSGA_start_new_balkan_order');m.effect('MSGA_schedule_new_order_victory');m.advance(10);assert m.debt==19
 # Every cancel path releases its lock and cannot reward a departed target or affect another client.
 for tag,stem,*_ in CLIENTS:
  for loss in ['missing','independent']:
   m=NewOrderModel(scripts,mod);m.setup();assert m.start(stem);m.advance(4)
   if loss=='missing':m.exists.discard(tag)
   else:m.subjects.pop(tag)
   m.advance(0);assert not m.jobs and 'MSGA_regularisation_active' not in m.flags['SER']
   assert 'MSGA_'+stem+'_regularised' not in m.flags['SER'] and m.autonomy[tag]==500
   assert m.start(next(s for t,s,*_ in CLIENTS if t!=tag))
   m.effect('MSGA_release_regularisation_'+stem);assert 'MSGA_regularisation_active' in m.flags['SER']
 # Old callback after lease expiry must not unlock a new process.
 m=NewOrderModel(scripts,mod);m.setup();assert m.start('croatia');m.advance(10);assert m.start('slovenia')
 m.effect('MSGA_finish_regularising_croatia');assert 'MSGA_regularisation_active' in m.flags['SER'] and len(m.jobs)==1
 # Recovery from an externally lost native job: no permanently orphaned lock.
 orphan=NewOrderModel(scripts,mod);orphan.setup();assert orphan.start('croatia');orphan.jobs.clear()
 orphan.advance(10);assert not orphan.start('slovenia');orphan.advance(1);assert orphan.start('slovenia')
 # Infrastructure cap and wartime ownership; rails cannot downgrade higher levels.
 m=NewOrderModel(scripts,mod);m.setup();m.buildings[45]['infrastructure']=5;m.controllers[1296]='GER';m.railways[tuple(RAILS[0])]=5
 m.focus(ECONOMIC[0]);assert m.buildings[45]['infrastructure']==5 and m.buildings[1296]['infrastructure']==2 and list(m.railways.values())==[5,2]
 # Cancel queued conference during war, then recover automatically at peace.
 m=NewOrderModel(scripts,mod);m.setup();m.clients();m.wars.add(frozenset(('SER','GER')));m.advance(2)
 assert 'MSGA_serbian_sphere_regularised' not in m.flags['SER'];m.wars.clear();m.effect('MSGA_resume_new_order');m.advance(2)
 assert 'MSGA_serbian_sphere_regularised' in m.flags['SER'] and not m.focus_available('stabilise_the_new_order')
 # Subject helper cancellation follows the actual idea cancel trigger.
 m.subjects.pop('CRO');assert m.condition(get(ideas['MSGA_stabilised_client_order'],'cancel'),'CRO')
 # Buildings fall back to controlled Serbia instead of constructing in occupied Belgrade.
 fallback=NewOrderModel(scripts,mod);fallback.setup();fallback.controllers[107]='GER'
 fallback.focus('restore_serbian_industry');fallback.focus('restart_serbian_commerce')
 for building in ['industrial_complex','arms_factory','office_park']:
  assert fallback.buildings[107].get(building,0)==0 and sum(b.get(building,0) for b in fallback.buildings.values())==1
 poor=NewOrderModel(scripts,mod);poor.setup();poor.pp=24;assert not poor.start('croatia') and not poor.jobs
 wrong=NewOrderModel(scripts,mod);wrong.execute(wrong.effects['MSGA_start_new_balkan_order'],'CRO');assert wrong.debt==4
 timed=NewOrderModel(scripts,mod);timed.setup();timed.advance(121)
 assert 'MSGA_reconstruction_authority' not in timed.ideas['SER'] and set(STAGES)&timed.ideas['SER']=={STAGES[0]} and timed.debt==19
 gate=NewOrderModel(scripts,mod);gate.setup();gate.recover(ECONOMIC);gate.clients();gate.advance(2)
 for tag,stem,*_ in CLIENTS:
  flag='MSGA_'+stem+'_regularised';gate.flags['SER'].remove(flag)
  assert not gate.focus_available('stabilise_the_new_order');gate.flags['SER'].add(flag)
 report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'version':'0.13.0','focus_count':8,'focus_days':105,'scenarios':cases,'additional_negative_cases':36,'debt_B':15,'treasury_cost_B':0,'native_industrial_progress_total':.20,'decision_cost_PP':25,'decision_days':10,'simultaneous_client_decisions':1,'regularisation_flags':['MSGA_'+s+'_regularised' for t,s,*_ in CLIENTS],'assets':30,'conference':'2 days after all current clients regularised; independent economic gate retained','territory_subjects_armies_preserved':True,'Albania_outside_South_Slavic_question':True,'engine_validation':'Pending user; AST models do not certify UI, native timer order, AI, save reload or engine economy ticks'}
 report['additional_negative_cases']=49
 report['chapter_version']=report['version'];report['version']=re.search(r'^version="([^"]+)"',(mod/'descriptor.mod').read_text(),re.M)[1]
 args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n');print(f'LIVE New Balkan Order validated: {len(cases)} progression cases plus {report["additional_negative_cases"]} negative/cancellation/timing cases. Engine test pending user.')

if __name__=='__main__':main()
