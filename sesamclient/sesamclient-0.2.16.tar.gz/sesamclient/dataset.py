# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import json
import logging

import ijson

from .entitybase import EntityBase
from .utils import validate_response_is_ok

logger = logging.getLogger(__name__)


class Dataset(EntityBase):
    """
    This class represents a dataset.
    """

    def __str__(self):
        result = super().__str__()
        return result

    def get_entities_as_stream(self, since=None, limit=None, start=0, history=True):
        """This returns a http stream for getting the entities of this dataset. (The returned object is a file-like
        stream from the 'requests' library, i.e response.raw)

        :param since: The opaque value that can be used to efficiently skip already seen entities.

        :param limit: The "limit" parameter specifies the maximum number of entities to return.
                      If this is not specified, all available entities are returned.

        :param start: The "start" parameter is a positive integer that specified how many entities to skip from the
                      start of where the "since"-parameters starts. This is far less efficient than using the
                      "since"-parameter, but it can be manually set in a gui to explore the dataset. NOTE: Clients
                      should use the "since"-parameter whenever possible.

        :param history: If this is true (the default) all entities, including replaced ones, will be returned. \
                        If this is false, only the latest version of the entities will be returned.

        """
        url = self._connection.get_dataset_entities_url(self.id)

        params = {}
        if since is not None:
            params["since"] = since
        if limit is not None:
            params["limit"] = limit
        if start is not None:
            params["start"] = start
        if history is not None:
            params["history"] = history

        # The entities are streamed from the server, so we have to enable streaming here.
        response = self._connection.do_get_request(url, stream=True, params=params)
        validate_response_is_ok(response)

        return response.raw

    def get_entities(self, since=None, limit=None, start=0, history=True):
        """This returns a generator for iterating over the entities of this dataset.

        :param since: The opaque value that can be used to efficiently skip already seen entities.

        :param limit: The "limit" parameter specifies the maximum number of entities to return.
                      If this is not specified, all available entities are returned.

        :param start: The "start" parameter is a positive integer that specified how many entities to skip from the
                      start of where the "since"-parameters starts. This is far less efficient than using the
                      "since"-parameter, but it can be manually set in a gui to explore the dataset. NOTE: Clients
                      should use the "since"-parameter whenever possible.

        :param history: If this is true (the default) all entities, including replaced ones, will be returned. \
                        If this is false, only the latest version of the entities will be returned.


        Note: If you just need the raw bytes, consider using the get_entities_as_stream() method instead. That will be
        faster.
        """
        entities_stream = self.get_entities_as_stream(since=since, limit=limit, start=start, history=history)

        # we use the ijson library to handle the streaming json reading. The call to ijson.items()
        # returns a generator object that can be used to iterate over the entities as they arrive
        # from the server.

        # TODO: The client should use the same json parser functions as the node. The node has some
        # propriatory ways of encoding types that isn't standard parts of json (for instance datetime
        # and Decimal). At some point, the node will need to be able to read a stream of
        # json entities with the special encoding, but it currently (27jan2015) can only read plain json, and doesn't
        # support reading json entities with the various "~" encodings. For now we leave the encoded values as-is.
        return ijson.items(entities_stream, 'item')

    def get_entity(self, entity_id):
        """Returns the specified entity.

        :param entity_id:
        """
        url = self._connection.get_dataset_entity_url(self.id, entity_id)
        response = self._connection.do_get_request(url)
        validate_response_is_ok(response)
        return json.loads(response.text)

    @property
    def num_entities_in_index(self):
        return self._raw_jsondata["runtime"]["index-estimate"]

    @property
    def num_entities_in_log(self):
        return self._raw_jsondata["runtime"]["log-estimate"]

    def run_dtl(self, dtl):
        """Runs the specified dtl on the dataset.

        :param dtl:
        :return: If all went well: a dict with a "sourceEntity" and a "resultEntity" value. If something went wrong a
                 dict with an "error" value (a string describing the error).
        """
        if not isinstance(dtl, str):
            dtl = json.dumps(dtl, indent=4)

        url = self._connection.get_dataset_url(self.id)

        response = self._connection.do_post_request(url, data={"operation": "run-dtl", "dtl": dtl})
        validate_response_is_ok(response)
        return json.loads(response.text)

    def delete(self):
        """Deletes this dataset from the sesam-node.
        """
        url = self._connection.get_dataset_url(self.id)
        response = self._connection.do_delete_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def get_metadata(self):
        """Gets the current metadata for this dataset"""
        url = self._connection.get_dataset_metadata_url(self.id)
        response = self._connection.do_get_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])
        metadata = json.loads(response.text)
        return metadata

    def set_metadata(self, metadata):
        """Replaces the metadata for this dataset with the specified dictionary"""
        url = self._connection.get_dataset_metadata_url(self.id)
        response = self._connection.do_put_request(url, json=metadata)
        validate_response_is_ok(response, allowable_response_status_codes=[200])

    def delete_metadata(self):
        """Deleted all metadata for this dataset"""
        url = self._connection.get_dataset_metadata_url(self.id)
        response = self._connection.do_delete_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])
