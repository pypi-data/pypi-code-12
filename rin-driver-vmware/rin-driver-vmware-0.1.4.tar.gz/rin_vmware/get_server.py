#!/usr/bin/env python3

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import ssl
import json
import sys,os

from rin.config import Config
from rin.utils import Utils

DEFAULT_PATH = '/usr/local/etc/rin-vmware.yml'

def get_obj(si, vimtype, name):
    obj = None
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vimtype], True)

    # Note: Why not to use list-comprehension
    # - This processing is faster than list-comprehension because this implementation
    #   interrupts the loop when target object is found. In this processing, the time
    #   to this methods is reduced in half on average.
    for c in container.view:
        if c.name == name:
            return c

def get_host(si, vm):
    obj = None
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)

    # The reason why this doesn't use list-comprehension is the same of 'get_obj' method.
    for c in container.view:
        if vm in c.vm:
            return c

def get_vminfo(target, config):
    if not target:
        sys.exit(1)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    si = SmartConnect(host          = config['server'],
                      user          = config['userid'],
                      pwd           = config['passwd'],
                      sslContext    = context)
    if not si:
        sys.exit(1)

    vm = get_obj(si, vim.VirtualMachine, target)
    if vm != None:
        ipaddrs = []
        for nic in vm.guest.net:
            ipaddrs += [x for x in nic.ipAddress if Utils.validate_ipv4(x)]
    
        boottime = ''
        if vm.runtime.bootTime:
            # The reason of this check is that suspended VM doesn't have bootTime parameter
            boottime = vm.runtime.bootTime.strftime('%Y-%m-%d %H:%M:%S')

        return {
          'name'      : vm.name,
          'location'  : get_host(si, vm).name,
          'address'   : ipaddrs,
          'status'    : vm.runtime.powerState,
          'type'      : 'Virtual',
          'manager'   : 'VMware',
          'boottime'  : boottime,
          'cores'     : vm.summary.config.numCpu,
          'RAM'       : vm.summary.config.memorySizeMB,
          'OS'        : vm.summary.config.guestId,
          'Alarm'     : vm.summary.overallStatus,
        }

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    path = DEFAULT_PATH
    if 'RIN_CONFIG' in os.environ:
        path = os.environ['RIN_CONFIG']

    conf = Config.load(path)
    if conf == None:
        sys.exit(1)

    vminfo = [get_vminfo(sys.argv[1], x) for x in conf['vmware']]
    if vminfo != []:
        print(json.dumps(vminfo))

if __name__ == "__main__":
    main()
