import logging
from typing import List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


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
        self.events = []

    def __repr__(self):
        return f'Device({self.device_id}, {self.device_name}, {self.device_type})'

    def query(self) -> SwitchBotStatus:
        raise NotImplementedError

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


@dataclass
class SwitchBotWebhook:
    url: str
    createTime: int | None
    lastUpdateTime: int | None
    deviceList: str | None
    enable: bool | None


@dataclass
class SwitchBotUserRepo:
    devices: List[SwitchBotDevice]
    scenes: List[SwitchBotScene]
    webhooks: List[str]


class SwitchBotUser:
    def __init__(self, secret, token, devices: List[SwitchBotDevice]):
        self.secret = secret
        self.token = token
        self.devices = devices

    def sync(self, devices: List[SwitchBotDevice]):
        raise NotImplementedError
