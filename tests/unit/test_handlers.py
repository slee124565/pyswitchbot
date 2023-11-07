from switchbot import bootstrap
from switchbot.service_layer import unit_of_work
from switchbot.adapters import iot_api_server
from switchbot.domain import commands

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


def bootstrap_test_app():
    return bootstrap.bootstrap(
        uow=unit_of_work.MemoryUnitOfWork(),
        start_orm=False,
        iot=iot_api_server.FakeApiServer()
    )


class TestRegister:
    def test_register(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        bus.handle(commands.Register(secret='secret2', token='token2'))
        u1 = bus.uow.users.get_by_secret(secret='secret1')
        u2 = bus.uow.users.get_by_secret(secret='secret2')
        assert all([u1, u2])
        assert u1.token == 'token1'
        assert u2.token == 'token2'

    def test_unregister(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        bus.handle(commands.Register(secret='secret2', token='token2'))
        u1 = bus.uow.users.get_by_secret(secret='secret1')
        bus.handle(commands.Unregister(uid=u1.uid))
        assert bus.uow.users.get_by_uid(uid=u1.uid) is None
        assert bus.uow.users.get_by_secret('secret2')


class TestRequestSync:
    def test_new_devices_added(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))
        u = bus.uow.users.get_by_uid(uid=u.uid)
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


class TestReportState:
    def test_update_device_status(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret1', token='token1'))
        u = bus.uow.users.get_by_secret('secret1')
        bus.handle(commands.RequestSync(uid=u.uid, devices=_init_dev_data_list))

        bus.handle(commands.ReportState(_dev_status_data))

        dev_id = _dev_status_data.get("deviceId")
        u = bus.uow.users.get_by_uid(uid=u.uid)
        dev_state = bus.uow.users.get_dev_state_by_did(uid=u.uid, did=dev_id)
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


class TestSubscribe:

    def test_subscribe(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Subscribe(secret='secret'))
        """subscriber 是否屬於另一個 aggregator?"""

    def test_unsubscribe(self):
        pass
