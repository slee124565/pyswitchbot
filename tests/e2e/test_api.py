"""todo:"""
import pytest
from switchbot.entrypoints.flask_app import ApiAccessTokenError
from . import api_client

webhook_data = [{
    "eventType": "changeReport",
    "eventVersion": "1",
    "context": {
        "deviceType": "WoPlugUS",
        "deviceMac": "6055F930FF22",
        "powerState": "ON",
        "timeOfSample": 1698720698088
    }
}, {
    "eventType": "changeReport",
    "eventVersion": "1",
    "context": {
        "deviceType": "WoPlugUS",
        "deviceMac": "6055F92FCFD2",
        "powerState": "OFF",
        "timeOfSample": 1698682911154
    }
}]

test_devices = [
    {
        "deviceId": "6055F92FCFD2",
        "deviceName": "小風扇開關",
        "deviceType": "Plug Mini (US)",
        "enableCloudService": True,
        "hubDeviceId": ""
    },
    {
        "deviceId": "6055F930FF22",
        "deviceName": "風扇開關",
        "deviceType": "Plug Mini (US)",
        "enableCloudService": True,
        "hubDeviceId": ""
    }
]


def test_happy_user_iot_service_journey():
    secret = 'secret'
    token = 'token'

    # 用戶註冊iot服務
    r = api_client.post_to_register(secret=secret, token=token, expect_success=True)
    user_id = r.json.get('userId')
    assert user_id

    # 模擬系統更新用戶設備清單
    api_client.post_to_request_sync(secret=secret, devices=test_devices)

    # 模擬系統更新用戶設備狀態資料
    api_client.post_to_report_state(secret=secret, state={
        "deviceId": "6055F92FCFD2",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F92FCFD2",
        "power": "off",
        "voltage": 115.2,
        "weight": 0,
        "electricityOfDay": 102,
        "electricCurrent": 0,
        "version": "V1.4-1.4"
    })
    api_client.post_to_report_state(secret=secret, state={
        "deviceId": "6055F930FF22",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F930FF22",
        "power": "off",
        "voltage": 114.7,
        "weight": 0,
        "electricityOfDay": 122,
        "electricCurrent": 0,
        "version": "V1.4-1.4"
    })

    # 模擬第三方服務 AoG 訂閱用戶iot intent服務
    api_client.post_to_subscribe(secret=secret, token=token, expect_success=True)

    # 模擬 AoG 查詢用戶設備列表 sync intent
    r = api_client.post_to_query_user_dev_list(secret=secret)
    assert isinstance(r.json.get("payload").get("devices"), list)
    assert len(r.json.get("payload").get("devices")) == 2

    # 模擬 AoG 查詢用戶設備列表中的第一個設備狀態 query intent
    dev = r.json.get("payload").get("devices")[0]
    assert isinstance(dev, dict)
    dev_id = dev.get("id")
    r = api_client.post_to_query_user_dev_state(secret=secret, dev_id=dev_id)
    keys = r.json.get("payload").get("devices").keys()
    assert len(keys) == 1
    assert keys[0] == dev_id
    assert len(r.json.get("payload").get("devices")[dev_id].keys()) > 0
    dev_onoff = r.json.get("payload").get("devices")[dev_id].get("on")

    # 模擬 AoG 控制用戶設備列表中的第一個設備狀態ON/OFF, execute intent
    ctr_onoff = not dev_onoff
    api_client.post_to_ctrl_user_dev_onoff(secret=secret, dev_id=dev_id, dev_onoff=ctr_onoff)

    # 模擬系統接收到SwitchBot Webhook ReportChange 設備狀態更新資料
    state = {
        "eventType": "changeReport",
        "eventVersion": "1",
        "context": {
            "deviceType": "WoPlugUS",
            "deviceMac": f"{dev_id}",
            "powerState": "ON" if ctr_onoff else "OFF",
            "timeOfSample": 123456789
        }
    }
    api_client.post_to_report_state(secret=secret, state=state)

    # 模擬系統因為 ReportChange 而啟動查詢用戶設備列表中的第一個設備狀態
    api_client.post_to_report_state(secret=secret, state={
        "deviceId": f"{dev_id}",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": f"{dev_id}",
        "power": "on" if ctr_onoff else "off",
        "voltage": 114.7,
        "weight": 0,
        "electricityOfDay": 122,
        "electricCurrent": 0,
        "version": "V1.4-1.4"
    })

    # 模擬 Aog 查詢操控設備的最新狀態
    r = api_client.post_to_query_user_dev_state(secret=secret, dev_id=dev_id)
    keys = r.json.get("payload").get("devices").keys()
    assert len(keys) == 1
    assert keys[0] == dev_id
    assert len(r.json.get("payload").get("devices")[dev_id].keys()) > 0
    dev_onoff = r.json.get("payload").get("devices")[dev_id].get("on")
    assert dev_onoff == ctr_onoff

    # 確認 pubsub adapter 有收到 ReportSubscriberChange 通知 (todo)

    # 用戶取消訂閱 (todo: check unsubscribe event log)
    api_client.post_to_unsubscribe(secret=secret)

    # 查詢用戶設備列表時，因為第三方服務已經取消訂閱，應該產生錯誤
    with pytest.raises(Exception) as err:
        api_client.post_to_query_user_dev_list(secret=secret)
        assert isinstance(err, ApiAccessTokenError)

    # 用戶註銷帳號
    api_client.post_to_unregister(secret=secret, token=token, expect_success=True)

    # 查詢用戶設備列表時，因為用戶不存在，應該產生錯誤
    with pytest.raises(Exception) as err:
        api_client.post_to_query_user_dev_list(secret=secret)
        assert isinstance(err, ApiAccessTokenError)

