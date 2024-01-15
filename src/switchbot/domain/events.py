# pylint: disable=too-few-public-methods
from typing import List
from dataclasses import dataclass


class Event:
    pass


@dataclass
class UserRegistered(Event):
    """代表系統已經新增了一個用戶資訊"""
    uid: str


@dataclass
class UserDevListFetched(Event):
    """代表系統已經訂閱用戶的設備清單更新"""
    uid: str


@dataclass
class UserDevStatesAllFetched(Event):
    """表示訂閱用戶設備已經全部更新狀態，需要 pub RequestSubscriberToSync"""
    uid: str


@dataclass
class UserDevMerged(Event):
    """表示已註冊用戶的webhook已經設定完成，用戶資料與來源端同步機制建立"""
    uid: str


# @dataclass
# class DevStateUpdated(Event):
#     """表示新訂閱用戶的設備狀態是第一次更新，不需要 pub ReportSubscriberDevState"""
#     dev_id: str
#     state: dict


@dataclass
class UserDevStateChanged(Event):
    """表示收到用戶某個設備狀態變更事件"""
    dev_id: str


@dataclass
class RequestReloadUser(Event):
    """表示要求已註冊用戶的資料重新下載更新"""
    uid: str


@dataclass
class UserUnregistered(Event):
    """表示用戶註銷本服務"""
    uid: str
