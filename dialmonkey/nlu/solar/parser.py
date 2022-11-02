from dialmonkey.component import Component 
from dialmonkey.da import DAI,DA
from itertools import chain
from dialmonkey.repositories import SolarRepository
from collections import deque
from itertools import starmap
import re

def create_intent_formatter(intent, **default_slots):
    def formatter(**x):
        args = [f'{k}={v}' if v != '' else f'{k}' for k,v in chain(default_slots.items(), x.items())]
        return f"{intent}({','.join(args)})"
    return formatter

def regex_parser(reg, formatter):
    expr = re.compile(reg)
    def call(x):
        match = expr.match(x)
        if match:
            if callable(formatter): return formatter(**match.groupdict())
            else: return formatter
        return None
    return call

def Sequential(*parsers):
    def call(x):
        for f in parsers:
            result = f(x)
            if result is not None: return result
        return None
    return call

def simplify(x):
    x = x.lower()
    words = []
    strip_chars = [',','.','!','?', '"', "'", ';']
    for w in x.split(): 
        append_end = []
        for ch in strip_chars:
            if w.startswith(ch): words.append(ch)
            if w.endswith(ch): append_end.append(ch)
            w = w.strip(ch) 
        words.append(w)
        append_end.reverse()
        words.extend(append_end)
    x = ' '.join(words)

    x = x.replace('n\'t', ' not').replace('\'m', ' am')
    x = re.sub(r'(^|\s)our planet($|\s)', lambda m: m.group(1) + 'earth' + m.group(2), x)
    x = re.sub(r'(^|\s)largest($|\s)', lambda m: m.group(1) + 'biggest' + m.group(2), x)
    x = re.sub(r'(^|\s)larger($|\s)', lambda m: m.group(1) + 'bigger' + m.group(2), x)
    x = re.sub(r'(^|\s)us($|\s)', lambda m: m.group(1) + 'earth' + m.group(2), x)
    return x

# Builds a function which replaces known words with tokens
def build_tokenize(repo: SolarRepository):
    objectRegex = re.compile(r'(?:^|\s)(' + "|".join([re.escape(simplify(x['englishName'])) for x in repo.bodies() if x['englishName']]) + r')(?:$|\s)') 
    def tokenize(x): 
        matches = []
        def map_match(x):
            def fn(match):
                matches.append(match.group(1))
                return match.group(0).replace(match.group(1), x)
            return fn
        x = objectRegex.sub(map_match('<object>'), x)
        return x, matches
    return tokenize

# Build the parser used to parse the expression
def build_parser():
    free_start = r'^(?:.*\s|)'
    free_end = r'(?:\s.*|)$'
    fr = r'(?:\s.*|)'
    propertymap = dict(big='size', large='size', far='distance',close='distance', heavy='mass') 
    propertyreg = '|'.join(propertymap.keys())
    propertyval = '|'.join(['gravity'] + list(propertymap.values()))
    def map_object(x):
        return x.replace(' ', '_')
    return Sequential(
        # Request planets
        regex_parser(free_start + rf'(?:which|what) is{fr} (?P<f>biggest|largest|smallest|closest|furthest|heaviest|lightest){fr} (?P<o>planet|body|asteroid|moon|gas giant)' + free_end,lambda f, o,**k: f'request(filter={f},object={map_object(o)})'),
        regex_parser(free_start + rf'(?:what|which){fr} (?P<o>planet|body|asteroid|moon|gas giant) is{fr} (?P<f>biggest|largest|smallest|closest|furthest|heaviest|lightest)' + free_end,lambda f, o,**k: f'request(filter={f},object={map_object(o)})'),
        regex_parser(free_start + rf'what{fr} (?P<o>planet|body|asteroid|moon|gas giant){fr} greatest mass' + free_end,lambda o,**k: f'request(filter=heaviest,object={map_object(o)})'),
        regex_parser(free_start + rf'what{fr} (?P<o>planet|body|asteroid|moon|gas giant){fr} lowest mass' + free_end,lambda o,**k: f'request(filter=lightest,object={map_object(o)})'),

        # request life
        regex_parser(free_start + fr'is{fr} life{fr} <object>' + free_end, 'request_life(name=<object>)'), 
        regex_parser(free_start + fr'(?:could|does){fr} (?:be|exist|exists) life{fr} <object>' + free_end, 'request_support_life(name=<object>)'), 
        regex_parser(free_start + fr'(?:could|does){fr} <object> support life' + free_end, 'request_support_life(name=<object>)'), 
        regex_parser(free_start + fr'(?:could|does){fr} (?:be|exist|exists) life' + free_end, 'request_support_life()'), 
        regex_parser(free_start + fr'(?:could|does){fr} live' + free_end, 'request_support_life()'), 
        regex_parser(free_start + fr'best{fr} to (?:live|support life)' + free_end, 'request_best_life_conditions()'), 
        regex_parser(free_start + fr'humans{fr} (?:landed|visited){fr} <object>' + free_end, 'request_humans_landed(name=<object>)'), 
        regex_parser(free_start + fr'humans{fr} (?:landed|visited)' + free_end, 'request_humans_landed()'), 


        
        # Distance and travel time
        regex_parser(free_start + fr'how far{fr} <object>{fr} from <object>' + free_end, 'request_distance(name=<object>,from=<object>)'),
        regex_parser(free_start + fr'how far{fr} from <object>{fr} is <object>' + free_end, 'request_distance(name=<object>,from=<object>)'),
        regex_parser(free_start + fr'how far{fr} <object>' + free_end, 'request_distance(name=<object>)'),
        regex_parser(free_start + fr'distance to{fr} <object>' + free_end, 'request_distance(name=<object>)'),
        
        regex_parser(free_start + fr'how far' + free_end, 'request_distance()'),
        regex_parser(free_start + fr'how long{fr} (?:get|travel) to{fr} <object>' + free_end, 'request_travel_time(name=<object>)'),
        regex_parser(free_start + fr'how long{fr} (?:get|travel)' + free_end, 'request_travel_time()'),



        # Request property
        regex_parser(free_start + rf"how{fr} (?P<f>{propertyreg}){fr} <object>" + free_end,lambda f,**k: f'request_property(filter={propertymap[f]},name=<object>)'),
        regex_parser(free_start + rf'how{fr} (?P<f>{propertyreg}){fr} (?:is it|it is)' + free_end,lambda f,**k: f'request_property(property={propertymap[f]})'),
        regex_parser(free_start + rf'how{fr} (?P<f>big,large,far,close,heavy){fr} (?:is it|it is)' + free_end,lambda f,**k: f'request_property(property={f})'),
        regex_parser(free_start + rf"what is{fr} (?P<f>{propertyval}){fr} (?:of|on|in) <object>" + free_end,lambda f,**k: f'request_property(property={f},name=<object>)'),
        regex_parser(free_start + rf'what is{fr} (?P<f>{propertyval})' + free_end,lambda f,**k: f'request_property(property={f})'),



        regex_parser(free_start + fr'what{fr} moons{fr} <object>' + free_end,lambda **k: 'request_moons(name=<object>)'),
        regex_parser(free_start + fr'what{fr} moons{fr}' + free_end,lambda **k: 'request_moons()'),

        # Count moons
        regex_parser(free_start + fr'how many moons{fr} it (?:have|has)' + free_end,lambda **k: 'count_moons()'),
        regex_parser(free_start + fr'how many moons{fr} <object> have' + free_end,lambda **k: 'count_moons(name=<object>)'),
        regex_parser(free_start + fr'how many moons' + free_end,lambda **k: 'count_moons()'),

        # count_planets
        regex_parser(free_start + r'how many planets (?:.*\s|)bigger than (?:.*\s|)<object>' + free_end,lambda **k: 'count_planets(filter=bigger,name=<object>)'),
        regex_parser(free_start + r'how many planets (?:.*\s|)bigger' + free_end,lambda **k: 'count_planets(filter=bigger)'),
        regex_parser(free_start + r'how many planets (?:.*\s|)larger than (?:.*\s|)<object>' + free_end,lambda **k: 'count_planets(filter=bigger,name=<object>)'),
        regex_parser(free_start + r'how many planets (?:.*\s|)larger' + free_end,lambda **k: 'count_planets(filter=bigger)'),
        regex_parser(free_start + fr'how many planets{fr} smaller than{fr} <object>' + free_end,lambda **k: 'count_planets(filter=smaller,name=<object>)'),
        regex_parser(free_start + r'how many planets (?:.*\s|)smaller' + free_end,lambda **k: 'count_planets(filter=smaller)'), 
        regex_parser(free_start + r'how many planets (?:.*\s|)lighter than (?:.*\s|)<object>' + free_end,lambda **k: 'count_planets(filter=lower_gravity,name=<object>)'),
        regex_parser(free_start + r'how many planets (?:.*\s|)lighter' + free_end,lambda **k: 'count_planets(filter=lower_gravity)'), 
        regex_parser(free_start + fr'how many planets{fr} (?:smaller|lower) gravity' + free_end,lambda **k: 'count_planets(filter=lower_gravity)'),
        regex_parser(free_start + fr'how many planets{fr} (?:bigger|greater|higher) gravity' + free_end,lambda **k: 'count_planets(filter=higher_gravity)'),
        regex_parser(free_start + fr'how many planets{fr} (?:smaller|lower) mass' + free_end,lambda **k: 'count_planets(filter=lower_mass)'),
        regex_parser(free_start + fr'how many planets{fr} (?:bigger|greater|higher) mass' + free_end,lambda **k: 'count_planets(filter=higher_mass)'),
        regex_parser(free_start + fr'how many planets{fr} (?:support|possibility){fr} life' + free_end,lambda **k: 'count_planets(filter=support_life)'),
        regex_parser(free_start + r'how many planets' + free_end,lambda **k: 'count_planets()'),

        # list planets
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)bigger than (?:.*\s|)<object>' + free_end,lambda **k: 'request_planets(filter=bigger,name=<object>)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)bigger' + free_end,lambda **k: 'request_planets(filter=bigger)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)larger than (?:.*\s|)<object>' + free_end,lambda **k: 'request_planets(filter=bigger,name=<object>)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)larger' + free_end,lambda **k: 'request_planets(filter=bigger)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)smaller than (?:.*\s|)<object>' + free_end,lambda **k: 'request_planets(filter=smaller,name=<object>)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)smaller' + free_end,lambda **k: 'request_planets(filter=smaller)'), 
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)lighter than (?:.*\s|)<object>' + free_end,lambda **k: 'request_planets(filter=lower_gravity,name=<object>)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets (?:.*\s|)lighter' + free_end,lambda **k: 'request_planets(filter=lower_gravity)'), 
        regex_parser(free_start + fr'(?:what|list|list of) (?:the |)planets{fr} (?:smaller|lower) gravity' + free_end,lambda **k: 'request_planets(filter=lower_gravity)'),
        regex_parser(free_start + fr'(?:what|list|list of) (?:the |)planets{fr} (?:bigger|greater|higher) gravity' + free_end,lambda **k: 'request_planets(filter=higher_gravity)'),
        regex_parser(free_start + fr'(?:what|list|list of) (?:the |)planets{fr} (?:smaller|lower) mass' + free_end,lambda **k: 'request_planets(filter=lower_mass)'),
        regex_parser(free_start + fr'(?:what|list|list of) (?:the |)planets{fr} (?:bigger|greater|higher) mass' + free_end,lambda **k: 'request_planets(filter=higher_mass)'),
        regex_parser(free_start + fr'(?:what|list|list of) (?:the |)planets{fr} (?:support|possibility){fr} life' + free_end,lambda **k: 'request_planets(filter=support_life)'),
        regex_parser(free_start + r'(?:what|list|list of) (?:the |)planets' + free_end,lambda **k: 'request_planets()'),

        # List them
        regex_parser(free_start + rf'list (?:of\s|)them' + free_end, 'request_list()'),
        regex_parser(free_start + rf'name them' + free_end, 'request_list()'),


        # General
        regex_parser(free_start + rf'what (?:is|about) <object>' + free_end, 'request(name=<object>)'),
        regex_parser(free_start + '<object>' + free_end, 'request(name=<object>)'),

        # Greet
        regex_parser(free_start + rf'(?:hi|hello)' + free_end, 'greet()'),
        regex_parser(free_start + rf'(?:ask you)' + free_end, 'question_request()'),
        regex_parser(free_start + rf'(?:thanks|thank)' + free_end, 'goodbye(thanks)'),
        regex_parser(free_start + rf'(?:ok|goodbye|that is all)' + free_end, 'goodbye()'),
    )

class SolarSystemNLU(Component):
    def __init__(self, *args, repo = None, **kwargs):
        super().__init__(*args,**kwargs)
        self._repo = repo if repo is not None else SolarRepository()
        self._parser = build_parser()
        self._tokenize = build_tokenize(self._repo)
        self._match_token = re.compile(r'<\w+>')
        self._act_regex = re.compile(r'^([\w_]+)\(([^\)]*)\)$')

    def _evaluate(self, x, logger):
        x = simplify(x)
        logger.info('NLU: simplified: "%s"' % x)
        x, tokens = self._tokenize(x)
        logger.info('NLU: tokenized: "%s"' % x)
        x = self._parser(x)
        if x is None: return [] # No result
        match = self._act_regex.match(x)
        if len(match.group(2).strip()) == 0: return [(match.group(1), None, None)] # Intent only

        results = []
        tokens = deque(tokens)
        for slotvalue in match.group(2).split(','):
            slot, value = slotvalue.split('=') if '=' in slotvalue else (slotvalue, None)

            # Map tokens back
            slot = self._match_token.sub(lambda _: tokens.popleft(), slot)
            if value is not None:
                value = self._match_token.sub(lambda _: tokens.popleft(), value)

            results.append((match.group(1), slot, value))
        return results

    def __call__(self, dial, logger):
        result = self._evaluate(dial['user'], logger)
        dial['nlu'] = DA(list(starmap(DAI, result)))
        logger.info('NLU: %s', str(dial['nlu']))
        return dial
