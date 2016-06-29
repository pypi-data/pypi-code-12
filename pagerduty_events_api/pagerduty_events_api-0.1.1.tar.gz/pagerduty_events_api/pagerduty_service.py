from pagerduty_events_api.pagerduty_incident import PagerdutyIncident
from pagerduty_events_api.pagerduty_rest_client import PagerdutyRestClient


class PagerdutyService:
    def __init__(self, key):
        self.__service_key = key

    def get_service_key(self):
        return self.__service_key

    def trigger(self, description):
        payload = {'service_key': self.__service_key,
                   'event_type': 'trigger',
                   'description': description}

        incident_data = PagerdutyRestClient().post(payload)

        return PagerdutyIncident(self.__service_key, incident_data['incident_key'])
