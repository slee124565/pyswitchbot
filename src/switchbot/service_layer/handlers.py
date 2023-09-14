from typing import List, Dict, Callable, Type, TYPE_CHECKING
from switchbot.domain import commands, events, model
# if TYPE_CHECKING:
#     from . import unit_of_work
from . import unit_of_work


def send_dev_ctrl_cmd(
        cmd: commands.SendDeviceCtrlCmd,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.devices.send_dev_ctrl_cmd(
            secret=cmd.secret,
            token=cmd.token,
            dev_id=cmd.dev_id,
            cmd_type=cmd.cmd_type,
            cmd_value=cmd.cmd_value,
            cmd_param=cmd.cmd_param
        )


def get_device_list(
        cmd: commands.CheckAuthToken,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.devices.get_dev_list(
            secret=cmd.secret,
            token=cmd.token
        )


def check_auth_token(
        cmd: commands.CheckAuthToken,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.devices.get_dev_list(
            secret=cmd.secret,
            token=cmd.token
        )


def exec_manual_scene(
        cmd: commands.ExecManualScene,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.devices.exec_manual_scene(
            secret=cmd.secret,
            token=cmd.token,
            scene_id=cmd.scene_id
        )


EVENT_HANDLERS = {
    # events.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    # events.Deallocated: [remove_allocation_from_read_model, reallocate],
    # events.OutOfStock: [send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CheckAuthToken: check_auth_token,
    commands.GetDeviceList: get_device_list,
    commands.SendDeviceCtrlCmd: send_dev_ctrl_cmd,
    commands.ExecManualScene: exec_manual_scene,
    # commands.Allocate: allocate,
    # commands.CreateBatch: add_batch,
    # commands.ChangeBatchQuantity: change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]
