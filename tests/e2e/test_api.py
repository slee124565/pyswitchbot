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


def test_subscribe_a_account_n_dev_intent_fulfillment():
    secret = 'secret'
    token = 'token'

    # 訂閱用戶設備連結服務
    api_client.post_to_subscribe(secret=secret, token=token, expect_success=True)

    # 模擬系統存在一個服務更新用戶設備列表以及設備裝態
    devices = [
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
    api_client.post_to_request_sync(secret=secret, devices=devices)
    api_client.post_to_report_state(state={
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
    api_client.post_to_report_state(state={
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

    # 查詢用戶設備列表
    r = api_client.post_to_query_user_dev_list(secret=secret)
    assert isinstance(r.json.get("payload").get("devices"), list)
    assert len(r.json.get("payload").get("devices")) == 2

    # 查詢用戶設備列表中的第一個設備狀態
    dev = r.json.get("payload").get("devices")[0]
    assert isinstance(dev, dict)
    dev_id = dev.get("id")
    r = api_client.post_to_query_user_dev_state(secret=secret, dev_id=dev_id)
    keys = r.json.get("payload").get("devices").keys()
    assert len(keys) == 1
    assert keys[0] == dev_id
    assert len(r.json.get("payload").get("devices")[dev_id].keys()) > 0
    dev_onoff = r.json.get("payload").get("devices")[dev_id].get("on")

    # 控制用戶設備列表中的第一個設備狀態ON/OFF
    ctr_onoff = not dev_onoff
    api_client.post_to_ctrl_user_dev_onoff(secret=secret, dev_id=dev_id, dev_onoff=ctr_onoff)

    # 模擬接收ReportState Webhook 設備狀態更新事件
    state = {
        "eventType": "changeReport",
        "eventVersion": "1",
        "context": {
            "deviceType": "WoPlugUS",
            "deviceMac": "DEVICE_MAC_ADDR",
            "powerState": "ON" if ctr_onoff else "OFF",
            "timeOfSample": 123456789
        }
    }
    api_client.post_to_report_state(state=state)

    # 查詢用戶設備列表中的第一個設備狀態
    r = api_client.post_to_query_user_dev_state(secret=secret, dev_id=dev_id)
    keys = r.json.get("payload").get("devices").keys()
    assert len(keys) == 1
    assert keys[0] == dev_id
    assert len(r.json.get("payload").get("devices")[dev_id].keys()) > 0
    dev_onoff = r.json.get("payload").get("devices")[dev_id].get("on")
    assert dev_onoff == ctr_onoff

    # 用戶取消訂閱
    api_client.post_to_unsubscribe(secret=secret)

    # 查詢用戶設備列表時，因為用戶不存在，應該產生錯誤
    with pytest.raises(Exception) as err:
        api_client.post_to_query_user_dev_list(secret=secret)
        assert isinstance(err, ApiAccessTokenError)
