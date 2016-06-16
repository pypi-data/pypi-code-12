
"""

"""

from tingyun.armoury.ammunition.memcache_tracker import wrap_memcache_trace

# option: {object_path: $object_path, command: $command}
memcache_attr = {
    "add": {"path": "Client.add", "command": "add"},
    "append": {"path": "Client.append", "command": "append"},
    "cas": {"path": "Client.cas", "command": "cas"},
    "decr": {"path": "Client.decr", "command": "decr"},
    "delete": {"path": "Client.delete", "command": "delete"},
    "delete_multi": {"path": "Client.delete_multi", "command": "delete"},
    "get": {"path": "Client.get", "command": "get"},
    "gets": {"path": "Client.gets", "command": "get"},
    "get_multi": {"path": "Client.get_multi", "command": "get"},
    "incr": {"path": "Client.incr", "command": "incr"},
    "prepend": {"path": "Client.prepend", "command": "prepend"},
    "replace": {"path": "Client.replace", "command": "replace"},
    "set": {"path": "Client.set", "command": "set"},
    "set_multi": {"path": "Client.set_multi", "command": "set"},
}


def detect(module):
    for attr in memcache_attr:
        if hasattr(module.Client, attr):
            wrap_memcache_trace(module, memcache_attr[attr]['path'], memcache_attr[attr]['command'])
