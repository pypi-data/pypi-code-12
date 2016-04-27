from plytix.retailers.fields import *
from plytix.retailers.services import BaseEndpoint


class DataEndpoint(BaseEndpoint):
    """ Endpoint to track data.
    """
    _BASE_ENDPOINT = 'data'
    _BASE_ENDPOINT_RESOURCE = None

    def track(self, customer_id, actions, site_id=None, session_id=None):
        """ Service to track data. Required customer_id, actions and one of them: site_id or session_id
        :param customer_id: Customer identifier.
        :param actions: Actions to track. Dictionary of products. Each product contains a list actions.
            Each action is a dictionary: {'product_id': [{'action_name': 'action', 'action_value': value}, ...]}
        :param session_id: Session identifier.
        :param site_id: Origin site identifier.
        :return: Response.
        """
        data = {
            INPUT_DATA_TRACK_CUSTOMER_ID: customer_id,
            INPUT_DATA_TRACK_ACTIONS: actions,
        }

        if session_id:
            data[INPUT_DATA_TRACK_SESSION_ID] = session_id
        if site_id:
            data[INPUT_DATA_TRACK_SITE_ID] = site_id

        # TODO Validate data
        endpoint = self._BASE_ENDPOINT + '/track'
        try:
            response = super(DataEndpoint, self)._raw_post(endpoint=endpoint, data=data)
            return response.ok
        except Exception as e:
            raise e

    def get_actions(self):
        """ Get all available actions.
        :return: List of actions.
        """
        endpoint = self._BASE_ENDPOINT + '/actions'
        try:
            response = super(DataEndpoint, self)._raw_get(endpoint=endpoint)
            return response.json()[INPUT_DATA_GET_ACTIONS_ACTIONS]
        except Exception as e:
            raise e