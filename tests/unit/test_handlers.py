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
        start_orm=False,
        uow=unit_of_work.MemoryUnitOfWork(),
        iot=iot_api_server.FakeApiServer()
    )


class TestRegister:
    def test_register(self):
        bus = bootstrap_test_app()
        user1 = bus.handle(commands.Register(secret='secret1', token='token'))
        user2 = bus.handle(commands.Register(secret='secret2', token='token'))
        assert bus.uow.users.get(uid=user1.uid) is not None

    def test_user_disconnect(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(secret='secret', token='token'))
        bus.handle(commands.Register(secret='secret', token='token'))
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        bus.handle(commands.Disconnect(user_id='user_id'))
        assert bus.uow.users.get(user_id='user_id') is None


class TestSubscribe:

    def test_subscribe(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Subscribe(secret='secret'))
        """subscriber 是否屬於另一個 aggregator?"""

    def test_unsubscribe(self):
        pass


class TestReportState:
    def test_update_device_status(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(user_id='user_id', secret='secret', token='token'))

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        bus.handle(commands.ReportState(_dev_status_data))

        _user = bus.uow.users.get(user_id='user_id')
        _dev = next((dev for dev in _user.devices
                     if dev.device_id == _dev_status_data['deviceId']))
        assert _dev.state.dump() == _dev_status_data


class TestRequestSync:
    def test_new_devices_added(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(user_id='user_id', secret='secret', token='token'))

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _user = bus.uow.users.get(user_id='user_id')
        assert [dev.dump() for dev in _user.devices] == _init_dev_data_list

    def test_a_device_name_changed(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(user_id='user_id', secret='secret', token='token'))
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _init_dev_data_list[1]['deviceName'] = '床頭燈'
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _user = bus.uow.users.get(user_id='user_id')
        for dev in _user.devices:
            if dev.device_id == '6055F92FCFD2':
                assert dev.device_name == '小風扇開關'
            elif dev.device_id == '6055F930FF22':
                assert dev.device_name == '床頭燈'
            else:
                assert False
        assert len(_user.devices) == 2

    def test_a_device_removed(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(user_id='user_id', secret='secret', token='token'))

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        del _init_dev_data_list[1]
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _user = bus.uow.users.get(user_id='user_id')
        assert len(_user.devices) == 1
        device = _user.devices[0]
        assert device.device_id == '6055F92FCFD2'
        assert device.device_name == '小風扇開關'
        assert device.device_type == 'Plug Mini (US)'

    def test_no_device_changed(self):
        bus = bootstrap_test_app()
        bus.handle(commands.Register(user_id='user_id', secret='secret', token='token'))

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _user = bus.uow.users.get(user_id='user_id')
        assert [dev.dump() for dev in _user.devices] == _init_dev_data_list
