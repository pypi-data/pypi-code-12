# -*- coding: utf-8 -*-
import logging
from foxha.connection import Connection
from foxha import inner_logic

LOG = logging.getLogger(__name__)


class FoxHAProvider(object):
    def __init__(self, dbaas_api):
        self.dbaas_api = dbaas_api
        self.fox_connection = Connection(
            dbaas_api.endpoint, dbaas_api.port, dbaas_api.database_name,
            dbaas_api.user, dbaas_api.password, dbaas_api.cipher
        )

    def get_group_info(self, group_name):
        LOG.info("Get group data for: {}".format(group_name))
        return inner_logic.get_group(group_name, self.fox_connection)

    def failover(self, group_name):
        LOG.info("Doing failover to: {}".format(group_name))
        return inner_logic.failover(group_name, self.fox_connection)

    def switchover(self, group_name):
        LOG.info("Doing switchover to: {}".format(group_name))
        return inner_logic.switchover(group_name, self.fox_connection)

    def set_master(self, group_name, node_ip):
        if self.get_group_info(group_name).master.ip != node_ip:
            self.switchover(group_name)

    def start(self, group_name):
        LOG.info("Start group: {}".format(group_name))
        return inner_logic.start(group_name, self.fox_connection)

    def add_group(
            self, group_name, description, vip_address,
            mysql_user, mysql_password, repl_user, repl_password
    ):
        LOG.info("Adding group: {}".format(group_name))
        return inner_logic.add_group(
            self.fox_connection, group_name, description, vip_address,
            mysql_user, mysql_password, repl_user, repl_password
        )

    def delete_group(self, group_name):
        LOG.info("Deleting group: {}".format(group_name))
        return inner_logic.delete_group(self.fox_connection, group_name)

    def add_node(self, group_name, name, node_ip, port, mode, status):
        LOG.info("Adding node: {} | {}".format(group_name, node_ip))
        return inner_logic.add_node(
            self.fox_connection, group_name, node_ip, port, mode, status
        )

    def delete_node(self, group_name, node_ip):
        LOG.info("Deleting node: {} | {}".format(group_name, node_ip))
        return inner_logic.delete_node(
            self.fox_connection, group_name, node_ip
        )
