import sys
import json
import base64
import logging

import asyncio

import aiohttp

import binascii

from urllib import parse

from apslite_agent.tasks import parse_params_and_run_task
from apslite_agent.utils import get_agent_version
from apslite_agent import exceptions

logger = logging.getLogger(__name__)


PY344 = sys.version_info > (3, 4, 4)


class OdinCloudConsumer(object):
    def __init__(self, config, oa_id, config_file):
        self.auth = self.get_oauth_keys(config)
        self._config = config
        self._config_file = config_file
        self.oa_id = oa_id
        self.access_token = None
        self.websocket_gate_url = config['auth'].get('websocket_gate_url')
        self.deferred_task = None
        self.access_token = None

        logger.info("Starting, my ID is %s", self.oa_id)

    def get_oauth_keys(self, config):
        auth = base64.b64decode(config['auth']['keys']).decode().replace('\n', '')

        key, secret = auth.split(':')

        return {
            'client_id': key,
            'client_secret': secret,
        }

    def get_service_url(self):
        return self._config['auth']['service_url']

    def oauth_data(self):
        auth = {
            'grant_type': 'client_credentials',
        }

        auth.update(self.auth)

        return auth

    def get_websocket_url(self):
        parts = parse.urlparse(self.websocket_gate_url)
        query = {
            'oa_hostname': self._config['oa']['openapi_url'],
            'service_url': self.get_service_url(),
            'access_token': self.access_token,
            'agent_version': get_agent_version(),
        }

        url = parse.urlunparse(parts._replace(path=parse.urljoin(parts.path, self.oa_id),
                                              query=parse.urlencode(query)))

        logger.debug("Gate URL: %s", url)

        return url

    @asyncio.coroutine
    def ping(self, ws, ping_interval):
        while True:
            try:
                yield from asyncio.sleep(ping_interval)
                ws.ping()
            except asyncio.CancelledError:
                break

    def create_pinned_session(self):
        try:
            fingerprint = self._config['ssl']['fingerprint']
        except KeyError:
            raise RuntimeError("Configuration error: SSL fingerprint is required when SSL "
                               "pinning is turned on")

        def to_binary(s):
            return binascii.unhexlify(s.replace(':', ''))

        conn = aiohttp.TCPConnector(fingerprint=to_binary(fingerprint))

        return aiohttp.ClientSession(connector=conn)

    def create_common_session(self):
        return aiohttp.ClientSession()

    @asyncio.coroutine
    def get_access_token(self):
        url = parse.urlunparse(parse.urlparse(self._config['auth']['service_url'])._replace(
            path='/api/oauth2/token/',
        ))
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(self.oauth_data())

        response = yield from aiohttp.request('POST', url, data=data, headers=headers)
        tokens = yield from response.json()

        if 'access_token' not in tokens:
            raise RuntimeError("Failed to authorize in the service")

        return tokens['access_token']

    @asyncio.coroutine
    def __call__(self):
        sleep_for = 5
        ping_interval = 60
        ws = None

        while True:
            self.access_token = yield from self.get_access_token()

            if self._config.get('ssl', {}).get('pin_ssl', True):
                session = self.create_pinned_session()
            else:
                session = self.create_common_session()

            task = None

            try:
                ws = yield from session.ws_connect(self.get_websocket_url())
            except:
                if ws:
                    yield from ws.close()

                session.close()
                logger.error("Error connecting to the Gate, retrying in %s seconds...", sleep_for)
                yield from asyncio.sleep(sleep_for)
                continue

            try:
                if PY344:
                    task = asyncio.ensure_future(self.ping(ws, ping_interval))
                else:
                    task = asyncio.async(self.ping(ws, ping_interval))

                yield from self.ws_handler(ws)
            except RuntimeError as e:
                logger.exception("WebSocket error: %s", e)
            finally:
                if task:
                    task.cancel()
                    task = None

                logger.info("Connection closed")
                session.close()

            yield from asyncio.sleep(sleep_for)

    def get_meta(self, data):
        return {
            'correlation_id': data.get('meta', {}).get('correlation_id'),
            'access_token': self.access_token,
            'url': self.get_service_url(),
        }

    def run_task(self, data, ws):
        task_name = data.get('task_name', '')
        body = data.get('data')

        logger.info("Got task %s", task_name)
        result = parse_params_and_run_task(task_name, body, ws=ws)

        result['meta'] = self.get_meta(data)

        if 'result' in result:
            result.update({
                'type': 'task_result',
            })

        return result

    @asyncio.coroutine
    def handle_message(self, msg, ws):
        results = []

        if self.deferred_task:
            results.append(self.run_task(self.deferred_task, ws))

            self.deferred_task = None

        if msg.tp == aiohttp.MsgType.text:
            try:
                data = json.loads(msg.data)
            except ValueError:
                logger.error("Error loading json")
                return results

            if data.get('type', '').endswith('_result') and data.get('status') != 'ok':
                logger.error("Got an error from the Gate: %s", data)
                return results

            if data.get('status') == 'error' and data.get('message') == 'unauthorized':
                logger.warn("Access token has expired, refreshing...")

                self.deferred_task = data
                self.refresh_access_token(ws)
                return results

            if data.get('type') == 'task':
                results.append(self.run_task(data, ws))
                return results

        elif msg.tp == aiohttp.MsgType.closed:
            raise exceptions.ConnectionClosed()

        elif msg.tp == aiohttp.MsgType.error:
            logger.error("WebSocket error: %s", msg.data)

    @asyncio.coroutine
    def ws_handler(self, ws):
        while True:
            msg = yield from ws.receive()

            try:
                results = yield from self.handle_message(msg, ws)

                if results:
                    for res in results:
                        ws.send_str(json.dumps(res))
            except exceptions.ConnectionClosed:
                logger.warn("Connection closed")
                break
            except:
                logger.exception("Error handling message")
