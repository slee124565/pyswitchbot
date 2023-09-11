# pylint: disable=attribute-defined-outside-init
import abc

from switchbot.adapters import switchbotapi


class AbstractUnitOfWork(abc.ABC):
    devices: switchbotapi.AbstractSwitchBotApiServer

    def collect_new_events(self):
        for dev in self.devices.seen:
            while dev.events:
                yield dev.events.pop(0)

