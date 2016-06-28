#!/usr/bin/env python3

import asyncio
import functools
import logging
import os
import random
import ribbonbridge as rb
import serial.tools.list_ports
import serial.aio
import sfp
import websockets as ws
import sys
import uuid

_dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_dirname)

if sys.version_info < (3,4,4):
    asyncio.ensure_future = asyncio.async

from . import commontypes_pb2 as rbcommon
from . import daemon_pb2 as rbdaemon
from . import robot_pb2 as rbrobot
from . import dongle_pb2 as rbdongle

__all__ = ['DaemonListenServer']

#__computer_id__ = random.randint(0, 1<<32-1)
#__computer_id__ = 432342 # Static for debugging purposes FIXME
__computer_id__ = uuid.getnode() & (1<<32-1)

class DongleManager(rb.Proxy):
    class Mode:
        NONE = 0
        FULL_DUPLEX = 1
        DOUBLE_DONGLE = 2

    @classmethod
    @asyncio.coroutine
    def create(cls):
        self = cls( os.path.join(_dirname, 'dongle_pb2.py') )
        self.dongle_event = asyncio.Condition()
        self.__task = asyncio.ensure_future(self.__poll_serial())
        self._dongles = set()
        self._connections = {}
        self._mode = self.Mode.NONE
        self._transmit_dongle = None
        self._receive_dongle = None
        self._duplex_dongle = None
        self._outbox = asyncio.Queue()

        self.__out_pump_handle = asyncio.ensure_future(self.__out_pump())

        return self

    def add_robot_connection(self, connection):
        self._connections[connection._serial_id] = connection

    def remove_robot_connection(self, serial_id):
        try:
            del self._connections[serial_id]
        except KeyError:
            logging.warning('Remove non-existent connection: {}'.format(serial_id))

    @asyncio.coroutine
    def stop(self):
        self.__task.cancel()

    @asyncio.coroutine
    def transmitUnicast(self, obj):
        logging.info('DongleManager.transmitUnicast')
        fut = asyncio.Future()
        yield from self._outbox.put((obj, fut))
        return fut

    @asyncio.coroutine
    def handle_dongle_added(self, com_ports):
        #yield from self.dongle_event.acquire()
        logging.info('Dongle added: {}'.format(str(com_ports)))
        for port in com_ports:
            dongle = yield from Dongle.create(port)
            self._dongles.add(dongle)
            
        if len(self._dongles) >= 2:
            # Set the original dongle to be a receiver
            # Add the new dongle
            logging.info('Multiple dongles detected. Switching to double-dongle mode.')
            it = iter(self._dongles)
            dongle = next(it)
            yield from dongle.set_receiver(self._from_dongle)
            self._receive_dongle = dongle
            dongle = next(it)
            yield from dongle.set_transmitter()
            self._transmit_dongle = dongle
            self._duplex_dongle = None
            self._mode = self.Mode.DOUBLE_DONGLE
        elif len(self._dongles) > 0:
            logging.info('Single dongle detected. Switching to full-duplex mode.')
            it = iter(self._dongles)
            dongle = next(it)
            yield from dongle.set_full_duplex(self._from_dongle)
            self._receive_dongle = None
            self._transmit_dongle = None
            self._duplex_dongle = dongle
            self._mode = self.Mode.FULL_DUPLEX
        else:
            logging.info('No dongles detected.')
            self._receive_dongle = None
            self._transmit_dongle = None
            self._duplex_dongle = None
            self._mode = self.Mode.NONE
        logging.info('Notifying dongle_event...')
        #yield from self.dongle_event.notify_all()
        #yield from self.dongle_event.release()

    @asyncio.coroutine
    def handle_dongle_removed(self, dongles):
        #yield from self.dongle_event.acquire()
        logging.info('Dongle removed: {}'.format(str(dongles)))
        for d in self._dongles:
            if d._serial_port in dongles:
                self._dongles.remove(d)
                break

        if len(self._dongles) >= 2:
            it = iter(self._dongles)
            dongle = next(it)
            yield from dongle.set_receiver(self._from_dongle)
            self._receive_dongle = dongle
            dongle = next(it)
            yield from dongle.set_transmitter()
            self._transmit_dongle = dongle
            self.mode = self.Mode.DOUBLE_DONGLE
        elif len(self._dongles) == 1:
            it = iter(self._dongles)
            dongle = next(it)
            yield from dongle.set_full_duplex(self._from_dongle)
            self.mode = self.Mode.FULL_DUPLEX
        else:
            logging.info('No dongles detected.')
            self._receive_dongle = None
            self._transmit_dongle = None
            self._duplex_dongle = None
            self._mode = self.Mode.NONE
        #yield from self.dongle_event.notify_all()
        #yield from self.dongle_event.release()

    @asyncio.coroutine
    def __poll_serial(self):
        while True:
            logging.info('poll.')
            dongles = serial.tools.list_ports.comports()
            filtered_dongles = set()
            dongle_descriptions = ['Barobo USB-Serial Adapter',
                                   'Linkbot USB-Serial Adapter']
            for d in dongles:
                if d[1] in dongle_descriptions:
                    filtered_dongles.add(d[0])

            dongles = filtered_dongles

            current_dongle_ports = set()
            for d in self._dongles:
                current_dongle_ports.add(d._serial_port)

            if len(dongles) > len(self._dongles):
                # A dongle was plugged in
                yield from self.handle_dongle_added(dongles-current_dongle_ports)
            elif len(self._dongles) > len(dongles):
                # A dongle was removed
                yield from self.handle_dongle_removed(current_dongle_ports-dongles)

            yield from asyncio.sleep(1)
            
    @asyncio.coroutine
    def __out_pump(self):
        logging.info('DongleManager.__out_pump() starting...')
        def done_cb(user_fut, fut):
            user_fut.set_result(fut.result())

        while True:
            logging.info('DongleManager waiting on outbox...')
            msg, user_fut = yield from self._outbox.get()
            if self._mode == self.Mode.FULL_DUPLEX:
                trx_dongle = self._duplex_dongle
            elif self._mode == self.Mode.DOUBLE_DONGLE:
                trx_dongle = self._transmit_dongle
            logging.info('DongleManager processing transmitUnicast message...')
            fut = yield from trx_dongle.transmitUnicast(msg)
            fut.add_done_callback(functools.partial(done_cb, user_fut))
            rc = yield from fut
            if rc.queuedMessages >= 2:
                exponent = rc.queuedMessages - 2
                backoff = (2**exponent) * 14
                yield from asyncio.sleep(backoff/1000)

    @asyncio.coroutine
    def _from_dongle(self, payload):
        # Multiplex based on serial ID
        try:
            yield from self._connections[payload.serialId.value]\
                           .inbox.put(
                               payload.sessionMessage.payload.value )
            logging.info('Reply forwarded to robot proxy.')
        except KeyError:
            logging.info('Received reply from unconnected robot: '+payload.serialId.value)
            pass


class Dongle(rb.Proxy):
    @classmethod
    @asyncio.coroutine
    def create(cls, serial_port, logger=None):
        self = cls( os.path.join(_dirname, 'dongle_pb2.py') )
        (transport, protocol) = yield from serial.aio.create_serial_connection(
            asyncio.get_event_loop(),
            functools.partial(sfp.asyncio.SfpProtocol, asyncio.get_event_loop()),
            serial_port,
            baudrate=115200 )
        self._serial_port = serial_port
        self._proxy = protocol
        self._transport = transport

        # FIXME : SFP Crashes w/out the following sleep
        yield from asyncio.sleep(1)

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('Dongle <{}>'.format(serial_port))

        self._pump = asyncio.ensure_future(self._from_dongle_pump())

        yield from self.setComputerId( computerId = __computer_id__ )
        return self

    def stop(self):
        self._pump.cancel()

    @asyncio.coroutine
    def set_receiver(self, recv_handler):
        # recv_handler - a coroutine to be called whenever a new transmission
        # is received. recv_handler(payload) where payload is a protobuf
        # dongle.receiveTransmission object.
        fut = yield from self.setRadioMode(mode=rbdongle.setRadioMode.RECEIVE)
        self.rb_add_broadcast_handler('receiveTransmission', recv_handler)
        return fut

    @asyncio.coroutine
    def set_transmitter(self):
        try:
            self.rb_remove_broadcast_handler('receiveTransmission')
        except KeyError:
            pass
        fut = yield from self.setRadioMode(mode=rbdongle.setRadioMode.TRANSMIT)
        return fut

    @asyncio.coroutine
    def set_full_duplex(self, recv_handler):
        yield from self.setRadioMode(mode=rbdongle.setRadioMode.FULL_DUPLEX)
        self.rb_add_broadcast_handler('receiveTransmission', recv_handler)

    @asyncio.coroutine
    def _from_dongle_pump(self):
        while True:
            packet = yield from self._proxy.recv()
            yield from self.rb_deliver(packet)

    @asyncio.coroutine
    def rb_emit_to_server(self, bytestring):
        self._proxy.write(bytestring)

class RobotConnection():
    @classmethod
    @asyncio.coroutine
    def create (cls, dongle, serial_id, connections):
        self = cls()
        self._connections = connections
        self._serial_id = serial_id
        self._dongle = dongle

        # Create a new websocket server
        self._server = yield from ws.serve(self._new_connection, '0.0.0.0', 0)
        host, port = self._server.server.sockets[0].getsockname()
        self.host = host
        self.port = port

        self.inbox = asyncio.Queue()
        self._dongle.add_robot_connection(self)
        asyncio.ensure_future(self.__pump())
        self._connections.add(self)
        return self

    @asyncio.coroutine
    def _new_connection(self, protocol, uri):
        # Now we need to forward all incoming shit to the dongle and all shit
        # from the dongle back
        self._protocol = protocol
        while True:
            try:
                msg = yield from protocol.recv()
                logging.info('RobotConnection received message from proxy.')
                args = self._dongle.rb_get_args_obj('transmitUnicast')
                args.serialId.value = self._serial_id
                args.destinationPort = rbcommon.ROBOT_SERVER
                args.sourcePort = rbcommon.ROBOT_CLIENT
                args.sessionMessage.computerId = __computer_id__
                args.sessionMessage.payload.value = msg
                fut = yield from self._dongle.transmitUnicast(args)
                fut.add_done_callback(self.__unicast_done)
            except ws.exceptions.ConnectionClosed:
                self._connections.remove(self)
                # Create and send a robot disconnect message TODO
                

    def __unicast_done(self, fut):
        logging.info('{} MESSAGES QUEUED ON DONGLE'.format(fut.result().queuedMessages))

    @asyncio.coroutine
    def __pump(self):
        while True:
            msg = yield from self.inbox.get()
            logging.info('RobotConnection received new inbox message.')
            yield from self._protocol.send(msg)

    @asyncio.coroutine
    def close(self):
        pass
       
class DaemonServer(rb.Server): 
    @classmethod
    @asyncio.coroutine
    def create(cls, recv_func, dongle):
        # recv_func should be a coroutine that, when called, receives bytes
        # from the transport.
        self = cls()
        self._recv = recv_func
        self._dongle = dongle
        asyncio.ensure_future(self._pump())
        self._robot_connections = set()
        self._run_futures = []
        return self

    def get_run_future(self):
        fut = asyncio.Future()
        self._run_futures.append(fut)
        return fut

    @asyncio.coroutine
    def _pump(self):
        while True:
            logging.info("Daemon received message from client.")
            payload = yield from self._recv()
            yield from self.inbox(payload)

    @asyncio.coroutine
    def resolveSerialId(self, payload):
        pbuf = rbdaemon.resolveSerialId.In()
        pbuf.ParseFromString(payload)
        serial_id = pbuf.serialId.value
        robot_connection = yield from RobotConnection.create(
            self._dongle,
            serial_id,
            self._robot_connections )
        reply = rbdaemon.resolveSerialId.Result()
        reply.status = rbcommon.OK
        reply.endpoint.address = robot_connection.host
        reply.endpoint.port = robot_connection.port
        return reply.SerializeToString()        

class DaemonListenServer():
    @classmethod
    @asyncio.coroutine
    def create(cls, hostname='localhost', port=42000):
        self = cls()
        # Open a websocket
        self._server = yield from ws.serve(self._new_connection, hostname, port)
        self._connections = set()
        self._dongle = yield from DongleManager.create()
        logging.info('Now listening for new connections...')
        return self

    @asyncio.coroutine
    def _new_connection(self, protocol, uri):
        logging.info("New connection received from: "+uri)
        protocol.handshake()
        server = yield from DaemonServer().create(protocol.recv, self._dongle)
        server.deliver = protocol.send
        self._connections.add(server)
        fut = server.get_run_future()
        yield from fut


