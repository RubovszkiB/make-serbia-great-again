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
    topology_keys = {'id', 'x', 'y', 'cost', 'prerequisite', 'available', 'cancel_if_invalid'}
    topology = lambda fs: [[item for item in f if item[0] in topology_keys] for f in fs]
    assert topology(focuses) == topology(baseline), 'Focus topology or timing changed'
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
    event_ast = scripts['events/MSGA_SER_events.txt']
    assert get(event_ast, 'add_namespace') == 'MSGA'
    events = [get(v, 'id') for k, _, v in event_ast if k == 'country_event']
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
    capstone = get(next(f for f in focuses if get(f, 'id') == 'MSGA_serbian_recovery'), 'completion_reward')
    assert get(get(capstone, 'add_to_variable'), 'MSGA_business_bonus') == '0.03'
    final_army = get(next(f for f in focuses if get(f, 'id') == 'MSGA_ready_for_the_uncertain'), 'completion_reward')
    assert get(get(final_army, 'set_variable'), 'MSGA_defence_planning') == '0.10'
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
    required += [v for k, _, v in all_pairs if k in ('custom_effect_tooltip', 'title', 'desc', 'name') and isinstance(v, str) and v.startswith('MSGA')]
    assert not set(required) - set(locale_keys), f'Missing localisation {set(required) - set(locale_keys)}'
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
    report = {'static_validation': 'passed', 'script_files': len(scripts), 'focuses': len(focuses),
              'custom_sprites': len(sprites), 'pixel_identical_icons': len(focuses), 'events': len(events),
              'decisions': len(decisions), 'categories': len(categories), 'idea_definitions': len(ideas),
              'dynamic_modifiers': len(dynamic), 'localisation_keys': len(locale_keys),
              'original_topology_and_titles': 'unchanged', 'sole_terminal_focus': 'MSGA_the_kosovo_question',
              'business_value_cap': 0.10, 'military_final_planning': 0.10,
              'paid_one_time_review_decisions': 7, 'guarded_refundable_major_projects': 7,
              'phase2_war_effects': 0, 'campaign_acceptance': 'not certified by static checks'}
    output = ROOT / 'docs/phase1_static_validation.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
