import json
from typing import List, Dict
from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_load


# from . import commands, events


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

    def query(self):
        raise NotImplementedError

    def execute(self, cmd):
        raise NotImplementedError

    def asdict(self) -> dict:
        data = SwitchBotDeviceSchema().dump(self)
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def fromdict(cls, data: dict) -> 'SwitchBotDevice':
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


class SwitchBotStatus:
    kwargs: dict

    def __repr__(self):
        return f'DevStatus({json.dumps(self.kwargs)})'

    def __init__(
            self,
            device_id,
            device_type,
            hub_device_id,
            power=None,
            battery=None,
            version=None,
            device_mode=None,
            calibrate=None,
            group=None,
            moving=None,
            slide_position=None,
            temperature=None,
            humidity=None,
            lock_state=None,
            door_state=None,
            working_status=None,
            online_status=None,
            move_detected=None,
            brightness=None,
            color=None,
            color_temperature=None,
            voltage=None,
            weight=None,
            electricity_of_day=None,
            electric_current=None):
        self.device_id = device_id
        self.device_type = device_type
        self.hub_device_id = hub_device_id
        self.power = power
        self.battery = battery
        self.version = version
        self.device_mode = device_mode
        self.calibrate = calibrate
        self.group = group
        self.moving = moving
        self.slide_position = slide_position
        self.temperature = temperature
        self.humidity = humidity
        self.lock_state = lock_state
        self.door_state = door_state
        self.working_status = working_status
        self.online_status = online_status
        self.move_detected = move_detected
        self.brightness = brightness
        self.color = color
        self.color_temperature = color_temperature
        self.voltage = voltage
        self.weight = weight
        self.electricity_of_day = electricity_of_day
        self.electric_current = electric_current

    @classmethod
    def fromdict(cls, data: dict) -> 'SwitchBotStatus':
        return SwitchBotStatusSchema().load(data)

    def asdict(self) -> dict:
        data = SwitchBotStatusSchema().dump(self)
        return {k: v for k, v in data.items() if v is not None}


class SwitchBotStatusSchema(Schema):
    device_id = fields.String(data_key='deviceId', required=True)
    device_type = fields.String(data_key='deviceType', required=True)
    hub_device_id = fields.String(data_key='hubDeviceId', required=True)
    power = fields.String(missing=None)
    battery = fields.Integer(missing=None)
    version = fields.String(missing=None)
    device_mode = fields.String(data_key='deviceMode', missing=None)
    calibrate = fields.Boolean(missing=None)
    group = fields.Boolean(missing=None)
    moving = fields.Boolean(missing=None)
    slide_position = fields.String(data_key='slidePosition', missing=None)
    temperature = fields.Float(missing=None)
    humidity = fields.Integer(missing=None)
    lock_state = fields.String(data_key='lockState', missing=None)
    door_state = fields.String(data_key='doorState', missing=None)
    working_status = fields.String(data_key='workingStatus', missing=None)
    online_status = fields.String(data_key='onlineStatus', missing=None)
    move_detected = fields.Boolean(data_key='moveDetected', missing=None)
    brightness = fields.String(missing=None)
    color = fields.String(missing=None)
    color_temperature = fields.Integer(data_key='colorTemperature', missing=None)
    voltage = fields.Float(missing=None)
    weight = fields.Float(missing=None)
    electricity_of_day = fields.Integer(data_key='electricityOfDay', missing=None)
    electric_current = fields.Float(data_key='electricCurrent', missing=None)

    @post_load
    def make_iot_state(self, data, **kwargs):
        return SwitchBotStatus(**data)


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
    data = {
        "deviceId": "6055F92FCFD2",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F92FCFD2",
        "power": "off",
        "voltage": 114.1,
        "weight": 0,
        "electricityOfDay": 3,
        "electricCurrent": 0,
        "version": "V1.4-1.4"
    }
    obj = SwitchBotDevice.fromdict(data)
    assert isinstance(obj, SwitchBotDevice)
    assert obj.device_id == data.get('deviceId')
    assert obj.device_name == data.get('deviceName')
    assert obj.device_type == data.get('deviceType')
    assert obj.enable_cloud_service == data.get('enableCloudService')
    assert obj.hub_device_id == data.get('hubDeviceId')
    assert obj.asdict() == data
    pass
