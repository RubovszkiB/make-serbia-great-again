"""Targeted LIVE syntax/API/art and executable-AST checks; no engine claim."""
from pathlib import Path
from collections import defaultdict,Counter
from zipfile import ZipFile
import argparse,copy,hashlib,json,math,re,subprocess
from PIL import Image
from validate_phase1 import parse,get,descend,unique,ROOT,decision_presentation
from validate_bosnia import TFR,GAME
from validation_history import expected_hash

def val(body,name,default=None):return next((v for k,o,v in body if k==name),default)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Model:
 """Execute chapter AST. Combat, native ticks, annex UI and rendering are external."""
 def __init__(self,scripts,mod,source,borders=False,balanced=False):
  self.scripts=scripts;self.mod=mod;self.source=source
  self.effects={k:v for p,a in scripts.items() if p.startswith('common/scripted_effects/') for k,o,v in a}
  self.triggers={k:v for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
  self.focus_ast={get(v,'id'):v for k,o,v in scripts['common/national_focus/MSGA_SER_endgame.txt'][0][2] if k=='focus'}
  self.decisions={k:v for cat,o,a in scripts['common/decisions/MSGA_endgame_decisions.txt'] for k,o,v in a}
  self.events={get(v,'id'):v for k,o,v in scripts['events/MSGA_endgame_events.txt'] if k=='country_event'}
  self.exists={'SER','CRO','SLV','BOS','HRZ','MNT','MAC','ALB','BUL','ROM','GRE'}
  self.subjects={t:'SER' for t in ['CRO','SLV','BOS','HRZ','MNT','MAC','ALB']}
  self.flags=defaultdict(set);self.ideas=defaultdict(set);self.variables=defaultdict(float);self.cores=defaultdict(set)
  self.flags['SER']={'MSGA_south_slavic_unity_open','MSGA_new_balkan_order_stabilised','MSGA_balkan_war_victory','MSGA_srpska_united'}
  self.states={s:t for t,ids in source['native_states'].items() for s in ids}
  self.states.update({44:'ALB',886:'ALB',777:'BUL'});self.controllers=self.states.copy();self.wars=set()
  self.focuses=set();self.pp=10000.;self.debt=19.;self.money=10.;self.day=0;self.jobs={};self.seen=set();self.queue=[]
  self.buildings=defaultdict(lambda:defaultdict(int));self.slots=defaultdict(int);self.armies=Counter({t:2 for t in self.subjects});self.stockpiles=Counter({t:1000 for t in self.subjects})
  self.compliance=defaultdict(float);self.resistance=defaultdict(float);self.autonomy=defaultdict(lambda:500.);self.xp=0;self.stability=0;self.support=0;self.development=0;self.cosmetic=None;self.capital=107;self.leader='SER_Aleksandar_Vucic';self.tree='MSGA_SER_new_balkan_order';self.build_reject=False
  self.choices={'MSGA_endgame.19':1 if borders else 0,'MSGA_endgame.23':1 if balanced else 0}
 def number(self,value,scope):
  try:return float(value)
  except ValueError:
   if value.startswith('building_level@'):return self.buildings[scope][value.split('@')[1]]
   return self.variables[(scope,value)]
 def condition(self,ast,scope='SER'):
  for k,o,v in ast:
   if k in self.triggers:ok=self.condition(self.triggers[k],scope)==(v=='yes')
   elif re.fullmatch('[A-Z]{3}',k) and k not in ['AND','NOT']:ok=self.condition(v,k)
   elif k.isdigit():ok=self.condition(v,int(k))
   elif k=='OR':ok=any(self.condition([t],scope) for t in v)
   elif k in ['AND','custom_trigger_tooltip']:ok=self.condition([t for t in v if t[0]!='tooltip'],scope)
   elif k=='NOT':ok=not any(self.condition([t],scope) for t in v)
   elif k=='tag':ok=scope==v
   elif k=='always':ok=v=='yes'
   elif k=='has_country_flag':ok=v in self.flags[scope]
   elif k=='has_completed_focus':ok=v in self.focuses
   elif k=='exists':ok=(scope in self.exists)==(v=='yes')
   elif k=='country_exists':ok=v in self.exists
   elif k=='has_war':ok=any(scope in w for w in self.wars)==(v=='yes')
   elif k=='is_subject_of':ok=self.subjects.get(scope)==v
   elif k=='state':ok=scope==int(v)
   elif k=='any_owned_state':ok=any(self.condition(v,s) for s,t in self.states.items() if t==scope)
   elif k=='is_owned_by':ok=self.states[scope]==v
   elif k=='is_fully_controlled_by':ok=self.controllers[scope]==v
   elif k=='is_core_of':ok=v in self.cores[scope]
   elif k=='check_variable':
    a=self.variables[(scope,get(v,'var'))];b=self.number(get(v,'value'),scope);cmp=get(v,'compare')
    ok={'greater_than':a>b,'greater_than_or_equals':a>=b,'equals':a==b}[cmp]
   elif k in ['infrastructure','industrial_complex','arms_factory','office_park']:ok=self.buildings[scope][k]<float(v)
   else:raise AssertionError('Unmodelled condition '+k)
   if not ok:return False
  return True
 def execute(self,ast,scope='SER'):
  branch=False
  for k,o,v in ast:
   if k in ['if','else_if','else']:
    if k=='if':branch=False
    if not branch and (k=='else' or self.condition(get(v,'limit'),scope)):
     self.execute([t for t in v if t[0]!='limit'],scope);branch=True
    continue
   if k in self.effects:self.execute(self.effects[k],scope)
   elif re.fullmatch('[A-Z]{3}',k):self.execute(v,k)
   elif k.isdigit():self.execute(v,int(k))
   elif k=='hidden_effect':self.execute(v,scope)
   elif k in ['custom_effect_tooltip','log']:pass
   elif k=='set_country_flag':self.flags[scope].add(v)
   elif k=='clr_country_flag':self.flags[scope].discard(v)
   elif k in ['add_ideas','remove_ideas']:
    self.ideas[scope].add(v) if k=='add_ideas' else self.ideas[scope].discard(v)
   elif k=='add_timed_idea':self.ideas[scope].add(get(v,'idea'))
   elif k in ['set_temp_variable','set_variable','add_to_variable']:
    key=(scope,get(v,'var'));amount=self.number(get(v,'value'),scope)
    self.variables[key]=self.variables[key]+amount if k=='add_to_variable' else amount
   elif k=='add_debt':self.debt+=self.variables[(scope,'debt_var_temp')]
   elif k=='add_industrial_development':self.development+=self.variables[(scope,'industrial_development_var_temp')]
   elif k=='add_political_power':self.pp+=float(v)
   elif k=='add_stability':
    if scope=='SER':self.stability+=float(v)
   elif k=='add_war_support':self.support+=float(v)
   elif k=='army_experience':self.xp+=float(v)
   elif k=='add_compliance':self.compliance[scope]+=float(v)
   elif k=='add_resistance':self.resistance[scope]+=float(v)
   elif k=='add_autonomy_score':self.autonomy[scope]+=float(get(v,'value'))
   elif k=='annex_country':
    t=get(v,'target');assert t!='ALB' and get(v,'transfer_troops')=='yes'
    assert self.subjects.get(t)==scope and t in self.exists and not self.wars
    for s,owner in self.states.copy().items():
     if owner==t:self.states[s]=self.controllers[s]=scope
    self.armies[scope]+=self.armies.pop(t);self.stockpiles[scope]+=self.stockpiles.pop(t);self.exists.remove(t);self.subjects.pop(t);self.ideas[t].clear()
   elif k=='transfer_state':self.states[int(v)]=self.controllers[int(v)]=scope
   elif k=='add_core_of':self.cores[scope].add(v)
   elif k=='add_extra_state_shared_building_slots':self.slots[scope]+=int(v)
   elif k=='add_building_construction':
    if not self.build_reject:self.buildings[scope][get(v,'type')]+=int(get(v,'level'))
   elif k=='every_country':
    for c in list(self.exists):
     if self.condition(val(v,'limit',[]),c):self.execute([t for t in v if t[0]!='limit'],c)
   elif k=='set_cosmetic_tag':self.cosmetic=v
   elif k=='set_capital':self.capital=int(get(v,'state'))
   elif k=='load_focus_tree':self.tree=get(v,'tree')
   elif k=='country_event':self.queue.append(get(v,'id'))
   elif k=='add_opinion_modifier':pass
   else:raise AssertionError('Unmodelled effect '+k)
 def effect(self,name):self.execute(self.effects[name]);self.events_ready()
 def events_ready(self):
  while self.queue:
   id=self.queue.pop(0)
   if id in self.seen:continue
   self.seen.add(id);options=[v for k,o,v in self.events[id] if k=='option'];option=options[self.choices.get(id,0)]
   assert self.condition(val(option,'trigger',[]))
   self.execute([t for t in option if t[0] not in ['name','ai_chance','trigger']])
 def available(self,stem):
  body=self.focus_ast['MSGA_'+stem]
  return 'MSGA_'+stem not in self.focuses and all(get(v,'focus') in self.focuses for k,o,v in body if k=='prerequisite') and all(get(v,'focus') not in self.focuses for k,o,v in body if k=='mutually_exclusive') and self.condition(get(body,'available'))
 def focus(self,stem):
  assert self.available(stem),'Blocked focus '+stem
  body=self.focus_ast['MSGA_'+stem];self.day+=float(get(body,'cost'))*7;self.focuses.add('MSGA_'+stem);self.execute(get(body,'completion_reward'));self.events_ready()
 def start(self,stem):
  id='MSGA_'+stem;body=self.decisions[id]
  if id in self.jobs or not self.condition(get(body,'visible')) or not self.condition(get(body,'available')) or self.pp<float(get(body,'cost')):return False
  self.pp-=float(get(body,'cost'));self.jobs[id]=self.day+int(val(body,'days_remove',0));self.execute(get(body,'complete_effect'));self.events_ready();return True
 def advance(self,days):
  self.day+=days
  for id,end in list(self.jobs.items()):
   body=self.decisions[id]
   if self.condition(get(body,'cancel_trigger')):self.jobs.pop(id);self.execute(get(body,'cancel_effect'))
   elif self.day>=end:self.jobs.pop(id);self.execute(get(body,'remove_effect'))
  self.events_ready()
 def decision(self,stem):
  assert self.start(stem),'Blocked decision '+stem
  days=int(get(self.decisions['MSGA_'+stem],'days_remove'));self.advance(days-1)
  assert 'MSGA_eg_'+stem+'_done' not in self.flags['SER'];self.advance(1)
  assert 'MSGA_eg_'+stem+'_done' in self.flags['SER'];assert not self.start(stem)

def main():
 cli=argparse.ArgumentParser();cli.add_argument('--mod-root',type=Path,required=True);cli.add_argument('--report',type=Path,default=ROOT/'docs/endgame_validation.json');cli.add_argument('--prepared',action='store_true');args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
 source=json.loads((ROOT/('logs/endgame_prepared_record.json' if args.prepared else 'docs/endgame_sources.json')).read_text())
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ['.txt','.gfx']}
 if args.prepared:
  # Prepared overlay checks can read the unchanged source, but do not count as LIVE validation.
  baseline={p.relative_to(ROOT/'make_serbia_great_again').as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in (ROOT/'make_serbia_great_again').rglob('*') if p.suffix in ['.txt','.gfx']};scripts=baseline|scripts
 else:
  for p,d in source['baseline_sha256'].items():
   if p not in source['changed_relative_paths']:assert digest(mod/p)==d,p
  for p,d in source['deployed_sha256'].items():assert digest(mod/p)==expected_hash(p,d),p
 for p,d in source['native_sources_sha256'].items():assert digest(TFR/p)==d,p
 assert digest(Path(source['package']))==source['package_sha256']
 tree=scripts['common/national_focus/MSGA_SER_endgame.txt'][0][2];focuses={get(v,'id'):v for k,o,v in tree if k=='focus'}
 continuation=ROOT/'docs/yugoslav_politics_sources.json'
 if continuation.exists() and not args.prepared:
  political=json.loads(continuation.read_text());new_ids={'MSGA_'+row[0] for row in political['focuses']}
  assert len(focuses)==40 and new_ids<=focuses.keys()
  old=parse(subprocess.check_output(['git','show','a182e7944cdd528b540ab9f121c5ccf2e7104fd8:make_serbia_great_again/common/national_focus/MSGA_SER_endgame.txt'],cwd=ROOT).decode('utf-8-sig'))
  assert [(k,o,v) for k,o,v in tree if k!='focus' or get(v,'id') not in new_ids]==old[0][2], 'Existing endgame must be unchanged'
 else:assert len(focuses)==29
 unique([(get(v,'x'),get(v,'y')) for v in focuses.values()],'endgame positions')
 unique([get(v,'id') for p,a in scripts.items() if p.startswith('common/national_focus/') for k,o,b in a for k,o,v in b if k=='focus'],'all focus IDs')
 for stem,days,x,y,parents,avail in source['focuses']:
  b=focuses['MSGA_'+stem];assert math.isclose(float(get(b,'cost'))*7,days)
  assert [get(v,'focus') for k,o,v in b if k=='prerequisite']==['MSGA_'+p for p in parents]
  assert all('MSGA_'+p in focuses for p in parents)
 assert get(get(focuses['MSGA_a_serbian_century'],'mutually_exclusive'),'focus')=='MSGA_the_yugoslav_idea'
 assert get(get(focuses['MSGA_the_yugoslav_idea'],'mutually_exclusive'),'focus')=='MSGA_a_serbian_century'
 expected=parse(subprocess.check_output(['git','show','cc60584:make_serbia_great_again/common/scripted_effects/MSGA_new_order_effects.txt'],cwd=ROOT).decode('utf-8-sig'))
 def unhook(ast):return [(k,o,unhook(v) if isinstance(v,list) else v) for k,o,v in ast if k!='MSGA_try_start_endgame']
 assert unhook(scripts['common/scripted_effects/MSGA_new_order_effects.txt'])==expected,'Only the endgame hand-off may change'
 decisions={k:v for cat,o,b in scripts['common/decisions/MSGA_endgame_decisions.txt'] for k,o,v in b};assert len(decisions)==34
 for stem,name,pp,debt,days,tag,route,previous,focus in source['decisions']:
  b=decisions['MSGA_'+stem];assert float(get(b,'cost'))==pp and int(get(b,'days_remove'))==days
  assert 'fire_only_once' not in [k for k,o,v in b] # permit refunded retry
  assert 'custom_trigger_tooltip' in [k for k,o,v in get(b,'available')]
  assert 'hidden_effect' in [k for k,o,v in get(b,'complete_effect')]
 events={get(v,'id'):v for k,o,v in scripts['events/MSGA_endgame_events.txt'] if k=='country_event'};assert len(events)==31
 all_events=[get(v,'id') for p,a in scripts.items() if p.startswith('events/') for k,o,v in a if k=='country_event'];unique(all_events,'all country event IDs')
 sprites=[v for p,a in scripts.items() if p.startswith('interface/') for k,o,b in a for k,o,v in b if k.lower()=='spritetype'];names=[get(v,'name').strip('"') for v in sprites];unique(names,'sprites');sprite_map={get(v,'name').strip('"'):get(v,'texturefile').strip('"') for v in sprites}
 for b in focuses.values():assert get(b,'icon') in names and get(b,'icon')+'_shine' in names
 for b in decisions.values():assert 'GFX_decision_'+get(b,'icon') in names
 for b in events.values():assert get(b,'picture') in names
 # Every supplied event composition has a used sprite, including the final army announcement.
 used={get(b,'picture') for b in events.values()}
 with ZipFile(source['package']) as z:
  for p,a in source['assets'].items():
   data=(mod/p).read_bytes();assert hashlib.sha256(data).hexdigest()==a['sha256'];assert data[84:88]==b'DXT5'
   assert hashlib.sha256(z.read(a['source_member'])).hexdigest()==a['source_sha256']
   with Image.open(mod/p) as im:assert list(im.size)==a['size'];im.load()
   if '/event_pictures/' in p:assert any(sprite_map[n]==p for n in used),p
   if a['native_map_geometry']:assert a['map_bbox'] and 'map/provinces.bmp' in source['native_sources_sha256']
 locales='\n'.join(p.read_text(encoding='utf-8-sig') for p in (mod/'localisation/english').glob('*.yml'))
 if args.prepared:locales+='\n'+'\n'.join(p.read_text(encoding='utf-8-sig') for p in (ROOT/'make_serbia_great_again/localisation/english').glob('*.yml'))
 keys=re.findall(r'^ ([^:]+):',locales,re.M);unique(keys,'localisation')
 for id,b in focuses.items():assert id in keys and id+'_desc' in keys
 for id,b in decisions.items():assert id in keys and id+'_desc' in keys
 for id,b in events.items():assert id+'.t' in keys and id+'.d' in keys and all(get(v,'name') in keys for k,o,v in b if k=='option')
 ideas={k:v for p,a in scripts.items() if p.startswith('common/ideas/') for _,_,b in a for _,_,d in b for k,o,v in d}
 known={kind:set(re.findall(r'^## (\w+)',(GAME/'documentation'/f'{kind}_documentation.md').read_text(),re.M)) for kind in ['triggers','effects','modifiers']}
 native_mods={k for k,o,v in parse((TFR/'common/modifier_definitions/00_TFR_economic_modifiers_definition.txt').read_text())}
 for k,o,b in get(get(scripts['common/ideas/MSGA_endgame_ideas.txt'],'ideas'),'country'):
  assert 'GFX_idea_'+get(b,'picture') in names and k in keys and k+'_desc' in keys
  for token,o,v in get(b,'modifier'):assert token in known['modifiers']|native_mods and abs(float(v))<=.25,token
 generic=parse((TFR/'common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt').read_text(encoding='utf-8-sig'))
 assert ('add_to_variable','=',parse('var = debt_var value = debt_var_temp')) in get(generic,'add_debt')
 effects={k:v for k,o,v in scripts['common/scripted_effects/MSGA_endgame_effects.txt']}
 triggers={k:v for k,o,v in scripts['common/scripted_triggers/MSGA_endgame_triggers.txt']}
 local_effects={k for p,a in scripts.items() if p.startswith('common/scripted_effects/') for k,o,v in a};local_triggers={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
 def check_effect(body):
  for k,o,v in body:
   if k in ['if','else_if','else']:check_condition(val(v,'limit',[]));check_effect([t for t in v if t[0]!='limit'])
   elif k in ['every_country']:check_condition(val(v,'limit',[]));check_effect([t for t in v if t[0]!='limit'])
   elif k in ['hidden_effect'] or k.isdigit() or k in ['SER','CRO','SLV','BOS','HRZ','MNT','MAC','ALB']:check_effect(v)
   else:assert k in known['effects']|local_effects|{'add_debt','add_industrial_development'},k
 def check_condition(body):
  for k,o,v in body:
   if k in ['OR','AND','NOT','any_owned_state'] or k.isdigit() or k in ['SER','CRO','SLV','BOS','HRZ','MNT','MAC','ALB']:check_condition(v)
   else:assert k in known['triggers']|local_triggers|{'infrastructure','industrial_complex','arms_factory','office_park'},k
 for body in effects.values():check_effect(body)
 for body in triggers.values():check_condition(body)
 chapter=[(k,o,v) for p,a in scripts.items() if 'endgame' in p for k,o,v in descend(a)]
 for k,o,v in chapter:
  if k in ['add_ideas','remove_ideas']:assert v in ideas,v
  if k=='annex_country':assert get(v,'target') in ['MNT','MAC','CRO','SLV','BOS','HRZ'] and get(v,'transfer_troops')=='yes'
  if k=='add_core_of':assert v=='SER'
 assert not ({k for k,o,v in chapter}&{'load_oob','create_unit','delete_unit','add_equipment_to_stockpile','set_politics','create_country_leader','declare_war_on','add_income','add_debt_with_inflation'})
 for folder,size in [('',(82,52)),('medium/',(41,26)),('small/',(10,7))]:
  for tag in ['SER_MSGA_GREATER_SERBIA','SER_MSGA_YUGOSLAV_FEDERATION']:
   p=mod/('gfx/flags/'+folder+tag+'.tga')
   with Image.open(p) as im:
    assert im.size==size and im.mode=='RGBA'
    if 'YUGOSLAV' in tag:
     assert im.getpixel((0,0))[:3]==(0,56,147) and im.getpixel((0,size[1]//2))[:3]==(255,255,255) and im.getpixel((0,size[1]-1))[:3]==(216,30,43)
     assert all(len({im.getpixel((x,y)) for x in range(size[0])})==1 for y in range(size[1])),'No emblem allowed'
    else:assert p.read_bytes()==(TFR/('gfx/flags/'+folder+'SER.tga')).read_bytes()
  assert all(t in keys and t+'_DEF' in keys and t+'_ADJ' in keys for t in ['SER_MSGA_GREATER_SERBIA','SER_MSGA_YUGOSLAV_FEDERATION'])
 cases=[];federal_checkpoint=None
 for route,borders,balanced in [('gs',False,False)]+[('yug',a,b) for a in [False,True] for b in [False,True]]:
  m=Model(scripts,mod,source,borders,balanced);m.effect('MSGA_try_start_endgame');assert m.tree=='MSGA_SER_endgame';m.effect('MSGA_try_start_endgame');m.focus('future_of_the_south_slavs')
  armies=sum(m.armies.values());stockpiles=sum(m.stockpiles.values());money=m.money
  if route=='gs':
   for stem in ['a_serbian_century','one_serbian_state','montenegrin_question','macedonian_question','one_people_one_state','secure_the_vardar']:m.focus(stem)
   assert not m.available('the_yugoslav_idea')
   for d in source['decisions']:
    if d[6]=='gs' and d[5] in ['MNT','MAC']:m.decision(d[0])
   for stem in ['integrate_montenegro','integrate_macedonia','consolidate_serbian_lands','the_greater_serbian_state','belgrades_sphere']:m.focus(stem)
   for d in source['decisions']:
    if d[6]=='gs' and d[5] not in ['MNT','MAC']:m.decision(d[0])
   m.focus('serbian_hegemony');assert m.cosmetic=='SER_MSGA_GREATER_SERBIA' and set(m.subjects)=={'CRO','SLV','BOS','HRZ','ALB'} and math.isclose(m.debt-19,10)
   assert 'MSGA_hegemon_balkans' in m.ideas['SER'] and not {'MSGA_serbian_state_reborn','MSGA_belgrades_sphere_spirit'}&m.ideas['SER']
  else:
   for stem in ['the_yugoslav_idea','a_common_homeland','reconcile_the_republics','draft_a_federal_model']:m.focus(stem)
   assert not m.available('a_serbian_century') and not m.available('conference_of_belgrade')
   for d in source['decisions']:
    if d[6]=='yug' and d[5]:m.decision(d[0])
   assert (m.states[848]=='BOS')==borders
   for stem in ['conference_of_belgrade','the_federal_constitution']:m.focus(stem)
   assert not m.available('proclaim_the_federation');m.decision('ratify_federal_constitution');m.focus('proclaim_the_federation')
   assert not m.available('federal_yugoslavia');federal_checkpoint=copy.deepcopy(m);m.decision('proclaim_federal_republic_yugoslavia')
   for stem in ['federal_yugoslavia','one_yugoslav_army','one_yugoslav_economy','integrate_the_commands','rebuild_the_common_market','arsenal_of_yugoslavia','yugoslav_development_plan','brotherhood_reforged','a_new_yugoslavia']:m.focus(stem)
   assert m.cosmetic=='SER_MSGA_YUGOSLAV_FEDERATION' and set(m.subjects)=={'ALB'} and math.isclose(m.debt-19,11.75)
   assert 'MSGA_federation_reborn' in m.ideas['SER'] and not {'MSGA_yugoslav_project','MSGA_federal_transition','MSGA_yugoslav_federation'}&m.ideas['SER']
  assert sum(m.armies.values())==armies and sum(m.stockpiles.values())==stockpiles and m.money==money and m.states[44]=='ALB' and m.states[886]=='ALB'
  assert m.leader=='SER_Aleksandar_Vucic' and m.capital==107 and 'MSGA_endgame.14' in m.seen
  before=(m.debt,m.pp,copy.deepcopy(m.armies),copy.deepcopy(m.stockpiles),copy.deepcopy(m.buildings));m.effect('MSGA_try_start_endgame')
  for d in source['decisions']:
   if d[6]==route:m.effect('MSGA_eg_finish_'+d[0])
  for stem,*_ in source['focuses']:
   if 'MSGA_eg_focus_'+stem in m.flags['SER']:m.effect('MSGA_eg_focus_'+stem)
  assert before==(m.debt,m.pp,m.armies,m.stockpiles,m.buildings)
  cases.append({'route':route,'restore_Bosnian_borders':borders,'balanced_federation':balanced,'new_native_debt_B':m.debt-19,'treasury_cost_B':0,'subjects_remaining':sorted(m.subjects),'army_stockpile_totals_preserved':True})
 # Missing/independent subject, foreign territory, war, wrong country and queued completion safety.
 negatives=[]
 for loss in ['independent','missing','foreign_control','war','extra_conquest']:
  m=Model(scripts,mod,source);m.effect('MSGA_try_start_endgame')
  for f in ['future_of_the_south_slavs','a_serbian_century','one_serbian_state','montenegrin_question']:m.focus(f)
  before=(m.pp,m.debt);assert m.start('begin_montenegrin_integration');assert not m.start('begin_montenegrin_integration')
  if loss=='independent':m.subjects.pop('MNT')
  elif loss=='missing':m.exists.remove('MNT')
  elif loss=='foreign_control':m.controllers[105]='BUL'
  elif loss=='war':m.wars.add(frozenset(('MNT','BUL')))
  else:m.states[777]='MNT'
  m.advance(5);assert not m.jobs and before==(m.pp,m.debt) and 'MSGA_eg_begin_montenegrin_integration_done' not in m.flags['SER']
  m.effect('MSGA_eg_finish_begin_montenegrin_integration');m.effect('MSGA_eg_cancel_begin_montenegrin_integration');assert before==(m.pp,m.debt)
  m.subjects['MNT']='SER';m.exists.add('MNT');m.controllers[105]='MNT';m.wars.clear();m.states[777]='BUL';m.decision('begin_montenegrin_integration')
  negatives.append(loss)
 m=Model(scripts,mod,source);m.flags['SER'].remove('MSGA_new_balkan_order_stabilised');m.effect('MSGA_try_start_endgame');assert m.tree!='MSGA_SER_endgame'
 m=Model(scripts,mod,source);m.execute(m.effects['MSGA_try_start_endgame'],'CRO');assert m.tree!='MSGA_SER_endgame'
 # Recheck the entire federation immediately before completion: no partial annexation.
 for failure in ['departing_MAC','occupied_HRZ','foreign_CRO_conquest']:
  m=copy.deepcopy(federal_checkpoint);before=(m.pp,m.debt,m.states.copy(),m.subjects.copy(),m.armies.copy());assert m.start('proclaim_federal_republic_yugoslavia')
  if failure=='departing_MAC':m.subjects.pop('MAC')
  elif failure=='occupied_HRZ':m.controllers[851]='BUL'
  else:m.states[777]='CRO'
  changed=(m.states.copy(),m.subjects.copy(),m.armies.copy());m.advance(35)
  assert (m.pp,m.debt)==before[:2] and (m.states,m.subjects,m.armies)==changed
  assert m.cosmetic is None and 'MSGA_yugoslav_federation_proclaimed' not in m.flags['SER'] and not m.jobs
  negatives.append('atomic_federation_'+failure)
 # Independent administration processes can proceed together without sharing debt/locks.
 m=Model(scripts,mod,source);m.effect('MSGA_try_start_endgame')
 for f in ['future_of_the_south_slavs','a_serbian_century','one_serbian_state','montenegrin_question','macedonian_question']:m.focus(f)
 assert m.start('begin_montenegrin_integration') and m.start('establish_vardar_administration');m.advance(20)
 assert 'MSGA_eg_begin_montenegrin_integration_done' in m.flags['SER'] and 'MSGA_eg_establish_vardar_administration_done' not in m.flags['SER'];m.advance(5)
 assert 'MSGA_eg_establish_vardar_administration_done' in m.flags['SER'] and m.debt==20.25 and not m.jobs
 negatives.append('parallel_country_processes')
 # Pending flags survive model serialization; no early completion and no duplicate borrow.
 m=Model(scripts,mod,source);m.effect('MSGA_try_start_endgame')
 for f in ['future_of_the_south_slavs','a_serbian_century','one_serbian_state','montenegrin_question']:m.focus(f)
 assert m.start('begin_montenegrin_integration');saved=copy.deepcopy(m);assert not saved.start('begin_montenegrin_integration');saved.advance(20);assert saved.debt==19.5
 # Native construction rejection rolls back introduced slots without inventing buildings.
 m=Model(scripts,mod,source);m.build_reject=True;m.flags['SER']|={'MSGA_endgame_choice_active','MSGA_yugoslavia_path'};m.effect('MSGA_eg_focus_arsenal_of_yugoslavia');assert m.buildings[107]['arms_factory']==0 and m.slots[107]==0
 report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'prepared_overlay_only':args.prepared,'version':source['version'],'focus_count':29,'timed_decisions':31,'optional_peaceful_dialogues':3,'events':31,'DDS_assets':len(source['assets']),'flags':6,'scenarios':cases,'negative_cases':negatives+['premature_tree_entry','wrong_country','pending_save_model','native_build_rejection'],'native_debt_API':'debt_var_temp + add_debt; no treasury change, no inflation multiplier','baseline_preserved_except':'one New Balkan Order hand-off and two version descriptors','actual_engine_validation':'NOT RUN: user reserved game testing. Models do not certify timers, annexation transfer, UI, native construction ticks or engine save/load.'}
 report['chapter_version']=source['version']
 report['version']=re.search(r'^version="([^"]+)"',(mod/'descriptor.mod').read_text(),re.M)[1] if not args.prepared else source['version']
 report['installed_tree_focus_count']=len(focuses)
 args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
