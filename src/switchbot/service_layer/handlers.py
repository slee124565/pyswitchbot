import logging
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from switchbot.domain import commands, events, model
from switchbot.adapters import iot_api_server
# if TYPE_CHECKING:
#     from . import unit_of_work
from . import unit_of_work

logger = logging.getLogger(__name__)


class InvalidSrcServer(Exception):
    pass


# def send_dev_ctrl_cmd(
#         cmd: commands.SendDeviceCtrlCmd,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         # dev = uow.devices.get(dev_id=cmd.dev_id)
#         response = uow.api_server.send_dev_ctrl_cmd(
#             secret=cmd.secret,
#             token=cmd.token,
#             dev_id=cmd.dev_id,
#             cmd_type=cmd.cmd_type,
#             cmd_value=cmd.cmd_value,
#             cmd_param=cmd.cmd_param
#         )


# def get_device_list(
#         cmd: commands.GetDeviceList,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         dev_list = uow.api_server.get_dev_list(
#             secret=cmd.secret,
#             token=cmd.token
#         )


# def check_auth_token(
#         cmd: commands.CheckAuthToken,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         uow.api_server.get_dev_list(
#             secret=cmd.secret,
#             token=cmd.token
#         )


# def exec_manual_scene(
#         cmd: commands.ExecManualScene,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         uow.api_server.exec_manual_scene(
#             secret=cmd.secret,
#             token=cmd.token,
#             scene_id=cmd.scene_id
#         )


# def config_webhook(
#         cmd: commands.ConfigWebhook,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         uow.api_server.create_webhook_config(
#             secret=cmd.secret,
#             token=cmd.token,
#             url=cmd.url
#         )


# def update_webhook(
#         cmd: commands.UpdateWebhook,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         uow.api_server.update_webhook_config(
#             secret=cmd.secret,
#             token=cmd.token,
#             url=cmd.url,
#             enable=True
#         )


# def delete_webhook(
#         cmd: commands.DeleteWebhook,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     with uow:
#         uow.api_server.delete_webhook_config(
#             secret=cmd.secret,
#             token=cmd.token,
#             url=cmd.url,
#         )


# def report_event(
#         cmd: commands.ReportEvent,
#         uow: unit_of_work.AbstractUnitOfWork
# ):
#     # with uow:
#     #     uow.devices.report_event(
#     #
#     #     )
#     raise NotImplementedError


def report_state(
        cmd: commands.ReportState,
        uow: unit_of_work.AbstractUnitOfWork
):
    logger.debug(f'cmd: {cmd}')
    with uow:
        state = model.SwitchBotStatus.load(cmd.state)
        uow.users.update_dev_state(state)


def request_sync(
        cmd: commands.RequestSync,
        uow: unit_of_work.AbstractUnitOfWork
):
    """sync with user devices data"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        user_repo = uow.users.get(user_id=cmd.user_id)
        _devices = [model.SwitchBotDevice.load(data) for data in cmd.devices]
        user_repo.request_sync(devices=_devices)


def unlink_user(
        cmd: commands.Disconnect,
        uow: unit_of_work.AbstractUnitOfWork
):
    """unlink user from service"""
    logger.debug(f'cmd: {cmd}')
    with uow:
        uow.users.remove(user_id=cmd.user_id)


EVENT_HANDLERS = {
    # events.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    # events.Deallocated: [remove_allocation_from_read_model, reallocate],
    # events.OutOfStock: [send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    # commands.CheckAuthToken: check_auth_token,
    # commands.GetDeviceList: get_device_list,
    # commands.SendDeviceCtrlCmd: send_dev_ctrl_cmd,
    # commands.ExecManualScene: exec_manual_scene,
    # commands.ConfigWebhook: config_webhook,
    # commands.UpdateWebhook: update_webhook,
    # commands.DeleteWebhook: delete_webhook,
    # commands.ReportEvent: report_event,
    commands.ReportState: report_state,
    commands.RequestSync: request_sync,
    commands.Disconnect: unlink_user,
}  # type: Dict[Type[commands.Command], Callable]
