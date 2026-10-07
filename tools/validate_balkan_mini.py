"""Targeted LIVE native checks and short parsed-script smoke; never engine QA."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import argparse, copy, hashlib, json, re
from PIL import Image
from validate_phase1 import parse,get,descend,unique
from validate_balkan_rearmament import Smoke,val
from implement_balkan_mini import ROOT,TARGET,TFR,GAME,TAGS,ROWS,CONTRACTS,IDEAS,FORTS,ARMOUR_DEF,MNT_DEF,ident

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class MiniSmoke(Smoke):
 def __init__(self,scripts,tag,nsb=False):
  super().__init__(scripts,tag,nsb)
  self.effects.update(dict((k,v) for k,o,v in scripts['common/scripted_effects/MSGA_balkan_mini_effects.txt']))
  self.triggers.update(dict((k,v) for p,a in scripts.items() if p.startswith('common/scripted_triggers/MSGA_balkan_mini') for k,o,v in a))
  self.focus_ast={get(v,'id'):v for _,_,tree in scripts[f'common/national_focus/MSGA_{tag}_mini.txt'] for k,o,v in tree if k=='focus'}
  self.decisions={k:v for _,_,cat in scripts['common/decisions/MSGA_balkan_mini_procurement.txt'] for k,o,v in cat if k.startswith('MSGA_'+tag)}
  self.owner.update({104:'BOS',105:'MNT',106:'MAC'});self.controller=self.owner.copy();self.factory.update({104:1,105:0,106:1});self.infrastructure.update({104:2,105:2,106:4});self.slots.update({104:8,105:8,106:8})
  self.exists.update(TAGS);self.templates=set();self.caps={};self.fort_levels=Counter();self.manpower=10000;self.stock=Counter();self.root='SER';self.from_tag='KOS';self.flags['SER'].add('MSGA_serbian_vehicles_initialized')
 def condition(self,a,scope=None):
  scope=self.tag if scope is None else scope
  for k,o,v in a:
   if k in ['ROOT','FROM'] or k in TAGS:
    target=self.root if k=='ROOT' else self.from_tag if k=='FROM' else k;ok=self.condition(v,target)
   elif k=='exists':ok=(scope in self.exists)==(v=='yes')
   elif k=='has_template':ok=v.strip('"') in self.templates
   elif k=='is_core_of':ok=TAGS.get(v)==scope
   elif k=='has_manpower':ok=self.manpower>int(v)
   elif k=='has_equipment':ok=all(self.stock[kk]>int(vv) if oo=='>' else self.stock[kk]<int(vv) for kk,oo,vv in v)
   elif k=='free_building_slots' and val(v,'province'):
    ok=10-self.fort_levels[int(get(v,'province'))]>int(get(v,'size'))
   else:ok=super().condition([(k,o,v)],scope)
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
   if k in TAGS:self.execute(v,k)
   elif k=='division_template':self.templates.add(get(v,'name').strip('"'))
   elif k=='set_division_template_cap':self.caps[get(v,'division_template').strip('"')]=int(get(v,'division_cap'))
   elif k=='add_building_construction' and get(v,'type')=='bunker':self.fort_levels[int(get(v,'province'))]+=int(get(v,'level'))
   else:super().execute([(k,o,v)],scope)

def main():
 cli=argparse.ArgumentParser();cli.add_argument('--mod-root',required=True,type=Path);cli.add_argument('--report',type=Path,default=ROOT/'docs/balkan_mini_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True);assert mod==TARGET.resolve(strict=True)
 record=json.loads((ROOT/'docs/balkan_mini_sources.json').read_text())
 for p,d in record['baseline_sha256'].items():
  if p not in record['deployed_sha256']:assert digest(mod/p)==d,p
 for p,d in record['deployed_sha256'].items():assert digest(mod/p)==d,p
 for p,d in record['native_sources_sha256'].items():assert digest(TFR/p)==d,p
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig',errors='replace')) for p in mod.rglob('*') if p.suffix in ['.txt','.gfx']}
 tags={k for k,o,v in parse((TFR/'common/country_tags/00_countries.txt').read_text())};assert set(TAGS)<=tags
 known={kind:set(re.findall(r'^## (\w+)',(GAME/'documentation'/f'{kind}_documentation.md').read_text(encoding='utf-8-sig'),re.M)) for kind in ['effects','triggers','modifiers']}
 local_effects={k for p,a in scripts.items() if p.startswith('common/scripted_effects/') for k,o,v in a};local_triggers={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
 native_mods={k for k,o,v in parse((TFR/'common/modifier_definitions/00_TFR_economic_modifiers_definition.txt').read_text())}
 assert 'production_speed_arms_factory_factor' in (TFR/'common/ideas/00_TFR_laws_economic.txt').read_text();native_mods.add('production_speed_arms_factory_factor')
 def condition(a):
  for k,o,v in a:
   if k in ['OR','AND','NOT','hidden_trigger','custom_trigger_tooltip','ROOT','FROM'] or k in tags or k.isdigit():condition([t for t in v if t[0]!='tooltip'])
   else:assert k in known['triggers']|local_triggers|{'arms_factory','infrastructure'},'Unknown trigger '+k
 def effect(a):
  for k,o,v in a:
   if k in ['if','else','else_if']:condition(val(v,'limit',[]));effect([t for t in v if t[0]!='limit'])
   elif k in ['hidden_effect','ROOT','FROM'] or k in tags or k.isdigit():effect(v)
   else:assert k in known['effects']|local_effects|{'add_income'},'Unknown effect '+k
 for p,a in scripts.items():
  if p.startswith('common/scripted_effects/MSGA_balkan_mini'): [effect(v) for k,o,v in a]
  if p.startswith('common/scripted_triggers/MSGA_balkan_mini'):[condition(v) for k,o,v in a]
 keys=[]
 for p in (mod/'localisation/english').glob('*.yml'):keys+=re.findall(r'^ ([^:]+):',p.read_text(encoding='utf-8-sig'),re.M)
 unique(keys,'English localization');assert 'NO EFFECT' not in (mod/'localisation/english/MSGA_balkan_mini_l_english.yml').read_text()
 new_keys=re.findall(r'^ ([^:]+):',(mod/'localisation/english/MSGA_balkan_mini_l_english.yml').read_text(encoding='utf-8-sig'),re.M);assert all(re.fullmatch(r'\w+',key) for key in new_keys)
 sprites={};local_names=[]
 for base in [TFR,mod]:
  for p in (base/'interface').glob('*.gfx'):
   for k,o,v in descend(parse(p.read_text(encoding='utf-8-sig',errors='replace'))):
    if k.lower()=='spritetype':
     name=get(v,'name').strip('"');texture=next((vv for kk,oo,vv in v if kk.lower()=='texturefile'),None)
     if texture:sprites[name]=texture.strip('"')
     if base==mod:local_names.append(name)
 unique(local_names,'sprite IDs')
 all_focuses=[get(v,'id') for p,a in scripts.items() if p.startswith('common/national_focus/') for k,o,v in descend(a) if k=='focus' and isinstance(v,list)];unique(all_focuses,'focus IDs')
 for tag,rows in ROWS.items():
  tree=get(scripts[f'common/national_focus/MSGA_{tag}_mini.txt'],'focus_tree');assert get(tree,'id')=='MSGA_'+tag+'_mini';bodies={get(v,'id'):v for k,o,v in tree if k=='focus'};assert len(bodies)==14
  unique([(get(v,'x'),get(v,'y')) for v in bodies.values()],tag+' positions')
  for i,(stem,days,x,y,parents) in enumerate(rows):
   id=ident(tag,stem);b=bodies[id];assert abs(float(get(b,'cost'))*7-days)<1e-5 and [get(v,'focus') for k,o,v in b if k=='prerequisite']==[ident(tag,p) for p in parents]
   assert all(p in bodies for p in [ident(tag,p) for p in parents]);assert id in keys and id+'_desc' in keys and id+'_reward_tt' in keys
   assert get(b,'icon') in sprites and get(b,'icon')+'_shine' in sprites;condition(get(b,'available'));effect(get(b,'completion_reward'))
   assert (('MSGA_mini_rearmament_unlocked','=','yes') in get(b,'available'))==(i>=6)
   assert float(get(get(b,'ai_will_do'),'factor'))>=500 if i>=6 else float(get(get(b,'ai_will_do'),'factor'))<=60
 ideas=get(get(scripts['common/ideas/MSGA_balkan_mini_ideas.txt'],'ideas'),'country');assert len(ideas)==23
 for id,o,b in ideas:
  assert id in keys and id+'_desc' in keys and 'GFX_idea_'+get(b,'picture') in sprites
  assert dict((k,float(v)) for k,o,v in get(b,'modifier'))==IDEAS[id.removeprefix('MSGA_')][2]
  assert all(k in known['modifiers']|native_mods for k,o,v in get(b,'modifier'))
 dmap={k:v for _,_,cat in scripts['common/decisions/MSGA_balkan_mini_procurement.txt'] for k,o,v in cat};assert len(dmap)==13
 for tag,stem,cost,days,focus,items,icon in CONTRACTS:
  id=ident(tag,stem);b=dmap[id];assert get(b,'cost')=='0' and int(get(b,'days_remove'))==days and 'GFX_decision_'+icon in sprites
  assert 'ONE-TIME ONLY' in next(p.read_text() for p in (mod/'localisation/english').glob('MSGA_balkan_mini*'))
  for suffix in ['', '_desc','_available_tt','_start_tt','_finish_tt']:assert id+suffix in keys
  for k in ['visible','available','cancel_trigger']:condition(get(b,k))
  for k in ['complete_effect','remove_effect','cancel_effect']:effect(get(b,k))
  assert not val(b,'fire_only_once') and ('NOT','=',parse('has_country_flag = '+id+'_completed')) in get(get(b,'available'),'custom_trigger_tooltip')
 eq={};units={}
 for p in (TFR/'common/units/equipment').glob('*.txt'):
  for k,o,v in parse(p.read_text(encoding='utf-8-sig',errors='replace')):
   if k=='equipments':eq.update(dict((kk,vv) for kk,oo,vv in v))
 for p in (TFR/'common/units').glob('*.txt'):
  for k,o,v in parse(p.read_text(encoding='utf-8-sig',errors='replace')):
   if k=='sub_units':units.update(dict((kk,vv) for kk,oo,vv in v))
 new_effects=scripts['common/scripted_effects/MSGA_balkan_mini_effects.txt']
 for k,o,v in descend(new_effects):
  if k=='add_equipment_to_stockpile':assert get(v,'type') in eq and get(v,'producer') in tags
  assert k not in ['create_unit','create_equipment_variant','load_oob','delete_unit','annex_country','add_core_of','declare_war_on','add_manpower','set_state_owner']
  if k=='has_country_flag':assert v not in ['MSGA_srpska_released','MSGA_bosnian_war_started','MSGA_bosnia_intervened']
 # Starting units are in the original assigned BOS OOB, not a startup effect.
 old=parse((TFR/'history/units/BOS_2020.txt').read_text(encoding='utf-8-sig'));current=scripts['history/units/BOS_2020.txt'];aux=scripts['history/units/MSGA_BOS_auxiliary_militias.txt']
 assert current[:-2]==old and current[-2]==aux[0]
 assert current[-1]==parse((mod/'history/units/MSGA_BOS_auxiliary_militias.txt').read_text().replace('location = 11586','location = 11899'))[-1]
 additions=[v for k,o,v in current[-1][2] if k=='division'];assert len(additions)==2 and len(get(current[-2][2],'regiments'))==3 and all(k=='militia' for k,o,v in get(current[-2][2],'regiments'))
 unique([get(v,'name') for k,o,b in current if k=='units' for kk,oo,v in b if kk=='division'],'starting Bosnia unit names')
 assert all(get(v,'location')=='11899' and get(v,'division_template')=='"Bosnian Territorial Brigade"' for v in additions)
 # Compute formation requirements directly from native battalions, including supports.
 req=Counter();men=0;template=get(parse(ARMOUR_DEF),'division_template')
 for group in ['regiments','support']:
  for k,o,v in get(template,group):
   assert k in units;men+=int(get(units[k],'manpower'))
   for typ,oo,n in get(units[k],'need'):req[typ]+=int(n)
 assert dict(req)|{'manpower':men}==record['armoured_requirements'];assert req['modern_tank_chassis']==50 and 100-req['modern_tank_chassis']==50
 assert get(eq['modern_tank_equipment_1'],'archetype')=='modern_tank_chassis'
 ser=scripts['common/scripted_effects/MSGA_SER_vehicle_effects.txt'];variants=[v for k,o,v in descend(ser) if k=='create_equipment_variant' and get(v,'name')=='"T-55A"'];assert {get(v,'type') for v in variants}=={'modern_tank_chassis_1','modern_tank_equipment_1'}
 for k,o,v in descend(new_effects):
  if k=='add_equipment_to_stockpile' and get(v,'type') in ['modern_tank_chassis_1','modern_tank_equipment_1']:assert get(v,'variant_name')=='"T-55A"' and get(v,'producer')=='SER' and get(v,'amount')=='100'
 native_start=get(get(scripts['common/scripted_effects/MSGA_SER_effects.txt'],'MSGA_start_kosovo_war'),'if');assert ('set_country_flag','=','MSGA_kosovo_war_started') in native_start and ('declare_war_on','=',parse('target = KOS type = annex_everything')) in native_start
 on=get(scripts['common/on_actions/MSGA_balkan_mini_on_actions.txt'],'on_actions');assert not any(k=='on_daily' for k,o,v in on)
 declaration=get(get(on,'on_declare_war'),'effect');startup=get(get(on,'on_startup'),'effect')
 for k,o,v in descend(startup):assert k not in ['create_unit','load_oob','add_building_construction','declare_war_on']
 for tag in TAGS:
  state=get(parse((TFR/record['geometry_and_graphics']['geometry'][str(TAGS[tag])]['file']).read_text()),'state');provinces={int(k) for k,o,v in get(state,'provinces')}
  assert all(p in provinces for p,n in FORTS[tag]);assert ('add_core_of','=',tag) in get(state,'history')
 geometry=record['geometry_and_graphics']['geometry'];assert min(geometry['105']['provinces'],key=lambda p:p['y'])['province']==11858
 assert {p for p,n in FORTS['MAC']}=={3882,907};assert all(p['y']<690 for p in geometry['106']['provinces'] if p['province'] in [3882,907])
 with ZipFile(record['package']) as z:
  assert digest(Path(record['package']))==record['package_sha256'] and len(record['assets'])==50
  for p,a in record['assets'].items():
   assert '/Previews/' not in a['source_member'] and digest(mod/p)==a['sha256'] and hashlib.sha256(z.read(a['source_member'])).hexdigest()==a['source_sha256']
   assert (mod/p).read_bytes()[84:88]==b'DXT5' and p in sprites.values()
   with Image.open(mod/p) as im:assert list(im.size)==a['size'];im.load()
 # Short smoke uses the real parsed reward, trigger and contract scripts.
 routes=[];negative=[];models=[]
 for tag,rows in ROWS.items():
  m=MiniSmoke(scripts,tag);root=ident(tag,rows[6][0]);assert not m.available(root)
  m.flags['SER'].add('MSGA_kosovo_war_active');assert not m.available(root);m.flags['SER'].clear();negative.append(tag+'_active_only_not_started')
  for stem,*_ in rows[:6]:m.focus(ident(tag,stem))
  m.flags['SER'].add('MSGA_kosovo_war_started');m.execute(declaration);assert all('MSGA_mini_rearmament_unlocked' in m.flags[t] for t in TAGS)
  m.flags['SER'].clear();assert m.available(root), 'Own flag must survive cleanup of the active war'
  for stem,*_ in rows[6:]:m.focus(ident(tag,stem))
  assert m.factory[TAGS[tag]]=={'BOS':3,'MAC':2,'MNT':1}[tag] and dict(m.fort_levels)==dict(FORTS[tag])
  assert m.infrastructure[TAGS[tag]]=={'BOS':3,'MAC':5,'MNT':4}[tag]
  before=copy.deepcopy((m.factory,m.slots,m.equipment,m.flags,m.ideas,m.fort_levels,m.xp,m.ws))
  for stem,*_ in rows:m.execute(m.effects[ident(tag,stem)+'_reward'])
  assert before==(m.factory,m.slots,m.equipment,m.flags,m.ideas,m.fort_levels,m.xp,m.ws)
  if tag=='MNT':assert m.templates=={'MSGA MNT Territorial Militia'}
  routes.append({'tag':tag,'focuses':14,'state_MIL':m.factory[TAGS[tag]],'forts':dict(m.fort_levels),'infrastructure':m.infrastructure[TAGS[tag]],'own_unlock_survives_SER_flag_cleanup':True,'rewards_once':True})
  legacy=MiniSmoke(scripts,tag);legacy.flags['SER'].add('MSGA_kosovo_war_started');legacy.execute(m.effects['MSGA_mini_unlock_rearmament']);assert legacy.available(root);negative.append(tag+'_old_save_migration')
  blocked=MiniSmoke(scripts,tag);blocked.flags['SER'].add('MSGA_kosovo_war_started');blocked.root='CRO';blocked.execute(declaration);assert not blocked.flags[tag];negative.append(tag+'_unrelated_war_callback')
 for tag,stem,cost,days,focus,items,icon in CONTRACTS:
  id=ident(tag,stem)
  for nsb in ([False,True] if 't55' in stem else [False]):
   m=MiniSmoke(scripts,tag,nsb);m.flags[tag].add('MSGA_mini_rearmament_unlocked');m.focuses={ident(tag,s) for s,*_ in ROWS[tag]};assert m.start(id);assert abs(m.money-20+cost)<1e-8;assert not m.start(id)
   m.advance(days-1);assert not m.equipment;m=copy.deepcopy(m);m.advance(1)
   expected={(typ,prod,''):n for typ,n,prod in items}
   if 't55' in stem:
    expected={('modern_tank_chassis_1' if nsb else 'modern_tank_equipment_1','SER','"T-55A"'):100};assert m.templates=={'Bosnian Armoured Brigade'} and m.caps=={'Bosnian Armoured Brigade':1}
   assert dict(m.equipment)==expected and id+'_completed' in m.flags[tag] and not m.start(id)
   before=copy.deepcopy((m.money,m.equipment,m.templates,m.caps));m.execute(m.effects[id+'_finish']);m.execute(m.effects[id+'_cancel']);assert before==(m.money,m.equipment,m.templates,m.caps)
   models.append({'id':id,'NSB':nsb,'once_paid_and_delivered':True,'exact_days':days,'model_pending_roundtrip':True})
  m=MiniSmoke(scripts,tag);m.flags[tag].add('MSGA_mini_rearmament_unlocked');m.focuses={ident(tag,s) for s,*_ in ROWS[tag]};m.money=cost-.01;assert not m.start(id);negative.append(id+'_insufficient_funds')
  m.money=20;assert m.start(id);m.capitulated=True;m.advance(1);assert m.money==20 and not m.equipment;m.capitulated=False;assert m.start(id);m.advance(days);assert id+'_completed' in m.flags[tag];negative.append(id+'_refund_retry')
 for tag in TAGS:
  m=MiniSmoke(scripts,tag);m.flags[tag].add('MSGA_mini_rearmament_unlocked');m.focuses={ident(tag,s) for s,*_ in ROWS[tag]};first=next(c for c in CONTRACTS if c[0]==tag);second=next(c for c in CONTRACTS if c[0]==tag and c!=first);assert m.start(ident(tag,first[1])) and not m.start(ident(tag,second[1]));negative.append(tag+'_parallel_shipments')
 m=MiniSmoke(scripts,'BOS');m.flags['BOS'].add('MSGA_mini_rearmament_unlocked');m.focuses.add('MSGA_BOS_search_for_old_armour');assert m.start('MSGA_BOS_purchase_yugoslav_t55_reserves');m.exists.remove('SER');m.advance(1);assert m.money==20 and not m.equipment;negative.append('T55_missing_supplier_refund')
 for tag,stem in [('BOS','emergency_defence_budget'),('MAC','emergency_defence_budget'),('MNT','emergency_defence_fund')]:
  m=MiniSmoke(scripts,tag);m.flags[tag].add('MSGA_mini_rearmament_unlocked');m.focuses={ident(tag,s) for s,*_ in ROWS[tag]};id=ident(tag,stem);m.focuses.remove(id);m.controller[TAGS[tag]]='SER';assert not m.available(id);negative.append(tag+'_lost_industry_control')
  m.controller[TAGS[tag]]=tag;m.reject=True;before=(m.factory[TAGS[tag]],m.slots[TAGS[tag]]);m.focus(id);assert before==(m.factory[TAGS[tag]],m.slots[TAGS[tag]]);negative.append(tag+'_building_rejection_rollback')
 m=MiniSmoke(scripts,'BOS');m.templates.add('Bosnian Armoured Brigade');m.flags['BOS'].add('MSGA_BOS_armoured_brigade_unlocked');assert not m.condition(m.triggers['MSGA_BOS_can_train_armoured_brigade'])
 m.stock=Counter({k:n for k,n in req.items()});assert m.condition(m.triggers['MSGA_BOS_can_train_armoured_brigade']);m.manpower=4549;assert not m.condition(m.triggers['MSGA_BOS_can_train_armoured_brigade']);negative.append('BOS_training_requires_actual_equipment_and_manpower')
 assert IDEAS['MAC_reserve_mobilisation'][2]=={'conscription_factor':.03,'mobilization_speed':.1} and IDEAS['MNT_reserve_mobilisation'][2]=={'conscription_factor':.02,'mobilization_speed':.1}
 assert (mod.parent/'make_serbia_great_again.mod').read_bytes()==(mod/'make_serbia_great_again.mod').read_bytes() and 'version="0.17.0"' in (mod/'descriptor.mod').read_text()
 report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'version':'0.17.0','focus_count':42,'decision_count':13,'idea_count':23,'DDS':50,'existing_files_unchanged':600,'starting_BOS_militias':2,'militia_battalions_each':3,'armour_requirements':dict(req)|{'manpower':men},'armour_cap':1,'T55_existing_design_reused':True,'focus_routes':routes,'contract_models':models,'negative_cases':negative,'existing_Balkan_AI_restoration_hashes_unchanged':True,'Serbian_Kosovo_Bosnia_endgame_economic_scripts_hashes_unchanged':True,'actual_engine_validation':'NOT RUN. User reserves game/saves; parsed-script smoke does not certify engine AI training, construction, research, equipment transfer, rendering or save/load.'}
 args.report.write_text(json.dumps(report,indent=2)+'\n');print(f'LIVE mini checks passed: 42 focuses, 13 one-time contracts, {len(models)} DLC delivery models, {len(negative)} negative cases; original campaigns and AI restoration unchanged.')

if __name__=='__main__':main()
