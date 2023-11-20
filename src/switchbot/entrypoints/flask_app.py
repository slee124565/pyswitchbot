import logging
import json
import base64
from http import HTTPStatus

import requests
from flask import Flask, jsonify, request, url_for, redirect
import logging.config as logging_config
from switchbot.domain import commands
from switchbot.service_layer import unit_of_work
from switchbot.adapters import iot_api_server
from switchbot.service_layer.handlers import InvalidSrcServer
from switchbot import bootstrap, views, config

logging_config.dictConfig(config.logging_config)
logger = logging.getLogger(__name__)
app = Flask(__name__)
bus = bootstrap.bootstrap(
    uow=unit_of_work.JsonFileUnitOfWork(),
    start_orm=False,
    iot=iot_api_server.SwitchBotApiServer()
)
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
    logger.debug(f'auth_header {auth_header}')
    # if not auth_header:
    #     raise ApiAccessTokenError
    auth_type, auth_string = auth_header.split(' ')
    # if auth_type != 'Basic':
    #     raise ApiAccessTokenError
    base64_bytes = base64.b64decode(auth_string)
    decoded_string = base64_bytes.decode('utf-8')
    api_key, user_secret = decoded_string.split(':', 1)
    if api_key == 'OAUTH':
        return json.loads(user_secret)
    else:
        return decoded_string
    # # Base64解碼
    # # 獲取 api_key 和 user_secret
    # if api_key != 'secret':
    #     raise ApiAccessTokenError
    # return api_key, user_secret


@app.route('/fulfillment', methods=['POST'])
def fulfillment():
    try:
        # check request access token
        token = _check_api_access_token(http_request=request)
        logger.debug(f'token: {token}')
        assert isinstance(token, dict)
        post_data = request.json
        assert isinstance(post_data, dict)
        uid = token.get('uid')
        subscriber_id = token.get('subscriber_id')
        logger.debug(f'request token (uid, subscriber_id) {uid, subscriber_id}')

        # create cmd according to IntentID
        request_id = post_data.get("requestId")
        intent_id = post_data.get("inputs")[0].get("intent")
        response = {
            "requestId": request_id,
            "payload": {},
        }

        # response according to fulfillment
        logger.info(f'request {request.json}')
        if intent_id == "action.devices.SYNC":
            _payload = views.get_user_sync_intent_fulfillment(
                uid=uid,
                subscriber_id=subscriber_id,
                request_id=request_id,
                uow=bus.uow
            )
            response.get("payload").update(_payload)
            logger.info(f'response {response}')
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.QUERY":
            _payload = views.get_user_query_intent_fulfillment(
                uid=uid,
                subscriber_id=subscriber_id,
                devices_dto=post_data.get("inputs")[0].get("payload").get("devices"),
                uow=bus.uow
            )
            response.get("payload").update(_payload)
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.EXECUTE":
            aog_cmds_dto = post_data.get("inputs")[0].get("payload").get("commands")
            cmd = commands.ExecAoGCmds(
                uid=uid,
                subscriber_id=subscriber_id,
                aog_cmds_dto=aog_cmds_dto
            )
            bus.handle(cmd)
            _payload = views.get_user_exec_intent_fulfillment(
                uid=uid,
                subscriber_id=subscriber_id,
                aog_cmds_dto=aog_cmds_dto,
                uow=bus.uow
            )
            response.get("payload").update(_payload)
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.DISCONNECT":
            cmd = commands.Unsubscribe(uid=uid, subscriber_id=subscriber_id)
            bus.handle(cmd)
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
        _check_api_access_token(http_request=request)
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
        _check_api_access_token(http_request=request)
        cmd = commands.ReportState(
            uid=request.json.get('userId'),
            state=request.json.get("state"))
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
        _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.RequestSync(
            uid=data.get('userId'),
            devices=data.get('devices')
        )
        bus.handle(cmd)
        return redirect(f"{url_for('profile')}?u={data.get('userId')}")

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        # check request access token
        _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.Subscribe(
            uid=data.get('userId'),
            subscriber_id=data.get('subscriberId')
        )
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.ACCEPTED

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/unregister', methods=['POST'])
def unregister():
    try:
        # check request access token
        _check_api_access_token(http_request=request)
        data = request.json

        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.Unregister(
            uid=data.get('userId'),
        )
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.ACCEPTED

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/profile', methods=['GET'])
def profile():
    try:
        # check request access token
        _check_api_access_token(http_request=request)
        user_secret = request.args.get('s', default=None, type=str)
        user_id = request.args.get('u', default=None, type=str)
        if user_secret:
            return jsonify(views.user_profile_by_secret(
                secret=user_secret,
                uow=bus.uow
            )), HTTPStatus.OK
        elif user_id:
            return jsonify(views.user_profile_by_uid(
                uid=user_id,
                uow=bus.uow
            )), HTTPStatus.OK
    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/register', methods=['POST'])
def register():
    try:
        # check request access token
        _check_api_access_token(http_request=request)
        data = request.json
        if not isinstance(data, dict):
            return jsonify({}), HTTPStatus.BAD_REQUEST

        cmd = commands.Register(
            token=data.get('userToken'),
            secret=data.get('userSecret')
        )
        bus.handle(cmd)
        return redirect(f"{url_for('profile')}?s={data.get('userSecret')}")

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


if __name__ == '__main__':
    """todo: debug flag should be assigned by config module"""
    app.run(debug=True)
