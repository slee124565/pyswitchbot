import logging
import pytest
from switchbot.entrypoints.flask_app import ApiAccessTokenError
from . import api_client

logger = logging.getLogger(__name__)

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

_test_devices = [
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


@pytest.mark.usefixtures("restart_api")
def test_happy_user_iot_service_journey():
    secret = 'secret'
    token = 'token'
    # 用戶註冊iot服務
    r = api_client.post_to_register(secret=secret, token=token, expect_success=True)
    uid = r.json().get('uid')
    assert uid

    # 模擬系統更新用戶設備清單
    r = api_client.post_to_request_sync(user_id=uid, devices=_test_devices)
    data = r.json()
    assert data.get('uid') == uid
    assert data.get('devices') == len(_test_devices)

    # 模擬系統更新用戶設備狀態資料
    api_client.post_to_report_state(uid=uid, state={
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
    api_client.post_to_report_state(uid=uid, state={
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

    # todo: 模擬第三方服務 AoG 訂閱用戶iot intent服務
    subscriber_id = 'aog'
    api_client.post_to_subscribe(uid=uid, subscriber_id=subscriber_id)

    # 模擬 AoG 查詢用戶設備列表 sync intent
    r = api_client.post_to_query_user_dev_list(uid=uid, subscriber_id=subscriber_id)
    resp = r.json()
    logger.info(f'sync fulfillment: {resp}')
    assert isinstance(resp.get("payload").get("devices"), list)
    assert len(resp.get("payload").get("devices")) == 2

    # 模擬 AoG 查詢用戶設備列表中的第一個設備狀態 query intent
    dev = resp.get("payload").get("devices")[0]
    assert isinstance(dev, dict)
    dev_id = dev.get("id")
    r = api_client.post_to_query_user_dev_state(uid=uid, subscriber_id=subscriber_id, dev_id=dev_id)
    resp = r.json()
    logger.debug(f'query fulfillment: {resp}')
    keys = resp.get("payload").get("devices").keys()
    assert len(keys) == 1
    dto = resp.get("payload").get("devices")
    logger.debug(f'state dto {dto}')
    assert isinstance(dto, dict)
    dev_onoff = next((dto[_id].get("on") for _id in dto))
    logger.debug(f'target dev power {dev_onoff}')

    # # 模擬 AoG 控制用戶設備列表中的第一個設備狀態ON/OFF, execute intent
    # ctr_onoff = not dev_onoff
    # r = api_client.post_to_ctrl_user_dev_onoff(uid=uid, subscriber_id=subscriber_id, dev_id=dev_id, dev_onoff=ctr_onoff)
    # resp = r.json()
    # assert isinstance(resp, dict)
    # logger.debug(f'exec fulfillment: {resp}')
    # items = resp.get("payload").get("commands")
    # assert isinstance(items, list)
    # for item in items:
    #     assert isinstance(item, dict)
    #     assert item.get("ids")
    #     assert item.get("status")
    #     assert item.get("states")
    #
    # # 模擬系統接收到SwitchBot Webhook ReportChange 設備狀態更新資料
    # state = {
    #     "eventType": "changeReport",
    #     "eventVersion": "1",
    #     "context": {
    #         "deviceType": "WoPlugUS",
    #         "deviceMac": f"{dev_id}",
    #         "powerState": "ON" if ctr_onoff else "OFF",
    #         "timeOfSample": 123456789
    #     }
    # }
    # api_client.post_to_report_state(uid=user_id, state=state)
    #
    # # 模擬系統因為 ReportChange 而啟動查詢用戶設備列表中的第一個設備狀態
    # api_client.post_to_report_state(uid=user_id, state={
    #     "deviceId": f"{dev_id}",
    #     "deviceType": "Plug Mini (US)",
    #     "hubDeviceId": f"{dev_id}",
    #     "power": "on" if ctr_onoff else "off",
    #     "voltage": 114.7,
    #     "weight": 0,
    #     "electricityOfDay": 122,
    #     "electricCurrent": 0,
    #     "version": "V1.4-1.4"
    # })
    #
    # # 模擬 Aog 查詢操控設備的最新狀態
    # r = api_client.post_to_query_user_dev_state(secret=secret, dev_id=dev_id)
    # keys = resp.get("payload").get("devices").keys()
    # assert len(keys) == 1
    # assert keys[0] == dev_id
    # resp = r.json()
    # assert len(resp.get("payload").get("devices")[dev_id].keys()) > 0
    # dev_onoff = resp.get("payload").get("devices")[dev_id].get("on")
    # assert dev_onoff == ctr_onoff
    #
    # # 確認 pubsub adapter 有收到 ReportSubscriberChange 通知 (todo)

    # 用戶取消訂閱 (todo: check unsubscribe event log)
    api_client.post_to_unsubscribe(uid=uid, subscriber_id=subscriber_id)

    # # 查詢用戶設備列表時，因為第三方服務已經取消訂閱，應該產生錯誤
    # with pytest.raises(Exception) as err:
    #     api_client.post_to_query_user_dev_list(secret=secret)
    #     assert isinstance(err, ApiAccessTokenError)

    # 用戶註銷帳號
    api_client.post_to_unregister(uid=uid)

    # # 查詢用戶設備列表時，因為用戶不存在，應該產生錯誤
    # with pytest.raises(Exception) as err:
    #     api_client.post_to_query_user_dev_list(secret=secret)
    #     assert isinstance(err, ApiAccessTokenError)
