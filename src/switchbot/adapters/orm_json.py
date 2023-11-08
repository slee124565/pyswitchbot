import os
import logging
import json
from typing import List
from marshmallow import Schema, fields, post_load, post_dump
from switchbot.domain import model

logger = logging.getLogger(__name__)


class OrmJsonSchemaError(Exception):
    pass


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
        return model.SwitchBotDevice(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SwitchBotChangeReportSchema(Schema):
    event_type = fields.String(data_key="eventType", required=True)
    event_version = fields.String(data_key="eventVersion", required=True)
    context = fields.Dict(data_key="context", required=True)

    @post_load
    def make_change_report(self, data, **kwargs):
        return model.SwitchBotChangeReport(**data)

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
        return model.SwitchBotStatus(**data)

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
        return model.SwitchBotScene(**data)


class SwitchBotUserRepoSchema(Schema):
    uid = fields.String(data_key='userId')
    secret = fields.String(data_key='userSecret')
    token = fields.String(data_key='userToken')
    devices = fields.List(fields.Nested(SwitchBotDeviceSchema()))
    states = fields.List(fields.Nested(SwitchBotStatusSchema()))
    changes = fields.List(fields.Nested(SwitchBotChangeReportSchema()))
    scenes = fields.List(fields.Str(), load_default=None)
    webhooks = fields.List(fields.Str(), load_default=None)

    @post_load
    def make_user_repo(self, data, **kwargs):
        return model.SwitchBotUserRepo(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class MarshmallowSchemaConverter:
    _users = []  # type: List['model.SwitchBotUserRepo']

    def __init__(self, file: str):
        self._file = file
        if os.path.exists(file):
            with open(self._file, 'r') as fh:
                content = json.loads(fh.read())
                if not isinstance(content, list):
                    raise OrmJsonSchemaError
            _schema = SwitchBotUserRepoSchema()
            self._users = [_schema.load(data) for data in content]
        else:
            self._users = []

    def commit(self):
        self._save()

    def _save(self):
        with open(self._file, 'w') as fh:
            _schema = SwitchBotUserRepoSchema()
            content = [_schema.dump(u) for u in self._users]
            fh.write(json.dumps(content, indent=2, ensure_ascii=False))

    def register_user(self, user: model.SwitchBotUserRepo):
        n, u = next(((n, u) for n, u in enumerate(self._users) if u.secret == user.secret), (None, None))
        if u is None:
            self._users.append(user)
        else:
            logger.warning(f'register w/ secret already exist on user {u.uid}, skip')
            # del self._users[n]
            # self._users.append(user)
        self._save()

    def unregister_user(self, uid: str):
        n, u = next(((n, u) for n, u in enumerate(self._users) if u.uid == uid), (None, None))
        if u is None:
            m = f'user uid {uid} not exist'
            logger.warning(m)
            raise ValueError(m)
        else:
            del self._users[n]
            logger.info(f'unregister user {u}, replaced with new user {u}')
        self._save()

    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.secret == secret), None)

    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.uid == uid), None)

    def get_by_dev_id(self, dev_id) -> model.SwitchBotUserRepo:
        return next((u for u in self._users for d in u.devices if d.device_id == dev_id), None)

    def get_dev_state(self, uid: str, dev_id: str) -> model.SwitchBotStatus:
        u = self.get_by_uid(uid=uid)
        return next((s for s in u.states if s.device_id == dev_id), None)

    def get_dev_last_change_report(self, uid: str, dev_id: str) -> model.SwitchBotChangeReport:
        u = self.get_by_uid(uid=uid)
        return next((c for c in u.changes[::-1] if c.context.get("deviceMac") == dev_id), None)

    def count(self) -> int:
        return len(self._users)


def session_factory(file: str):
    return MarshmallowSchemaConverter(file)
