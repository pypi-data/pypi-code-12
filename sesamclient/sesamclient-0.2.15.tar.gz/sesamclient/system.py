# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import logging
import copy

from .entitybase import EntityBase
from . import utils


logger = logging.getLogger(__name__)


class System(EntityBase):
    """
    This class represents a system.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete(self):
        """Deletes this system from the sesam-node.
        """
        url = self._connection.get_system_url(self.id)
        response = self._connection.do_delete_request(url)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def modify(self, system_config):
        """Modifies the system with the specified configuration."""
        system_config = copy.deepcopy(system_config)
        system_config["_id"] = self.id
        response = self._connection.do_put_request(self._connection.get_system_config_url(self.id), json=system_config)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)
