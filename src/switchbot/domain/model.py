import logging
import uuid
from typing import List
from dataclasses import dataclass
# from marshmallow import Schema, fields, post_load, post_dump

from switchbot.domain import events

logger = logging.getLogger(__name__)


class SwitchBotChangeReport:
    """
    "eventType": "changeReport",
    "eventVersion": "1",
    "context": {
    """

    def __init__(
            self,
            event_type,
            event_version,
            context,
    ):
        self.event_type = event_type
        self.event_version = event_version
        self.context = context


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

    def __eq__(self, other):
        if not isinstance(other, SwitchBotDevice):
            # 如果不是，則直接返回 False
            return False
        return (self.device_id == other.device_id and
                self.device_name == other.device_name and
                self.device_type == other.device_type and
                self.enable_cloud_service == other.enable_cloud_service and
                self.hub_device_id == other.hub_device_id and
                self.curtain_devices_ids == other.curtain_devices_ids and
                self.calibrate == other.calibrate and
                self.group == other.group and
                self.master == other.master and
                self.open_direction == other.open_direction and
                self.lock_devices_ids == other.lock_devices_ids and
                self.group_name == other.group_name and
                self.lock_device_id == other.lock_device_id and
                self.key_list == other.key_list and
                self.version == other.version and
                self.blind_tilt_devices_ids == other.blind_tilt_devices_ids and
                self.direction == other.direction and
                self.slide_position == other.slide_position)

    def __hash__(self):
        return hash((self.device_id, self.device_name, self.device_type))

    def __repr__(self):
        return f'Device({self.device_id}, {self.device_name}, {self.device_type})'

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


class SwitchBotUserRepo:
    def __init__(
            self,
            uid: str,
            secret: str,
            token: str,
            devices: List[SwitchBotDevice],
            states: List[SwitchBotStatus],
            scenes: List[SwitchBotScene],
            webhooks: List[SwitchBotWebhook]
    ):
        self.uid = uid
        self.secret = secret
        self.token = token
        self.devices = devices
        self.states = states
        self.scenes = scenes
        self.webhooks = webhooks
        self.events = []

    def __eq__(self, other):
        if not isinstance(other, SwitchBotUserRepo):
            return False
        return all([
            self.uid == other.uid,
            self.secret == other.secret,
            self.token == other.token,
            len(self.devices) == len(other.devices)
        ])

    def __hash__(self):
        return hash((self.uid, self.secret, self.token))

    def sync(self) -> List[SwitchBotDevice]:
        return self.devices

    def query(self, dev_id_list: List[str]) -> List[SwitchBotStatus]:
        targets = [next((dev for dev in self.devices if dev.device_id == dev_id)) for dev_id in dev_id_list]
        return [dev.state for dev in targets]

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
                if sync_dev != user_dev:  # device modified
                    self._update_device(device=sync_dev)
                else:  # device already exist
                    pass
            else:  # device new added
                sync_dev = next((dev for dev in devices if dev.device_id == sync_dev_id), None)
                self.devices.append(sync_dev)
        for user_dev_id in user_dev_id_list:
            if user_dev_id not in sync_dev_id_list:
                self._remove_device(dev_id=user_dev_id)
        self.events.append(
            events.UserDevFetched(user_id=self.uid)
        )

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


class SwitchBotUserFactory:
    @classmethod
    def create_user(cls,
                    secret: str, token: str, uid: str = None) -> SwitchBotUserRepo:
        uid = str(uuid.uuid4()) if uid is None else uid
        return SwitchBotUserRepo(
            uid=uid, secret=secret, token=token,
            devices=[], states=[], scenes=[], webhooks=[]
        )
