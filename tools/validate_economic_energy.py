"""Validate installed economy/energy AST, native APIs, art and lifecycle cases.

Deterministic script execution is not an HOI4 engine playthrough.
"""
from pathlib import Path
from collections import Counter
from PIL import Image
import argparse, copy, hashlib, json, math, re, struct
from validate_phase1 import ROOT, parse, get, descend, unique
from validate_bosnia import TFR, GAME

START = {45, 107, 108, 1296}
ENERGY = {'power_plant':4, 'energy_farm':4, 'nuclear_reactor':2}

class DevelopmentModel:
    def __init__(self, scripts):
        self.effects = {k:v for p,a in scripts.items() if p.startswith('common/scripted_effects/') and 'economic_energy' in p for k,o,v in a}
        self.triggers = {k:v for p,a in scripts.items() if p.startswith('common/scripted_triggers/') and 'economic_energy' in p for k,o,v in a}
        self.decisions = {k:v for c,o,b in scripts['common/decisions/MSGA_economic_energy_decisions.txt'] for k,o,v in b}
        self.events = {get(v,'id'):v for k,o,v in scripts['events/MSGA_economic_energy_events.txt'] if k=='country_event'}
        self.flags = {c:{} for c in ['SER','PRC','SOV','GER','ITA','HUN','CRO']}
        self.exists = set(self.flags); self.wars=set(); self.focuses={'MSGA_serbian_recovery'}
        self.techs=set(); self.ideas={}; self.money=10.; self.pp=300.; self.day=0
        self.variables={}; self.temp={}; self.jobs={}; self.queue=[]; self.delivered=[]; self.update_calls=0
        self.owners={s:'SER' for s in START|{785,1305,104,851,848,105,106,44}}
        self.controllers=self.owners.copy(); self.slots=Counter(); self.resources={s:Counter() for s in self.owners}
        self.buildings={s:Counter(infrastructure=2) for s in self.owners}
        # Represent the approved early investments, with native Belgrade
        # values assigned (Counter.update would add to the default level).
        self.buildings[45]['infrastructure']=5;self.buildings[107]['infrastructure']=3;self.buildings[107]['power_plant']=2;self.buildings[1296]['infrastructure']=4
        self.research=[]; self.industrial=0.; self.academic=0.; self.energy_balance=-1; self.reject_buildings=False
        self.run(self.effects['MSGA_unlock_economic_energy'])

    def value(self, token, scope='SER'):
        if token.startswith('building_level@'):return self.buildings[scope][token.split('@',1)[1]]
        if token=='income_var':return self.money
        try:return float(token)
        except ValueError:return self.temp.get(token,self.variables.get(token,0))

    def condition(self, ast, scope='SER'):
        for k,o,v in ast:
            if k=='AND': ok=all(self.condition([a],scope) for a in v)
            elif k=='OR': ok=any(self.condition([a],scope) for a in v)
            elif k=='NOT': ok=not any(self.condition([a],scope) for a in v)
            elif k=='hidden_trigger':ok=self.condition(v,scope)
            elif k in self.triggers: ok=self.condition(self.triggers[k],scope)==(v=='yes')
            elif k in self.flags:ok=self.condition(v,k)
            elif k.isdigit():ok=self.condition(v,int(k))
            elif k=='tag':ok=scope==v
            elif k=='state':ok=scope==int(v)
            elif k=='has_country_flag':ok=v in self.flags[scope]
            elif k=='has_idea':ok=v in self.ideas
            elif k=='has_completed_focus':ok=v in self.focuses
            elif k=='has_tech':ok=v in self.techs
            elif k=='has_war':ok=any(scope in w for w in self.wars)==(v=='yes')
            elif k=='has_war_with':ok=frozenset((scope,v)) in self.wars
            elif k=='exists':ok=(scope in self.exists)==(v=='yes')
            elif k=='is_owned_by':ok=self.owners[scope]==v
            elif k=='is_fully_controlled_by':ok=self.controllers[scope]==v
            elif k=='check_variable':
                value=self.value(get(v,'var'),scope);target=self.value(get(v,'value'),scope)
                compare=get(v,'compare');ok={'greater_than_or_equals':value>=target,'greater_than':value>target,'equals':value==target}[compare]
            elif k=='custom_trigger_tooltip':ok=self.condition([a for a in v if a[0]!='tooltip'],scope)
            elif k=='free_building_slots':
                kind=get(v,'building');cap=ENERGY.get(kind,20)
                ok=self.slots[scope]>0 and self.buildings[scope][kind]<cap
            elif k in ['infrastructure','industrial_complex',*ENERGY]:
                assert o=='<';ok=self.buildings[scope][k]<float(v)
            elif k=='always':ok=v=='yes'
            elif k=='has_resources_in_country':
                assert get(v,'resource')=='coal';amount=next(x for x in v if x[0]=='amount');ok=self.energy_balance<float(amount[2])
            else:raise AssertionError(('Unmodeled condition',k,o,v))
            if not ok:return False
        return True

    def run(self, ast, scope='SER'):
        branch=False
        for k,o,v in ast:
            if k in ('if','else_if','else'):
                if k=='if':branch=False
                if not branch and (k=='else' or self.condition(get(v,'limit'),scope)):
                    self.run([a for a in v if a[0]!='limit'],scope);branch=True
            elif k in self.effects:self.run(self.effects[k],scope)
            elif k=='hidden_effect':self.run(v,scope)
            elif k.isdigit():self.run(v,int(k))
            elif k in self.flags:self.run(v,k)
            elif k=='set_country_flag':
                name=get(v,'flag') if isinstance(v,list) else v
                self.flags[scope][name]=self.day+int(get(v,'days')) if isinstance(v,list) else None
            elif k=='clr_country_flag':self.flags[scope].pop(v,None)
            elif k=='set_temp_variable':self.temp[get(v,'var')]=self.value(get(v,'value'),scope)
            elif k=='add_to_temp_variable':self.temp[get(v,'var')]=self.temp.get(get(v,'var'),0)+self.value(get(v,'value'),scope)
            elif k=='set_variable':self.variables[get(v,'var')]=float(get(v,'value'))
            elif k=='add_to_variable':self.variables[get(v,'var')]=self.variables.get(get(v,'var'),0)+float(get(v,'value'))
            elif k=='add_income':self.money+=self.temp['income_var_temp']
            elif k=='add_industrial_development':self.industrial+=self.temp['industrial_development_var_temp']
            elif k=='add_academic_development':self.academic+=self.temp['academic_development_var_temp']
            elif k=='add_political_power':self.pp+=float(v)
            elif k=='add_extra_state_shared_building_slots':assert scope in START;self.slots[scope]+=int(v)
            elif k=='add_resource':assert scope in START;self.resources[scope][get(v,'type')]+=int(get(v,'amount'))
            elif k=='add_building_construction':
                assert scope in START;kind=get(v,'type');amount=int(get(v,'level'));assert get(v,'instant_build')=='yes'
                cap=5 if kind=='infrastructure' else ENERGY.get(kind,20)
                assert self.buildings[scope][kind]+amount<=cap
                if kind in ENERGY:assert not any(self.buildings[scope][other] for other in ENERGY if other!=kind)
                if not self.reject_buildings:self.buildings[scope][kind]+=amount
            elif k=='add_timed_idea':
                name=get(v,'idea');assert name not in self.ideas,'Self stacking';self.ideas[name]=self.day+int(get(v,'days'))
            elif k=='add_ideas':assert v not in self.ideas;self.ideas[v]=None
            elif k=='add_tech_bonus':assert get(v,'category')=='nuclear';self.research.append(v)
            elif k=='update_power_plants_effect':self.update_calls+=1
            elif k=='country_event':self.queue.append((self.day+int(get(v,'days')),get(v,'id')))
            elif k in ['custom_effect_tooltip','log']:pass
            else:raise AssertionError(('Unmodeled effect',k,o,v))

    def start(self, stem):
        id='MSGA_'+stem;body=self.decisions[id]
        if id in self.jobs:return False
        if not self.condition(get(body,'visible')) or not self.condition(get(body,'available')):return False
        cost=int(get(body,'cost'))
        if self.pp<cost:return False
        custom=next((b for a,o,b in body if a=='custom_cost_trigger'),None)
        if custom is not None and not self.condition(custom):return False
        self.pp-=cost;self.run(get(body,'complete_effect'))
        days=next((int(b) for a,o,b in body if a=='days_remove'),None)
        if days:self.jobs[id]=self.day+days
        return True

    def advance(self, days):
        for _ in range(days):
            self.day+=1
            for table in [self.ideas,self.flags['SER']]:
                for name,date in list(table.items()):
                    if date is not None and date<=self.day:table.pop(name)
            for id,end in list(self.jobs.items()):
                body=self.decisions[id]
                if self.condition(get(body,'cancel_trigger')):
                    self.run(get(body,'cancel_effect'));self.jobs.pop(id)
                elif end<=self.day:
                    self.run(get(body,'remove_effect'));self.jobs.pop(id)
            due=[q for q in self.queue if q[0]<=self.day];self.queue=[q for q in self.queue if q[0]>self.day]
            for date,id in due:
                event=self.events[id]
                if self.condition(get(event,'trigger')):
                    self.run(get(event,'immediate'));self.delivered.append(id)

    def prerequisites(self,p):
        if p.get('requires'):self.flags['SER']['MSGA_done_'+p['requires']]=None
        if p.get('technology'):self.techs.add(p['technology'])

def main():
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,required=True);cli.add_argument('--report',type=Path,default=ROOT/'docs/economic_energy_validation.json');args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
    source=json.loads((ROOT/'docs/economic_energy_sources.json').read_text())
    scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
    ux=json.loads((ROOT/'docs/decision_ux_sources.json').read_text()) if (ROOT/'docs/decision_ux_sources.json').exists() else {'files':{}}
    for path,digest in source['baseline_sha256'].items():
        assert hashlib.sha256((mod/path).read_bytes()).hexdigest()==ux['files'].get(path,{}).get('after_sha256',digest),('Existing campaign changed',path)
    for path,digest in source['native_sources_sha256'].items():assert hashlib.sha256((TFR/path).read_bytes()).hexdigest()==digest,('Native TFR changed',path)
    all_decisions=[k for p,a in scripts.items() if p.startswith('common/decisions/') and '/categories/' not in p for c,o,b in a for k,o,v in b if isinstance(v,list)]
    all_ideas=[k for p,a in scripts.items() if p.startswith('common/ideas/') for c,o,b in a for t,o,d in b for k,o,v in d]
    all_events=[get(v,'id') for p,a in scripts.items() if p.startswith('events/') for k,o,v in a if k in ['country_event','news_event']]
    sprite_bodies=[v for p,a in scripts.items() if p.startswith('interface/') for k,o,v in descend(a) if k.lower()=='spritetype']
    all_sprites=[get(v,'name').strip('"') for v in sprite_bodies]
    for values,label in [(all_decisions,'decisions'),(all_ideas,'ideas'),(all_events,'events'),(all_sprites,'sprites')]:unique(values,label)
    sprites={get(v,'name').strip('"'):get(v,'texturefile').strip('"') for v in sprite_bodies}
    for path,record in source['assets'].items():
        data=(mod/path).read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'];assert data[84:88]==record['compression'].encode()
        with Image.open(mod/path) as im:assert list(im.size)==record['size'];im.load()
        assert list(sprites.values()).count(path)==1
    loc=(mod/'localisation/english/MSGA_economic_energy_l_english.yml').read_text(encoding='utf-8-sig')
    keys=set(re.findall(r'^ (\S+):\d',loc,re.M));assert loc.startswith('l_english:')
    for p in source['projects']+source['programmes']:
        id='MSGA_'+p['stem'];assert {id,id+'_desc'}<=keys and 'GFX_decision_'+id in sprites
    for id,title,image,body,option in source['events']:
        assert {id+'.t',id+'.d',id+'.a'}<=keys and sprites['GFX_MSGA_event_'+image].endswith(image+'.dds');assert body.count('\n\n')>=1
    native_generic=parse((TFR/'common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt').read_text())
    for n,var in [('add_income','income'),('add_industrial_development','industrial_development'),('add_academic_development','academic_development')]:
        assert ('add_to_variable','=',parse(f'var = {var}_var value = {var}_var_temp')) in get(native_generic,n)
    native_mods={k for k,o,v in parse((TFR/'common/modifier_definitions/00_TFR_economic_modifiers_definition.txt').read_text())}
    known={kind:set(re.findall(r'^## (\w+)',(GAME/'documentation'/f'{kind}_documentation.md').read_text(),re.M)) for kind in ['effects','triggers','modifiers']}
    # Building modifiers are generated from the installed native building IDs.
    buildings={k for k,o,v in get(parse((TFR/'common/buildings/TFR_buildings.txt').read_text()),'buildings')}
    building_mods={'production_speed_'+b+'_factor' for b in buildings}
    idea_bodies=get(get(scripts['common/ideas/MSGA_economic_energy_ideas.txt'],'ideas'),'country')
    for id,o,v in idea_bodies:
        assert get(v,'traits')==[('ZZZ_blank_idea_trait',None,None)]
        for k,o,value in get(v,'modifier'):assert k in known['modifiers']|native_mods|building_mods,('Invalid modifier',k)
    declarations={k for p,a in scripts.items() if p.startswith('common/scripted_triggers/') for k,o,v in a}
    conditions_allowed=known['triggers']|declarations|{'state','infrastructure','industrial_complex',*ENERGY}
    def conditions(a):
        for k,o,v in a:
            if k in ['AND','OR','NOT','hidden_trigger','SER','PRC','SOV','GER','ITA','HUN'] or k.isdigit():conditions(v)
            elif k=='custom_trigger_tooltip':conditions([x for x in v if x[0]!='tooltip'])
            else:assert k in conditions_allowed,('Invalid trigger',k)
    for p,a in scripts.items():
        if 'economic_energy' not in p:continue
        if p.startswith('common/scripted_triggers/'):
            for k,o,v in a:conditions(v)
        for k,o,v in descend(a):
            if k in ['limit','available','visible','trigger','cancel_trigger','allowed','allowed_civil_war']:conditions(v)
    new_effects=scripts['common/scripted_effects/MSGA_economic_energy_effects.txt']
    assert not ({k for k,o,v in descend(new_effects)} & {'add_income_with_inflation','add_debt','transfer_state','annex_country','load_focus_tree','declare_war_on','set_autonomy','add_core_of'})
    m=DevelopmentModel(scripts);cases=[]
    for s in START|{785,1305,104,851,848,105,106,44}:
        assert m.condition(m.triggers['MSGA_development_starting_serbia_state'],s)==(s in START)
    m.focuses.clear();assert m.condition(m.triggers['MSGA_development_unlocked']);m.flags['SER'].clear();assert not m.condition(m.triggers['MSGA_development_unlocked'])
    for p in source['programmes']:
        m=DevelopmentModel(scripts);m.prerequisites(p);cash=m.money;pp=m.pp;assert m.start(p['stem'])
        assert math.isclose(m.money,cash-p['cash']) and m.pp==pp-p['pp'];assert not m.start(p['stem'])
        id='MSGA_'+p['stem'];m.advance(179);assert id in m.ideas and not m.start(p['stem'])
        m.advance(1);assert id not in m.ideas and not m.start(p['stem'])
        m.advance(69);assert not m.start(p['stem']);m.advance(1);assert m.start(p['stem'])
        poor=DevelopmentModel(scripts);poor.prerequisites(p);poor.money=max(0,p['cash']-.001);poor.pp=49 if p['pp'] else 300
        assert not poor.start(p['stem']);cases.append('Repeatable: '+p['stem'])
    building_projects=[]
    for p in source['projects']:
        stem=p['stem'];pending='MSGA_pending_'+stem;done='MSGA_done_'+stem
        decision=get(get(scripts['common/decisions/MSGA_economic_energy_decisions.txt'], 'MSGA_serbian_energy_development' if p['energy'] else 'MSGA_serbian_economic_cooperation'),'MSGA_'+stem)
        start=get(get(decision,'complete_effect'),'hidden_effect')
        assert ('set_country_flag','=',pending) in start
        if p['state']:assert ('set_country_flag','=','MSGA_development_state_'+str(p['state'])+'_busy') in start
        assert not any(k=='set_country_flag' and isinstance(v,list) for k,o,v in descend(start)),stem
        finish=get(new_effects,'MSGA_finish_'+stem);success=get(finish,'if');safety='MSGA_safe_finish_'+stem
        assert (safety,'=','yes') in get(success,'limit')
        assert not any(k.startswith('MSGA_eligible_') for k,o,v in descend(finish)),stem
        assert not any(k in ['has_tech','has_country_flag','check_variable','has_war'] for k,o,v in descend(get(scripts['common/scripted_triggers/MSGA_economic_energy_triggers.txt'],safety))),stem
        for release in [pending]+(['MSGA_development_state_'+str(p['state'])+'_busy'] if p['state'] else []):
            assert ('clr_country_flag','=',release) in descend(success)
            assert ('clr_country_flag','=',release) in descend(get(new_effects,'MSGA_cancel_'+stem))
        grants=[i for i,(k,o,v) in enumerate(success) if k==str(p['state']) and any(x[0]=='add_building_construction' for x in descend(v))]
        if grants:
            building_projects.append('MSGA_'+stem)
            delivery=next(v for k,o,v in success if k=='if')
            assert ('has_country_flag','=','MSGA_building_delivered_'+stem) in get(delivery,'limit')
            assert ('set_country_flag','=',done) in delivery
            assert grants[-1]<success.index(('if','=',delivery)),stem
            assert any(k=='log' and 'completion fired' in v for k,o,v in finish),stem
            assert any(k=='log' and 'verified' in v for k,o,v in descend(success)),stem
            rejected=DevelopmentModel(scripts);rejected.prerequisites(p)
            # Exercise the physical construction branch, not the valid
            # maximum-infrastructure slot fallback.
            if p['reward'] in ('mining','grid','hydro'):rejected.buildings[p['state']]['infrastructure']=4
            rejected.reject_buildings=True;assert rejected.start(stem);rejected.advance(p['days'])
            assert math.isclose(rejected.money,10) and rejected.pp==300 and done not in rejected.flags['SER'],(stem,rejected.money,rejected.pp,rejected.flags['SER'])
            assert pending not in rejected.flags['SER'] and rejected.slots[p['state']]==0
            assert rejected.industrial==0 and rejected.academic==0 and not any(rejected.resources[p['state']].values())
            assert rejected.start(stem);cases.append('Rejected native construction refunds without completion: '+stem)
        m=DevelopmentModel(scripts);m.prerequisites(p);cash=m.money;pp=m.pp;before=copy.deepcopy(m.buildings)
        assert m.start(p['stem']);assert math.isclose(m.money,cash-p['cash']) and m.pp==pp-p['pp']
        assert not m.start(p['stem']);m.advance(p['days']-1);assert 'MSGA_done_'+p['stem'] not in m.flags['SER']
        m.advance(1);assert 'MSGA_done_'+p['stem'] in m.flags['SER'] and not m.start(p['stem'])
        if p['reward'] in ENERGY:assert m.buildings[p['state']][p['reward']]==before[p['state']][p['reward']]+1 and m.update_calls==1
        if p['reward'] in ['mining','jadar']:assert m.resources[p['state']]['steel']==3 and m.resources[p['state']]['tungsten']==2
        if p['state']:
            for mode in ['owner','controller']:
                lost=DevelopmentModel(scripts);lost.prerequisites(p);assert lost.start(p['stem']);original=copy.deepcopy(lost.buildings)
                (lost.owners if mode=='owner' else lost.controllers)[p['state']]='CRO';lost.advance(1)
                assert math.isclose(lost.money,10) and lost.pp==300 and lost.buildings==original
                assert 'MSGA_done_'+p['stem'] not in lost.flags['SER'] and not lost.jobs
                (lost.owners if mode=='owner' else lost.controllers)[p['state']]='SER';assert lost.start(p['stem'])
        for changed in ['poor','chain','tech']:
            bad=DevelopmentModel(scripts);bad.prerequisites(p)
            if changed=='poor':bad.money=p['cash']-.001
            elif changed=='chain' and p['requires']:bad.flags['SER'].pop('MSGA_done_'+p['requires'])
            elif changed=='tech' and p['technology']:bad.techs.clear()
            else:continue
            assert not bad.start(p['stem'])
        cases.append('One-time/cancellation: '+p['stem'])
        # Delay completion beyond the old one-day grace period. This tests
        # the scripts' resilience, not HOI4's application of a building.
        delayed=DevelopmentModel(scripts);delayed.prerequisites(p);assert delayed.start(stem)
        delayed.jobs['MSGA_'+stem]+=7;delayed.techs.clear()
        if p['requires']:delayed.flags['SER'].pop('MSGA_done_'+p['requires'],None)
        delayed.advance(p['days']+6);assert pending in delayed.flags['SER'] and delayed.flags['SER'][pending] is None
        delayed.advance(1);assert done in delayed.flags['SER'] and pending not in delayed.flags['SER']
        cases.append('Delayed callback, no start-only recheck: '+stem)
    # Native state exclusivity, reservations, first and second building ceilings.
    for first,blocked in [('expand_kostolac_energy_complex','develop_bor_renewable_complex'),('develop_bor_renewable_complex','expand_kostolac_energy_complex')]:
        m=DevelopmentModel(scripts);assert m.start(first);assert not m.start(blocked);m.advance(next(p['days'] for p in source['projects'] if p['stem']==first));assert not m.start(blocked)
    for first,second,building,state in [('develop_bor_renewable_complex','expand_bor_renewable_complex','energy_farm',108),('first_serbian_nuclear_power_plant','expand_serbian_nuclear_programme','nuclear_reactor',45)]:
        m=DevelopmentModel(scripts);levels=[m.buildings[state][building]]
        for stem in [first,second]:
            p=next(p for p in source['projects'] if p['stem']==stem);m.prerequisites(p);assert m.start(stem)
            m.advance(p['days']-1);assert m.buildings[state][building]==levels[-1]
            m.advance(1);levels.append(m.buildings[state][building])
        assert levels==[0,1,2] and not m.start(first) and not m.start(second)
        cases.append('Timed building counter sequence 0 -> 1 -> 2: '+building)
    for p in source['projects']:
        if p['reward'] in ('mining','grid','hydro'):
            m=DevelopmentModel(scripts);m.buildings[p['state']]['infrastructure']=5
            assert m.start(p['stem']);m.advance(p['days'])
            assert m.buildings[p['state']]['infrastructure']==5 and m.slots[p['state']]==1
            assert 'MSGA_done_'+p['stem'] in m.flags['SER'];cases.append('Capped infrastructure slot fallback: '+p['stem'])
    grants=Counter(get(v,'type') for k,o,v in descend(new_effects) if k=='add_building_construction')
    assert all(grants[b]==2 for b in ENERGY),grants
    # Eight separate queued milestones are idempotent, with rewards only in decisions.
    m=DevelopmentModel(scripts)
    for id,title,image,body,option in source['events']:
        effect='MSGA_milestone_'+id.replace('MSGA_','').replace('.','_')
        m.run(m.effects[effect]);m.run(m.effects[effect])
    snapshot=(m.money,m.pp,copy.deepcopy(m.buildings));m.advance(1)
    assert Counter(m.delivered)==Counter(id for id,*_ in source['events']);assert snapshot==(m.money,m.pp,m.buildings)
    for id,title,image,body,option in source['events']:m.run(m.effects['MSGA_milestone_'+id.replace('MSGA_','').replace('.','_')])
    m.advance(2);assert len(m.delivered)==8
    m=DevelopmentModel(scripts)
    for stem in ['develop_jadar_mining_project','serbian_mineral_processing_expansion','central_serbian_industrial_park']:
        p=next(p for p in source['projects'] if p['stem']==stem);assert m.start(stem);m.advance(p['days'])
    m.advance(1);assert Counter(m.delivered)['MSGA_econ.4']==1 and m.variables['MSGA_permanent_economic_projects']==3
    report={'validation':'passed','validated_mod_root':str(mod),'categories':['MSGA_serbian_economic_cooperation','MSGA_serbian_energy_development'],'projects':19,'repeatable_programmes':18,'milestones':8,'provided_art_DDS':len(source['assets']),'repeatable_timing_days':[180,70,250],'starting_states':sorted(START),'mining_rewards_each':{'steel':3,'tungsten':2},'maximum_scripted_energy_buildings':{b:grants[b] for b in ENERGY},'existing_campaign_hashes_preserved':len(set(source['baseline_sha256'])-ux['files'].keys()),'approved_presentation_and_category_cleanup':sorted(set(source['baseline_sha256'])&ux['files'].keys()),'modeled_cases':cases,'native_exclusivity':'Kostolac/Bor alternatives tested in both orders','cancellation':'Ownership/control loss or rejected native construction returns costs without rewards; permits retry','engine_acceptance':'NOT RUN: user reserved the game test; no game window or save was touched.'}
    report.update(static_model_validation='passed',actual_engine_validation='NOT RUN: user performs the HOI4 test; building counters model script commands only.',project_lifecycle='Persistent pending/busy flags; explicit release/refund. Native before/after building counters must increase by exactly 1 before secondary rewards and completion; rejected construction rolls back its introduced shared slot.',delayed_callback_cases=19,building_projects_checked_in_model=building_projects,nuclear_model_levels=[0,1,2],decision_icon_composition='Tight foreground crop, aspect preserved, centred within a 3px dark frame on 52x45 DXT5; categories/spirits/events unchanged.')
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='modeled_cases'},indent=2))

if __name__=='__main__':main()
