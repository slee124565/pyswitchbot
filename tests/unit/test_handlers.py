import os
import logging
import pytest
from switchbot import bootstrap
from switchbot.service_layer import unit_of_work
from switchbot.adapters import iot_api_server
from switchbot.domain import commands
from switchbot.service_layer.handlers import SwBotIotError

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


def bootstrap_test_app():
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
    return bootstrap.bootstrap(
        uow=unit_of_work.JsonFileUnitOfWork(json_file=JSON_FILE),
        # uow=unit_of_work.MemoryUnitOfWork(),
        start_orm=False,
        iot=iot_api_server.FakeApiServer()
    )


class TestRegister:
    def test_register(self):
        bus = bootstrap_test_app()

        bus.handle(commands.Register(secret='secret1', token='token1'))
        bus.handle(commands.Register(secret='secret2', token='token2'))
        count = bus.uow.users.count()
        assert count == 2
        u1 = bus.uow.users.get_by_secret(secret='secret1')
        u2 = bus.uow.users.get_by_secret(secret='secret2')
        assert all([u1, u2])
        assert u1.token == 'token1'
        assert u2.token == 'token2'

        bus.handle(commands.Unregister(uid=u1.uid))
        assert bus.uow.users.get_by_uid(uid=u1.uid) is None
        assert bus.uow.users.get_by_secret('secret2')
        assert count == bus.uow.users.count() + 1

    def test_unregister(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        bus.handle(commands.Register(secret='secret2', token='token2'))
        count = bus.uow.users.count()
        assert count == 2
        u1 = bus.uow.users.get_by_secret(secret='secret1')

        bus.handle(commands.Unregister(uid=u1.uid))

        assert bus.uow.users.get_by_uid(uid=u1.uid) is None
        assert bus.uow.users.get_by_secret('secret2')
        count = bus.uow.users.count()
        assert count == 1


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
        assert len(u.states) == 1
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
    """todo: JTBD"""

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
        assert len(u.get_subscribers()) == 1

        bus.handle(commands.Unsubscribe(uid=uid, subscriber_id=subscriber_id))
        u = bus.uow.users.get_by_uid(uid=uid)
        assert len(u.get_subscribers()) == 0
