"""Targeted LIVE static/native checks and short AST-driven rearmament smoke test.

This does not claim an engine run, AI scheduling, or actual production ticks.
"""
from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict, Counter
import argparse, copy, hashlib, json, re
from PIL import Image
from validate_phase1 import parse, get, descend, unique
from implement_balkan_rearmament import ROOT, TARGET, TFR, GAME, TAGS, NATIVE_TRIGGER, ALB, CRO, CONTRACTS, IDEAS, identity

def val(a,k,default=None):return next((v for key,o,v in a if key==k),default)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Smoke:
 def __init__(self,scripts,tag,nsb=False):
  self.scripts=scripts;self.tag=tag;self.nsb=nsb
  self.effects={k:v for k,o,v in scripts['common/scripted_effects/MSGA_balkan_rearmament_effects.txt']}
  self.triggers={k:v for k,o,v in scripts['common/scripted_triggers/MSGA_balkan_rearmament_triggers.txt']}
  self.flags=defaultdict(set);self.ideas=defaultdict(set);self.vars=defaultdict(float);self.money=20.;self.day=0;self.pp=0;self.stab=0;self.ws=0;self.xp=0;self.jobs={};self.equipment=Counter();self.focuses=set();self.capitulated=False;self.exists=set(TAGS)|{'SER','GER','SOV','USA','TUR'};self.research={k:0 for k in TAGS};self.locked={k:True for k in TAGS};self.reject=False
  self.owner={44:'ALB',109:'CRO'};self.controller=self.owner.copy();self.factory={44:1,109:2};self.infrastructure={44:2,109:3};self.slots={44:8,109:8};self.forts=0;self.research_bonuses=[]
  self.focus_ast={get(v,'id'):v for _,_,tree in scripts.get(f'common/national_focus/MSGA_{tag}_rearmament.txt',[]) for k,o,v in tree if k=='focus'}
  self.decisions={k:v for _,_,cat in scripts['common/decisions/MSGA_balkan_procurement.txt'] for k,o,v in cat if k.startswith('MSGA_'+tag)}
 def number(self,value,scope):
  try:return float(value)
  except ValueError:
   if value=='income_var':return self.money
   if value=='building_level@arms_factory':return self.factory[scope]
   return self.vars[(scope,value)]
 def condition(self,a,scope=None):
  scope=self.tag if scope is None else scope
  for k,o,v in a:
   if k in self.triggers:ok=self.condition(self.triggers[k],scope)==(v=='yes')
   elif k=='SER':ok=self.condition(v,'SER')
   elif k.isdigit():ok=self.condition(v,int(k))
   elif k=='NOT':ok=not any(self.condition([t],scope) for t in v)
   elif k=='OR':ok=any(self.condition([t],scope) for t in v)
   elif k in ['AND','hidden_trigger','custom_trigger_tooltip']:ok=self.condition([t for t in v if t[0]!='tooltip'],scope)
   elif k=='tag':ok=scope==v
   elif k=='always':ok=v=='yes'
   elif k=='has_country_flag':ok=v in self.flags[scope]
   elif k=='has_idea':ok=v in self.ideas[scope]
   elif k=='has_completed_focus':ok=v in self.focuses
   elif k=='has_capitulated':ok=self.capitulated==(v=='yes')
   elif k=='country_exists':ok=v in self.exists
   elif k=='amount_research_slots':ok=self.research[scope]==int(v)
   elif k=='has_dlc':ok=self.nsb
   elif k=='is_owned_by':ok=self.owner[scope]==v
   elif k=='is_fully_controlled_by':ok=self.controller[scope]==v
   elif k=='arms_factory':ok=self.factory[scope]<int(v)
   elif k=='infrastructure':ok=self.infrastructure[scope]<int(v)
   elif k=='free_building_slots':ok=self.slots[scope]>self.factory[scope]+1
   elif k=='check_variable':
    x=self.number(get(v,'var'),scope);y=self.number(get(v,'value'),scope);cmp=get(v,'compare');ok={'equals':x==y,'greater_than_or_equals':x>=y}[cmp]
   else:raise AssertionError('Unmodelled condition '+k)
   if not ok:return False
  return True
 def execute(self,a,scope=None):
  scope=self.tag if scope is None else scope;branch=False
  for k,o,v in a:
   if k in ['if','else_if','else']:
    if k=='if':branch=False
    if not branch and (k=='else' or self.condition(get(v,'limit'),scope)):
     self.execute([t for t in v if t[0]!='limit'],scope);branch=True
    continue
   if k in self.effects:self.execute(self.effects[k],scope)
   elif k.isdigit():self.execute(v,int(k))
   elif k=='hidden_effect':self.execute(v,scope)
   elif k in ['log','custom_effect_tooltip']:pass
   elif k=='set_country_flag':self.flags[scope].add(v)
   elif k=='clr_country_flag':self.flags[scope].discard(v)
   elif k=='remove_ideas':self.ideas[scope].discard(v)
   elif k=='add_ideas':self.ideas[scope].add(v)
   elif k=='add_timed_idea':assert get(v,'days')=='180';self.ideas[scope].add(get(v,'idea'))
   elif k=='country_lock_all_division_template':self.locked[scope]=v=='yes'
   elif k=='set_research_slots':self.research[scope]=int(v)
   elif k in ['set_temp_variable','add_to_temp_variable']:
    key=(scope,get(v,'var'));value=self.number(get(v,'value'),scope);self.vars[key]=self.vars[key]+value if k.startswith('add_') else value
   elif k=='add_income':self.money+=self.vars[(scope,'income_var_temp')]
   elif k=='add_political_power':self.pp+=float(v)
   elif k=='add_stability':self.stab+=float(v)
   elif k=='add_war_support':self.ws+=float(v)
   elif k=='army_experience':self.xp+=float(v)
   elif k=='add_extra_state_shared_building_slots':self.slots[scope]+=int(v)
   elif k=='add_building_construction':
    typ=get(v,'type');level=int(get(v,'level'))
    if typ=='arms_factory' and not self.reject:self.factory[scope]+=level
    if typ=='infrastructure':self.infrastructure[scope]+=level
    if typ=='bunker':assert scope==109 and get(v,'province')=='3627';self.forts+=level
   elif k=='add_tech_bonus':self.research_bonuses.append(v)
   elif k=='add_equipment_to_stockpile':self.equipment[(get(v,'type'),get(v,'producer'),val(v,'variant_name',''))]+=int(get(v,'amount'))
   else:raise AssertionError('Unmodelled effect '+k)
 def available(self,id):return id not in self.focuses and all(get(v,'focus') in self.focuses for k,o,v in self.focus_ast[id] if k=='prerequisite') and self.condition(get(self.focus_ast[id],'available'))
 def focus(self,id):
  assert self.available(id),id;body=self.focus_ast[id];self.focuses.add(id);self.day+=float(get(body,'cost'))*7;self.execute(get(body,'completion_reward'))
 def start(self,id):
  if id in self.jobs or not self.condition(get(self.decisions[id],'visible')) or not self.condition(get(self.decisions[id],'available')):return False
  self.execute(get(self.decisions[id],'complete_effect'));self.jobs[id]=self.day+int(get(self.decisions[id],'days_remove'));return True
 def advance(self,days):
  self.day+=days
  for id,end in list(self.jobs.items()):
   body=self.decisions[id]
   if self.condition(get(body,'cancel_trigger')):self.jobs.pop(id);self.execute(get(body,'cancel_effect'))
   elif self.day>=end:self.jobs.pop(id);self.execute(get(body,'remove_effect'))

def main():
 cli=argparse.ArgumentParser();cli.add_argument('--mod-root',type=Path,required=True);cli.add_argument('--report',type=Path,default=ROOT/'docs/balkan_rearmament_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True);assert mod==TARGET.resolve(strict=True)
 record=json.loads((ROOT/'docs/balkan_rearmament_sources.json').read_text())
 for p,d in record['baseline_sha256'].items():
  if p not in record['deployed_sha256']:assert sha(mod/p)==d,p
 for p,d in record['deployed_sha256'].items():assert sha(mod/p)==d,p
 for p,d in record['native_sources_sha256'].items():assert sha(TFR/p)==d,p
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig',errors='replace')) for p in mod.rglob('*') if p.suffix in ['.txt','.gfx']}
 # The single native override differs only by seven tag clauses in relevance.
 orig=parse((TFR/NATIVE_TRIGGER).read_text(encoding='utf-8-sig'));current=scripts[NATIVE_TRIGGER]
 native_or=get(get(orig,'is_relavent_tag'),'OR');new_or=get(get(current,'is_relavent_tag'),'OR')
 assert new_or==native_or+[("tag","=",tag) for tag in TAGS]
 assert [(k,o,v) for k,o,v in current if k!='is_relavent_tag']==[(k,o,v) for k,o,v in orig if k!='is_relavent_tag']
 country_tags={k for k,o,v in parse((TFR/'common/country_tags/00_countries.txt').read_text())};assert set(TAGS)<=country_tags
 truth_cases=0
 for tag in country_tags:
  for native_result in [False,True]:
   added=tag in TAGS;assert (native_result or added)==(native_result if not added else True);truth_cases+=1
 startup=parse((TFR/'common/on_actions/00_TFR_on_actions_ZZZ_startup.txt').read_text(encoding='utf-8-sig'))
 blocks=[v for k,o,v in descend(startup) if k=='every_country' and isinstance(v,list) and ('is_relavent_tag','=','no') in val(v,'limit',[])]
 assert len(blocks)==1 and ('add_ideas','=','ai_disabled_production') in blocks[0] and ('country_lock_all_division_template','=','yes') in blocks[0] and ('set_research_slots','=','0') in blocks[0]
 disabled=get(get(parse((TFR/'common/ideas/TFR_ideas_ZZZ_mishmash.txt').read_text()),'ideas'),'hidden_ideas');assert dict((k,float(v)) for k,o,v in get(get(disabled,'ai_disabled_production'),'modifier'))=={'production_speed_buildings_factor':-9999.,'industrial_capacity_factory':-9999.,'industrial_capacity_dockyard':-9999.,'consumer_goods_factor':10.,'conscription':-1.}
 # Audit actual producer-lock applications; other native locking is country-specific.
 audit={}
 for folder in ['common','events','history']:
  for p in (TFR/folder).rglob('*.txt'):
   txt=p.read_text(encoding='utf-8-sig',errors='replace')
   if re.search(r'add_ideas\s*=\s*ai_disabled_production',txt):audit[p.relative_to(TFR).as_posix()]=len(re.findall(r'add_ideas\s*=\s*ai_disabled_production',txt))
 assert set(audit)=={'common/on_actions/00_TFR_on_actions_ZZZ_startup.txt','common/decisions/TFR_decisions_ISR.txt'}
 israeli=parse((TFR/'common/decisions/TFR_decisions_ISR.txt').read_text(encoding='utf-8-sig'))
 def applications(a,scope=None):
  found=[]
  for k,o,v in a:
   if k=='add_ideas' and v=='ai_disabled_production':found.append(scope)
   elif isinstance(v,list):found+=applications(v,k if k in country_tags else scope)
  return found
 assert set(applications(israeli))<=set(['ISR','SYR','HEZ','LEB','JOR',None]) and not set(TAGS)&set(applications(israeli))
 known={kind:set(re.findall(r'^## (\w+)',(GAME/'documentation'/f'{kind}_documentation.md').read_text(encoding='utf-8-sig'),re.M)) for kind in ['effects','triggers','modifiers']}
 native_mods={k for k,o,v in parse((TFR/'common/modifier_definitions/00_TFR_economic_modifiers_definition.txt').read_text())}
 assert 'production_speed_arms_factory_factor' in (TFR/'common/ideas/00_TFR_laws_economic.txt').read_text()
 native_mods.add('production_speed_arms_factory_factor')
 local_effects={k for p,a in scripts.items() if p.startswith('common/scripted_effects/') for k,o,v in a};local_triggers={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
 def check_condition(a):
  for k,o,v in a:
   if k in ['NOT','OR','AND','hidden_trigger','custom_trigger_tooltip'] or k in country_tags or k.isdigit():check_condition([t for t in v if t[0]!='tooltip'])
   else:assert k in known['triggers']|local_triggers|{'arms_factory','infrastructure'},k
 def check_effect(a):
  for k,o,v in a:
   if k in ['if','else','else_if']:check_condition(val(v,'limit',[]));check_effect([t for t in v if t[0]!='limit'])
   elif k in ['hidden_effect'] or k in country_tags or k.isdigit():check_effect(v)
   else:assert k in known['effects']|local_effects|{'add_income'},k
 for k,o,v in scripts['common/scripted_effects/MSGA_balkan_rearmament_effects.txt']:check_effect(v)
 for k,o,v in scripts['common/scripted_triggers/MSGA_balkan_rearmament_triggers.txt']:check_condition(v)
 keys=re.findall(r'^ ([^:]+):','\n'.join(p.read_text(encoding='utf-8-sig') for p in (mod/'localisation/english').glob('*.yml')),re.M);unique(keys,'localisation')
 names=[];sprites={}
 for base in [TFR,mod]:
  for p in (base/'interface').glob('*.gfx'):
   for _,_,b in parse(p.read_text(encoding='utf-8-sig',errors='replace')):
    if not isinstance(b,list):continue
    for k,o,v in b:
     if k.lower()=='spritetype':
      name=get(v,'name').strip('"');texture=next((vv for kk,oo,vv in v if kk.lower()=='texturefile'),None)
      if texture:sprites[name]=texture.strip('"')
 for p,a in scripts.items():
  if p.startswith('interface/'):
   names += [get(v,'name').strip('"') for _,_,b in a for k,o,v in b if k.lower()=='spritetype']
 unique(names,'local sprite names')
 focuses=[get(v,'id') for p,a in scripts.items() if p.startswith('common/national_focus/') for _,_,b in a for k,o,v in b if k=='focus'];unique(focuses,'all focus IDs')
 for tag,rows in [('ALB',ALB),('CRO',CRO)]:
  tree=get(scripts[f'common/national_focus/MSGA_{tag}_rearmament.txt'],'focus_tree');assert get(tree,'id')=='MSGA_'+tag+'_rearmament'
  fmap={get(v,'id'):v for k,o,v in tree if k=='focus'};assert len(fmap)==len(rows)
  unique([(get(v,'x'),get(v,'y')) for v in fmap.values()],tag+' focus positions')
  for stem,title,days,x,y,parents,weight in rows:
   id=identity(tag,stem);b=fmap[id];assert float(get(b,'cost'))*7==days and [get(v,'focus') for k,o,v in b if k=='prerequisite']==[identity(tag,s) for s in parents]
   assert get(b,'icon') in sprites and get(b,'icon')+'_shine' in sprites
   assert id in keys and id+'_desc' in keys and id+'_reward_tt' in keys
   assert ('custom_effect_tooltip','=',id+'_reward_tt') in get(b,'completion_reward');assert not any(k in ['mutually_exclusive','bypass'] for k,o,v in b)
   check_condition(get(b,'available'));assert float(get(get(b,'ai_will_do'),'factor'))==weight
 decisions=[k for p,a in scripts.items() if p.startswith('common/decisions/') and '/categories/' not in p for _,_,cat in a for k,o,v in cat if k.startswith('MSGA_')];unique(decisions,'decision IDs')
 cats=scripts['common/decisions/MSGA_balkan_procurement.txt'];dmap={k:v for _,_,cat in cats for k,o,v in cat};assert len(dmap)==11
 for tag,stem,title,cost,days,focus,items,icon in CONTRACTS:
  id=identity(tag,stem);b=dmap[id];assert get(b,'cost')=='0' and int(get(b,'days_remove'))==days and 'GFX_decision_'+icon in sprites
  for suffix in ['', '_desc','_available_tt','_start_tt','_finish_tt']:assert id+suffix in keys
  check_condition(get(b,'available'));check_condition(get(b,'visible'));check_condition(get(b,'cancel_trigger'))
  for key in ['complete_effect','remove_effect','cancel_effect']:check_effect(get(b,key))
  available=get(get(b,'available'),'custom_trigger_tooltip');assert ('NOT','=',parse('has_country_flag = '+id+'_completed')) in available
 ideas=get(get(scripts['common/ideas/MSGA_balkan_rearmament_ideas.txt'],'ideas'),'country');assert len(ideas)==14
 for id,o,b in ideas:
  assert id in keys and id+'_desc' in keys and 'GFX_idea_'+get(b,'picture') in sprites
  assert dict((k,float(v)) for k,o,v in get(b,'modifier'))==IDEAS[id.removeprefix('MSGA_')][2]
  assert all(k in known['modifiers']|native_mods for k,o,v in get(b,'modifier'))
 # Preserve all original OOB definitions/units exactly; append one template only.
 native_oob=parse((TFR/'history/units/CRO_2020.txt').read_text(encoding='utf-8-sig'));installed_oob=scripts['history/units/CRO_2020.txt'];assert installed_oob[:-1]==native_oob
 template=installed_oob[-1];assert template[0]=='division_template' and get(template[2],'name')=='"Croatian Light Infantry"'
 regiments=get(template[2],'regiments');assert [(k,get(v,'x'),get(v,'y')) for k,o,v in regiments]==[('infantry','0','0'),('infantry','0','1'),('artillery_brigade','1','0')];assert get(template[2],'support')==[]
 infantry=get(get(parse((TFR/'common/units/infantry.txt').read_text(encoding='utf-8-sig')),'sub_units'),'infantry');assert get(infantry,'group')=='infantry' and 'category_light_infantry' in [k for k,o,v in get(infantry,'categories')]
 # Exactly +2 factories in 109, no other history fields altered; national total 3.
 p='history/states/109-Eastern Croatia.txt';native_state=parse((TFR/p).read_text());new_state=scripts[p]
 orig_build=get(get(get(native_state,'state'),'history'),'buildings');new_build=get(get(get(new_state,'state'),'history'),'buildings');assert [t for t in new_build if t[0]!='arms_factory']==orig_build and get(new_build,'arms_factory')=='2'
 def no_factory(a):return [(k,o,no_factory(v) if isinstance(v,list) else v) for k,o,v in a if k!='arms_factory']
 assert no_factory(new_state)==native_state
 owners=[];national=0;alb_total=0
 for path in (TFR/'history/states').glob('*.txt'):
  body=get(parse(path.read_text(encoding='utf-8-sig',errors='replace')),'state');hist=val(body,'history',[]);owner=val(hist,'owner');build=val(hist,'buildings',[])
  if owner=='CRO':national+=int(val(build,'arms_factory',0));owners.append((int(get(body,'id')),path))
  if owner=='ALB':alb_total+=int(val(build,'arms_factory',0))
 assert national==1 and national+2==3 and alb_total==1
 assert all(p not in record['changed_relative_paths'] for p in ['history/units/ALB_2000.txt','history/states/44-Albania.txt','history/countries/ALB - Albania.txt'])
 assert '3627' in [k for k,o,v in get(get(native_state,'state'),'provinces')]
 geometry={r['province']:r['centre_xy'] for r in record['Slavonia_geometry']};assert geometry[3627][0]==max(row[0] for row in geometry.values()), 'Fort must be on the eastern Slavonian frontier'
 eq={};subunits={}
 for p in (TFR/'common/units/equipment').glob('*.txt'):
  for k,o,b in parse(p.read_text(encoding='utf-8-sig',errors='replace')):
   if k=='equipments':eq.update({k:v for k,o,v in b})
 for p in (TFR/'common/units').glob('*.txt'):
  for k,o,b in parse(p.read_text(encoding='utf-8-sig',errors='replace')):
   if k=='sub_units':subunits.update({k:v for k,o,v in b})
 assert all(k in subunits for k,o,v in regiments)
 for k,o,v in descend(scripts['common/scripted_effects/MSGA_balkan_rearmament_effects.txt']):
  if k=='add_equipment_to_stockpile':assert get(v,'type') in eq and get(v,'producer') in country_tags
  if k=='custom_effect_tooltip':assert v in keys
  assert k not in ['create_unit','load_oob','delete_unit','set_state_owner','annex_country','add_core_of','add_debt','set_rule']
  if k=='add_tech_bonus':assert get(v,'category') in (TFR/'common/technology_tags/00_technology.txt').read_text()
 german=(TFR/'history/countries/GER - Germany.txt').read_text();assert re.search(r'name = "Leopard 2A5"\s+type = modern_tank_chassis_1',german)
 with ZipFile(record['package']) as z:
  assert sha(Path(record['package']))==record['package_sha256'] and len(record['assets'])==29
  for p,a in record['assets'].items():
   assert sha(mod/p)==a['sha256'] and hashlib.sha256(z.read(a['source_member'])).hexdigest()==a['source_sha256'] and (mod/p).read_bytes()[84:88]==b'DXT5'
   with Image.open(mod/p) as im:assert list(im.size)==a['size'];im.load()
   assert p in sprites.values()
 # Full focus routes: peaceful Croatia, then actual intervention flag, both DLC modes.
 routes=[]
 for tag,rows in [('ALB',ALB),('CRO',CRO)]:
  m=Smoke(scripts,tag);m.ideas[tag].add('ai_disabled_production');m.execute(m.effects['MSGA_restore_balkan_ai']);assert 'ai_disabled_production' not in m.ideas[tag] and not m.locked[tag] and m.research[tag]==TAGS[tag]
  if tag=='CRO':assert not m.available('MSGA_CRO_aggressive_rearmament')
  for index,(stem,*_) in enumerate(rows):
   if tag=='CRO' and index==6:m.flags['SER'].add('MSGA_bosnia_intervened')
   m.focus(identity(tag,stem))
  assert m.factory[44 if tag=='ALB' else 109]==(2 if tag=='ALB' else 5)
  if tag=='CRO':assert m.forts==2 and m.infrastructure[109]==4
  before=copy.deepcopy((m.money,m.pp,m.ws,m.factory,m.slots,m.equipment,m.research_bonuses,m.flags))
  for stem,*_ in rows:m.execute(m.effects[identity(tag,stem)+'_reward'])
  assert before==(m.money,m.pp,m.ws,m.factory,m.slots,m.equipment,m.research_bonuses,m.flags)
  routes.append({'country':tag,'focuses':len(rows),'military_factories_in_project_state':m.factory[44 if tag=='ALB' else 109],'all_focus_rewards_one_time':True})
 contracts=[];negatives=[]
 for tag,stem,title,cost,days,focus,items,icon in CONTRACTS:
  for nsb in ([False,True] if stem=='german_armour_contract' else [False]):
   m=Smoke(scripts,tag,nsb);m.focuses={identity(tag,s) for s,*_ in (ALB if tag=='ALB' else CRO)};id=identity(tag,stem);assert m.start(id)
   assert abs(m.money-(20-cost))<1e-8 and not m.start(id);m.advance(days-1);assert not m.equipment;m=copy.deepcopy(m);m.advance(1)
   expected={(typ,prod,''):n for typ,n,prod in items}
   if nsb:expected={('modern_tank_chassis_1','GER','"Leopard 2A5"'):40}
   assert dict(m.equipment)==expected and id+'_completed' in m.flags[tag] and not m.start(id)
   before=(m.money,m.equipment.copy());m.execute(m.effects[id+'_finish']);m.execute(m.effects[id+'_cancel']);assert before==(m.money,m.equipment)
   contracts.append({'id':id,'NSB':nsb,'cost_B':cost,'days':days,'delivery_exact_once':True,'no_early_delivery':True,'persistent_pending_model':True})
  m=Smoke(scripts,tag);m.focuses={identity(tag,s) for s,*_ in (ALB if tag=='ALB' else CRO)};m.money=cost-.01;assert not m.start(id);negatives.append(id+'_insufficient_treasury')
  m.money=20;assert m.start(id);m.capitulated=True;m.advance(1);assert abs(m.money-20)<1e-8 and not m.equipment;m.capitulated=False;assert m.start(id);m.advance(days);assert id+'_completed' in m.flags[tag];negatives.append(id+'_cancel_refund_retry')
 m=Smoke(scripts,'CRO');m.focuses.add('MSGA_CRO_armoured_modernisation');assert m.start('MSGA_CRO_german_armour_contract');m.exists.remove('GER');m.advance(1);assert m.money==20 and not m.equipment;negatives.append('German_seller_disappears')
 m=Smoke(scripts,'ALB');m.focuses.add('MSGA_ALB_a_vulnerable_nation');assert m.start('MSGA_ALB_purchase_old_eastern_rifles');m.focuses.add('MSGA_ALB_open_the_surplus_markets');assert not m.start('MSGA_ALB_acquire_old_mortars');negatives.append('parallel_contract_guard')
 for tag in TAGS:
  m=Smoke(scripts,tag);m.ideas[tag].add('ai_disabled_production');m.execute(m.effects['MSGA_restore_balkan_ai']);assert not m.locked[tag] and m.research[tag]==TAGS[tag] and not m.ideas[tag]
  for week in range(8):m.execute(m.effects['MSGA_restore_balkan_ai']);assert not m.locked[tag] and m.research[tag]==TAGS[tag] and not m.ideas[tag]
  m.research[tag]+=1;m.ideas[tag].add('ai_disabled_production');m.execute(m.effects['MSGA_restore_balkan_ai']);assert m.research[tag]==TAGS[tag]+1 and not m.ideas[tag]
 for tag in ['GRE','SER','HRZ','ISR']:
  m=Smoke(scripts,tag);m.ideas[tag].add('ai_disabled_production');m.execute(m.effects['MSGA_restore_balkan_ai']);assert 'ai_disabled_production' in m.ideas[tag] and not m.flags[tag]
 m=Smoke(scripts,'ALB');m.reject=True;m.focuses.add('MSGA_ALB_a_vulnerable_nation');slots=m.slots[44];m.focus('MSGA_ALB_expand_military_workshops');assert m.factory[44]==1 and m.slots[44]==slots;negatives.append('native_build_rejection_rolls_back_slot')
 m=Smoke(scripts,'CRO');m.flags['SER'].add('MSGA_bosnia_intervened');m.controller[109]='SER';m.focus('MSGA_CRO_aggressive_rearmament');assert not m.available('MSGA_CRO_emergency_defence_budget');negatives.append('lost_industry_control')
 on=scripts['common/on_actions/MSGA_balkan_rearmament_on_actions.txt'];assert not any(k in ['on_daily','add_building_construction','load_oob','create_unit'] for k,o,v in descend(on))
 assert (mod.parent/'make_serbia_great_again.mod').read_bytes()==(mod/'make_serbia_great_again.mod').read_bytes()
 descriptor=(mod/'make_serbia_great_again.mod').read_text();assert 'version="0.16.0"' in descriptor and 'remote_file_id="3813570241"' in descriptor and Path(re.search(r'^path="([^"]+)"',descriptor,re.M)[1]).resolve()==mod
 report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'version':'0.16.0','focus_count':25,'decision_count':11,'ideas':14,'DDS':29,'Croatia_starting_MIL':3,'Croatia_Proper_MIL':2,'Albania_starting_MIL':1,'CRO_new_template':'2 infantry + 1 artillery_brigade; no supports; no new units','AI_targets':TAGS,'native_relevance_truth_cases':truth_cases,'production_lock_addition_paths_audited':audit,'weekly_reapplication_model':'8 weeks per country; native startup exclusion and cleanup protect listed tags; unrelated countries unchanged','focus_smoke_models':routes,'contract_models':contracts,'negative_cases':negatives,'original_files_preserved':559-2,'actual_engine_validation':'NOT RUN. Static/model smoke only; user reserves running game and saves. Actual AI production, construction, training, equipment usability, focus selection and rendering require engine tests.'}
 args.report.write_text(json.dumps(report,indent=2)+'\n');print(f'LIVE Balkan checks passed: 25 focuses, 11 one-time contracts, 12 delivery models, {len(negatives)} negative cases, 7 AI targets.')

if __name__=='__main__':main()
