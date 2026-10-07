"""Install the approved political chapter in LIVE first, without touching saves/TFR."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageOps, ImageDraw
import hashlib, io, json, math, shutil
from deploy_local import ROOT, SOURCE, TARGET, inventory
from validate_phase1 import parse, get

TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
PACK=Path(r'C:\Users\Balazs\Downloads\MSGA_Yugo_Politics_Visuals_v1.zip')
PREFIX='MSGA_Yugo_Politics_Visuals_v1/'
TREE='common/national_focus/MSGA_SER_endgame.txt'
ROUTES=['socialist','status_quo','nationalist']
CHOICES=['return_to_socialism','keep_the_status_quo','a_national_yugoslavia']
FOCUSES=[
 ('yugoslavia_proclaimed','Yugoslavia Proclaimed',28,19,12,'a_new_yugoslavia',None,'yugoslavia_proclaimed'),
 ('future_of_the_federation','The Future of the Federation',28,19,13,'yugoslavia_proclaimed',None,'the_future_of_the_federation'),
 ('return_to_socialism','Return to Socialism',35,16,14,'future_of_the_federation','socialist','return_to_socialism'),
 ('titos_legacy',"Tito’s Legacy",35,16,15,'return_to_socialism','socialist','titos_legacy'),
 ('socialist_yugoslavia','Socialist Yugoslavia',35,16,16,'titos_legacy','socialist','socialist_yugoslavia'),
 ('keep_the_status_quo','Keep the Status Quo',35,19,14,'future_of_the_federation','status_quo','keep_the_status_quo'),
 ('the_vucic_system','The Vučić System',35,19,15,'keep_the_status_quo','status_quo','the_vucic_system'),
 ('a_stable_federation','A Stable Federation',35,19,16,'the_vucic_system','status_quo','a_stable_federation'),
 ('a_national_yugoslavia','A National Yugoslavia',35,22,14,'future_of_the_federation','nationalist','a_national_yugoslavia'),
 ('national_renewal','National Renewal',35,22,15,'a_national_yugoslavia','nationalist','national_renewal'),
 ('national_yugoslavia','National Yugoslavia',35,22,16,'national_renewal','nationalist','national_yugoslavia'),
]
IDEAS={
 'titos_legacy':("Tito’s Legacy",'titos_legacy',{'stability_factor':.10,'political_power_factor':.10,'industrial_capacity_factory':.05,'recruitable_population_factor':.05,'compliance_growth_on_our_occupied_states':.10,'resistance_target_on_our_occupied_states':-.10}),
 'renewed_socialist_federation':('A Renewed Socialist Federation','socialist_yugoslavia',{'stability_factor':.10,'political_power_factor':.10,'industrial_capacity_factory':.075,'consumer_goods_factor':-.03,'compliance_growth_on_our_occupied_states':.10}),
 'vucic_system':('The Vučić System','the_vucic_system',{'political_power_factor':.15,'stability_factor':.10,'consumer_goods_factor':-.02,'production_speed_buildings_factor':.05,'income_growth_factor':.05}),
 'federal_continuity':('Federal Continuity','a_stable_federation',{'stability_factor':.10,'industrial_capacity_factory':.05,'production_speed_buildings_factor':.05,'political_power_factor':.10,'resistance_target_on_our_occupied_states':-.05}),
 'yugoslav_national_renewal':('Yugoslav National Renewal','national_renewal',{'war_support_factor':.10,'stability_factor':.10,'army_org_factor':.05,'recruitable_population_factor':.05,'political_power_factor':.10,'resistance_target_on_our_occupied_states':-.10}),
 'one_yugoslav_state':('One Yugoslav State','national_yugoslavia',{'stability_factor':.10,'war_support_factor':.10,'industrial_capacity_factory':.05,'army_attack_factor':.05,'army_defence_factor':.05,'recruitable_population_factor':.10}),
}
DESCS={
 'yugoslavia_proclaimed':'The federation has been formed. Its republics now need a political settlement that can give their common institutions lasting authority.',
 'future_of_the_federation':'Three answers compete in Belgrade: socialist renewal, continuity under the existing presidency, or a national Yugoslav state. We must choose one course for the federation.',
 'return_to_socialism':'Ivica Dačić will lead a Yugoslav socialist party built from the existing Serbian organisation. Political mobilisation and federal solidarity will anchor the new government.',
 'titos_legacy':'We will draw on Tito-era federal symbolism and the promise of a common socialist homeland, adapting that legacy to a new century.',
 'socialist_yugoslavia':'A renewed socialist federation will combine political mobilisation with industrial cooperation and a lasting settlement between its republics.',
 'keep_the_status_quo':'The existing presidency will continue to guide the federation. Stability and pragmatic administration take priority over a new political order.',
 'the_vucic_system':'The presidency will consolidate the networks of political negotiation and economic cooperation that hold the federation together.',
 'a_stable_federation':'Continuity has become a federal settlement. Common institutions will offer the republics predictable government and a stable foundation for development.',
 'a_national_yugoslavia':'Vučić will lead a national Yugoslav government. The federation retains its constitutional identity while placing renewed emphasis on common authority and public resolve.',
 'national_renewal':'A programme of national renewal will strengthen public confidence, military cohesion and the authority of federal institutions.',
 'national_yugoslavia':'One Yugoslav state now speaks through a consolidated federal government. The political settlement is complete and the republics remain within the existing federation.',
}
EVENTS=[
 (1,'The Politics of the New Yugoslavia','the_politics_of_the_new_yugoslavia','yugoslavia_proclaimed',None,'The federation exists, but its political character remains unsettled. Delegates arrive in Belgrade as the presidency prepares to open a debate on the future of their common state.','The political debate begins.'),
 (2,'The Political Future of Yugoslavia','the_political_future_of_yugoslavia','future_of_the_federation',None,'Socialists call for solidarity and a renewed federal tradition. Supporters of the presidency argue for continuity and pragmatic government. Nationalists demand stronger common authority. The coming political programme will decide which vision prevails.','We must choose our course.'),
 (3,'The Return of the Red Star','the_return_of_the_red_star','titos_legacy','socialist','The socialist leadership has adopted the red star of the historic Yugoslav tricolour. Dačić presents it as a symbol of solidarity between the republics, rather than a promise to restore every institution of the twentieth century.','A socialist homeland for a new generation.'),
 (4,'Federal Continuity','federal_continuity','a_stable_federation','status_quo','The presidency has secured a settlement based on continuity. Vučić remains at the head of the existing government as the republics turn toward predictable administration and economic cooperation.','The federation stands on firmer ground.'),
 (5,'National Renewal','national_renewal','national_renewal','nationalist','The national government has launched its programme of renewal. Vučić calls for public resolve, cohesive armed forces and a common Yugoslav authority. The federation retains its constitutional name and plain tricolour.','One federation, a common purpose.'),
 (6,'A Yugoslavia for a New Era','a_yugoslavia_for_a_new_era',None,None,'The political debate has reached its conclusion. A settled government now speaks for the federation, while its constituent republics prepare for the next stage of common development.','The political settlement is complete.'),
]

def sha(data):return hashlib.sha256(data).hexdigest()
def route_flag(route):return 'MSGA_yugoslavia_'+route+'_path'
def eligible(route=None,choice=False):
 body='tag = SER has_country_flag = MSGA_yugoslavia_path has_country_flag = MSGA_endgame_yugoslavia_complete has_country_flag = MSGA_yugoslav_federation_proclaimed'
 for r in ROUTES:
  if r==route and not choice:body+=' has_country_flag = '+route_flag(r)
  else:body+=' NOT = { has_country_flag = '+route_flag(r)+' }'
 if choice:body+=' NOT = { has_country_flag = MSGA_yugoslav_political_settlement_complete }'
 return body
def leader(character,subideology,ideology):
 return f'''add_country_leader_role = {{ character = {character} promote_leader = yes country_leader = {{ ideology = {subideology} expire = "2099.1.1.1" }} }}
 set_politics = {{ ruling_party = {ideology} }}
 promote_character = {{ character = {character} ideology = {subideology} }}'''

def main():
 baseline=inventory(TARGET);assert baseline==inventory(SOURCE),'Inspect divergence before editing LIVE'
 assert len(baseline)==528 and 'version="0.14.0"' in (TARGET/'descriptor.mod').read_text()
 native=['common/ideologies/TFR_ideologies.txt','localisation/english/TFR_ideologies_l_english.yml','common/characters/TFR_characters_SER.txt','history/countries/SER - Serbia.txt','events/TFR_events_SER.txt','events/TFR_events_GER.txt','gfx/flags/medium/YUG_communist.tga']
 files={};loc={};sprites=[];assets={};effects=[];blocks=[]
 def put(path,text):
  if not path.endswith(('.yml','.mod')):parse(text)
  text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
  files[path]=text.encode('utf-8-sig' if path.endswith('.yml') else 'utf-8')
 def event(n):return f'country_event = {{ id = MSGA_yugopolitics.{n} }}'
 settlement='set_country_flag = MSGA_yugoslav_political_settlement_complete'
 reward={
  'yugoslavia_proclaimed':'add_political_power = 50 add_stability = 0.05 '+event(1),
  'future_of_the_federation':'add_political_power = 25 '+event(2),
  'return_to_socialism':f'''set_country_flag = {route_flag('socialist')}
   {leader('SER_ivica_dacic','market_socialism','communist')}
   add_popularity = {{ ideology = communist popularity = 0.5 }}
   set_party_name = {{ ideology = communist name = MSGA_yp_socialist_party long_name = MSGA_yp_socialist_party_long }}
   add_stability = 0.10 add_political_power = 75 add_war_support = -0.05''',
  'titos_legacy':'add_ideas = MSGA_yp_titos_legacy '+event(3),
  'socialist_yugoslavia':'MSGA_yp_restore_socialist_identity = yes remove_ideas = MSGA_yp_titos_legacy add_ideas = MSGA_yp_renewed_socialist_federation '+settlement+' '+event(6),
  'keep_the_status_quo':f"set_country_flag = {route_flag('status_quo')} add_political_power = 100 add_stability = 0.10",
  'the_vucic_system':'add_ideas = MSGA_yp_vucic_system',
  'a_stable_federation':'remove_ideas = MSGA_yp_vucic_system add_ideas = MSGA_yp_federal_continuity '+settlement+' '+event(4)+' '+event(6),
  'a_national_yugoslavia':f'''set_country_flag = {route_flag('nationalist')}
   {leader('SER_aleksandar_vucic','autocrat','nationalist')}
   add_popularity = {{ ideology = nationalist popularity = 0.5 }}
   add_war_support = 0.10 add_stability = 0.05 add_political_power = 75''',
  'national_renewal':'add_ideas = MSGA_yp_yugoslav_national_renewal '+event(5),
  'national_yugoslavia':'remove_ideas = MSGA_yp_yugoslav_national_renewal add_ideas = MSGA_yp_one_yugoslav_state '+settlement+' '+event(6),
 }
 for stem,title,days,x,y,parent,route,art in FOCUSES:
  choice=stem in CHOICES;availability=eligible(route,choice)
  exclusions='mutually_exclusive = { '+' '.join('focus = MSGA_'+p for p in CHOICES if p!=stem)+' }' if choice else ''
  blocks.append(f'''focus = {{ id = MSGA_{stem} icon = GFX_MSGA_yp_focus_{stem} x = {x} y = {y} cost = {days/7:g}
   prerequisite = {{ focus = MSGA_{parent} }} {exclusions}
   available = {{ {availability} }} cancel_if_invalid = yes continue_if_invalid = no
   completion_reward = {{ MSGA_yp_focus_{stem} = yes }} }}''')
  effects.append(f'''MSGA_yp_focus_{stem} = {{ if = {{ limit = {{ {availability} has_completed_focus = MSGA_{parent} NOT = {{ has_country_flag = MSGA_yp_done_{stem} }} }}
   set_country_flag = MSGA_yp_done_{stem} {reward[stem]} }} }}''')
  loc['MSGA_'+stem]=title;loc['MSGA_'+stem+'_desc']=DESCS[stem]
 original=(TARGET/TREE).read_text(encoding='utf-8-sig');parse(original)
 assert original.rstrip().endswith('}')
 new_blocks='\n'.join(line.rstrip() for line in '\n'.join(blocks).splitlines())
 put(TREE,original.rstrip()[:-1]+'\n# Approved Yugoslav political continuation, preserving all previous focuses.\n'+new_blocks+'\n}\n')
 effects.append(f'''MSGA_yp_restore_socialist_identity = {{ if = {{ limit = {{ {eligible('socialist')} has_country_flag = MSGA_yp_done_titos_legacy }} set_cosmetic_tag = SER_MSGA_SOCIALIST_YUGOSLAVIA }} }}''')
 put('common/scripted_effects/MSGA_yugoslav_politics_effects.txt','\n'.join(effects)+'\n')
 ev=[]
 for n,title,art,stem,route,desc,option in EVENTS:
  condition=eligible(route) if route else 'tag = SER has_country_flag = MSGA_yugoslavia_path has_country_flag = MSGA_endgame_yugoslavia_complete'
  condition+=' has_country_flag = '+('MSGA_yp_done_'+stem if stem else 'MSGA_yugoslav_political_settlement_complete')
  loc[f'MSGA_yugopolitics.{n}.t']=title;loc[f'MSGA_yugopolitics.{n}.d']=desc;loc[f'MSGA_yugopolitics.{n}.a']=option
  immediate='immediate = { MSGA_yp_restore_socialist_identity = yes }' if n==3 else ''
  ev.append(f'''country_event = {{ id = MSGA_yugopolitics.{n} title = MSGA_yugopolitics.{n}.t desc = MSGA_yugopolitics.{n}.d picture = GFX_MSGA_yp_event_{art}
   is_triggered_only = yes fire_only_once = yes trigger = {{ {condition} }} {immediate}
   option = {{ name = MSGA_yugopolitics.{n}.a }} }}''')
 put('events/MSGA_yugoslav_politics_events.txt','add_namespace = MSGA_yugopolitics\n'+'\n'.join(ev)+'\n')
 ideas=[]
 for stem,(title,art,modifiers) in IDEAS.items():
  name='MSGA_yp_'+stem;loc[name]=title;loc[name+'_desc']=DESCS[art]
  ideas.append(f'{name} = {{ picture = MSGA_yp_idea_{stem} allowed = {{ original_tag = SER }} removal_cost = -1 modifier = {{ '+ ' '.join(f'{k} = {v:g}' for k,v in modifiers.items())+' } }')
 put('common/ideas/MSGA_yugoslav_politics_ideas.txt','ideas = { country = {\n'+'\n'.join(ideas)+'\n} }\n')
 loc['MSGA_yp_socialist_party']='SPJ';loc['MSGA_yp_socialist_party_long']='Socialist Party of Yugoslavia'
 ideologies=[k for k,o,v in get(parse((TFR/native[0]).read_text()),'ideologies')]
 for suffix in ['']+['_'+k for k in ideologies]:
  tag='SER_MSGA_SOCIALIST_YUGOSLAVIA'+suffix;loc[tag]='Yugoslavia';loc[tag+'_DEF']='the Socialist Federal Republic of Yugoslavia';loc[tag+'_ADJ']='Yugoslav'
 put('localisation/english/MSGA_yugoslav_politics_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items())+'\n')
 with ZipFile(PACK) as z:
  manifest=json.loads(z.read(PREFIX+'manifest.json'));assert len(manifest)==17
  def artwork(kind,stem,size,sprite,member):
   raw=z.read(PREFIX+member);im=Image.open(io.BytesIO(raw)).convert('RGBA')
   fitted=ImageOps.fit(im,size,method=Image.Resampling.LANCZOS) if kind=='event_pictures' else ImageOps.contain(im,size,method=Image.Resampling.LANCZOS)
   canvas=Image.new('RGBA',size,(0,0,0,0));canvas.alpha_composite(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2))
   data=io.BytesIO();canvas.save(data,format='DDS',pixel_format='DXT5');blob=data.getvalue();assert blob[84:88]==b'DXT5'
   path='gfx/'+kind+'/MSGA_yp_'+stem+'.dds';files[path]=blob
   sprites.append(f'spriteType = {{ name = "{sprite}" texturefile = "{path}" }}')
   assets[path]={'source_member':PREFIX+member,'source_sha256':sha(raw),'sha256':sha(blob),'size':list(size),'compression':'DXT5','crop':'event fit' if kind=='event_pictures' else 'aspect preserved, transparent canvas'}
  for stem,title,days,x,y,parent,route,art in FOCUSES:
   assert any(a['file']=='focus/'+art+'.png' for a in manifest)
   artwork('interface/goals',stem,(95,85),'GFX_MSGA_yp_focus_'+stem,'focus/'+art+'.png')
   sprites.append(f'spriteType = {{ name = "GFX_MSGA_yp_focus_{stem}_shine" texturefile = "gfx/interface/goals/MSGA_yp_{stem}.dds" }}')
  for n,title,art,*_ in EVENTS:artwork('event_pictures',art,(500,250),'GFX_MSGA_yp_event_'+art,'event/'+art+'.png')
  for stem,(title,art,mods) in IDEAS.items():artwork('interface/ideas',stem,(64,64),'GFX_idea_MSGA_yp_idea_'+stem,'focus/'+art+'.png')
 put('interface/MSGA_yugoslav_politics_assets.gfx','spriteTypes = {\n'+'\n'.join(sprites)+'\n}\n')
 # Native RGBA TGA geometry; a separate cosmetic never overwrites normal flags.
 for folder,size in [('',(82,52)),('medium/',(41,26)),('small/',(10,7))]:
  im=Image.new('RGBA',(size[0]*8,size[1]*8));w,h=im.size;draw=ImageDraw.Draw(im)
  for i,color in enumerate([(0,56,147,255),(255,255,255,255),(216,30,43,255)]):draw.rectangle((0,round(h*i/3),w-1,round(h*(i+1)/3)-1),fill=color)
  def star(radius):return [(w/2+radius*(1 if i%2==0 else .382)*math.sin(math.pi*i/5),h/2-radius*(1 if i%2==0 else .382)*math.cos(math.pi*i/5)) for i in range(10)]
  draw.polygon(star(h*.38),fill=(245,195,40,255));draw.polygon(star(h*.335),fill=(211,28,38,255))
  buf=io.BytesIO();im.resize(size,Image.Resampling.LANCZOS).save(buf,format='TGA');files['gfx/flags/'+folder+'SER_MSGA_SOCIALIST_YUGOSLAVIA.tga']=buf.getvalue()
 for name in ['descriptor.mod','make_serbia_great_again.mod']:
  text=(TARGET/name).read_text(encoding='utf-8-sig');assert 'version="0.14.0"' in text
  put(name,text.replace('version="0.14.0"','version="0.15.0"'))
 backup=ROOT/'logs/yugoslav_politics_backup';backup.mkdir(parents=True,exist_ok=True)
 for p,data in files.items():
  target=TARGET/p;assert target.resolve().is_relative_to(TARGET.resolve())
  if target.exists():
   saved=backup/p;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,saved)
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 launcher=TARGET.parent/'make_serbia_great_again.mod';shutil.copyfile(launcher,backup/'launcher.mod');shutil.copyfile(TARGET/'make_serbia_great_again.mod',launcher)
 record={'version':'0.15.0','runtime':str(TARGET),'package':str(PACK),'package_sha256':sha(PACK.read_bytes()),'baseline_sha256':baseline,'deployed_sha256':{p:sha(d) for p,d in files.items()},'changed_relative_paths':sorted(files),'deployed_absolute_paths':[str(TARGET/p) for p in sorted(files)]+[str(launcher)],'native_sources_sha256':{p:sha((TFR/p).read_bytes()) for p in native},'focuses':FOCUSES,'assets':assets,'normal_flag_sha256':{p:d for p,d in baseline.items() if p.startswith('gfx/flags/') and 'SER_MSGA_YUGOSLAV_FEDERATION' in p},'ideology_keys':{'authoritarian_socialist':'communist','socialist_subideology':'market_socialism','nationalist':'nationalist','nationalist_subideology':'autocrat','status_quo':'conservative'},'leader_reuse':{'socialist':'SER_ivica_dacic','nationalist':'SER_aleksandar_vucic','status_quo':'unchanged'},'actual_engine_validation':'Reserved for user; no game or save touched'}
 (ROOT/'docs/yugoslav_politics_sources.json').write_text(json.dumps(record,indent=2)+'\n')
 print(f'LIVE 0.15.0 installed: {len(files)} relative paths; validate before source sync.')

if __name__=='__main__':main()
