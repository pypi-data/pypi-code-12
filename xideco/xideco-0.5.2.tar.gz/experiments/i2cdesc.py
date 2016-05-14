desc = {
    "adxl345": {
        "device_address": 83,
        "commands": {
            "init": [
                {
                    u"cmd": u"init",
                    u"device_address": 83
                },
                {
                    u"cmd": u"write_byte",
                    u"device_address": 83,
                    u"register": 45,
                    u"value": 0
                }, {
                    u"cmd": u"write_byte",
                    u"device_address": 83,
                    u"register": 45,
                    u"value": 8
                }, {
                    u"cmd": u"write_byte",
                    u"device_address": 83,
                    u"register": 49,
                    u"value": 8
                }, {
                    u"cmd": u"write_byte",
                    u"device_address": 83,
                    u"register": 49,
                    u"value": 3
                }],
            "read": [{
                "cmd": "read_block",
                "device_address": 83,
                "register": 50,
                "num_bytes": 6
            }]
        }
    },
    "tmp102": {
        "device_address": 72,
        "commands": {
            "read": [{
                "cmd": "read_block",
                "device_address": 72,
                "register": 50,
                "num_bytes": 2
            }]
        }
    }
}

instructions = desc["adxl345"]["commands"]["init"]
for x in instructions:
    print(x)