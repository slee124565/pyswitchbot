import os
import logging
from switchbot import bootstrap
from switchbot.service_layer import unit_of_work
from switchbot.adapters import iot_api_server
from switchbot.domain import commands

logger = logging.getLogger(__name__)

_init_dev_data_list = [
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

_dev_status_data = {
    "deviceId": "6055F92FCFD2",
    "deviceType": "Plug Mini (US)",
    "hubDeviceId": "6055F92FCFD2",
    "power": "off",
    "version": "V1.4-1.4",
    "voltage": 114.7,
    "weight": 0.0,
    "electricityOfDay": 3,
    "electricCurrent": 0.0
}
JSON_FILE = '.teststore'
_test_uow = unit_of_work.JsonFileUnitOfWork(json_file=JSON_FILE)
_test_iot = iot_api_server.FakeApiServer()


def bootstrap_test_app():
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
    return bootstrap.bootstrap(
        uow=_test_uow,
        # uow=unit_of_work.MemoryUnitOfWork(),
        start_orm=False,
        iot=_test_iot
    )


class TestRegister:
    def test_user_first_register(self):
        """
        用戶系統 (Common Service) 可以透過用戶 SwitchBot KeyPairs 對本系統進行用戶註冊 (Register)，本系統會針對這個用戶，
        產生一組 uid (userID)，(Registered) 之後、本系統會透過 OpenAPI 服務查詢用戶設備列表，設定用戶在 OpenAPI 系統中設備狀態通知
        Webhook 的 URI 設定 (UpdateUserWebhook)，更新用戶在本系統內的設備清單 (RequestSync)，並且查詢用戶設備的狀態 (ReportState)
        記錄在本系統資料庫中，藉以支援 AoG Intent API & Webhook 服務
        """
        bus = bootstrap_test_app()

        bus.handle(commands.Register(secret='secret1', token='token1'))

        assert bus.uow.users.count() == 1
        u1 = bus.uow.users.get_by_secret(secret='secret1')
        assert u1.token == 'token1'
        assert len(u1.devices) == 2
        assert len(u1.states) == 2

        bus.handle(commands.Unregister(uid=u1.uid))
        assert bus.uow.users.get_by_uid(uid=u1.uid) is None
        assert bus.uow.users.count() == 0

    def test_user_repeat_register(self):
        """用戶重複註冊時，將會觸發用戶設備與狀態的更新"""
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))

        bus.handle(commands.Register(secret='secret1', token='token1'))
        u1 = bus.uow.users.get_by_secret(secret='secret1')
        assert u1.token == 'token1'
        assert len(u1.devices) == 2
        assert len(u1.states) == 2

        bus.handle(commands.Unregister(uid=u1.uid))
        assert bus.uow.users.get_by_uid(uid=u1.uid) is None
        assert bus.uow.users.count() == 0


class TestRequestSync:
    def test_new_devices_added(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))
        u = bus.uow.users.get_by_uid(uid=u.uid)
        logger.warning(f'{len(u.devices)} == {len(_init_dev_data_list)}')
        assert len(u.devices) == len(_init_dev_data_list)
        assert [d.device_id for d in u.devices] == [data.get("deviceId") for data in _init_dev_data_list]

    def test_a_device_name_changed(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        _init_dev_data_list[1]['deviceName'] = '床頭燈'
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        u = bus.uow.users.get_by_uid(uid=u.uid)
        for dev in u.devices:
            if dev.device_id == '6055F92FCFD2':
                assert dev.device_name == '小風扇開關'
            elif dev.device_id == '6055F930FF22':
                assert dev.device_name == '床頭燈'
            else:
                assert False
        assert len(u.devices) == 2

    def test_a_device_removed(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        del _init_dev_data_list[1]
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        u = bus.uow.users.get_by_uid(uid=u.uid)
        assert len(u.devices) == 1
        device = u.devices[0]
        assert device.device_id == '6055F92FCFD2'
        assert device.device_name == '小風扇開關'
        assert device.device_type == 'Plug Mini (US)'

    def test_no_device_changed(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        u = bus.uow.users.get_by_uid(uid=u.uid)
        assert [d.device_id for d in u.devices] == [data.get("deviceId") for data in _init_dev_data_list]


class TestReportChange:
    def test_report_change(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        _dev_change_data = {
            "eventType": "changeReport",
            "eventVersion": "1",
            "context": {
                "deviceType": "WoPlugUS",
                "deviceMac": "6055F92FCFD2",
                "powerState": "ON",
                "timeOfSample": 1698720698088
            }
        }
        bus.handle(commands.ReportChange(change=_dev_change_data))

        dev_id = _dev_change_data.get("context").get("deviceMac")
        u = bus.uow.users.get_by_dev_id(dev_id=dev_id)
        c = u.get_dev_last_change_report(dev_id=dev_id)
        assert c.context.get("timeOfSample") == _dev_change_data.get("context").get("timeOfSample")


class TestReportState:
    def test_update_device_status(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        bus.handle(commands.ReportState(uid=u.uid, state=_dev_status_data))

        dev_id = _dev_status_data.get("deviceId")
        u = bus.uow.users.get_by_uid(uid=u.uid)
        dev_state = u.get_dev_state(dev_id=dev_id)
        assert dev_state
        assert all([
            dev_state.device_id == _dev_status_data.get("deviceId"),
            dev_state.device_type == _dev_status_data.get("deviceType"),
            dev_state.hub_device_id == _dev_status_data.get("hubDeviceId"),
            dev_state.power == _dev_status_data.get("power"),
            dev_state.version == _dev_status_data.get("version"),
            dev_state.voltage == _dev_status_data.get("voltage"),
            dev_state.weight == _dev_status_data.get("weight"),
            dev_state.electricity_of_day == _dev_status_data.get("electricityOfDay"),
            dev_state.electric_current == _dev_status_data.get("electricCurrent"),
        ])


class TestSubscription:
    """
    依據訂閱服務業務規則設計本服務 Testcase
    1. 尚未訂閱用戶 IoT 服務之前，第三方服務無法透過 API 查詢該用戶設備清單 (SYNC)。
    test_aog_service_cannot_access_user_sync_intent_before_subscription
    2. 第三方服務訂閱用戶 IoT 服務成功之後，方可透過 Intent API 查詢該用戶 IoT 設備清單：
    test_aog_service_can_access_user_sync_intent_after_subscription
    3. 第三方服務訂閱用戶 IoT 服務成功之後，方可查詢該用戶多個 IoT 設備的設備狀態：
    test_aog_service_can_access_user_query_intent_after_subscription
    4. 第三方服務訂閱用戶 IoT 服務成功之後，方可傳遞設備執行指令控制設備狀態的改變：
    test_aog_service_can_access_user_exec_intent_after_subscription
    5. 第三方服務訂閱用戶 IoT 服務成功之後，之後用戶設備狀態變更事件發生時，第三方服務會收到該用戶設備狀態更新事件通知 (Webhook)：
    test_subscribed_user_dev_change_webhook_aog_notify_sent
    6. 第三方服務取消訂閱該用戶 IoT 服務 (DISCONNECT) 之後，將無法使用 sync intent API 查詢該用戶 IoT 設備清單：
    test_aog_sync_intent_api_fails_after_disconnect_intent_sent
    7. 第三方服務取消訂閱該用戶 IoT 服務 (DISCONNECT) 之後，該用戶設備狀態變更事件發生時，
    第三方服務也不會收到該用戶設備狀態更新事件通知 (Webhook)：
    test_no_webhook_notify_sent_for_aog_on_disconnected_user_device_change
    """

    def test_subscription(self):
        """第三方服務可以 [訂閱 Subscribe/取消訂閱 Unsubscribe] 本系統用戶IoT服務"""
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))
        uid = u.uid
        subscriber_id = 'aog'
        bus.handle(commands.Subscribe(uid=uid, subscriber_id=subscriber_id))
        bus.handle(commands.Subscribe(uid=uid, subscriber_id=subscriber_id))
        u = bus.uow.users.get_by_uid(uid=uid)
        assert len(u.subscribers) == 1

        bus.handle(commands.Unsubscribe(uid=uid, subscriber_id=subscriber_id))
        u = bus.uow.users.get_by_uid(uid=uid)
        assert len(u.subscribers) == 0


def test_send_dev_ctrl_cmd():
    bus = bootstrap_test_app()
    bus.handle(commands.Register(secret='secret1', token='token1'))
    u = bus.uow.users.get_by_secret('secret1')
    subscriber_id = 'aog'
    bus.handle(commands.Subscribe(uid=u.uid, subscriber_id=subscriber_id))

    d = u.devices[0]
    s = u.get_dev_state(dev_id=d.device_id)
    cmd_value = 'turnOn' if s.power == "on" else "turnOff"
    bus.handle(
        commands.SendDevCtrlCmd(
            uid=u.uid, subscriber_id=subscriber_id, dev_id=d.device_id,
            cmd_type="command", cmd_value=cmd_value, cmd_param="default"
        )
    )
    assert _test_iot.dev_ctrl_cmd_sent
