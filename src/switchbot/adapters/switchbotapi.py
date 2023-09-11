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
from typing import List, Set
from http import HTTPStatus
from switchbot.domain import model
from switchbot.domain import commands

logger = logging.getLogger(__name__)
SWITCHBOT_API_URI = os.getenv('SWITCHBOT_API_URI', 'https://api.switch-bot.com')


class SwitchBotAPIServerError(Exception):
    pass


class AbstractSwitchBotApiServer(abc.ABC):
    def __init__(self, secret, token):
        self.secret = secret
        self.token = token
        self.api_uri = SWITCHBOT_API_URI
        self.seen = set()  # type:Set[model.SwitchBotDevice]

    def _get(self, endpoint: str, params: dict = None):
        raise NotImplementedError

    def _post(self, endpoint: str, data: dict):
        raise NotImplementedError

    def get_dev_list(self) -> List[model.SwitchBotDevice]:
        raise NotImplementedError

    def get_dev_status(self, dev_id: str) -> model.SwitchBotDeviceStatus:
        raise NotImplementedError

    def send_dev_ctrl_cmd(self, dev_cmd: commands.SwitchBotDevCmd):
        raise NotImplementedError

    def get_scene_list(self):
        raise NotImplementedError

    def exec_scene(self, scene_id):
        raise NotImplementedError

    def config_webhook(self, uri):
        raise NotImplementedError

    def get_webhook_config(self):
        raise NotImplementedError

    def update_webhook_config(self, uri):
        raise NotImplementedError

    def delete_webhook_config(self):
        raise NotImplementedError

    def _get_auth_headers(self, nonce=None):
        # Declare empty header dictionary
        headers = {}
        # open token
        token = self.token
        # secret key
        secret = self.secret
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
        logger.debug(f'API headers {json.dumps(headers)}')
        return headers


class SwitchBotHttpApiServer(AbstractSwitchBotApiServer):
    def _get(self, endpoint: str, params: dict = None):
        try:
            headers = self._get_auth_headers()
            if params:
                resp = requests.get(
                    url=f'{self.api_uri}{endpoint}',
                    headers=headers,
                    params=params
                )
            else:
                resp = requests.get(
                    url=f'{self.api_uri}{endpoint}',
                    headers=headers,
                )

            if resp.status_code != HTTPStatus.OK:
                resp.raise_for_status()

            return resp.json()
        except Exception as err:
            raise SwitchBotAPIServerError(err)

    def _post(self, endpoint: str, data: dict):
        try:
            headers = self._get_auth_headers()
            resp = requests.post(
                url=f'{self.api_uri}{endpoint}',
                headers=headers,
                data=data
            )
            if resp.status_code != HTTPStatus.OK:
                resp.raise_for_status()

            return resp.json()
        except Exception as err:
            raise SwitchBotAPIServerError(err)

    def get_dev_list(self) -> List[model.SwitchBotDevice]:
        resp_body = self._get(endpoint='/v1.1/devices')
        _dev_list = []
        for _data in resp_body.get('deviceList', []):
            assert isinstance(_data, dict)
            _data.update({'deviceBaseType': 'deviceList'})
            _dev_list.append(model.SwitchBotDevice(**_data))
        for _data in resp_body.get('infraredRemoteList', []):
            assert isinstance(_data, dict)
            _data.update({'deviceBaseType': 'infraredRemoteList'})
            _dev_list.append(model.SwitchBotDevice(**_data))

        return _dev_list

    def get_dev_status(self, dev_id: str) -> model.SwitchBotDeviceStatus:
        resp_body = self._get(endpoint=f'GET https://api.switch-bot.com/v1.1/devices/{dev_id}/status')
        assert isinstance(resp_body, dict)
        return model.SwitchBotDeviceStatus(**resp_body)

