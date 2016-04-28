#!/usr/bin/env python3

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from rin.config import Config
from rin.utils import Utils

import sys,os
import ssl
import json

DEFAULT_PATH = '/usr/local/etc/rin-vmware.yml'

def get_vminfo(host, vm):
    ipaddrs = []
    for nic in vm.guest.net:
        ipaddrs += [x for x in nic.ipAddress if Utils.validate_ipv4(x)]

    boottime = ''
    if vm.runtime.bootTime:
        # The reason of this check is that suspended VM doesn't have bootTime parameter
        boottime = vm.runtime.bootTime.strftime('%Y-%m-%d %H:%M:%S')

    return {
        'name'      : vm.name,
        'location'  : host.name,
        'address'   : ipaddrs,
        'status'    : vm.runtime.powerState,
        'type'      : 'Virtual',
        'manager'   : 'VMware',
        'boottime'  : boottime,
    }

def get_vmsinfo(opts):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    si = SmartConnect(host          = opts['server'],
                      user          = opts['userid'],
                      pwd           = opts['passwd'],
                      sslContext    = context)
    if not si:
         sys.exit(1)

    machines = []
    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            for dc in child.hostFolder.childEntity:
                for host in dc.host:
                    machines += [get_vminfo(host, x) for x in host.vm]

    return machines

def main():
    vms = []

    path = DEFAULT_PATH
    if 'RIN_CONFIG' in os.environ:
        path = os.environ['RIN_CONFIG']

    conf = Config.load(path)
    if conf == None:
        sys.exit(1)

    for manager_info in conf['vmware']:
        vms += get_vmsinfo(manager_info)

    print(json.dumps(vms))

if __name__ == "__main__":
    main()
