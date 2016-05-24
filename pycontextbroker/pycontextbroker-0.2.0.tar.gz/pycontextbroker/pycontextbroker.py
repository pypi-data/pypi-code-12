import logging
import requests
from pycontextbroker.cb_attribute import ContextBrokerAttribute
from pycontextbroker.cb_entity import ContextBrokerEntity
from pycontextbroker.cb_subscription import ContextBrokerSubscription

logger = logging.getLogger(__name__)


class ContextBrokerClient(object):

    def __init__(self, ip, port):
        self.cb_address = 'http://{}:{}'.format(ip, port)
        self.entity = ContextBrokerEntity(self.cb_address)
        self.attribute = ContextBrokerAttribute(self.cb_address)
        self.subscription = ContextBrokerSubscription(self.cb_address)

        try:
            requests.get(self.cb_address)
        except:
            logger.exception(
                "Failed to initialize ContextBroker client: "
                "connection refused, please check provided IP and PORT"
            )

    # Context Broker
    def get_version_data(self):
        return requests.get(self.cb_address + '/version').json()

    def get_orion_version_data(self):
        orion_data = self.get_version_data().get('orion')
        if not orion_data:
            logger.exception("Failed to gather Orion Context Broker version data")
        return orion_data

    def get_version(self):
        return self.get_orion_version_data().get('version')

    def get_uptime(self):
        return self.get_orion_version_data().get('uptime')
