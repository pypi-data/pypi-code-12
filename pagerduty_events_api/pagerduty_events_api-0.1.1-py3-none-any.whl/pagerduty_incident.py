from pagerduty_events_api.pagerduty_rest_client import PagerdutyRestClient


class PagerdutyIncident:
    def __init__(self, service_key, incident_key):
        self.__service_key = service_key
        self.__incident_key = incident_key

    def get_service_key(self):
        return self.__service_key

    def get_incident_key(self):
        return self.__incident_key

    def acknowledge(self):
        self.__send_request_with_event_type('acknowledge')

    def resolve(self):
        self.__send_request_with_event_type('resolve')

    def __send_request_with_event_type(self, event_type):
        payload = {'service_key': self.__service_key,
                   'event_type': event_type,
                   'incident_key': self.__incident_key}

        PagerdutyRestClient().post(payload)
