import requests
from requests.auth import HTTPBasicAuth
from http import HTTPStatus
from switchbot import config


def post_to_report_state(state):
    """todo: only localhost and ALLOWED_REPORT_STATE_HOST requests should be accepted"""
    url = config.get_api_url()
    r = requests.post(
        f"{url}/state",
        json={
            "state": state
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]


def post_to_request_sync(secret, devices):
    """todo: user_id as API SECRET KEY"""
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', secret)
    r = requests.post(
        f"{url}/sync",
        auth=auth,
        json={
            "userId": secret,
            "devices": devices
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]


def post_to_ctrl_user_dev_onoff(secret, dev_id, dev_onoff):
    """todo:"""
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', secret)
    r = requests.post(
        f'{url}/fulfillment',
        auth=auth,
        json={
            "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
            "inputs": [{
                "intent": "action.devices.EXECUTE",
                "payload": {
                    "commands": [
                        {
                            "devices": [
                                {
                                    "id": f"{dev_id})"
                                },
                            ],
                            "execution": [
                                {
                                    "command": "action.devices.commands.OnOff",
                                    "params": {
                                        "on": f"{dev_onoff}"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }]
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]
    return r


def post_to_query_user_dev_state(secret, dev_id):
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', secret)
    r = requests.post(
        f'{url}/fulfillment',
        auth=auth,
        json={
            "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
            "inputs": [{
                "intent": "action.devices.QUERY",
                "payload": {
                    "devices": [{
                        "id": f"{dev_id}"
                    }]
                }
            }]
        }
    )
    assert r.status_code == HTTPStatus.OK
    assert isinstance(r.json, dict)
    assert r.json.get("requestId") == "ff36a3cc-ec34-11e6-b1a0-64510650abcf"
    assert isinstance(r.json.get("payload"), dict)
    assert isinstance(r.json.get("payload").get("devices"), dict)
    return r


def post_to_query_user_dev_list(secret):
    """todo: embedded user_id into http request header"""
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', secret)
    r = requests.post(
        f'{url}/fulfillment',
        auth=auth,
        json={
            "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
            "inputs": [{
                "intent": "action.devices.SYNC"
            }]
        }
    )
    assert r.status_code in [HTTPStatus.OK]
    assert isinstance(r.json, dict)
    assert r.json.get("requestId") == "ff36a3cc-ec34-11e6-b1a0-64510650abcf"
    assert isinstance(r.json.get("payload"), dict)
    assert r.json.get("payload").get("agentUserId") == secret
    assert isinstance(r.json.get("payload").get("devices"), list)
    return r


def post_to_unsubscribe(secret):
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', secret)
    r = requests.post(
        f'{url}/fulfillment',
        auth=auth,
        json={
            "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
            "inputs": [{
                "intent": "action.devices.DISCONNECT"
            }]
        }
    )
    assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]


def post_to_subscribe(secret, token, expect_success=True):
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', secret)
    r = requests.post(
        f"{url}/subscribe",
        auth=auth,
        json={
            "userSecret": secret,
            "userToken": token
        }
    )
    if expect_success:
        assert r.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.OK]
