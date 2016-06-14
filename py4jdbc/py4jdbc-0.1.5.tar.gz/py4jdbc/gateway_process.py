import os
import sys
import signal
import atexit
import logging
import threading
from subprocess import Popen, PIPE
from os.path import abspath, dirname, join

from py4j.java_gateway import GatewayClient, JavaGateway

import py4jdbc
from py4jdbc.version import __version__ as py4jdbc_version


class GatewayProcess:
    command = ['java', '-Xmx512m', 'Gateway']

    shutdown_signals = (
        signal.SIGINT, signal.SIGTERM,
        signal.SIGHUP, signal.SIGQUIT,
        signal.SIGABRT)

    def __init__(self, handle_signals=True, require_ctx_manager=True):
        self._gateway = None
        self._in_ctx_manager = False
        self._require_ctx_manager = require_ctx_manager
        self._shutdown_event = threading.Event()
        self._handle_signals = handle_signals
        self.logger = logging.getLogger('py4jdbc')
        self.is_running = False

    def __enter__(self):
        self._in_ctx_manager = True
        return self.gateway

    def __exit__(self, *args):
        self.shutdown()

    def run(self):
        if self._gateway is not None:
            msg = 'GatewayProcess is already running: %r'
            raise RuntimeError(msg % self)

        if self._require_ctx_manager and not self._in_ctx_manager:
            msg = 'The GatewayProcess must be invoked as a context manager.'
            raise RuntimeError(msg)

        # If program terminates normally, shut down the gateway.
        atexit.register(self.shutdown)

        # Establish signals so if it fails, shutdown the gateway.
        if self._handle_signals:
            self._set_signal_handlers()

        # Now launch the gateway server.
        try:
            self._launch_gateway()
        except Exception as exc:
            self.shutdown()
            raise exc
        self._lauch_echo_thread()
        client = GatewayClient(port=self._gateway_port)
        gateway = JavaGateway(client, auto_convert=True)

        self.is_running = True
        return gateway

    def shutdown(self):
        if self.is_running:
            self.logger.info('Shutting down gateway server: %r', self)
            # Tell the echo server to stop.
            self._shutdown_event.set()
            # Try shutting down the gateway server.
            self.gateway.shutdown()
            # Then forcibly kill.
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
            self.is_running = False

    # -----------------------------------------------------------------------
    # Handle signals.
    # -----------------------------------------------------------------------
    def _shutdown_handler(self, signal, frame):
        self.shutdown()

    def _set_signal_handlers(self):
        self.logger.info('Setting shutdown signal handlers.')
        default_int_handler = signal.default_int_handler
        for sig in self.shutdown_signals:
            handler = signal.getsignal(sig)
            if handler is self._shutdown_handler:
                continue
            elif handler not in [0, default_int_handler]:
                def _handler(*args, **kwargs):
                    try:
                        handler(*args, **kwargs)
                    except RecursionError:
                        return
                    default_int_handler(*args, **kwargs)
                handler = _handler
            else:
                handler = self._shutdown_handler
            signal.signal(sig, handler)

    # -----------------------------------------------------------------------
    # Runs the gateway subprocess and streams it's output to stdout.
    # -----------------------------------------------------------------------
    @property
    def gateway(self):
        if self._gateway is None:
            self._gateway = self.run()
        return self._gateway

    def _launch_gateway(self):
        self.logger.info('Launching gateway server.')
        # Start the GatewayServer.
        self._proc = proc = Popen(
            self.command, stdout=PIPE, stdin=PIPE, preexec_fn=os.setsid)
        try:
            # Determine which ephemeral port the server started on:
            gateway_port = gateway_port = proc.stdout.readline()
            if isinstance(gateway_port, bytes):
                gateway_port = gateway_port.decode('ascii')
            self._gateway_port = gateway_port = int(gateway_port)
            self.logger.info('Gateway server port is %s', gateway_port)
        except ValueError:
            # Grab the remaining lines of stdout
            (stdout, _) = proc.communicate()
            if isinstance(stdout, bytes):
                stdout = stdout.decode('utf8')
            exit_code = proc.poll()
            error_msg = "Launching GatewayServer failed"
            error_msg += " with exit code %d!\n" % exit_code if exit_code else "!\n"
            error_msg += "Warning: Expected GatewayServer to output a port, but found "
            if gateway_port == "" and stdout == "":
                error_msg += "no output.\n"
            else:
                error_msg += "the following:\n\n"
                error_msg += "--------------------------------------------------------------\n"
                error_msg += gateway_port + stdout
                error_msg += "--------------------------------------------------------------\n"
            raise Exception(error_msg)

    def _lauch_echo_thread(self):
        self.logger.info('Launching gateway server echo thread.')
        out = self._proc.stdout
        event = self._shutdown_event
        _EchoOutputThread(out, event).start()


class _EchoOutputThread(threading.Thread):

    def __init__(self, stream, shutdown_event):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stream = stream
        self.shutdown_event = shutdown_event

    def run(self):
        while True:
            if self.shutdown_event.isSet():
                sys.exit(0)
            line = self.stream.readline()
            if isinstance(line, bytes):
                line = line.decode('utf8')
            sys.stderr.write(line)
