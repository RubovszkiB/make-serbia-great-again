"""Targeted installed syntax/native API, artwork, progression and exclusivity checks."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import argparse, copy, hashlib, json, math, re, subprocess
from validate_phase1 import parse, get, descend, unique
from validate_endgame import Model, val
from validate_bosnia import GAME
from implement_yugoslav_politics import ROOT, TARGET, TFR, FOCUSES, IDEAS, EVENTS, CHOICES, ROUTES, TREE

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Politics(Model):
 def __init__(self,scripts,mod,record):
  super().__init__(scripts,mod,json.loads((ROOT/'docs/endgame_sources.json').read_text()))
  self.events.update({get(v,'id'):v for k,o,v in scripts['events/MSGA_yugoslav_politics_events.txt'] if k=='country_event'})
  self.leader='SER_aleksandar_vucic';self.ideology='conservative'
  self.roles={'SER_aleksandar_vucic':{'conservative'},'SER_ivica_dacic':{'social_democrat'}}
  self.popularity={'communist':.05,'nationalist':.10,'conservative':.40};self.party={'conservative':('SNS','Serbian Progressive Party')};self.promoted={}
  # Reach the gateway through the existing formation AST, including actual
  # modeled subject integrations, instead of inventing completed state flags.
  self.effect('MSGA_try_start_endgame')
  for stem in ['future_of_the_south_slavs','the_yugoslav_idea','a_common_homeland','reconcile_the_republics','draft_a_federal_model']:self.focus(stem)
  for row in self.source['decisions']:
   if row[6]=='yug' and row[5]:self.decision(row[0])
  for stem in ['conference_of_belgrade','the_federal_constitution']:self.focus(stem)
  self.decision('ratify_federal_constitution');self.focus('proclaim_the_federation');self.decision('proclaim_federal_republic_yugoslavia')
  for stem in ['federal_yugoslavia','one_yugoslav_army','one_yugoslav_economy','integrate_the_commands','rebuild_the_common_market','arsenal_of_yugoslavia','yugoslav_development_plan','brotherhood_reforged','a_new_yugoslavia']:self.focus(stem)
  assert set(self.subjects)=={'ALB'} and self.cosmetic=='SER_MSGA_YUGOSLAV_FEDERATION'
 def execute(self,ast,scope='SER'):
  # Run blocks together so the inherited if/else branch semantics are preserved.
  custom={'add_country_leader_role','set_politics','promote_character','add_popularity','set_party_name'}
  batch=[]
  for k,o,v in ast:
   if k not in custom:batch.append((k,o,v));continue
   if batch:super().execute(batch,scope);batch=[]
   assert scope=='SER'
   if k=='add_country_leader_role':
    char=get(v,'character');sub=get(get(v,'country_leader'),'ideology');party={'market_socialism':'communist','autocrat':'nationalist'}[sub]
    self.roles[char].add(party)
    if get(v,'promote_leader')=='yes':self.promoted[party]=char
   elif k=='set_politics':
    self.ideology=get(v,'ruling_party');self.leader=self.promoted.get(self.ideology,self.leader)
   elif k=='promote_character':
    char=get(v,'character');party={'market_socialism':'communist','autocrat':'nationalist'}[get(v,'ideology')]
    assert party in self.roles[char];self.promoted[party]=char
    if self.ideology==party:self.leader=char
   elif k=='add_popularity':
    party=get(v,'ideology');self.popularity[party]=min(1.,max(0.,self.popularity[party]+float(get(v,'popularity'))))
   elif k=='set_party_name':self.party[get(v,'ideology')]=(get(v,'name'),get(v,'long_name'))
  if batch:super().execute(batch,scope)
 def events_ready(self):
  while self.queue:
   id=self.queue.pop(0)
   if id in self.seen:continue
   body=self.events[id]
   if not self.condition(val(body,'trigger',[])):continue
   self.seen.add(id);self.execute(val(body,'immediate',[]));option=[v for k,o,v in body if k=='option'][0]
   self.execute([t for t in option if t[0] not in ['name','ai_chance','trigger']])
 def available(self,stem):
  body=self.focus_ast['MSGA_'+stem]
  return 'MSGA_'+stem not in self.focuses and all(get(v,'focus') in self.focuses for k,o,v in body if k=='prerequisite') and all(value not in self.focuses for k,o,v in body if k=='mutually_exclusive' for key,_,value in v if key=='focus') and self.condition(get(body,'available'))

def main():
 cli=argparse.ArgumentParser();cli.add_argument('--mod-root',type=Path,required=True);cli.add_argument('--report',type=Path,default=ROOT/'docs/yugoslav_politics_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
 record=json.loads((ROOT/'docs/yugoslav_politics_sources.json').read_text());assert mod==TARGET.resolve(strict=True)
 for path,sha in record['baseline_sha256'].items():
  if path not in record['deployed_sha256']:assert digest(mod/path)==sha,path
 for path,sha in record['deployed_sha256'].items():assert digest(mod/path)==sha,path
 for path,sha in record['native_sources_sha256'].items():assert digest(TFR/path)==sha,path
 for path,sha in record['normal_flag_sha256'].items():assert digest(mod/path)==sha,path
 assert digest(Path(record['package']))==record['package_sha256']
 scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ['.txt','.gfx']}
 tree=scripts[TREE][0][2];focuses={get(v,'id'):v for k,o,v in tree if k=='focus'};assert len(focuses)==40
 ids={'MSGA_'+row[0] for row in FOCUSES};old=parse(subprocess.check_output(['git','show','a182e7944cdd528b540ab9f121c5ccf2e7104fd8:make_serbia_great_again/'+TREE],cwd=ROOT).decode('utf-8-sig'))[0][2]
 assert [(k,o,v) for k,o,v in tree if k!='focus' or get(v,'id') not in ids]==old,'Original tree layout, rewards and availability changed'
 unique([(get(b,'x'),get(b,'y')) for b in focuses.values()],'positions')
 unique([get(v,'id') for p,a in scripts.items() if p.startswith('common/national_focus/') for k,o,b in a for k,o,v in b if k=='focus'],'all focus IDs')
 effects=dict((k,v) for k,o,v in scripts['common/scripted_effects/MSGA_yugoslav_politics_effects.txt'])
 for stem,title,days,x,y,parent,route,art in FOCUSES:
  b=focuses['MSGA_'+stem];assert float(get(b,'cost'))*7==days
  assert get(get(b,'prerequisite'),'focus')=='MSGA_'+parent and 'MSGA_'+parent in focuses
  assert (get(b,'x'),get(b,'y'))==(str(x),str(y))
  exclusions={v for k,o,a in b if k=='mutually_exclusive' for k,o,v in a if k=='focus'}
  assert exclusions==({'MSGA_'+s for s in CHOICES if s!=stem} if stem in CHOICES else set())
  if route and stem not in CHOICES:assert ('has_country_flag','=','MSGA_yugoslavia_'+route+'_path') in get(b,'available')
  assert not any(k=='bypass' for k,o,v in b)
 for stem in ['socialist_yugoslavia','a_stable_federation','national_yugoslavia']:
  assert ('set_country_flag','=','MSGA_yugoslav_political_settlement_complete') in list(descend(effects['MSGA_yp_focus_'+stem]))
 ideologies=get(parse((TFR/'common/ideologies/TFR_ideologies.txt').read_text()),'ideologies')
 assert get(get(ideologies,'communist'),'types') and get(get(get(ideologies,'communist'),'types'),'market_socialism') is not None
 assert get(get(get(ideologies,'nationalist'),'types'),'autocrat') is not None
 locnative=(TFR/'localisation/english/TFR_ideologies_l_english.yml').read_text(encoding='utf-8-sig');assert re.search(r'^ communist:.*Authoritarian Socialist',locnative,re.M)
 characters=get(parse((TFR/'common/characters/TFR_characters_SER.txt').read_text()),'characters')
 assert get(characters,'SER_ivica_dacic') and get(characters,'SER_aleksandar_vucic')
 history=(TFR/'history/countries/SER - Serbia.txt').read_text();assert 'recruit_character = SER_ivica_dacic' in history and 'recruit_character = SER_aleksandar_vucic' in history
 for char in ['SER_ivica_dacic','SER_aleksandar_vucic']:
  assert not any(k==char for p,a in scripts.items() if p.startswith('common/characters/') for _,_,b in a for k,_,v in b), 'Reuse native characters'
 tokens={kind:set(re.findall(r'^## (\w+)',(GAME/'documentation'/f'{kind}_documentation.md').read_text(encoding='utf-8-sig'),re.M)) for kind in ['effects','triggers','modifiers']}
 native_modifiers={k for k,o,v in parse((TFR/'common/modifier_definitions/00_TFR_economic_modifiers_definition.txt').read_text())}
 def commands(body):
  for k,o,v in body:
   if k in ['if','else_if','else']:
    conditions(get(v,'limit'));commands([t for t in v if t[0]!='limit'])
   elif k=='hidden_effect':commands(v)
   else:assert k in tokens['effects']|effects.keys(),k
 def conditions(body):
  for k,o,v in body:
   if k in ['AND','OR','NOT']:conditions(v)
   else:assert k in tokens['triggers'],k
 for body in effects.values():commands(body)
 for id in ids:conditions(get(focuses[id],'available'))
 chapter=[t for p,a in scripts.items() if 'yugoslav_politics' in p for t in descend(a)]
 assert not {k for k,o,v in chapter}&{'annex_country','transfer_state','set_state_owner','add_core_of','load_oob','create_unit','add_equipment_to_stockpile','declare_war_on','add_debt','add_income','add_to_variable','set_variable'}
 native_loc='\n'.join(p.read_text(encoding='utf-8-sig') for p in (mod/'localisation/english').glob('*.yml'));keys=re.findall(r'^ ([^:]+):',native_loc,re.M);unique(keys,'localisation')
 sprites={};names=[]
 for p,a in scripts.items():
  if p.startswith('interface/'):
   for _,_,b in a:
    for k,o,v in b:
     if k.lower()=='spritetype':name=get(v,'name').strip('"');names.append(name);sprites[name]=get(v,'texturefile').strip('"')
 unique(names,'sprites')
 for id in ids:
  b=focuses[id];assert id in keys and id+'_desc' in keys
  assert get(b,'icon') in sprites and get(b,'icon')+'_shine' in sprites
 ev={get(v,'id'):v for k,o,v in scripts['events/MSGA_yugoslav_politics_events.txt'] if k=='country_event'};assert len(ev)==6
 unique([get(v,'id') for p,a in scripts.items() if p.startswith('events/') for k,o,v in a if k=='country_event'],'events')
 for id,b in ev.items():
  assert get(b,'picture') in sprites
  for key in ['title','desc']:assert get(b,key) in keys
  assert all(get(v,'name') in keys for k,o,v in b if k=='option');conditions(get(b,'trigger'));commands(val(b,'immediate',[]))
 idea_ast=get(get(scripts['common/ideas/MSGA_yugoslav_politics_ideas.txt'],'ideas'),'country');assert len(idea_ast)==6
 for id,o,b in idea_ast:
  assert id in keys and id+'_desc' in keys and 'GFX_idea_'+get(b,'picture') in sprites
  stem=id.removeprefix('MSGA_yp_');assert dict((k,float(v)) for k,o,v in get(b,'modifier'))==IDEAS[stem][2]
  assert all(k in tokens['modifiers']|native_modifiers for k,o,v in get(b,'modifier'))
 with ZipFile(record['package']) as z:
  for p,a in record['assets'].items():
   assert digest(mod/p)==a['sha256'] and hashlib.sha256(z.read(a['source_member'])).hexdigest()==a['source_sha256']
   assert (mod/p).read_bytes()[84:88]==b'DXT5'
   with Image.open(mod/p) as im:assert list(im.size)==a['size'];im.load()
   assert p in sprites.values()
  assert len(record['assets'])==23
 for folder,size in [('',(82,52)),('medium/',(41,26)),('small/',(10,7))]:
  with Image.open(mod/('gfx/flags/'+folder+'SER_MSGA_SOCIALIST_YUGOSLAVIA.tga')) as im:
   assert im.size==size and im.mode=='RGBA';assert im.getpixel((size[0]//2,size[1]//2))[0]>180
   assert im.getpixel((0,0))[2]>120 and all(len({im.getpixel((x,y)) for x in range(size[0])})>1 for y in [size[1]//2])
 cases=[]
 for route,choice,middle,final,ideology,leader,cosmetic,idea in [
  ('socialist','return_to_socialism','titos_legacy','socialist_yugoslavia','communist','SER_ivica_dacic','SER_MSGA_SOCIALIST_YUGOSLAVIA','renewed_socialist_federation'),
  ('status_quo','keep_the_status_quo','the_vucic_system','a_stable_federation','conservative','SER_aleksandar_vucic','SER_MSGA_YUGOSLAV_FEDERATION','federal_continuity'),
  ('nationalist','a_national_yugoslavia','national_renewal','national_yugoslavia','nationalist','SER_aleksandar_vucic','SER_MSGA_YUGOSLAV_FEDERATION','one_yugoslav_state')]:
  m=Politics(scripts,mod,record);territory=copy.deepcopy((m.states,m.controllers,m.subjects,m.armies,m.stockpiles,m.cores));debt=m.debt;money=m.money
  m.focus('yugoslavia_proclaimed');m.focus('future_of_the_federation');assert all(m.available(c) for c in CHOICES)
  m.focus(choice);assert m.cosmetic=='SER_MSGA_YUGOSLAV_FEDERATION'
  assert m.leader==leader and m.ideology==ideology
  if route=='socialist':assert math.isclose(m.popularity['communist'],.55) and m.party['communist']==('MSGA_yp_socialist_party','MSGA_yp_socialist_party_long')
  if route=='nationalist':assert math.isclose(m.popularity['nationalist'],.60)
  for other in CHOICES:
   if other!=choice:
    assert not m.available(other);before=copy.deepcopy((m.pp,m.flags,m.leader,m.ideology,m.popularity));m.effect('MSGA_yp_focus_'+other);assert before==(m.pp,m.flags,m.leader,m.ideology,m.popularity)
  saved=copy.deepcopy(m);saved.focus(middle);saved.focus(final);m=saved
  assert m.cosmetic==cosmetic and m.leader==leader and m.ideology==ideology
  assert 'MSGA_yugoslav_political_settlement_complete' in m.flags['SER'];assert 'MSGA_yp_'+idea in m.ideas['SER']
  assert len({id for id,_,b in idea_ast}&m.ideas['SER'])==1 and 'MSGA_federation_reborn' in m.ideas['SER']
  assert territory==(m.states,m.controllers,m.subjects,m.armies,m.stockpiles,m.cores) and m.debt==debt and m.money==money
  before=copy.deepcopy((m.pp,m.stability,m.support,m.flags,m.ideas,m.popularity,m.roles));m.effect('MSGA_yp_focus_'+choice);m.effect('MSGA_yp_focus_'+middle);m.effect('MSGA_yp_focus_'+final);assert before==(m.pp,m.stability,m.support,m.flags,m.ideas,m.popularity,m.roles)
  cases.append({'route':route,'leader':leader,'ruling_party':ideology,'cosmetic':cosmetic,'settlement_complete':True,'native_starting_popularity_model':m.popularity[ideology] if route!='status_quo' else None,'territory_debt_armies_unchanged':True,'duplicate_rewards_blocked':True})
 negatives=[]
 for flag in ['MSGA_yugoslavia_path','MSGA_endgame_yugoslavia_complete','MSGA_yugoslav_federation_proclaimed']:
  m=Politics(scripts,mod,record);m.flags['SER'].remove(flag);assert not m.available('yugoslavia_proclaimed');m.effect('MSGA_yp_focus_yugoslavia_proclaimed');assert 'MSGA_yp_done_yugoslavia_proclaimed' not in m.flags['SER'];negatives.append('missing_'+flag)
 m=Politics(scripts,mod,record);m.focuses.clear();assert not m.available('yugoslavia_proclaimed');negatives.append('missing_final_formation_focus')
 m=Politics(scripts,mod,record);m.execute(m.effects['MSGA_yp_focus_yugoslavia_proclaimed'],'CRO');assert 'MSGA_yp_done_yugoslavia_proclaimed' not in m.flags['CRO'];negatives.append('wrong_country')
 for route in ROUTES:
  m=Politics(scripts,mod,record);m.flags['SER'].add('MSGA_yugoslavia_'+route+'_path');m.queue.append('MSGA_yugopolitics.3');m.events_ready();assert m.cosmetic=='SER_MSGA_YUGOSLAV_FEDERATION';negatives.append('premature_red_star_'+route)
 m=Politics(scripts,mod,record);m.flags['SER']|={'MSGA_yugoslavia_socialist_path','MSGA_yugoslavia_nationalist_path'};assert not any(m.available(row[0]) for row in FOCUSES);negatives.append('conflicting_flags_fail_closed')
 m=Politics(scripts,mod,record);m.ideology='authoritarian_democrat';before=(m.leader,m.ideology,m.party.copy());m.focus('yugoslavia_proclaimed');m.focus('future_of_the_federation');m.focus('keep_the_status_quo');m.focus('the_vucic_system');m.focus('a_stable_federation');assert before==(m.leader,m.ideology,m.party);negatives.append('status_quo_preserves_actual_ideology_party')
 # Descriptor identity/path must match the active launcher and actual folder.
 launcher=mod.parent/'make_serbia_great_again.mod';assert launcher.read_bytes()==(mod/'make_serbia_great_again.mod').read_bytes()
 descriptor=launcher.read_text();assert Path(re.search(r'^path="([^"]+)"',descriptor,re.M)[1]).resolve()==mod and 'remote_file_id="3813570241"' in descriptor and 'version="0.15.0"' in descriptor
 report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'version':'0.15.0','focus_ids':sorted(ids),'events':6,'ideas':6,'DDS_assets':23,'socialist_flags':3,'normal_flags_sha256_unchanged':record['normal_flag_sha256'],'three_full_route_models':cases,'negative_cases':negatives,'all_previous_528_files_preserved_except':sorted(set(record['baseline_sha256'])&set(record['deployed_sha256'])),'actual_engine_validation':'NOT RUN. User reserves game tests; native leaders, popularity redistribution and rendering remain engine checks.'}
 args.report.write_text(json.dumps(report,indent=2)+'\n');print(f"Political chapter LIVE checks passed: 3 complete routes, {len(negatives)} negative cases, 11 focuses, 6 events, 6 ideas.")

if __name__=='__main__':main()
