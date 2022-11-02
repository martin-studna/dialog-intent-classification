from . import policy
import pytest
import os
import re
from logging import getLogger
from dialmonkey.dialogue import Dialogue
from dialmonkey.da import DA, DAI

@pytest.fixture(scope='module')
def repo():
    from dialmonkey.repositories.solar import SolarRepository
    return SolarRepository()

@pytest.fixture
def logger():
    return getLogger()

expression_file = os.path.join(os.path.dirname(__file__), '../../../data/solar-expressions.tsv')
@pytest.mark.parametrize('input,output', [tuple(x.strip().split('\t')) for x in open(expression_file, 'r') if x.strip() != ''])
def test_does_not_fail(input, output, repo, logger):
    component = policy.SolarPolicy(repo = repo)
    dial = Dialogue()
    dial.nlu = DA.parse_cambridge_da(output)
    for x in dial.nlu.dais:
        dial.state[x.slot] = { x.value: 1.0, None: 0.0 }
    dial = component(dial, logger)

    assert dial is not None
    assert isinstance(dial, Dialogue)
    assert dial.action is not None
    assert dial.action.to_cambridge_da_string() != ''

