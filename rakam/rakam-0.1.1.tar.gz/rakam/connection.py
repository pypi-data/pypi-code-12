import json
import logging
from collections import OrderedDict

from requests import Session, RequestException

from rakam.exceptions import RakamError, InvalidKeyError, BadKeyError
from rakam.sql import RakamSqlParser


logger = logging.getLogger('rakam.connection')


_EMPTY_PROPERTIES = {}


class RakamCredentials(object):
    def __init__(self, read_key=None, write_key=None, master_key=None):
        self.read_key = read_key
        self.write_key = write_key
        self.master_key = master_key


class RakamConnection(object):
    """
        Communication with rakam server through a persistent connection.
    """

    bulk_uri = "/event/bulk"
    query_uri = "/query/execute"

    def __init__(self, rakam_url, rakam_credentials=None, options=None):
        if options is None:
            options = {}

        self.rakam_url = rakam_url
        self.rakam_credentials = rakam_credentials or RakamCredentials()
        self.write_retry = options.get('write_retry', 0)
        self.write_timeout = options.get('write_timeout', None)
        self.session = Session()
        self.sql_parser = RakamSqlParser()

    def send_bulk_events(self, events):
        max_retries = max(self.write_retry or 0, 0)
        retries = 0

        url = self.rakam_url + self.bulk_uri
        api_key = self.rakam_credentials.master_key
        timeout = self.write_timeout

        if api_key is None:
            raise RakamError("Master key must be set for bulk.")

        while True:
            try:
                response = self._send_post(
                    url,
                    params={'commit': 'false'},
                    data=json.dumps(
                        OrderedDict(
                            [
                                ('api', {'writeKey': api_key}),
                                (
                                    'events',
                                    [
                                        OrderedDict(
                                            (
                                                ("collection", event['collection']),
                                                ("properties", event.get('properties', _EMPTY_PROPERTIES))
                                            )
                                        )
                                        for event in events
                                    ]
                                )
                            ]
                        )
                    ),
                    headers={'Content-Type': 'application/json'},
                    timeout=timeout
                )
            except RequestException as request_exc:
                if retries < max_retries:
                    retries += 1
                    logger.info("Error at rakam request, retrying... Attempt: %s", retries)
                    # retries once more
                else:
                    raise RakamError("Sending events failed with: %s after %s retries" % (request_exc, retries))
            else:
                status_code = int(response.status_code)
                if status_code / 100 != 2:
                    if status_code / 100 == 5 and retries < max_retries:  # Server error, lets retry.
                        retries += 1
                        logger.info("Server error at rakam request, retrying... Attempt: %s", retries)
                        # retries once more
                    else:
                        if status_code == 401:
                            raise InvalidKeyError("Invalid rakam key. Please check that you are using the master key.")
                        elif status_code == 403:
                            raise BadKeyError("Wrong rakam key. Please check that you are using the key for project.")
                        else:
                            raise RakamError(
                                "Sending events failed with status_code: %s body: %s" %
                                (response.status_code, response.text,)
                            )

                else:
                    break  # break on sucess.

        return True

    def execute_sql(self, query, timeout=None):
        url = self.rakam_url + self.query_uri
        api_key = self.rakam_credentials.read_key

        request_kwargs = {
            'headers': {
                'read_key': api_key,
                'Content-Type': 'application/json',
            },
            'data': json.dumps(
                {
                    "query": query,
                    "export_type": "JSON",
                }
            ),
        }

        if timeout is None:
            request_kwargs['timeout'] = timeout

        try:
            response = self._send_post(
                url,
                **request_kwargs
            )
        except RequestException as request_exc:
            raise RakamError("Http request failed with: %s" % (request_exc,))
        else:
            status_code = int(response.status_code)
            if status_code / 100 == 2:
                return self._parse_sql_response(response.json())
            elif status_code == 401:
                raise InvalidKeyError("Invalid rakam key. Please check that you are using the read key.")
            elif status_code == 403:
                message = "Wrong rakam key. Please check that you are using the key for project."
                try:
                    json_body = response.json()
                except:
                    pass
                else:
                    if "error" in json_body:
                        message = json_body["error"]

                raise BadKeyError(message)
            else:
                error_message = response.json()
                raise RakamError(
                    "Request failed with status: %s error_code: %s error: %s" % (
                        status_code,
                        error_message.get('error_code', ''),
                        error_message.get('error', ''),
                    )
                )

    def _parse_sql_response(self, sql_result):
        return self.sql_parser.parse(sql_result)

    # Request sending methods
    def _send_get(self, url, **kwargs):
        return self._send_request(url, method='GET', **kwargs)

    def _send_post(self, url, **kwargs):
        return self._send_request(url, method='POST', **kwargs)

    def _send_request(self, url, method='GET', data='', params=None, headers=None, timeout=None):
        request_kwargs = {'url': url, 'data': data}
        if params is not None:
            request_kwargs['params'] = params

        if headers is not None:
            request_kwargs['headers'] = headers

        if timeout is not None:
            request_kwargs['timeout'] = timeout

        method_upper = method.upper()
        if method_upper == 'GET':
            send_method = self.session.get
        elif method_upper == 'POST':
            send_method = self.session.post
        else:
            raise RakamError("%s method is not supported." % (method,))

        return send_method(**request_kwargs)
