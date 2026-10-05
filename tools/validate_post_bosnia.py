"""Validate installed post-Bosnia scripts and execute their actual AST.

Models are deterministic dependency/payment tests, not an engine playthrough.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import hashlib
import io
import itertools
import json
import re
import subprocess
import zipfile
from PIL import Image
from validate_phase1 import ROOT, parse, get, descend, unique
from validate_bosnia import BosniaModel, TFR, GAME

class PostBosniaModel(BosniaModel):
    def __init__(self,scripts,mod):
        super().__init__(scripts,mod)
        self.xp=0;self.pp=100;self.stability=0;self.support=0;self.bop=0;self.has_bop=True
        self.doctrines=[];self.opinions={};self.once_events=set();self.templates={}
        for s in self.states:
            self.buildings[s]={'infrastructure':2};self.extra_slots[s]=0;self.modifiers[s]=set()
        self.cores[107]={'SER'};self.provinces[11586]='SER'

    def condition(self,ast,scope='SER'):
        for k,o,v in ast:
            if k=='check_variable':
                value={'income_var':self.money,'debt_var':self.debt}[get(v,'var')]
                comparison=get(v,'compare');target=float(get(v,'value'))
                ok=value>=target if comparison=='greater_than_or_equals' else value>target
            elif k=='has_power_balance':ok=self.has_bop and get(v,'id')=='MSGA_SER_streets_presidency'
            elif k=='state':ok=scope==int(v)
            elif k=='owner':ok=self.condition(v,self.states[scope])
            elif k=='is_fully_controlled_by' and v=='OWNER':ok=self.controllers[scope]==self.states[scope]
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
            if k in ('every_state','every_subject_country','random_owned_controlled_state'):
                if k=='every_state':targets=list(self.states)
                elif k=='every_subject_country':targets=[t for t,overlord in self.subjects.items() if overlord==scope and t in self.exists]
                else:targets=[s for s in self.states if self.states[s]==scope and self.controllers[s]==scope][:1]
                limit=next((b for a,_,b in v if a=='limit'),[])
                for target in targets:
                    if self.condition(limit,target):self.execute([x for x in v if x[0]!='limit'],target)
            elif k=='set_temp_variable':
                value=get(v,'value');self.temp=self.debt if value=='debt_var' else float(value)
            elif k=='multiply_temp_variable':self.temp*=float(get(v,'value'))
            elif k=='add_power_balance_value':self.bop+=float(get(v,'value'))
            elif k=='add_opinion_modifier':self.opinions[(scope,get(v,'target'))]=get(v,'modifier')
            elif k=='add_doctrine_cost_reduction':self.doctrines.append(v)
            elif k=='army_experience':self.xp+=float(v)
            elif k=='add_political_power':self.pp+=float(v)
            elif k=='add_stability':self.stability+=float(v)
            elif k=='add_war_support':self.support+=float(v)
            elif k=='unlock_decision_tooltip':pass
            elif k=='remove_ideas':
                self.ideas[scope].discard(v);self.timed=[x for x in self.timed if x[0]!=v]
            elif k=='load_oob':
                body=parse((self.mod/'history/units'/f'{v.strip(chr(34))}.txt').read_text(encoding='utf-8-sig'))
                for a,_,b in body:
                    if a=='division_template':self.templates[(scope,get(b,'name'))]=b
                super().execute([(k,o,v)],scope)
            elif k=='annex_country':
                assert get(v,'transfer_troops')=='yes'
                target=get(v,'target');self.units=[(scope if t==target else t,n,p) for t,n,p in self.units]
                for (tag,name),template in list(self.templates.items()):
                    if tag==target:self.templates[(scope,name)]=template
                super().execute([(k,o,v)],scope)
            else:super().execute([(k,o,v)],scope)

    def advance(self,days):
        end=self.day+days
        while self.queue and min(self.queue)[0]<=end:
            item=min(self.queue);self.queue.remove(item);self.day,scope,id=item
            body=self.event_ast[id]
            if get(body,'id') in self.once_events:continue
            trigger=next((b for a,_,b in body if a=='trigger'),[])
            if not self.condition(trigger,scope):continue
            self.delivered.append(item)
            if ('fire_only_once','=','yes') in body:self.once_events.add(id)
            self.execute(next((b for a,_,b in body if a=='immediate'),[]),scope)
        self.day=end

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--mod-root',type=Path,required=True)
    cli.add_argument('--report',type=Path,default=ROOT/'docs/post_bosnia_validation.json')
    args=cli.parse_args();mod=args.mod_root.resolve()
    scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
    tree=scripts['common/national_focus/MSGA_SER_post_bosnia.txt'][0][2]
    focuses={get(b,'id'):b for k,_,b in tree if k=='focus'}
    assert len(focuses)==12 and all(get(b,'cost')=='2' for b in focuses.values())
    positions=[(get(b,'x'),get(b,'y')) for b in focuses.values()];unique(positions,'post-Bosnia positions')
    opening=['MSGA_victory_in_bosnia','MSGA_rebuild_the_west','MSGA_new_serbian_era']
    branches=[['MSGA_lessons_bosnian_war','MSGA_arm_new_serbian_sphere','MSGA_serbian_defence_network'],['MSGA_consolidate_victory','MSGA_bind_new_protectorates','MSGA_serbian_sphere'],['MSGA_repair_war_economy','MSGA_serbian_industrial_consolidation','MSGA_economic_heart_balkans']]
    graph={id:[get(v,'focus') for k,_,v in b if k=='prerequisite'] for id,b in focuses.items()}
    assert graph[opening[0]]==[]
    for sequence in [opening]+[[opening[-1]]+branch for branch in branches]:
        for prior,current in zip(sequence,sequence[1:]):assert graph[current]==[prior]
    # Earlier approved tree topology and reward data remain unchanged.
    for path in ['common/national_focus/MSGA_SER_phase1.txt','common/national_focus/MSGA_SER_kosovo_war.txt','common/national_focus/MSGA_SER_post_kosovo.txt','common/national_focus/MSGA_SER_bosnian_crisis.txt','common/bop/MSGA_SER_bop.txt','common/scripted_effects/MSGA_SER_vehicle_effects.txt']:
        before=subprocess.check_output(['git','show','b4d79a4:make_serbia_great_again/'+path],cwd=ROOT).decode('utf-8-sig')
        assert scripts[path]==parse(before),f'Unrelated earlier content changed: {path}'
    tags='\n'.join(p.read_text(encoding='utf-8-sig') for p in (TFR/'common/country_tags').glob('*.txt'))
    assert all(re.search(r'^'+t+r'\s*=\s*"countries/',tags,re.M) for t in ['BOS','HRZ','SRP'])
    sources=json.loads((ROOT/'docs/post_bosnia_sources.json').read_text())
    # No modifications to the upstream mod, and no new country tags or replace_path.
    assert not (mod/'common/country_tags').exists()
    assert 'replace_path' not in (mod/'descriptor.mod').read_text()
    locales='\n'.join(p.read_text(encoding='utf-8-sig') for p in (mod/'localisation/english').glob('*.yml'))
    keys=re.findall(r'^ ([^:]+):',locales,re.M);unique(keys,'localisation')
    for id in focuses:assert id in keys and id+'_desc' in keys
    sprites={get(v,'name').strip('"'):v for p,ast in scripts.items() if p.startswith('interface/') for k,_,v in descend(ast) if k.lower()=='spritetype'}
    sprite_names=[get(v,'name').strip('"') for p,ast in scripts.items() if p.startswith('interface/') for k,_,v in descend(ast) if k.lower()=='spritetype'];unique(sprite_names,'sprites')
    used_assets=set()
    for id,b in focuses.items():
        for key in [get(b,'icon'),get(b,'icon')+'_shine']:
            assert key in sprites;used_assets.add(get(sprites[key],'texturefile').strip('"'))
    events={get(v,'id'):v for k,_,v in scripts['events/MSGA_post_bosnia_events.txt'] if k=='country_event'}
    assert len(events)==16
    for id,body in events.items():
        assert id+'.t' in keys and id+'.d' in keys
        assert get(body,'picture') in sprites
        used_assets.add(get(sprites[get(body,'picture')],'texturefile').strip('"'))
        for k,_,option in body:
            if k=='option':assert get(option,'name') in keys
    decisions=dict((k,v) for k,_,v in scripts['common/decisions/MSGA_post_bosnia_decisions.txt'][0][2])
    for id,body in decisions.items():
        assert id in keys and id+'_desc' in keys
        assert get(body,'icon') in sprites;used_assets.add(get(sprites[get(body,'icon')],'texturefile').strip('"'))
    assert len(decisions)==3
    with zipfile.ZipFile(sources['package']) as supplied:
        assert hashlib.sha256(Path(sources['package']).read_bytes()).hexdigest()==sources['package_sha256']
        for rel,record in sources['assets'].items():
            data=(mod/rel).read_bytes();assert data==supplied.read(record['package_entry'])
            if rel.endswith('.dds'):
                assert rel in used_assets
                im=Image.open(io.BytesIO(data)).convert('RGBA')
                png='source_png/'+('event_pictures/' if '/event_pictures/' in rel else 'focus_icons/' if '/goals/' in rel else 'decision_icons/')+Path(rel).stem+'.png'
                original=Image.open(io.BytesIO(supplied.read(png))).convert('RGBA')
                assert im.size==original.size and im.tobytes()==original.tobytes()
    ideas=get(get(scripts['common/ideas/MSGA_post_bosnia_ideas.txt'],'ideas'),'country')
    docs=(GAME/'documentation/modifiers_documentation.md').read_text()
    for id,_,body in ideas:
        assert 'GFX_idea_'+get(body,'picture') in sprites
        for key,_,v in get(body,'modifier'):
            assert '\n## '+key+'\n' in docs or key in ('income_growth_factor','business_value_factor')
            assert abs(float(v))<=.10,f'Bad percentage scaling {id}: {key}={v}'
    sphere=get(get(ideas,'MSGA_serbian_sphere_spirit'),'modifier')
    assert get(sphere,'political_power_factor')=='0.05' and get(sphere,'stability_factor')=='0.03'
    heart=get(get(ideas,'MSGA_economic_heart_spirit'),'modifier')
    assert heart==parse('consumer_goods_factor = -0.02 industrial_capacity_factory = 0.05 business_value_factor = 0.05 income_growth_factor = 0.02')
    assert get(get(ideas,'MSGA_integrated_protectorate'),'modifier')==parse('autonomy_gain_global_factor = -0.10 autonomy_gain_trade_factor = -0.10 trade_opinion_factor = 0.10')
    for tag in ['BOS','HRZ']:
        oob=scripts[f'history/units/MSGA_{tag}_auxiliary_militias.txt']
        template=get(oob,'division_template');grid=get(template,'regiments')
        assert len(grid)==3 and all(k=='militia' for k,_,v in grid)
        assert not any(k=='support' for k,_,v in template)
        units=[v for k,_,v in descend(oob) if k=='division'];assert len(units)==2
        assert all(get(u,'location')=='11586' and get(u,'start_equipment_factor')=='1' for u in units)
    new_template=get(scripts['history/units/MSGA_SER_srpska_td_template.txt'],'division_template')
    old_template=get(scripts['history/units/MSGA_SER_kosovo_brigade_template.txt'],'division_template')
    assert [x for x in new_template if x[0]!='name']==[x for x in old_template if x[0]!='name']
    assert get(new_template,'name')=='"Srpska Teritorijalna Odbrana"'
    # Reuse exact tank/IFV/APC variant package in both DLC modes, change only name/location.
    for suffix in ['', '_legacy']:
        original=(mod/f'history/units/MSGA_SER_kosovo_brigade{suffix}.txt').read_text().replace('Kosovska Mehanizovana Brigada','Srpska Teritorijalna Odbrana').replace('location = 14400','location = 11586')
        assert parse(original)==scripts[f'history/units/MSGA_SER_srpska_td{suffix}.txt']
    effects=scripts['common/scripted_effects/MSGA_bosnia_effects.txt']
    assert ('country_event','=',parse('id = MSGA_postbosnia.12 days = 100')) in descend(get(effects,'MSGA_settle_bosnia'))
    assert ('MSGA_open_post_bosnia','=','yes') in descend(get(effects,'MSGA_settle_bosnia'))
    assert ('annex_country','=',parse('target = SRP transfer_troops = yes')) in descend(get(effects,'MSGA_unite_srpska'))
    assert not any(k=='add_core_of' for k,_,v in descend(get(effects,'MSGA_unite_srpska')))

    def settled():
        m=PostBosniaModel(scripts,mod)
        m.execute(parse('MSGA_open_post_bosnia = yes'));assert 'MSGA_post_bosnia_started' not in m.flags['SER']
        m.exists.add('SRP');m.wars={frozenset(('BOS','SER')),frozenset(('BOS','SRP'))}
        m.flags['SER'].update(['MSGA_bosnian_crisis_active','MSGA_bosnian_war_started','MSGA_bosnia_intervened','MSGA_bosnia_defeated'])
        m.factions['SER']='MSGA_serbian_alliance';m.faction_leader['MSGA_serbian_alliance']='SER'
        m.units=[('SRP','Native Srpska Guard',6983)]
        m.templates[('SRP','Native Srpska Guard')]=parse('name = "Native Srpska Guard" regiments = { militia = { x = 0 y = 0 } }')
        m.execute(parse('MSGA_settle_bosnia = yes'))
        assert m.tree=='MSGA_SER_post_bosnia' and m.subjects=={'BOS':'SER','HRZ':'SER','SRP':'SER'} and not m.wars
        m.execute(parse('MSGA_open_post_bosnia = yes MSGA_settle_bosnia = yes'));assert len([x for x in m.queue if x[2]=='MSGA_postbosnia.12'])==1
        return m
    def complete(m,id):
        assert id not in m.focuses
        assert all(p in m.focuses for p in graph[id])
        assert m.condition(get(focuses[id],'available'))
        m.advance(14);m.focuses.add(id);m.execute(get(focuses[id],'completion_reward'));m.advance(0)
    def purchase(m,id):
        body=decisions[id]
        assert m.condition(get(body,'visible')) and m.condition(get(body,'available')) and m.condition(get(body,'custom_cost_trigger'))
        assert m.pp>=int(get(body,'cost'))
        m.pp-=int(get(body,'cost'));m.execute(get(body,'complete_effect'));m.advance(0)

    # All six branch orders, both Srpska choices, both tank-designer modes.
    tested=[]
    for order,annex,dlc in itertools.product(itertools.permutations(range(3)),[False,True],[False,True]):
        m=settled();m.dlc=dlc;m.debt=2
        for id in opening:complete(m,id)
        assert m.buildings[1296]['infrastructure']==3 and all('MSGA_western_reconstruction' in m.modifiers[s] for s in [1296,104,851,848,849,850])
        chosen=False
        for index in order:
            for id in branches[index]:
                complete(m,id)
                if m.day>=100 and not chosen:
                    assert [(d,t) for d,t,e in m.delivered if e=='MSGA_postbosnia.12']==[(100,'SER')]
                    option=[b for k,_,b in events['MSGA_postbosnia.12'] if k=='option'][0 if annex else 1]
                    if annex:assert m.condition(get(option,'trigger'))
                    before_cores=copy.deepcopy(m.cores);before_money=m.money
                    m.execute([x for x in option if x[0] not in ('name','trigger','ai_chance')]);m.advance(0);chosen=True
                    assert m.money==before_money and m.cores==before_cores
                if id=='MSGA_arm_new_serbian_sphere':
                    for region in ['bosnian','herzegovinian']:purchase(m,'MSGA_organise_'+region+'_territorial_militias')
                if id=='MSGA_serbian_defence_network':purchase(m,'MSGA_form_srpska_territorial_defence')
        assert m.day==168 and chosen
        assert abs(m.debt-(2-.5+(1 if annex else 0)))<1e-8 and abs(m.money-9)<1e-8
        assert m.xp==25 and m.bop==.10 and m.pp==150
        assert abs(m.development-.20)<1e-8 and abs(m.stability-.15)<1e-8 and abs(m.support-.05)<1e-8
        assert m.buildings[107]['industrial_complex']==2 and m.buildings[107]['office_park']==1
        assert m.opinions[('BOS','SER')]=='MSGA_postwar_cooperation' and m.opinions[('HRZ','SER')]=='MSGA_postwar_cooperation'
        assert all('MSGA_integrated_protectorate' in m.ideas[t] for t in ['BOS','HRZ'])
        assert not any('MSGA_western_reconstruction' in value for value in m.modifiers.values())
        assert 'MSGA_postwar_income_recovery' not in {x[0] for x in m.timed}
        assert len(m.units)==6 and all(t=='SER' for t,n,p in m.units if n!='Native Srpska Guard')
        assert all(t=='SER' for t,n,p in m.units) if annex else m.subjects['SRP']=='SER'
        assert ('SER','"Srpska Teritorijalna Odbrana"') in m.templates
        before=(len(m.units),m.money,m.debt,m.development)
        for id,body in decisions.items():m.execute(get(body,'complete_effect'))
        m.execute(parse('MSGA_check_regional_power = yes MSGA_unite_srpska = yes'));m.advance(0)
        assert before==(len(m.units),m.money,m.debt,m.development)
        assert sum(e=='MSGA_postbosnia.16' for d,t,e in m.delivered)==1
        tested.append({'branches':list(order),'annex':annex,'NSB':dlc,'days':168,'Serbian_auxiliaries':5,'treasury_cost_B':1})
    # Early legacy prompt cannot annex at day 70; startup/weekly recovery works.
    legacy=settled();legacy.queue=[x for x in legacy.queue if x[2]!='MSGA_postbosnia.12']
    legacy.queue.append((70,'SER','MSGA_bosnia.11'));legacy.advance(70)
    assert not any(e=='MSGA_postbosnia.12' for d,t,e in legacy.delivered)
    legacy.advance(29);legacy.execute(parse('MSGA_check_srpska_question = yes'));legacy.advance(0)
    assert not any(e=='MSGA_postbosnia.12' for d,t,e in legacy.delivered)
    legacy.advance(1);legacy.execute(parse('MSGA_check_srpska_question = yes'));legacy.advance(0)
    assert [(d,t) for d,t,e in legacy.delivered if e=='MSGA_postbosnia.12']==[(100,'SER')]
    legacy.execute(parse('MSGA_check_srpska_question = yes'));legacy.advance(0)
    assert sum(e=='MSGA_postbosnia.12' for d,t,e in legacy.delivered)==1
    # Missing territory or insufficient treasury cannot create free divisions.
    for region,cost in [('bosnian',.25),('herzegovinian',.25),('srpska',.5)]:
        m=settled();m.flags['SER'].update(['MSGA_protectorate_militias_unlocked','MSGA_srpska_td_unlocked'])
        effect='MSGA_raise_'+region+'_militias' if region!='srpska' else 'MSGA_raise_srpska_territorial_defence'
        m.money=cost-.01;before=len(m.units);m.execute(parse(effect+' = yes'));assert len(m.units)==before
        m.money=10;m.provinces[11586]='BOS';m.execute(parse(effect+' = yes'));assert len(m.units)==before and m.money==10
    # Debt relief is bounded at zero, and a missing BOP does not create a duplicate.
    for debt in [0,.25,.5,2]:
        m=settled();m.debt=debt;m.execute(parse('MSGA_repair_postwar_economy = yes'))
        assert m.debt==max(0,debt-.5)
    m=settled();m.has_bop=False;m.execute(get(focuses['MSGA_consolidate_victory'],'completion_reward'));assert m.bop==0
    m=settled();m.buildings[1296]['infrastructure']=5;m.execute(parse('MSGA_rebuild_western_regions = yes'));assert m.buildings[1296]['infrastructure']==5
    m=settled();m.states[107]=m.controllers[107]='BOS';m.execute(parse('MSGA_consolidate_postwar_industry = yes'))
    assert sum(b.get('industrial_complex',0) for b in m.buildings.values())==2
    m=settled();m.flags['SER'].add('MSGA_completed_serbian_sphere');m.execute(parse('MSGA_check_regional_power = yes'));assert 'MSGA_regional_power_achieved' not in m.flags['SER']
    report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'version':'0.10.0','focus_ids':list(focuses),'focus_days':14,'total_focus_days':168,'scenarios':tested,'puppets':{'BOS':[104],'HRZ':[851],'SRP':[848,849,850]},'militia_battalions':3,'Serbian_control':'all five new auxiliary divisions spawn as Serbian-owned, regionally named formations','Srpska_TD':'exact Kosovo brigade template and equipment package; both DLC modes','militia_cost_per_pair':{'PP':25,'treasury_B':.25},'Srpska_TD_cost':{'PP':0,'treasury_B':.5},'Srpska_question_days':100,'legacy_70_day_migration':'passed','annexation_debt_B':1,'annexation_treasury_cost':0,'unit_and_template_preservation':'passed in model; actual engine not tested','debt_floor_and_control_funding_guards':'passed','prior_focus_trees_and_BOP':'unchanged','DDS_assets':31,'GFX_definitions':'all supplied assets used, no duplicate sprite keys','actual_game_validation':'pending user test; no engine playthrough or fresh engine log claimed'}
    report['version']=re.search(r'^version="([^"]+)"',(mod/'descriptor.mod').read_text(),re.M)[1]
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='scenarios'},indent=2))

if __name__=='__main__':main()
