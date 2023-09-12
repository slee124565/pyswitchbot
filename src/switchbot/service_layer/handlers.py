from typing import List, Dict, Callable, Type, TYPE_CHECKING
from switchbot.domain import commands, events, model
# if TYPE_CHECKING:
#     from . import unit_of_work
from . import unit_of_work


def get_device_list(
        cmd: commands.CheckAuthToken,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        devices = uow.devices.get_dev_list(
            secret=cmd.secret,
            token=cmd.token
        )

    return devices


def check_auth_token(
        cmd: commands.CheckAuthToken,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.devices.get_dev_list(
            secret=cmd.secret,
            token=cmd.token
        )


EVENT_HANDLERS = {
    # events.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    # events.Deallocated: [remove_allocation_from_read_model, reallocate],
    # events.OutOfStock: [send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CheckAuthToken: check_auth_token,
    commands.GetDeviceList: get_device_list
    # commands.Allocate: allocate,
    # commands.CreateBatch: add_batch,
    # commands.ChangeBatchQuantity: change_batch_quantity,
}  # type: Dict[Type[commands.Command], Callable]
