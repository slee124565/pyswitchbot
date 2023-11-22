import logging
from switchbot.service_layer import unit_of_work
from switchbot.domain import model
from switchbot import gh_intent

logger = logging.getLogger(__name__)


def user_profile_by_uid(uid: str, uow: unit_of_work.AbstractUnitOfWork) -> dict:
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        data = {}
        if u:
            data.update({
                'uid': u.uid,
                'devices': len(u.devices),
                'states': len(u.states),
                'changes': len(u.changes),
            })
        return data


def user_profile_by_secret(secret: str, uow: unit_of_work.AbstractUnitOfWork) -> dict:
    with uow:
        u = uow.users.get_by_secret(secret=secret)
        data = {}
        if u:
            data.update({
                'uid': u.uid,
                'devices': len(u.devices),
                'states': len(u.states),
                'changes': len(u.changes),
            })
        return data


def _convert_dev_to_aog_sync_dto(dev: model.SwitchBotDevice) -> gh_intent.SyncDevice:
    if dev.device_type in ['Plug Mini (US)']:
        _dev_id = dev.device_id
        _dev_type = "action.devices.types.OUTLET"
        _dev_traits = ["action.devices.traits.OnOff"]
        _name = dev.device_name
        _will_report_state = True
        sync_dev = gh_intent.SyncDevice(
            device_id=_dev_id,
            name=gh_intent.SyncDeviceName(name=_name),
            device_type=_dev_type,
            traits=_dev_traits,
            will_report_state=_will_report_state
        )
    else:
        logger.warning(f'device object: {dev.dump()}')
        raise NotImplementedError

    return sync_dev


def user_sync_intent_fulfillment(
        uid: str, subscriber_id: str, request_id: str, uow: unit_of_work.AbstractUnitOfWork
):
    """
    0. 檢查 subscriber_id 是否屬於 user.subscribers
    1. 設定 agentUserId = uid
    2. 設定 user device sync data list
    """
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')
        sync_dto = gh_intent.SyncResponse(
            requestId=request_id,
            payload=gh_intent.SyncResponsePayload(
                agentUserId=f"{u.uid}",
                devices=[_convert_dev_to_aog_sync_dto(dev) for dev in u.devices]
            )
        )
    return sync_dto.dump()


def _convert_dev_state_to_dev_state_dto(dev_state: model.SwitchBotStatus) -> gh_intent.QueryDeviceStatus:
    if dev_state.device_type in ['Plug Mini (US)']:
        return gh_intent.QueryDeviceStatus(
            online=True,
            status="SUCCESS",
            extra_fields={
                "on": True if dev_state.power == "on" else False
            }
        )
    else:
        logger.warning(f'device status object: {dev_state.dump()}')
        raise NotImplementedError


def user_query_intent_fulfillment(
        uid: str, subscriber_id: str, gh_query_dto: gh_intent.QueryRequest, uow: unit_of_work.AbstractUnitOfWork
) -> dict:
    """
    1. 檢查 subscriber_id 是否屬於 user.subscribers
    2.
    """
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')
        dev_dto_ids = [dev_dto.id for dev_dto in gh_query_dto.inputs[0].payload.devices]
        dev_dto_states = {
            f"{_id}": _convert_dev_state_to_dev_state_dto(u.get_dev_state(dev_id=_id))
            for _id in dev_dto_ids
        }
        query_resp_dto = gh_intent.QueryResponse(
            requestId=gh_query_dto.requestId,
            payload=gh_intent.QueryResponsePayload(
                devices=dev_dto_states
            )
        )
    return query_resp_dto.dump()


def _convert_dev_state_to_dev_exec_cmd_state(dev_state: model.SwitchBotStatus) -> gh_intent.ExecuteCommandResponseItem:
    if dev_state.device_type in ['Plug Mini (US)']:
        return gh_intent.ExecuteCommandResponseItem(
            ids=[dev_state.device_id],
            status="PENDING",
            states={
                "online": True,
                "on": True if dev_state.power == "on" else False
            }
        )
    else:
        raise NotImplementedError


def user_exec_intent_fulfillment(
        uid: str, subscriber_id: str, gh_exec_dto: gh_intent.ExecuteRequest, uow: unit_of_work.AbstractUnitOfWork
) -> dict:
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')
        if gh_exec_dto.inputs[0].intent != gh_intent.ExecuteInputItem.INTENT:
            raise ValueError
        if len(gh_exec_dto.inputs) != 1:
            raise NotImplementedError
        if len(gh_exec_dto.inputs[0].payload.commands) != 1:
            raise NotImplementedError
        req_cmd = gh_exec_dto.inputs[0].payload.commands[0]
        _commands = [
            _convert_dev_state_to_dev_exec_cmd_state(
                u.get_dev_state(dev_id=_dev.id))
            for _dev in req_cmd.devices
        ]
        exec_resp_dto = gh_intent.ExecuteResponse(
            requestId=gh_exec_dto.requestId,
            payload=gh_intent.ExecuteResponsePayload(
                commands=_commands
            )
        )
    return exec_resp_dto.dump()
