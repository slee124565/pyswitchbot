import logging
from typing import List, Dict, Callable, Type  # , TYPE_CHECKING
from switchbot.domain import commands, events, model
from switchbot.adapters import iot_api_server
# if TYPE_CHECKING:
#     from . import unit_of_work
from . import unit_of_work

logger = logging.getLogger(__name__)


class InvalidSrcServer(Exception):
    pass


def report_state(
        cmd: commands.ReportState,
        uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug(f'cmd: {cmd}')
    with uow:
        state = model.SwitchBotStatus.load(cmd.state)
        uow.users.update_dev_state(state)


def report_change(
        cmd: commands.ReportChange,
        uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug(f'cmd: {cmd}')
    with uow:
        change = model.SwitchBotChangeReport.load(cmd.change)
        uow.users.update_dev_change(change)


def request_sync(
        cmd: commands.RequestSync,
        uow: unit_of_work.AbstractUnitOfWork
):
    """sync with user devices data"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        user = uow.users.get_by_uid(uid=cmd.uid)
        if user is None:
            raise ValueError(f'User ({cmd.uid}) not exist')
        _devices = [model.SwitchBotDevice(
            device_id=data.get("deviceId"),
            device_name=data.get("deviceName"),
            device_type=data.get("deviceType"),
            enable_cloud_service=data.get("enableCloudService"),
            hub_device_id=data.get("hubDeviceId")
        ) for data in cmd.devices]
        user.request_sync(devices=_devices)
        uow.commit()


def unlink_user(
        cmd: commands.Disconnect,
        uow: unit_of_work.AbstractUnitOfWork
):
    """unlink user from service"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        uow.users.remove(user_id=cmd.user_id)


def subscribe_user_iot(
        cmd: commands.Subscribe,
        uow: unit_of_work.AbstractUnitOfWork
):
    """3rd party service (aog) subscribe user iot service"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        uow.users.subscribe(secret=cmd.secret)
        uow.commit()


def unregister_user(
        cmd: commands.Unregister,
        uow: unit_of_work.AbstractUnitOfWork
):
    """register user iot service w/key-pair"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        uow.users.unregister(uid=cmd.uid)
        uow.commit()


def register_user(
        cmd: commands.Register,
        uow: unit_of_work.AbstractUnitOfWork
):
    """register user iot service w/key-pair"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        user = model.SwitchBotUserFactory.create_user(
            secret=cmd.secret,
            token=cmd.token
        )
        uow.users.register(user=user)
        uow.commit()
    return user


def pull_user_devices(
        event: events.UserRegistered,
        uow: unit_of_work.AbstractUnitOfWork
        # iot: iot_api_server.AbstractIotApiServer
):
    """todo: Register >> pull user device from switchbot openapi"""
    with uow:
        user = uow.users.get(user_id=event.user_id)
        devices = uow.api_server.get_dev_list(
            secret=user.secret,
            token=user.token,
        )
        user.request_sync(devices=devices)
        uow.commit()


def pull_user_dev_states(
        event: events.UserDevFetched,
        iot: iot_api_server.AbstractIotApiServer
):
    """todo: pull user devices state from switchbot openapi"""
    logger.warning('todo: pull_dev_states')


def pub_user_synced(
        event: events.UserDevSynced,
        publish: Callable
):
    """todo: publish user devices synced event for other system"""
    logger.warning('todo: pub_user_synced')


def setup_user_switchbot_webhook(
        event: events.UserDevSynced,
        iot: iot_api_server.AbstractIotApiServer
):
    """todo: config user webhook config for switchbot open-api"""
    logger.warning('todo: setup_user_switchbot_webhook')


EVENT_HANDLERS = {
    events.UserRegistered: [pull_user_devices],
    events.UserDevFetched: [pull_user_dev_states],
    events.UserDevSynced: [pub_user_synced, setup_user_switchbot_webhook],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.Register: register_user,
    commands.Unregister: unregister_user,
    commands.Subscribe: subscribe_user_iot,
    commands.RequestSync: request_sync,
    commands.ReportState: report_state,
    commands.ReportChange: report_change,
    commands.Disconnect: unlink_user,
}  # type: Dict[Type[commands.Command], Callable]
