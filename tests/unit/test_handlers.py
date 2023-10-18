from typing import List
from switchbot import bootstrap
from switchbot.service_layer import unit_of_work
from switchbot.adapters import repository
from switchbot.domain import model, commands

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


class FakeRepository(repository.AbstractRepository):
    def __init__(self, devices: List[model.SwitchBotDevice]):
        super().__init__()
        self._devices = devices

    def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
        self._devices.extend(devices)

    def _get(self, user_id: str) -> List[model.SwitchBotDevice]:
        return self._devices


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.devices = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
    )


class TestDisconnect:
    def test_user_disconnect(self):
        bus = bootstrap_test_app()

        bus.handle(commands.Disconnect(user_id='user_id'))

        assert not bus.uow.devices.get(user_id='user_id')


class TestReportState:
    def test_update_device_status(self):
        bus = bootstrap_test_app()

        bus.handle(commands.ReportState(_dev_status_data))

        _devices = bus.uow.devices.get(user_id='user_id')
        _dev = next((dev for dev in _devices if dev.device_id == _dev_status_data['deviceId']))
        assert _dev.state.dump() == _dev_status_data


class TestRequestSync:
    def test_new_devices_added(self):
        bus = bootstrap_test_app()

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _devices = bus.uow.devices.get(user_id='user_id')
        assert [dev.dump() for dev in _devices] == _init_dev_data_list

    def test_a_device_name_changed(self):
        bus = bootstrap_test_app()

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        _init_dev_data_list[0]['deviceName'] = '床頭燈'
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _devices = bus.uow.devices.get(user_id='user_id')
        for dev in _devices:
            if dev.device_id == '6055F92FCFD2':
                assert dev.device_name == '小風扇開關'
            elif dev.device_id == '6055F930FF22':
                assert dev.device_name == '床頭燈'
            else:
                assert False
        assert len(_devices) == 2

    def test_a_device_removed(self):
        bus = bootstrap_test_app()

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        del _init_dev_data_list[1]
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _devices = bus.uow.devices.get(user_id='user_id')
        assert len(_devices) == 1
        device = _devices[0]
        assert device.device_id == '6055F92FCFD2'
        assert device.device_name == '小風扇開關'
        assert device.device_type == 'Plug Mini (US)'

    def test_no_device_changed(self):
        bus = bootstrap_test_app()

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _devices = bus.uow.devices.get(user_id='user_id')
        assert [dev.dump() for dev in _devices] == _init_dev_data_list
