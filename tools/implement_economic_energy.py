"""Generate additive Serbian decisions using inspected, installed TFR APIs."""
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageOps
import argparse, hashlib, io, json, struct, shutil
from validate_phase1 import ROOT, parse, get
from validate_bosnia import TFR, GAME

MOD = ROOT / 'make_serbia_great_again'
LIVE = Path(r'C:\Users\Balazs\Documents\Paradox Interactive\Hearts of Iron IV\mod\make_serbia_great_again')
PACK = Path(r'C:\Users\Balazs\Downloads\MSGA_Economic_Energy_Visuals.zip')
CATEGORIES = ['MSGA_serbian_economic_cooperation', 'MSGA_serbian_energy_development']
PREFIX = 'MSGA_'
PROJECTS = []
PROGRAMMES = []
REFRESH = False
REFRESH_TEXT = {'common/decisions/MSGA_economic_energy_decisions.txt',
                'common/scripted_effects/MSGA_economic_energy_effects.txt',
                'common/scripted_triggers/MSGA_economic_energy_triggers.txt'}

def project(stem, title, state, cash, days, reward, text, crop, *, group='domestic', energy=False, requires=None, technology=None, event=None, industrial=0.025, academic=0):
    PROJECTS.append(dict(stem=stem, title=title, state=state, cash=cash, days=days, reward=reward, text=text, crop=crop,
                         group=group, energy=energy, requires=requires, technology=technology, event=event,
                         industrial=industrial, academic=academic, pp=50 if stem=='seek_russian_nuclear_expertise' else 0))

def programme(stem, title, modifiers, text, crop, *, group='domestic', energy=False, requires=None, pp=0):
    PROGRAMMES.append(dict(stem=stem, title=title, modifiers=modifiers, text=text, crop=crop, group=group,
                           energy=energy, requires=requires, pp=pp, cash=0 if pp else .2))

# Crops contain only individual illustrated motifs, not board labels/costs.
D = [(28, y, 202, y+80) for y in [264,365,467,569,670,774,878]]
C = [(540,y,713,y+82) for y in [263,364,466,568]]
R = [(540,y,713,y+79) for y in [731,815,899]]
E = [(1045,y,1203,y+83) for y in [262,364,466,568]]
ED = [(28,y,180,y+99) for y in [282,407,529,652]]
EC = [(540,y,688,y+99) for y in [286,407,524,636,751,865]]
ER = [(1050,y,1209,y+99) for y in [284,406,525,646,766,880]]

project('expand_bor_mining_complex','Expand the Bor Mining Complex',108,.5,120,'mining',
        '+3 Steel, +2 Tungsten; +1 Infrastructure below level 5 (otherwise +1 shared building slot); Industrial Development +0.05.',D[5],event='MSGA_econ.3',industrial=.05)
project('develop_jadar_mining_project','Develop the Jadar Mining Project',1296,.5,120,'jadar',
        '+3 Steel, +2 Tungsten, +1 shared building slot and Industrial Development +0.05.',D[5],industrial=.05)
project('serbian_mineral_processing_expansion','Serbian Mineral Processing Expansion',1296,.5,120,'civilian',
        '+1 Civilian Factory and +1 shared building slot; Industrial Development +0.03.',D[4],industrial=.03)
project('central_serbian_industrial_park','Central Serbian Industrial Park',1296,.5,90,'civilian',
        '+1 Civilian Factory and +1 shared building slot around Kragujevac; Industrial Development +0.03.',D[1],industrial=.03)
project('southern_serbian_industrial_development','Southern Serbian Industrial Development',108,.5,90,'slot',
        '+1 shared building slot and Industrial Development +0.03 around Nis. Complements the earlier southern factory investment.',D[0],industrial=.03)
project('morava_logistics_development','Serbian Logistics and Morava Development',1296,.4,120,'logistics',
        '+1 Infrastructure and +1 shared building slot; Industrial Development +0.025. Requires room below the native infrastructure cap of 5.',D[2],event='MSGA_econ.2')

programme('industrial_efficiency_programme','Industrial Efficiency Programme',{'production_factory_efficiency_gain_factor':.075,'industrial_capacity_factory':.025},
          'Production Efficiency Growth +7.5%; Factory Output +2.5%.',D[6])
programme('subsidise_serbian_manufacturers','Subsidise Serbian Manufacturers',{'industrial_capacity_factory':.05},'Factory Output +5%.',D[4])
programme('infrastructure_investment_programme','Infrastructure Investment Programme',{'production_speed_buildings_factor':.05,'production_speed_infrastructure_factor':.10},
          'Construction Speed +5%; Infrastructure Construction Speed +10%.',D[2])
programme('support_serbian_businesses','Support Serbian Businesses',{'business_value_factor':.04,'income_growth_factor':.005},'Business Value +4%; native Income Growth +0.5%.',D[3])
programme('chinese_industrial_cooperation','Chinese Industrial Cooperation',{'industrial_capacity_factory':.05,'production_speed_industrial_complex_factor':.05},
          'Factory Output +5%; Civilian Factory Construction Speed +5%.',C[0],group='china')
programme('chinese_mining_expertise','Chinese Mining Expertise',{'local_resources_factor':.10,'industrial_development_monthly':.0025},
          'Resource Gain +10%; monthly Industrial Development +0.0025.',C[1],group='china')
programme('chinese_infrastructure_cooperation','Chinese Infrastructure Cooperation',{'production_speed_buildings_factor':.075,'production_speed_infrastructure_factor':.10},
          'Construction Speed +7.5%; Infrastructure Construction Speed +10%.',C[2],group='china')
programme('chinese_technology_transfer','Chinese Technology Transfer',{'research_speed_factor':.03,'industrial_development_monthly':.0025},
          'Research Speed +3%; monthly Industrial Development +0.0025.',C[3],group='china')
programme('russian_energy_cooperation','Russian Energy Cooperation',{'factory_energy_consumption':-.03,'industrial_capacity_factory':.03},
          'Factory Energy Consumption -3%; Factory Output +3%.',R[0],group='russia')
programme('russian_heavy_industry_cooperation','Russian Heavy Industry Cooperation',{'production_factory_efficiency_gain_factor':.05,'production_speed_arms_factory_factor':.05},
          'Production Efficiency Growth +5%; Military Factory Construction Speed +5%.',R[1],group='russia')
programme('russian_technological_assistance','Russian Technological Assistance',{'research_speed_factor':.02,'industrial_development_monthly':.0025},
          'Research Speed +2%; monthly Industrial Development +0.0025.',R[2],group='russia')
programme('european_development_grants','European Development Grants',{'business_value_factor':.025,'society_development_monthly':.002,'industrial_development_monthly':.002},
          'Business Value +2.5%; monthly Society and Industrial Development +0.002 each.',E[0],group='europe',pp=50)
programme('european_industrial_standards','European Industrial Standards',{'production_factory_efficiency_gain_factor':.05,'industrial_capacity_factory':.03},
          'Production Efficiency Growth +5%; Factory Output +3%.',E[1],group='europe')
programme('european_technology_partnership','European Technology Partnership',{'research_speed_factor':.03,'academic_development_monthly':.0025},
          'Research Speed +3%; monthly Academic Development +0.0025.',E[2],group='europe')
programme('european_business_cooperation','European Business Cooperation',{'business_value_factor':.05,'income_growth_factor':.005},
          'Business Value +5%; native Income Growth +0.5%.',E[3],group='europe')

project('modernise_serbian_power_grid','Modernise the Serbian Power Grid',107,.4,60,'grid',
        '+1 Infrastructure below level 5 (otherwise +1 shared building slot); Industrial Development +0.025. For 180 days: Construction Speed +5%, Power Plant and Infrastructure Construction Speed +10%.',ED[0],energy=True,event='MSGA_energy.1')
project('modernise_nikola_tesla_complex','Modernise the Nikola Tesla Complex',1296,.5,90,'power_plant',
        '+1 Power Plant and +1 shared building slot in the Obrenovac region; Industrial Development +0.025.',ED[1],energy=True)
project('expand_kostolac_energy_complex','Expand the Kostolac Energy Complex',108,.5,90,'power_plant',
        '+1 Power Plant and +1 shared building slot; Industrial Development +0.025. Native TFR rules make this incompatible with Bor renewable generation in Morava.',ED[2],energy=True)
project('upgrade_djerdap_power_system','Upgrade the Djerdap Power System',108,.4,75,'hydro',
        '+2 native Energy resource from existing hydroelectric generation; +1 Infrastructure below level 5 (otherwise +1 shared building slot); Industrial Development +0.025. No additional Energy Farm is granted.',ED[3],energy=True)
programme('chinese_renewable_technology_transfer','Chinese Renewable Technology Transfer',{'production_speed_energy_farm_factor':.125,'production_speed_buildings_factor':.03,'industrial_development_monthly':.0025},
          'Energy Farm Construction Speed +12.5%; Construction Speed +3%; monthly Industrial Development +0.0025.',EC[0],energy=True,group='china')
project('develop_bor_renewable_complex','Develop the Bor Renewable Energy Complex',108,.5,120,'energy_farm',
        '+1 Energy Farm and +1 shared building slot; Industrial Development +0.03. Native TFR rules make this incompatible with a Kostolac Power Plant in Morava.',EC[1],energy=True,group='china',event='MSGA_energy.2',industrial=.03)
project('expand_bor_renewable_complex','Expand the Bor Renewable Complex',108,.6,120,'energy_farm',
        '+1 additional Energy Farm and +1 shared building slot; Industrial Development +0.025. This is the final scripted Energy Farm.',EC[2],energy=True,group='china',requires='develop_bor_renewable_complex')
project('establish_serbian_solar_manufacturing','Establish Serbian Solar Manufacturing',45,.5,90,'civilian',
        '+1 Civilian Factory and +1 shared building slot in Vojvodina; Industrial Development +0.03. No Energy Farm is granted.',EC[3],energy=True,group='china',industrial=.03)
project('develop_grid_scale_storage','Develop Grid-Scale Energy Storage',107,.4,90,'storage',
        'Permanent Factory Energy Consumption -3%; Industrial Development +0.025. Uses native efficiency rather than a new storage currency.',EC[4],energy=True)
programme('renewable_energy_subsidies','Renewable Energy Subsidies',{'production_speed_energy_farm_factor':.15,'industrial_development_monthly':.0025},
          'Energy Farm Construction Speed +15%; monthly Industrial Development +0.0025.',EC[5],energy=True)
project('seek_russian_nuclear_expertise','Seek Russian Nuclear Expertise',None,.2,60,'expertise',
        'One 50% nuclear research bonus; Academic Development +0.05. Unlocks the nuclear programme and technical assistance; grants no reactor.',ER[0],energy=True,group='russia',event='MSGA_energy.3',industrial=0,academic=.05)
project('establish_serbian_nuclear_programme','Establish the Serbian Nuclear Programme',None,.5,120,'nuclear_programme',
        'One 50% nuclear research bonus; Academic Development +0.05; Research Speed +3% for 365 days. Unlocks workforce training; grants no reactor.',ER[1],energy=True,group='russia',requires='seek_russian_nuclear_expertise',industrial=0,academic=.05)
project('train_serbian_nuclear_workforce',"Train Serbia's Nuclear Workforce",None,.3,90,'workforce',
        'One 50% nuclear research bonus; Academic Development +0.05. Unlocks construction after native reactor technology is researched.',ER[2],energy=True,group='russia',requires='establish_serbian_nuclear_programme',industrial=0,academic=.05)
project('first_serbian_nuclear_power_plant',"Begin Construction of Serbia's First Nuclear Power Plant",45,1.5,180,'nuclear_reactor',
        '+1 Nuclear Reactor and +1 shared building slot in Vojvodina; Industrial Development +0.05. Requires $nuclear_reactors$ technology and no incompatible energy building.',ER[3],energy=True,group='russia',requires='train_serbian_nuclear_workforce',technology='nuclear_reactors',event='MSGA_energy.4',industrial=.05)
project('expand_serbian_nuclear_programme','Expand the Serbian Nuclear Programme',45,1.5,180,'nuclear_reactor',
        '+1 additional Nuclear Reactor and +1 shared building slot in Vojvodina; Industrial Development +0.025. Requires $nuclear_reactors2$ technology; this is the final scripted reactor.',ER[4],energy=True,group='russia',requires='first_serbian_nuclear_power_plant',technology='nuclear_reactors2')
programme('russian_nuclear_technical_assistance','Russian Nuclear Technical Assistance',{'production_speed_nuclear_reactor_factor':.125,'research_speed_factor':.02,'academic_development_monthly':.0025},
          'Nuclear Reactor Construction Speed +12.5%; Research Speed +2%; monthly Academic Development +0.0025.',ER[5],energy=True,group='russia',requires='seek_russian_nuclear_expertise')

EVENTS = [
 ('MSGA_econ.1','A New Economic Strategy for Serbia','infrastructure_strategy_meeting',
  'Belgrade has brought economic planners, manufacturers and infrastructure specialists around the same table. Recovery must now become a sustained programme of investment rather than a succession of emergency measures.\n\nDomestic projects and cooperation with China, Russia and European partners can strengthen production without placing the country inside a new political bloc. Each programme will be judged by its practical contribution to Serbia.', 'Build on the recovery.'),
 ('MSGA_econ.2','The Morava Corridor Takes Shape','highway_rail_renaissance',
  'New freight connections and improved road access are linking central Serbian workshops to suppliers and customers. The corridor is becoming an economic route as well as a transport project.\n\nIndustry can now plan around more reliable deliveries. Further investment will depend on productive use of these connections rather than another round of announcements.', 'Connect our economic centres.'),
 ('MSGA_econ.3','The Bor Expansion','mining_expansion',
  'The expanded Bor complex has begun turning investment into dependable industrial capacity. Improved access and modern equipment support extraction, while domestic firms prepare to process a larger share of the output.\n\nThe programme is measured in useful inputs for Serbian industry. Steel and tungsten production provide the campaign economy with a practical representation of that mineral investment.', 'Bring the investment into production.'),
 ('MSGA_econ.4','Serbian Industrial Revival','industrial_revival',
  'Several permanent projects have now moved beyond the planning stage. Industrial sites, mineral processing and transport investment are beginning to reinforce one another across Serbia.\n\nThe improvement is gradual, but visible. A stronger domestic production base gives the government more room to meet future challenges without relying on temporary economic measures alone.', 'The results are becoming visible.'),
 ('MSGA_energy.1',"Powering Serbia's Future",'energy_modernisation_briefing',
  'The first stage of grid modernisation has been completed. Engineers can now direct further work towards reliable supply, improved connections and the replacement of ageing equipment.\n\nTraditional generation, renewables and a possible civilian nuclear programme will each require careful investment. Modernisation begins with a network capable of supporting them.', 'Build a dependable power system.'),
 ('MSGA_energy.2','A Renewable Partnership with China','chinese_renewable_partnership',
  'Serbian and Chinese specialists have completed the opening stage of the Bor renewable project. The partnership combines equipment, engineering support and local work on generation and grid connections.\n\nIts purpose is practical: diversify supply and develop expertise that Serbian firms can use themselves. Additional capacity will follow the same measured investment process.', 'Diversify Serbian generation.'),
 ('MSGA_energy.3','The Nuclear Question','russian_nuclear_briefing',
  'Russian technical advisers have joined Serbian planners to examine a peaceful civilian nuclear programme. Their first task is to establish the expertise needed for licensing, research and long-term operation.\n\nAdvice alone cannot build a reactor. Serbia must organise a programme, train a workforce, research the required technology and commit substantial capital before construction can begin.', 'Prepare before we build.'),
 ('MSGA_energy.4','Serbia Enters the Nuclear Age','first_serbian_nuclear_plant',
  "Serbia's first civilian nuclear power plant has entered service. Years of preparation, technical training and concentrated investment have produced a new source of dependable generation.\n\nThe achievement brings lasting responsibilities for operation and maintenance. A second reactor remains a separate project, requiring additional funding and the appropriate native technology.", 'A new chapter in Serbian energy.')
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(folder): return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file()}
def write(path, text, bom=False):
    p=MOD/path; p.parent.mkdir(parents=True,exist_ok=True)
    text='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
    if REFRESH and path not in REFRESH_TEXT:
        assert p.read_text(encoding='utf-8-sig')==text,path
        return
    if p.exists() and not REFRESH: raise AssertionError('Additive file already exists: '+path)
    p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8',newline='\r\n')
def cash_test(amount):return f'check_variable = {{ var = income_var value = {amount:g} compare = greater_than_or_equals }}'
def charge(amount):return f'set_temp_variable = {{ var = income_var_temp value = {-amount:g} }} add_income = yes'
def refund(amount):return f'set_temp_variable = {{ var = income_var_temp value = {amount:g} }} add_income = yes'
def partner(group):
    return {'domestic':'','china':'PRC = { exists = yes NOT = { has_war_with = SER } }',
            'russia':'SOV = { exists = yes NOT = { has_war_with = SER } }',
            'europe':'OR = { GER = { exists = yes NOT = { has_war_with = SER } } ITA = { exists = yes NOT = { has_war_with = SER } } HUN = { exists = yes NOT = { has_war_with = SER } } }'}[group]
def debug(stem, message):return f'log = "[MSGA ECON] MSGA_{stem} {message}"'
def infra(stem, state):return 'if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } '+debug(stem,f'granted infrastructure in state {state}')+' } else = { add_extra_state_shared_building_slots = 1 '+debug(stem,f'infrastructure capped; granted shared slot in state {state}')+' }'

def decision_crop(p):
    # Tight foreground motifs from the supplied boards; do not reuse these
    # crops for spirits, categories or event pictures.
    crops = {
      tuple(D[0]):(113,270,199,346), tuple(D[1]):(111,372,200,450),
      tuple(D[2]):(107,474,200,553), tuple(D[3]):(108,576,199,652),
      tuple(D[4]):(105,677,200,756), tuple(D[5]):(98,779,200,865),
      tuple(D[6]):(106,883,200,971),
      tuple(C[0]):(625,265,714,345), tuple(C[1]):(620,368,714,449),
      tuple(C[2]):(600,471,705,547), tuple(C[3]):(620,570,714,648),
      tuple(R[0]):(614,733,714,813), tuple(R[1]):(615,819,714,898),
      tuple(R[2]):(615,902,714,984),
      tuple(E[0]):(1101,265,1206,346), tuple(E[1]):(1103,364,1206,446),
      tuple(E[2]):(1103,468,1206,549), tuple(E[3]):(1103,570,1206,650),
      tuple(ED[0]):(93,295,182,385), tuple(ED[1]):(88,421,182,505),
      tuple(ED[2]):(88,539,182,627), tuple(ED[3]):(88,664,182,751),
      tuple(EC[0]):(568,309,658,374), tuple(EC[1]):(592,415,681,503),
      tuple(EC[2]):(592,533,681,623), tuple(EC[3]):(583,654,681,731),
      tuple(EC[4]):(587,762,681,847), tuple(EC[5]):(583,887,681,970),
      tuple(ER[0]):(1095,311,1183,376), tuple(ER[1]):(1111,420,1208,505),
      tuple(ER[2]):(1109,539,1208,626), tuple(ER[3]):(1109,664,1208,752),
      tuple(ER[4]):(1109,787,1208,873), tuple(ER[5]):(1131,913,1208,984),
    }
    return crops[tuple(p['crop'])]

def decision_image(im):
    # Fit the complete selected foreground object inside a two-pixel margin.
    # Contain preserves aspect ratio and avoids chopping off the emblem.
    result=Image.new('RGBA',(52,45),(19,27,31,255))
    motif=ImageOps.contain(im,(48,41),method=Image.Resampling.LANCZOS).convert('RGBA')
    result.paste(motif,((52-motif.width)//2,(45-motif.height)//2))
    return result
def development(p):
    return ''.join(f' set_temp_variable = {{ var = {name}_development_var_temp value = {p[name]:g} }} add_{name}_development = yes' for name in ['industrial','academic'] if p[name])
def event_effect(id):return 'MSGA_milestone_'+id.replace('MSGA_','').replace('.','_')

def main():
    global MOD, REFRESH
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--refresh-projects-and-icons',action='store_true')
    REFRESH=cli.parse_args().refresh_projects_and_icons
    baseline=inventory(LIVE);assert baseline==inventory(MOD)
    prior=json.loads((ROOT/'docs/economic_energy_sources.json').read_text()) if REFRESH else None
    if REFRESH:
        backup=ROOT/'logs/economic_energy_bugfix_backup';backup.mkdir(parents=True,exist_ok=True)
        if not (backup/'before_sha256.json').exists():(backup/'before_sha256.json').write_text(json.dumps(baseline,indent=2)+'\n')
        for path in REFRESH_TEXT|{p for p in prior['assets'] if p.startswith('gfx/interface/decisions/') and prior['assets'][p]['size']==[52,45]}:
            dest=backup/path;dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():shutil.copyfile(LIVE/path,dest)
        MOD=LIVE  # Commit runtime changes first, then mirror only these paths.
    native_buildings=get(parse((TFR/'common/buildings/TFR_buildings.txt').read_text()),'buildings')
    assert get(get(native_buildings,'infrastructure'),'level_cap')==parse('state_max = 5')
    owners={}; histories={}
    state_files=[TFR/p for p in prior['starting_serbia_states'].values()] if REFRESH else (TFR/'history/states').glob('*.txt')
    for p in state_files:
        a=get(parse(p.read_text(encoding='utf-8-sig',errors='replace')),'state');h=get(a,'history')
        values=[v for k,o,v in h if k=='owner']
        if values and values[-1]=='SER': owners[int(get(a,'id'))]=p.relative_to(TFR).as_posix();histories[int(get(a,'id'))]=h
    assert set(owners)=={45,107,108,1296},owners
    loc={}
    def l(k,v):assert k not in loc,k;loc[k]=v
    l(CATEGORIES[0],'Serbian Economic Cooperation');l(CATEGORIES[1],'Serbian Energy Development')
    l(CATEGORIES[0]+'_desc','Permanent investment in original Serbian territory and measured cooperation with domestic, Chinese, Russian and European industry. Optional development programmes remain available throughout the campaign.')
    l(CATEGORIES[1]+'_desc','Modernise the Serbian grid, develop renewable generation with China and prepare a civilian nuclear programme with Russian technical support. Native TFR energy buildings remain mutually exclusive within each state.')
    l('MSGA_development_repeatable_tt','Effect lasts 180 days. The programme may be renewed 70 days after the effect expires. It cannot stack with itself.')
    l('MSGA_development_state_free_tt','No other MSGA development project is running in the target state.')
    l('MSGA_development_cancel_tt','If the target is lost or its native building capacity becomes incompatible, the project is cancelled and its Treasury and PP costs are returned. A cancelled project may be restarted.')
    triggers=['MSGA_development_starting_serbia_state = { OR = { state = 45 state = 107 state = 108 state = 1296 } }',
              'MSGA_development_unlocked = { tag = SER OR = { has_country_flag = MSGA_economic_energy_unlocked has_completed_focus = MSGA_serbian_recovery has_country_flag = MSGA_completed_serbian_recovery } }']
    categories=[]
    for i,c in enumerate(CATEGORIES):categories.append(f'{c} = {{ icon = GFX_decision_category_MSGA_development_{i} allowed = {{ tag = SER }} visible = {{ MSGA_development_unlocked = yes }} visible_when_empty = yes priority = {14-i} }}')
    effects=['MSGA_unlock_economic_energy = { if = { limit = { MSGA_development_unlocked = yes } set_country_flag = MSGA_economic_energy_unlocked '+event_effect('MSGA_econ.1')+' = yes } }']
    # Derive the narrative threshold from actual completed investments; no currency/meter.
    count='MSGA_check_industrial_revival = { set_variable = { var = MSGA_permanent_economic_projects value = 0 } '
    for p in PROJECTS:
        if not p['energy']:count+=f'if = {{ limit = {{ has_country_flag = MSGA_done_{p["stem"]} }} add_to_variable = {{ var = MSGA_permanent_economic_projects value = 1 }} }} '
    count+=f'if = {{ limit = {{ check_variable = {{ var = MSGA_permanent_economic_projects value = 3 compare = greater_than_or_equals }} }} {event_effect("MSGA_econ.4")} = yes }} }}';effects.append(count)
    decisions={c:[] for c in CATEGORIES}
    asset_records={};sprites=[]
    extra_ideas={'MSGA_grid_modernisation_bonus':({'production_speed_buildings_factor':.05,'production_speed_power_plant_factor':.10,'production_speed_infrastructure_factor':.10},ED[0],True),
                 'MSGA_nuclear_programme_research':({'research_speed_factor':.03},ER[1],True),
                 'MSGA_grid_scale_storage_network':({'factory_energy_consumption':-.03},EC[4],True)}
    l('MSGA_grid_modernisation_bonus','Serbian Grid Modernisation');l('MSGA_nuclear_programme_research','Serbian Nuclear Research Programme');l('MSGA_grid_scale_storage_network','Serbian Grid-Scale Storage')
    for p in PROJECTS:
        stem=p['stem'];id='MSGA_'+stem;pending='MSGA_pending_'+stem;done='MSGA_done_'+stem;eligible='MSGA_eligible_'+stem
        state=p['state'];reward=p['reward'];rules='tag = SER'
        if p['requires']:rules+=' has_country_flag = MSGA_done_'+p['requires']
        if p['technology']:rules+=' has_tech = '+p['technology']
        state_effect='';state_rules=''
        if state:
            state_rules='MSGA_development_starting_serbia_state = yes is_owned_by = SER is_fully_controlled_by = SER'
            if reward=='logistics':state_rules+=' infrastructure < 5'
            if reward=='civilian':state_rules+=' industrial_complex < 20'
            if reward in ['power_plant','energy_farm','nuclear_reactor']:
                limit=2 if reward=='nuclear_reactor' else 4
                state_rules+=f' {reward} < {limit} '
                state_rules+=' '.join(f'{b} < 1' for b in ['power_plant','energy_farm','nuclear_reactor'] if b!=reward)
            rules+=f' {state} = {{ {state_rules} }}'
            if reward=='mining':state_effect=infra(stem,state)+' add_resource = { type = steel amount = 3 } add_resource = { type = tungsten amount = 2 }'
            elif reward=='jadar':state_effect='add_extra_state_shared_building_slots = 1 add_resource = { type = steel amount = 3 } add_resource = { type = tungsten amount = 2 }'
            elif reward=='slot':state_effect='add_extra_state_shared_building_slots = 1'
            elif reward=='logistics':state_effect='add_extra_state_shared_building_slots = 1 add_building_construction = { type = infrastructure level = 1 instant_build = yes }'
            elif reward in ['grid','hydro']:state_effect=infra(stem,state)+(' add_resource = { type = coal amount = 2 }' if reward=='hydro' else '')
            elif reward in ['civilian','power_plant','energy_farm','nuclear_reactor']:
                building='industrial_complex' if reward=='civilian' else reward
                state_effect=f'add_extra_state_shared_building_slots = 1 add_building_construction = {{ type = {building} level = 1 instant_build = yes }}'
        triggers.append(f'{eligible} = {{ {rules} }}')
        safety='MSGA_safe_finish_'+stem
        # Start-only prerequisite/technology checks must not invalidate a
        # paid project at the final tick. Retain actual reward capacity and
        # native energy exclusivity, without a circular free-slot test.
        safe_rules='tag = SER'+(f' {state} = {{ {state_rules.replace("MSGA_development_starting_serbia_state = yes ", "")} }}' if state else '')
        triggers.append(f'{safety} = {{ {safe_rules} }}')
        grants_building=reward in ['mining','logistics','grid','hydro','civilian','power_plant','energy_farm','nuclear_reactor']
        if reward in ['logistics','civilian','power_plant','energy_farm','nuclear_reactor']:
            building='infrastructure' if reward=='logistics' else 'industrial_complex' if reward=='civilian' else reward
            state_effect+=' '+debug(stem,f'granted {building} in state {state}')
        release=f'clr_country_flag = {pending} '+(f'clr_country_flag = MSGA_development_state_{state}_busy' if state else '')
        cancel='MSGA_cancel_'+stem
        effects.append(f'{cancel} = {{ if = {{ limit = {{ has_country_flag = {pending} }} '+(debug(stem,'cancelled')+' ' if grants_building else '')+refund(p['cash'])+' '+(f'add_political_power = {p["pp"]} ' if p['pp'] else '')+release+' } }')
        reward_code=(f'{state} = {{ {state_effect} }} ' if state else '')+development(p)
        if reward in ['power_plant','energy_farm','nuclear_reactor']:reward_code+=' update_power_plants_effect = yes'
        if reward in ['expertise','nuclear_programme','workforce']:reward_code+=f' add_tech_bonus = {{ name = MSGA_nuclear_research_bonus bonus = 0.5 uses = 1 category = nuclear }}'
        if reward=='grid':reward_code+=' add_timed_idea = { idea = MSGA_grid_modernisation_bonus days = 180 }'
        if reward=='nuclear_programme':reward_code+=' add_timed_idea = { idea = MSGA_nuclear_programme_research days = 365 }'
        if reward=='storage':reward_code+=' add_ideas = MSGA_grid_scale_storage_network'
        if p['event']:reward_code+=' '+event_effect(p['event'])+' = yes'
        after_done=' MSGA_check_industrial_revival = yes' if not p['energy'] else ''
        effects.append(f'MSGA_finish_{stem} = {{ '+(debug(stem,'completion fired')+' ' if grants_building else '')+f'if = {{ limit = {{ has_country_flag = {pending} NOT = {{ has_country_flag = {done} }} {safety} = yes }} {reward_code} set_country_flag = {done}{after_done} {release} }} else = {{ {cancel} = yes }} }}')
        available=f'MSGA_development_unlocked = yes has_war = no {eligible} = yes {partner(p["group"])}'
        if state:available+=f' custom_trigger_tooltip = {{ tooltip = MSGA_development_state_free_tt NOT = {{ has_country_flag = MSGA_development_state_{state}_busy }} }}'
        start=f'{charge(p["cash"])} set_country_flag = {pending}'
        if state:start+=f' set_country_flag = MSGA_development_state_{state}_busy'
        start+=' custom_effect_tooltip = MSGA_development_cancel_tt'
        threshold=3 if reward=='nuclear_reactor' else p['cash']+1
        ai=f'base = {8 if p["energy"] else 5} modifier = {{ factor = 0 NOT = {{ {cash_test(threshold)} }} }}'
        if p['energy']:ai+=' modifier = { factor = 3 has_resources_in_country = { resource = coal amount < 0 } }'
        block=f'''{id} = {{
 icon = GFX_decision_{id} allowed = {{ tag = SER }}
 visible = {{ MSGA_development_unlocked = yes NOT = {{ has_country_flag = {done} }} }}
 available = {{ {available} NOT = {{ has_country_flag = {pending} }} }}
 cost = {p['pp']} custom_cost_text = MSGA_development_cost_{str(p['cash']).replace('.','_')}
 custom_cost_trigger = {{ {cash_test(p['cash'])} }}
 days_remove = {p['days']} cancel_if_not_visible = no
 cancel_trigger = {{ NOT = {{ {safety} = yes }} }}
 complete_effect = {{ {start} }}
 remove_effect = {{ MSGA_finish_{stem} = yes }} cancel_effect = {{ {cancel} = yes }}
 ai_will_do = {{ {ai} }}
}}'''
        decisions[CATEGORIES[int(p['energy'])]].append(block)
        loc_title=({'china':'China: ','russia':'Russia: ','europe':'Europe: '}.get(p['group'],''))+p['title']
        l(id,loc_title);l(id+'_desc',f'One-time investment: ${p["cash"]:g}B Treasury'+(f' and {p["pp"]} PP' if p['pp'] else '')+f'. Takes {p["days"]} days. '+p['text']+(f' Target: $STATE_{state}$. Only original 2020 Serbia territory is eligible.' if state else ''))
    for p in PROGRAMMES:
        stem=p['stem'];id='MSGA_'+stem;cooldown='MSGA_cooldown_'+stem
        available='MSGA_development_unlocked = yes has_war = no '+partner(p['group'])
        if p['requires']:available+=' has_country_flag = MSGA_done_'+p['requires']
        effect=(charge(p['cash'])+' ' if p['cash'] else '')+f'add_timed_idea = {{ idea = {id} days = 180 }} set_country_flag = {{ flag = {cooldown} days = 250 }} custom_effect_tooltip = MSGA_development_repeatable_tt'
        cost=f'custom_cost_text = MSGA_development_cost_{str(p["cash"]).replace(".","_")} custom_cost_trigger = {{ {cash_test(p["cash"])} }}' if p['cash'] else ''
        decisions[CATEGORIES[int(p['energy'])]].append(f'''{id} = {{
 icon = GFX_decision_{id} allowed = {{ tag = SER }} visible = {{ MSGA_development_unlocked = yes }}
 available = {{ {available} NOT = {{ has_country_flag = {cooldown} }} NOT = {{ has_idea = {id} }} }}
 cost = {p['pp']} {cost}
 complete_effect = {{ {effect} }}
 ai_will_do = {{ base = 2 modifier = {{ factor = 0 NOT = {{ {cash_test(1)} }} }} }}
}}''')
        title=({'china':'China: ','russia':'Russia: ','europe':'Europe: '}.get(p['group'],''))+p['title']
        l(id,title);l(id+'_desc',('Cost: 50 PP; no Treasury cost. ' if p['pp'] else 'Cost: $0.2B Treasury. ')+p['text']+' Effect lasts 180 days. The programme may be renewed 70 days after the effect expires. It cannot stack with itself.')
        extra_ideas[id]=(p['modifiers'],p['crop'],p['energy'])
    for amount in sorted({p['cash'] for p in PROJECTS+PROGRAMMES if p['cash']}):l('MSGA_development_cost_'+str(amount).replace('.','_'),f'§Y${amount:g}B§!')
    l('MSGA_nuclear_research_bonus','Serbian Civilian Nuclear Research')
    for id,title,image,body,option in EVENTS:
        effects.append(f'{event_effect(id)} = {{ if = {{ limit = {{ NOT = {{ has_country_flag = {id.replace(".","_")}_queued }} NOT = {{ has_country_flag = {id.replace(".","_")}_seen }} }} set_country_flag = {id.replace(".","_")}_queued country_event = {{ id = {id} days = 1 }} }} }}')
        l(id+'.t',title);l(id+'.d',body);l(id+'.a',option)
    event_text='add_namespace = MSGA_econ\nadd_namespace = MSGA_energy\n'
    for id,title,image,body,option in EVENTS:event_text+=f'country_event = {{ id = {id} title = {id}.t desc = {id}.d picture = GFX_MSGA_event_{image} is_triggered_only = yes trigger = {{ tag = SER NOT = {{ has_country_flag = {id.replace(".","_")}_seen }} }} immediate = {{ set_country_flag = {id.replace(".","_")}_seen }} option = {{ name = {id}.a }} }}\n'
    with ZipFile(PACK) as z:
        root='MSGA_Economic_Energy_Visuals/'
        boards={False:Image.open(io.BytesIO(z.read(root+'decision_concepts/MSGA_preview_economic_cooperation.png'))).convert('RGB'),True:Image.open(io.BytesIO(z.read(root+'decision_concepts/MSGA_preview_energy_development.png'))).convert('RGB')}
        def artwork(path,sprite,im,size,compression,entry,crop):
            out=MOD/path;out.parent.mkdir(parents=True,exist_ok=True)
            is_decision=size==(52,45)
            if REFRESH and not is_decision:
                asset_records[path]=prior['assets'][path]
                sprites.append(f'spriteType = {{ name = "{sprite}" texturefile = "{path}" }}')
                return
            assert REFRESH or not out.exists(),path
            result=decision_image(im) if is_decision else ImageOps.fit(im,size,method=Image.Resampling.LANCZOS).convert('RGBA')
            result.save(out,pixel_format=compression)
            with Image.open(out) as check:assert check.size==size;check.load()
            sprites.append(f'spriteType = {{ name = "{sprite}" texturefile = "{path}" }}')
            asset_records[path]={'sha256':sha(out),'size':list(size),'compression':compression,'zip_entry':root+entry,'crop':list(crop) if crop else None}
        for p in PROJECTS+PROGRAMMES:
            id='MSGA_'+p['stem'];crop=decision_crop(p);b=boards[p['energy']].crop(crop)
            artwork('gfx/interface/decisions/'+id+'.dds','GFX_decision_'+id,b,(52,45),'DXT5','decision_concepts/MSGA_preview_'+('energy_development' if p['energy'] else 'economic_cooperation')+'.png',crop)
        for id,(mods,crop,energy) in extra_ideas.items():
            artwork('gfx/interface/ideas/'+id+'.dds','GFX_idea_'+id,boards[energy].crop(crop),(64,64),'DXT5','decision_concepts/MSGA_preview_'+('energy_development' if energy else 'economic_cooperation')+'.png',crop)
        for i in range(2):
            crop=(24,22,198,150)
            artwork(f'gfx/interface/decisions/MSGA_development_category_{i}.dds',f'GFX_decision_category_MSGA_development_{i}',boards[bool(i)].crop(crop),(52,40),'DXT5','decision_concepts/MSGA_preview_'+('energy_development' if i else 'economic_cooperation')+'.png',crop)
        for id,title,image,body,option in EVENTS:
            entry='event_pictures/MSGA_event_'+image+'.png';im=Image.open(io.BytesIO(z.read(root+entry))).convert('RGB')
            artwork('gfx/event_pictures/MSGA_event_'+image+'.dds','GFX_MSGA_event_'+image,im,(500,250),'DXT3',entry,None)
    idea_text='ideas = { country = {\n'
    for id,(mods,crop,energy) in extra_ideas.items():
        idea_text+=f'{id} = {{ picture = {id} traits = {{ ZZZ_blank_idea_trait }} allowed = {{ always = no }} allowed_civil_war = {{ always = yes }} removal_cost = -1 modifier = {{ '+' '.join(f'{k} = {v:g}' for k,v in mods.items())+' } }\n'
        if id+'_desc' not in loc:l(id+'_desc','A Serbian development programme using the native TFR economy and energy system.')
    idea_text+='} }\n'
    output={
      'common/decisions/categories/MSGA_economic_energy_categories.txt':'\n'.join(categories)+'\n',
      'common/decisions/MSGA_economic_energy_decisions.txt':'\n'.join(c+' = {\n'+'\n'.join(bs)+'\n}' for c,bs in decisions.items())+'\n',
      'common/scripted_triggers/MSGA_economic_energy_triggers.txt':'\n'.join(triggers)+'\n',
      'common/scripted_effects/MSGA_economic_energy_effects.txt':'\n'.join(effects)+'\n',
      'common/on_actions/MSGA_economic_energy_on_actions.txt':'on_actions = { on_startup = { effect = { SER = { MSGA_unlock_economic_energy = yes } } } on_weekly = { effect = { if = { limit = { tag = SER } MSGA_unlock_economic_energy = yes } } } on_focus_completed = { effect = { if = { limit = { tag = SER } MSGA_unlock_economic_energy = yes } } } }\n',
      'common/ideas/MSGA_economic_energy_ideas.txt':idea_text,
      'events/MSGA_economic_energy_events.txt':event_text,
      'interface/MSGA_economic_energy_assets.gfx':'spriteTypes = {\n'+'\n'.join(sprites)+'\n}\n',
      'localisation/english/MSGA_economic_energy_l_english.yml':'l_english:\n'+'\n'.join(' '+k+':0 "'+v.replace('\\','\\\\').replace('\n','\\n').replace('"','\\"')+'"' for k,v in loc.items())+'\n'
    }
    for path,text in output.items():
        if not path.endswith('.yml'):parse(text)
        write(path,text,bom=path.endswith('.yml'))
    changed=REFRESH_TEXT|{p for p,a in asset_records.items() if a['size']==[52,45]}
    assert all(sha(MOD/p)==digest for p,digest in baseline.items() if not REFRESH or p not in changed),'Unrelated campaign files changed'
    if REFRESH:
        for path in sorted(changed):shutil.copyfile(LIVE/path,ROOT/'make_serbia_great_again'/path)
        assert inventory(LIVE)==inventory(ROOT/'make_serbia_great_again')
    native_paths=['common/buildings/TFR_buildings.txt','common/scripted_effects/00_TFR_scripted_effects_ZZZ_generic.txt','common/modifier_definitions/00_TFR_economic_modifiers_definition.txt','common/dynamic_modifiers/00_TFR_dynamic_modifiers_ZZZ_generic.txt','common/technologies/electronic_mechanical_engineering.txt','common/decisions/TFR_decisions_SER.txt','common/decisions/TFR_decisions_SOV.txt','common/decisions/TFR_decisions_GER.txt']+list(owners.values())
    data={'runtime':str(LIVE),'package':str(PACK),'package_sha256':sha(PACK),'baseline_sha256':prior['baseline_sha256'] if REFRESH else baseline,
          'starting_serbia_states':owners,'state_geography':{'Bor/Kostolac/Djerdap/Nis':108,'Jadar/Obrenovac/Kragujevac/Morava corridor':1296,'Belgrade city':107,'Vojvodina/nuclear site/solar manufacturing':45},
          'reference_repository':'https://github.com/RubovszkiB/HOI4-TFR-Austria-Hungary-reborn','reference_commit':'8e4e35f8093f826dc21fafbccb82e3e1cd3eb18e',
          'native_sources_sha256':{p:sha(TFR/p) for p in native_paths},'native_energy_buildings':{n:get(native_buildings,n) for n in ['power_plant','energy_farm','nuclear_reactor']},
          'assets':asset_records,'projects':PROJECTS,'programmes':PROGRAMMES,'events':EVENTS,
          'new_runtime_files':sorted(list(output)+list(asset_records)),
          'fallbacks':['No separate copper/lithium resource. User requested native steel and tungsten: each mining project grants +3 steel and +2 tungsten.','No dedicated hydro building is introduced. Djerdap adds 2 native coal/Energy resource to existing generation.','No storage currency/building: native factory_energy_consumption -3% permanently.','User chose native energy exclusivity: Kostolac thermal and Bor renewable projects share state 108 and are alternatives.'],
          'native_graphics_examples':{'decision':['gfx/interface/decisions/generic/generic_construction.png',[52,45]],'compressed_decision':['gfx/interface/decisions/reconstruction.dds','DXT5'],'event':['gfx/event_pictures/report_event_001.dds',[500,250],'DXT3'],'category':['GAME/gfx/interface/decisions/decision_category_generic_economy.dds',[52,40]],'idea':['gfx/interface/ideas/companies/industrial/lifan_industry.dds',[64,64],'DXT5']}}
    (ROOT/'docs/economic_energy_sources.json').write_text(json.dumps(data,indent=2)+'\n')
    print(f'Generated {len(PROJECTS)} permanent projects, {len(PROGRAMMES)} repeatable programmes, 8 milestones and {len(asset_records)} supplied-art DDS. Existing 320 campaign files unchanged; targeted runtime files synchronized.')

if __name__=='__main__':main()
