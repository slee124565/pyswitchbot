import requests
from requests.auth import HTTPBasicAuth
from http import HTTPStatus
from switchbot import config


def post_to_intent_execute(user_id, dev_id):
    """todo:"""
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', user_id)
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
                                        "on": True
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
    # response = r.json
    # assert isinstance(response, dict)
    # assert response.get("requestId") == "ff36a3cc-ec34-11e6-b1a0-64510650abcf"
    # assert isinstance(response.get("payload"), dict)
    # assert response.get("payload").get("commands", None) is not None
    # cmds = response.get("payload").get("commands")
    # assert isinstance(cmds, list)
    # assert list(cmds[0].get("ids")) == [dev_id]


def post_to_intent_query(user_id, dev_id):
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', user_id)
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
    return r
    # response = r.json
    # assert isinstance(response, dict)
    # assert response.get("requestId") == "ff36a3cc-ec34-11e6-b1a0-64510650abcf"
    # assert isinstance(response.get("payload"), dict)
    # assert response.get("payload").get("devices", None) is not None
    # states = response.get("payload").get("devices")
    # assert isinstance(states, dict)
    # assert list(states.keys()) == [dev_id]


def post_to_intent_disconnect(user_id):
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', user_id)
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


def post_to_intent_sync(user_id):
    """todo: embedded user_id into http request header"""
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', user_id)
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
    # response = r.json
    # assert isinstance(response, dict)
    # assert response.get("requestId") == "ff36a3cc-ec34-11e6-b1a0-64510650abcf"
    # assert isinstance(response.get("payload"), dict)
    # assert response.get("payload").get("devices", None) is not None
    # assert isinstance(response.get("payload").get("devices"), list)
    return r


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


def post_to_request_sync(user_id, devices):
    """todo: user_id as API SECRET KEY"""
    url = config.get_api_url()
    auth = HTTPBasicAuth('secret', user_id)
    r = requests.post(
        f"{url}/sync",
        auth=auth,
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
