from typing import List, Union
from switchbot.adapters.iot_api_server import AbstractIotApiServer
from switchbot.domain import model


class FakeSwitchBotApiServer(AbstractIotApiServer):
    def get_dev_list(self, secret: str, token: str) -> List[model.SwitchBotDevice]:
        raise NotImplementedError

    def get_dev_status(self, secret: str, token: str, dev_id: str) -> model.SwitchBotStatus:
        raise NotImplementedError

    def send_dev_ctrl_cmd(self, secret: str, token: str, dev_id: str, cmd_type: str, cmd_value: str,
                          cmd_param: Union[str, dict]):
        raise NotImplementedError

    def get_scene_list(self, secret: str, token: str) -> List[model.SwitchBotScene]:
        raise NotImplementedError

    def exec_manual_scene(self, secret: str, token: str, scene_id: str):
        raise NotImplementedError

    def create_webhook_config(self, secret: str, token: str, url: str):
        raise NotImplementedError

    def read_webhook_config(self, secret: str, token: str) -> List[str]:
        raise NotImplementedError

    def read_webhook_config_list(self, secret: str, token: str, url_list: List[str]):
        raise NotImplementedError

    def update_webhook_config(self, secret: str, token: str, url: str, enable: bool):
        raise NotImplementedError

    def delete_webhook_config(self, secret: str, token: str, url: str):
        raise NotImplementedError
