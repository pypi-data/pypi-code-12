"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""
import StringIO
import json
import logging
import time
import uuid

import re
from abc import abstractproperty, ABCMeta
from datetime import datetime
from threading import Thread
from urlparse import urlparse

import pika
from pika.exceptions import ChannelClosed
from rdflib import Graph, RDF, Literal, BNode, URIRef
from rdflib.namespace import Namespace, FOAF, XSD

from agora.client.wrapper import Agora

__author__ = 'Fernando Serena'

log = logging.getLogger('agora.stoa.client')

STOA = Namespace('http://www.smartdeveloperhub.org/vocabulary/stoa#')
TYPES = Namespace('http://www.smartdeveloperhub.org/vocabulary/types#')
AMQP = Namespace('http://www.smartdeveloperhub.org/vocabulary/amqp#')


class RequestGraph(Graph):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(RequestGraph, self).__init__()
        self._request_node = BNode()
        self._agent_node = BNode()
        self._broker_node = BNode()
        self._channel_node = BNode()
        self._message_id = self._agent_id = self._submitted_on = self._exchange_name = None
        self._routing_key = self._broker_host = self._broker_port = self._broker_vh = None

        # Node binding
        self.add((self.request_node, STOA.replyTo, self.channel_node))
        self.add((self.request_node, STOA.submittedBy, self.agent_node))
        self.add((self.channel_node, RDF.type, STOA.DeliveryChannel))
        self.add((self.broker_node, RDF.type, AMQP.Broker))
        self.add((self.channel_node, AMQP.broker, self.broker_node))
        self.add((self.agent_node, RDF.type, FOAF.Agent))

        # Default graph
        self.message_id = uuid.uuid4()
        self.submitted_on = datetime.now()
        self.agent_id = uuid.uuid4()
        self.exchange_name = ""
        self.routing_key = ""
        self.broker_host = "localhost"
        self.broker_port = 5672
        self.broker_vh = "/"

        self.bind('stoa', STOA)
        self.bind('amqp', AMQP)
        self.bind('foaf', FOAF)
        self.bind('types', TYPES)

    @property
    def request_node(self):
        return self._request_node

    @property
    def broker_node(self):
        return self._broker_node

    @property
    def channel_node(self):
        return self._channel_node

    @property
    def agent_node(self):
        return self._agent_node

    @property
    def message_id(self):
        return self._message_id

    @abstractproperty
    def type(self):
        pass

    @message_id.setter
    def message_id(self, value):
        self._message_id = Literal(str(value), datatype=TYPES.UUID)
        self.set((self._request_node, STOA.messageId, self._message_id))

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        self._agent_id = Literal(str(value), datatype=TYPES.UUID)
        self.set((self._agent_node, STOA.agentId, self._agent_id))

    @property
    def submitted_on(self):
        return self._submitted_on

    @submitted_on.setter
    def submitted_on(self, value):
        self._submitted_on = Literal(value)
        self.set((self._request_node, STOA.submittedOn, self._submitted_on))

    @property
    def exchange_name(self):
        return self._exchange_name

    @exchange_name.setter
    def exchange_name(self, value):
        self._exchange_name = Literal(value, datatype=TYPES.Name)
        self.set((self.channel_node, AMQP.exchangeName, self._exchange_name))

    @property
    def routing_key(self):
        return self._routing_key

    @routing_key.setter
    def routing_key(self, value):
        self._routing_key = Literal(value, datatype=TYPES.Name)
        self.set((self.channel_node, AMQP.routingKey, self._routing_key))

    @property
    def broker_host(self):
        return self._broker_host

    @broker_host.setter
    def broker_host(self, value):
        self._broker_host = Literal(value, datatype=TYPES.Hostname)
        self.set((self.broker_node, AMQP.host, self._broker_host))

    @property
    def broker_port(self):
        return self._broker_port

    @broker_port.setter
    def broker_port(self, value):
        self._broker_port = Literal(value, datatype=TYPES.Port)
        self.set((self.broker_node, AMQP.port, self._broker_port))

    @property
    def broker_vh(self):
        return self._broker_vh

    @broker_vh.setter
    def broker_vh(self, value):
        self._broker_vh = Literal(value, datatype=TYPES.Path)
        self.set((self.broker_node, AMQP.virtualHost, self._broker_vh))

    def transform(self, elem):
        return elem


class FragmentRequestGraph(RequestGraph):
    __metaclass__ = ABCMeta

    @staticmethod
    def __is_variable(elm):
        return elm.startswith('?')

    def __extend_uri(self, short):
        """
        Extend a prefixed uri with the help of a specific dictionary of prefixes
        :param short: Prefixed uri to be extended
        :return:
        """
        if short == 'a':
            return RDF.type
        for prefix in sorted(self.__prefixes, key=lambda x: len(x), reverse=True):
            if short.startswith(prefix):
                return URIRef(short.replace(prefix + ':', self.__prefixes[prefix]))
        return short

    def is_uri(self, uri):
        if uri.startswith('<') and uri.endswith('>'):
            uri = uri.lstrip('<').rstrip('>')
            parse = urlparse(uri, allow_fragments=True)
            return bool(len(parse.scheme))
        elif ':' in uri:
            prefix_parts = uri.split(':')
            return len(prefix_parts) == 2 and prefix_parts[0] in self.__prefixes

        return uri == 'a'

    @staticmethod
    def tp_parts(tp):
        if tp.endswith('"'):
            parts = [tp[tp.find('"'):]]
            st = tp.replace(parts[0], '').rstrip()
            parts = st.split(" ") + parts
        else:
            parts = tp.split(' ')
        return tuple(parts)

    def __init__(self, *args, **kwargs):
        super(FragmentRequestGraph, self).__init__()
        if not args:
            raise AttributeError('A graph pattern must be provided')

        self.__prefixes = kwargs.get('prefixes', None)
        if self.__prefixes is None:
            raise AttributeError('A prefixes list must be provided')

        elements = {}

        for tp in args:
            s, p, o = self.tp_parts(tp.strip())
            if s not in elements:
                if self.__is_variable(s):
                    elements[s] = BNode(s.lstrip('?'))
                    self.set((elements[s], RDF.type, STOA.Variable))
                    self.set((elements[s], STOA.label, Literal(s, datatype=XSD.string)))
                elif self.is_uri(s):
                    extended = self.__extend_uri(s)
                    if extended == s:
                        elements[s] = URIRef(s.lstrip('<').rstrip('>'))
                    else:
                        elements[s] = self.__extend_uri(s)
            if p not in elements:
                if self.is_uri(p):
                    elements[p] = self.__extend_uri(p)
            if o not in elements:
                if self.__is_variable(o):
                    elements[o] = BNode(o.lstrip('?'))
                    self.set((elements[o], RDF.type, STOA.Variable))
                    self.set((elements[o], STOA.label, Literal(o, datatype=XSD.string)))
                elif self.is_uri(o):
                    extended = self.__extend_uri(o)
                    if extended == o:
                        elements[o] = URIRef(o.lstrip('<').rstrip('>'))
                    else:
                        elements[o] = self.__extend_uri(o)
                else:
                    elements[o] = Literal(o.lstrip('"').rstrip('"'))

            self.add((elements[s], elements[p], elements[o]))


class StreamRequestGraph(FragmentRequestGraph):
    def __init__(self, *args, **kwargs):
        super(StreamRequestGraph, self).__init__(*args, **kwargs)
        self.add((self.request_node, RDF.type, STOA.StreamRequest))

    @property
    def type(self):
        return 'stream'

    def transform(self, quad):
        def __extract_lang(v):
            def __lang_tag_match(strg, search=re.compile(r'[^a-z]').search):
                return not bool(search(strg))

            if '@' in v:
                (v_aux, lang) = tuple(v.split('@'))
                (v, lang) = (v_aux, lang) if __lang_tag_match(lang) else (v, None)
            else:
                lang = None
            return v, lang

        def __transform(x):
            if type(x) == str or type(x) == unicode:
                if self.is_uri(x):
                    return URIRef(x.lstrip('<').rstrip('>'))
                elif '^^' in x:
                    (value, ty) = tuple(x.split('^^'))
                    return Literal(value.replace('"', ''), datatype=URIRef(ty.lstrip('<').rstrip('>')))
                elif x.startswith('_:'):
                    return BNode(x.replace('_:', ''))
                else:
                    (elm, lang) = __extract_lang(x)
                    elm = elm.replace('"', '')
                    if lang is not None:
                        return Literal(elm, lang=lang)
                    else:
                        return Literal(elm, datatype=XSD.string)
            return x

        triple = quad[1:]
        return tuple([quad[0]] + map(__transform, triple))


class QueryRequestGraph(FragmentRequestGraph):
    def __init__(self, *args, **kwargs):
        super(QueryRequestGraph, self).__init__(*args, **kwargs)
        self.add((self.request_node, RDF.type, STOA.QueryRequest))

    @property
    def type(self):
        return 'query'


class EnrichmentRequestGraph(FragmentRequestGraph):
    def __init__(self, *args, **kwargs):
        self._target_resource = ""
        super(EnrichmentRequestGraph, self).__init__(*args, **kwargs)
        self.add((self.request_node, RDF.type, STOA.EnrichmentRequest))

    @property
    def type(self):
        return 'enrichment'

    @property
    def target_resource(self):
        return self._target_resource

    @target_resource.setter
    def target_resource(self, value):
        self._target_resource = URIRef(value)
        self.set((self.request_node, STOA.targetResource, self._target_resource))


class StoaClient(object):
    def __init__(self, broker_host='localhost', broker_port=5672, wait=False, monitoring=None, agora_host='localhost',
                 agora_port=5002, stop_event=None, exchange='stoa', topic_pattern='stoa.request',
                 response_prefix='stoa.response'):
        self.agora = Agora(host=agora_host, port=agora_port)
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker_host, port=broker_port))
        self.__channel = self.__connection.channel()
        self.__listening = False
        self.__accept_queue = self.__response_queue = None
        self.__monitor = Thread(target=self.__monitor_consume, args=[monitoring]) if monitoring else None
        self.__last_consume = datetime.now()
        self.__keep_monitoring = True
        self.__accepted = False
        self.__message = None
        self.__wait = wait
        self.__stop_event = stop_event
        self.__exchange = exchange
        self.__topic_pattern = topic_pattern
        self.__response_prefix = response_prefix

    def __monitor_consume(self, t):
        log.debug('Stoa client monitor started...')
        while self.__keep_monitoring:
            if (datetime.now() - self.__last_consume).seconds > t:
                self.stop()
                break
            else:
                time.sleep(0.1)

    def request(self, message):
        self.__response_queue = self.__channel.queue_declare(auto_delete=True).method.queue
        message.routing_key = self.__response_queue
        self.__message = message

        self.__accept_queue = self.__channel.queue_declare(auto_delete=True).method.queue
        self.__channel.queue_bind(exchange=self.__exchange, queue=self.__accept_queue,
                                  routing_key='{}.{}'.format(self.__response_prefix, str(message.agent_id)))

        body = message.serialize(format='turtle')

        self.__channel.basic_publish(exchange=self.__exchange,
                                     routing_key='{}.{}'.format(self.__topic_pattern, self.__message.type),
                                     body=body)

        log.debug(body)
        log.info('sent {} request!'.format(self.__message.type))

        self.__listening = True
        return self.agora.prefixes, self.__consume()

    def __consume(self):
        def __response_callback(properties, body):
            stop_flag = False
            if properties.headers.get('state', None) == 'end':
                log.info('End of stream received!')
                stop_flag = True

            format = properties.headers.get('format', 'json')
            if format == 'turtle':
                graph = Graph()
                graph.parse(StringIO.StringIO(body), format=format)
                yield properties.headers, graph
            else:
                items = json.loads(body) if format == 'json' else eval(body)
                if items and not isinstance(items, list):
                    items = [items]
                for item in items:
                    yield properties.headers, item

            if stop_flag:
                self.stop()

        log.debug('Waiting for acceptance...')
        for message in self.__channel.consume(self.__accept_queue, no_ack=True, inactivity_timeout=1):
            if message is not None:
                method, properties, body = message
                g = Graph()
                g.parse(StringIO.StringIO(body), format='turtle')
                if len(list(g.subjects(RDF.type, STOA.Accepted))) == 1:
                    log.info('Request accepted!')
                    self.__accepted = True
                else:
                    log.error('Bad request!')
                self.__channel.queue_delete(self.__accept_queue)
                self.__channel.cancel()
                break
            elif self.__stop_event is not None:
                if self.__stop_event.isSet():
                    self.stop()
        if not self.__accepted:
            log.debug('Request not accepted. Aborting...')
            raise StopIteration()
        if self.__monitor is not None:
            self.__monitor.start()
        log.debug('Listening...')
        for message in self.__channel.consume(self.__response_queue, no_ack=True, inactivity_timeout=1):
            if message is not None:
                method, properties, body = message
                for headers, item in __response_callback(properties, body):
                    yield headers, self.__message.transform(item)
            elif not self.__wait:
                yield None
            elif self.__stop_event is not None:
                if self.__stop_event.isSet():
                    self.stop()
                    raise StopIteration()
            else:
                log.debug('Inactivity timeout...')
            self.__last_consume = datetime.now()
        if self.__monitor is not None:
            self.__keep_monitoring = False
            log.debug('Waiting for client monitor to stop...')
            self.__monitor.join()

    def stop(self):
        try:
            self.__channel.queue_delete(self.__accept_queue)
            self.__channel.queue_delete(self.__response_queue)
            self.__channel.cancel()
            self.__channel.close()
            self.__listening = False
        except ChannelClosed:
            pass
        log.debug('Stopped stoa client!')

    @property
    def listening(self):
        return self.__listening


def get_fragment_generator(*args, **kwargs):
    stoa_kwargs = kwargs['STOA']
    stoa_kwargs.update({k: kwargs[k] for k in kwargs if k == 'wait' or k == 'monitoring'})
    client = StoaClient(**stoa_kwargs)
    request = StreamRequestGraph(prefixes=client.agora.prefixes, *args)
    if 'updating' in kwargs:
        request.add(
            (request.request_node, STOA.expectedUpdatingDelay, Literal(kwargs['updating'], datatype=XSD.integer)))
    if 'gen' in kwargs:
        request.add((request.request_node, STOA.allowGeneralisation, Literal(True, datatype=XSD.boolean)))
    if 'events' in kwargs:
        request.add((request.request_node, STOA.updateOnEvents, Literal(True, datatype=XSD.boolean)))
    request.broker_host = stoa_kwargs['broker_host']
    return client.request(request)


def get_query_generator(*args, **kwargs):
    stoa_kwargs = kwargs['STOA']
    stoa_kwargs.update({k: kwargs[k] for k in kwargs if k == 'wait' or k == 'monitoring'})
    client = StoaClient(**stoa_kwargs)
    request = QueryRequestGraph(prefixes=client.agora.prefixes, *args)
    if 'updating' in kwargs:
        request.add(
            (request.request_node, STOA.expectedUpdatingDelay, Literal(kwargs['updating'], datatype=XSD.integer)))
    if 'gen' in kwargs:
        request.add((request.request_node, STOA.allowGeneralisation, Literal(True, datatype=XSD.boolean)))
    if 'events' in kwargs:
        request.add((request.request_node, STOA.updateOnEvents, Literal(True, datatype=XSD.boolean)))
    request.broker_host = stoa_kwargs['broker_host']
    return client.request(request)


def get_enrichment_generator(*args, **kwargs):
    def apply_target(x):
        if x.startswith('*'):
            return x.replace('*', '<{}>'.format(target))
        return x

    target = kwargs['target']
    del kwargs['target']
    args = map(lambda x: apply_target(x), args)

    client = StoaClient(**kwargs)
    request = EnrichmentRequestGraph(prefixes=client.agora.prefixes, *args)
    request.broker_host = kwargs['broker_host']
    request.target_resource = target
    return client.request(request)
