import logging
from typing import Optional, List, Set, Dict, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

from switchbot import config
from switchbot.domain.model import SwitchBotDevice, SwitchBotChangeReport, SwitchBotStatus, SwitchBotScene, \
    SwitchBotWebhook
from switchbot.domain.model import SwitchBotUserRepo

logger = logging.getLogger(__name__)

DEFAULT_FIREBASE_RTDB_URL = config.get_firebase_rtdb_url()
# 使用應用默認憑證初始化 Firebase Admin SDK
_firebase_app = firebase_admin.initialize_app(credentials.ApplicationDefault(), {
    'databaseURL': DEFAULT_FIREBASE_RTDB_URL
})


def session_maker():
    return RTDBSessionFactory


class SwitchBotWebhookDTO(BaseModel):
    url: str = Field(..., description="Webhook 的 URL")
    create_time: Optional[int] = Field(None, alias="createTime", description="Webhook 的創建時間戳（毫秒）")
    last_update_time: Optional[int] = Field(None, alias="lastUpdateTime", description="Webhook 最後更新時間戳（毫秒）")
    device_list: Optional[str] = Field(None, alias="deviceList", description="Webhook 關聯的設備列表")
    enable: Optional[bool] = Field(None, description="Webhook 是否啟用")

    @classmethod
    def from_domain(cls, webhook: "SwitchBotWebhook") -> "SwitchBotWebhookDTO":
        """從領域模型 SwitchBotWebhook 轉換為 DTO"""
        return cls(
            url=webhook.url,
            create_time=webhook.createTime,
            last_update_time=webhook.lastUpdateTime,
            device_list=webhook.deviceList,
            enable=webhook.enable,
        )

    def to_domain(self) -> "SwitchBotWebhook":
        """從 DTO 轉換回領域模型 SwitchBotWebhook"""
        return SwitchBotWebhook(
            url=self.url,
            createTime=self.create_time,
            lastUpdateTime=self.last_update_time,
            deviceList=self.device_list,
            enable=self.enable,
        )


class SwitchBotSceneDTO(BaseModel):
    scene_id: str = Field(..., alias="sceneId", description="場景的唯一識別碼")
    scene_name: str = Field(..., alias="sceneName", description="場景名稱")

    @classmethod
    def from_domain(cls, scene: "SwitchBotScene") -> "SwitchBotSceneDTO":
        """從領域模型 SwitchBotScene 轉換為 DTO"""
        return cls(
            scene_id=scene.scene_id,
            scene_name=scene.scene_name,
        )

    def to_domain(self) -> "SwitchBotScene":
        """從 DTO 轉換回領域模型 SwitchBotScene"""
        return SwitchBotScene(
            scene_id=self.scene_id,
            scene_name=self.scene_name,
        )


class SwitchBotStatusDTO(BaseModel):
    device_id: str = Field(..., alias="deviceId", description="設備唯一識別碼")
    device_type: str = Field(..., alias="deviceType", description="設備類型")
    hub_device_id: Optional[str] = Field(None, alias="hubDeviceId", description="所屬 Hub 的唯一識別碼")
    power: Optional[str] = Field(None, description="電源狀態 ('ON'/'OFF')")
    battery: Optional[int] = Field(None, description="電池電量百分比 (0-100)")
    version: Optional[str] = Field(None, description="韌體版本 (如 'V6.3')")
    device_mode: Optional[str] = Field(None, alias="deviceMode", description="設備模式 (如 'pressMode', 'switchMode')")
    calibrate: Optional[bool] = Field(None, description="是否已校準")
    group: Optional[bool] = Field(None, description="是否屬於群組")
    moving: Optional[bool] = Field(None, description="設備是否正在移動")
    slide_position: Optional[int] = Field(None, alias="slidePosition", description="滑動位置 (0-100)")
    temperature: Optional[float] = Field(None, description="設備的溫度數據")
    humidity: Optional[int] = Field(None, description="設備的濕度百分比 (0-100)")
    lock_state: Optional[str] = Field(None, alias="lockState", description="門鎖狀態 ('locked'/'unlocked')")
    door_state: Optional[str] = Field(None, alias="doorState", description="門的開關狀態 ('open'/'closed')")
    working_status: Optional[str] = Field(None, alias="workingStatus", description="工作狀態 (如 'cleaning', 'paused')")
    online_status: Optional[str] = Field(None, alias="onlineStatus", description="在線狀態 ('online'/'offline')")
    move_detected: Optional[bool] = Field(None, alias="moveDetected", description="是否檢測到移動")
    brightness: Optional[int] = Field(None, description="光亮度數值")
    color: Optional[str] = Field(None, description="光的顏色值 (如 '#FFFFFF')")
    color_temperature: Optional[int] = Field(None, alias="colorTemperature", description="光的色溫")
    voltage: Optional[float] = Field(None, description="電壓 (適用於電力設備)")
    weight: Optional[float] = Field(None, description="設備的重量")
    electricity_of_day: Optional[int] = Field(None, alias="electricityOfDay", description="當日用電量 (kWh)")
    electric_current: Optional[float] = Field(None, alias="electricCurrent", description="電流 (A)")
    light_level: Optional[int] = Field(None, alias="lightLevel", description="光線等級")

    @classmethod
    def from_domain(cls, status: "SwitchBotStatus") -> "SwitchBotStatusDTO":
        """從領域模型 SwitchBotStatus 轉換為 DTO"""
        return cls(
            device_id=status.device_id,
            device_type=status.device_type,
            hub_device_id=status.hub_device_id,
            power=status.power,
            battery=status.battery,
            version=status.version,
            device_mode=status.device_mode,
            calibrate=status.calibrate,
            group=status.group,
            moving=status.moving,
            slide_position=status.slide_position,
            temperature=status.temperature,
            humidity=status.humidity,
            lock_state=status.lock_state,
            door_state=status.door_state,
            working_status=status.working_status,
            online_status=status.online_status,
            move_detected=status.move_detected,
            brightness=status.brightness,
            color=status.color,
            color_temperature=status.color_temperature,
            voltage=status.voltage,
            weight=status.weight,
            electricity_of_day=status.electricity_of_day,
            electric_current=status.electric_current,
            light_level=status.light_level,
        )

    def to_domain(self) -> "SwitchBotStatus":
        """從 DTO 轉換回領域模型 SwitchBotStatus"""
        return SwitchBotStatus(
            device_id=self.device_id,
            device_type=self.device_type,
            hub_device_id=self.hub_device_id,
            power=self.power,
            battery=self.battery,
            version=self.version,
            device_mode=self.device_mode,
            calibrate=self.calibrate,
            group=self.group,
            moving=self.moving,
            slide_position=self.slide_position,
            temperature=self.temperature,
            humidity=self.humidity,
            lock_state=self.lock_state,
            door_state=self.door_state,
            working_status=self.working_status,
            online_status=self.online_status,
            move_detected=self.move_detected,
            brightness=self.brightness,
            color=self.color,
            color_temperature=self.color_temperature,
            voltage=self.voltage,
            weight=self.weight,
            electricity_of_day=self.electricity_of_day,
            electric_current=self.electric_current,
            light_level=self.light_level,
        )


class SwitchBotChangeReportDTO(BaseModel):
    event_type: str = Field(..., alias="eventType", description="事件類型，例如 'changeReport'")
    event_version: str = Field(..., alias="eventVersion", description="事件版本號，例如 '1'")
    context: Dict[str, Any] = Field(..., description="事件上下文，包括設備類型、MAC 地址和狀態等")

    @classmethod
    def from_domain(cls, report: "SwitchBotChangeReport") -> "SwitchBotChangeReportDTO":
        """從領域模型 SwitchBotChangeReport 轉換為 DTO"""
        return cls(
            event_type=report.event_type,
            event_version=report.event_version,
            context=report.context,
        )

    def to_domain(self) -> "SwitchBotChangeReport":
        """從 DTO 轉換回領域模型 SwitchBotChangeReport"""
        return SwitchBotChangeReport(
            event_type=self.event_type,
            event_version=self.event_version,
            context=self.context,
        )


class SwitchBotDeviceDTO(BaseModel):
    device_id: str = Field(..., alias="deviceId", description="設備唯一識別碼")
    device_name: str = Field(..., alias="deviceName", description="設備名稱")
    device_type: str = Field(..., alias="deviceType", description="設備類型")
    enable_cloud_service: bool = Field(..., alias="enableCloudService", description="是否啟用雲端服務")
    hub_device_id: Optional[str] = Field(None, alias="hubDeviceId", description="Hub 設備 ID")
    curtain_devices_ids: Optional[List[str]] = Field(None, alias="curtainDevicesIds", description="窗簾設備列表")
    calibrate: Optional[bool] = Field(None, description="是否已校準")
    group: Optional[bool] = Field(None, description="是否為群組設備")
    master: Optional[bool] = Field(None, description="是否為主設備")
    open_direction: Optional[str] = Field(None, alias="openDirection", description="開啟方向")
    lock_devices_ids: Optional[List[str]] = Field(None, alias="lockDevicesIds", description="鎖設備列表")
    group_name: Optional[str] = Field(None, alias="groupName", description="群組名稱")
    lock_device_id: Optional[str] = Field(None, alias="lockDeviceId", description="鎖設備 ID")
    key_list: Optional[Dict[str, str]] = Field(None, alias="keyList", description="設備的密鑰列表")
    version: Optional[int] = Field(None, description="設備版本")
    blind_tilt_devices_ids: Optional[List[str]] = Field(None, alias="blindTiltDevicesIds",
                                                        description="百葉窗傾斜設備 ID 列表")
    direction: Optional[str] = Field(None, description="設備方向")
    slide_position: Optional[int] = Field(None, alias="slidePosition", description="滑動位置")
    target_state: Optional[Dict[str, str]] = Field(None, description="設備目標狀態")

    @classmethod
    def from_domain(cls, device: SwitchBotDevice) -> "SwitchBotDeviceDTO":
        return cls(
            device_id=device.device_id,
            device_name=device.device_name,
            device_type=device.device_type,
            enable_cloud_service=device.enable_cloud_service,
            hub_device_id=device.hub_device_id,
            curtain_devices_ids=device.curtain_devices_ids,
            calibrate=device.calibrate,
            group=device.group,
            master=device.master,
            open_direction=device.open_direction,
            lock_devices_ids=device.lock_devices_ids,
            group_name=device.group_name,
            lock_device_id=device.lock_device_id,
            key_list=device.key_list,
            version=device.version,
            blind_tilt_devices_ids=device.blind_tilt_devices_ids,
            direction=device.direction,
            slide_position=device.slide_position,
            target_state=device.target_state,
        )

    def to_domain(self) -> SwitchBotDevice:
        return SwitchBotDevice(
            device_id=self.device_id,
            device_name=self.device_name,
            device_type=self.device_type,
            enable_cloud_service=self.enable_cloud_service,
            hub_device_id=self.hub_device_id,
            curtain_devices_ids=self.curtain_devices_ids,
            calibrate=self.calibrate,
            group=self.group,
            master=self.master,
            open_direction=self.open_direction,
            lock_devices_ids=self.lock_devices_ids,
            group_name=self.group_name,
            lock_device_id=self.lock_device_id,
            key_list=self.key_list,
            version=self.version,
            blind_tilt_devices_ids=self.blind_tilt_devices_ids,
            direction=self.direction,
            slide_position=self.slide_position,
        )


class SwitchBotUserRepoDTO(BaseModel):
    raise NotImplementedError


class RTDBSessionFactory:
    def __init__(self, root_path: str = 'switchbot'):
        self._root_path = root_path
        self.ref_root = db.reference(f'/{self._root_path}')
        # self.ref_users = self.ref_root.child('users')
        self.ref_users = self.ref_root.child('users')
        self.queried = set()  # type: Set[SwitchBotUserRepo]

    def commit(self):
        for user in self.queried:
            if user.dirty_flag:
                self.add(user)
                logger.debug(f'model user {user} db updated')
        self.queried.clear()

    def rollback(self):
        pass

    def add(self, user):
        user_data = user.dump()
        self.ref_users.child(user.uid).set(user_data)
        logger.info(f'新增 SwitchBotUserRepo: {user.uid} 成功')

    def get(self, uid):
        user_data = self.ref_users.child(uid).get()
        if user_data is None or not isinstance(user_data, dict):
            logger.warning(f'無法找到 UID 為 {uid} 的使用者')
            return None
        user_repo = SwitchBotUserRepo.load(user_data)
        self.queried.add(user_repo)
        return user_repo

    def get_by_dev_id(self, dev_id):
        all_users = self.ref_users.get()
        if all_users is None or not isinstance(all_users, dict):
            return None
        for uid, user_data in all_users.items():
            devices = user_data.get('devices', [])
            if any(dev['deviceId'] == dev_id for dev in devices):
                user_repo = SwitchBotUserRepo.load(user_data)
                self.queried.add(user_repo)
                return user_repo
        logger.warning(f'無法找到包含裝置 ID 為 {dev_id} 的使用者')
        return None

    def get_by_secret(self, secret):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError

    def delete(self, uid):
        raise NotImplementedError
