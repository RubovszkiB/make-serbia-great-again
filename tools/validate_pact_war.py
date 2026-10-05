"""Installed wartime AST checks and deterministic models, NOT engine acceptance.

Capitulation is an EXTERNAL engine input. The model never generates surrender
from capital loss. Target-only end_wars follows the installed API documentation;
combat, peace conferences, AI calls, country restoration and save UI need HOI4.
"""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,math,re,subprocess,zipfile
from PIL import Image
from validate_phase1 import ROOT,parse,get,descend,unique
from validate_bosnia import TFR,GAME
from validate_encirclement import EncirclementModel
from implement_pact_war import COUNTRIES,SIDE,PEACE,wrap_native

TAGS=[c[0] for c in COUNTRIES]

class WarModel(EncirclementModel):
 def __init__(self,scripts,mod):
  super().__init__(scripts,mod)
  self.callback_root='MNT';self.callback_from='SER'
  self.rules={c:{} for c in self.flags};self.technology={c:set() for c in self.flags}
  self.metrics={c:{'stability':0.,'support':0.,'xp':0.} for c in self.flags}
  self.expirations={};self.native_fallbacks=0
  self.idea_ast={k:v for p,a in scripts.items() if p.startswith('common/ideas/') for _,_,b in a for _,_,d in b for k,_,v in d}
  self.faction_leader['MSGA_zagreb_tirana_pact']='CRO';self.faction_leader['MSGA_serbian_alliance']='SER'
  for c in TAGS:self.factions[c]='MSGA_zagreb_tirana_pact'
  for state,cores in self.native_state_cores.items():self.cores[state]=cores.copy()
  for c in ['SER','BOS','HRZ']:self.factions[c]='MSGA_serbian_alliance'
  self.flags['SER']|={'MSGA_pact_war_opened','MSGA_pact_planning_active'}
  self.wars={frozenset(('SER',c)) for c in TAGS}
  self.units=[(c,'Surviving '+c+' brigade',s) for c,s,*_ in COUNTRIES]+[('SER','Existing Kosovo Brigade',785)]
  self.execute(self.effects['MSGA_prepare_pact_campaign'])

 def condition(self,ast,scope='SER'):
  for k,o,v in ast:
   if k in ('ROOT','FROM'):ok=self.condition(v,self.callback_root if k=='ROOT' else self.callback_from)
   elif k in ('any_country','any_other_country'):
    ok=any(self.condition(v,c) for c in self.flags if c in self.exists and (k=='any_country' or c!=scope))
   elif k=='controller':ok=self.condition(v,self.controllers[scope])
   elif k=='has_war_together_with':
    def enemies(c):return {next(iter(w-{c})) for w in self.wars if c in w}
    ok=bool(enemies(scope)&enemies(v))
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
   if k in ('ROOT','FROM'):self.execute(v,self.callback_root if k=='ROOT' else self.callback_from)
   elif k in ('add_stability','add_war_support','army_experience'):
    field={'add_stability':'stability','add_war_support':'support','army_experience':'xp'}[k]
    self.metrics[scope][field]+=float(v)
   elif k=='set_country_flag' and isinstance(v,list):
    name=get(v,'flag');self.flags[scope].add(name);self.flag_dates[(scope,name)]=self.day
   elif k=='set_faction_leader':
    assert v=='yes' and self.factions[scope];self.faction_leader[self.factions[scope]]=scope
   elif k=='leave_faction':
    assert v=='yes';old=self.factions[scope];self.factions[scope]=None
    if self.faction_leader.get(old)==scope:
     assert not any(f==old for f in self.factions.values()),'Leaving leader stranded living members'
     self.faction_leader.pop(old,None)
   elif k=='set_autonomy':
    assert scope=='SER' and get(v,'autonomy_state')=='autonomy_puppet'
    assert get(v,'end_wars')=='yes' and get(v,'end_civil_wars')=='no'
    target=get(v,'target');assert 'MSGA_pact_real_capitulation' in self.flags[target]
    assert target in self.exists;self.subjects[target]=scope
    self.wars={w for w in self.wars if target not in w}
   elif k in ('set_rule','clear_rule'):
    for a,_,b in v:
     if a=='desc':continue
     if k=='set_rule':self.rules[scope][a]=b
     else:self.rules[scope].pop(a,None)
   elif k=='set_state_controller_to':self.controllers[scope]=v
   elif k=='every_country':
    for c in self.flags:
     if c in self.exists and self.condition(next((v for k,o,v in v if k=='limit'),[]),c):
      self.execute([x for x in v if x[0]!='limit'],c)
   elif k=='set_technology':
    for name,_,val in v:
     if name=='popup':continue
     assert name=='MSGA_highland_resistance_tech' and val in ('0','1')
     if val=='1':self.technology[scope].add(name)
     else:self.technology[scope].discard(name)
   elif k=='add_timed_idea':
    name=get(v,'idea');days=int(get(v,'days'));self.ideas[scope].add(name)
    self.expirations[(scope,name)]=self.day+days;self.timed.append((name,days))
   elif k=='remove_ideas':
    if v in self.ideas[scope]:
     self.ideas[scope].discard(v);self.expirations.pop((scope,v),None)
     self.execute(next((b for a,_,b in self.idea_ast.get(v,[]) if a=='on_remove'),[]),scope)
   elif k=='hidden_effect':self.execute(v,scope)
   else:super().execute([(k,o,v)],scope)

 def advance(self,days):
  # Advance the actual hidden-event queue and model native timed idea expiry.
  end=self.day+days
  while self.expirations and min(self.expirations.values())<=end:
   expiry=min(self.expirations.values());super().advance(expiry-self.day)
   for (c,name),date in list(self.expirations.items()):
    if date<=self.day:self.execute(parse('remove_ideas = '+name),c)
  super().advance(end-self.day)

 def callback(self,tag,winner='SER'):
  self.callback_root=tag;self.callback_from=winner
  body=get(get(self.scripts[PEACE][0][2],'on_capitulation'),'effect')
  if self.condition(get(get(body,'if'),'limit'),tag):self.execute(body[:1],tag)
  else:self.native_fallbacks+=1

def main():
 cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,required=True);cli.add_argument('--report',type=Path,default=ROOT/'docs/pact_war_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
 sources=json.loads((ROOT/'docs/pact_war_sources.json').read_text())
 original=subprocess.check_output(['git','show','d87f5c9:make_serbia_great_again/'+PEACE],cwd=ROOT).decode('utf-8-sig')
 assert scripts[PEACE]==parse(wrap_native(original)),'Native peace handler changed outside the exact narrow wrapper'
 handler=get(scripts['common/scripted_effects/MSGA_pact_war_effects.txt'],'MSGA_handle_pact_capitulation')
 assert handler[0]==parse('if = { limit = { NOT = { has_country_flag = MSGA_pact_real_capitulation } } set_country_flag = MSGA_pact_real_capitulation }')[0]
 assert hashlib.sha256((TFR/PEACE).read_bytes()).hexdigest()==sources['native_guard_override']['upstream_sha256']
 # All pre-existing files except the two documented script hooks and descriptors are byte-identical.
 allowed=set(sources['changed_relative_paths'])
 for path,digest in sources['baseline_sha256'].items():
  if path=='common/decisions/categories/MSGA_SER_categories.txt' and 'common/scripted_triggers/MSGA_new_order_triggers.txt' in scripts:
   old=parse(subprocess.check_output(['git','show','26a1e41:make_serbia_great_again/'+path],cwd=ROOT).decode('utf-8-sig'))
   assert scripts[path][:-1]==old and scripts[path][-1][0]=='MSGA_consolidate_the_serbian_sphere'
  elif path not in allowed:assert hashlib.sha256((mod/path).read_bytes()).hexdigest()==digest,path
 before_effect=parse(subprocess.check_output(['git','show','d87f5c9:make_serbia_great_again/common/scripted_effects/MSGA_encirclement_effects.txt'],cwd=ROOT).decode('utf-8-sig'))
 new_effect=copy.deepcopy(scripts['common/scripted_effects/MSGA_encirclement_effects.txt'])
 def remove_calls(body):
  return [(k,o,remove_calls(v) if isinstance(v,list) else v) for k,o,v in body if k not in ('MSGA_prepare_pact_campaign','MSGA_start_pact_observer') and (k,o,v)!=('NOT','=',parse('has_country_flag = MSGA_balkan_war_victory'))]
 assert remove_calls(new_effect)==before_effect
 # Native country capitals, state owner/core, province membership AND VP record.
 WarModel.native_state_cores={}
 for tag,state,province,*_ in COUNTRIES:
  country=parse(next((TFR/'history/countries').glob(tag+'*.txt')).read_text(encoding='utf-8-sig',errors='replace'));assert get(country,'capital')==str(state)
  body=get(parse(next((TFR/'history/states').glob(str(state)+'-*')).read_text(encoding='utf-8-sig',errors='replace')),'state');history=get(body,'history')
  assert ('owner','=',tag) in history and ('add_core_of','=',tag) in history
  WarModel.native_state_cores[state]={v for k,o,v in history if k=='add_core_of'}
  assert any(k==str(province) for k,o,v in get(body,'provinces'))
  assert any(k=='victory_points' and v[0][0]==str(province) and float(v[1][0])>0 for k,o,v in history)
 # Bind every supplied sprite to its exact DDS and every visible event to that sprite.
 gfx={get(v,'name').strip('"'):get(v,'texturefile').strip('"') for k,o,v in scripts['interface/MSGA_balkan_war_eventpictures.gfx'][0][2]}
 events={get(v,'id'):v for k,o,v in scripts['events/MSGA_pact_war_events.txt'] if k=='country_event'}
 assert set(events)=={f'MSGA_pactwar.{i}' for i in list(range(1,12))+[90]}
 for i,(tag,s,p,stem,city,img,cd,rd) in enumerate(COUNTRIES):
  for id,image in [(i*2+1,city+'_has_fallen'),(i*2+2,img)]:
   sprite='GFX_MSGA_event_'+image;assert get(events[f'MSGA_pactwar.{id}'],'picture')==sprite
   path=gfx[sprite];assert path=='gfx/event_pictures/MSGA_event_'+image+'.dds'
   record=sources['assets'][path];data=(mod/path).read_bytes()
   assert hashlib.sha256(data).hexdigest()==record['sha256']
   with zipfile.ZipFile(sources['package']) as z:assert data==z.read(record['zip_member'])
   with Image.open(mod/path) as image:assert image.size==(474,178);image.load()
 assert len(gfx)==10 and len(sources['assets'])==10
 # Verify triggers/effects against shipped engine docs; condition data is handled separately.
 docs={kind:(GAME/'documentation'/f'{kind}_documentation.md').read_text() for kind in ['triggers','effects','modifiers']}
 known={kind:set(re.findall(r'^## (\w+)',text,re.M)) for kind,text in docs.items()}
 custom={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
 def check_conditions(body):
  for k,o,v in body:
   if k in ('AND','OR','NOT','FROM','ROOT','controller','any_country','any_other_country') or k in TAGS+['SER'] or k.isdigit():check_conditions(v)
   else:assert k in known['triggers']|custom,(k,'unknown trigger')
 for path,ast in scripts.items():
  if 'pact_war' not in path:continue
  if path.startswith('common/scripted_triggers/'):
   for k,o,v in ast:check_conditions(v)
  for k,o,v in descend(ast):
   if k in ('trigger','limit','allow'):check_conditions(v)
   if k=='modifier' and path.startswith('common/ideas/'):
    for name,o,val in v:assert name in known['modifiers'] or name=='custom_modifier_tooltip',name
 for token in ['set_major','set_faction_leader','leave_faction','set_autonomy','set_state_controller_to','set_rule','clear_rule','set_technology']:
  assert token in known['effects'],token
 assert re.search(r'end_wars\s*=\s*yes',docs['effects'].split('## set_autonomy\n',1)[1].split('\n## ',1)[0])
 assert 'can_decline_call_to_war = no' in (TFR/'common/autonomous_states/puppet.txt').read_text()
 # Valid terrain syntax mirrors native hidden effect-only technologies.
 tech=get(get(scripts['common/technologies/MSGA_pact_war_technologies.txt'],'technologies'),'MSGA_highland_resistance_tech')
 assert get(tech,'allow')==parse('always = no')
 assert not any(k=='folder' for k,o,v in tech),'Do not expose an effect-only technology in research UI'
 native_units={k:v for file in (TFR/'common/units').glob('*.txt') for a,o,b in parse(file.read_text(encoding='utf-8-sig',errors='replace')) if a=='sub_units' for k,o,v in b}
 land={name for name,unit in native_units.items() if any(k=='categories' and any(a=='category_army' for a,o,b in v) for k,o,v in unit)}
 assert set(sources['land_units_with_terrain_bonus'])==land
 for name in land:assert get(tech,name)==parse('mountain = { defence = 0.10 }')
 native_terrain=(TFR/'common/technologies/land_doctrine.txt').read_text();assert re.search(r'mountain\s*=\s*\{[^}]*defence\s*=',native_terrain)
 every_new='\n'.join((mod/p).read_text(encoding='utf-8-sig') for p in allowed if p.endswith(('.txt','.gfx')) and p!=PEACE and 'encirclement_effects' not in p)
 words={k for k,o,v in descend(parse(every_new))}
 assert not words&{'white_peace','annex_country','set_state_owner','transfer_state','add_core_of','remove_core_of','delete_unit','load_oob','declare_war_on','add_to_war','set_surrender_progress','surrender_limit','max_surrender_limit_offset','remove_from_war','on_daily'}
 loc=(mod/'localisation/english/MSGA_pact_war_l_english.yml').read_text(encoding='utf-8-sig')
 assert (mod/'localisation/english/MSGA_pact_war_l_english.yml').read_bytes().startswith(b'\xef\xbb\xbf')
 for i in range(1,12):
  line=next(line for line in loc.splitlines() if line.startswith(f' MSGA_pactwar.{i}.d:'))
  assert line.count('\\n\\n')==1 and '\\\\n' not in line,(i,'two paragraphs required')
 EncirclementModel.unit_types=native_units
 cases=[]
 def effect(m,name):m.execute(m.effects[name])
 def flags(m):return {f'MSGA_{c[3]}_defeated' for c in COUNTRIES}&m.flags['SER']
 def cap(m,tag,winner='SER'):
  m.capitulated.add(tag);m.controllers[next(c[1] for c in COUNTRIES if c[0]==tag)]='SER'
  m.callback(tag,winner);effect(m,'MSGA_retry_pact_settlements');m.advance(0)
 # 120 defeat orders x three Serbian-side winners. Never fake capitals as capitulations.
 for order,winner in itertools.product(itertools.permutations(TAGS),['SER','BOS','GER']):
  m=WarModel(scripts,mod);owners=m.states.copy();cores=copy.deepcopy(m.cores);army=m.units.copy()
  if winner!='SER':
   m.factions[winner]=m.factions['SER'];m.wars|={frozenset((winner,t)) for t in TAGS}
  effect(m,'MSGA_start_pact_observer');assert set(TAGS)<=m.majors
  for n,tag in enumerate(order,1):
   # Occupy every capital without an engine surrender input.
   province=next(c[2] for c in COUNTRIES if c[0]==tag);m.provinces[province]=winner
   previous_wars=m.wars.copy();effect(m,'MSGA_scan_pact_capitals');effect(m,'MSGA_scan_pact_capitals');m.advance(0)
   assert m.wars==previous_wars and len(flags(m))==n-1 and tag not in m.subjects
   capital_id=next(i*2+1 for i,c in enumerate(COUNTRIES) if c[0]==tag)
   assert sum(id==f'MSGA_pactwar.{capital_id}' for day,c,id in m.delivered)==1
   cap(m,tag,winner)
   remaining=set(TAGS)-set(order[:n]);assert len(flags(m))==n
   assert m.subjects[tag]=='SER' and tag in m.exists and all(tag not in war for war in m.wars)
   assert all(frozenset(('SER',t)) in m.wars for t in remaining)
   assert all(t in m.majors for t in remaining),'Remaining enemies must count for engine all-majors rule'
   assert m.states==owners and m.cores==cores and m.units==army
   assert m.states[785]==m.states[1305]=='SER'
   assert ('MSGA_balkan_coalition_defeated' in m.flags['SER'])==(n==5)
   if remaining:
    assert m.factions[tag] is None and m.rules[tag]['can_decline_call_to_war']=='yes'
    assert 'MSGA_pact_postwar_neutrality' in m.ideas[tag]
    faction=m.factions[next(iter(remaining))];assert m.faction_leader[faction] in remaining
   before=(copy.deepcopy(m.metrics),copy.deepcopy(m.queue),m.wars.copy(),copy.deepcopy(m.subjects),m.native_fallbacks,m.flag_dates.copy())
   m.callback(tag,winner);effect(m,'MSGA_retry_pact_settlements');m.advance(0)
   assert before==(m.metrics,m.queue,m.wars,m.subjects,m.native_fallbacks,m.flag_dates),'Duplicate surrender changed result or fell through to native annexation'
   # Puppet restoration may clear the engine's capitulation boolean. A repeated
   # callback must still be consumed using recorded proof and subject status.
   m.capitulated.discard(tag);m.callback(tag,winner)
   assert m.native_fallbacks==before[-2] and m.flag_dates==before[-1],'Restored puppet fell through or refreshed capitulation date'
  assert sum(id=='MSGA_pactwar.11' for day,c,id in m.delivered)==1
  assert all(m.factions[t]==m.factions['SER'] for t in TAGS)
  for tag in TAGS:
   before=m.native_fallbacks;m.callback(tag,winner)
   assert m.native_fallbacks==before,'Late duplicate after final victory reached native annexation'
  m.advance(2);assert not any(id=='MSGA_pactwar.90' for day,c,id in m.queue)
  cases.append({'kind':'defeat_order','order':order,'winner':winner})
 # Independent capital orders, recapture, rewards exactly once and no subject transitions.
 for order in itertools.permutations(TAGS):
  m=WarModel(scripts,mod);wars=m.wars.copy()
  for tag in order:
   province=next(c[2] for c in COUNTRIES if c[0]==tag)
   m.provinces[province]='SER';effect(m,'MSGA_scan_pact_capitals');m.advance(0)
   m.provinces[province]=tag;effect(m,'MSGA_scan_pact_capitals');m.provinces[province]='SER';effect(m,'MSGA_scan_pact_capitals');m.advance(0)
  assert m.wars==wars and not flags(m) and not set(TAGS)&set(m.subjects)
  assert all(math.isclose(m.metrics['SER'][k],v) for k,v in {'stability':.1,'support':.28,'xp':65.}.items())
  assert len([id for day,c,id in m.delivered if id.startswith('MSGA_pactwar.')])==5
  m.advance(45);assert all('MSGA_highland_resistance_tech' not in m.technology[t] for t in TAGS)
  cases.append({'kind':'capital_order_and_expiry','order':order})
 # Negative context, callback proof, already-capitulated capitals, rollback/save recovery.
 for tag,state,province,stem,city,img,cd,rd in COUNTRIES:
  for negative in ['third_party','peace_subject','already_capitulated','capital_owned_but_not_controlled','no_campaign']:
   m=WarModel(scripts,mod);m.provinces[province]='GER'
   if negative=='peace_subject':m.subjects['GER']='SER'
   if negative=='already_capitulated':m.capitulated.add(tag);m.provinces[province]='SER'
   if negative=='capital_owned_but_not_controlled':m.states[state]='SER';m.provinces[province]=tag
   if negative=='no_campaign':m.flags['SER'].discard('MSGA_pact_war_opened');m.provinces[province]='SER'
   effect(m,'MSGA_scan_pact_capitals');assert 'MSGA_'+city+'_fallen' not in m.flags['SER'];assert not flags(m)
   cases.append({'kind':negative,'tag':tag})
  m=WarModel(scripts,mod);m.provinces[province]='SER';effect(m,'MSGA_scan_pact_capitals');effect(m,'MSGA_retry_pact_settlements')
  assert not flags(m) and tag not in m.subjects,'Capital control is not surrender proof'
  m.callback(tag);assert m.native_fallbacks==1 and not flags(m),'Callback without has_capitulated must not settle'
  m.capitulated.add(tag);m.callback(tag,'GER');assert not flags(m) and m.native_fallbacks==2,'Third-party victor must use native handler'
  m.wars.add(frozenset(('USA','GER')));cap(m,tag);assert frozenset(('USA','GER')) in m.wars
  recorded=m.flag_dates[(tag,'MSGA_pact_real_capitulation')];m.advance(1);m.callback(tag)
  assert m.flag_dates[(tag,'MSGA_pact_real_capitulation')]==recorded,'Late duplicate refreshed surrender evidence'
  assert 'MSGA_highland_resistance_tech' not in m.technology[tag]
  restored=copy.deepcopy(m);effect(restored,'MSGA_prepare_pact_campaign');effect(restored,'MSGA_retry_pact_settlements');effect(restored,'MSGA_start_pact_observer');effect(restored,'MSGA_start_pact_observer')
  assert len([id for day,c,id in restored.queue if id=='MSGA_pactwar.90'])==1
  cap_id=next(i*2+2 for i,c in enumerate(COUNTRIES) if c[0]==tag)
  assert sum(id==f'MSGA_pactwar.{cap_id}' for day,c,id in restored.delivered)==1
  cases.append({'kind':'guard_proof_duplicate_unrelated_war_recovery','tag':tag})
  m=WarModel(scripts,mod);cap(m,tag)
  assert 'MSGA_'+city+'_fallen' not in m.flags['SER'] and 'MSGA_'+stem+'_defeated' in m.flags['SER']
  assert not any(id==f'MSGA_pactwar.{cap_id-1}' for day,c,id in m.delivered)
  cases.append({'kind':'normal_capitulation_without_capital_event','tag':tag})
  m=WarModel(scripts,mod);m.wars.clear();effect(m,'MSGA_start_pact_observer')
  assert not any(id=='MSGA_pactwar.90' for day,c,id in m.queue)
  cases.append({'kind':'no_observer_after_external_peace','tag':tag})
 # Final requires actual surviving subjects, not merely forged five flags.
 for missing in TAGS:
  m=WarModel(scripts,mod)
  for tag,s,p,stem,*_ in COUNTRIES:
   m.flags['SER'].add('MSGA_'+stem+'_defeated');m.flags[tag].add('MSGA_pact_real_capitulation')
   m.subjects[tag]='SER';m.wars.discard(frozenset(('SER',tag)))
  del m.subjects[missing];effect(m,'MSGA_finish_pact_campaign');assert 'MSGA_balkan_coalition_defeated' not in m.flags['SER']
  cases.append({'kind':'final_missing_subject','tag':missing})
 # Preexisting majors are not demoted. Final faction admission deferred while unrelated war remains.
 m=WarModel(scripts,mod);m.flags['ALB'].discard('MSGA_pact_temporary_major');m.wars.add(frozenset(('SER','USA')))
 for tag in TAGS:cap(m,tag)
 assert 'ALB' in m.majors and frozenset(('SER','USA')) in m.wars
 assert all(m.factions[t] is None for t in TAGS)
 cases.append({'kind':'preserve_native_major_and_unrelated_serbian_war'})
 report={'validation':'passed','validated_mod_root':str(mod),'namespace':'MSGA_pactwar','visible_event_ids':[f'MSGA_pactwar.{i}' for i in range(1,12)],'observer':'MSGA_pactwar.90','verified_capitals':sources['capitals'],'artwork_files':10,'native_peace_wrapper':'original 0.11 AST byte-independent parity; native upstream hash unchanged','terrain_tech_land_unit_types':len(land),'capitulation_orders':120,'winner_variants':['SER','BOS subject','GER active faction ally'],'modeled_scenarios':len(cases),'cases':cases,'capital_capture_forces_capitulation':False,'target_autonomy':'autonomy_puppet, freedom 0.5, end_wars yes, end_civil_wars no','engine_acceptance':'NOT RUN: user reserved gameplay. Engine restoration, AI calls, peace conference order, rendering and save serialization require in-game testing. Model uses documented target-only war cancellation; normal combat casualties are not simulated.'}
 report['version']=get(parse((mod/'descriptor.mod').read_text()),'version').strip('"')
 args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))

if __name__=='__main__':main()
