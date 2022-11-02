from .rule_solar import SolarRuleDST
from ..da import DAI, DA
import pytest
import json
import logging

def create_logger():
    return logging.getLogger()

def test_food_from_existing():
    dst = SolarRuleDST()
    da = DA()
    da.append(DAI('request', 'food', 'Chinese', 0.7))
    da.append(DAI('request', 'food', 'Italian', 0.2))
    result = dst(dict(nlu = da, state=dict(food={None:0.8, 'Chinese': 0.2})), create_logger())

    assert result['state'] is not None
    assert type(result['state']) == dict
    assert 'food' in result['state']
    assert isinstance(result['state'], dict)

    # Fix for approx equal 
    result['state']['food'] = { k: round(v, 5) for k, v in result['state']['food'].items() }
    result['state'] = {k2: { (k if k is not None else 'none'): v for k,v in v2.items() } for k2, v2 in result['state'].items()}
    assert json.dumps(result['state'], sort_keys=True) == json.dumps(dict(food={'none':0.08, 'Italian':0.2,'Chinese':0.72}), sort_keys = True)
    
def test_food_from_empty_state():
    dst = SolarRuleDST()
    da = DA()
    da.append(DAI('request', 'food', 'Chinese', 0.7))
    da.append(DAI('request', 'food', 'Italian', 0.2))
    result = dst(dict(nlu = da, state=None), create_logger())

    assert result['state'] is not None
    assert type(result['state']) == dict
    assert 'food' in result['state']
    assert isinstance(result['state'], dict)

    # Fix for approx equal
    result['state']['food'] = { k: round(v, 5) for k, v in result['state']['food'].items() }
    result['state'] = {k2: { (k if k is not None else 'none'): v for k,v in v2.items() } for k2, v2 in result['state'].items()}
    assert json.dumps(result['state'], sort_keys=True) == json.dumps(dict(food={'none':0.1, 'Italian':0.2,'Chinese':0.7}), sort_keys = True)
    
def test_food_from_empty_slot():
    dst = SolarRuleDST()
    da = DA()
    da.append(DAI('request', 'food', 'Chinese', 0.7))
    da.append(DAI('request', 'food', 'Italian', 0.2))
    result = dst(dict(nlu = da, state=dict(test=dict())), create_logger())

    assert result['state'] is not None
    assert type(result['state']) == dict
    assert 'food' in result['state']
    assert isinstance(result['state'], dict)

    # Fix for approx equal
    result['state']['food'] = { k: round(v, 5) for k, v in result['state']['food'].items() }
    result['state'] = {k2: { (k if k is not None else 'none'): v for k,v in v2.items() } for k2, v2 in result['state'].items()}
    assert json.dumps(result['state'], sort_keys=True) == json.dumps(dict(test=dict(), food={'none':0.1, 'Italian':0.2,'Chinese':0.7}), sort_keys = True)
    

def test_bugfix10():
    da = DA.parse('negate()/1.000&negate(area=dontcare)/0.579&negate(type=restaurant)/0.564&negate(food=indian)/0.920')
    print(da)
    state = {'food': {None: 0.0684892960121275, 'chinese': 0.9315107039878725}}
    dst = SolarRuleDST()
    result = dst(dict(nlu = da, state=state), create_logger())

