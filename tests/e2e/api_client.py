import requests
from http import HTTPStatus
from switchbot import config


def post_to_intent_execute():
    """todo: """
    raise NotImplementedError


def post_to_intent_query():
    """todo: """
    raise NotImplementedError


def post_to_intent_disconnect(user_id):
    """todo: embedded user_id into http request header"""
    url = config.get_api_url()
    r = requests.post(
        f'{url}/fulfillment',
        json={
            "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
            "inputs": [{
                "intent": "action.devices.DISCONNECT"
            }]
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]


def post_to_intent_sync(user_id):
    """todo: embedded user_id into http request header"""
    url = config.get_api_url()
    r = requests.post(
        f'{url}/fulfillment',
        json={
            "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
            "inputs": [{
                "intent": "action.devices.SYNC"
            }]
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]
    response = r.json
    assert isinstance(response, dict)
    assert response.get("requestId") == "ff36a3cc-ec34-11e6-b1a0-64510650abcf"
    assert isinstance(response.get("payload"), dict)
    assert response.get("payload").get("devices", None) is not None
    assert isinstance(response.get("payload").get("devices"), list)


def post_to_report_state(state):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/state",
        json={
            "state": state
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]


def post_to_request_sync(user_id, devices):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/sync",
        json={
            "userId": user_id,
            "devices": devices
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]


def post_to_subscribe(user_id, secret, token, expect_success=True):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/subscribe",
        json={
            "userId": user_id,
            "userSecret": secret,
            "userToken": token
        }
    )
    if expect_success:
        assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]
    return r
