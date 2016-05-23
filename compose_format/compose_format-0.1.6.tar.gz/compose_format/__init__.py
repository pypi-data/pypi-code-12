#!/usr/bin/env python3
from collections import OrderedDict
import pyaml
from yaml import load


class ComposeFormat:
    TOPLEVEL_ORDER = ['version', 'services', 'volumes', 'networks']
    SERVICE_ORDER = [
        'image', 'command', 'entrypoint', 'container_name',
        'links', 'volumes_from', 'volumes', 'volume_driver', 'tmpfs',
        'build',
        'expose', 'ports',
        'net', 'network_mode', 'networks',
        'labels',
        'devices',
        'read_only',
        'env_file', 'environment',
        'cpu_shares', 'cpu_quota', 'cpuset', 'domainname', 'hostname', 'ipc',
        'mac_address', 'mem_limit', 'memswap_limit', 'privileged',
        'depends_on', 'extends', 'external_links',
        'stdin_open', 'user', 'working_dir',
        'extra_hosts', 'restart', 'ulimits', 'tty', 'dns', 'dns_search', 'pid',
        'security_opt', 'cap_add', 'cap_drop', 'cgroup_parent', 'logging', 'log_driver', 'log_opt',
        'stopsignal',
    ]
    BUILD_ORDER = ['context', 'dockerfile', 'args']

    ORDERS = {
        'version': TOPLEVEL_ORDER,
        'image': SERVICE_ORDER,
        'dockerfile': BUILD_ORDER
    }

    def __init__(self):
        pass

    def format(self, path, replace=False, strict=True):
        with open(path, 'r') as file:
            data = file.read()
        original = data
        formatted = self.format_string(data, replace=replace, strict=strict)

        if replace:
            with open(path, 'w') as file:
                file.write(formatted)
        else:
            print(formatted)
        return original == formatted

    def format_string(self, data, replace=False, strict=True):
        data = self.reorder(load(data), strict=strict)

        def is_legacy_version(data):
            if 'version' not in data:
                return True
            return str(data['version']) != '2' and str(data['version']) != '\'2\''

        vspacing = [1, 0] if is_legacy_version(data) else [0, 1, 0]

        formatted = pyaml.dump(data, vspacing=vspacing, indent=2, width=120, string_val_style='plain')
        return formatted.strip() + '\n'

    @staticmethod
    def reorder(data, strict=True):
        if type(data) is dict or type(data) is OrderedDict:
            for key in ComposeFormat.ORDERS.keys():
                if key not in data.keys():
                    continue
                current_order = ComposeFormat.ORDERS[key]

                def order(item):
                    key, _ = item
                    if strict:
                        assert key in current_order, 'key: {0} not known'.format(key)

                    if key in current_order:
                        return current_order.index(key)
                    return len(current_order) + ComposeFormat.name_to_order(key)

                result = {key: ComposeFormat.reorder(value, strict=strict) for key, value in data.items()}
                result = OrderedDict(sorted(result.items(), key=order))

                return result
            return {key: ComposeFormat.reorder(value, strict=strict) for key, value in data.items()}
        if type(data) is list:
            return sorted([ComposeFormat.reorder(item, strict=strict) for item in data])
        if len(str(data)) >= 1 and str(data)[0].isdigit():
            return '\'{}\''.format(data)
        return data

    @staticmethod
    def name_to_order(value):
        from functools import reduce

        return reduce(lambda left, right: (left * 256 + right), (ord(char) for char in value))
