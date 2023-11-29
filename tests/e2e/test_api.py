import logging
import os

import pytest
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
def test_user_iot_service():
    secret = os.environ.get("SWITCHBOTAPI_SECRET_KEY")
    token = os.environ.get("SWITCHBOTAPI_TOKEN")
    dev_count = int(os.environ.get("SWITCHBOT_DEVICE_COUNT"))

    # 用戶註冊iot服務
    r = api_client.post_to_register(secret=secret, token=token, expect_success=True)
    data = r.json()
    uid = data.get('uid')
    assert uid
    assert data.get('uid') == uid
    assert data.get('devices') == dev_count
    assert data.get('states') == dev_count

    # 第三方服務 aog 訂閱用戶 iot 服務
    subscriber_id = 'aog'
    api_client.post_to_subscribe(uid=uid, subscriber_id=subscriber_id)

    # 模擬 AoG 查詢用戶設備列表 sync intent
    r = api_client.post_to_query_user_dev_list(uid=uid, subscriber_id=subscriber_id)
    resp = r.json()
    logger.info(f'sync fulfillment: {resp}')
    assert isinstance(resp.get("payload").get("devices"), list)
    assert len(resp.get("payload").get("devices")) == dev_count

    # 模擬 AoG 查詢用戶設備列表中的第一個設備狀態 query intent
    dev = resp.get("payload").get("devices")[-1]
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

    # 模擬 AoG 控制用戶設備列表中的第一個設備狀態ON/OFF, execute intent
    ctr_onoff = not dev_onoff
    logger.debug(f"set target dev power {ctr_onoff}")
    r = api_client.post_to_ctrl_user_dev_onoff(
        uid=uid, subscriber_id=subscriber_id, dev_id=dev_id, dev_onoff=ctr_onoff
    )
    resp = r.json()
    assert isinstance(resp, dict)
    logger.debug(f'exec fulfillment: {resp}')
    items = resp.get("payload").get("commands")
    assert isinstance(items, list)
    for item in items:
        assert isinstance(item, dict)
        assert item.get("ids")
        assert item.get("status")
        assert item.get("states")

    # 用戶取消訂閱 (todo: check unsubscribe event log)
    api_client.post_to_unsubscribe(uid=uid, subscriber_id=subscriber_id)

    # 用戶註銷帳號
    api_client.post_to_unregister(uid=uid)
