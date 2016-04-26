from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import sys
import random
import traceback
import threading
from threading import Event, Lock, Thread
import time
from immunio.deps.requests.exceptions import HTTPError
import msgpack

try:
    # Py2
    from Queue import Queue, Empty, Full
    from urlparse import urljoin
except ImportError:
    # Py3
    from queue import Queue, Empty, Full
    from urllib.parse import urljoin

from immunio import (
    __agent_name__,
    __ca_file__,
    __version__,
    __vm_version__,
)
from immunio.counters import aggregate_values
from immunio.deps import requests
from immunio.auth import get_hmac
from immunio.logger import log


DEFAULT_KEY = "-default-"
DEFAULT_SECRET = "-default-"

DEFAULT_HELLO_URL = "https://agent.immun.io/"

DEFAULT_HTTP_TIMEOUT = 30  # seconds

DEFAULT_MAX_REPORT_INTERVAL = 10  # seconds
DEFAULT_MIN_REPORT_SIZE = 25  # number of messages

DEFAULT_MAX_REPORT_SIZE = 50  # number of messages

# A value less than the AgentManager DEFAULT_MAX_REQUEST_SIZE
DEFAULT_MAX_REPORT_BYTES = 1500000

DEFAULT_MAX_MESSAGE_BYTES = DEFAULT_MAX_REPORT_BYTES # Size per message

DEFAULT_MAX_SEND_QUEUE_SIZE = 500  # number of messages

DEFAULT_INITIAL_DELAY_MS = 100  # milliseconds
DEFAULT_MAX_DELAY_MS = 10 * 60 * 1000  # milliseconds

# How many messages will we store from the Agentmanager before we start to
# discard them.
MAX_RECEIVE_QUEUE_SIZE = 5


class Channel(object):
    def __init__(self, config, state_getter=None, environment=None):
        self.state_getter = state_getter

        # Store the provided environment information until it has been sent
        # successfully. Once sent, this value will be set to None so it only
        # gets sent once.
        self._environment = environment

        # LOAD DATA FROM CONFIG
        # Key and secret must be binary strings for hmac & hashlib
        self._key = config.get('key', DEFAULT_KEY).encode('ascii')
        self._secret = config.get('secret', DEFAULT_SECRET).encode('ascii')

        self._hello_url = config.get('hello_url', DEFAULT_HELLO_URL)

        # How long should an HTTP request wait before declaring an error.
        self._http_timeout = config.get('http_timeout', DEFAULT_HTTP_TIMEOUT,
                                        datatype=int)

        # These two settings control the overall message throughput for the
        # channel. The max_report_interval the maximum acceptable latency for a
        # message. If a single message is sent it would stay in the send queue
        # for at-most max_report_interval seconds.
        # The min_report_size controls how much batching will take place. A
        # min_report_size of 1 will cause messages to be sent immediately. A
        # higher value will allow that many messages to be queued before the
        # report is sent. Setting min_report_size higher will be more efficient
        # but will increase latency.
        self._max_report_interval = config.get(
            'max_report_interval', DEFAULT_MAX_REPORT_INTERVAL, datatype=int)
        self._min_report_size = config.get(
            'min_report_size', DEFAULT_MIN_REPORT_SIZE, datatype=int)

        # This settings limits the size of a single report. During normal use,
        # A report will be sent whenever 'min_report_size' is reached. After
        # a connection failure, we may have more than 'min_report_size' messages
        # in the send buffer. This setting limits the maximum number of messages
        # that will be sent in a single report.
        self._max_report_size = config.get(
            'max_report_size', DEFAULT_MAX_REPORT_SIZE, datatype=int)

        # This setting limits the number of bytes contained in a single report.
        # The size should be kept in sync with the Kafta configuration
        self._max_report_bytes = config.get(
            'max_report_bytes', DEFAULT_MAX_REPORT_BYTES, datatype=int)

        # This setting limits the size of each individual message. It must
        # be smaller than max_report_bytes and should leave room for report
        # header information
        self._max_message_bytes = config.get(
            'max_message_bytes', DEFAULT_MAX_MESSAGE_BYTES, datatype=int)

        # Safety valve. If the Agent can't communicate, this is the most
        # messages that will be buffered before messages get discarded.
        self._max_send_queue_size = config.get(
            'max_send_queue_size', DEFAULT_MAX_SEND_QUEUE_SIZE, datatype=int)

        # These two values control the exponential backoff behaviour during
        # communication failure.
        self._initial_delay_ms = config.get(
            'initial_delay_ms', DEFAULT_INITIAL_DELAY_MS, datatype=int)
        self._max_delay_ms = config.get(
            'max_delay_ms', DEFAULT_MAX_DELAY_MS, datatype=int)

        # Threadsafe data
        self._send_queue = Queue(self._max_send_queue_size)
        self._receive_queue = Queue(maxsize=MAX_RECEIVE_QUEUE_SIZE)
        self._is_connected = Event()
        self._stopped = Event()
        self._timings_lock = Lock()

        # Non-threadsafe values
        self._thread = None
        self._url = None
        self._agent_uuid = None
        self._mseq = None
        self._send_seq = 0
        self._send_buffer = []
        self._error_count = 0
        self._success_count = 0
        self._last_report_time = 0
        # _timings is shared by both threads. Use `self._timings_lock` to access
        self._timings = {}
        # _timings_buffer contains timing data that is copied from _timings
        # into the Channel thread, but has not yet been successfully delivered.
        self._timings_buffer = {}

        # Use a session to encourage connection keep-alive.
        self._session = requests.Session()

        # The dropped message count is read-write by the main thread, and
        # read-only by the worker thread. The Python GIL ensures this is safe.
        self.dropped_message_count = 0

        # The number of messages that were dropped due to 413s.
        self.too_large_count = 0

    def start(self):
        if not self._thread:
            self._thread = Thread(target=self._thread_worker)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        if self._thread:
            log.debug("Stopping channel")
            self._stopped.set()
            self._thread.join()
            self._thread = None

    def is_connected(self):
        return self._is_connected.is_set()

    def wait_for_connection(self, timeout=None):
        return self._is_connected.wait(timeout)

    def send_message(self, message):
        # Start thread if it's not already running
        self.start()

        # pre-serialize message before adding to queue. This ensures any
        # serialization errors are raised in the thread of the caller, not
        # the worker thread.
        message_bytes = bytes(msgpack.dumps(message))

        if len(message_bytes) > self._max_message_bytes:
            raise ValueError("Message size too large: {0} > {1}".format(
                len(message_bytes), self._max_message_bytes))

        try:
            self._send_queue.put_nowait(message_bytes)
        except Full:
            log.debug(
                "Dropping message for agent manager "
                "due to queue overflow (%(message)s)", {
                    "message": message,
                    })
            # No room for this message on the queue. Discard.
            self.dropped_message_count += 1

    def get_message(self, block=True, timeout=None):
        try:
            msg = self._receive_queue.get(block, timeout)
        except Empty:
            # No messages available, return None
            return None
        return msg

    def add_timings(self, timings):
        """
        Add additional timing information to the aggregate values.

        Called from the "main" thread.

        Obtain a lock before modifying the totals to avoid interference
        from the Channel worker thread.
        """
        with self._timings_lock:
            aggregate_values(self._timings, timings)

    def get_timings(self):
        """
        Get the current value for the `timings` struct to send with a report.

        Called from the Channel worker thread.

        Transfers the data from _timings to _timings_buffer.

        Obtains a lock on the shared structure, then merges the available
        data with that awaiting delivery.
        """
        with self._timings_lock:
            aggregate_values(self._timings_buffer, self._timings)
            self._timings = {}
        return self._timings_buffer

    def clear_timings(self):
        """
        Mark the _timings_buffer as successfully sent to Agentmanager.

        The _timings_buffer is only accessed by the channel thread
        """
        self._timings_buffer = {}

    def _thread_worker(self):
        log.debug("Starting channel on thread %(ident)s", {
            "ident": threading.current_thread().ident,
            })
        while not self._stopped.is_set():
            try:
                now = time.time()
                if self._prepare_messages_to_send(now):
                    self._send_messages(now)
            except Exception as exc:
                log.warn("Unhandled exception in Immunio channel: %(exc)s", {
                    "exc": exc,
                    })

    def _prepare_messages_to_send(self, now):
        """
        This function is run repeatedly by the _thread_worker function.
        """
        # self._last_report_time is initially 0 so one message will always
        # be sent immediately.
        time_since_last_report = now - self._last_report_time

        interval_expired = time_since_last_report >= self._max_report_interval
        min_report_size_reached = (
            len(self._send_buffer) >= self._min_report_size)

        # We have two different behaviours here. If we haven't reached our
        # max_report_interval, and we haven't reached the min_report_size,
        # we block waiting for more messages.
        if not interval_expired and not min_report_size_reached:
            # Block wait for more messages
            timeout = self._max_report_interval - time_since_last_report
            try:
                msg = self._send_queue.get(block=True, timeout=timeout)
            except Empty:
                # timeout expired, send what we have
                return True
            self._send_buffer.append(msg)
            if len(self._send_buffer) < self._min_report_size:
                # Still not enough messages
                return False

        # See if we can squeeze in more queued messages, up to max_report_size
        while len(self._send_buffer) < self._max_report_size:
            try:
                msg = self._send_queue.get(block=False)
                self._send_buffer.append(msg)
            except Empty:
                # No more messages, carry on
                break
        return True

    def _backoff(self):
        # Exponential backoff
        delay_ms = self._initial_delay_ms * (2 ** (self._error_count - 1))
        # Cap at max_delay_ms
        delay_ms = min(delay_ms, self._max_delay_ms)
        # Add randomness to backoff to avoid herd
        delay_ms = random.randrange(delay_ms)
        log.info("Delaying %(delay_ms)d ms before next request", {
            "delay_ms": delay_ms,
            })
        time.sleep(delay_ms / 1000.0)

    def _log_exception(self, ex_type, ex, tb):
        self._error_count += 1
        if self._error_count == 1:
            log.warn(
                "Connection failed after %(success_count)d successes: "
                "%(ex)s (%(ex_type)s)", {
                    "success_count": self._success_count,
                    "ex": ex,
                    "ex_type": ex_type,
                    })
        else:
            log.warn("Connection failure [%(error_count)d]: "
                     "%(ex)s (%(ex_type)s)", {
                "error_count": self._error_count,
                "ex": ex,
                "ex_type": ex_type,
                })
        log.debug("\n".join(traceback.format_tb(tb)))
        self._is_connected.clear()
        self._success_count = 0

    def _send_messages(self, now):
        try:
            # If we don't have an active connection, start from scratch
            if not self._is_connected.is_set():
                self._hello()
            self._handshake()
            self._last_report_time = now
            # If we successfully handshaked, we have an active connection
            self._success_count += 1
            if self._error_count > 0:
                log.warn(
                    "Connection re-established after "
                    "%(error_count)d failures", {
                        "error_count": self._error_count,
                        })
            self._is_connected.set()
            self._error_count = 0
            return
        except HTTPError as exc:
            self._log_exception(*sys.exc_info())
            error_code = exc.response.status_code
            if error_code == 413:
                log.warn("Request too large, dropping a message")
                if self._send_buffer:
                    self._send_buffer = self._send_buffer[1:]
                    self.dropped_message_count += 1
                    self.too_large_count += 1
            else:
                self._backoff()
        except Exception:
            self._log_exception(*sys.exc_info())
            self._backoff()

    def _hello(self):
        """
        GET from hello URL. Contains url for handshake phase.
        """
        params = {
            "name": __agent_name__,
            "version": __version__,
            "vm_version": __vm_version__,
        }

        r = self._session.get(self._hello_url, params=params,
                              headers={
                                  'Accept': 'application/x-msgpack',
                              },
                              verify=__ca_file__, timeout=self._http_timeout)
        r.raise_for_status()

        response = msgpack.loads(r.content)

        url = response["url"]
        # URL may be relative so join to self._hello_url
        self._url = urljoin(self._hello_url, url)

        log.info("Agent connected to %(hello_url)s", {
            "hello_url": self._hello_url,
            })

    def _num_messages_in_size(self, size, delimiter=b','):
        """Return the number of messages that will fit in size bytes.

        _send_buffer is read to determine how many messages, with
         delimiters between each, could fit in the provided size.
        """

        size += len(delimiter)  # Count an extra delimiter that won't be sent
        for cnt, message in enumerate(self._send_buffer):
            size -= len(message)
            size -= len(delimiter)
            if size < 0:
                return cnt
        return len(self._send_buffer)

    def _handshake(self):
        body = {
            "name": __agent_name__,
            "version": __version__,
            "vm_version": __vm_version__,
            "send_seq": self._send_seq,
            "dropped_message_count": self.dropped_message_count,
            "too_large_message_count": self.too_large_count,
            "timings": self.get_timings(),
        }
        # Include agent state info
        if self.state_getter:
            body.update(self.state_getter())

        # Include the environment if it hasn't been sent yet.
        if self._environment:
            body["environment"] = self._environment

        if self._agent_uuid:
            body["agent_uuid"] = self._agent_uuid
        if self._mseq is not None:
            body["mseq"] = self._mseq

        packer = msgpack.Packer()

        body_bytes = bytes()

        # Add an extra element for 'msgs'
        body_bytes += packer.pack_map_header(len(body) + 1)

        for k, v in body.items():
            body_bytes += packer.pack(k)
            body_bytes += packer.pack(v)

        # Add the msgs key
        body_bytes += packer.pack("msgs")

        # Include room for the array header, which may be up to 5 bytes.
        body_size = len(body_bytes) + 5

        # Number of messages that fit in this report:
        msg_size = self._max_report_bytes - body_size
        num_msgs = self._num_messages_in_size(msg_size)

        # Append the array header
        body_bytes += packer.pack_array_header(num_msgs)
        body_bytes += b''.join(self._send_buffer[:num_msgs])

        # Convert JSON to binary and sign with HMAC
        body_sig = get_hmac(self._secret, body_bytes)

        params = {
            "name": __agent_name__,
            "version": __version__,
            "key": self._key,
            "sig": body_sig,
        }
        log.trace(
            "Sending request to agent manager "
            "with params (%(params)s) and body (%(body)s)", {
                "params": params,
                "body": body_bytes,
                })

        r = self._session.post(self._url, params=params, data=body_bytes,
                               headers={
                                   'Accept': 'application/x-msgpack',
                                   'Content-Type': 'application/x-msgpack',
                               },
                               verify=__ca_file__, timeout=self._http_timeout)
        log.trace(
            "Received response from agent manager "
            "(status: %(status)s, body: %(content)s)", {
                "status": r.status_code,
                "content": r.content,
                })
        r.raise_for_status()

        # If request was successful, remove sent msgs in  _send_buffer
        self._send_seq += num_msgs
        self._send_buffer = self._send_buffer[num_msgs:]
        # Reset the timings buffer
        self.clear_timings()

        # We've successfully sent the environment, clear it so it doesn't
        # send again.
        self._environment = None

        response = msgpack.loads(r.content)

        new_agent_uuid = response.get("agent_uuid")
        if new_agent_uuid:
            if new_agent_uuid != self._agent_uuid:
                log.info("Agent UUID: %(new_agent_uuid)s", {
                    "new_agent_uuid": new_agent_uuid,
                    })
            self._agent_uuid = new_agent_uuid
            # TODO Persist this somewhere

        msgs = response.get("msgs", [])
        for msg in msgs:
            # The messages we receive depend on our state. We can discard
            # messages when we don't have space and the agentmanager will
            # send them again.
            try:
                self._receive_queue.put_nowait(msg)
            except Full:
                # Discard the message, agentmanager will resend.
                pass

        # Save the manager seq so the manager knows we got the response
        self._mseq = response.get("mseq")
