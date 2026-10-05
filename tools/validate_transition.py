"""Regress the real installed transition AST; this is not an engine combat test."""
from pathlib import Path
import argparse,json,subprocess
from validate_phase1 import ROOT,parse,get,descend
from validate_bosnia import BosniaModel

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--mod-root',type=Path,required=True)
    cli.add_argument('--report',type=Path,default=ROOT/'docs/transition_validation.json')
    args=cli.parse_args();mod=args.mod_root.resolve()
    scripts={p.relative_to(mod).as_posix():parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt','.gfx')}
    focuses={get(v,'id'):v for k,_,v in scripts['common/national_focus/MSGA_SER_post_kosovo.txt'][0][2] if k=='focus'}
    baseline=parse(subprocess.check_output(['git','show','1da12b2:make_serbia_great_again/common/national_focus/MSGA_SER_post_kosovo.txt'],cwd=ROOT).decode('utf-8-sig'))
    assert scripts['common/national_focus/MSGA_SER_post_kosovo.txt']==baseline,'Unrelated focus layout/reward changed'
    ready=get(scripts['common/scripted_triggers/MSGA_SER_triggers.txt'],'MSGA_bosnian_chapter_ready')
    forbidden={'MSGA_kosovo_rebuilt','MSGA_bosnian_question_emerging','MSGA_final_post_kosovo_story','MSGA_kosovo_review_progress','MSGA_done_commission_kosovo_dossier','MSGA_done_assess_kfor','MSGA_done_consult_general_staff','MSGA_done_contact_regional_partners','MSGA_done_map_northern_contingencies'}
    assert not any(isinstance(v,str) and v in forbidden for k,_,v in descend(ready))
    effects=scripts['common/scripted_effects/MSGA_SER_post_kosovo_effects.txt']
    unlock=get(effects,'MSGA_enter_bosnian_chapter')
    assert get(get(unlock,'if'),'limit')==parse('MSGA_bosnian_chapter_ready = yes NOT = { has_country_flag = MSGA_bosnian_crisis_started }')
    assert ('MSGA_enter_bosnian_chapter','=','yes') in get(effects,'MSGA_begin_serbian_question')
    on_actions=get(scripts['common/on_actions/MSGA_SER_post_kosovo_on_actions.txt'],'on_actions')
    assert ('MSGA_enter_bosnian_chapter','=','yes') in descend(get(on_actions,'on_startup'))
    weekly=get(on_actions,'on_weekly');assert ('MSGA_enter_bosnian_chapter','=','yes') in descend(weekly)
    first=next(v for k,_,v in scripts['common/national_focus/MSGA_SER_bosnian_crisis.txt'][0][2] if k=='focus')
    assert get(first,'id')=='MSGA_start_make_serbia_great_again'
    assert not any(k in ('available','prerequisite','bypass') for k,_,v in first),'Unexpected first-focus gate'

    def integrated():
        model=BosniaModel(scripts,mod);model.tree='MSGA_SER_post_kosovo'
        model.flags['SER'].update(['MSGA_post_kosovo_active','MSGA_kosovo_resolution_done','MSGA_kosovo_fully_integrated'])
        return model
    scenarios=[]
    for order in [['MSGA_rebuild_kosovo','MSGA_invest_in_pristina'],['MSGA_invest_in_pristina','MSGA_rebuild_kosovo']]:
        for final_decision in [False,True]:
            m=integrated()
            for id in order:
                m.focuses.add(id);m.execute(get(focuses[id],'completion_reward'))
                m.execute(parse('MSGA_enter_bosnian_chapter = yes'));assert m.tree=='MSGA_SER_post_kosovo'
            if final_decision:
                m.execute(parse('MSGA_complete_kosovo_reconstruction = yes'));assert 'MSGA_kosovo_rebuilt' in m.flags['SER']
            m.execute(get(focuses['MSGA_a_lasting_peace'],'completion_reward'));assert m.tree=='MSGA_SER_post_kosovo'
            # No narrative event is delivered before the focus completion unlock.
            m.focuses.add('MSGA_the_serbian_question');m.execute(get(focuses['MSGA_the_serbian_question'],'completion_reward'))
            assert m.tree=='MSGA_SER_bosnian_crisis' and 'MSGA_bosnian_crisis_active' in m.flags['SER']
            assert not {'MSGA_bosnian_question_emerging','MSGA_final_post_kosovo_story'} & m.flags['SER']
            before=m.queue.copy();m.execute(parse('MSGA_begin_serbian_question = yes MSGA_enter_bosnian_chapter = yes'));assert m.queue==before
            assert m.condition(next((v for k,_,v in first if k=='available'),[]))
            m.advance(4);assert m.tree=='MSGA_SER_bosnian_crisis'
            scenarios.append({'focus_order':order,'final_decision_completed':final_decision,'unlock':'immediate at approved terminal focus, before narrative events'})
    # Serialized older campaigns can contain completed focuses without narrative flags.
    m=integrated();m.focuses.update(['MSGA_rebuild_kosovo','MSGA_invest_in_pristina','MSGA_the_serbian_question'])
    m.execute(get(get(on_actions,'on_startup'),'effect'));assert m.tree=='MSGA_SER_bosnian_crisis'
    # Prevent global/early unlocks, and retry control loss without replaying rewards.
    blocked=[]
    for failure in ['war','integration','rebuild','pristina','terminal','ownership','control','core']:
        m=integrated();m.focuses.update(['MSGA_rebuild_kosovo','MSGA_invest_in_pristina','MSGA_the_serbian_question'])
        if failure=='war':m.flags['SER'].remove('MSGA_kosovo_resolution_done')
        elif failure=='integration':m.flags['SER'].remove('MSGA_kosovo_fully_integrated')
        elif failure in ('rebuild','pristina','terminal'):m.focuses.remove({'rebuild':'MSGA_rebuild_kosovo','pristina':'MSGA_invest_in_pristina','terminal':'MSGA_the_serbian_question'}[failure])
        elif failure=='ownership':m.states[785]='KOS'
        elif failure=='control':m.controllers[1305]='KOS'
        elif failure=='core':m.cores[785].clear()
        m.execute(parse('MSGA_enter_bosnian_chapter = yes'));assert m.tree=='MSGA_SER_post_kosovo';blocked.append(failure)
        if failure=='control':
            before_money=m.money;before_debt=m.debt;m.controllers[1305]='SER'
            m.execute(get(weekly,'effect'));assert m.tree=='MSGA_SER_bosnian_crisis' and m.money==before_money and m.debt==before_debt
    m=integrated();m.focuses.update(['MSGA_rebuild_kosovo','MSGA_invest_in_pristina','MSGA_the_serbian_question']);m.execute(parse('MSGA_enter_bosnian_chapter = yes'),'BOS');assert m.tree=='MSGA_SER_post_kosovo'
    report={'static_and_model_validation':'passed','validated_mod_root':str(mod),'blocked_Bosnia_focus':'MSGA_start_make_serbia_great_again','required_terminal_Kosovo_focus':'MSGA_the_serbian_question','final_reconstruction_decision_required':False,'focus_layout_and_artwork':'unchanged','positive_scenarios':scenarios,'startup_recovery_without_story_flags':'passed','weekly_retry_after_control_recovered':'passed','negative_cases':blocked+['wrong country scope'],'duplicate_transition_and_reward_prevention':'passed','gameplay_validation':'not certified by these model checks'}
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
