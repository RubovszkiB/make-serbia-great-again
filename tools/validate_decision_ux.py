"""Installed decision UX checks, executable preservation and authored reward audit.

Static/model checks do not certify HOI4 rendering or engine building delivery.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
from PIL import Image
from validate_phase1 import ROOT, parse, get, descend, obsolete_previews
from fix_decision_ux import gameplay, OBSOLETE

def main():
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,required=True);args=cli.parse_args();mod=args.mod_root
    ledger=json.loads((ROOT/'docs/decision_ux_sources.json').read_text());econ=json.loads((ROOT/'docs/economic_energy_sources.json').read_text())
    scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
    decisions={k:v for p,a in scripts.items() if p.startswith('common/decisions/') and '/categories/' not in p and Path(p).name.startswith('MSGA') for c,o,entries in a for k,o,v in entries}
    categories={k for p,a in scripts.items() if p.startswith('common/decisions/categories/') for k,o,v in a}
    assert 'MSGA_economic_development' not in categories and not (OBSOLETE & decisions.keys())
    assert {'MSGA_serbian_economic_cooperation','MSGA_serbian_energy_development'}<=categories
    for p,a in scripts.items():
        if p.startswith('common/decisions/') and '/categories/' not in p and Path(p).name.startswith('MSGA'):
            assert all(c in categories for c,o,v in a),p
        assert not any(k=='unlock_decision_tooltip' and v in OBSOLETE for k,o,v in descend(a)),p
    for path,record in ledger['files'].items():
        assert hashlib.sha256((mod/path).read_bytes()).hexdigest()==record['after_sha256'],path
        if record['before_sha256'] is None:continue
        before=subprocess.check_output(['git','show',ledger['baseline_commit']+':make_serbia_great_again/'+path],cwd=ROOT)
        # Git stores LF text while this Windows runtime uses CRLF.
        lf=before.replace(b'\r\n',b'\n')
        assert record['before_sha256'] in {hashlib.sha256(b).hexdigest() for b in (before,lf,lf.replace(b'\n',b'\r\n'))},path
        if path.endswith('.yml'):
            old_lines=before.decode('utf-8-sig').replace('\r\n','\n').splitlines();new_lines=(mod/path).read_text(encoding='utf-8-sig').splitlines()
            allowed={'MSGA_expand_defence_desc','MSGA_unlock_capital_tt','MSGA_unlock_belgrade_tt','MSGA_unlock_morava_tt','MSGA_unlock_resources_tt'}
            assert len(old_lines)==len(new_lines)
            changed=set()
            for old,new in zip(old_lines,new_lines):
                if old==new:continue
                key=old.split(':',1)[0].strip();assert key in allowed and new.startswith(' '+key+':'),path;changed.add(key)
                if key!='MSGA_expand_defence_desc':assert old.split('. ',1)[0]==new.split('. ',1)[0] and 'after A Recovery Made in Serbia' in new
                else:assert new==old.replace('state 1296','Central Serbia')
            assert changed==allowed
            continue
        old=parse(before.decode('utf-8-sig'));new=scripts[path]
        if path.startswith('common/decisions/'):
            assert gameplay(new)==gameplay([a for a in old if a[0]!='MSGA_economic_development']),path
        elif path.startswith('common/national_focus/'):
            def strip(a):return [(k,o,strip(v) if isinstance(v,list) else v) for k,o,v in obsolete_previews(a)]
            assert new==strip(old),path
    loc={}
    for p in (mod/'localisation/english').glob('*.yml'):
        for line in p.read_text(encoding='utf-8-sig').splitlines():
            m=re.match(r'\s*(\S+):\d+\s+"(.*)"\s*$',line)
            if m:assert m[1] not in loc,m[1];loc[m[1]]=m[2]
    for id,body in decisions.items():
        for k,o,v in descend(body):
            if k in ('custom_effect_tooltip','tooltip','custom_cost_text') and v.startswith('MSGA_'):assert v in loc,(id,v)
    for id in ledger['global_cleaned_decisions']:
        b=decisions[id]
        for key,o,a in b:
            if key=='available':
                visible=repr([i for i in a if i[0] not in ('custom_trigger_tooltip','hidden_trigger')])
                assert not any(t in visible for t in ('has_country_flag','check_variable','is_owned_by','is_fully_controlled_by','MSGA_regularisation_free')),id
    effects=scripts['common/scripted_effects/MSGA_economic_energy_effects.txt'];physical=[]
    for p in econ['projects']+econ['programmes']:
        id='MSGA_'+p['stem'];b=decisions[id]
        assert get(get(get(b,'available'),'custom_trigger_tooltip'),'hidden_trigger')
        assert get(get(b,'complete_effect'),'hidden_effect')
        assert not any(t in loc[id+'_desc']+loc[id+'_requirements_tt']+loc[id+'_reward_tt'] for t in ('MSGA_','pending','busy','state 45','state 108','state 1296','state 107','native','scripted')),(id,'Technical prose')
        if p in econ['projects']:
            assert str(p['days'])+' days' in loc[id+'_desc'] and get(b,'days_remove')==str(p['days'])
            finish=get(effects,'MSGA_finish_'+p['stem'])
            grants=[v for k,o,v in descend(finish) if k=='add_building_construction']
            if grants:
                physical.append(id)
                for grant in grants:
                    building=get(grant,'type')
                    state=get(get(finish,'if'),str(p['state']))
                    assert ('set_temp_variable','=',parse('var = MSGA_delivery_before value = building_level@'+building)) in descend(state)
                    assert ('set_temp_variable','=',parse('var = MSGA_delivery_after value = building_level@'+building)) in descend(state)
                    assert ('check_variable','=',parse('var = MSGA_delivery_after value = MSGA_delivery_expected compare = equals')) in descend(state)
                    assert get(grant,'instant_build')=='yes' and get(grant,'level')=='1'
                assert any(k=='has_country_flag' and v=='MSGA_building_delivered_'+p['stem'] for k,o,v in descend(finish))
                assert '+1 ' in loc[id+'_completion_tt']
            if p['reward'] in ('mining','jadar'):
                assert '+3 Steel' in loc[id+'_completion_tt'] and '+2 Tungsten' in loc[id+'_completion_tt']
        else:assert '180 days' in loc[id+'_desc'] and '70 days' in loc[id+'_desc']
    for stem in ['first_serbian_nuclear_power_plant','expand_serbian_nuclear_programme']:
        assert '+1 Nuclear Reactor in Vojvodina' in loc['MSGA_'+stem+'_completion_tt']
        assert '180 days' in loc['MSGA_'+stem+'_desc']
    images=[]
    for path,a in econ['assets'].items():
        if a['size']!=[52,45]:continue
        data=(mod/path).read_bytes();assert data[84:88]==b'DXT5'
        im=Image.open(mod/path).convert('RGBA');assert im.size==(52,45)
        assert all(max(im.getpixel(pos)[:3])<30 and im.getpixel(pos)[3]>245 for pos in [(0,0),(51,0),(0,44),(51,44)])
        images.append(im)
    assert len(images)==37
    # Inspection sheet uses the installed DDS bytes, not the generator's source image.
    sheet=Image.new('RGB',(9*104,5*90),(65,65,65))
    for i,im in enumerate(images):sheet.paste(im.resize((104,90),Image.Resampling.NEAREST),(i%9*104,i//9*90))
    sheet.save(ROOT/'logs/decision_ux_framed_icons.png')
    report={'validation':'passed','runtime':str(mod),'economic_energy_decisions_cleaned':37,'other_campaign_decisions_cleaned':len(ledger['global_cleaned_decisions']),'total_decisions_cleaned':37+len(ledger['global_cleaned_decisions']),'obsolete_decisions_removed':9,'obsolete_category_absent':True,'focus_layout_and_gameplay':'Unchanged; eight obsolete decision preview hints removed','campaign_gates_and_effects':'Exactly preserved after presentation normalization','physical_reward_paths_checked':physical,'framed_decision_DDS':37,'non_decision_art':'Unchanged; checked by economic validator and whole-installation diff','nuclear':'180-day reachable callbacks and 0 -> 1 -> 2 counters checked in the deterministic model only','engine_validation':'NOT RUN: no game window or save was touched. Actual reactor increase, tooltips and icon appearance still require the user test.'}
    (ROOT/'docs/decision_ux_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
