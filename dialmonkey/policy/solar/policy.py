from itertools import groupby
from inspect import signature
from dialmonkey.da import DA, DAI
from dialmonkey.component import Component
from dialmonkey.dialogue import Dialogue
from dialmonkey.utils import choose_one
from dialmonkey.repositories import SolarRepository
import scipy.constants

km_au = scipy.constants.au / 1000


class RequestQueryMapper:
    def __init__(self, repo):
        self._repo: SolarRepository = repo
        self._property_map = repo.properties()

    def greet(self):
        return ('greet', None, None)

    def goodbye(self, thanks=None):
        return ('exit', None, None)

    def request_travel_time(self, context):
        name = context.require('name')
        body1 = self._find_body(context.try_get('from', 'earth'))
        body2 = self._find_body(name)
        raise DirectResponse(('error', 'not_implemented', None))

    def request_distance(self, context):
        name = context.require('name')
        body1 = self._find_body(context.try_get('from', 'earth'))
        body2 = self._find_body(name)
        min_d, mean_d, max_d = self._repo.measure_distance(
            body1['id'], body2['id'])
        return [
            ('inform', 'from', body1['englishName']),
            ('inform', 'to', body2['englishName']),
            ('inform', 'minimal_distance', f"{min_d / km_au:.2f}au"),
            ('inform', 'mean_distance', f"{mean_d / km_au:.2f}au"),
            ('inform', 'maximal_distance', f"{max_d / km_au:.2f}au"),
        ]

    #
    # Planets
    #
    def _planet_filter(self, collection, name, filter):
        top = None
        if filter == 'support_life':
            collection = [x for x in collection if x['isHabitable'] == True]
        elif filter == 'smaller':
            y = self._find_body(name())
            collection = [
                x for x in collection if x['meanRadius'] < y['meanRadius']]
            top_obj = collection.sort(key=lambda x: x['meanRadius'])
            top = ('inform', 'min_radius',
                   f"{collection[0]['meanRadius']:.0f}km")
        elif filter == 'larger' or filter == 'bigger':
            y = self._find_body(name())
            collection = [
                x for x in collection if x['meanRadius'] > y['meanRadius']]
            top_obj = collection.sort(key=lambda x: -x['meanRadius'])
            top = ('inform', 'max_radius',
                   f"{collection[0]['meanRadius']:.0f}km")
        elif filter == "lower_gravity":
            y = self._find_body(name())
            collection = [x for x in collection if x['gravity'] < y['gravity']]
            top_obj = collection.sort(key=lambda x: x['gravity'])
            top = ('inform', 'min_gravity',
                   f"{collection[0]['gravity'] / scipy.constants.g:.1f}g")
        elif filter == "higher_gravity":
            y = self._find_body(name())
            collection = [x for x in collection if x['gravity'] > y['gravity']]
            top_obj = collection.sort(key=lambda x: -x['gravity'])
            top = ('inform', 'max_gravity',
                   f"{collection[0]['gravity'] / scipy.constants.g:.1f}g")
        else:
            raise ValueError('unknown filter %s' % filter)
        return collection, top

    def count_planets(self, context, filter=None):
        planets = [x for x in self._repo.bodies() if x['isPlanet']]
        result = [
            ('inform', 'count', f'{len(planets)}'), ('inform', 'object', 'planet')]
        if filter is not None:
            planets, top = self._planet_filter(
                planets, lambda: context.try_get('name', 'earth'), filter)
            result[0] = ('inform', 'count', f'{len(planets)}')
            if top is not None:
                result.append(top)
        if len(planets) == 1:
            result.append(('inform', 'single_name', planets[0]['englishName']))
        return result

    def request_planets(self, context, filter=None):
        planets = [x for x in self._repo.bodies() if x['isPlanet']]
        result = [
            ('inform', 'count', f'{len(planets)}'), ('inform', 'object', 'planet')]
        if filter is not None:
            planets, top = self._planet_filter(
                planets, lambda: context.try_get('name', 'earth'), filter)
            result[0] = ('inform', 'count', f'{len(planets)}')
            if top is not None:
                result.append(top)
        result.append(('inform', 'names', ','.join(
            [x['englishName'] for x in planets])))
        return result

    def request_list(self, context):
        last_request = context.try_get_last_count_request()
        if last_request:
            intent, values, state_values = last_request
            intent = intent.replace('count_', 'request_')
            values.update(context.values)
            state_values.update(context.values)
            return self(intent, values, state_values)
        return ('ask', 'what_to_list', None)

    def request_life(self, context):
        name = context.require('name')
        body = self._find_body(name)
        return [('inform', 'name', body['englishName']),
                ('inform', 'life', 'yes' if body['hasLife'] else 'no'),
                ('inform', 'habitable',
                 'yes' if body['isHabitable'] else 'no'),
                ('inform', 'could_support_life', 'yes' if body['couldSupportLife'] else 'no')]

    def request_support_life(self, context):
        name = context.require('name')
        body = self._find_body(name)
        return [('inform', 'name', body['englishName']),
                ('inform', 'life', 'yes' if body['hasLife'] else 'no'),
                ('inform', 'habitable',
                 'yes' if body['isHabitable'] else 'no'),
                ('inform', 'could_support_life', 'yes' if body['couldSupportLife'] else 'no')]

    def request_best_life_conditions(self):
        habitable = [x for x in self._repo.bodies() if x['isHabitable']]
        bodies = [x for x in self._repo.bodies() if x['couldSupportLife']]
        return [('inform', 'habitable_bodies', ','.join([x['englishName'] for x in habitable])),
                ('inform', 'habitable_bodies_count', f'{len(habitable)}'),
                ('inform', 'life_supportable_bodies', ','.join([x['englishName'] for x in bodies]))]

    def request_humans_landed(self, context):
        name = context.require('name')
        body = self._find_body(name)
        return [('inform', 'name', body['englishName']),
                ('inform', 'humans_landed', 'yes' if body['humansLanded'] else 'no')]

    def request(self, context, name=None, filter=None, object=None):
        if object is None and name is None:
            name = context.require('name')
        if name is None:
            bodies = self._repo.bodies()
            if object == 'planet':
                bodies = (x for x in bodies if x['isPlanet'])
            elif object == 'solar_body' or object == 'body':
                pass
            elif object == 'gas_giant':
                bodies = (
                    x for x in bodies if x['isPlanet'] and x['planetType'] == 'gas_giant')
            else:
                raise ValueError('unknown object type %s' % object)

            append_info = None
            if filter == 'largest' or filter == 'biggest':
                body = max(bodies, key=lambda x: x['meanRadius'])
                append_info = ('inform', 'radius',
                               f"{body['meanRadius']:.0f}km")
            elif filter == 'smallest':
                body = min(bodies, key=lambda x: x['meanRadius'])
                append_info = ('inform', 'radius',
                               f"{body['meanRadius']:.0f}km")
            elif filter == 'lightest':
                body = max(bodies, key=lambda x: (
                    x['mass']['massExponent'], x['mass']['massValue']))
                append_info = (
                    'inform', 'mass', f"{body['mass']['massValue']:0.1f} x {body['mass']['massExponent']}")
            elif filter == 'heaviest':
                body = min(bodies, key=lambda x: (
                    x['mass']['massExponent'], x['mass']['massValue']))
                append_info = (
                    'inform', 'mass', f"{body['mass']['massValue']:0.1f} x {body['mass']['massExponent']}")
            elif filter == 'closest':
                body = min(bodies, key=lambda x: self._repo.measure_distance(
                    x['id'], 'terre')[1])
                _, distance, _ = self._repo.measure_distance(
                    body['id'], 'terre')
                append_info = ('inform', 'mean_distance',
                               f"{distance / km_au:0.2f}au")

            elif filter == 'furthest':
                body = min(bodies, key=lambda x: -
                           self._repo.measure_distance(x['id'], 'terre')[1])
                _, distance, _ = self._repo.measure_distance(
                    body['id'], 'terre')
                append_info = ('inform', 'mean_distance',
                               f"{distance / km_au:0.2f}au")

            else:
                raise ValueError('unknown filter %s' % filter)

            result = [('inform', 'name', body['englishName']),
                      ('inform', 'object', object), ('inform', 'filter', filter)]
            if append_info is not None:
                result.append(append_info)
            return result
        else:
            body = self._find_body(name)
            return [
                ('inform', 'name', body['englishName']),
                ('inform', 'radius', f"{body['meanRadius']:.0f}km"),
                ('inform', 'gravity',
                 f"{body['gravity'] / scipy.constants.g:0.1f}g"),
                ('inform', 'mass',
                 f"{body['mass']['massValue']:0.1f} x {body['mass']['massExponent']}"),
            ]

    def request_property(self, context, property):
        name = context.require('name')
        append_info = []
        intent = 'inform'
        body = self._find_body(name)
        if property in self._property_map:
            pname, format = self._property_map[property]
            if isinstance(format, str):
                format_str = format
                def format(x): return format_str % x
            append_info = [(intent, property, format(body[pname]))]
        elif property == 'mass':
            append_info = [
                ('inform', 'mass', f"{body['mass']['massValue']:0.1f} x {body['mass']['massExponent']}")]
        elif property == 'discovery':
            append_info = [(intent, 'discovered_by', body['discoveredBy']),
                           (intent, 'discovered_by', body['discoveryDate'])]
        else:
            raise ValueError('unknown property %s' % property)

        result = [(intent, 'name', body['englishName'])]
        result.extend(append_info)
        return result

    def count_moons(self, context):
        name = context.require('name')
        planet = self._find_body(name)
        moons = len(planet['moons'])
        return [('inform', 'count', f'{moons}'), ('inform', 'object', 'moon'), ('inform', 'names', ','.join((x['moon'] for x in planet['moons'])))]

    def question_request(self, context):
        return ('question_granted', None, None)

    def request_moons(self, context):
        name = context.require('name')
        planet = self._find_body(name)
        moons = len(planet['moons'])
        return [('inform', 'count', f'{moons}'), ('inform', 'object', 'moon'), ('inform', 'names', ','.join((x['moon'] for x in planet['moons'])))]

    def _find_body(self, name):
        body = [x for x in self._repo.bodies(
        ) if x['englishName'].lower() == name]
        if len(body) == 0:
            raise DirectResponse(
                [('error', 'not_found', None), ('error', 'name', name)])
        return body[0]

    def __call__(self, intent, values, state_values):
        if not hasattr(self, intent):
            return None
        method = getattr(self, intent)
        try:
            parameters = signature(method).parameters
            required = [x for x, y in parameters.items()
                        if y.default is not None]
            for r in required:
                if r == 'context':
                    continue
                if r not in values:
                    raise RequiredSlot(r)
            nargs = {k: v for k, v in values.items() if k in parameters}
            if 'context' in parameters:
                nargs['context'] = Context(intent, values, state_values)
            return method(**nargs)
        except DirectResponse as e:
            return e.value


class Context:
    def __init__(self, intent, values, state_values):
        self.intent = intent
        self.values = values
        self.state_values = state_values
        self.state_change = lambda state: state

    def require(self, slot, allow_state=True):
        if slot in self.values:
            return self.values[slot]
        if allow_state and slot in self.state_values:
            return self.state_values[slot]
        raise RequiredSlot(slot)

    def try_get(self, slot, default=None, allow_state=True):
        if slot in self.values:
            return self.values[slot]
        if allow_state and slot in self.state_values:
            return self.state_values[slot]
        return default

    def try_get_last_count_request(self):
        if '_last_count' in self.state_values:
            return self.state_values['_last_count']

    def push_state(slot, value):
        change = self.state_change

        def state_update(state):
            state = dict(**change(state))
            state.update({slot: {value: 1.0, None: 0.0}})
            return state
        self.state_change = state_update


class DirectResponse(BaseException):
    def __init__(self, value):
        self.value = value


class RequiredSlot(DirectResponse):
    def __init__(self, slot):
        super().__init__(('request', slot, None))


class SolarPolicy(Component):
    def __init__(self, *args, repo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._threshold = 0.7
        self._repository = repo if repo is not None else SolarRepository()
        self._mapper = RequestQueryMapper(self._repository)

    def _map_call(self, da: DA, state) -> DA:
        assert da is not None
        assert isinstance(da, DA)
        assert state is not None
        if not da.dais:
            return DA([DAI('error', 'not_understood', None)])

        dai = [(x.intent, x.confidence) for x in da.dais]
        dai.sort()
        dai = [(k, sum(map(lambda x: x[1], s)))
               for k, s in groupby(dai, key=lambda x: x[0])]
        dai.sort(reverse=True)

        # We support single intent for now
        intent, _ = dai[0]
        values = {x.slot: x.value for x in da.dais if x.confidence >
                  self._threshold}
        state_values = ((k, max((p if p is not None else 'none', v if v is not None else 'none')
                        for v, p in x.items())) for k, x in state.items() if k is not None and not k.startswith('_'))
        state_values = {
            k: v for k, (p, v) in state_values if p > self._threshold and isinstance(k, str)}

        # Add meta attributes
        state_values.update(
            **{k: x for k, x in state.items() if k is not None and k.startswith('_')})
        response = self._mapper(intent, values, state_values)
        if response is None:
            response = list()
        elif not isinstance(response, list):
            response = [response]

        # Map to DA
        da = DA()
        for r in response:
            da.append(DAI(*r))
        if intent.startswith('count_'):
            state['_last_count'] = (intent, values, state_values)
        return da

    def __call__(self, dial: Dialogue, logger):
        response: DA = self._map_call(dial['nlu'], dial['state'])
        dial.action = response

        if any((x for x in response.dais if x.intent == 'exit')):
            dial.end_dialogue()
        return dial

    def reset(self):
        pass
