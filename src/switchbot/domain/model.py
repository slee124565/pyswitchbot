import json
from typing import List, Dict
from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_load
# from . import commands, events


@dataclass
class SwitchBotDevice:
    def __init__(
            self,
            device_id: str,
            device_name: str,
            device_type: str,
            enable_cloud_service: bool,
            hub_device_id: str,
            curtain_devices_ids: list = None,
            calibrate: bool = None,
            group: bool = None,
            master: bool = None,
            open_direction: str = None,
            lock_devices_ids: list = None,
            group_name: str = None,
            lock_device_id: str = None,
            key_list: dict = None,
            version: int = None,
            blind_tilt_devices_ids: list = None,
            direction: str = None,
            slide_position: int = None,
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.enable_cloud_service = enable_cloud_service
        self.hub_device_id = hub_device_id
        self.curtain_devices_ids = curtain_devices_ids
        self.calibrate = calibrate
        self.group = group
        self.master = master
        self.open_direction = open_direction
        self.lock_devices_ids = lock_devices_ids
        self.group_name = group_name
        self.lock_device_id = lock_device_id
        self.key_list = key_list
        self.version = version
        self.blind_tilt_devices_ids = blind_tilt_devices_ids
        self.direction = direction
        self.slide_position = slide_position

    def __repr__(self):
        return f'Device({self.device_id}, {self.device_name}, {self.device_type})'

    def sync(self):
        data = self.asdict()
        return {k: v for k, v in data.items() if v is not None}

    def query(self):
        raise NotImplementedError

    def execute(self, cmd):
        raise NotImplementedError

    def asdict(self):
        data = SwitchBotDeviceSchema().dump(self)
        return data

    @classmethod
    def fromdict(cls, data: dict):
        return SwitchBotDeviceSchema().load(data)


class SwitchBotDeviceSchema(Schema):
    device_id = fields.String(data_key="deviceId")
    device_name = fields.String(data_key="deviceName")
    device_type = fields.String(data_key="deviceType")
    enable_cloud_service = fields.Boolean(data_key="enableCloudService")
    hub_device_id = fields.String(data_key="hubDeviceId")
    curtain_devices_ids = fields.List(fields.String(), data_key="curtainDevicesIds", missing=None)
    calibrate = fields.Boolean(missing=None)
    group = fields.Boolean(missing=None)
    master = fields.Boolean(missing=None)
    open_direction = fields.String(data_key="openDirection", missing=None)
    lock_devices_ids = fields.List(fields.String(), data_key="lockDevicesIds", missing=None)
    group_name = fields.String(data_key="groupName", missing=None)
    lock_device_id = fields.String(data_key="lockDeviceId", missing=None)
    key_list = fields.Dict(data_key="keyList", missing=None)
    version = fields.Integer(missing=None)
    blind_tilt_devices_ids = fields.List(fields.String(), data_key="blindTiltDevicesIds", missing=None)
    direction = fields.String(missing=None)
    slide_position = fields.Integer(data_key="slidePosition", missing=None)

    @post_load
    def make_iot_device(self, data, **kwargs):
        return SwitchBotDevice(**data)


# class InfraredIoTDevice:
#     deviceId: str
#     deviceName: str
#     remoteType: str
#     hubDeviceId: str


class SwitchBotDeviceStatus:
    kwargs: dict

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return f'DevStatus({json.dumps(self.kwargs)})'


@dataclass
class SwitchBotScene:
    sceneId: str
    sceneName: str


@dataclass
class SwitchBotWebhook:
    url: str
    createTime: int | None
    lastUpdateTime: int | None
    deviceList: str | None
    enable: bool | None


if __name__ == '__main__':
    _data = {'deviceId': '6055F92FCFD2', 'deviceName': '小風扇開關', 'deviceType': 'Plug Mini (US)',
             'enableCloudService': True, 'hubDeviceId': ''}
    _schema = SwitchBotDeviceSchema()
    obj = _schema.load(_data, partial=True)
    pass
