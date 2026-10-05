"""Focused installed-content checks for the Bosnia chapter; no combat simulation."""
from pathlib import Path
import argparse,hashlib,json,re
from collections import Counter
from PIL import Image
from validate_phase1 import parse,get,descend,unique,ROOT
from validate_kosovo import CampaignModel

TFR=Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV')

def strip_guards(ast):
    result=[]
    for key,op,value in ast:
        if key=='MSGA_native_balkan_story_allowed':continue
        if key=='if' and isinstance(value,list) and next((v for k,_,v in value if k=='limit'),None)==parse('MSGA_native_balkan_story_allowed = yes'):
            result.extend(strip_guards([x for x in value if x[0]!='limit']));continue
        if isinstance(value,list):value=strip_guards(value)
        if key=='trigger' and value==[]:continue
        result.append((key,op,value))
    return result

class BosniaModel(CampaignModel):
    """Read actual reward/event ASTs; model only timing, ownership and guard effects."""
    def __init__(self,scripts,mod):
        super().__init__(scripts)
        self.mod=mod;self.scripts=scripts;self.day=0;self.queue=[];self.delivered=[];self.military=0;self.timed=[];self.stock=Counter();self.units=[];self.progress=0
        self.event_ast={get(v,'id'):v for p,ast in scripts.items() if p.startswith('events/MSGA_') for k,_,v in ast if k=='country_event'}
        for c in ['BOS','SRP','SOV','PRC','ARM']:
            self.flags[c]=set();self.ideas[c]=set();self.factions[c]=None
        self.exists.update(['BOS','SOV','PRC','ARM']);self.exists.discard('SRP')
        for s in [45,107,108,1296,785,1305]:self.states[s]=self.controllers[s]='SER';self.cores[s]={'SER'}
        for s in [848,849,850]:self.states[s]=self.controllers[s]='BOS';self.cores[s]={'BOS','SRP'}
        self.provinces={11586:'SER',3617:'SER',11887:'SER',6998:'SER',14402:'SER',14400:'SER'}
        self.flags['SER'].add('MSGA_campaign_active')

    def condition(self,ast,scope='SER'):
        for k,op,v in ast:
            if k in ('AND','OR','NOT'):
                parts=[self.condition([x],scope) for x in v]
                ok=all(parts) if k=='AND' else any(parts) if k=='OR' else not any(parts)
            elif k in self.flags:ok=self.condition(v,k)
            elif k.isdigit():ok=self.condition(v,int(k))
            elif k=='MSGA_native_balkan_story_allowed':ok='MSGA_campaign_active' not in self.flags['SER']
            elif k=='has_war':ok=any(scope in w for w in self.wars)==(v=='yes')
            elif k=='is_subject':ok=v=='no'
            elif k=='has_completed_focus':ok=v in self.focuses
            elif k=='surrender_progress':ok=self.progress>float(v)
            elif k=='controls_province':ok=self.provinces.get(int(v))==scope
            else:ok=super().condition([(k,op,v)],scope)
            if not ok:return False
        return True

    def execute(self,ast,scope='SER'):
        branch=False
        for k,op,v in ast:
            if k in ('if','else_if','else'):
                if k=='if':branch=False
                if not branch and (k=='else' or self.condition(get(v,'limit'),scope)):
                    self.execute([x for x in v if x[0]!='limit'],scope);branch=True
                continue
            if k in self.flags:self.execute(v,k)
            elif k.isdigit():self.execute(v,int(k))
            elif k in self.effects:self.execute(self.effects[k],scope)
            elif k=='country_event':self.queue.append((self.day+int(next((b for a,_,b in v if a=='days'),'0')),scope,get(v,'id')))
            elif k=='release':
                assert scope=='BOS' and v=='SRP';self.exists.add(v)
                for s in [848,849,850]:self.states[s]=self.controllers[s]='SRP'
            elif k=='delete_unit':self.units=[x for x in self.units if x[0]!=scope]
            elif k=='load_oob':
                oob=parse((self.mod/'history/units'/f'{v.strip(chr(34))}.txt').read_text(encoding='utf-8-sig'))
                for name,_,body in descend(oob):
                    if name=='division':self.units.append((scope,get(body,'name'),int(get(body,'location'))))
                self.loaded_oobs.append(v)
            elif k=='add_to_war':
                assert frozenset(('SRP','BOS')) in self.wars
                assert get(v,'targeted_alliance')=='SRP' and get(v,'enemy')=='BOS'
                self.wars.add(frozenset(('SER','BOS')));self.trace.append(('join','SER','SRP','BOS'))
            elif k=='add_military_development':self.military+=self.temp
            elif k=='add_timed_idea':self.timed.append((get(v,'idea'),int(get(v,'days'))))
            elif k=='add_equipment_to_stockpile':self.stock[get(v,'type')]+=int(get(v,'amount'))
            elif k=='hidden_effect':self.execute(v,scope)
            elif k in ('set_politics','promote_character','custom_effect_tooltip','remove_mission'):pass
            else:super().execute([(k,op,v)],scope)

    def advance(self,days):
        end=self.day+days
        while self.queue and min(self.queue)[0]<=end:
            item=min(self.queue);self.queue.remove(item);self.day,scope,id=item;self.delivered.append(item)
            body=self.event_ast[id]
            self.execute(next((v for k,_,v in body if k=='immediate'),[]),scope)
        self.day=end

def main():
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,default=ROOT/'make_serbia_great_again');cli.add_argument('--report',type=Path,default=ROOT/'docs/bosnia_validation.json');args=cli.parse_args();mod=args.mod_root.resolve()
    scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
    sources=json.loads((ROOT/'docs/bosnia_sources.json').read_text())
    # Native compatibility copies must differ only by the documented gates/OOB.
    for path,record in sources['native_guard_overrides'].items():
        native=(TFR/path).read_bytes();assert hashlib.sha256(native).hexdigest()==record['upstream_sha256'],f'TFR changed; rebase guard override: {path}'
        before=parse(native.decode('utf-8-sig'));after=scripts[path]
        if record.get('oob_only'):
            assert [(k,o,'"SER_2000"' if k=='oob' else v) for k,o,v in after]==before
        else:assert strip_guards(after)==strip_guards(before),f'Unrelated native script changed: {path}'
    native_events={get(v,'id'):v for k,_,v in scripts['events/TFR_events_SER.txt'] if k=='country_event'}
    for id in sources['native_guard_overrides']['events/TFR_events_SER.txt']['extra']['gated_events']:
        assert ('MSGA_native_balkan_story_allowed','=','yes') in get(native_events[id],'trigger')
    for winner,loser in sources['native_guard_overrides']['common/on_actions/TFR_on_actions_ZZZ_peace.txt']['extra']['gated_winner_loser_pairs']:
        branches=[v for k,_,v in descend(scripts['common/on_actions/TFR_on_actions_ZZZ_peace.txt']) if k=='if' and isinstance(v,list) and any(a=='limit' for a,_,_ in v)]
        limits=[get(v,'limit') for v in branches]
        match=[lim for lim in limits if next((get(v,'original_tag') for k,_,v in lim if k=='FROM' and any(a=='original_tag' for a,_,_ in v)),None)==winner and next((get(v,'original_tag') for k,_,v in lim if k=='ROOT' and any(a=='original_tag' for a,_,_ in v)),None)==loser]
        assert len(match)==1 and ('MSGA_native_balkan_story_allowed','=','yes') in match[0]
    focuses={get(v,'id'):v for k,_,v in scripts['common/national_focus/MSGA_SER_bosnian_crisis.txt'][0][2] if k=='focus'}
    assert len(focuses)==13;positions=[(get(v,'x'),get(v,'y')) for v in focuses.values()];unique(positions,'Focus positions')
    ids=[get(v,'id') for ast in scripts.values() for k,_,v in descend(ast) if k=='focus' and isinstance(v,list)];unique(ids,'Focus IDs')
    event_ids=[get(v,'id') for p,ast in scripts.items() if p.startswith('events/') for k,_,v in ast if k in ('country_event','news_event')];unique(event_ids,'Event IDs')
    decisions=[(k,v) for _,_,entries in scripts['common/decisions/MSGA_bosnia_decisions.txt'] for k,_,v in entries];unique([k for k,_ in decisions],'Bosnia decision IDs')
    graph={id:[get(v,'focus') for k,_,v in b if k=='prerequisite'] for id,b in focuses.items()}
    def visit(id,trail=()):
        assert id not in trail
        for parent in graph[id]:assert parent in focuses;visit(parent,trail+(id,))
    for id in focuses:visit(id)
    assert set(focuses)-{x for ps in graph.values() for x in ps}=={'MSGA_watch_the_conflict'}
    assert int(get(focuses['MSGA_seed_the_rebellion_in_bosnia'],'cost'))*7==42
    assert int(get(focuses['MSGA_watch_the_conflict'],'cost'))*7==70
    assert all(get(v,'cost')=='5' for id,v in focuses.items() if id not in ['MSGA_seed_the_rebellion_in_bosnia','MSGA_watch_the_conflict'])
    assert graph['MSGA_seed_the_rebellion_in_bosnia']==['MSGA_prepare_the_nation_for_war','MSGA_prepare_for_the_unthinkable']
    assert graph['MSGA_prepare_for_the_unthinkable']==['MSGA_buy_equipment_serbian_air_force','MSGA_spend_money_command_structure','MSGA_prepare_logistics_network']
    assert get(focuses['MSGA_prepare_for_the_unthinkable'],'available')==parse('has_country_flag = MSGA_air_procurement_done')
    locale='\n'.join(p.read_text(encoding='utf-8-sig') for p in (mod/'localisation/english').glob('*.yml'));keys=re.findall(r'^ ([^:]+):',locale,re.M);unique(keys,'Localisation keys')
    for id in focuses:assert id in keys and id+'_desc' in keys
    for id,_ in decisions:assert id in keys and id+'_desc' in keys
    assert 'Serbia might need to intervene.' in locale
    assert 'regime\'s arguments' in locale
    sprites={get(v,'name').strip('"'):v for p,ast in scripts.items() if p.startswith('interface/') for k,_,v in descend(ast) if k=='SpriteType'}
    for id,body in focuses.items():assert get(body,'icon') in sprites and get(body,'icon')+'_shine' in sprites
    for path,source in sources['assets'].items():
        p=mod/path;assert p.read_bytes()==(ROOT/source).read_bytes();im=Image.open(p).convert('RGBA');assert im.getchannel('A').getextrema()[1]>0
        expected=(95,85) if '/goals/' in path else (60,68) if '/ideas/' in path else (474,156) if '/event_pictures/' in path else (52,40) if p.stem=='MSGA_territorial_defence' else (36,36)
        assert im.size==expected
    state_data={}
    for p in (TFR/'history/states').glob('*.txt'):
        body=get(parse(p.read_text(encoding='utf-8-sig',errors='replace')),'state');id=int(get(body,'id'));state_data[id]=body
    for state in [848,849,850]:assert ('add_core_of','=','SRP') in get(state_data[state],'history') and ('owner','=','BOS') in get(state_data[state],'history')
    for path,ast in scripts.items():
        if not path.startswith('history/units/MSGA_'):continue
        for k,_,v in descend(ast):
            if k=='division':assert int(get(v,'location')) in {int(n) for s in state_data.values() for n,_,_ in get(s,'provinces')}
    for file,name in [('MSGA_SER_territorial_template','Territorial Defence Militia'),('MSGA_SRP_guard','Srpska Guard')]:
        template=get(scripts[f'history/units/{file}.txt'],'division_template');assert get(template,'name')==f'"{name}"'
        assert [k for k,_,_ in get(template,'regiments')]==['militia']*3
        assert not any(k in ('support','is_locked','locked','division_cap') for k,_,_ in template)
    srp=[v for k,_,v in descend(scripts['history/units/MSGA_SRP_guard.txt']) if k=='division'];assert len(srp)==3
    assert [int(get(v,'location')) for v in srp]==[6983,11741,11574]
    for state in [107,45,108,1296,785,1305]:
        unit=get(get(scripts[f'history/units/MSGA_SER_territorial_{state}.txt'],'units'),'division');prov=int(get(unit,'location'));assert str(prov) in {k for k,_,_ in get(state_data[state],'provinces')}
        assert ('owner','=','HUN') not in get(state_data[state],'history')
    assert 'MSGA_form_territorial_107' not in [k for k,_ in decisions]
    effects=scripts['common/scripted_effects/MSGA_bosnia_effects.txt']
    procurement={get(v,'id'):v for k,_,v in scripts['events/MSGA_bosnia_events.txt'] if k=='country_event'}
    for event in ['MSGA_bosnia.4','MSGA_bosnia.5']:
        fallback=[v for k,_,v in procurement[event] if k=='option' and get(v,'name')==event+'.c'][0]
        assert float(get(get(fallback,'ai_chance'),'factor'))>0, 'Unfunded AI must be able to defer procurement'
    assert not any(k in ('annex_country','puppet','transfer_state','add_core_of','create_wargoal','white_peace') for k,_,_ in descend(effects))
    calls=[v for k,_,v in descend(effects) if k=='declare_war_on'];assert len(calls)==1 and get(calls[0],'target')=='SRP'
    assert ('release','=','SRP') in descend(get(effects,'MSGA_release_srpska'))
    assert ('promote_character','=','SRP_milorad_dodik_char') in descend(get(effects,'MSGA_release_srpska'))
    assert ('country_event','=',parse('id = MSGA_bosnia.7 days = 15')) in descend(get(effects,'MSGA_release_srpska'))
    # Names/designs are verified against TFR source, including DLC designer aliases.
    def variants(tag):
        p=next((TFR/'history/countries').glob(tag+' - *'));return {(get(v,'name').strip('"'),get(v,'type')) for k,_,v in descend(parse(p.read_text(encoding='utf-8-sig'))) if k=='create_equipment_variant'}
    assert ('Su-30','small_plane_airframe_1') in variants('ARM')
    assert ('Su-24','small_plane_cas_airframe_0') in variants('SOV')
    assert ('Shenyang J-16','small_plane_airframe_1') in variants('PRC')
    native_air=(TFR/'localisation/english/replace/TFR_replace_equip_air_l_english.yml').read_text(encoding='utf-8-sig')
    assert 'SOV_attack_helicopter_equipment_1: "Mi-24' in native_air and 'PRC_attack_helicopter_equipment_1: "Changhe Z-10"' in native_air
    ideas=get(get(scripts['common/ideas/MSGA_bosnia_ideas.txt'],'ideas'),'country');rearm=get(ideas,'MSGA_serbian_rearmament_program')
    bonus=get(rearm,'equipment_bonus');assert len(bonus)==4 and all(get(v,'build_cost_ic')=='-0.25' for _,_,v in bonus)
    equipment_files={p.name:p for p in (GAME/'common/units/equipment').glob('*.txt')}
    equipment_files.update({p.name:p for p in (TFR/'common/units/equipment').glob('*.txt')})
    equipment_defs={k:v for p in equipment_files.values() for key,_,body in parse(p.read_text(encoding='utf-8-sig',errors='replace')) if key=='equipments' for k,_,v in body}
    for kind,_,_ in bonus:assert get(equipment_defs[kind],'is_archetype')=='yes',f'Production bonus requires a real archetype: {kind}'
    assert get(equipment_defs['modern_tank_equipment_1'],'archetype')=='modern_tank_chassis'
    bos_oob=parse((TFR/'history/units/BOS_2020.txt').read_text(encoding='utf-8-sig'))
    assert len([v for k,_,v in descend(bos_oob) if k=='division'])==4
    assert {'mechanized','light_mechanized','modern_armor','artillery_brigade'} <= {k for k,_,_ in descend(bos_oob)}
    assert get(rearm,'modifier')==parse('expense_growth_factor = 0.15 military_factory_upkeep_factor = 0.05')
    # Inspect loaded defines/static modifiers rather than assuming vanilla values.
    defines=(GAME/'common/defines/00_defines.lua').read_text();base=float(re.search(r'BASE_SURRENDER_LIMIT\s*=\s*([\d.]+)',defines)[1]);war=float(re.search(r'BASE_STABILITY_WAR_FACTOR\s*=\s*(-?[\d.]+)',defines)[1])
    native_static=parse((TFR/'common/modifiers/00_TFR_modifiers_ZZZ_static.txt').read_text(encoding='utf-8-sig'));low=float(get(get(native_static,'war_support_bad_modifier'),'surrender_limit'))
    limits=[]
    for id in ['MSGA_SRP_last_stand','MSGA_KOS_last_stand']:
        modifier=get(get(ideas,id),'modifier');bonus=float(get(modifier,'surrender_limit'));maximum=1-float(get(modifier,'max_surrender_limit_offset'))
        limits.extend(min(maximum,base+bonus+low*(1-support)) for support in [0,.25,.5,.75,1])
    assert all(abs(x-.99)<1e-8 for x in limits) and max(limits)<1
    prepared=get(get(ideas,'MSGA_prepared_for_war'),'modifier');assert abs((war+float(get(prepared,'war_stability_factor')))/war-.7)<1e-8
    # Parse and execute actual code for one-time payments/spawns, both supplier
    # paths/DLC modes, the 15-day scheduler and the guarded intervention.
    model=BosniaModel(scripts,mod)
    assert not model.condition(parse('MSGA_native_balkan_story_allowed = yes'))
    model.flags['SER'].discard('MSGA_campaign_active');assert model.condition(parse('MSGA_native_balkan_story_allowed = yes'));model.flags['SER'].add('MSGA_campaign_active')
    model.execute(get(focuses['MSGA_establish_territorial_defence'],'completion_reward'));model.execute(parse('MSGA_establish_territorial_defence = yes'));assert len(model.units)==1 and model.units[0][2]==11586
    for id,body in decisions:
        if not id.startswith('MSGA_form_territorial_'):continue
        assert get(body,'cost')=='0' and get(body,'days_remove')=='14' and get(body,'fire_only_once')=='yes'
        assert get(body,'custom_cost_trigger')==parse('check_variable = { var = income_var value = 0.5 compare = greater_than_or_equals }')
        assert model.condition(get(body,'visible'));before=model.money
        model.execute(get(body,'complete_effect'));assert model.money==before-.5 and not model.condition(get(body,'visible'))
        count=len(model.units);model.execute(get(body,'remove_effect'));assert len(model.units)==count+1
        model.execute(get(body,'remove_effect'));assert len(model.units)==count+1
    # Losing control before delivery refunds once and spawns nothing.
    lost=BosniaModel(scripts,mod);body=dict(decisions)['MSGA_form_territorial_45'];lost.execute(get(body,'complete_effect'));lost.controllers[45]='HUN';lost.execute(get(body,'remove_effect'));lost.execute(get(body,'remove_effect'));assert lost.money==10 and not lost.units
    for supplier,cost,total in [('russian',15,125),('chinese',10,70)]:
        for dlc in [False,True]:
            buyer=BosniaModel(scripts,mod);buyer.dlc=dlc;buyer.flags['SER'].add('MSGA_air_procurement_open');buyer.money=cost-1
            buyer.execute(parse(f'MSGA_buy_{supplier}_air_package = yes'));assert not buyer.stock and buyer.money==cost-1
            buyer.money=cost;buyer.execute(parse(f'MSGA_buy_{supplier}_air_package = yes'));assert buyer.money==0 and sum(buyer.stock.values())==total
            if supplier=='russian':assert sorted(buyer.stock.values())==[25,50,50]
            else:assert sorted(buyer.stock.values())==[30,40]
            buyer.execute(parse(f'MSGA_buy_{supplier}_air_package = yes'));assert sum(buyer.stock.values())==total and buyer.money==0
    total=BosniaModel(scripts,mod);total.flags['SER'].add('MSGA_air_procurement_done')
    for id,b in focuses.items():
        if any(k=='add_military_development' for k,_,_ in get(b,'completion_reward')):total.execute(get(b,'completion_reward'))
    assert total.military==60 and ('MSGA_serbian_rearmament_program',200) in total.timed
    assert total.stock['train_equipment_1']==15 and total.stock['motorized_equipment_1']==150
    # No release before preparations. Deterministic declaration by BOS after 15 days.
    war_model=BosniaModel(scripts,mod);war_model.execute(parse('MSGA_release_srpska = yes'));assert 'SRP' not in war_model.exists
    war_model.flags['SER'].update(['MSGA_bosnia_propaganda_prepared','MSGA_bosnia_military_prepared']);war_model.execute(parse('MSGA_release_srpska = yes'))
    assert 'SRP' in war_model.exists and len(war_model.units)==3 and all(war_model.states[s]=='SRP' for s in [848,849,850])
    war_model.execute(parse('MSGA_release_srpska = yes'));assert len(war_model.units)==3
    war_model.advance(14);assert not war_model.wars
    war_model.advance(1);assert war_model.wars=={frozenset(('BOS','SRP'))} and ('declare','BOS','SRP') in war_model.trace
    war_model.progress=.10;war_model.execute(parse('MSGA_check_bosnian_intervention = yes'));assert 'MSGA_bosnia_intervention_fired' not in war_model.flags['SER']
    war_model.execute(get(focuses['MSGA_watch_the_conflict'],'completion_reward'));war_model.advance(0);assert 'MSGA_bosnia_intervention_fired' in war_model.flags['SER']
    war_model.execute(parse('MSGA_check_bosnian_intervention = yes'));war_model.advance(2)
    assert sum(id=='MSGA_bosnia.9' for _,_,id in war_model.delivered)==1
    war_model.execute(parse('MSGA_join_srpska_war = yes'));war_model.execute(parse('MSGA_join_srpska_war = yes'))
    assert war_model.trace.count(('join','SER','SRP','BOS'))==1 and 'SRP' in war_model.exists
    assert war_model.wars=={frozenset(('BOS','SRP')),frozenset(('BOS','SER'))}
    war_model.wars.clear();war_model.execute(parse('MSGA_cleanup_bosnia_war_modifiers = yes'));assert 'MSGA_SRP_last_stand' not in war_model.ideas['SRP']
    wait=BosniaModel(scripts,mod);wait.exists.add('SRP');wait.flags['SER'].update(['MSGA_bosnia_story_active','MSGA_watched_bosnian_conflict']);wait.wars.add(frozenset(('BOS','SRP')))
    for progress in [0,.01,.02]:wait.progress=progress;wait.execute(parse('MSGA_check_bosnian_intervention = yes'));assert not wait.queue
    wait.execute(parse('MSGA_schedule_bosnia_observer = yes'));wait.progress=.03;wait.advance(1);assert any(id=='MSGA_bosnia.9' for _,_,id in wait.delivered)
    # Earlier Kosovo cleanup removes its new Last Stand, and earlier rewards stay covered by prior validators.
    kos=CampaignModel(scripts);kos.execute(parse('MSGA_start_kosovo_war = yes'));assert 'MSGA_KOS_last_stand' in kos.ideas['KOS'];kos.execute(parse('MSGA_cleanup_kosovo_campaign = yes'));assert 'MSGA_KOS_last_stand' not in kos.ideas['KOS']
    report={'static_validation':'passed','validated_mod_root':str(mod),'version':'0.8.0','bosnia_focuses':13,'total_focuses':len(ids),'seed_days':42,'watch_days':70,'release_to_BOS_declaration_days':15,'Srpska_native_states':[848,849,850],'native_leader':'SRP_milorad_dodik_char','Srpska_starting_divisions':3,'militia_battalions_per_template':3,'territorial_decision_states':[45,108,1296,785,1305],'Belgrade_province':11586,'territorial_cost_B':.5,'territorial_days':14,'military_development_total':60,'rearmament_days':200,'Russian_package':{'cost_B':15,'Su30':50,'Su24':25,'Mi24':50},'Chinese_package':{'cost_B':10,'J16':40,'Z10':30},'logistics':{'trains':15,'utility_vehicles':150},'modeled_surrender_threshold_at_war_support_0_to_100_percent':limits,'base_war_stability_penalty_before_after':[war,war+.06],'supplied_DDS_assets':len(sources['assets']),'native_guard_only_overrides_verified':list(sources['native_guard_overrides']),'BOS_original_regular_divisions':4,'script_flow_model':'passed: payments, DLC packages, exact template/spawn counts, ownership/refund guards, 15-day war declaration, nonzero loss threshold, once-only join, cleanup','actual_combat_UI_and_engine_save_load':'not certified by static/model checks','postwar_peace_implemented':False}
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
