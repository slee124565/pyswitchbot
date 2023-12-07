import abc
import json
import time
import hashlib
import hmac
import base64
import uuid
import os
import logging
import requests
from typing import List, Set, Union
from http import HTTPStatus
from switchbot.domain import model

# from switchbot.domain.model import SwitchBotDevice, SwitchBotStatus, SwitchBotScene

logger = logging.getLogger(__name__)
SWITCHBOT_API_URI = os.getenv('SWITCHBOT_API_URI', 'https://api.switch-bot.com')


class SwitchBotAPIServerError(Exception):
    pass


class SwitchBotAPIResponseError(Exception):
    pass


class AbstractIotApiServer(abc.ABC):
    def get_dev_list(self, secret: str, token: str) -> List[model.SwitchBotDevice]:
        raise NotImplementedError

    def get_dev_status(self, secret: str, token: str, dev_id: str) -> model.SwitchBotStatus:
        raise NotImplementedError

    def send_dev_ctrl_cmd(self, secret: str, token: str, dev_id: str, cmd_type: str, cmd_value: str,
                          cmd_param: Union[str, dict]):
        raise NotImplementedError

    def get_scene_list(self, secret: str, token: str) -> List[model.SwitchBotScene]:
        raise NotImplementedError

    def exec_manual_scene(self, secret: str, token: str, scene_id: str):
        raise NotImplementedError

    def create_webhook_config(self, secret: str, token: str, url: str):
        raise NotImplementedError

    def read_webhook_config(self, secret: str, token: str) -> List[str]:
        raise NotImplementedError

    def read_webhook_config_list(self, secret: str, token: str, url_list: List[str]):
        raise NotImplementedError

    def update_webhook_config(self, secret: str, token: str, url: str, enable: bool):
        raise NotImplementedError

    def delete_webhook_config(self, secret: str, token: str, url: str):
        raise NotImplementedError

    # def report_event(self, evt_type: str, evt_version: str, evt_context: dict):
    #     raise NotImplementedError


class SwitchBotApiServer(AbstractIotApiServer):
    def __init__(self):
        self.api_uri = SWITCHBOT_API_URI

    @staticmethod
    def _get_auth_headers(secret: str, token: str, nonce=None):
        # Declare empty header dictionary
        headers = {}
        # open token
        # token = token
        # secret key
        # secret = secret
        # nonce
        nonce = uuid.uuid4() if not nonce else nonce
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(token, t, nonce)

        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(secret, 'utf-8')

        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
        # print('Authorization: {}'.format(token))
        # print('t: {}'.format(t))
        # print('sign: {}'.format(str(sign, 'utf-8')))
        # print('nonce: {}'.format(nonce))

        # Build api header JSON
        headers['Authorization'] = token
        headers['Content-Type'] = 'application/json'
        headers['charset'] = 'utf8'
        headers['t'] = str(t)
        headers['sign'] = str(sign, 'utf-8')
        headers['nonce'] = str(nonce)
        logger.debug(f'http headers {json.dumps(headers)}')
        return headers

    def _get(self, endpoint: str, secret: str, token: str, params: dict = None):
        try:
            headers = self._get_auth_headers(secret, token)
            if params:
                resp = requests.get(
                    url=f'{self.api_uri}{endpoint}',
                    headers=headers,
                    params=params
                )
            else:
                resp = requests.get(
                    url=f'{self.api_uri}{endpoint}',
                    headers=headers
                )

            if resp.status_code != HTTPStatus.OK:
                resp.raise_for_status()

            logger.info(f'GET,{endpoint},{params},{resp.json()}')
            return resp.json().get('body')
        except Exception:
            raise SwitchBotAPIServerError

    def _post(self, secret: str, token: str, endpoint: str, data: dict):
        try:
            headers = self._get_auth_headers(secret, token)
            # logger.debug(f'POST request {data}')
            resp = requests.post(
                url=f'{self.api_uri}{endpoint}',
                headers=headers,
                json=data
            )

            if resp.status_code != HTTPStatus.OK:
                resp.raise_for_status()

            logger.info(f'POST,{endpoint},{data},{resp.json()}')
            return resp.json().get('body')
        except Exception:
            raise SwitchBotAPIServerError

    def get_dev_list(self, secret: str, token: str) -> List[model.SwitchBotDevice]:
        resp_body = self._get(
            endpoint='/v1.1/devices',
            secret=secret,
            token=token
        )
        _dev_list = []
        for _data in resp_body.get('deviceList'):
            _dev_list.append(model.SwitchBotDevice.load(_data))
        for _data in resp_body.get('infraredRemoteList'):
            # assert isinstance(_data, dict)
            # _dev_list.append(model.SwitchBotDevice(**_data))
            raise NotImplementedError
        return _dev_list

    def send_dev_ctrl_cmd(self, secret: str, token: str, dev_id: str, cmd_type: str, cmd_value: str,
                          cmd_param: Union[str, dict]):
        resp_body = self._post(
            secret=secret,
            token=token,
            endpoint=f'/v1.1/devices/{dev_id}/commands',
            data={
                "commandType": cmd_type,
                "command": cmd_value,
                "parameter": cmd_param
            }
        )
        return resp_body.values() if isinstance(resp_body, dict) else resp_body

    def get_dev_status(self, secret: str, token: str, dev_id: str) -> model.SwitchBotStatus:
        resp_body = self._get(
            endpoint=f'/v1.1/devices/{dev_id}/status',
            secret=secret,
            token=token
        )
        return model.SwitchBotStatus.load(resp_body)

    def get_scene_list(self, secret: str, token: str) -> List[model.SwitchBotScene]:
        resp_body = self._get(
            endpoint=f'/v1.1/scenes',
            secret=secret,
            token=token
        )
        if not isinstance(resp_body, list):
            raise SwitchBotAPIResponseError
        return [model.SwitchBotScene.load(data) for data in resp_body]

    def exec_manual_scene(self, secret: str, token: str, scene_id: str):
        resp_body = self._post(
            endpoint=f'/v1.1/scenes/{scene_id}/execute',
            secret=secret,
            token=token,
            data={}
        )
        return resp_body

    def create_webhook_config(self, secret: str, token: str, url: str):
        resp_body = self._post(
            endpoint=f'/v1.1/webhook/setupWebhook',
            secret=secret,
            token=token,
            data={
                "action": "setupWebhook",
                "url": url,
                "deviceList": "ALL"
            }
        )
        if not isinstance(resp_body, dict):
            raise SwitchBotAPIResponseError
        return resp_body

    def read_webhook_config(self, secret: str, token: str) -> List[str]:
        resp_body = self._post(
            endpoint=f'/v1.1/webhook/queryWebhook',
            secret=secret,
            token=token,
            data={"action": "queryUrl"}
        )
        if not isinstance(resp_body, dict):
            raise SwitchBotAPIResponseError
        _config = resp_body.get('urls', [])
        return _config

    def read_webhook_config_list(self, secret: str, token: str, url_list: List[str]):
        resp_body = self._post(
            endpoint=f'/v1.1/webhook/queryWebhook',
            secret=secret,
            token=token,
            data={
                "action": "queryDetails",
                "urls": url_list
            }
        )
        return resp_body

    def update_webhook_config(self, secret: str, token: str, url: str, enable: bool):
        resp_body = self._post(
            endpoint=f'/v1.1/webhook/updateWebhook',
            secret=secret,
            token=token,
            data={
                "action": "updateWebhook",
                "config": {
                    "url": url,
                    "enable": True
                }
            }
        )
        return resp_body

    def delete_webhook_config(self, secret: str, token: str, url: str):
        resp_body = self._post(
            endpoint=f'/v1.1/webhook/deleteWebhook',
            secret=secret,
            token=token,
            data={
                "action": "deleteWebhook",
                "url": url
            }
        )
        return resp_body


class FakeApiServer(AbstractIotApiServer):
    """todo: response by fixed data"""

    def __init__(self):
        self.dev_ctrl_cmd_sent = False

    def get_dev_list(self, secret: str, token: str) -> List[model.SwitchBotDevice]:
        devices = [
            {
                "deviceId": "6055F92FCFD2",
                "deviceName": "小風扇開關",
                "deviceType": "Plug Mini (US)",
                "enableCloudService": True,
                "hubDeviceId": ""
            },
            {
                "deviceId": "6055F930FF22",
                "deviceName": "風扇開關",
                "deviceType": "Plug Mini (US)",
                "enableCloudService": True,
                "hubDeviceId": ""
            }
        ]
        return [model.SwitchBotDevice.load(d) for d in devices]

    def get_dev_status(self, secret: str, token: str, dev_id: str) -> model.SwitchBotStatus:
        scenes = [
            {
                "deviceId": "6055F92FCFD2",
                "deviceType": "Plug Mini (US)",
                "hubDeviceId": "6055F92FCFD2",
                "power": "off",
                "version": "V1.4-1.4",
                "voltage": 112.2,
                "weight": 0.0,
                "electricityOfDay": 43,
                "electricCurrent": 0.0
            },
            {
                "deviceId": "6055F930FF22",
                "deviceType": "Plug Mini (US)",
                "hubDeviceId": "6055F930FF22",
                "power": "on",
                "version": "V1.4-1.4",
                "voltage": 112.2,
                "weight": 35.0,
                "electricityOfDay": 184,
                "electricCurrent": 3.09
            }

        ]
        for d in scenes:
            if d.get('deviceId') == dev_id:
                return model.SwitchBotStatus.load(d)

    def send_dev_ctrl_cmd(self, secret: str, token: str, dev_id: str, cmd_type: str, cmd_value: str,
                          cmd_param: Union[str, dict]):
        self.dev_ctrl_cmd_sent = True

    def get_scene_list(self, secret: str, token: str) -> List[model.SwitchBotScene]:
        scenes = [
            {
                "sceneId": "T01-202309291436-01716250",
                "sceneName": "allOff"
            }
        ]
        return [model.SwitchBotScene.load(d) for d in scenes]

    def exec_manual_scene(self, secret: str, token: str, scene_id: str):
        raise NotImplementedError

    def create_webhook_config(self, secret: str, token: str, url: str):
        raise NotImplementedError

    def read_webhook_config(self, secret: str, token: str) -> List[str]:
        raise NotImplementedError

    def read_webhook_config_list(self, secret: str, token: str, url_list: List[str]):
        raise NotImplementedError

    def update_webhook_config(self, secret: str, token: str, url: str, enable: bool):
        return {'statusCode': 100, 'body': {}, 'message': 'success'}

    def delete_webhook_config(self, secret: str, token: str, url: str):
        raise NotImplementedError
