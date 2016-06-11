from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import glob
import logging
import os

from immunio import (
    __version__,
    __agent_name__,
)
from immunio.channel import DEFAULT_SECRET, DEFAULT_KEY
from immunio.exceptions import (
    ImmunioBlockedError,
    ImmunioOverrideResponse,
)
from immunio.logger import (
    log,
    make_logger_handler,
)
from immunio.vm import VM


class Engine(object):
    """
    Engine for processing data from incoming requests. Handles
    initializing and using the Lua VM.
    """
    def __init__(self, agent, config):
        self.agent = agent
        self.dev_mode = config.get("dev_mode", False, datatype=bool)

        debug_mode = config.get("debug_mode", False, datatype=bool)
        secret = config.get('secret', DEFAULT_SECRET).encode('ascii')
        key = config.get('key', DEFAULT_KEY).encode('ascii')

        # Keep track of in-progress requests
        self._requests = {}

        # Keep local copy of server-set data
        self._serverdata = {}

        # Configure the logger for the VM
        self.defence_logger = self.make_defence_logger(config)

        self.vmcode_version = None
        self.vmdata_version = None

        # Load the Lua VM for running hook handlers.
        self.vm = VM({
            "DEBUG_MODE": debug_mode,
            "DEV_MODE": self.dev_mode,
            "IMMUNIO_KEY": key,
            "IMMUNIO_SECRET": secret,
        })

        # Dynamic hooks sent from server. If a dynamic hook is present, it will
        # be run instead of any locally defined hook.
        self.dynamic_hooks = {}
        # Global utility functions available to the hook functions in the VM.
        self.utils = {}

        if debug_mode:
            log.info("Debug mode activated!")

        if self.dev_mode:
            log.info("Dev mode activated!")
            self.load_dynamic_handlers_from_files()

    def make_defence_logger(self, config):
        """
        Build a logger for recording defence actions.
        """
        new_logger = logging.getLogger("immunio.defence")
        # Sub-loggers behave a bit differently than the root logger.
        # Prevent log messages from propogating to the root logger.
        new_logger.propogate = False
        # Set logger level to lowest level to allow handler to control level.
        new_logger.setLevel(1)

        # If a log_file is specified, add a handler
        defence_log_file = config.get("defence_log_file")
        if defence_log_file:
            handler = make_logger_handler(
                defence_log_file, config.get("defence_log_level", "INFO"))
            new_logger.addHandler(handler)

        return new_logger

    def get_current_state(self):
        return {
            "vmcode_version": self.vmcode_version,
            "vmdata_version": self.vmdata_version,
        }

    def handle_message(self, timestamp, msg):
        """
        Handle an incoming message for the agent.
        """
        msgtype = msg.get("type")

        if msgtype == "engine.vm.code.update":
            if not self.dev_mode:
                self._update_hooks(msg)

        elif msgtype == "engine.vm.data.update":
            self._serverdata = msg["data"]
            self.vm.set_serverdata(self._serverdata)
            self.vmdata_version = msg["version"]

    def _update_hooks(self, msg):
        """
        Update the Agent hooks to the latest.
        """
        # Load all new hooks into the VM
        new_hooks = {}
        for hook_name, body in msg["code"].items():
            new_hooks[hook_name] = self.vm.create_function(body, hook_name)

        # Run supplied __init__ hook to build utils if provided
        new_utils = {}
        init = new_hooks.pop("__init__", None)
        if init:
            new_utils = self.vm.call(init)

        self.dynamic_hooks = new_hooks
        self.utils = new_utils
        self.vmcode_version = msg["version"]
        log.info("Updated VM code to version %(version)s", {
            "version": self.vmcode_version,
        })


    def _run_dynamic_hook(self, timestamp, request_id, plugin, hook, meta):
        """ Run dynamic hook in a VM. """

        request = self._requests[request_id]

        # Convert request to Lua table
        if isinstance(request, dict):
            request = self.vm.create_object(request)
            self._requests[request_id] = request

        dynamic_hook = self.dynamic_hooks[hook]

        # The provided globals are passed "by-reference" so may be
        # modified by the hook while executing in the VM.
        vars = {
            "agent_type": __agent_name__,
            "agent_version": __version__,
            "timestamp": timestamp,
            "plugin": plugin,
            "hook": hook,
            "meta": meta,
            "request": request,
            "utils": self.utils,
        }

        try:
            # Protect ourselves from exceptions in the engine
            result = self.vm.call(dynamic_hook, vars)
            return result
        except Exception as exc:
            # Raise exceptions in dev mode.
            if self.dev_mode:
                raise

            exception_msg = {
                "type": "engine.exception",
                "request_id": request_id,
                "timestamp": timestamp,
                "plugin": plugin,
                "hook": hook,
                "meta": repr(meta),
                "exception": str(exc),
            }
            log.warn("EXCEPTION IN ENGINE: %s" % exception_msg)
            self.agent.send_message(exception_msg)
            return {}

    def load_dynamic_handlers_from_files(self):
        # Load default hook handlers if present (they do not ship by default)
        path = os.path.realpath(
            os.path.dirname(__file__) + "../../../lua-hooks/hooks")
        log.info("Loading hook handlers from " + path + " ...")

        new_code = {}
        for file in glob.iglob(path + "/*.lua"):
            name = os.path.splitext(os.path.basename(file))[0]
            log.info("Loading hook " + name + " from " + file)
            with open(file, 'r') as f:
                content = f.read()
            new_code[name] = content

        # Compile and load the local code.
        self._update_hooks({
            "version": "local",
            "code": new_code,
        })

    def run_hook(self, timestamp, request_id, plugin, hook, meta):
        if request_id is None or request_id not in self._requests:
            # No usable request
            return {}

        # If a dynamic hook is available, use it.
        dynamic_hook = self.dynamic_hooks.get(hook)
        if dynamic_hook is None:
            # No Lua for this hook, return empty dict
            log.debug(
                "No hook code to run for `%(hook)s`, request %(request_id)s, "
                "returning empty result", {
                    "request_id": request_id,
                    "hook": hook,
                    })
            return {}

        log.debug(
            "Running dynamic hook for request %(request_id)s "
            "with plugin (%(plugin)s), hook (%(hook)s) and "
            "meta (%(meta)s).", {
                "request_id": request_id,
                "plugin": plugin,
                "hook": hook,
                "meta": meta,
                })
        result = self._run_dynamic_hook(timestamp, request_id,
                                        plugin, hook, meta)

        result = self.vm.to_python(result)

        # Ensure result is always a dict.
        if not isinstance(result, dict):
            result = {}

        # Check if there are any diagnostic reports to return
        if "diagnostics" in result:
            for diag in result["diagnostics"]:
                diag_msg = {
                    "type": "engine.diagnostic",
                    "diagnostic_type": diag["report_type"],
                    "diagnostic_message": diag["message"],
                    "diagnostic_meta": diag["meta"],
                    "diagnostic_version": "0.0.2",
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "plugin": plugin,
                    "hook": hook,
                    "meta": meta,
                }
                log.debug("Sending Diagnostic Report: %s" % diag_msg)
                self.agent.send_message(diag_msg)

        # Check if the hook has returned a log line
        if "log" in result and "msg" in result["log"]:
            msg = result["log"]["msg"]
            # Try to get log level, fallback to DEBUG if not specified.
            level = logging.DEBUG
            level_str = result["log"].get("level")
            if level_str:
                level_number = logging.getLevelName(level_str.upper())
                if isinstance(level_number, int):
                    level = level_number
            self.defence_logger.log(level, msg)

        # Check if request should be blocked
        if not result.get("allow", True):
            # request should be blocked
            raise ImmunioBlockedError()

        # Check if response should be overridden
        if "override_status" in result or "override_body" in result:
            raise ImmunioOverrideResponse(
                result.get("override_status", 200),
                result.get("override_headers", []),
                result.get("override_body", ""),
            )

        return result

    def http_new_request(self, timestamp, request_id):
        """
        Notify the engine that a new HTTP request is starting. Details
        of the request will be provided using hooks. Does not return a
        value.
        """
        self._requests[request_id] = {
            "type": "engine.http_request",
            "request_id": request_id,
            "start_time": timestamp,
        }
        log.debug("Created new Request %(request_id)s with data %(data)s", {
            "request_id": request_id,
            "data": self._requests[request_id],
            })

    def http_request_finish(self, timestamp, request_id):
        """
        Allow the engine to clean up data from a request.
        Does not return a value.
        """
        if request_id is None or request_id not in self._requests:
            # No usable request - This should never happen
            # TODO raise Exception
            return

        # Call finish hook
        self.run_hook(timestamp, request_id,
                      "request", "http_request_finish", meta={})

        # Check if this report should be sent.
        result = self.run_hook(timestamp, request_id,
                               "request", "should_report", meta={})
        should_report = False
        if isinstance(result, dict):
            should_report = result.get("report", False)

        req = self._requests[request_id]
        del self._requests[request_id]

        # Send request data if Lua says so.
        if should_report:
            # Convert the request data back to a Python dict if it was
            # a Lua table.
            if not isinstance(req, dict):
                req = self.vm.to_python(req)

            self.agent.send_message(req)

        log.debug("Finishing request %(request_id)s (data: %(data)s)", {
            "request_id": request_id,
            "data": req,
        })
