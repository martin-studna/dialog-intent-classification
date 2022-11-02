import requests
from scipy.special import ellipe
import scipy.constants
import math

class SolarRepository:
    _url = 'https://api.le-systeme-solaire.net/rest'

    def __init__(self):
        self._bodies = None
        self._details = dict()
        self._planets = ['mercury','venus','earth','mars','jupiter','saturn','uranus','neptune']
        self._gas_giants = ['jupiter', 'saturn','uranus','neptune']
        self._habitable_bodies = ['earth']
        self._could_be_habitable = ['earth', 'mars','moon','venus', 'europa']
        self._human_landed_bodies = ['moon', 'earth']
        pass 

    def bodies(self):
        if self._bodies is None:
            bodies = requests.get(SolarRepository._url + '/bodies')
            self._bodies = list(map(self._fix_single, bodies.json()['bodies'])) 
            self._details = {x['id']:x for x in self._bodies }
            for b in self._bodies:
                self._fix_moons(b)
        return self._bodies

    def _fix_single(self, b):
        b['isPlanet'] = b['englishName'].lower() in self._planets
        if b['isPlanet'] and b['englishName'].lower() in self._gas_giants:
            b['planetType'] = 'gas_giant'
        elif b['isPlanet']:
            b['planetType'] = 'planet'
        b['hasLife'] = b['englishName'].lower() == 'earth'
        b['couldSupportLife'] = b['englishName'].lower() in self._could_be_habitable
        b['humansLanded'] = b['englishName'].lower() in self._human_landed_bodies
        b['isHabitable'] = b['englishName'].lower() in self._habitable_bodies
        return b

    def _fix_moons(self, b):
        def fix_moon(m):
            m['id'] = self._index_from_rel(m['rel'])
            m['moon'] = self._details[m['id']]['englishName']
            return m
        if 'moons' in b and b['moons'] is not None:
            b['moons'] = list(map(fix_moon, b['moons'])) 


    def body(self, id):
        if self._bodies is None: self.bodies()
        return self._details[id]

    def _index_from_rel(self, rel):
        return rel[rel.rindex('/') + 1:]

    def measure_distance(self, id1, id2):
        b1 = self.body(id1)
        b2 = self.body(id2)
        assert b1 is not None
        assert b2 is not None

        def sun_distance(b):
            mean = b['semimajorAxis'] 
            min_dd, max_dd = b['perihelion'], b['aphelion']
            if min_dd == 0 or max_dd == 0:
                min_dd = mean
                max_dd = mean
            if 'aroundPlanet' in b and b['aroundPlanet'] is not None:
                min_d, mean_d, max_d = sun_distance(self.body(self._index_from_rel(b['aroundPlanet']['rel'])))
                min_dd += min_d
                max_dd += max_d
                mean += mean_d
            return min_dd, mean, max_dd

        def mean_distance(r1, r2):
            return math.pi / 2 * (r1 + r2) * ellipe(2 * math.sqrt(r1 * r2)/(r1 + r2))

        min_d1, r1, max_d1 = sun_distance(b1)
        min_d2, r2, max_d2 = sun_distance(b2) 
        return abs(min_d1 - min_d2), mean_distance(r1, r2), max_d1 + max_d2 


    def properties(self): 
        return dict(
            gravity=('gravity', lambda x: f'{x / scipy.constants.g:.1f}g'),
            radius=('meanRadius', '%.0fkm'),
            size=('meanRadius', '%.0fkm'),
        )
