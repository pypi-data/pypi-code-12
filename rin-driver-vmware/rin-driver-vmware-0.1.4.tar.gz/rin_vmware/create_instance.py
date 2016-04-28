#!/usr/bin/env python3

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from optparse import OptionParser

import ssl
import sys,os
import json

from rin.config import Config
from rin.utils import Utils

DEFAULT_PATH = '/usr/local/etc/rin-vmware.yml'

def check_obj(si, vimtype):
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vimtype], True)
    for c in container.view:
        print("[check_obj] %s: %s" % (vimtype, c.name))

def get_obj(si, vimtype, name):
    obj = None
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vimtype], True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def vmware_auth(config):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    return SmartConnect(host       = config['server'],
                        user       = config['userid'],
                        pwd        = config['passwd'],
                        sslContext = context)

def vmware_iscsi_controller(si, vmname):
    vmobj = get_obj(si, vim.VirtualMachine, vmname)
    for dev in vmobj.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualSCSIController):
            return dev

def vmware_new_unit_number(si, vmname):
    unit_number = None

    vmobj = get_obj(si, vim.VirtualMachine, vmname)
    for dev in vmobj.config.hardware.device:
        if hasattr(dev.backing, 'fileName'):
            unit_number = int(dev.unitNumber) + 1
            # unit_number 7 reserved for scsi controller
            if unit_number == 7:
                unit_number += 1

    return unit_number

def vmware_get_nic(si, options):
    nic = vim.vm.device.VirtualDeviceSpec()
    nic.operation                               = vim.vm.device.VirtualDeviceSpec.Operation.add
    nic.device                                  = vim.vm.device.VirtualVmxnet3()
    nic.device.wakeOnLanEnabled                 = True
    nic.device.addressType                      = "assigned"
    nic.device.key                              = options.network_device_key
    nic.device.deviceInfo                       = vim.Description()
    nic.device.deviceInfo.label                 = options.network_label
    nic.device.deviceInfo.summary               = options.network_device
    nic.device.backing                          = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    nic.device.backing.network                  = get_obj(si, vim.Network, options.network_device)
    nic.device.backing.deviceName               = options.network_device
    nic.device.backing.useAutoDetect            = False
    nic.device.connectable                      = vim.vm.device.VirtualDevice.ConnectInfo()
    nic.device.connectable.startConnected       = True
    nic.device.connectable.allowGuestControl    = True

    return nic

def vmware_get_storage(si, options):
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    disk_spec.fileOperation = "create"
    disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    disk_spec.device = vim.vm.device.VirtualDisk()
    disk_spec.device.capacityInKB = options.ssize * 1024 * 1024
    disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    disk_spec.device.backing.diskMode = 'persistent'
    disk_spec.device.unitNumber = vmware_new_unit_number(si, options.original)

    controller = vmware_iscsi_controller(si, options.original)
    if controller != None:
        disk_spec.device.controllerKey = controller.key

    return disk_spec

def create_vm(config, options):
    if not "config" in config:
        return None

    si = vmware_auth(config)
    if not si:
         sys.exit(1)

    template_vm = get_obj(si, vim.VirtualMachine, options.original)
    for dev in template_vm.config.hardware.device:
        if hasattr(dev.backing, 'fileName'):
            unit_number = int(dev.unitNumber) + 1
            # unit_number 7 reserved for scsi controller
            if unit_number == 7:
                unit_number += 1
                if unit_number >= 16:
                    print("[TEST] we don't support this many disks")
                    return
        if isinstance(dev, vim.vm.device.VirtualSCSIController):
            controller = dev

    # add nic information
    devices = []
    devices.append(vmware_get_nic(si, options))
    devices.append(vmware_get_storage(si, options))

    # declare VM spec
    vmconf = vim.vm.ConfigSpec(
            deviceChange    = devices,
            numCPUs         = options.vcpu,
            memoryMB        = options.mem,
            guestId         = options.guest_type)

    # config AdapterMapping, Specfication
    inputs = {
            'vm_name'   : options.name,
            'vm_ip'     : options.ipaddr,
            'subnet'    : config['config']['netmask'],
            'gateway'   : config['config']['gateway'],
            'dns'       : config['config']['dns'],
            'domain'    : config['config']['domain'] }

    adaptermap = vim.vm.customization.AdapterMapping()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    
    # Static IP Configuration
    adaptermap.adapter.dnsDomain = inputs['domain']
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = inputs['vm_ip']
    adaptermap.adapter.subnetMask = inputs['subnet']
    adaptermap.adapter.gateway = inputs['gateway']  

    globalip = vim.vm.customization.GlobalIPSettings()
    globalip.dnsServerList = inputs['dns']

    #For Linux . For windows follow sysprep
    ident = vim.vm.customization.LinuxPrep(
            domain=inputs['domain'],
            hostName=vim.vm.customization.FixedName(name=inputs['vm_name']))
    customspec = vim.vm.customization.Specification()

    #For only one adapter
    customspec.identity = ident
    customspec.nicSettingMap = [adaptermap]
    customspec.globalIPSettings = globalip

    # Creating relocate spec and clone spec
    relocateSpec = vim.vm.RelocateSpec()

    relocateSpec.host = get_obj(si, vim.HostSystem, options.host)
    if("datastore" in config['config']):
        relocateSpec.datastore = get_obj(si, vim.Datastore, config['config']['datastore'])

    cloneSpec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocateSpec, customization=customspec, config=vmconf)

    template_vm = get_obj(si, vim.VirtualMachine, options.original)
    clone = template_vm.Clone(name=options.name, folder=template_vm.parent, spec=cloneSpec)

    print('{"status":"OK"}')

    Disconnect(si)

def validate_options(options, parser):
    warn = None
    # validate cli options
    if options.name == None:
        warn = "[notification] 'name' option is mandatory"
    if options.ipaddr == None:
        warn = "[notification] 'ipaddr' option is mandatory"
    if options.host == None:
        warn = "[notification] 'host' option is mandatory"
    if options.original == None:
        warn = "[notification] 'original' option is mandatory"
    if options.vcenter == None:
        warn = "[notification] 'vcenter' option is mandatory"

    if warn != None:
        parser.print_help()
        print("")
        sys.exit(warn)

def get_options():
    parser = OptionParser()

    parser.add_option("-n", "--name", type=str, dest="name", help="VM name to create (mandatory)")
    parser.add_option("-v", "--vcenter", type=str, dest="vcenter", help="vCenter address to create new VM(mandatory)")
    parser.add_option("-a", "--ipaddr", type=str, dest="ipaddr", help="ipaddress assigned (mandatory)")
    parser.add_option("-t", "--host", type=str, dest="host", help="hostname which contains target VM (mandatory)")
    parser.add_option("-o", "--original", type=str, dest="original", help="original VM name to be cloned (mandatory)")
    parser.add_option("-g", "--guest_type", type=str, dest="guest_type", help="Guest types of new VM", default="otherGuest")
    parser.add_option("-d", "--datastore", type=str, dest="datastore", help="Datasotre to store")
    parser.add_option("-s", "--storage_size", type=int, dest="ssize", help="Storage size to attach VM [GB]", default=0)
    parser.add_option("-c", "--vcpu", type=int, dest="vcpu", help="Number of vCPU which VM has", default=1)
    parser.add_option("-m", "--mem", type=int, dest="mem", help="Memory size of VM", default=512)
    parser.add_option("-l", "--network_label", type=str, dest="network_label", help="Label of Network Adapter", default="Network Adapter 0")
    parser.add_option("-e", "--network_device", type=str, dest="network_device", help="Network device name", default="VM Network")
    parser.add_option("-k", "--networkkey", type=int, dest="network_device_key", help="Network device key", default=4000)

    (options, _) = parser.parse_args()

    validate_options(options, parser)

    return options

def main():
    path = DEFAULT_PATH
    if 'RIN_CONFIG' in os.environ:
        path = os.environ['RIN_CONFIG']

    conf = Config.load(path)
    options = get_options()

    [create_vm(x, options) for x in conf['vmware'] if x['server'] == options.vcenter]

# Start program
if __name__ == "__main__":
    main()
