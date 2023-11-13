from switchbot.adapters import repository, file_datastore
from switchbot.domain import model


class TestJsonFileDatastore:
    def test_get_by_dev_id(self):
        session = file_datastore.FileDatastore(file='.datastore')
        repo = repository.JsonFileRepository(session=session)
        d = model.SwitchBotDevice(
            device_id='did-1',
            device_name='dev_name',
            device_type='devType',
            enable_cloud_service=True,
            hub_device_id='hubDeviceId'
        )
        s = model.SwitchBotStatus(
            device_id='did-1',
            device_type='devType',
            hub_device_id='hubDeviceId'
        )
        c = model.SwitchBotChangeReport(
            event_type='eventType',
            event_version='eventVersion',
            context={
                "deviceType": "WoPlugUS",
                "deviceMac": "did-1",
                "powerState": "ON",
                "timeOfSample": 1698720698088
            }
        )
        u = model.SwitchBotUserRepo(
            uid='uid', secret='secret', token='token',
            devices=[d], changes=[c], states=[s], scenes=[], webhooks=[]
        )
        repo.add(u)
        assert repo.get_by_secret('secret') == u
        assert repo.get_by_uid('uid') == u
        assert repo.get_by_dev_id('did-1') == u
        assert u.get_dev_last_change_report(dev_id='did-1') == c
        assert u.get_dev_state(dev_id='did-1') == s
