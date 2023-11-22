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
    memory_bus.handle(commands.Subscribe(uid=u.uid, subscriber_id='aog'))
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
    data = views.user_sync_intent_fulfillment(
        uid=u.uid, subscriber_id='aog', request_id='test', uow=memory_bus.uow)
    assert gh_intent.SyncResponse.load(data)
    obj = gh_intent.SyncResponse.load(data)
    assert isinstance(obj, gh_intent.SyncResponse)
    assert obj.requestId == 'test'
    assert len(obj.payload.devices) == 2
    assert [d.device_id for d in obj.payload.devices] == ["6055F92FCFD2", "6055F930FF22"]


def test_user_query_intent_fulfillment_view(memory_bus):
    memory_bus.handle(commands.Register(secret='secret1', token='token1'))
    u = memory_bus.uow.users.get_by_secret('secret1')
    memory_bus.handle(commands.Subscribe(uid=u.uid, subscriber_id='aog'))
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
    memory_bus.handle(commands.ReportState(uid=u.uid, state={
        "deviceId": "6055F92FCFD2",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F92FCFD2",
        "power": "off",
        "version": "V1.4-1.4",
        "voltage": 114.7,
        "weight": 0.0,
        "electricityOfDay": 3,
        "electricCurrent": 0.0
    }))
    memory_bus.handle(commands.ReportState(uid=u.uid, state={
        "deviceId": "6055F92FCFD2",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F92FCFD2",
        "power": "on",
        "version": "V1.4-1.4",
        "voltage": 114.7,
        "weight": 0.0,
        "electricityOfDay": 3,
        "electricCurrent": 0.0
    }))

    query_intent = gh_intent.QueryRequest(
        requestId='testId',
        inputs=[gh_intent.QueryInputItem(
            intent="",
            payload=gh_intent.QueryPayload(
                devices=[gh_intent.QueryDeviceItem(
                    id="6055F92FCFD2"
                )]
            )
        )]
    )
    data = views.user_query_intent_fulfillment(
        uid=u.uid, subscriber_id="aog", gh_query_dto=query_intent, uow=memory_bus.uow
    )

    assert gh_intent.QueryResponse.load(data)
    obj = gh_intent.QueryResponse.load(data)
    assert isinstance(obj, gh_intent.QueryResponse)
    assert obj.requestId == 'testId'
    assert len(obj.payload.devices) == 1
    dev_states = obj.payload.devices
    assert isinstance(dev_states, dict)
    assert "6055F92FCFD2" in dev_states.keys()
    state = dev_states["6055F92FCFD2"]
    assert isinstance(state, gh_intent.QueryDeviceStatus)
    assert state.extra_fields.get("on") is True


def test_user_execute_intent_fulfillment_view(memory_bus):
    memory_bus.handle(commands.Register(secret='secret1', token='token1'))
    u = memory_bus.uow.users.get_by_secret('secret1')
    memory_bus.handle(commands.Subscribe(uid=u.uid, subscriber_id='aog'))
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
    memory_bus.handle(commands.ReportState(uid=u.uid, state={
        "deviceId": "6055F92FCFD2",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F92FCFD2",
        "power": "off",
        "version": "V1.4-1.4",
        "voltage": 114.7,
        "weight": 0.0,
        "electricityOfDay": 3,
        "electricCurrent": 0.0
    }))
    intent = gh_intent.ExecuteRequest(
        requestId="testId",
        inputs=[gh_intent.ExecuteInputItem(
            intent=gh_intent.ExecuteInputItem.INTENT,
            payload=gh_intent.ExecutePayload(
                commands=[
                    gh_intent.ExecuteCmdItem(
                        devices=[gh_intent.ExecuteCmdDevItem(
                            id="6055F92FCFD2"
                        )],
                        execution=[gh_intent.ExecuteCmdExecItem(
                            command="action.devices.commands.OnOff",
                            params={"on": True}
                        )]
                    )
                ]
            )
        )]
    )

    data = views.user_exec_intent_fulfillment(
        uid=u.uid, subscriber_id='aog', gh_exec_dto=intent, uow=memory_bus.uow
    )
    assert gh_intent.ExecuteResponse.load(data)
    obj = gh_intent.ExecuteResponse.load(data)
    assert isinstance(obj, gh_intent.ExecuteResponse)
    assert obj.requestId == 'testId'
    assert len(obj.payload.commands) == 1
    exec_cmd = obj.payload.commands[0]
    assert isinstance(exec_cmd, dict)
    assert exec_cmd.get("ids") == ["6055F92FCFD2"]
    assert exec_cmd.get("status") in ["SUCCESS", "PENDING", "OFFLINE", "EXCEPTIONS", "ERROR"]
    assert isinstance(exec_cmd.get("states"), dict)
    assert exec_cmd.get("states", None).get("online") is not None
    assert exec_cmd.get("states", None).get("on") is not None
