# pylint: disable=too-few-public-methods
from dataclasses import dataclass


class Event:
    pass


@dataclass
class UserRegistered(Event):
    """代表系統已經新增了一個用戶資訊"""
    uid: str


@dataclass
class UserRequestReload(Event):
    """表示要求已註冊用戶的資料重新下載更新"""
    uid: str


@dataclass
class UserDevListFetched(Event):
    """代表系統已經訂閱用戶的設備清單更新"""
    uid: str


@dataclass
class UserWebhookUpdated(Event):
    """代表用戶webhook uri 已更新，將用戶設備狀態更新事件通知將重新導向本系統"""
    uid: str


# @dataclass
# class UserDevStateFetched(Event):
#     """表示新訂閱用戶的設備狀態是第一次更新，不需要 pub ReportSubscriberDevState"""
#     dev_id: str
#     state: dict


@dataclass
class UserDevReportChanged(Event):
    """表示新訂閱用戶的設備狀態更新之後又有狀態變化，需要 pub ReportSubscriberDevState"""
    dev_id: str
    change: dict


# @dataclass
# class UserDevStatesAllFetched(Event):
#     """表示訂閱用戶設備已經全部更新狀態，需要 pub RequestSubscriberToSync"""
#     uid: str


# @dataclass
# class UserDevMerged(Event):
#     """表示已註冊用戶的webhook已經設定完成，用戶資料與來源端同步機制建立"""
#     uid: str


@dataclass
class UserDevStateChanged(Event):
    """表示用戶設備狀態有變更，若是有訂閱第三方服務的情況下，需要被通知"""
    uid: str
    dev_id: str


@dataclass
class UserDevListChanged(Event):
    """表示用戶設備清單有變更，若是有訂閱第三方服務的情況下，需要被通知"""
    uid: str
    # dev_id: str
    # change: dict
