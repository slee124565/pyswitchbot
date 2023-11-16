from typing import Union, List
from dataclasses import dataclass


class Command:
    pass


@dataclass
class Subscribe(Command):
    """第三方系統訂閱用戶設備IoT服務"""
    uid: str
    subscriber_id: str


@dataclass
class Unsubscribe(Command):
    """第三方系統取消用戶設備IoT訂閱服務"""
    uid: str
    subscriber_id: str


@dataclass
class Unregister(Command):
    """要用系統移除用戶資料"""
    uid: str


@dataclass
class Register(Command):
    """要求系統新增訂閱用戶"""
    # user_id: str
    secret: str
    token: str


@dataclass
class RequestSync(Command):
    """要求系統更新訂閱用戶設備清單"""
    uid: str
    devices: List[dict]


@dataclass
class ReportState(Command):
    """要求系統更新訂閱用戶的設備狀態"""
    uid: str
    state: dict


@dataclass
class ReportChange(Command):
    """webhook report change"""
    # {
    #     "eventType": "changeReport",
    #     "eventVersion": "1",
    #     "context": {
    #         "deviceType": "WoPlugUS",
    #         "deviceMac": "6055F930FF22",
    #         "powerState": "ON",
    #         "timeOfSample": 1698720698088
    #     }
    # }
    change: dict
    # event_type: str
    # event_version: str
    # context: dict


@dataclass
class Disconnect(Command):
    """訂閱用戶取消訂閱"""
    user_id: str
    subscriber_id: str


@dataclass
class ReportSubscriberToSync(Command):
    """通知外部整合系統用戶設備清單更新"""
    user_id: str


@dataclass
class ReportSubscriberDevState(Command):
    """通知外部整合系統用戶設備狀態更新"""
    user_id: str
    dev_id: str
    state: dict


@dataclass
class ExecAoGCmds(Command):
    """控制用戶設備指令"""
    uid: str
    subscriber_id: str
    aog_cmds_dto: list

