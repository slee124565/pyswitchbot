import logging
from typing import List
from dataclasses import dataclass
from marshmallow import Schema, fields, post_load, post_dump

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


class SwitchBotUserRepoSchema(Schema):
    """todo: how setup nested Schema"""
    user_id = fields.String(data_key='userId')
    devices = fields.List(fields.Nested(SwitchBotDeviceSchema()))
    states = fields.List(fields.Nested(SwitchBotStatusSchema()))
    scenes = fields.List(fields.Str(), load_default=None)
    webhooks = fields.List(fields.Str(), load_default=None)

    @post_load
    def make_user_repo(self, data, **kwargs):
        return SwitchBotUserRepo(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SwitchBotStatus:

    def __repr__(self):
        return f'{self.__class__.__name__}({self.device_id},{self.device_type})'

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
            electric_current=None
    ):
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

    def dump(self) -> dict:
        return SwitchBotStatusSchema().dump(self)

    @classmethod
    def load(cls, data: dict):
        return SwitchBotStatusSchema().load(data)


class SwitchBotDevice:
    state: SwitchBotStatus

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
        self.events = []

    def __repr__(self):
        return f'Device({self.device_id}, {self.device_name}, {self.device_type})'

    def dump(self) -> dict:
        return SwitchBotDeviceSchema().dump(self)

    @classmethod
    def load(cls, data: dict):
        return SwitchBotDeviceSchema().load(data)

    def execute(self, cmd_type, cmd_name, cmd_param):
        raise NotImplementedError


class SwitchBotScene:
    scene_id: str
    scene_name: str

    def __init__(
            self,
            scene_id,
            scene_name
    ):
        self.scene_id = scene_id
        self.scene_name = scene_name

    def dump(self) -> dict:
        return SwitchBotSceneSchema().dump(self)

    @classmethod
    def load(cls, data: dict):
        return SwitchBotSceneSchema().load(data)


@dataclass
class SwitchBotWebhook:
    url: str
    createTime: int | None
    lastUpdateTime: int | None
    deviceList: str | None
    enable: bool | None


class SwitchBotUserRepo:
    def __init__(
            self,
            user_id: str,
            devices: List[SwitchBotDevice],
            states: List[SwitchBotStatus],
            scenes: List[SwitchBotScene],
            webhooks: List[SwitchBotWebhook]
    ):
        self.user_id = user_id
        self.devices = devices
        self.states = states
        self.scenes = scenes
        self.webhooks = webhooks

    def sync(self) -> List[SwitchBotDevice]:
        return self.devices

    def query(self, dev_id_list: List[str]) -> List[SwitchBotStatus]:
        targets = [next((dev for dev in self.devices if dev.device_id == dev_id)) for dev_id in dev_id_list]
        return [dev.state for dev in targets]

    # def query(self, dev_id: str) ->:
    def query_dev_state(self, dev_id: str) -> SwitchBotStatus:
        dev = next((dev for dev in self.devices if dev.device_id == dev_id))
        return dev.state

    def report_state(self, state: SwitchBotStatus):
        dev = next((dev for dev in self.devices if dev.device_id == state.device_id))
        dev.state = state

    def request_sync(self, devices: List[SwitchBotDevice]):
        sync_dev_id_list = [dev.device_id for dev in devices]
        user_dev_id_list = [dev.device_id for dev in self.devices]
        for sync_dev_id in sync_dev_id_list:
            if sync_dev_id in user_dev_id_list:
                sync_dev = next((dev for dev in devices if dev.device_id == sync_dev_id), None)
                user_dev = next((dev for dev in self.devices if dev.device_id == sync_dev_id), None)
                _schema = SwitchBotDeviceSchema()
                if _schema.dump(sync_dev) != _schema.dump(user_dev):  # device modified
                    self._update_device(device=sync_dev)
                else:  # device already exist
                    pass
            else:  # device new added
                sync_dev = next((dev for dev in devices if dev.device_id == sync_dev_id), None)
                self.devices.append(sync_dev)
        for user_dev_id in user_dev_id_list:
            if user_dev_id not in sync_dev_id_list:
                self._remove_device(dev_id=user_dev_id)

    def disconnect(self):
        for dev_id in [dev.device_id for dev in self.devices]:
            self._remove_device(dev_id=dev_id)

    def _update_device(self, device: SwitchBotDevice):
        index = next((n for n, origin in enumerate(self.devices) if origin.device_id == device.device_id),
                     None)
        if index:
            self.devices[index] = device
        else:
            raise ValueError(f'device({device}) not exist')

    def _remove_device(self, dev_id: str):
        index = next((n for n, dev in enumerate(self.devices) if dev.device_id == dev_id), None)
        if index is not None:
            del self.devices[index]
        else:
            raise ValueError(f'device({dev_id}) not exist')

    @classmethod
    def load(cls, data: dict):
        return SwitchBotUserRepoSchema().load(data)

    def dump(self) -> dict:
        return SwitchBotUserRepoSchema().dump(self)
