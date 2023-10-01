"""
"""
import logging
# import json
from dataclasses import dataclass, asdict
from typing import List, Dict
from marshmallow import Schema, fields, post_load, post_dump
from switchbot.domain.model import SwitchBotDevice, SwitchBotStatus, SwitchBotScene, SwitchBotUserRepo

logger = logging.getLogger(__name__)


class SwitchBotDeviceSchema(Schema):
    device_id = fields.String(data_key="deviceId")
    device_name = fields.String(data_key="deviceName")
    device_type = fields.String(data_key="deviceType")
    enable_cloud_service = fields.Boolean(data_key="enableCloudService")
    hub_device_id = fields.String(data_key="hubDeviceId")
    curtain_devices_ids = fields.List(fields.String(), data_key="curtainDevicesIds", load_default=None)
    calibrate = fields.Boolean(load_default=None)
    group = fields.Boolean(load_default=None)
    master = fields.Boolean(load_default=None)
    open_direction = fields.String(data_key="openDirection", load_default=None)
    lock_devices_ids = fields.List(fields.String(), data_key="lockDevicesIds", load_default=None)
    group_name = fields.String(data_key="groupName", load_default=None)
    lock_device_id = fields.String(data_key="lockDeviceId", load_default=None)
    key_list = fields.Dict(data_key="keyList", load_default=None)
    version = fields.Integer(load_default=None)
    blind_tilt_devices_ids = fields.List(fields.String(), data_key="blindTiltDevicesIds", load_default=None)
    direction = fields.String(load_default=None)
    slide_position = fields.Integer(data_key="slidePosition", load_default=None)

    @post_load
    def make_device(self, data, **kwargs):
        return SwitchBotDevice(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SwitchBotStatusSchema(Schema):
    device_id = fields.String(data_key='deviceId', required=True)
    device_type = fields.String(data_key='deviceType', required=True)
    hub_device_id = fields.String(data_key='hubDeviceId', required=True)
    power = fields.String(load_default=None)
    battery = fields.Integer(load_default=None)
    version = fields.String(load_default=None)
    device_mode = fields.String(data_key='deviceMode', load_default=None)
    calibrate = fields.Boolean(load_default=None)
    group = fields.Boolean(load_default=None)
    moving = fields.Boolean(load_default=None)
    slide_position = fields.String(data_key='slidePosition', load_default=None)
    temperature = fields.Float(load_default=None)
    humidity = fields.Integer(load_default=None)
    lock_state = fields.String(data_key='lockState', load_default=None)
    door_state = fields.String(data_key='doorState', load_default=None)
    working_status = fields.String(data_key='workingStatus', load_default=None)
    online_status = fields.String(data_key='onlineStatus', load_default=None)
    move_detected = fields.Boolean(data_key='moveDetected', load_default=None)
    brightness = fields.String(load_default=None)
    color = fields.String(load_default=None)
    color_temperature = fields.Integer(data_key='colorTemperature', load_default=None)
    voltage = fields.Float(load_default=None)
    weight = fields.Float(load_default=None)
    electricity_of_day = fields.Integer(data_key='electricityOfDay', load_default=None)
    electric_current = fields.Float(data_key='electricCurrent', load_default=None)

    @post_load
    def make_status(self, data, **kwargs):
        return SwitchBotStatus(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SwitchBotSceneSchema(Schema):
    scene_id = fields.String(data_key="sceneId")
    scene_name = fields.String(data_key="sceneName")

    @post_load
    def make_scene(self, data, **kwargs):
        return SwitchBotScene(**data)

# @dataclass
# class UserRepo:
#     users: Dict[str, SwitchBotUser]


class SwitchBotUserRepoSchema(Schema):
    devices = fields.List(fields.Nested(SwitchBotDeviceSchema()))
    scenes = fields.List(fields.Nested(SwitchBotSceneSchema()))
    webhooks = fields.List(fields.Str())

    @post_load
    def make_user_portfolio(self, data, **kwargs):
        return SwitchBotUserRepo(**data)

# class UserRepoSchema(Schema):
#     users = fields.Dict(keys=fields.Str(), values=fields.Nested(UserSchema()))
#
#     @post_load
#     def make_user_repo(self, data, **kwargs):
#         return UserRepo(**data)


# class FileRepository(AbstractRepository):
#     _file: str
#     _repo: UserRepo
#
#     def _load(self):
#         with open(self._file) as file:
#             data = json.loads(file.read())
#         user_repo_schema = UserRepoSchema()
#         self._repo = user_repo_schema.load(data)
#         print(self._repo)
#         pass
#
#     def _save(self):
#         with open(self._file, 'w', encoding='utf-8') as file:
#             json.dump(asdict(self._repo), file, ensure_ascii=False, indent=2)
#
#     def __init__(self, repo_file: str = '.repository'):
#         super().__init__()
#         self._file = repo_file
#         self._load()
