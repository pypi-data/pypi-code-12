import psutil
import subprocess
import os
import re
from collections import namedtuple

partition = namedtuple('partition', ['device', 'label', 'mount', 'used', 'total', 'free', 'percent'])

def get_labels():
    prog = re.compile('(\/dev\/[a-z0-9]{3,}) on .+ \[(.+)\]')
    mounts = subprocess.check_output(['mount','-l']).decode('utf8')
    disks = {}
    for line in mounts.split('\n'):
        res = prog.match(line)
        if res is None:
            continue
        disks[res.group(1)] = res.group(2)
    return disks

def get_full_stat(labels):
    partitions = psutil.disk_partitions()

    data = []

    for part in partitions:
        if part.device not in labels:
            continue

        usage = psutil.disk_usage(part.mountpoint)

        data.append(partition(
            part.device,
            labels[part.device],
            part.mountpoint,
            usage.used,
            usage.total,
            usage.free,
            usage.percent,
        ))

    return data
