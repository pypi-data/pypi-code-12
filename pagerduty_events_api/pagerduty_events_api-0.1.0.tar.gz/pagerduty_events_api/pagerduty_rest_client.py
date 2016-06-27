import json
import requests


class PagerdutyException(Exception):
    pass


class PagerdutyBadRequestException(PagerdutyException):
    pass


class PagerdutyForbiddenException(PagerdutyException):
    pass


class PagerdutyServerErrorException(PagerdutyException):
    pass


class PagerdutyNotFoundException(PagerdutyException):
    pass


class PagerdutyRestClient:
    def post(self, payload):
        response = requests.post('https://events.pagerduty.com/generic/2010-04-15/create_event.json',
                                 json.dumps(payload))

        if response.status_code == 400:
            error_content = json.loads(response.content)
            raise PagerdutyBadRequestException(error_content['message'])

        if response.status_code == 403:
            error_content = json.loads(response.content)
            raise PagerdutyForbiddenException(error_content['message'])

        if response.status_code == 404:
            raise PagerdutyNotFoundException('Could not find PagerDuty endpoint')

        if 500 <= response.status_code < 600:
            raise PagerdutyServerErrorException('Internal server error')

        return json.loads(response.text)
