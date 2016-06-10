# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import copy
import json
import logging

import ijson

from .entitybase import EntityBase
from .pump import Pump
from . import utils

logger = logging.getLogger(__name__)


class Pipe(EntityBase):
    """
    This class represents a pipe.
    """

    def __str__(self):
        result = super().__str__()
        # TODO: add info about task, provider and sink.
        return result

    def get_pump(self):
        url = self._connection.get_pipe_pump_url(self.id)
        response = self._connection.do_get_request(url)
        pump_json = json.loads(response.text)
        return Pump(self.id, self._connection, pump_json)

    @property
    def source_dataset_id(self):
        """Returns the id of the dataset that this pipe reads data from, or None if the pipe doesn't
        read data from a dataset."""
        effective_config = self._raw_jsondata["config"]["effective"]
        producer_config = effective_config.get("source")
        if producer_config is None:
            return None

        return producer_config.get("dataset")

    @property
    def sink_dataset_id(self):
        """Returns the id of the dataset that this pipe feeds data to, or None if the pipe doesn't
        feed data to a dataset."""
        effective_config = self._raw_jsondata["config"]["effective"]
        sink_config = effective_config.get("sink")
        if sink_config is None:
            return None

        return sink_config.get("dataset")

    @property
    def execution_dataset_id(self):
        """Returns the id of the dataset that this pipe logs to, or None if the pipe doesn't
        log to a dataset (this is the case for the pipes of the old sdshare server and client)."""
        runtime = self._raw_jsondata["runtime"]
        return runtime.get("execution-dataset")

    def get_entities(self, since=None, limit=None):
        """This returns a generator for iterating over the entities of the source of this pipe.
        :param since:
        :param limit: The maximum number of entities to return. A value of None means return all the entities.
        """
        url = self._connection.get_pipe_entities_url(self.id)

        params = {}
        if since is not None:
            params["since"] = since
        if limit is not None:
            params["limit"] = limit

        # The entities are streamed from the server, so we have to enable streaming here.
        response = self._connection.do_get_request(url, stream=True, params=params)
        utils.validate_response_is_ok(response)

        # we use the ijson library to handle the streaming json reading. The call to ijson.items()
        # returns a generator object that can be used to iterate over the entities as they arrive
        # from the server.
        return ijson.items(response.raw, 'item')

    def delete(self):
        """Deletes this pipe from the sesam-node.
        """
        url = self._connection.get_pipe_url(self.id)
        response = self._connection.do_delete_request(url)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def modify(self, pipe_config):
        """Modifies the pipe with the specified configuration."""
        pipe_config = copy.deepcopy(pipe_config)
        pipe_config["_id"] = self.id
        response = self._connection.do_put_request(self._connection.get_pipe_config_url(self.id), json=pipe_config)
        utils.validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)
