import logging
import base64
from http import HTTPStatus

import requests
from flask import Flask, jsonify, request
from switchbot.domain import commands
from switchbot.service_layer.handlers import InvalidSrcServer
from switchbot import bootstrap, config  # views

logger = logging.getLogger(__name__)
app = Flask(__name__)
bus = bootstrap.bootstrap()
seudo_sync_payload = {
    "agentUserId": "1836.15267389",
    "devices": [
        {
            "id": "123",
            "type": "action.devices.types.OUTLET",
            "traits": [
                "action.devices.traits.OnOff"
            ],
            "name": {
                "defaultNames": [
                    "My Outlet 1234"
                ],
                "name": "Night light",
                "nicknames": [
                    "wall plug"
                ]
            },
            "willReportState": False,
            "roomHint": "kitchen",
            "deviceInfo": {
                "manufacturer": "lights-out-inc",
                "model": "hs1234",
                "hwVersion": "3.2",
                "swVersion": "11.4"
            },
            "otherDeviceIds": [
                {
                    "deviceId": "local-device-id"
                }
            ],
            "customData": {
                "fooValue": 74,
                "barValue": True,
                "bazValue": "foo"
            }
        },
        {
            "id": "456",
            "type": "action.devices.types.LIGHT",
            "traits": [
                "action.devices.traits.OnOff",
                "action.devices.traits.Brightness",
                "action.devices.traits.ColorSetting"
            ],
            "name": {
                "defaultNames": [
                    "lights out inc. bulb A19 color hyperglow"
                ],
                "name": "lamp1",
                "nicknames": [
                    "reading lamp"
                ]
            },
            "willReportState": False,
            "roomHint": "office",
            "attributes": {
                "colorModel": "rgb",
                "colorTemperatureRange": {
                    "temperatureMinK": 2000,
                    "temperatureMaxK": 9000
                },
                "commandOnlyColorSetting": False
            },
            "deviceInfo": {
                "manufacturer": "lights out inc.",
                "model": "hg11",
                "hwVersion": "1.2",
                "swVersion": "5.4"
            },
            "customData": {
                "fooValue": 12,
                "barValue": False,
                "bazValue": "bar"
            }
        }
    ]
}
seudo_query_payload = {
    "devices": {
        "123": {
            "on": True,
            "online": True,
            "status": "SUCCESS"
        },
        "456": {
            "on": True,
            "online": True,
            "status": "SUCCESS",
            "brightness": 80,
            "color": {
                "spectrumRgb": 16711935
            }
        }
    }
}
seudo_execute_payload = {
    "commands": [
        {
            "ids": [
                "123"
            ],
            "status": "SUCCESS",
            "states": {
                "on": True,
                "online": True
            }
        },
        {
            "ids": [
                "456"
            ],
            "status": "ERROR",
            "errorCode": "deviceTurnedOff"
        }
    ]
}


class ApiAccessTokenError(Exception):
    pass


def _check_api_access_token(http_request: requests.Request):
    """basic auth with ('secret', {user switchbot secret})
    todo: revise to api access token instead of user secret
    """
    auth_header = http_request.headers.get('Authorization')
    if not auth_header:
        raise ApiAccessTokenError
    auth_type, auth_string = auth_header.split(' ')
    if auth_type != 'Basic':
        raise ApiAccessTokenError
    # Base64解碼
    base64_bytes = base64.b64decode(auth_string)
    decoded_string = base64_bytes.decode('utf-8')
    # 獲取 api_key 和 user_secret
    api_key, user_secret = decoded_string.split(':')
    if api_key != 'secret':
        raise ApiAccessTokenError
    return api_key, user_secret


@app.route('/fulfillment', methods=['POST'])
def fulfillment():
    try:
        # check request access token
        api_key, user_secret = _check_api_access_token(http_request=request)
        data = request.json

        # create cmd according to IntentID
        request_id = data.get("requestId")
        intent_id = data.get("inputs")[0].get("intent")
        response = {
            "requestId": request_id,
            "payload": {},
        }

        # response according to fulfillment
        if intent_id == "action.devices.SYNC":
            response.get("payload").update(seudo_sync_payload)
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.QUERY":
            response.get("payload").update(seudo_query_payload)
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.EXECUTE":
            response.get("payload").update(seudo_execute_payload)
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.DISCONNECT":
            return jsonify({}), HTTPStatus.OK
        else:
            return jsonify({}), HTTPStatus.BAD_REQUEST

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/change', methods=['POSST'])
def report_change():
    try:
        api_key, user_secret = _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.ReportChange(change=request.json)
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.OK

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/state', methods=['POST'])
def report_state():
    try:
        # check request access token
        api_key, user_secret = _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.ReportState(state=request.json)
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.OK

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/sync', methods=['POST'])
def request_sync():
    try:
        # check request access token
        api_key, user_secret = _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.RequestSync(
            user_id=data.get('userId'),
            devices=data.get('devices')
        )
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.OK

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        # check request access token
        api_key, user_secret = _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.Register(
            user_id=data.get('userId'),
            token=data.get('userToken'),
            secret=data.get('userSecret')
        )
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.ACCEPTED

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


if __name__ == '__main__':
    app.run(debug=True)
