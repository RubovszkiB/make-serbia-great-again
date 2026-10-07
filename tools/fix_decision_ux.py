"""Targeted runtime-first decision presentation cleanup; no campaign redesign."""
from pathlib import Path
from dataclasses import dataclass, field
import argparse, hashlib, json, re, shutil, subprocess
from validate_phase1 import ROOT, TOKEN, parse, get

LIVE=Path(r'C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again')
BACKUP=ROOT/'logs/decision_ux_backup'
OBSOLETE={'MSGA_belgrade_business','MSGA_morava_works','MSGA_bor_modernisation','MSGA_lignite_modernisation','MSGA_jadar_survey','MSGA_jadar_feasibility','MSGA_support_enterprise','MSGA_foreign_priority','MSGA_invest_southern_serbia'}

@dataclass
class Node:
    key:str
    start:int
    end:int
    opening:int=0
    closing:int=0
    children:list=field(default_factory=list)

def nodes(text):
    tokens=[m for m in TOKEN.finditer(text) if not m[0].startswith('#')];i=0
    def block():
        nonlocal i
        result=[]
        while i<len(tokens) and tokens[i][0]!='}':
            t=tokens[i];i+=1;n=Node(t[0],t.start(),t.end())
            if i<len(tokens) and tokens[i][0] in ('=','>','<','>=','<=','!='):
                i+=1;v=tokens[i];i+=1
                if v[0]=='{':
                    n.opening=v.end();n.children=block();n.closing=tokens[i].start();n.end=tokens[i].end();i+=1
                else:n.end=v.end()
            result.append(n)
        return result
    result=block();assert i==len(tokens);return result

def gameplay(ast):
    """Ignore presentation wrappers, preserving every executable condition/effect."""
    out=[]
    for k,o,v in ast:
        if k in ('custom_effect_tooltip','tooltip'):continue
        if k in ('hidden_effect','hidden_trigger','custom_trigger_tooltip','custom_override_tooltip'):
            out.extend(gameplay(v));continue
        out.append((k,o,gameplay(v) if isinstance(v,list) else v))
    return out

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def words(id):return id.removeprefix('MSGA_').replace('_',' ').title()

def legacy_localisation(text):
    text=re.sub(r'^( MSGA_expand_defence_desc:.*)state 1296',r'\1Central Serbia',text,flags=re.M)
    replacements={
      'MSGA_unlock_capital_tt':('Funded development and partner decisions remain available.','Further investment programmes open after A Recovery Made in Serbia.'),
      'MSGA_unlock_belgrade_tt':('A further funded Office Park project remains available.','Further investment programmes open after A Recovery Made in Serbia.'),
      'MSGA_unlock_morava_tt':('Further funded corridor improvements remain available.','Further funded corridor improvements open after A Recovery Made in Serbia.'),
      'MSGA_unlock_resources_tt':('Further mining and energy projects remain available.','Further mining and energy projects open after A Recovery Made in Serbia.'),
    }
    for key,(old,new) in replacements.items():
        text=re.sub(r'^( '+re.escape(key)+r':.*)$',lambda m:m[0].replace(old,new),text,flags=re.M)
    return text

def presentation(id, category):
    # Player-facing summaries only; executable scripts are retained verbatim.
    if id.startswith('MSGA_form_territorial_'):
        region={'45':'Vojvodina','108':'Eastern Serbia','1296':'Central Serbia','785':'Kosovo','1305':'Northern Kosovo'}[id.rsplit('_',1)[1]]
        return (f'Serbia owns and fully controls its core territory in {region}.',f'Cost: $0.5B Treasury. Raise one territorial defence formation in {region} after 14 days; loss of the recruitment area returns the Treasury cost.')
    if id.startswith('MSGA_regularise_'):
        region=words(id).replace('Regularise ','')
        return (f'Pact victory is secured; {region} remains a Serbian subject; no other client regularisation is underway.',f'Regularise relations with {region} over 10 days. On completion: subject Stability +10%, closer relations with Serbia and Autonomy Score -50; remove its temporary post-war recovery restrictions where present.')
    entries={
      'MSGA_reopen_air_procurement':('At least $10B Treasury is available.','Reopen the aircraft procurement offer; choosing an aircraft package happens in the following event.'),
      'MSGA_organise_bosnian_territorial_militias':('Bosnia remains a Serbian subject; Serbia owns and controls Belgrade.','Cost: $0.25B Treasury and 25 PP. Organise the approved Bosnian militia formations under Serbian command.'),
      'MSGA_organise_herzegovinian_territorial_militias':('Herzegovina remains a Serbian subject; Serbia owns and controls Belgrade.','Cost: $0.25B Treasury and 25 PP. Organise the approved Herzegovinian militia formations under Serbian command.'),
      'MSGA_form_srpska_territorial_defence':('Srpska is a Serbian subject or has united with Serbia; Serbia owns and controls Belgrade.','Cost: $0.5B Treasury. Form the approved Srpska territorial defence units under Serbian command.'),
      'MSGA_SER_reaffirm_presidential_authority':('This measure has been used fewer than three times.','Cost: 35 PP. Move the balance of power 4% towards the Presidency. Can be used three times, with 120 days between uses.'),
      'MSGA_SER_address_public_grievances':('This measure has been used fewer than twice; sufficient Treasury is available.','Cost: 40 PP and $0.05B Treasury adjusted for inflation. Stability +1%; move the balance of power 2% towards the Streets. Can be used twice, with 120 days between uses.'),
      'MSGA_public_order':('This measure has been used fewer than twice; the previous public backlash has ended.','Cost: 25 PP. Move the balance of power 6% towards the Presidency; Stability -1%. A public backlash follows after 30 days. Can be used twice, with 180 days between uses.'),
      'MSGA_assess_world':('The international strategic assessment is ready.','Review the international situation and receive the existing strategic briefing.'),
      'MSGA_pending_outbreak':('This countdown cannot be selected.','The outbreak countdown leads to the existing public-health event if the crisis remains unresolved.'),
      'MSGA_restrict_border_traffic':('The outbreak countdown is active.','Cost: 10 PP. Delay the outbreak countdown by 120 days.'),
      'MSGA_emergency_screening':('The outbreak countdown is active.','Cost: 15 PP. Delay the outbreak countdown by 130 days.'),
      'MSGA_public_health_controls':('The outbreak countdown is active.','Cost: 20 PP. Delay the outbreak countdown by 150 days.'),
      'MSGA_mass_vaccination':('The vaccination programme becomes available from 1 January 2021.','Cost: 75 PP. After 20 days, resolve the domestic COVID crisis and gain Stability +2%.'),
      'MSGA_expand_defence':('No other major project is underway; Serbia owns and controls Central Serbia, has room for a military factory and sufficient Treasury.','Cost: 75 PP and $0.35B Treasury adjusted for inflation. Duration: 120 days. On completion: +1 Military Factory in Central Serbia if its required construction conditions still hold; otherwise the project payment and 75 PP are returned.'),
      'MSGA_procure_equipment':('At least $3B Treasury is available.','Cost: $3B Treasury. After 30 days: +3,500 Infantry Equipment, +100 Support Equipment, +50 Artillery, +150 Motorised Equipment and +3 Army Experience.'),
      'MSGA_integrate_kosovo_serb_militias':('Kosovo is integrated and the Kosovo campaign is resolved; Serbia owns and controls both Kosovo regions as core territory.','Cost: $2B Treasury. Integrate the Kosovo Serb Brigade under Serbian command using the approved brigade template.'),
      'MSGA_finish_kosovo_reconstruction':('Serbia owns and fully controls both Kosovo regions.','Cost: $1B Treasury and 50 PP. Industrial Development +0.05; +1 Infrastructure in Kosovo if below its maximum; remove the remaining reconstruction and rebellion restrictions. This final project is optional for the Bosnia chapter.'),
      'MSGA_assess_nato_readiness':('The strategic assessment is available.','Cost: 25 PP. Complete the NATO readiness assessment after 14 days; gain +5 Army Experience and advance the strategic review.'),
      'MSGA_strengthen_border_intelligence':('Sufficient Treasury is available for the border intelligence payment.','Cost: 35 PP and $0.03B Treasury adjusted for inflation. After 30 days: Strategic Vigilance for 180 days and progress in the strategic review.'),
    }
    if id.startswith('MSGA_raise_'):
        return ('Serbia fully controls at least one of its core states.','Cost: $2B Treasury. After 20 days, raise one '+words(id).replace('Raise ','')+' volunteer formation under Serbian command.')
    if id.startswith('MSGA_prepare_offensive_'):
        region='Kosovo' if id.endswith('785') else 'Northern Kosovo'
        return ('Serbia is at war with Kosovo.','Cost: 25 Command Power. After 14 days, remove the unprepared-sector penalty in '+region+' if the Kosovo campaign is still active.')
    assert id in entries,('Missing authored summary',id,category)
    return entries[id]

def main():
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--mod-root',type=Path,default=LIVE);args=cli.parse_args();mod=args.mod_root.resolve(strict=True)
    BACKUP.mkdir(parents=True,exist_ok=True);changes={};cleaned=[];loc={};removed=[]
    for p in sorted((mod/'common/decisions').glob('MSGA*.txt')):
        if p.name=='MSGA_economic_energy_decisions.txt':continue
        text=p.read_text(encoding='utf-8-sig');edits=[]
        for category in nodes(text):
            if category.key=='MSGA_economic_development':
                removed.extend(n.key for n in category.children);edits.append((category.start,category.end,''));continue
            for decision in category.children:
                if not decision.children:continue
                id=decision.key;requirement,reward=presentation(id,category.key);did=False
                for section in decision.children:
                    if section.key=='available':
                        body=text[section.opening:section.closing]
                        # Simple date/war/mission/always conditions already have readable native UI.
                        raw=any(k in body for k in ['has_country_flag','check_variable','is_owned_by','is_fully_controlled_by','MSGA_regularisation_free'])
                        if raw:
                            key=id+'_ux_requirements_tt';loc[key]=requirement
                            edits.append((section.opening,section.closing,' custom_trigger_tooltip = { tooltip = '+key+' hidden_trigger = { '+body+' } } '));did=True
                    elif section.key=='custom_cost_trigger':
                        body=text[section.opening:section.closing]
                        if 'check_variable' in body:edits.append((section.opening,section.closing,' hidden_trigger = { '+body+' } '));did=True
                    elif section.key in ['complete_effect','remove_effect','cancel_effect','timeout_effect']:
                        body=text[section.opening:section.closing]
                        technical=any(k in body for k in ['country_flag','variable','MSGA_','add_income'])
                        if technical:
                            key=id+'_ux_'+section.key+'_tt'
                            if section.key=='cancel_effect':summary=('Project cancelled; the Treasury payment and 75 PP are refunded.' if id=='MSGA_expand_defence' else 'Cancel this client process if the country is no longer a Serbian subject.')
                            else:summary=reward
                            loc[key]=summary
                            edits.append((section.opening,section.closing,' custom_effect_tooltip = '+key+' hidden_effect = { '+body+' } '));did=True
                if did:cleaned.append(id)
        new=text
        for a,b,replacement in sorted(edits,reverse=True):new=new[:a]+replacement+new[b:]
        old_ast=[n for n in parse(text) if n[0]!='MSGA_economic_development']
        assert gameplay(parse(new))==gameplay(old_ast),p
        if new!=text:changes[p.relative_to(mod).as_posix()]=new
    assert set(removed)==OBSOLETE,removed
    path='common/decisions/categories/MSGA_SER_categories.txt';text=(mod/path).read_text();old=nodes(text);n=next(n for n in old if n.key=='MSGA_economic_development');new=text[:n.start]+text[n.end:]
    assert parse(new)==[a for a in parse(text) if a[0]!='MSGA_economic_development'];changes[path]=new
    path='common/national_focus/MSGA_SER_phase1.txt';text=(mod/path).read_text();new=re.sub(r'^[ \t]*unlock_decision_tooltip\s*=\s*('+'|'.join(sorted(OBSOLETE))+r')\s*\n','',text,flags=re.M)
    assert len(re.findall('unlock_decision_tooltip',text))-len(re.findall('unlock_decision_tooltip',new))==8
    changes[path]=new
    path='localisation/english/MSGA_l_english.yml';text=(mod/path).read_text(encoding='utf-8-sig')
    new=legacy_localisation(text)
    assert text!=new;changes[path]=new
    # No supporting effects/variables are removed: early focuses still depend on them.
    loc_path='localisation/english/MSGA_decision_ux_l_english.yml'
    changes[loc_path]='l_english:\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items())
    records={}
    for path,new in changes.items():
        new='\n'.join(line.rstrip() for line in new.splitlines())+'\n'
        p=mod/path;dest=BACKUP/path;dest.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() and not dest.exists():shutil.copyfile(p,dest)
        before=sha(dest) if dest.exists() else None
        p.write_text(new,encoding='utf-8-sig' if path.endswith('.yml') else 'utf-8',newline='\r\n')
        records[path]={'before_sha256':before,'after_sha256':sha(p)}
    data={'runtime':str(mod),'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'files':records,'obsolete_category':'MSGA_economic_development','removed_decisions':sorted(removed),'global_cleaned_decisions':cleaned,'economic_cleaned_decisions':37,'gameplay_preservation':'Parsed executable conditions/effects are identical after removing presentation-only wrappers; only obsolete category decisions and eight dangling focus previews were removed.'}
    (ROOT/'docs/decision_ux_sources.json').write_text(json.dumps(data,indent=2)+'\n')
    print(f'Runtime updated: {len(cleaned)} campaign decisions cleaned; 9 obsolete decisions removed; {len(changes)} text files changed. Source synchronization awaits validation.')

if __name__=='__main__':main()
