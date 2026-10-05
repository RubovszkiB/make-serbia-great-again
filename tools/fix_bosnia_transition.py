"""Repair only the installed Kosovo-to-Bosnia connection, with a local backup."""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
LIVE=Path('C:/Users/Balazs/Documents/Paradox Interactive/Hearts of Iron IV/mod/make_serbia_great_again')
assert LIVE.resolve(strict=True)==LIVE.absolute()
BACKUP=ROOT/'logs/transition_backup'
BACKUP.mkdir(parents=True,exist_ok=True)

def replace_block(text,key,replacement):
    match=re.search(r'(?m)^'+re.escape(key)+r'\s*=\s*\{',text)
    start=match.start();end=text.index('{',start)+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[:start]+replacement.strip()+text[end:]

changes={}
path='common/scripted_triggers/MSGA_SER_triggers.txt'
s=(LIVE/path).read_text(encoding='utf-8-sig')
assert 'MSGA_bosnian_chapter_ready' not in s,'Transition patch is already installed'
changes[path]=s+'''
# Approved focus progression is authoritative; story events and the optional
# final reconstruction decision cannot hold the chapter switch hostage.
MSGA_bosnian_chapter_ready = {
 tag = SER
 has_country_flag = MSGA_kosovo_resolution_done
 has_country_flag = MSGA_kosovo_fully_integrated
 OR = { has_completed_focus = MSGA_rebuild_kosovo has_country_flag = MSGA_completed_rebuild_kosovo }
 OR = { has_completed_focus = MSGA_invest_in_pristina has_country_flag = MSGA_completed_invest_in_pristina }
 OR = { has_completed_focus = MSGA_the_serbian_question has_country_flag = MSGA_completed_the_serbian_question }
 785 = { is_owned_by = SER is_fully_controlled_by = SER is_core_of = SER }
 1305 = { is_owned_by = SER is_fully_controlled_by = SER is_core_of = SER }
}
'''
path='common/scripted_effects/MSGA_SER_post_kosovo_effects.txt'
s=(LIVE/path).read_text(encoding='utf-8-sig')
s=replace_block(s,'MSGA_begin_serbian_question','''
MSGA_begin_serbian_question = {
 if = { limit = { tag = SER OR = { has_completed_focus = MSGA_the_serbian_question has_country_flag = MSGA_completed_the_serbian_question } NOT = { has_country_flag = MSGA_serbian_question_chain_started } }
  set_country_flag = MSGA_serbian_question_chain_started
  country_event = { id = MSGA_postkosovo.12 }
 }
 # Completion opens the next chapter immediately. The existing narrative
 # events still run, but their one-shot flags are no longer progression gates.
 MSGA_enter_bosnian_chapter = yes
}''')
s=replace_block(s,'MSGA_enter_bosnian_chapter','''
MSGA_enter_bosnian_chapter = {
 if = { limit = { MSGA_bosnian_chapter_ready = yes NOT = { has_country_flag = MSGA_bosnian_crisis_started } }
  set_country_flag = MSGA_bosnian_crisis_started
  set_country_flag = MSGA_bosnian_crisis_active
  clr_country_flag = MSGA_post_kosovo_active
  load_focus_tree = { tree = MSGA_SER_bosnian_crisis keep_completed = yes }
 }
}''')
changes[path]=s
path='common/on_actions/MSGA_SER_post_kosovo_on_actions.txt'
s=(LIVE/path).read_text(encoding='utf-8-sig')
s=s.replace('if = { limit = { has_country_flag = MSGA_final_post_kosovo_story } MSGA_enter_bosnian_chapter = yes }','MSGA_enter_bosnian_chapter = yes')
# Startup recovers existing saves, and the weekly check retries when control
# was temporarily lost during completion. Neither callback grants rewards.
s=s.rstrip().rsplit('}',1)[0]+''' on_weekly = { effect = { if = { limit = { tag = SER has_country_flag = MSGA_campaign_active } MSGA_enter_bosnian_chapter = yes } } }
}
'''
changes[path]=s
manifest=[]
for relative,text in changes.items():
    p=LIVE/relative;assert p.resolve().is_relative_to(LIVE)
    before=p.read_bytes();target=BACKUP/relative;target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists(),'Do not overwrite the original backup'
    target.write_bytes(before);after=text.encode('utf-8');p.write_bytes(after)
    manifest.append({'file':str(p),'relative':relative,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest()})
(ROOT/'docs/transition_deployment.json').write_text(json.dumps({'runtime_target':str(LIVE),'files':manifest,'final_reconstruction_decision_required':False,'required_terminal_focus':'MSGA_the_serbian_question','first_Bosnia_focus':'MSGA_start_make_serbia_great_again','actual_game_validation':'pending'},indent=2)+'\n')
print(f'Installed transition repair in {len(manifest)} files; focus layout and artwork unchanged.')
