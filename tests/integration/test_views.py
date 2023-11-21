import logging
import pytest
from switchbot import bootstrap, views, gh_intent
from switchbot.service_layer import unit_of_work
from switchbot.adapters import iot_api_server
from switchbot.domain import commands

logger = logging.getLogger(__name__)


@pytest.fixture
def memory_bus():
    return bootstrap.bootstrap(
        uow=unit_of_work.MemoryUnitOfWork(),
        start_orm=False,
        iot=iot_api_server.FakeApiServer()
    )


def test_user_profile_by_uid_view(memory_bus):
    memory_bus.handle(commands.Register(secret='secret1', token='token1'))
    u = memory_bus.uow.users.get_by_secret('secret1')
    memory_bus.handle(commands.RequestSync(uid=u.uid, devices=[
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
    ]))

    data = views.user_profile_by_uid(uid=u.uid, uow=memory_bus.uow)
    logger.debug(f'views.user_profile_by_uid {data}')
    assert isinstance(data, dict)
    assert data.get("uid") == u.uid
    assert data.get("devices") == 2
    assert data.get("states") == 0
    assert data.get("changes") == 0


def test_user_profile_by_secret_view(memory_bus):
    memory_bus.handle(commands.Register(secret='secret1', token='token1'))
    u = memory_bus.uow.users.get_by_secret('secret1')
    memory_bus.handle(commands.RequestSync(uid=u.uid, devices=[
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
    ]))

    data = views.user_profile_by_secret(secret=u.secret, uow=memory_bus.uow)
    logger.debug(f'views.user_profile_by_uid {data}')
    assert isinstance(data, dict)
    assert data.get("uid") == u.uid
    assert data.get("devices") == 2
    assert data.get("states") == 0
    assert data.get("changes") == 0


def test_user_sync_intent_fulfillment_view(memory_bus):
    memory_bus.handle(commands.Register(secret='secret1', token='token1'))
    u = memory_bus.uow.users.get_by_secret('secret1')
    memory_bus.handle(commands.RequestSync(uid=u.uid, devices=[
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
    ]))
    data = views.get_user_sync_intent_fulfillment(
        uid=u.uid, subscriber_id='aog', request_id='test', uow=memory_bus.uow)
    assert gh_intent.SyncResponse.load(data)


def test_user_query_intent_fulfillment_view(memory_bus):
    pass


def test_user_execute_intent_fulfillment_view(memory_bus):
    pass
