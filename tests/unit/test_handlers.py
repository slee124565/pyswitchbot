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


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._products for b in p.batches if b.reference == batchref),
            None,
        )


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


class TestRequestSync:
    def test_new_devices_added(self):
        # bus.handle(commands.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None))
        # bus.handle(commands.Allocate("o1", "COMPLICATED-LAMP", 10))
        # [batch] = bus.uow.products.get("COMPLICATED-LAMP").batches
        # assert batch.available_quantity == 90
        # raise NotImplementedError
        bus = bootstrap_test_app()
        bus.handle(commands.RequestSync('user_id', _init_dev_data_list))
        assert [dev.dump() for dev in bus.uow.devices] == _init_dev_data_list

    def test_a_device_name_changed(self):
        raise NotImplementedError

    def test_a_device_removed(self):
        raise NotImplementedError

    def test_no_device_changed(self):
        raise NotImplementedError
