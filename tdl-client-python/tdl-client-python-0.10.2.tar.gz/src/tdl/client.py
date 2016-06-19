__author__ = 'tdpreece'
import logging
import time
import json
from collections import OrderedDict

import stomp

logger = logging.getLogger('tdl.client')
logger.addHandler(logging.NullHandler())


class Client(object):
    def __init__(self, hostname, unique_id, port=61613):
        self.hostname = hostname
        self.port = port
        self.unique_id = unique_id

    def go_live_with(self, processing_rules):
        self.run(ApplyProcessingRules(processing_rules))

    def run(self, handling_strategy):
        try:
            print('Starting client')
            remote_broker = RemoteBroker(self.hostname, self.port, self.unique_id)
            remote_broker.subscribe(handling_strategy)
            time.sleep(1)
            print('Stopping client')
            remote_broker.close()
        except Exception as e:
            print('There was a problem processing messages')
            logger.exception('Problem communicating with the broker.')


class ApplyProcessingRules(object):
    def __init__(self, processing_rules):
        self.processing_rules = processing_rules

    def process_next_message_from(self, remote_broker, headers, message):
        # Decode request
        try:
            decoded_message = json.loads(message)
            method = decoded_message['method']
            params = decoded_message['params']
            id = decoded_message['id']
        except:
            decoded_message = ''
            method = ''
            params = ''
            id = ''
            print('Invalid message format')
            action = 'stop'

        # Match implementation
        if method not in self.processing_rules.rules:
            user_result_message = 'error = "method \'{}\' did not match any processing rule", (NOT PUBLISHED)'.format(method)
            action = 'stop'
        else:
            implementation = self.processing_rules.rules[method].user_implementation
            try:
                result = implementation(*params)
                action = self.processing_rules.rules[method].client_action

                if 'publish' in action:
                    user_result_message = 'resp = {}'.format(self.get_parameter_msg(result))
                else:
                    user_result_message = 'resp = {}, (NOT PUBLISHED)'.format(self.get_parameter_msg(result))

            except Exception as e:
                result = ''
                logger.exception('The user implementation has thrown an exception: {}'.format(e.message))
                user_result_message = 'error = "user implementation raised exception", (NOT PUBLISHED)'
                action = 'stop'

            if 'publish' in action:
                response = OrderedDict([
                    ('result', result),
                    ('error', None),
                    ('id', id),
                ])

                remote_broker.acknowledge(headers)
                remote_broker.publish(response)

        self.print_user_message(params, user_result_message, id, method)
        if 'stop' in action:
            remote_broker.conn.unsubscribe(1)
            remote_broker.conn.remove_listener('listener')

    def print_user_message(self, params, user_result_message, id, method):
        params_str = ", ".join([self.get_parameter_msg(p) for p in params])
        print('id = {id}, req = {method}({params}), {user_result_message}'.format(id=id, method=method, params=params_str,
                                                                                  user_result_message=user_result_message))

    @staticmethod
    def get_parameter_msg(parameter):
        if not isinstance(parameter, basestring):
            return str(parameter)
        lines = str(parameter).split('\n')
        if len(lines) == 1:
            return '"{}"'.format(lines[0])
        if len(lines) == 2:
            return '"{} .. ( 1 more line )"'.format(lines[0])
        return '"{} .. ( {} more lines )"'.format(lines[0], len(lines) - 1)


class Listener(stomp.ConnectionListener):
    def __init__(self, remote_broker, handling_strategy):
        self.remote_broker = remote_broker
        self.handling_strategy = handling_strategy

    def on_message(self, headers, message):
        self.handling_strategy.process_next_message_from(self.remote_broker, headers, message)


class RemoteBroker(object):
    def __init__(self, hostname, port, unique_id):
        hosts = [(hostname, port)]
        self.conn = stomp.Connection(host_and_ports=hosts, timeout=10)
        self.conn.start()
        self.conn.connect(wait=True)
        self.unique_id = unique_id

    def acknowledge(self, headers):
        self.conn.ack(headers['message-id'], headers['subscription'])

    def publish(self, response):
        self.conn.send(
                body=json.dumps(response, separators=(',', ':')),
                destination='{}.resp'.format(self.unique_id)
        )

    def subscribe(self, handling_strategy):
        listener = Listener(self, handling_strategy)
        self.conn.set_listener('listener', listener)
        self.conn.subscribe(
                destination='{}.req'.format(self.unique_id),
                id=1,
                ack='client-individual'
        )

    def close(self):
        self.conn.disconnect()
