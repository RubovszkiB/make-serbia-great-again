"""Targeted static and script-flow checks; these do not replace HOI4 gameplay testing."""
from pathlib import Path
import argparse, json, re
from validate_phase1 import parse, get, descend, unique, ROOT, early_unlocks


class CampaignModel:
    """Execute the campaign's small documented effect subset against a test world.

    The model checks ordering and guard logic in the actual parsed scripts.
    It does not simulate combat, engine peace conferences, saves or rendering.
    """
    def __init__(self, scripts):
        self.effects = dict((k, v) for k, _, v in scripts['common/scripted_effects/MSGA_SER_effects.txt'])
        self.flags = {c: set() for c in ['SER', 'KOS', 'ALB', 'USA', 'GER']}
        self.ideas = {c: set() for c in self.flags}
        self.factions = {'USA': 'NATO', 'ALB': 'NATO', 'GER': 'NATO', 'SER': None, 'KOS': None}
        self.guarantees = {('USA', 'KOS'), ('GER', 'ALB'), ('USA', 'SER')}
        self.exists = set(self.flags)
        self.wars = set()
        self.states = {785: 'KOS', 1305: 'KOS'}
        self.controllers = self.states.copy()
        self.modifiers = {s: set() for s in self.states}
        self.capitulated = set()
        self.pristina = 'KOS'
        self.focuses = set()
        self.events = []
        self.trace = []
        self.tree = 'MSGA_SER_phase1'
        self.money = 10
        self.command_power = 100
        self.temp = 0

    def condition(self, ast, scope='SER'):
        def item(k, op, v):
            if k in self.flags: return self.condition(v, k)
            if k.isdigit(): return self.condition(v, int(k))
            if k == 'OR': return any(item(a, b, c) for a, b, c in v)
            if k == 'AND': return self.condition(v, scope)
            if k == 'NOT': return not any(item(a, b, c) for a, b, c in v)
            if k == 'always': return v == 'yes'
            if k == 'country_exists': return v in self.exists
            if k == 'exists':
                assert v in ('yes', 'no'), 'exists accepts a boolean, not a country tag'
                return (scope in self.exists) == (v == 'yes')
            if k == 'has_country_flag': return v in self.flags[scope]
            if k == 'has_war_with': return frozenset((scope, v)) in self.wars
            if k == 'has_capitulated': return (scope in self.capitulated) == (v == 'yes')
            if k == 'controls_province': return v == '14402' and self.pristina == scope
            if k == 'is_owned_by': return self.states[scope] == v
            if k == 'is_fully_controlled_by': return self.controllers[scope] == v
            if k == 'has_guaranteed': return (scope, v) in self.guarantees
            if k == 'is_in_faction': return bool(self.factions[scope]) == (v == 'yes')
            if k == 'is_faction_leader': return scope == 'USA'
            if k == 'is_in_faction_with': return self.factions[scope] is not None and self.factions[scope] == self.factions[v]
            if k == 'has_dynamic_modifier': return get(v, 'modifier') in self.modifiers[scope]
            if k == 'check_variable': return self.money >= float(get(v, 'value'))
            if k == 'command_power': return self.command_power > float(v)
            raise AssertionError('Unmodelled campaign trigger: ' + k)
        return all(item(k, op, v) for k, op, v in ast)

    def execute(self, ast, scope='SER'):
        branch_taken = False
        for k, _, v in ast:
            if k in ('if', 'else_if', 'else'):
                if k == 'if': branch_taken = False
                if not branch_taken and (k == 'else' or self.condition(get(v, 'limit'), scope)):
                    self.execute([p for p in v if p[0] != 'limit'], scope)
                    branch_taken = True
                continue
            if k in self.flags: self.execute(v, k)
            elif k.isdigit(): self.execute(v, int(k))
            elif k in self.effects: self.execute(self.effects[k], scope)
            elif k == 'every_other_country':
                for country in self.flags:
                    if country != scope and self.condition(next((x for a, _, x in v if a == 'limit'), []), country):
                        self.execute([p for p in v if p[0] != 'limit'], country)
            elif k == 'set_country_flag': self.flags[scope].add(v)
            elif k == 'clr_country_flag': self.flags[scope].discard(v)
            elif k == 'add_ideas': self.ideas[scope].add(v)
            elif k == 'remove_ideas': self.ideas[scope].discard(v)
            elif k == 'add_dynamic_modifier': self.modifiers[scope].add(get(v, 'modifier'))
            elif k == 'remove_dynamic_modifier': self.modifiers[scope].discard(get(v, 'modifier'))
            elif k == 'remove_from_faction':
                self.factions[v] = None
                self.trace.append(('leave_faction', v))
            elif k == 'diplomatic_relation':
                pair = (scope, get(v, 'country'))
                if get(v, 'active') == 'no': self.guarantees.discard(pair)
                else: self.guarantees.add(pair)
            elif k == 'declare_war_on':
                target = get(v, 'target')
                self.wars.add(frozenset((scope, target)))
                assert self.factions[scope] is None and self.factions[target] is None
                assert not any(t == target for _, t in self.guarantees), 'Defensive guarantee still active'
                self.trace.append(('declare', scope, target))
            elif k == 'annex_country':
                assert get(v, 'target') == 'KOS', 'Wrong annexation target'
                self.exists.discard('KOS')
                self.wars = {w for w in self.wars if 'KOS' not in w}
                self.trace.append(('annex', 'KOS'))
            elif k == 'transfer_state':
                self.states[int(v)] = self.controllers[int(v)] = scope
                self.trace.append(('transfer', int(v)))
            elif k == 'white_peace':
                assert v == 'ALB'
                self.wars.discard(frozenset((scope, v)))
                self.trace.append(('peace', v))
            elif k == 'complete_national_focus': self.focuses.add(v); self.trace.append(('complete', v))
            elif k == 'load_focus_tree': self.tree = get(v, 'tree')
            elif k == 'country_event': self.events.append((scope, get(v, 'id')))
            elif k == 'set_temp_variable': self.temp = float(get(v, 'value'))
            elif k == 'add_income': self.money += self.temp
            elif k == 'add_command_power': self.command_power += float(v)
            elif k in ('remove_from_array', 'add_war_support', 'add_stability', 'army_experience'): pass
            else: raise AssertionError('Unmodelled campaign effect: ' + k)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--mod-root', type=Path, default=ROOT/'make_serbia_great_again')
    cli.add_argument('--report', type=Path, default=ROOT/'docs/kosovo_validation.json')
    args = cli.parse_args(); mod = args.mod_root.resolve()
    scripts = {p.relative_to(mod).as_posix(): parse(p.read_text(encoding='utf-8-sig')) for p in mod.rglob('*') if p.suffix in ('.txt', '.gfx')}
    trees = {get(v, 'id'): v for p, ast in scripts.items() if p.startswith('common/national_focus/') for k, _, v in ast if k == 'focus_tree'}
    assert set(trees) == {'MSGA_SER_phase1', 'MSGA_SER_kosovo_war', 'MSGA_SER_post_kosovo'}
    focuses = {get(v, 'id'): v for tree in trees.values() for k, _, v in tree if k == 'focus'}
    all_focus_ids = [get(v, 'id') for tree in trees.values() for k, _, v in tree if k == 'focus']
    unique(all_focus_ids, 'All chapter focus IDs'); assert len(all_focus_ids) == 29
    war = [get(v, 'id') for k, _, v in trees['MSGA_SER_kosovo_war'] if k == 'focus']
    assert war == ['MSGA_plan_the_attack', 'MSGA_prepare_southern_command', 'MSGA_operation_return', 'MSGA_kosovo_has_been_retaken']
    for i, id in enumerate(war):
        assert get(focuses[id], 'cost') == '1'
        if i: assert get(get(focuses[id], 'prerequisite'), 'focus') == war[i-1]
    assert get(focuses[war[-1]], 'available') == parse('always = no')
    effects = scripts['common/scripted_effects/MSGA_SER_effects.txt']
    assert ('MSGA_enter_kosovo_chapter', '=', 'yes') in get(focuses['MSGA_the_kosovo_question'], 'completion_reward')
    assert get(get(get(effects, 'MSGA_enter_kosovo_chapter'), 'if'), 'load_focus_tree') == parse('tree = MSGA_SER_kosovo_war keep_completed = yes')
    penalty = get(scripts['common/dynamic_modifiers/MSGA_SER_dynamic_modifiers.txt'], 'MSGA_unprepared_sector')
    assert get(penalty, 'attacker_modifier') == 'yes'
    assert get(penalty, 'army_attack_factor') == '-0.30' and get(penalty, 'army_speed_factor') == '-0.10'
    decisions = scripts['common/decisions/MSGA_SER_kosovo_operations.txt'][0][2]
    for state in (785, 1305):
        body = get(decisions, 'MSGA_prepare_offensive_'+str(state))
        assert get(body, 'days_remove') == '14' and get(body, 'cost') == '0'
        assert get(body, 'complete_effect') == parse('add_command_power = -25')
        assert ('remove_dynamic_modifier', '=', parse('modifier = MSGA_unprepared_sector')) in descend(get(body, 'remove_effect'))
        assert not any(k == 'remove_dynamic_modifier' for k, _, _ in descend(get(body, 'complete_effect')))
    event_bodies = {get(v, 'id'): v for k, _, v in scripts['events/MSGA_SER_kosovo_events.txt'] if k == 'country_event'}
    assert {f'MSGA_kosovo.{i}' for i in range(1, 13)} <= set(event_bodies)
    for i in (10, 11): assert not any(k in ('annex_country', 'white_peace') for k, _, _ in descend(get(event_bodies[f'MSGA_kosovo.{i}'], 'option')))
    new_sprites = [v for k, _, v in descend(scripts['interface/MSGA_kosovo_assets.gfx']) if k == 'SpriteType']
    names = {get(v, 'name').strip('"') for v in new_sprites}
    for id in war: assert 'GFX_goal_'+id in names and 'GFX_goal_'+id+'_shine' in names
    for body in event_bodies.values():
        if any(k == 'picture' for k, _, _ in body): assert get(body, 'picture') in names
    locale = (mod/'localisation/english/MSGA_l_english.yml').read_text(encoding='utf-8-sig')
    for id in all_focus_ids: assert re.search(r'^ '+id+r'_desc:0 ', locale, re.M)
    declarations = [v for ast in scripts.values() for k, _, v in descend(ast) if k == 'declare_war_on']
    assert sorted(get(v, 'target') for v in declarations) == ['KOS', 'SER']
    annexations = [v for ast in scripts.values() for k, _, v in descend(ast) if k == 'annex_country']
    assert len(annexations) == 1 and get(annexations[0], 'target') == 'KOS'
    transfers = [v for ast in scripts.values() for k, _, v in descend(ast) if k == 'transfer_state']
    assert sorted(transfers) == ['1305', '785']
    tfr = Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3350890356')
    for state, province in [(785,14402),(1305,14400)]:
        p = next((tfr/'history/states').glob(str(state)+'-*'))
        text = p.read_text(encoding='utf-8-sig'); assert 'owner = KOS' in text and str(province) in text
    game = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV')
    docs = (game/'documentation/effects_documentation.md').read_text()
    trigger_docs = (game/'documentation/triggers_documentation.md').read_text()
    assert '## country_exists' in trigger_docs
    for ast in scripts.values():
        for k, _, v in descend(ast):
            if k == 'exists': assert v in ('yes', 'no')
    assert '## load_focus_tree' in docs and 'keep_completed' in docs and '## white_peace' in docs

    # Successful campaign, independent intervention, immediate resolution, duplicate guards.
    model = CampaignModel(scripts)
    model.execute(parse('MSGA_enter_kosovo_chapter = yes'))
    assert model.tree == 'MSGA_SER_kosovo_war'
    model.execute(parse('MSGA_start_kosovo_war = yes'))
    # Paying for one sector cannot remove either penalty before the timed callback,
    # and completing that callback must not prepare the other sector.
    prep = get(decisions, 'MSGA_prepare_offensive_785')
    assert model.condition(get(prep, 'custom_cost_trigger'))
    model.execute(get(prep, 'complete_effect'))
    assert model.command_power == 75 and all(model.modifiers.values())
    model.execute(get(prep, 'remove_effect'))
    assert not model.modifiers[785] and model.modifiers[1305]
    model.command_power = 24
    assert not model.condition(get(prep, 'custom_cost_trigger'))
    model.pristina = 'SER'; model.execute(parse('MSGA_check_pristina = yes'))
    assert model.factions['ALB'] is None and ('ALB', 'MSGA_kosovo.20') in model.events
    model.execute(get(event_bodies['MSGA_kosovo.20'], 'immediate'), 'ALB')
    assert model.trace.index(('leave_faction','ALB')) < model.trace.index(('declare','ALB','SER'))
    model.wars.add(frozenset(('SER','GER')))  # Unrelated war must survive peace.
    model.capitulated.add('KOS'); model.execute(parse('MSGA_resolve_kosovo_war = yes'))
    assert model.states == {785:'SER',1305:'SER'} and model.controllers == model.states
    assert frozenset(('SER','ALB')) not in model.wars and frozenset(('SER','GER')) in model.wars
    assert all(not x for x in model.modifiers.values()) and 'MSGA_kosovo_war_active' not in model.flags['SER']
    assert war[-1] in model.focuses
    before = (len(model.trace),len(model.events)); model.execute(parse('MSGA_resolve_kosovo_war = yes MSGA_check_pristina = yes'))
    assert before == (len(model.trace),len(model.events))
    model.execute(get(event_bodies['MSGA_kosovo.12'],'immediate')); assert model.tree == 'MSGA_SER_post_kosovo'
    # Ownership gate must require BOTH states and cannot replay a victory event.
    for owned in [[],[785],[1305],[785,1305]]:
        check = CampaignModel(scripts);check.flags['SER'].add('MSGA_kosovo_resolution_done')
        for state in owned: check.states[state]=check.controllers[state]='SER'
        check.execute(parse('MSGA_validate_kosovo_victory = yes'))
        assert (war[-1] in check.focuses) == (len(owned)==2)
    # The already-declared intervention event must become harmless after resolution.
    before = model.wars.copy();model.execute(get(event_bodies['MSGA_kosovo.20'],'immediate'),'ALB');assert before == model.wars
    # Treasury costs execute native nominal money effects, preserving timed delivery.
    militia = scripts['common/decisions/MSGA_SER_expansion.txt'][1][2]
    for name in ['scorpions','white_eagles','serbian_guard']:
        body = get(militia,'MSGA_raise_'+name)
        assert get(body,'cost')=='0' and model.condition(get(body,'custom_cost_trigger'))
        balance=model.money;model.execute(get(body,'complete_effect'));assert model.money==balance-2
    reserve = get(get(scripts['common/decisions/MSGA_SER_phase1.txt'],'MSGA_rearmament'),'MSGA_procure_equipment')
    balance=model.money;model.execute(get(reserve,'complete_effect'));assert model.money==balance-3
    report={'static_validation':'passed','validated_mod_root':str(mod),'focus_trees':list(trees),'total_focuses':len(all_focus_ids),'war_focus_days':[7,7,7], 'kosovo_states':[785,1305],'pristina_province':14402,'sector_attack_penalty':-0.30,'sector_movement_penalty':-0.10,'offensive_preparation_days':14,'offensive_preparation_CP':25,'militia_treasury_B':2,'reserve_treasury_B':3,'political_power_cost':0,'visible_campaign_events':14,'script_flow_model':'passed: ordering, ownership gates, cleanup, idempotency, pending intervention cancellation, unrelated-war preservation, treasury deductions','gameplay_test':'not certified by static checks or the model'}
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__ == '__main__': main()
