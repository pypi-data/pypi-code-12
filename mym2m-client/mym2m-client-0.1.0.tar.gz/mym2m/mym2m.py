#!/usr/bin/env python

import requests
from requests import RequestException
import json
from . import exceptions

DEMO_DATA_URL = 'http://api.demo.360telemetry.com/api/v1/service/json'


class API:
    """
    Handles the dispatch of snapshots to the server.
    """

    def __init__(self, device_key, unit_identifier, service_url=DEMO_DATA_URL):
        """
        Create a new instance.
        :param device_key:
        :param unit_identifier:
        :param service_url:
        :return:
        """
        self.device_key = device_key
        self.unit_identifier = unit_identifier
        self.service_url = service_url
        self.snapshots = []

    def add(self, new_snapshot):
        """
        Add a snapshot, ready for dispatch.
        :param new_snapshot:
        :return:
        """
        self.snapshots.append(new_snapshot)

    def dispatch(self):
        """
        Dispatch currently-stored snapshots to the server.
        :raises ApiException:
        :return:
        """

        response = None

        try:
            response = requests.post(
                self.service_url,
                data=self.__build_json(),
                headers={'X-Api-Key': self.device_key}
            )

            # Did we receive any configuration?
            return response.json()

        except ValueError as exception:
            # Problems deserialising the JSON response
            if response:
                raise exceptions.ApiException(exception.message)
            else:
                raise exceptions.ApiException(response.text)
        except RequestException as exception:
            # Problems communicating with the server
            raise exceptions.ApiException(exception.message[0])

    def __build_json(self):
        """
        Build a JSON string from the current state of this client
        :return:
        """
        return json.dumps(
            {
                "data": {
                    self.unit_identifier: map(lambda snapshot: snapshot.get_api_data(), self.snapshots)
                }
            }
        )
