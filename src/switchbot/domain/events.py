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
class DevStateUpdated(Event):
    """表示新訂閱用戶的設備狀態是第一次更新，不需要 pub ReportSubscriberDevState"""
    dev_id: str
    state: dict


@dataclass
class DevStateChanged(Event):
    """表示新訂閱用戶的設備狀態更新之後又有狀態變化，需要 pub ReportSubscriberDevState"""
    dev_id: str
    state: dict


@dataclass
class UserDevStatesAllFetched(Event):
    """表示訂閱用戶設備已經全部更新狀態，需要 pub RequestSubscriberToSync"""
    uid: str


@dataclass
class RequestReload(Event):
    """表示要求已註冊用戶的資料重新下載更新"""
    uid: str


@dataclass
class UserDevMerged(Event):
    """表示已註冊用戶的webhook已經設定完成，用戶資料與來源端同步機制建立"""
    uid: str
