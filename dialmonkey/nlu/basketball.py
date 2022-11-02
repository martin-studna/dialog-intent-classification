# Author: Matej Mik

from ..component import Component
from ..da import DAI
import re


def add_team_g(string, attributes):
    if 'tym' in string:
        if re.search('(muj|moj|meh)[^ ]{0,3} tym', string):
            attributes.append('team=default')
        else:
            team = string.split('tym')[-1].split(' ', 1)[1]
            if team.startswith('na '):
                team = team[3:]
            attributes.append(f'team={team}')
    return attributes

def add_team_s(string, attributes):
    if 'tym' in string:
        if re.search('(vychozi[^ ]{0,2}|(muj|moj|meh)[^ ]{0,3}) tym', string):
            attributes.append('default')
        team = string.split('tym')[-1].split(' ', 1)[1]
        if team.startswith('na '):
            team = team[3:]
        attributes.append(f'team={team}')
    return attributes

def add_type(string, attributes):
    if ' hrac' in string:
        attributes.append('type=player')
    elif ' tym' in string:
        attributes.append('type=team')
    return attributes

def add_nums(string, attributes):
    nums = re.findall('[0-9]+[^ ]?', string)
    if len(nums) == 1: 
        num = nums[0]
        if num.endswith('.'):
            attributes.append('rank=' + num.rstrip('.'))
        else:
            attributes.append('value=' + num)
    elif any([stem in string for stem in [' nejv', ' nejlepsi']]):
        attributes.append('rank=1')
    return attributes

def add_time(string, attributes):
    if ' dnes' in string:
        attributes.append('time=today')
    elif ' zitr' in string:
        attributes.append('time=tommorow')
    else:
        time = re.findall('[0-9]{1,2}[. ]{1,2}[0-9]{1,2}[.]?', string)
        if len(time) == 1:
            attributes.append(f'time={time[0]}')
    return attributes

def add_name(string, attributes):
    if re.search('(vychozi[^ ]{0,2}|(muj|moj|meh)[^ ]{0,3}) tym', string):
        attributes.append('name=default')
    else:
        names = re.findall(' hrac.*$', string) + re.findall(' tym.*$', string)
        if len(names) == 1:
            name = names[0].lstrip().split(' ', 1)
            if len(name) == 2:
                attributes.append(f'name={name[1]}')
    return attributes

def add_stat(string, attributes):
    if re.search('dv(.{2}bod|oje?k)', string):
        attributes.append('stat=2_pt_made')
    elif re.search('tr(.{1,2}bod|oje?k)', string):
        attributes.append('stat=3_pt_made')
    elif any([stem in string for stem in ['trestn', 'sestk', 'sestek']]):
        if any([stem in string for stem in ['uspesn', 'procent']]):
            attributes.append('stat=ft_percentage')
        else:
            attributes.append('stat=ft_made')
    elif any([stem in string for stem in ['vyher', 'vyhr']]):
        attributes.append('stat=wins')
    elif any([stem in string for stem in ['strelec', 'strelc', ' bod']]):
        attributes.append('stat=points')
    return attributes

def to_DAIs(intent, attributes):
    items = []
    if intent:
        if attributes:
            for att in attributes:
                items.append(DAI.parse(f'{intent}({att})'))
        else:
            items.append(DAI.parse(f'{intent}()'))
    return items

class BasketballNLU(Component):
    def __call__(self, dial, logger):
        intent= ''
        attributes = []
        if dial['user'].startswith('kde'):
            intent = 'request_game'
            attributes.append('place=?')
            attributes = add_team_g(dial['user'], attributes)
        elif dial['user'].startswith('kdy'):
            intent = 'request_game'
            attributes.append('time=?')
            attributes = add_team_g(dial['user'], attributes)
        elif any([stem in dial['user'] for stem in ['zapas', 'utkani']]):
            intent = 'request_game'
            attributes = add_time(dial['user'], attributes)
        elif any([dial['user'].startswith(stem) for stem in ['kolik', 'jaky pocet', 'na jake']]):
            intent = 'request_stats'
            if any([stem in dial['user'] for stem in ['kolikat', 'mist', 'pozic']]):
                attributes.append('rank=?')
            else:
                attributes.append('value=?')
            attributes = add_stat(dial['user'], attributes)
            attributes = add_type(dial['user'], attributes)
            attributes = add_name(dial['user'], attributes)
        elif any([dial['user'].startswith(stem) for stem in ['kter', 'kdo', 'jak']]):
            intent = 'request_stats'
            attributes.append('name=?')
            attributes = add_type(dial['user'], attributes)
            attributes = add_nums(dial['user'], attributes)
            attributes = add_stat(dial['user'], attributes)
        elif any([stem in dial['user'] for stem in ['zmen', 'nastav']]):
            intent = 'set'
            years = re.findall('[0-9]{4}', dial['user'])
            if len(years) == 1:
                attributes.append(f'season={years[0]}')
            attributes = add_team_s(dial['user'], attributes)
                
            
        for item in to_DAIs(intent, attributes):
            dial['nlu'].append(item)
        
        logger.info('NLU: %s', str(dial['nlu']))
        return dial