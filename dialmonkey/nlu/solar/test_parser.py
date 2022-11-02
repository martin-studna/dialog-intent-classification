from . import parser
import pytest
import os
import re
from logging import getLogger
from dialmonkey.dialogue import Dialogue
from dialmonkey.da import DA, DAI

def assert_acts_equal(act1, act2):
    assert isinstance(act1, str)
    assert isinstance(act2, str)
    int1 = act1[:act1.index('(')]
    int2 = act1[:act2.index('(')]
    assert int1 == int2, f"different intents {act1} != {act2}"
    par1 = act1[act1.index('(') + 1:-1]
    par2 = act2[act2.index('(') + 1:-1]
    par1 = { k:v for k,v in ((x.split('=') if '=' in x else (x,'')) for x in par1.split(','))}
    par2 = { k:v for k,v in ((x.split('=') if '=' in x else (x,'')) for x in par2.split(','))}
    assert all(v == par1[k] for k,v in par2.items()) and len(par1) == len(par2), f"different acts {act1} != {act2}"


def test_tokenize():
    class DummyRepository:
        def bodies(self):
            return [
                dict(englishName='Pluto', isPlanet=True),
                dict(englishName='Europa', isPlanet=False)
            ]
    tokenize = parser.build_tokenize(DummyRepository())
    result, matches = tokenize('pluto is not a planet, europa is a moon')
    assert result == '<object> is not a planet, <object> is a moon'
    assert len(matches) == 2
    assert matches[0] == 'pluto'
    assert matches[1] == 'europa'

def test_tokenize_moons():
    class DummyRepository:
        def bodies(self):
            return [
                dict(englishName='moon'),
            ]
    tokenize = parser.build_tokenize(DummyRepository())
    result, matches = tokenize('moons')
    assert result == 'moons'
    assert len(matches) == 0

@pytest.fixture
def repo():
    from dialmonkey.repositories.solar import SolarRepository
    return SolarRepository()

expression_file = os.path.join(os.path.dirname(__file__), '../../../data/solar-expressions.tsv')
@pytest.mark.parametrize('input,output', [tuple(x.strip().split('\t')) for x in open(expression_file, 'r') if x.strip() != ''])
def test_parse(input, output, repo):
    parse = parser.build_parser()
    x = parser.simplify(input)
    x = parse(x)
    assert x == output


def test_simplify():
    input = 'What, is <object>?'
    assert parser.simplify(input) == 'what , is <object> ?'

def test_solar_nlu_single_slotvalue():
    class DummyRepository:
        def bodies(self):
            return [
                dict(englishName='Jupiter', isPlanet=True),
                dict(englishName='Europa', isPlanet=False)
            ]
    dial = Dialogue()
    dial.set_user_input('How many moons does planet Jupiter have?')
    logger = getLogger()
    component = parser.SolarSystemNLU(repo = DummyRepository())
    dial = component(dial, logger)

    assert dial is not None
    assert isinstance(dial, Dialogue)
    assert dial.nlu is not None
    assert isinstance(dial.nlu, DA)
    assert dial.nlu.to_cambridge_da_string() == 'count_moons(name=jupiter)'

def test_solar_nlu_multiple_slotvalue():
    class DummyRepository:
        def bodies(self):
            return [
                dict(englishName='Jupiter', isPlanet=True),
                dict(englishName='Europa', isPlanet=False)
            ]
    dial = Dialogue()
    dial.set_user_input('What is the size of Jupiter?')
    logger = getLogger()
    component = parser.SolarSystemNLU(repo = DummyRepository())
    dial = component(dial, logger)

    assert dial is not None
    assert isinstance(dial, Dialogue)
    assert dial.nlu is not None
    assert isinstance(dial.nlu, DA)
    assert len(dial.nlu.dais) == 2
    assert dial.nlu.to_cambridge_da_string() == 'request_property(property=size,name=jupiter)'

def test_solar_nlu_invalid():
    class DummyRepository:
        def bodies(self):
            return [
                dict(englishName='Jupiter', isPlanet=True),
                dict(englishName='Europa', isPlanet=False)
            ]
    dial = Dialogue()
    dial.set_user_input('sdfsdfadfsdfasdfgsfgdf')
    logger = getLogger()
    component = parser.SolarSystemNLU(repo = DummyRepository())
    dial = component(dial, logger)

    assert dial is not None
    assert isinstance(dial, Dialogue)
    assert dial.nlu is not None
    assert isinstance(dial.nlu, DA)
    assert len(dial.nlu.dais) == 0
    assert dial.nlu.to_cambridge_da_string() == ''
