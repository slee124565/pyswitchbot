import logging
import uuid
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from marshmallow import Schema, fields, post_load, post_dump
from switchbot.domain import events

logger = logging.getLogger(__name__)


class SwitchBotChangeReport:
    """
    "eventType": "changeReport",
    "eventVersion": "1",
    "context":  {
        "deviceType": "WoPlugUS",
        "deviceMac": "6055F930FF22",
        "powerState": "ON",
        "timeOfSample": 1698720698088
    }
    """

    def __init__(
            self,
            event_type: str,
            event_version: str,
            context: dict,
    ):
        self.event_type = event_type
        self.event_version = event_version
        self.context = context

    def __eq__(self, other):
        if not isinstance(other, SwitchBotChangeReport):
            return False
        return all([
            self.event_type == other.event_type,
            self.event_version == other.event_version,
            self.context == other.context
        ])

    def __hash__(self):
        return hash(self.dump())

    @classmethod
    def load(cls, data: dict):
        _schema = SwitchBotChangeReportSchema()
        return _schema.load(data)

    def dump(self):
        _schema = SwitchBotChangeReportSchema()
        return _schema.dump(self)


class SwitchBotStatus:

    def __repr__(self):
        return f'{self.__class__.__name__}({self.device_id},{self.device_type})'

    device_id: str  # 設備唯一識別碼
    device_type: str  # 設備類型 (例如 "Bot", "Curtain")
    hub_device_id: Optional[str]  # Hub 設備唯一識別碼，可能為 None
    power: Optional[str]  # 電源狀態 ("ON"/"OFF")
    battery: Optional[int]  # 電池電量，百分比 (0-100)
    version: Optional[str]  # 韌體版本 (例如 "V6.3")
    device_mode: Optional[str]  # 設備模式 (例如 "pressMode", "switchMode", "customizeMode")
    calibrate: Optional[bool]  # 是否已校準 (適用於 Curtain 類型)
    group: Optional[bool]  # 是否屬於群組 (適用於 Curtain 和 Blind Tilt 類型)
    moving: Optional[bool]  # 是否正在移動 (適用於 Curtain 類型)
    slide_position: Optional[int]  # 滑動位置 (0-100，適用於 Curtain 類型)
    temperature: Optional[float]  # 溫度 (適用於 Meter 類型)
    humidity: Optional[int]  # 濕度 (0-100，適用於 Meter 類型)
    lock_state: Optional[str]  # 鎖狀態 ("locked"/"unlocked"，適用於 Lock 類型)
    door_state: Optional[str]  # 門狀態 ("open"/"closed"，適用於 Contact Sensor)
    working_status: Optional[str]  # 工作狀態 (例如 "cleaning", "paused"，適用於 Robot Vacuum Cleaner)
    online_status: Optional[str]  # 在線狀態 ("online"/"offline")
    move_detected: Optional[bool]  # 是否檢測到移動 (適用於 Motion Sensor)
    brightness: Optional[int]  # 光亮度數值 (適用於 Color Bulb 或 Strip Light)
    color: Optional[str]  # 顏色值 (例如 "#FFFFFF"，適用於 Color Bulb)
    color_temperature: Optional[int]  # 色溫 (適用於 Color Bulb)
    voltage: Optional[float]  # 電壓 (適用於電力設備)
    weight: Optional[float]  # 重量 (適用於特定感測設備)
    electricity_of_day: Optional[int]  # 當日用電量 (kWh，適用於電力設備)
    electric_current: Optional[float]  # 電流 (A，適用於電力設備)
    light_level: Optional[int]  # 光線等級 (適用於光感測設備)

    def __init__(self, **kwargs):
        # 初始化屬性
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_api_response(cls, response: Dict) -> "SwitchBotStatus":
        """從 API 回應初始化 SwitchBotStatus"""
        return cls(
            device_id=response.get("deviceId"),
            device_type=response.get("deviceType"),
            hub_device_id=response.get("hubDeviceId"),
            power=response.get("power"),
            battery=response.get("battery"),
            version=response.get("version"),
            device_mode=response.get("deviceMode"),
            calibrate=response.get("calibrate"),
            group=response.get("group"),
            moving=response.get("moving"),
            slide_position=response.get("slidePosition"),
            temperature=response.get("temperature"),
            humidity=response.get("humidity"),
            lock_state=response.get("lockState"),
            door_state=response.get("doorState"),
            working_status=response.get("workingStatus"),
            online_status=response.get("onlineStatus"),
            move_detected=response.get("moveDetected"),
            brightness=response.get("brightness"),
            color=response.get("color"),
            color_temperature=response.get("colorTemperature"),
            voltage=response.get("voltage"),
            weight=response.get("weight"),
            electricity_of_day=response.get("electricityOfDay"),
            electric_current=response.get("electricCurrent"),
            light_level=response.get("lightLevel"),
        )

    def to_dict(self) -> Dict:
        """將狀態轉換為字典格式"""
        return self.__dict__

    def __eq__(self, other):
        if not isinstance(other, SwitchBotStatus):
            return False
        return self.dump() == other.dump()

    def __hash__(self):
        return hash(self.dump())

    @classmethod
    def load(cls, data: dict):
        _schema = SwitchBotStatusSchema()
        return _schema.load(data)

    def dump(self):
        _schema = SwitchBotStatusSchema()
        return _schema.dump(self)


class SwitchBotDevice:
    """
    _target_state 的設計來源自 homekit device current/target state 概念，
    current_state 意思是設備目前的實際狀態
    target_state 意思是設備上一個指令執行之後，期望設備的狀態
    例如：
    系統針對 plug 設備，傳送了一個 turnOn 指令之後，就可以記錄目前該設備的 target_state = {"power": "on"}，
    之後系統可以針對 target/current state 做後續的邏輯處理，比如：
    1. 再一定的時間範圍內，重新傳送指令，直到完成目標狀態為止
    2. 依據目前時間，判斷給用戶查詢的狀態是 current/target power state
    """
    state: SwitchBotStatus

    device_id: str  # 設備唯一識別碼，必填
    device_name: str  # 設備名稱，必填
    device_type: str  # 設備類型（例如 "Bot", "Curtain", "Lock"），必填
    enable_cloud_service: bool  # 是否啟用雲端服務，必填
    hub_device_id: Optional[str]  # Hub 的唯一識別碼，可能為 None
    curtain_devices_ids: Optional[List[str]] = None  # 窗簾設備的 ID 列表，適用於 Curtain 類型
    calibrate: Optional[bool] = None  # 是否已校準，適用於需要校準的設備（例如 Curtain）
    group: Optional[bool] = None  # 是否屬於群組，適用於 Curtain 或 Blind Tilt
    master: Optional[bool] = None  # 是否為主設備，適用於群組中的設備
    open_direction: Optional[str] = None  # 窗簾的開啟方向，可能的值為 "left", "right", 或 "both"
    lock_devices_ids: Optional[List[str]] = None  # 鎖設備的 ID 列表，適用於 Lock 類型
    group_name: Optional[str] = None  # 群組名稱，適用於屬於群組的設備
    lock_device_id: Optional[str] = None  # 鎖設備的 ID，適用於 Lock 類型
    key_list: Optional[Dict[str, str]] = None  # 設備密鑰的字典，例如 {"keyName": "keyValue"}
    version: Optional[int] = None  # 設備版本，通常為整數型號編號
    blind_tilt_devices_ids: Optional[List[str]] = None  # 百葉窗傾斜設備的 ID 列表，適用於 Blind Tilt 類型
    direction: Optional[str] = None  # 設備的方向，例如 "up", "down", 或 "horizontal"
    slide_position: Optional[int] = None  # 滑動位置，適用於 Curtain 類型，範圍為 0-100

    def __init__(self, **kwargs):
        # 初始化時動態設置屬性
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.target_state = {}
        # self.events = []

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

    @classmethod
    def load(cls, data: dict):
        _schema = SwitchBotDeviceSchema()
        return _schema.load(data)

    def dump(self):
        _schema = SwitchBotDeviceSchema()
        return _schema.dump(self)


class SwitchBotScene:
    scene_id: str
    scene_name: str

    def __init__(
            self,
            scene_id: str,
            scene_name: str
    ):
        self.scene_id = scene_id
        self.scene_name = scene_name

    @classmethod
    def load(cls, data: dict):
        _schema = SwitchBotSceneSchema()
        return _schema.load(data)

    def dump(self):
        _schema = SwitchBotSceneSchema()
        return _schema.dump(self)


class SwitchBotCommandSchema(Schema):
    commandType = fields.Str(required=True)
    command = fields.Str(required=True)
    parameter = fields.Raw(required=False, allow_none=True)

    @post_load
    def make_switch_bot_command(self, data, **kwargs):
        return SwitchBotCommand(**data)


class SwitchBotCommand:
    def __init__(self, commandType: str, command: str, parameter: Optional[str | dict] = None):
        self.commandType = commandType
        self.command = command
        self.parameter = parameter

    @classmethod
    def load(cls, data: dict):
        _schema = SwitchBotCommandSchema()
        return _schema.load(data)

    def dump(self):
        _schema = SwitchBotCommandSchema()
        return _schema.dump(self)


@dataclass
class SwitchBotWebhook:
    url: str
    createTime: int | None
    lastUpdateTime: int | None
    deviceList: str | None
    enable: bool | None


class SwitchBotUserRepo:
    """
    todo: 新增 user.account_status, 參考 slack 用戶帳號狀態 Active|Inactive|Deactivated
    todo: send UserAccountDeactivated event for publish
    """

    def __init__(
            self,
            uid: str,
            secret: str,
            token: str,
            devices: List[SwitchBotDevice],
            changes: List[SwitchBotChangeReport],
            states: List[SwitchBotStatus],
            scenes: List[SwitchBotScene],
            webhooks: List[SwitchBotWebhook],
            subscribers: Set
    ):
        self.uid = uid
        self.secret = secret
        self.token = token
        self.devices = devices  # type: List[SwitchBotDevice]
        self.changes = changes  # type: List[SwitchBotChangeReport]
        self.states = states  # type: List[SwitchBotStatus]
        self._states = []  # type: List[Dict]
        self.scenes = scenes  # type: List[SwitchBotScene]
        self.webhooks = webhooks  # type: List[SwitchBotWebhook]
        self.subscribers = subscribers  # type: Set
        self.events = []  # type: List[events.Event]
        self.dirty_flag = False  # type: bool

    def set_dev_ctrl_cmd_sent(self, dev_id: str, cmd: SwitchBotCommand):
        logger.debug(f"dev {dev_id}, cmd {cmd}")
        logger.warning(f"todo: set_dev_ctrl_cmd_sent")
        logger.debug(f"user device {self.devices}")
        dev = next((d for d in self.devices if d.device_id == dev_id), None)
        if dev:
            if cmd.commandType == "command" and cmd.command in ["turnOn", "turnOff"]:
                dev.target_state.update({"power": "on"} if cmd.command == "turnOn" else {"power": "off"})
            else:
                raise NotImplementedError
        else:
            raise ValueError

    @classmethod
    def load(cls, data: dict):
        _schema = SwitchBotUserRepoSchema()
        return _schema.load(data)

    def dump(self):
        _schema = SwitchBotUserRepoSchema()
        return _schema.dump(self)

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
        """todo: target_state clean up"""
        dev = next((dev for dev in self.devices if dev.device_id == state.device_id))
        dev.state = state
        # for k in dev.target_state.keys():
        if dev.target_state:
            logger.warning("todo: dev target_state not clean up yet")

    def request_sync(self, devices: List[SwitchBotDevice]):
        sync_dev_id_list = [dev.device_id for dev in devices]
        user_dev_id_list = [dev.device_id for dev in self.devices]
        _is_user_dev_list_changed = False
        for sync_dev_id in sync_dev_id_list:
            if sync_dev_id in user_dev_id_list:
                sync_dev = next((dev for dev in devices if dev.device_id == sync_dev_id), None)
                user_dev = next((dev for dev in self.devices if dev.device_id == sync_dev_id), None)
                if sync_dev != user_dev:  # device modified
                    self._update_device(device=sync_dev)
                    _is_user_dev_list_changed = True
                else:  # device already exist
                    pass
            else:  # device new added
                sync_dev = next((dev for dev in devices if dev.device_id == sync_dev_id), None)
                self.devices.append(sync_dev)
                _is_user_dev_list_changed = True
        for user_dev_id in user_dev_id_list:
            if user_dev_id not in sync_dev_id_list:
                self._remove_device(dev_id=user_dev_id)
                _is_user_dev_list_changed = True
        self.events.append(events.UserDevListFetched(uid=self.uid))
        if _is_user_dev_list_changed:
            self.events.append(events.UserDevListChanged(uid=self.uid))

    def get_dev_by_id(self, dev_id) -> SwitchBotDevice:
        return next((d for d in self.devices if d.device_id == dev_id), None)

    def get_dev_state(self, dev_id: str) -> SwitchBotStatus:
        return next((s for s in self.states if s.device_id == dev_id), None)

    def update_dev_state(self, state: SwitchBotStatus):
        n, s = next(((n, s) for n, s in enumerate(self.states)
                     if s.device_id == state.device_id), (None, None))
        if s is None:
            self.states.append(state)
        else:
            if s != state:
                self.events.append(events.UserDevStateChanged(uid=self.uid, dev_id=state.device_id))
                del self.states[n]
                self.states.append(state)
            else:  # dev status report repeatedly
                logger.debug(f"update dev state with same status, skip")
                pass

    def add_change_report(self, change: SwitchBotChangeReport):
        self.changes.append(change)
        self.events.append(
            events.UserDevReportChanged(dev_id=change.context.get("deviceMac"),
                                        change=change.dump())
        )

    def get_dev_last_change_report(self, dev_id: str) -> SwitchBotChangeReport:
        dev_c_report = [c for c in self.changes if c.context.get('deviceMac') == dev_id]
        sorted_changes = sorted(dev_c_report, key=lambda c: c.context.get('timeOfSample'))
        return sorted_changes[-1] if len(sorted_changes) else None

    def disconnect(self):
        for dev_id in [dev.device_id for dev in self.devices]:
            self._remove_device(dev_id=dev_id)

    def subscribe(self, subscriber_id: str):
        self.subscribers.add(subscriber_id)
        logger.debug(f'user add subscriber {subscriber_id}, {self.subscribers}')

    def unsubscribe(self, subscriber_id: str):
        self.subscribers.remove(subscriber_id)
        logger.debug(f'user remove subscriber {subscriber_id}, {self.subscribers}')

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

    def request_reload(self):
        self.events.append(events.UserRequestReload(uid=self.uid))

    def set_webhook_uri(self, uri):
        self.webhooks = [uri]
        self.events.append(events.UserWebhookUpdated(uid=self.uid))


class SwitchBotUserFactory:
    @classmethod
    def create_user(cls,
                    secret: str, token: str, uid: str = None) -> SwitchBotUserRepo:
        uid = str(uuid.uuid4()) if uid is None else uid
        u = SwitchBotUserRepo(
            uid=uid, secret=secret, token=token,
            devices=[], changes=[], states=[], scenes=[], webhooks=[], subscribers=set()
        )
        u.events.append(events.UserRegistered(
            uid=u.uid
        ))
        return u


class SwitchBotSceneSchema(Schema):
    scene_id = fields.String(data_key="sceneId")
    scene_name = fields.String(data_key="sceneName")

    @post_load
    def make_scene(self, data, **kwargs):
        return SwitchBotScene(**data)


class SwitchBotStatusSchema(Schema):
    device_id = fields.String(data_key='deviceId', required=True)
    device_type = fields.String(data_key='deviceType', required=True)
    hub_device_id = fields.String(data_key='hubDeviceId')
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
    light_level = fields.Integer(data_key='lightLevel', load_default=None)

    @post_load
    def make_status(self, data, **kwargs):
        return SwitchBotStatus(**data)

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
        return SwitchBotChangeReport(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


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


class SwitchBotUserRepoSchema(Schema):
    uid = fields.String(data_key='userId')
    secret = fields.String(data_key='userSecret')
    token = fields.String(data_key='userToken')
    devices = fields.List(fields.Nested(SwitchBotDeviceSchema()))
    states = fields.List(fields.Nested(SwitchBotStatusSchema()))
    changes = fields.List(fields.Nested(SwitchBotChangeReportSchema()))
    scenes = fields.List(fields.Str(), load_default=[])
    webhooks = fields.List(fields.Str(), load_default=[])
    subscribers = fields.List(fields.Str(), load_default=set())

    @post_load
    def make_user_repo(self, data, **kwargs):
        data['subscribers'] = set(data['subscribers'])
        return SwitchBotUserRepo(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }
