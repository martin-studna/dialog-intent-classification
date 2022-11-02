from .solar import build_nlg
from dialmonkey.da import DA, DAI

def test_any_response():
    nlg = build_nlg([('test()', 'ok')])
    assert 'ok' == nlg(DA.parse_cambridge_da('test()')) 

def test_any_response():
    nlg = build_nlg([('test()', 'ok'), ('test()', 'cool')])
    responses = set()
    for _ in range(100):
        responses.add(nlg(DA.parse_cambridge_da('test()')))
    assert len(responses) == 2
    assert 'ok' in responses
    assert 'cool' in responses

def test_replace_placeholder():
    nlg = build_nlg([('test(name={name})', 'ok {name}')])
    assert 'ok jonas' == nlg(DA.parse_cambridge_da('test(name=jonas)')) 

def test_prioritize_specific_value():
    nlg = build_nlg([
        ('inform(price=cheap)', "You'll save money here."),
        ('inform(price={price})', "This place is {price}.")])

    responses = set()
    for _ in range(100):
        responses.add(nlg(DA.parse_cambridge_da('inform(price=cheap)')))
    assert len(responses) == 1
    assert "You'll save money here." in responses

def test_concatenate_multiple_templates():
    nlg = build_nlg([
        ('inform(price={price})', 'price: {price}.'),
        ('inform(rating={rating})', 'rating: {rating}.')])

    responses = set()
    for _ in range(100):
        responses.add(nlg(DA.parse_cambridge_da('inform(price=cheap,rating=good)')))
    assert len(responses) == 2
    assert 'price: cheap. rating: good.' in responses
    assert 'rating: good. price: cheap.' in responses

def test_prioritize_longer_templates():
    nlg = build_nlg([
        ('inform(price={price})', 'price: {price}.'),
        ('inform(price={price},rating={rating})', 'price: {price} and rating: {rating}.'),
        ('inform(rating={rating})', 'rating: {rating}.')])

    responses = set()
    for _ in range(100):
        responses.add(nlg(DA.parse_cambridge_da('inform(price=cheap,rating=good)')))
    assert len(responses) == 1
    assert 'price: cheap and rating: good.' in responses

