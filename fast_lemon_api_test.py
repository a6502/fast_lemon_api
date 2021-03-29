#!/usr/bin/env pytest-3

from fastapi.testclient import TestClient

from fast_lemon_api import app

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Welcome to the fast-lemon-api!\n"


neworder = {
    "isin": "blablablabla",
    "limit_price": 0.2,
    "side": "buy",
    "quantity": 1,
    "valid_until": 1996943663,
    "status": "open"
}

order_id = None


def test_post_orders1():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablabla",
                               "limit_price": 0.2,
                               "side": "buy",
                               "quantity": 1,
                               "valid_until": 1996943663,
                           })
    assert response.status_code == 201
    j = response.json()
    #print(repr(j))
    order_id = j.pop('uuid')
    assert j == neworder
    #assert 0


def test_post_orders2():
    response = client.post('/orders/',
                           json={
                               "isin": "blablabla",
                               "limit_price": 0.2,
                               "side": "buy",
                               "quantity": 1,
                               "valid_until": 1996950863
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'loc': ['body', 'isin'],
            'msg': 'ensure this value has at least 12 characters',
            'type': 'value_error.any_str.min_length',
            'ctx': {
                'limit_value': 12
            }
        }]
    }


def test_post_orders3():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablablabla",
                               "limit_price": 0.2,
                               "side": "buy",
                               "quantity": 1,
                               "valid_until": 1996950863
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'ctx': {
                'limit_value': 12
            },
            'loc': ['body', 'isin'],
            'msg': 'ensure this value has at most 12 characters',
            'type': 'value_error.any_str.max_length'
        }]
    }


def test_post_orders4():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablabla",
                               "limit_price": -1,
                               "side": "buy",
                               "quantity": 1,
                               "valid_until": 1996950863
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'ctx': {
                'limit_value': 0
            },
            'loc': ['body', 'limit_price'],
            'msg': 'ensure this value is greater than 0',
            'type': 'value_error.number.not_gt'
        }]
    }


def test_post_orders5():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablabla",
                               "limit_price": 0.2,
                               "side": "BUY!",
                               "quantity": 1,
                               "valid_until": 1996950863
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'ctx': {
                'enum_values': ['buy', 'sell']
            },
            'loc': ['body', 'side'],
            'msg':
            "value is not a valid enumeration member; permitted: 'buy', 'sell'",
            'type': 'type_error.enum'
        }]
    }


def test_post_orders6():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablabla",
                               "limit_price": 0.33333,
                               "side": "SELL",
                               "quantity": 0,
                               "valid_until": 1996950863
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'ctx': {
                'limit_value': 0
            },
            'loc': ['body', 'quantity'],
            'msg': 'ensure this value is greater than 0',
            'type': 'value_error.number.not_gt'
        }]
    }


def test_post_orders8():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablabla",
                               "limit_price": 0.2,
                               "side": "SELL",
                               "quantity": 1.1,
                               "valid_until": 1996950863
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'loc': ['body', 'quantity'],
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer'
        }]
    }


def test_post_orders7():
    response = client.post('/orders/',
                           json={
                               "isin": "blablablabla",
                               "limit_price": 0.2,
                               "side": "SELL",
                               "quantity": 2,
                               "valid_until": 1996
                           })
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{
            'loc': ['body', 'valid_until'],
            'msg': 'valid_until cannot be in the past',
            'type': 'value_error'
        }]
    }
