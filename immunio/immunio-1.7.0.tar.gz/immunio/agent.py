from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)


##############################################################################
##############################################################################
## Polyfill to support requests + gevent + python 2.7.9
##
## We can get rid of this by bringing in a new copy of requests once
## https://github.com/shazow/urllib3/issues/482 is fixed.
##
# Re-add sslwrap to Python 2.7.9
import inspect
__ssl__ = __import__('ssl')

try:
    _ssl = __ssl__._ssl
except AttributeError:
    _ssl = __ssl__._ssl2


def new_sslwrap(
        sock, server_side=False, keyfile=None, certfile=None,
        cert_reqs=__ssl__.CERT_NONE, ssl_version=__ssl__.PROTOCOL_SSLv23,
        ca_certs=None, ciphers=None):
    context = __ssl__.SSLContext(ssl_version)
    context.verify_mode = cert_reqs or __ssl__.CERT_NONE
    if ca_certs:
        context.load_verify_locations(ca_certs)
    if certfile:
        context.load_cert_chain(certfile, keyfile)
    if ciphers:
        context.set_ciphers(ciphers)

    caller_self = inspect.currentframe().f_back.f_locals['self']
    return context._wrap_socket(sock, server_side=server_side,
                                ssl_sock=caller_self)

if not hasattr(_ssl, 'sslwrap'):
    _ssl.sslwrap = new_sslwrap
##############################################################################
##############################################################################


from collections import defaultdict
import datetime
import inspect
import platform
import time
import uuid
import socket

from immunio import channel, wsgi
from immunio.engine import Engine
from immunio.logger import log
from immunio.deps.python_ifcfg import ifcfg
from immunio.timer import perf_time, Timer

##############################################################################
# Import the module-level helper methods from `immunio` to maintain the legacy
# `immunio.agent` namespace calls.
from immunio import (  # pylint: disable=unused-import
    report_custom_threat,
    report_failed_login_attempt,
    start,
)


# Use gevent greenlet-local if available, otherwise use normal thread-local
try:
    from gevent.local import local
except ImportError:
    from threading import local


DEFAULT_ENGINE = "SimpleEngine"
DEFAULT_REQUEST_UUID_HEADER = "x-request-uuid"

# How long should the Agent wait for the Immunio Service to provide an
# initial ruleset. Any "Falsy" value means don't wait at all.
DEFAULT_READY_TIMEOUT = None

# Logging defaults.
DEFAULT_LOG_FILE = "log/immunio.log"
DEFAULT_LOG_LEVEL = "info"


def collect_environment():
    """
    Collect information about the Agent environment.
    """
    try:
        import pip
        installed = pip.get_installed_distributions()
        packages = dict((x.project_name, x.version) for x in installed)
    except ImportError:
        packages = None

    hostname = socket.gethostname()
    try:
        # This may fail if hostname is not mapped to an IP by the system.
        hostname_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        hostname_ip = None

    try:
        ips = set()
        for _, iface in ifcfg.interfaces().iteritems():
            if iface['inet'] not in ['127.0.0.1', None]:
                ips.add(iface['inet'])

        ips = list(ips)
    except Exception:
        ips = []

    return {
        "platform": {
            "description": platform.platform(),
        },
        "host": {
            "hostname": hostname,
            "hostname_ip": hostname_ip,
            "ips": ips,
        },
        "runtime": {
            "name": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "language": {
            "name": "python",
        },
        "dependencies": packages,
    }

class AgentRequestStoreContext():
    def __init__(self, store, key, value):
        try:
            self.original_value = store[key]
            self.existed = True
        except KeyError:
            self.existed = False
        self.store = store
        self.key = key

        store[key] = value

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.existed:
            self.store[self.key] = self.original_value
        else:
            try:
                del self.store[self.key]
            except KeyError:
                log.warn("Request Store attempted to delete missing key %s",
                         self.key)


class Agent(object):
    """
    Manages all aspects of Immunio on a target webserver. There should only
    be a single instance of this class for each webserver process.
    """

    MAX_MESSAGES_PER_WORK = 5

    def __init__(self, config, plugin_manager):
        self._config = config

        # Flag to indicate if we have received and processed all initial rules
        # from the Immunio servers.
        self.ready = False

        # Switch to the real logger now that the config is loaded.
        log.switch(
            self._config.get("log_file", DEFAULT_LOG_FILE),
            self._config.get("log_level", DEFAULT_LOG_LEVEL))

        # Create thread-local storage for maintaining the active request_id
        # We don't currently support fully multithreaded servers but we do need
        # this for gevent-based servers since more than one request will be
        # active at a given time.
        self._local = local()
        self._local.request_id = None
        self._local.request_properties = {}

        # The name of the header to add to each response with the request_uuid.
        self._request_uuid_header = self._config.get(
            "request_uuid_header", DEFAULT_REQUEST_UUID_HEADER)

        # How long should the Agent wait to be initialized before starting to
        # process requests.
        self._ready_timeout = self._config.get(
            "ready_timeout", DEFAULT_READY_TIMEOUT, datatype=int)

        # Make a shared timer instance for recording durations
        self.timer = Timer(self.add_timing)

        # Track the hook timings for each request
        self._request_timings = defaultdict(dict)

        # Track the start time of each request so we can track the total
        # duration at the end.
        self._request_start_times = {}

        # If the agent is disabled, don't create Engine, Channel,
        # or PluginManager
        if not self.enabled:
            return

        # Create the engine inside a sandbox.
        self._engine = Engine(self, self._config)

        # Create Channel to communicate with server.
        self._channel = channel.Channel(
            self._config, self._engine.get_current_state,
            environment=collect_environment())

        # Set the callback functions for plugin hooks
        plugin_manager.set_hook_callback(self.run_hook)
        plugin_manager.set_timer_callback(self.add_timing)

        # Start monitoring imported libraries
        # DISABLED until we can reduce the volume of reported data
        # self.import_monitor = ImportMonitor(self)
        # self.import_monitor.start()

    @property
    def enabled(self):
        """
        Check if the Agent is enabled or not.
        """
        return self._config.get("agent_enabled", True, datatype=bool)

    def get_request_uuid_header(self):
        return self._request_uuid_header

    def start(self):
        """
        Start the agent.
        """

    def send_message(self, message):
        """
        Send a message using the current channel.
        """
        self._channel.send_message(message)

    def block_until_ready(self, timeout=60):
        """
        Block until we receive a "ready" message from Immunio. This ensures
        the Agent has received all initialization messages and is ready to
        process incoming traffic with the latest rulesets.
        """
        timeout_expiry = time.time() + timeout
        while not self.ready:
            # Check if our timeout has expired.
            remaining_time = timeout_expiry - time.time()
            if remaining_time < 0:
                return False

            # Wait for an incoming message (at most half a second - we can't
            # use `remaining_time` since we may get the ready message in
            # another green thread and this thread will be stuck waiting).
            msg = self._channel.get_message(block=True, timeout=0.5)
            if msg:
                # Process the message.
                self._process_rx_message(msg)
        return True

    def _do_work(self):
        """
        This function must be called periodically to give the agent a chance
        to do some processing.
        """
        # Process incoming channel messages
        for _ in range(self.MAX_MESSAGES_PER_WORK):
            msg = self._channel.get_message(block=False)
            if not msg:
                break
            self._process_rx_message(msg)

    def _process_rx_message(self, msg):
        """
        Process an incoming message from the Immunio service.
        """
        now = self.timestamp()
        msgtype = msg.get("type")

        # Pass Engine messages into the Engine for processing.
        if str(msgtype).startswith("engine."):
            self._engine.handle_message(now, msg)

        # After processing incoming messages, we are considered "ready" once
        # vmcode and vmdata are set.
        self.ready = self._engine.vmcode_version and self._engine.vmdata_version

    def wrap_wsgi_app(self, app):
        """
        Wrap a WSGI app with the Agent. If agent is disabled, just return
        the original app.
        """
        # Don't wrap again if we've already wrapped once.
        if isinstance(app, wsgi.WsgiWrapper):
            log.warn("The WSGI app callable has already been wrapped by "
                     "Immunio. Immunio will operate normally, but you can "
                     "remove the explict call to `agent.wrap_wsgi_app()`. "
                     "Please contact support@immun.io for more information.")
            return app

        if self.enabled:
            return wsgi.WsgiWrapper(self, app, self._request_uuid_header)
        else:
            return app

    def gen_request_id(self):
        return str(uuid.uuid1())

    def timestamp(self):
        """
        Create a timestamp string. Append a 'Z' so it's clear that all
        timestamps are UTC.
        """
        return datetime.datetime.utcnow().isoformat() + "Z"

    def http_new_request(self):
        # Grab the time from the perf_time clock
        start_time = perf_time()
        # Also grab an ISO8601 timestamp string.
        now = self.timestamp()

        self._channel.start()

        # If configured, block this request until the Agent is initialized.
        # Any 'falsy' timeout means don't wait at all.
        if not self.ready and self._ready_timeout:
            # Start the Channel immediately.
            self.block_until_ready(timeout=int(self._ready_timeout))
            # NOTE: After the timeout expires, we allow the request to
            #       continue even though the Agent hasn't been fully
            #       initialized. This is to prevent a permanent outage if
            #       the Immunio Service is experiencing any down time. If you
            #       would rather wait for full Immunio protection you can
            #       set the `ready_timeout` setting to a huge number to block
            #       forever.
            self._ready_timeout = None

        # Generate new ID
        if self.get_request_id() is not None:
            raise Exception("New request starting before previous request "
                            "(id=%s) complete." % self._local.request_id)
        self._local.request_id = self.gen_request_id()

        # Create a new property store
        try:
            if self._local.request_properties:
                log.warn("New request with existing properties, clearing")
        except AttributeError:
            pass  # No request_properties is expected
        self._local.request_properties = {}

        # Save the request start time
        self._request_start_times[self._local.request_id] = start_time

        # Report to engine
        self._engine.http_new_request(now, self._local.request_id)
        return self._local.request_id

    def http_request_finish(self, request_id=None):
        now = self.timestamp()
        # If request_id is not provided, try to find it
        if request_id is None:
            request_id = self.get_request_id()

        # Report to engine
        self._engine.http_request_finish(now, request_id)

        # Calculate the duration of the request
        duration_sec = perf_time() - self._request_start_times[request_id]
        duration_ms = duration_sec * 1000
        del self._request_start_times[request_id]
        self.add_timing("request.total", duration_ms)

        request_timings = self._request_timings.pop(request_id, {})
        # Ensure that the top-level `plugin` key is present, even if no plugins
        # were timed. This is required by the backend processing.
        request_timings.setdefault("plugin", {})
        self._channel.add_timings(request_timings)

        # Done with this request_id, clear it to help detect failures
        self._local.request_id = None
        self._local.request_properties = {}
        # Let the agent steal a bit of time after each request
        self._do_work()

    def add_timing(self, name, duration_ms):
        """
        Add a single time duration for the current request. The name must
        have at least two parts, separated by a dot (`.`) like `request.total`
        or `plugin.xss.render_template_done` or `hook.http_request_start`.
        """
        request_id = self.get_request_id()

        # The first dotted element is the category (hook, plugin, request)
        category, name = name.split(".", 1)

        timings = (self._request_timings[request_id]
                   .setdefault(category, {})
                   .setdefault(name, {}))
        timings.setdefault("count", 0)
        timings["count"] += 1
        timings.setdefault("total_duration", 0.0)
        timings["total_duration"] += duration_ms

    def run_hook(self, plugin, hook, meta, request_id=None):
        """
        Send the hook data into the Engine. If the Engine is not enabled,
        do nothing.
        """
        # If the Agent is not enabled, return an empty `dict` and no-op
        if not self.enabled:
            return {}

        with self.timer("hook.%s" % hook):
            now = self.timestamp()
            # If request_id is not provided, try to find it
            if request_id is None:
                request_id = self.get_request_id()

            result = self._engine.run_hook(now, request_id, plugin, hook, meta)
            log.debug("Result from hook: %(result)s", {
                "result": result,
                })
            return result

    def get_request_id(self):
        """
        Find the current request_id from thread-local storage. This is
        primarily to support gevent-based servers. We don't support fully
        threaded servers yet.
        This will require some work to make it safe for use in async code
        like tornado or twisted.
        """
        # Default to None if request_id is not set for this thread.
        return getattr(self._local, "request_id", None)

    def property_set(self, key, value):
        return AgentRequestStoreContext(self._local.request_properties, key,
                                        value)

    def property_get(self, key, default=None):
        return self._local.request_properties.get(key, default)
