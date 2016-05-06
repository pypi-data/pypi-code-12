import logging
from .base_client import BaseNSXClient
log = logging.getLogger(__name__)


class NSXClient(BaseNSXClient):
    def list_security_groups(self):
        groups = self._get_security_groups()
        return groups['list']['securitygroup']

    def add_member_to_security_group(self, security_group, member):
        return self._add_member(security_group, member)
