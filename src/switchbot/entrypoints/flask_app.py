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
from switchbot import bootstrap, views, config, gh_intent

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

        # response according to fulfillment
        logger.info(f'post_data {post_data}')
        logger.debug(f"{intent_id}, {subscriber_id}, {uid}, {request_id}")
        if intent_id == "action.devices.SYNC":
            response = views.user_sync_intent_fulfillment(
                uid=uid,
                subscriber_id=subscriber_id,
                request_id=request_id,
                uow=bus.uow
            )
            logger.info(f"FULFILLMENT {request_id}, {response}")
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.QUERY":
            gh_query_dto = gh_intent.QueryRequest.load(post_data)
            response = views.user_query_intent_fulfillment(
                uid=uid,
                subscriber_id=subscriber_id,
                gh_query_dto=gh_query_dto,
                uow=bus.uow
            )
            logger.info(f"FULFILLMENT {request_id}, {response}")
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.EXECUTE":
            gh_execute_dto = gh_intent.ExecuteRequest.load(post_data)
            assert isinstance(gh_execute_dto, gh_intent.ExecuteRequest)
            assert len(gh_execute_dto.inputs) == 1
            _responses_dto = []
            for cmd_dto in gh_execute_dto.inputs[0].payload.commands:
                assert isinstance(cmd_dto, gh_intent.ExecuteCmdItem)
                for cmd_exec_dto in cmd_dto.execution[:1]:
                    logger.debug(f"cmd_exec_dto type {type(cmd_exec_dto)}")
                    assert isinstance(cmd_exec_dto, gh_intent.ExecuteCmdExecItem)
                    if cmd_exec_dto.command == "action.devices.commands.OnOff":
                        _cmd_type = 'command'
                        _cmd_value = 'turnOn' if cmd_exec_dto.params.get("on") else 'turnOff'
                        _cmd_param = 'default'
                        cmd_devs_dto = cmd_dto.devices
                        for cmd_dev_dto in cmd_devs_dto:
                            cmd = commands.SendDevCtrlCmd(
                                uid=uid,
                                subscriber_id=subscriber_id,
                                dev_id=cmd_dev_dto.id,
                                cmd_type=_cmd_type,
                                cmd_value=_cmd_value,
                                cmd_param=_cmd_param
                            )
                            bus.handle(cmd)
                            _cmd_resp_dto = gh_intent.ExecuteCommandResponseItem(
                                ids=[f"{cmd_dev_dto.id}"],
                                status="PENDING",
                                states={
                                    "online": True,
                                    "on": True if cmd_exec_dto.params.get("on") else False
                                }
                            )
                            _responses_dto.append(_cmd_resp_dto)
                    else:
                        raise NotImplementedError
            response = gh_intent.ExecuteResponse(
                requestId=gh_execute_dto.requestId,
                payload=gh_intent.ExecuteResponsePayload(
                    commands=_responses_dto
                )
            ).dump()
            logger.info(f"FULFILLMENT {request_id}, {response}")
            return jsonify(response), HTTPStatus.OK
        elif intent_id == "action.devices.DISCONNECT":
            cmd = commands.Unsubscribe(uid=uid, subscriber_id=subscriber_id)
            bus.handle(cmd)
            logger.info(f"FULFILLMENT {request_id}")
            return jsonify({}), HTTPStatus.OK
        else:
            logger.warning(f"INTENT_ID invalid, {post_data}")
            return jsonify({}), HTTPStatus.BAD_REQUEST

    except ApiAccessTokenError:
        return jsonify({}), HTTPStatus.UNAUTHORIZED
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


@app.route('/change', methods=['POST'])
def report_change():
    """todo: check client domain in allowed host"""
    try:
        # _check_api_access_token(http_request=request)
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


def main():
    app.run(
        host="localhost",
        debug=True,
        threaded=True
    )


if __name__ == '__main__':
    """todo: debug flag should be assigned by config module"""
    main()
