"""Validate the installed post-Kosovo chapter without claiming gameplay acceptance."""
from pathlib import Path
from collections import Counter
import argparse,json,re,subprocess,hashlib,zipfile
from PIL import Image
from validate_phase1 import parse,get,descend,ROOT,unique
from validate_kosovo import CampaignModel
TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV')
def main():
 cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,default=ROOT/'make_serbia_great_again');cli.add_argument('--report',type=Path,default=ROOT/'docs/post_kosovo_validation.json');args=cli.parse_args();mod=args.mod_root.resolve()
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
 tree=scripts['common/national_focus/MSGA_SER_post_kosovo.txt'][0][2];focus={get(v,'id'):v for k,_,v in tree if k=='focus'}
 ids=['restore_order_in_kosovo','review_kosovo_administration','consolidate_serbian_authority','rebuild_kosovo','invest_in_pristina','a_lasting_peace','the_serbian_question'];ids=['MSGA_'+x for x in ids]
 assert list(focus)==ids and [int(get(focus[i],'cost'))*7 for i in ids]==[14,7,14,21,21,14,7]
 assert [get(v,'focus') for k,_,v in focus[ids[5]] if k=='prerequisite']==ids[3:5]
 assert 'MSGA_the_cost_of_integration' not in focus
 # Previously implemented gameplay must survive unchanged, apart from chapter loading.
 for path in ['common/national_focus/MSGA_SER_phase1.txt','common/national_focus/MSGA_SER_kosovo_war.txt','events/MSGA_SER_kosovo_events.txt','common/decisions/MSGA_SER_expansion.txt','common/decisions/MSGA_SER_phase1.txt','common/ideas/MSGA_SER_ideas.txt','common/bop/MSGA_SER_bop.txt']:
  before=parse(subprocess.check_output(['git','show','09f9212:make_serbia_great_again/'+path],cwd=ROOT).decode('utf-8-sig'))
  if path.endswith('MSGA_SER_phase1.txt'):
   # Only the removed Kosovo filler unlock tooltips may differ from this baseline.
   def strip_filler(ast):
    removed={'MSGA_commission_kosovo_dossier','MSGA_assess_kfor','MSGA_consult_general_staff','MSGA_contact_regional_partners','MSGA_map_northern_contingencies'}
    return [(k,o,strip_filler(v) if isinstance(v,list) else v) for k,o,v in ast if not(k=='unlock_decision_tooltip' and v in removed)]
   assert strip_filler(scripts[path])==strip_filler(before),path
  else:assert scripts[path]==before,path
 effects=scripts['common/scripted_effects/MSGA_SER_post_kosovo_effects.txt']
 core_operations=[]
 for name,_,ast in effects:
  for k,_,v in ast:
   if k=='if':
    for state,_,body in v:
     if state in ('785','1305'):
      core_operations.extend((state,target) for key,_,target in body if key=='add_core_of')
 assert core_operations==[('1305','SER'),('785','SER'),('1305','SER')]
 assert not any(k in ('declare_war_on','annex_country','transfer_state','create_wargoal','add_state_core') for path in ['common/scripted_effects/MSGA_SER_post_kosovo_effects.txt','events/MSGA_SER_post_kosovo_events.txt','common/national_focus/MSGA_SER_bosnian_crisis.txt'] for k,_,_ in descend(scripts[path]))
 events={get(v,'id'):v for k,_,v in scripts['events/MSGA_SER_post_kosovo_events.txt'] if k=='country_event'};assert len(events)==15
 locales='\n'.join(p.read_text(encoding='utf-8-sig') for p in (mod/'localisation/english').glob('*.yml'))
 sprites={get(v,'name').strip('"'):v for path,ast in scripts.items() if path.startswith('interface/') for k,_,v in descend(ast) if k.lower()=='spritetype'}
 for id,body in focus.items():assert get(body,'icon') in sprites and get(body,'icon')+'_shine' in sprites
 for i,body in events.items():
  assert get(body,'fire_only_once')=='yes' and get(body,'picture') in sprites
  for suffix in ['t','d','a']:assert re.search(r'^ '+re.escape(i+'.'+suffix)+r':0 ',locales,re.M)
 pack=ROOT/'art/post_kosovo_assets/MSGA_Post_Kosovo_Visual_Assets';manifest=json.loads((pack/'asset_manifest.json').read_text());alpha={}
 for group,size,key,folder in [('focuses',(95,95),'dds_95x95','goals'),('events',(474,156),'dds_474x156','events'),('decisions',(60,60),'dds_60x60','decisions')]:
  for asset in manifest[group]:
   id=asset['id'].replace('SER_','MSGA_',1);p=mod/f'gfx/interface/{folder}/{id}.dds';assert p.read_bytes()==(pack/asset[key]).read_bytes();img=Image.open(p).convert('RGBA');assert img.size==size;assert img.getchannel('A').getextrema()[1]>0;alpha[id]=img.getchannel('A').getextrema()
 # Start conditions and modules are checked against Serbia's actual researched technologies.
 history=get(parse((TFR/'history/countries/SER - Serbia.txt').read_text(encoding='utf-8-sig')),'set_technology')
 techs={k for k,_,v in history if v=='1'}
 country=parse((TFR/'history/countries/SER - Serbia.txt').read_text(encoding='utf-8-sig'))
 for k,_,v in country:
  if k=='if':
   for name,_,body in v:
    if name=='set_technology':techs.update(a for a,_,b in body if b=='1')
 native_techs={}
 for p in (TFR/'common/technologies').glob('*.txt'):
  for k,_,ast in parse(p.read_text(encoding='utf-8-sig')):
   if k=='technologies':native_techs.update({a:b for a,_,b in ast if isinstance(b,list)})
 enabled=set();equip=set()
 for id in techs:
  for k,_,v in native_techs.get(id,[]):
   if k=='enable_equipment_modules':enabled.update(a for a,_,_ in v)
   if k=='enable_equipments':equip.update(a for a,_,_ in v)
 assert {'modern_tank_chassis_1','mechanized_equipment_1','light_mechanized_equipment_1'} <= equip
 variant_bodies=[v for k,_,v in descend(scripts['common/scripted_effects/MSGA_SER_vehicle_effects.txt']) if k=='create_equipment_variant' and get(v,'type')=='modern_tank_chassis_1']
 assert [get(v,'name').strip('"') for v in variant_bodies]==['M-84A','T-55A']
 modules=get(parse((TFR/'common/units/equipment/modules/00_tank_modules.txt').read_text(encoding='utf-8-sig')),'equipment_modules')
 chassis=get(get(parse((TFR/'common/units/equipment/tank_chassis.txt').read_text(encoding='utf-8-sig')),'equipments'),'modern_tank_chassis');slots=get(chassis,'module_slots');stats={}
 for body in variant_bodies:
  fitted=get(body,'modules');assert {v for _,_,v in fitted}<=enabled
  for slot,_,module in fitted:
   assert get(get(modules,module),'category') in {k for k,_,_ in get(get(slots,slot),'allowed_module_categories')}
  for slot,_,data in slots:
   if any(k=='required' and v=='yes' for k,_,v in data):assert slot in {k for k,_,_ in fitted}
  values={k:float(get(chassis,k)) for k in ['build_cost_ic','reliability','armor_value','hardness','maximum_speed','breakthrough']};mul=Counter()
  for _,_,module in fitted:
   for k,_,v in get(modules,module):
    if k=='add_stats':
     for a,_,b in v:values[a]=values.get(a,0)+float(b)
    if k=='multiply_stats':
     for a,_,b in v:mul[a]+=float(b)
  for k,v in mul.items():values[k]*=1+v
  stats[get(body,'name').strip('"')]=values
 assert stats['M-84A']['build_cost_ic']<10 and stats['M-84A']['armor_value']<40 and .65<=stats['M-84A']['reliability']<=.85
 assert get(variant_bodies[1],'obsolete')=='yes'
 # Equipment totals come from the actual battalion/support definitions, not the concept image.
 units={}
 for base in [GAME,TFR]:
  for p in (base/'common/units').glob('*.txt'):
   for k,_,v in parse(p.read_text(encoding='utf-8-sig')):
    if k=='sub_units':units.update({a:b for a,_,b in v})
 template=scripts['history/units/MSGA_SER_kosovo_brigade_template.txt'][0][2];required=Counter();width=0
 for group in ['regiments','support']:
  for unit,_,position in get(template,group):
   assert unit in units
   required.update({k:int(v) for k,_,v in get(units[unit],'need')})
   width+=int(next((v for k,_,v in units[unit] if k=='combat_width'),'0'))
 assert width==16 and required['modern_tank_chassis']==14
 for suffix,tank in [('', 'modern_tank_chassis_1'),('_legacy','modern_tank_equipment_1')]:
  spawned=get(scripts['history/units/MSGA_SER_kosovo_brigade'+suffix+'.txt'][0][2],'division')
  assert get(spawned,'start_equipment_factor')=='1' and get(spawned,'start_manpower_factor')=='1'
  assert get(get(get(spawned,'force_equipment_variants'),tank),'version_name')=='"T-55A"'
 assert not any(k=='add_equipment_to_stockpile' for k,_,_ in descend(scripts['common/scripted_effects/MSGA_SER_vehicle_effects.txt']))
 # Treasury/core guards also prevent direct effect calls from granting a premature brigade.
 premature=CampaignModel(scripts);premature.execute(parse('MSGA_raise_kosovo_brigade = yes'));assert premature.money==10 and not premature.loaded_oobs
 legacy=CampaignModel(scripts);legacy.dlc=False;legacy.execute(parse('MSGA_initialize_serbian_vehicles = yes'));assert legacy.variants==['BVP M-80A','BTR-80A','M-84A','T-55A']
 # Execute parsed rewards in both economic branch orders and after a serialized model checkpoint.
 for order in [ids[3:5],list(reversed(ids[3:5]))]:
  model=CampaignModel(scripts);model.states=model.controllers={785:'SER',1305:'SER'};model.flags['SER'].update(['MSGA_kosovo_resolution_done','MSGA_kosovo_victory_queued']);model.ideas['SER'].add('SER_rebellion_of_kosovo')
  model.execute(parse('MSGA_enter_post_kosovo_chapter = yes'));assert model.tree=='MSGA_SER_post_kosovo'
  before=model.events.copy();model.execute(parse('MSGA_open_post_kosovo = yes'));assert model.events==before
  model.execute(get(focus[ids[0]],'completion_reward'));assert model.cores[1305]=={'SER'} and not model.cores[785]
  model.execute(get(focus[ids[1]],'completion_reward'));assert model.debt==0 and not model.cores[785]
  model.execute([x for x in get(events['MSGA_postkosovo.3'],'option') if x[0] not in ('name','ai_chance')]);assert model.debt==1 and model.money==10 and model.cores[785]=={'SER'}
  model.execute([x for x in get(events['MSGA_postkosovo.3'],'option') if x[0] not in ('name','ai_chance')]);assert model.debt==1
  model.execute(get(focus[ids[2]],'completion_reward'));assert 'SER_rebellion_of_kosovo' not in model.ideas['SER']
  for id in order:model.execute(get(focus[id],'completion_reward'))
  assert model.buildings[785]=={'infrastructure':4,'industrial_complex':2,'office_park':1}
  assert abs(model.development-.10)<1e-8 and len(model.damage_repaired)==3
  before=model.buildings[785].copy()
  for id in order:model.execute(get(focus[id],'completion_reward'))
  assert before==model.buildings[785]
  decision=scripts['common/decisions/MSGA_SER_post_kosovo.txt'][0][2][0][2];assert get(decision,'cost')=='0' and model.condition(get(decision,'available'))
  model.money=1.99;assert not model.condition(get(decision,'custom_cost_trigger'));model.execute(get(decision,'complete_effect'));assert not model.loaded_oobs
  model.money=2;model.execute(get(decision,'complete_effect'));assert model.money==0 and model.loaded_oobs==['MSGA_SER_kosovo_brigade_template','MSGA_SER_kosovo_brigade']
  model.execute(get(decision,'complete_effect'));assert len(model.loaded_oobs)==2
  checkpoint=json.loads(json.dumps({c:list(flags) for c,flags in model.flags.items()}));model.flags={c:set(flags) for c,flags in checkpoint.items()}
  model.execute(parse('MSGA_initialize_serbian_vehicles = yes'));assert model.variants.count('M-84A')==1
  model.execute(get(focus[ids[5]],'completion_reward'));model.execute(get(focus[ids[6]],'completion_reward'));assert model.tree=='MSGA_SER_bosnian_crisis'
  for i in [12,13,14]:model.execute(get(events[f'MSGA_postkosovo.{i}'],'immediate'))
  assert model.tree=='MSGA_SER_bosnian_crisis' and not model.wars
  before=len(model.events);model.execute(parse('MSGA_enter_bosnian_chapter = yes MSGA_enter_post_kosovo_chapter = yes'));assert len(model.events)==before and model.tree=='MSGA_SER_bosnian_crisis'
 # 0.9: the actual new options must pay once, use fractional native development,
 # and unlock exactly one final decision after BOTH existing focus rewards.
 final=get(scripts['common/decisions/MSGA_SER_post_kosovo.txt'][0][2],'MSGA_finish_kosovo_reconstruction')
 assert get(final,'cost')=='50' and get(final,'fire_only_once')=='yes'
 assert get(final,'custom_cost_trigger')==parse('check_variable = { var = income_var value = 1 compare = greater_than_or_equals }')
 choices=[v for k,_,v in events['MSGA_postkosovo.9'] if k=='option'];assert len(choices)==2
 for choice,expected_cost,expected_development in zip(choices,[.5,0],[.15,.13]):
  reconstruction=CampaignModel(scripts);reconstruction.states=reconstruction.controllers={785:'SER',1305:'SER'};reconstruction.flags['SER'].add('MSGA_kosovo_fully_integrated')
  assert not reconstruction.condition(get(final,'visible'))
  reconstruction.execute(get(focus['MSGA_rebuild_kosovo'],'completion_reward'));assert not reconstruction.condition(get(final,'visible'))
  reconstruction.execute(get(focus['MSGA_invest_in_pristina'],'completion_reward'));assert reconstruction.condition(get(final,'visible'))
  reward=[x for x in choice if x[0] not in ('name','trigger','ai_chance')]
  reconstruction.execute(reward);reconstruction.execute(reward)
  assert reconstruction.money==10-expected_cost and abs(reconstruction.development-expected_development)<1e-8
  assert reconstruction.buildings[785]=={'infrastructure':5,'industrial_complex':3 if expected_cost else 2,'office_park':1 if expected_cost else 2}
  assert ('MSGA_kosovo_development_program',180) in reconstruction.timed_ideas
  assert 'MSGA_kosovo_reconstruction_state' in reconstruction.modifiers[785]
  reconstruction.execute(get(final,'complete_effect'));reconstruction.execute(get(final,'complete_effect'))
  assert reconstruction.money==9-expected_cost and abs(reconstruction.development-expected_development-.05)<1e-8
  assert not reconstruction.condition(get(final,'visible')) and not reconstruction.modifiers[785]
  assert reconstruction.events.count(('SER','MSGA_postkosovo.15'))==1
 # Insufficient treasury cannot produce a free state-funded city upgrade.
 poor=CampaignModel(scripts);poor.states[785]=poor.controllers[785]='SER';poor.money=.49
 poor.execute(parse('MSGA_pristina_state_investment = yes'));assert poor.money==.49 and poor.development==0
 new_ideas=get(get(scripts['common/ideas/MSGA_reconstruction_ideas.txt'],'ideas'),'country')
 assert get(get(new_ideas,'MSGA_pristina_private_capital'),'modifier')==parse('business_value_factor = 0.05 income_growth_factor = 0.02')
 assert get(get(new_ideas,'MSGA_kosovo_development_program'),'modifier')==parse('industrial_development_monthly = 0.005')
 state_modifier=get(scripts['common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt'],'MSGA_kosovo_reconstruction_state')
 assert get(state_modifier,'state_production_speed_buildings_factor')=='0.10'
 assert all(float(v)==.20 for k,_,v in state_modifier if k.startswith('state_repair_speed_'))
 # Supplied DDS bytes are used unchanged, including their authored 474x178 size.
 image_map={'MSGA_bosnia.6':'srpska_uprising','MSGA_bosnia.9':'serbia_enters_bosnian_war','MSGA_bosnia.10':'bosnia_capitulation','MSGA_postbosnia.12':'question_of_republika_srpska','MSGA_postkosovo.7':'kosovo_reconstruction_begins','MSGA_postkosovo.9':'future_of_pristina','MSGA_postkosovo.15':'kosovo_rebuilt'}
 all_events={get(v,'id'):v for path,ast in scripts.items() if path.startswith('events/') for k,_,v in ast if k=='country_event'}
 supplied_hashes={}
 package_path=Path('C:/Users/Balazs/Downloads/MSGA_TFR_Bosnia_Kosovo_Event_Assets_70d.zip')
 with zipfile.ZipFile(package_path) as package:
  previous=parse(package.read('MSGA_TFR_Bosnia_Kosovo_Event_Assets_70d/interface/MSGA_eventpictures.gfx').decode('utf-8-sig'))
  # The shared Srpska question sprite moved to the complete supplied 100-day GFX.
  old_entries=[(k,o,v) for k,o,v in previous[0][2] if get(v,'name').strip('"')!='GFX_MSGA_event_question_of_republika_srpska']
  assert scripts['interface/MSGA_eventpictures.gfx'][0][2]==old_entries
  for id,stem in image_map.items():
   key='GFX_MSGA_event_'+stem;relative='gfx/event_pictures/MSGA_event_'+stem+'.dds';data=(mod/relative).read_bytes()
   assert get(all_events[id],'picture')==key and get(sprites[key],'texturefile').strip('"')==relative
   if stem=='question_of_republika_srpska':
    latest=json.loads((ROOT/'docs/post_bosnia_sources.json').read_text())['assets']
    assert hashlib.sha256(data).hexdigest()==latest[relative]['sha256']
   else:assert data==package.read('MSGA_TFR_Bosnia_Kosovo_Event_Assets_70d/'+relative)
   img=Image.open(mod/relative).convert('RGBA');assert img.size==(474,178) and img.getchannel('A').getextrema()[1]>0
   supplied_hashes[relative]=hashlib.sha256(data).hexdigest()
 assert 'MSGA_kosovo_crisis' not in [k for k,_,_ in scripts['common/decisions/categories/MSGA_SER_categories.txt']]
 assert [k for k,_,_ in scripts['common/decisions/MSGA_SER_strategic_review.txt']]==['MSGA_strategic_review']
 report={'static_validation':'passed','validated_mod_root':str(mod),'focus_days':[14,7,14,21,21,14,7],'north_state':1305,'remaining_state':785,'integration_debt_B':1,'integration_treasury_debit':0,'removed_native_spirit':'SER_rebellion_of_kosovo','militia_treasury_B':2,'militia_PP':0,'brigade_width':width,'brigade_equipment_required':dict(required),'variant_stats_before_country_tech_modifiers':stats,'legal_starting_modules':True,'supplied_DDS_assets':22,'visible_events':15,'postwar_rewards_in_either_order':'passed','debt_and_spawn_idempotence':'passed','Bosnian_transition_without_war':'passed','save_load':'model flag checkpoint passed; actual engine save/load not tested','gameplay_rendering_and_production_UI':'not certified by these checks'}
 report.update({'version':'0.10.0','reconstruction_model':'passed: both choices, insufficient treasury, one-time payments, fractional development, infrastructure cap, final decision gating and cleanup','new_supplied_DDS_hashes':supplied_hashes,'supplied_event_image_dimensions':[474,178],'state_repair_bonus':.20,'state_construction_bonus':.10,'temporary_development_monthly':.005,'private_capital_business_value':.05,'private_capital_monthly_income_growth':.02,'removed_filler_decisions':5})
 args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
