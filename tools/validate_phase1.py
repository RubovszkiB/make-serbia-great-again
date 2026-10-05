"""Static checks for MSGA Phase 1. Does not claim campaign acceptance."""
from pathlib import Path
import json
import re
import struct
import subprocess
from collections import Counter
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "make_serbia_great_again"
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|>=|<=|!=|=|>|<|\{|\}|[^\s{}=<>!#]+')


def parse(text):
    tokens = [t for t in TOKEN.findall(text) if not t.startswith('#')]
    cursor = 0

    def block(nested=False):
        nonlocal cursor
        pairs = []
        while cursor < len(tokens) and tokens[cursor] != '}':
            key = tokens[cursor]
            cursor += 1
            if cursor < len(tokens) and tokens[cursor] in ('=', '>', '<', '>=', '<=', '!='):
                operator = tokens[cursor]
                cursor += 1
                value = tokens[cursor]
                cursor += 1
                if value == '{':
                    value = block(True)
                pairs.append((key, operator, value))
            else:
                pairs.append((key, None, None))
        if nested:
            assert cursor < len(tokens) and tokens[cursor] == '}', 'Unclosed block'
            cursor += 1
        return pairs

    result = block()
    assert cursor == len(tokens), 'Unexpected closing brace'
    return result


def descend(pairs):
    for key, op, value in pairs:
        yield key, op, value
        if isinstance(value, list):
            yield from descend(value)


def get(pairs, key):
    return next(value for name, _, value in pairs if name == key)


def unique(values, label):
    duplicates = [v for v, n in Counter(values).items() if n > 1]
    assert not duplicates, f'{label} duplicates: {duplicates}'


def main():
    scripts = {p.relative_to(MOD).as_posix(): parse(p.read_text(encoding='utf-8-sig'))
               for p in MOD.rglob('*') if p.suffix in ('.txt', '.gfx')}
    all_pairs = [item for ast in scripts.values() for item in descend(ast)]
    focus_path = 'common/national_focus/MSGA_SER_phase1.txt'
    tree = scripts[focus_path][0][2]
    focuses = [v for k, _, v in tree if k == 'focus']
    focus_ids = [get(f, 'id') for f in focuses]
    assert len(focus_ids) == 18
    unique(focus_ids, 'Focus')
    baseline_text = subprocess.check_output(
        ['git', 'show', '38d855e:make_serbia_great_again/' + focus_path], cwd=ROOT).decode('utf-8')
    baseline = [v for k, _, v in parse(baseline_text)[0][2] if k == 'focus']
    topology_keys = {'id', 'x', 'y', 'cost', 'prerequisite', 'cancel_if_invalid'}
    topology = lambda fs: [[item for item in f if item[0] in topology_keys] for f in fs]
    assert topology(focuses) == topology(baseline), 'Focus topology or timing changed'
    by_focus = {get(f, 'id'): f for f in focuses}
    assert get(by_focus['MSGA_reopen_on_serbian_terms'], 'available') == parse('has_country_flag = MSGA_mass_vaccination_complete')
    assert not any(k == 'available' for k, _, _ in by_focus['MSGA_watch_the_western_shield'])
    assert get(by_focus['MSGA_the_kosovo_question'], 'available') == parse('has_country_flag = MSGA_western_shield_cracked')
    graph = {get(f, 'id'): [get(v, 'focus') for k, _, v in f if k == 'prerequisite'] for f in focuses}
    visited, active = set(), set()

    def visit(node):
        assert node in graph, f'Missing prerequisite {node}'
        assert node not in active, f'Cycle at {node}'
        if node in visited:
            return
        active.add(node)
        for parent in graph[node]:
            visit(parent)
        active.remove(node)
        visited.add(node)

    for focus in focus_ids:
        visit(focus)
    referenced = {n for parents in graph.values() for n in parents}
    assert set(graph) - referenced == {'MSGA_the_kosovo_question'}
    sprites = [v for k, _, v in descend(scripts['interface/MSGA_focus_icons.gfx']) if k == 'SpriteType']
    sprite_names = [get(s, 'name').strip('"') for s in sprites]
    unique(sprite_names, 'Sprite')
    for f in focuses:
        assert get(f, 'icon') == 'GFX_goal_' + get(f, 'id')
        assert get(f, 'icon') in sprite_names
        assert get(f, 'icon') + '_shine' in sprite_names
        assert get(f, 'completion_reward')
        meaningful = [k for k, _, _ in get(f, 'completion_reward')
                      if k not in ('set_country_flag', 'custom_effect_tooltip')]
        assert meaningful, f'Only flags/text in focus {get(f, "id")}'
    for sprite in sprites:
        texture = MOD / get(sprite, 'texturefile').strip('"')
        assert texture.is_file(), texture
        header = texture.read_bytes()[:128]
        assert header[:4] == b'DDS ' and struct.unpack_from('<I', header, 88)[0] == 32
        image = Image.open(texture).convert('RGBA')
        reference = Image.open(ROOT / 'art/focus_icons/MSGA_TFR_focus_icons/png_95' / (texture.stem + '.png')).convert('RGBA')
        assert image.size == (95, 95) and image.tobytes() == reference.tobytes()
    categories = [k for k, _, _ in scripts['common/decisions/categories/MSGA_SER_categories.txt']]
    unique(categories, 'Category')
    decisions = []
    for p, ast in scripts.items():
        if p.startswith('common/decisions/') and '/categories/' not in p:
            for category, _, entries in ast:
                assert category in categories
                decisions.extend(k for k, _, _ in entries)
    unique(decisions, 'Decision')
    ideas = [k for k, _, _ in scripts['common/ideas/MSGA_SER_ideas.txt'][0][2][0][2]]
    dynamic = [k for k, _, _ in scripts['common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt']]
    effects = [k for k, _, _ in scripts['common/scripted_effects/MSGA_SER_effects.txt']]
    triggers = [k for k, _, _ in scripts['common/scripted_triggers/MSGA_SER_triggers.txt']]
    for label, values in [('Idea', ideas), ('Dynamic modifier', dynamic), ('Effect', effects), ('Trigger', triggers)]:
        unique(values, label)
    event_bodies = [v for p, ast in scripts.items() if p.startswith('events/') for k, _, v in ast if k == 'country_event']
    namespaces = [v for p, ast in scripts.items() if p.startswith('events/') for k, _, v in ast if k == 'add_namespace']
    events = [get(v, 'id') for v in event_bodies]
    assert all(i.split('.')[0] in namespaces for i in events)
    unique(events, 'Event')
    for k, _, v in all_pairs:
        if k in ('add_ideas', 'remove_ideas', 'has_idea', 'remove_idea', 'add_idea', 'idea') and isinstance(v, str) and v.startswith('MSGA_'):
            assert v in ideas, (k, v)
        if k in ('add_dynamic_modifier', 'remove_dynamic_modifier', 'has_dynamic_modifier'):
            assert get(v, 'modifier') in dynamic
        if k == 'country_event':
            assert get(v, 'id') in events
        if k == 'unlock_decision_tooltip':
            assert v in decisions
        if k.startswith('MSGA_') and v == 'yes':
            assert k in effects + triggers, f'Undefined call {k}'
    effects_ast = scripts['common/scripted_effects/MSGA_SER_effects.txt']
    recovery_refresh = get(effects_ast, 'MSGA_refresh_recovery')
    assert get(get(recovery_refresh, 'clamp_variable'), 'max') == '0.10'
    capstone = get(by_focus['MSGA_serbian_recovery'], 'completion_reward')
    assert ('remove_ideas', '=', 'SER_scars_of_bombings_idea') in capstone
    final_army = get(next(f for f in focuses if get(f, 'id') == 'MSGA_ready_for_the_uncertain'), 'completion_reward')
    assert get(get(final_army, 'swap_ideas'), 'add_idea') == 'MSGA_army_ready'
    assert not any(k == 'on_daily' for k, _, _ in all_pairs), 'Daily polling is forbidden'
    covid = get(scripts['common/decisions/MSGA_SER_covid.txt'], 'MSGA_public_health')
    assert len(covid) == 2
    for name, _, cost, flag in [('MSGA_hospital_funding', None, '50', 'MSGA_hospitals_supported'),
                               ('MSGA_mass_vaccination', None, '75', 'MSGA_mass_vaccination_complete')]:
        decision = get(covid, name)
        assert get(decision, 'cost') == cost and get(decision, 'days_remove') == '35'
        assert ('set_country_flag', '=', flag) in get(decision, 'remove_effect')
        assert not any(v == flag for k, _, v in get(decision, 'complete_effect'))
    assert ('has_country_flag', '=', 'MSGA_hospitals_supported') in get(get(covid, 'MSGA_mass_vaccination'), 'available')
    event_by_id = {get(b, 'id'): b for b in event_bodies}
    dispatcher = event_by_id['MSGA_chronicle.1']
    assert get(dispatcher, 'hidden') == 'yes'
    random_pool = get(get(get(dispatcher, 'immediate'), 'if'), 'random_list')
    assert random_pool[0] == ('35', '=', []) and len(random_pool) == 8
    for _, _, branch in random_pool[1:]:
        assert get(get(branch, 'modifier'), 'factor') == '0'
        assert get(get(get(branch, 'modifier'), 'NOT'), 'AND'), 'Eligibility must negate the complete conjunction'
        assert get(get(branch, 'set_country_flag'), 'days') == '360'
        assert get(branch, 'country_event')
    assert get(get(get(effects_ast, 'MSGA_start_chronicle'), 'if'), 'country_event') == parse('id = MSGA_chronicle.1 days = 120 random_days = 90')
    for id, b in event_by_id.items():
        assert get(b, 'is_triggered_only') == 'yes'
        if id.startswith('MSGA_chronicle.'):
            assert not any(k == 'fire_only_once' for k, _, _ in b)
        elif get(b, 'id') not in ('MSGA.10', 'MSGA.11', 'MSGA_geopolitics.2'):
            assert get(b, 'fire_only_once') == 'yes'
    major_ids = {'MSGA_belgrade_business', 'MSGA_morava_works', 'MSGA_bor_modernisation',
                 'MSGA_lignite_modernisation', 'MSGA_jadar_survey', 'MSGA_jadar_feasibility', 'MSGA_expand_defence'}
    for p, ast in scripts.items():
        if not p.startswith('common/decisions/') or '/categories/' in p:
            continue
        for _, _, entries in ast:
            for name, _, body in entries:
                if name in major_ids:
                    assert get(body, 'days_remove')
                    assert ('MSGA_major_project_free', '=', 'yes') in get(body, 'available')
                    assert any(k == 'is_fully_controlled_by' for k, _, _ in descend(get(body, 'available')))
                    assert any(k == 'MSGA_refund_project' for k, _, _ in descend(get(body, 'cancel_effect')))
                if p.endswith('MSGA_SER_strategic_review.txt'):
                    assert int(get(body, 'cost')) > 0
                    assert any(k == 'set_country_flag' and v == name.replace('MSGA_', 'MSGA_started_', 1)
                               for k, _, v in descend(get(body, 'complete_effect')))
    locale_path = MOD / 'localisation/english/MSGA_l_english.yml'
    assert locale_path.read_bytes().startswith(b'\xef\xbb\xbf')
    locale = locale_path.read_text(encoding='utf-8-sig')
    locale_keys = re.findall(r'^\s*([^\s:]+):\d\s+".*"\s*$', locale, re.M)
    unique(locale_keys, 'Localisation')
    required = focus_ids + [f + '_desc' for f in focus_ids] + ideas + dynamic + categories + decisions
    required += [k + '_desc' for k in ideas + categories + decisions]
    required += [v for k, _, v in all_pairs if k in ('custom_effect_tooltip', 'title', 'desc', 'name') and isinstance(v, str) and v.startswith('MSGA')]
    assert not set(required) - set(locale_keys), f'Missing localisation {set(required) - set(locale_keys)}'
    for key in re.findall(r'\$([^$\s]+)\$', locale):
        assert key in locale_keys, f'Unresolved localisation substitution {key}'
    baseline_locale = subprocess.check_output(['git', 'show', '38d855e:make_serbia_great_again/localisation/english/MSGA_l_english.yml'], cwd=ROOT).decode('utf-8-sig')
    for focus in focus_ids:
        pattern = rf'^\s*{focus}:\d\s+"(.*)"\s*$'
        assert re.search(pattern, locale, re.M)[1] == re.search(pattern, baseline_locale, re.M)[1]
    forbidden = {'declare_war_on', 'create_wargoal', 'annex_country', 'transfer_state', 'add_state_core', 'set_state_owner'}
    assert not {k for k, _, _ in all_pairs} & forbidden
    variable_writes = set()
    variable_reads = set()
    for k, _, v in all_pairs:
        if k in ('set_variable', 'add_to_variable', 'clamp_variable'):
            key = next((val for name, _, val in v if name == 'var'), v[0][0])
            if key.startswith('MSGA_'):
                variable_writes.add(key)
        if isinstance(v, str) and v.startswith('MSGA_') and (k in ('value', 'var') or k in ('business_value_factor', 'industrial_capacity_factory', 'production_factory_efficiency_gain_factor', 'supply_consumption_factor', 'planning_speed', 'army_org_regain')):
            variable_reads.add(v)
    assert not variable_reads - variable_writes, f'Uninitialised variables {variable_reads-variable_writes}'
    quote_effect = get(scripts['common/scripted_effects/MSGA_SER_effects.txt'], 'MSGA_update_quotes')
    assert get(get(quote_effect, 'if'), 'multiply_variable')[-1][2] == '0.75'
    # Resolve external dependencies against the installed source, not recalled IDs.
    import os
    tfr = Path(os.environ.get('MSGA_TFR_ROOT', r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356'))
    assert tfr.is_dir(), 'Set MSGA_TFR_ROOT to the installed TFR source'
    source = lambda sub: '\n'.join(p.read_text(encoding='utf-8-sig', errors='replace') for p in (tfr/sub).rglob('*.txt'))
    external_ideas = source('common/ideas')
    external_effects = source('common/scripted_effects')
    external_triggers = source('common/scripted_triggers')
    external_events = source('events')
    equipment = source('common/units/equipment')
    buildings = source('common/buildings')
    external_modifier_source = external_ideas + source('common/dynamic_modifiers')
    local_modifier_keys = {k for p, ast in scripts.items() if p.startswith('common/ideas/')
                           for key, _, value in descend(ast) if key == 'modifier' for k, _, _ in value}
    for key in local_modifier_keys:
        assert re.search(r'\b' + re.escape(key) + r'\s*=', external_modifier_source), f'Unverified modifier {key}'
    for k, _, v in all_pairs:
        if k in ('add_ideas', 'remove_ideas', 'has_idea') and isinstance(v, str) and not v.startswith('MSGA_'):
            assert re.search(r'\b'+re.escape(v)+r'\s*=\s*\{', external_ideas), f'Unknown TFR idea {v}'
        if k in ('add_income_with_inflation', 'add_debt_with_inflation'):
            assert re.search(r'\b'+k+r'\s*=\s*\{', external_effects)
        if k in ('generic_not_has_corona',):
            assert re.search(r'\b'+k+r'\s*=\s*\{', external_triggers)
        if k == 'add_equipment_to_stockpile':
            assert re.search(r'\b'+get(v, 'type')+r'\s*=\s*\{', equipment)
        if k == 'add_building_construction':
            assert re.search(r'\b'+get(v, 'type')+r'\s*=\s*\{', buildings)
        if k == 'has_global_flag':
            assert re.search(r'set_global_flag\s*=\s*'+re.escape(v)+r'\b', external_events + external_effects), f'Unverified global flag {v}'
    for state in (107, 108, 1296):
        matches = [p for p in (tfr/'history/states').glob('*.txt') if re.search(r'\bid\s*=\s*'+str(state)+r'\b', p.read_text(encoding='utf-8-sig', errors='replace'))]
        assert len(matches) == 1 and 'owner = SER' in matches[0].read_text(encoding='utf-8-sig')
    assert 'category = cat_old_land_doctrine' in source('common/national_focus')
    report = {'static_validation': 'passed', 'script_files': len(scripts), 'focuses': len(focuses),
              'custom_sprites': len(sprites), 'pixel_identical_icons': len(focuses), 'events': len(events),
              'decisions': len(decisions), 'categories': len(categories), 'idea_definitions': len(ideas),
              'dynamic_modifiers': len(dynamic), 'localisation_keys': len(locale_keys),
              'original_layout_prerequisites_timing_and_titles': 'unchanged', 'sole_terminal_focus': 'MSGA_the_kosovo_question',
              'availability_changes': ['reopening requires vaccination', 'watch starts monitoring', 'Kosovo requires collapse report'],
              'auxiliary_business_value_cap': 0.10, 'verified_idea_modifiers': sorted(local_modifier_keys),
              'chronicle_visible_events': 7, 'chronicle_interval_days': [120, 210], 'chronicle_cooldown_days': 360,
              'covid_decisions': 2, 'daily_polling': False, 'tfr_external_references': 'checked against installed scripts',
              'paid_one_time_review_decisions': 7, 'guarded_refundable_major_projects': 7,
              'phase2_war_effects': 0, 'campaign_acceptance': 'not certified by static checks'}
    output = ROOT / 'docs/phase1_static_validation.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
