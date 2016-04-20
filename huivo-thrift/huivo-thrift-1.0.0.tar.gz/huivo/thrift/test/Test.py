__author__ = 'sunquan'

from huivo.thrift.client.Client import Client
from huivo.thrift.client.Configurator import Configurator
from huivo.thrift.client.Configurator import ServiceSetting
from huivo.thrift.client.ClientFactory import ClientFactory


import TestService, time

#client = Client("t02:2181", "/thrift-test/", "huivo.thrift.test.TestService$Iface", TestService.Iface, TestService.Client)

configurator = Configurator()
configurator.zookeeper_address = "t02:2181,t03:2181,t04:2181"
configurator.zookeeper_root_path = "/thrift-test/"
configurator.add_setting(ServiceSetting(TestService.Iface, TestService.Client, "huivo.thrift.test.TestService$Iface"))

clientFactory = ClientFactory()
client = clientFactory.get_client(TestService.Iface)

while True:
    try:
        print client.hello("sun quan")
    except Exception as e:
        print e
        pass
    time.sleep(1)