from switchbot import gh_intent


def test_execute_intent():
    request = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "inputs": [
            {
                "intent": "action.devices.EXECUTE",
                "payload": {
                    "commands": [
                        {
                            "devices": [
                                {
                                    "id": "123",
                                    "customData": {
                                        "fooValue": 74,
                                        "barValue": True,
                                        "bazValue": "sheepdip"
                                    }
                                },
                                {
                                    "id": "456",
                                    "customData": {
                                        "fooValue": 36,
                                        "barValue": False,
                                        "bazValue": "moarsheep"
                                    }
                                }
                            ],
                            "execution": [
                                {
                                    "command": "action.devices.commands.OnOff",
                                    "params": {
                                        "on": True
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    # assert ExecuteRequestSchema().load(data)
    obj = gh_intent.ExecuteRequest.load(request)
    assert isinstance(obj, gh_intent.ExecuteRequest)
    assert obj.dump() == request

    response = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "payload": {
            "commands": [
                {
                    "ids": [
                        "123"
                    ],
                    "status": "SUCCESS",
                    "states": {
                        "on": True,
                        "online": True
                    }
                },
                {
                    "ids": [
                        "456"
                    ],
                    "status": "ERROR",
                    "errorCode": "deviceTurnedOff"
                }
            ]
        }
    }
    obj = gh_intent.ExecuteResponse.load(response)
    assert isinstance(obj, gh_intent.ExecuteResponse)
    assert obj.dump() == response


def test_query_intent():
    request = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "inputs": [
            {
                "intent": "action.devices.QUERY",
                "payload": {
                    "devices": [
                        {
                            "id": "123",
                            "customData": {
                                "fooValue": 74,
                                "barValue": True,
                                "bazValue": "foo"
                            }
                        },
                        {
                            "id": "456",
                            "customData": {
                                "fooValue": 12,
                                "barValue": False,
                                "bazValue": "bar"
                            }
                        }
                    ]
                }
            }
        ]
    }
    obj = gh_intent.QueryRequest.load(request)
    assert isinstance(obj, gh_intent.QueryRequest)
    assert obj.dump() == request

    response = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "payload": {
            "devices": {
                "123": {
                    "on": True,
                    "online": True,
                    "status": "SUCCESS"
                },
                "456": {
                    "on": True,
                    "online": True,
                    "status": "SUCCESS",
                    "brightness": 80,
                    "color": {
                        "spectrumRgb": 16711935
                    }
                }
            }
        }
    }
    obj = gh_intent.QueryResponse.load(response)
    assert isinstance(obj, gh_intent.QueryResponse)
    assert obj.dump() == response


def test_sync_intent():
    request = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "inputs": [
            {
                "intent": "action.devices.SYNC"
            }
        ]
    }
    obj = gh_intent.SyncRequest.load(request)
    assert isinstance(obj, gh_intent.SyncRequest)
    assert obj.dump() == request

    response = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "payload": {
            "agentUserId": "1836.15267389",
            "devices": [
                {
                    "id": "123",
                    "type": "action.devices.types.OUTLET",
                    "traits": [
                        "action.devices.traits.OnOff"
                    ],
                    "name": {
                        "defaultNames": [
                            "My Outlet 1234"
                        ],
                        "name": "Night light",
                        "nicknames": [
                            "wall plug"
                        ]
                    },
                    "willReportState": False,
                    "roomHint": "kitchen",
                    "deviceInfo": {
                        "manufacturer": "lights-out-inc",
                        "model": "hs1234",
                        "hwVersion": "3.2",
                        "swVersion": "11.4"
                    },
                    "otherDeviceIds": [
                        {
                            "deviceId": "local-device-id"
                        }
                    ],
                    "customData": {
                        "fooValue": 74,
                        "barValue": False,
                        "bazValue": "foo"
                    }
                },
                {
                    "id": "456",
                    "type": "action.devices.types.LIGHT",
                    "traits": [
                        "action.devices.traits.OnOff",
                        "action.devices.traits.Brightness",
                        "action.devices.traits.ColorSetting"
                    ],
                    "name": {
                        "defaultNames": [
                            "lights out inc. bulb A19 color hyperglow"
                        ],
                        "name": "lamp1",
                        "nicknames": [
                            "reading lamp"
                        ]
                    },
                    "willReportState": False,
                    "roomHint": "office",
                    "attributes": {
                        "colorModel": "rgb",
                        "colorTemperatureRange": {
                            "temperatureMinK": 2000,
                            "temperatureMaxK": 9000
                        },
                        "commandOnlyColorSetting": False
                    },
                    "deviceInfo": {
                        "manufacturer": "lights out inc.",
                        "model": "hg11",
                        "hwVersion": "1.2",
                        "swVersion": "5.4"
                    },
                    "customData": {
                        "fooValue": 12,
                        "barValue": False,
                        "bazValue": "bar"
                    }
                }
            ]
        }
    }
    obj = gh_intent.SyncResponse.load(response)
    assert isinstance(obj, gh_intent.SyncResponse)
    assert obj.dump() == response
