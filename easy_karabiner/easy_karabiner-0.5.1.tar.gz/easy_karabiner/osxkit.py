# coding: utf-8
from __future__ import print_function
import os
import subprocess
from . import util
from .fucking_string import ensure_utf8

__all__ = ['get_app_info', 'get_all_app_info',
           'get_peripheral_info', 'get_all_peripheral_info']


def call(cmd, **kwargs):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, **kwargs)
    output = proc.stdout.read().decode('utf-8')
    return output


def contains_any_keywords(s, *keywords):
    words = set(w.lower() for w in s.split())
    keywords = set(w.lower() for w in keywords)
    return not words.isdisjoint(keywords)


def get_name_without_suffix(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_all_app_info():
    """Return dict contains applications information. Item in the dict has format like:

        'basename / display_name' : (absolute_path, bundle_identifier)

    NOTICE: `basename` or `display_name` already removed '.app' suffix
    """
    # list absolute path of all applications
    LIST_APP_PATH_CMD = ('mdfind', '-0', 'kMDItemContentType==com.apple.application-bundle')
    # get Bundle-Identifier and Display-Name of applications by absolute path
    LIST_APP_INFO_CMD = ('mdls', '-raw',
                         '-name', 'kMDItemCFBundleIdentifier',
                         '-name', 'kMDItemDisplayName')

    raw_paths = call(LIST_APP_PATH_CMD).split('\x00')
    app_paths = [p for p in raw_paths if p.strip()]

    raw_infos = call(LIST_APP_INFO_CMD + tuple(app_paths))
    info_lines = raw_infos.split('\x00')

    app_ids = info_lines[0::2]
    app_infos = tuple(zip(app_paths, app_ids))
    # display name not always equal to basename,
    # because system language and application name maybe not English
    display_names = tuple(info_lines[1::2])
    basenames = tuple(get_name_without_suffix(p) for p in app_paths)

    name_map = tuple(zip(display_names + basenames, app_infos + app_infos))
    return dict(name_map)


def get_app_info(name):
    if not hasattr(get_app_info, 'infos'):
        get_app_info.infos = get_all_app_info()

    if name.endswith('.app'):
        name = name[:-4]
    name = ensure_utf8(name)
    return get_app_info.infos.get(name)


def lines2tree(lines):
    def do_lines2tree(root, lines, i=0, level=-1):
        while i < len(lines):
            line = lines[i]
            indent_level = len(line) - len(line.lstrip())

            if indent_level > level:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()

                if line.endswith(':'):
                    root[key] = {}
                    i = do_lines2tree(root[key], lines, i + 1, indent_level)
                else:
                    root[key] = val
                    i += 1
            else:
                break
        return i

    tree = {}
    do_lines2tree(tree, lines)
    return tree


def get_devices(item, conditions):
    devices = {}
    for k in item:
        if isinstance(item[k], dict) and any(fn(k) for fn in conditions):
            devices[k] = item[k]
    return devices


def get_display_name(key, brand, product_id):
    id_num = product_id[-4:]

    if key == 'Apple Internal Keyboard / Trackpad':
        name = 'built-in keyboard and trackpad'
    elif contains_any_keywords(key, 'Device'):
        name = '%s_%s' % (brand, id_num)
    else:
        name = '%s_%s' % (key, id_num)

    return util.escape_string(name)


def get_all_peripheral_info():
    """Return dict contains devices information. Item in the dict has format like:

        'display_name' : (vendor_id, product_id)
    """
    # list information about USB and Bluetooth devices
    CMD = ('system_profiler', '-detailLevel', 'mini', '-timeout', '1',
           'SPUSBDataType', 'SPBluetoothDataType')

    output = call(CMD)
    lines = [line for line in output.split('\n') if line.strip()]
    info_tree = lines2tree(lines)

    # Bluetooth Devices
    item = [v for k, v in info_tree['Bluetooth'].items() if k.startswith('Devices')][0]
    conditions = [
        lambda k: k == 'Apple Internal Keyboard / Trackpad',
        lambda k: item[k].get('Major Type') == 'Peripheral',
    ]
    devices = get_devices(item, conditions)

    # USB Devices
    for item in info_tree['USB'].values():
        conditions = [
            lambda k: contains_any_keywords(k, 'Keyboard', 'Trackpad', 'Mouse'),
            lambda k: item[k].get('Built-In') != 'Yes',
        ]
        devices.update(get_devices(item, conditions))

    # only keep (Vendor ID, Product ID) properties
    for k in sorted(devices.keys()):
        device = devices.pop(k)
        if 'Product ID' in device and 'Vendor ID' in device:
            product_id = device['Product ID']
            vendor_parts = device['Vendor ID'].split(' ', 1)
            vendor_id = vendor_parts[0]
            brand = device.get('Manufacturer', vendor_parts[-1].strip()[1:-1])
            # construct display name from properties
            name = ensure_utf8(get_display_name(k, brand, product_id))

            devices[name] = (vendor_id, product_id)

    return devices


def get_peripheral_info(name):
    if not hasattr(get_peripheral_info, 'infos'):
        get_peripheral_info.infos = get_all_peripheral_info()

    name = ensure_utf8(name)
    return get_peripheral_info.infos.get(name)


# used for test purpose
if __name__ == '__main__':
    app_names = ['Finder', 'Xee³',
                 '虾米音乐', '坚果云', '地图',
                 'xiami', 'Nutstore', 'Maps']

    peripheral_names = ['“fz”的键盘_0255', 'Lenovo_USB_Optical_Mouse_6019',
                        'built_in_keyboard_and_trackpad', 'CHERRY_GmbH_0011']

    print(' Application Info '.center(80, '-'))
    for app_name in app_names:
        print('%s    \t%s' % (app_name, get_app_info(app_name)))

    print(' Peripheral Info '.center(80, '-'))
    for peripheral_name in peripheral_names:
        print('%-42s\t%s' % (peripheral_name, get_peripheral_info(peripheral_name)))
