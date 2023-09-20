import click
import logging
import logging.config as logging_config
import os
import json
from switchbot import bootstrap, views
from switchbot import config
from switchbot.domain import commands

logging_config.dictConfig(config.logging_config)
logger = logging.getLogger(__name__)
# logger.info('switchbot cli process')
bus = bootstrap.bootstrap()
env_secret, env_token = config.get_switchbot_key_pair()


# 主命令
@click.group()
def switchbotcli():
    """SwitchBot Open API CLI tool."""
    pass


# 'auth' 子命令集
@switchbotcli.group(help="Manage authentication.")
def auth():
    """Commands for SwitchBot user authentication."""
    pass


# @auth.command()
# @click.option('--secret', prompt='Your Secret Key', help='Your secret key for authentication.')
# @click.option('--token', prompt='Your Token', help='Your token for authentication.')
# def config(secret, token):
#     """Configure authentication."""
#     click.echo(f"Configured authentication with secret: {secret} and token: {token}")
@auth.command()
@click.option('--secret', prompt='Your Secret Key', help='Your secret key for authentication.')
@click.option('--token', prompt='Your Token', help='Your token for authentication.')
@click.option('--envfile', default='.env', help='Your dotenv config file.')
def config(secret, token, envfile):
    """Configure authentication."""
    lines = [
        f'SWITCHBOTAPI_SECRET_KEY={secret}\n'
        f'SWITCHBOTAPI_TOKEN={token}\n'
    ]
    with open(envfile, 'w') as fh:
        fh.writelines(lines)
    click.echo(f"Configured authentication with secret: {secret} and token: {token}")


@auth.command()
@click.option('--envfile', default='.env', help='Your dotenv config file.')
def list(envfile):
    """List authentication information."""
    click.echo("Listing all authentication information.")
    with open(envfile) as fh:
        click.echo(fh.read())


@auth.command()
@click.option('--secret', default=env_secret, help='Your secret key for authentication.')
@click.option('--token', default=env_token, help='Your token for authentication.')
def check(secret, token):
    """Check authentication status."""
    cmd = commands.CheckAuthToken(secret=secret, token=token)
    bus.handle(cmd)
    click.echo('OK')


# 'device' 子命令集
@switchbotcli.group(help="Manage devices.")
def device():
    """Commands for user devices."""
    pass


@device.command()
@click.option('--save', is_flag=True, help="Save device list.")
def listall(save):
    """List all devices."""
    click.echo(f"Listing all devices. Save: {save}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    # cmd = commands.GetDeviceList(secret=secret, token=token)
    click.echo(
        json.dumps(
            views.get_device_list(
                secret=secret,
                token=token,
                uow=bus.uow
            ), indent=2, ensure_ascii=False
        )
    )


@device.command()
@click.argument('dev_id')
def query(dev_id):
    """Query device by ID."""
    click.echo(f"Querying device status {dev_id}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    click.echo(
        json.dumps(
            views.get_device_status(
                secret=secret,
                token=token,
                dev_id=dev_id,
                uow=bus.uow
            )
            , indent=2, ensure_ascii=False
        )
    )


@device.command()
@click.argument('command')
@click.argument('dev_id')
@click.option('--cmd_type', default='command', help="SwitchBot API commandType.")
@click.option('--cmd_param', default='default', help="SwitchBot API commandParameter.")
def cmd(command, dev_id, cmd_type, cmd_param):
    """Send a command to device."""
    click.echo(f"Sending command {command} to device {dev_id} with type:{cmd_type}, param:{cmd_param}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    _cmd = commands.SendDeviceCtrlCmd(
        secret=secret,
        token=token,
        dev_id=dev_id,
        cmd_type=cmd_type,
        cmd_value=command,
        cmd_param=cmd_param
    )
    bus.handle(_cmd)
    click.echo(f'Command sent')


# 'scene' 子命令集
@switchbotcli.group(help="Manage scenes.")
def scene():
    """Commands for scenes."""
    pass


@scene.command()
@click.option('--save', is_flag=True, help="Save scene list.")
def listall(save):
    """List all scenes."""
    click.echo(f"Listing all scenes. Save: {save}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    click.echo(
        json.dumps(
            views.get_scene_list(
                secret=secret,
                token=token,
                uow=bus.uow
            ), indent=2, ensure_ascii=False
        )
    )


@scene.command()
@click.argument('scene_id')
def start(scene_id):
    """Start a scene."""
    click.echo(f"Starting scene {scene_id}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    _cmd = commands.ExecManualScene(
        secret=secret,
        token=token,
        scene_id=scene_id
    )
    bus.handle(_cmd)
    click.echo(f'Command sent')


# 'webhook' 子命令集
@switchbotcli.group(help="Manage webhooks.")
def webhook():
    """Commands for webhooks."""
    pass


@webhook.command()
@click.argument('url')
def create(url):
    """Save user webhook config from SwitchBot Open API cloud ."""
    click.echo(f"Creating webhook {url}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    _cmd = commands.ConfigWebhook(
        secret=secret,
        token=token,
        url=url
    )
    bus.handle(_cmd)
    click.echo(f'Command sent')


@webhook.command()
def read():
    """Get user webhook config from SwitchBot Open API cloud."""
    click.echo(f"Getting webhook")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    click.echo(
        json.dumps(
            views.read_webhook_config(
                secret=secret,
                token=token,
                uow=bus.uow
            ), indent=2, ensure_ascii=False
        )
    )


@webhook.command()
@click.argument('url')
def read_detail(url):
    """Get user webhook config from SwitchBot Open API cloud."""
    click.echo(f"Getting webhook {url} detail")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    click.echo(
        json.dumps(
            views.read_webhook_config_detail(
                secret=secret,
                token=token,
                url=url,
                uow=bus.uow
            ), indent=2, ensure_ascii=False
        )
    )


@webhook.command()
@click.argument('url')
def update(url):
    """Update a webhook."""
    click.echo(f"Updating webhook {url}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    _cmd = commands.UpdateWebhook(
        secret=secret,
        token=token,
        url=url
    )
    bus.handle(_cmd)
    click.echo(f'Command sent')


@webhook.command()
@click.argument('url')
def delete(url):
    """Delete a webhook."""
    click.echo(f"Deleting webhook {url}")
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    _cmd = commands.DeleteWebhook(
        secret=secret,
        token=token,
        url=url
    )
    bus.handle(_cmd)
    click.echo(f'Command sent')


# 程序入口
if __name__ == '__main__':
    switchbotcli()
