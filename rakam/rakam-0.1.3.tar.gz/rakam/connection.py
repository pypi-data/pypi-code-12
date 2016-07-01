import json
import logging
from collections import OrderedDict

from requests import Session, RequestException, ReadTimeout

from rakam.exceptions import RakamError, MissingKey, InvalidKeyError, BadKeyError, ConflictError
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
    commit_uri = "/event/bulk/commit"
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
        api_key = self._get_master_key()
        timeout = self.write_timeout

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
            except ReadTimeout:  # Read timeout means events might be added but response not received.
                raise RakamError("Read timeout on bulk.")
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
                            self._raise_for_403(response)
                        else:
                            self._raise_for_unknown(response)

                else:
                    break  # break on sucess.

        return True

    def commit_bulk_events(self, timeout=None, raise_on_read_timeout=False):
        """
            Commits bulk events recently sent to api.
            Returns a True if commit is finished successfully.
            Returns False if read timeout occurs (Commit continues even though a timeout.)

            Raises a subclass of RakamError if request was unsuccessfull or a ConnectionTimeout occurs.
        """
        url = self.rakam_url + self.commit_uri
        api_key = self._get_master_key()

        request_kwargs = {
            'headers': {
                'master_key': api_key,
                'Content-Type': 'application/json',
            },
            'data': json.dumps({"collections": None})
        }

        if timeout is not None:
            request_kwargs['timeout'] = timeout

        success = False
        try:
            response = self._send_post(url, **request_kwargs)
        except ReadTimeout:  # Read timeout is assumed to be processing
            if raise_on_read_timeout:
                raise RakamError("Read timeout on commit.")
            else:
                logger.info("Read timeout on commit, silently passing...")

        except RequestException as request_exc:
            raise RakamError("Http request failed with: %s" % (request_exc,))
        else:
            status_code = int(response.status_code)
            if status_code / 100 == 2:
                success = True
            elif status_code == 401:
                raise InvalidKeyError("Invalid rakam key. Please check that you are using the master key.")
            elif status_code == 403:
                self._raise_for_403(response)
            elif status_code == 409:
                raise ConflictError("Another commit is being proccessed.")
            else:
                self._raise_for_unknown(response)

        return success

    def execute_sql(self, query, timeout=None):
        url = self.rakam_url + self.query_uri
        api_key = self._get_read_key()

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

        if timeout is not None:
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
                self._raise_for_403(response)
            else:
                self._raise_for_unknown(response)

    def _parse_sql_response(self, sql_result):
        return self.sql_parser.parse(sql_result)

    def _parse_error_body(self, json_body):
        return json_body.get("error", None)

    def _get_read_key(self):
        read_key = self.rakam_credentials.read_key
        if read_key is not None:
            return read_key
        else:
            raise MissingKey("read_key is not provided.")

    def _get_write_key(self):
        write_key = self.rakam_credentials.write_key
        if write_key is not None:
            return write_key
        else:
            raise MissingKey("write_key is not provided.")

    def _get_master_key(self):
        master_key = self.rakam_credentials.master_key
        if master_key is not None:
            return master_key
        else:
            raise MissingKey("master_key is not provided.")

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

    # Response handling methods
    def _parse_error_response(self, response):
        try:
            message = self._parse_error_body(response.json())
        except ValueError:
            pass

        return message

    def _raise_for_403(self, response):
        message = self._parse_error_response(response)
        if message is None:
            message = "Wrong rakam key. Please check that you are using the key for project."

        raise BadKeyError(message)

    def _raise_for_unknown(self, response):
        status_code = response.status_code
        try:
            error_message = response.json()
        except ValueError:
            raise RakamError(
                "Request failed with status: %s body: %s" % (
                    status_code, response.text
                )
            )
        except:
            raise RakamError(
                "Request failed with status: %s" % (status_code,)
            )
        else:
            raise RakamError(
                "Request failed with status: %s error_code: %s error: %s" % (
                    status_code,
                    error_message.get('error_code', ''),
                    error_message.get('error', ''),
                )
            )
