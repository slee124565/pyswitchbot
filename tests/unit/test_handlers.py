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
    def _remove(self, user_id: str):
        n = next((n for n, user in enumerate(self._users) if user.user_id == user_id), None)
        if n is not None:
            del self._users[n]
        else:
            raise ValueError(f'User ({user_id}) not exist')

    def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
        for user in self._users:
            return next((dev for dev in user.devices if dev.device_id == dev_id))
        raise ValueError(f'Device ({dev_id}) not exist')

    def __init__(self):
        super().__init__()
        self._users = [
            model.SwitchBotUserRepo(
                user_id='user_id',
                devices=[],
                scenes=[],
                webhooks=[]
            ),
            model.SwitchBotUserRepo(
                user_id='tester',
                devices=[],
                scenes=[],
                webhooks=[]
            ),
        ]

    def _get(self, user_id: str) -> model.SwitchBotUserRepo:
        return next((user for user in self._users if user.user_id == user_id), None)

    def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
        user = self._get(user_id=user_id)
        user.devices.extend(devices)

    # def _get(self, user_id: str) -> List[SwitchBotDevice]:
    #     raise Exception

    # def _list(self, user_id: str) -> List[model.SwitchBotDevice]:
    #     return self._devices

    # def _update(self, status: model.SwitchBotStatus):
    #     dev = next((dev for dev in self._devices if dev.device_id == status.device_id))
    #     dev.state = status


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.users = FakeRepository()
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
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        bus.handle(commands.Disconnect(user_id='user_id'))

        assert bus.uow.users.get(user_id='user_id') is None


class TestReportState:
    def test_update_device_status(self):
        bus = bootstrap_test_app()

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        bus.handle(commands.ReportState(_dev_status_data))

        _user = bus.uow.users.get(user_id='user_id')
        _dev = next((dev for dev in _user.devices
                     if dev.device_id == _dev_status_data['deviceId']))
        assert _dev.state.dump() == _dev_status_data


class TestRequestSync:
    def test_new_devices_added(self):
        bus = bootstrap_test_app()

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _user = bus.uow.users.get(user_id='user_id')
        assert [dev.dump() for dev in _user.devices] == _init_dev_data_list

    def test_a_device_name_changed(self):
        bus = bootstrap_test_app()
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

        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))

        _user = bus.uow.users.get(user_id='user_id')
        assert [dev.dump() for dev in _user.devices] == _init_dev_data_list
