import logging
from typing import List, Dict, Callable, Type  # , TYPE_CHECKING
from switchbot.domain import commands, events, model
from switchbot.adapters.iot_api_server import SwitchBotApiServer
# if TYPE_CHECKING:
#     from . import unit_of_work
from . import unit_of_work

logger = logging.getLogger(__name__)


class InvalidSrcServer(Exception):
    pass


class SwBotIotError(Exception):
    pass


def send_dev_ctrl_cmd(
        cmd: commands.SendDevCtrlCmd,
        uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug(f'cmd: {cmd}')
    with uow:
        u = uow.users.get_by_uid(uid=cmd.uid)
        if u is None:
            raise ValueError(f"uid {cmd.uid} not exist in users")
        if cmd.subscriber_id not in u.subscribers:
            raise ValueError(f"subscriber {cmd.subscriber_id} not in user {cmd.uid} subscribers")
        api_server = SwitchBotApiServer()
        api_server.send_dev_ctrl_cmd(
            secret=u.secret,
            token=u.token,
            dev_id=cmd.dev_id,
            cmd_type=cmd.cmd_type,
            cmd_value=cmd.cmd_value,
            cmd_param=cmd.cmd_param
        )
        u.set_dev_ctrl_cmd_sent(
            dev_id=cmd.dev_id,
            cmd=model.SwitchBotCommand(
                commandType=cmd.cmd_type,
                command=cmd.cmd_value,
                parameter=cmd.cmd_param)
        )
        uow.commit()


def report_state(
        cmd: commands.ReportState,
        uow: unit_of_work.AbstractUnitOfWork
):
    """
    {
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
    """
    logger.debug(f'cmd: {cmd}')
    with uow:
        state = model.SwitchBotStatus(
            device_id=cmd.state.get("deviceId"),
            device_type=cmd.state.get("deviceType"),
            hub_device_id=cmd.state.get("hubDeviceId"),
            power=cmd.state.get("power"),
            version=cmd.state.get("version"),
            voltage=cmd.state.get("voltage"),
            weight=cmd.state.get("weight"),
            electricity_of_day=cmd.state.get("electricityOfDay"),
            electric_current=cmd.state.get("electricCurrent")
        )
        u = uow.users.get_by_uid(uid=cmd.uid)
        u.update_dev_state(state=state)
        uow.commit()


def report_change(
        cmd: commands.ReportChange,
        uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug(f'cmd: {cmd}')
    with uow:
        dev_id = cmd.change.get("context", {}).get("deviceMac", None)
        if dev_id is None:
            raise ValueError(f"dev_id not exist, {cmd.change}")
        u = uow.users.get_by_dev_id(dev_id=dev_id)
        if u is None:
            raise ValueError(f"dev_id {dev_id} not exist in users")
        u.add_change_report(model.SwitchBotChangeReport(
            event_type=cmd.change.get("eventType"),
            event_version=cmd.change.get("eventVersion"),
            context=cmd.change.get("context")
        ))
        uow.commit()


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
        u = uow.users.get_by_uid(uid=cmd.user_id)
        if u:
            u.unsubscribe(cmd.subscriber_id)
        uow.commit()


def subscribe_user_iot(
        cmd: commands.Subscribe,
        uow: unit_of_work.AbstractUnitOfWork
):
    """3rd party service (aog) subscribe user iot service"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        u = uow.users.get_by_uid(uid=cmd.uid)
        u.subscribe(subscriber_id=cmd.subscriber_id)
        uow.commit()


def unsubscribe_user_iot(
        cmd: commands.Unsubscribe,
        uow: unit_of_work.AbstractUnitOfWork
):
    """3rd party service (aog) subscribe user iot service"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        u = uow.users.get_by_uid(uid=cmd.uid)
        u.unsubscribe(subscriber_id=cmd.subscriber_id)
        uow.commit()


def unregister_user(
        cmd: commands.Unregister,
        uow: unit_of_work.AbstractUnitOfWork
):
    """register user iot service w/key-pair"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        u = uow.users.get_by_uid(uid=cmd.uid)
        if not u:
            raise SwBotIotError(f'user {cmd.uid} is not exist')
        uow.users.delete(uid=cmd.uid)
        uow.commit()


def register_user(
        cmd: commands.Register,
        uow: unit_of_work.AbstractUnitOfWork
):
    """register user iot service w/key-pair"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        u = uow.users.get_by_secret(secret=cmd.secret)
        if u:
            raise SwBotIotError(f'register secret already been used by user {u.uid}')
        user = model.SwitchBotUserFactory.create_user(
            secret=cmd.secret,
            token=cmd.token
        )
        uow.users.add(u=user)
        uow.commit()


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
    commands.Unsubscribe: unsubscribe_user_iot,
    commands.RequestSync: request_sync,
    commands.ReportState: report_state,
    commands.ReportChange: report_change,
    commands.SendDevCtrlCmd: send_dev_ctrl_cmd,
    commands.Disconnect: unlink_user,
}  # type: Dict[Type[commands.Command], Callable]
