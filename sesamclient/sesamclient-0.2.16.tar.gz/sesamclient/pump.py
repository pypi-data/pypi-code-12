# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import time

import dateutil.parser

from .entitybase import EntityBase
from .exceptions import PumpIsAlreadyRunning, TimeoutWhileWaitingForRunningPumpToFinishException
from .utils import validate_response_is_ok, validate_equal_case_insensitive


def parse_datetime(datetimestring):
    if not datetimestring:
        return None
    return dateutil.parser.parse(datetimestring)


class Pump(EntityBase):
    """
    """
    def __init__(self, pipe_id, connection, raw_jsondata):
        self.pipe_id = pipe_id
        super().__init__(connection, raw_jsondata)

    @property
    def id(self):
        return "pump:" + self.pipe_id

    @property
    def type(self):
        return "pump"

    def __str__(self):
        result = super().__str__()
        result += "\n    pipe_id:%r" % (self.pipe_id,)
        return result

    def get_is_running(self):
        # Note: we must retrieve up-to-date information from the server, since the runtime stuff is so
        #       dynamic.
        self.update_raw_jsondata_from_url(self._connection.get_pipe_pump_url(self.pipe_id))
        return self._raw_jsondata["runtime"]["is-running"]

    def wait_for_pump_to_finish_running(self, timeout=60):
        """Utility method for waiting until the pump is no longer running. This is useful in
        integration tests that want to make sure that the pump has been run after the test-code has
        modified the data in the source-system of a pipe.

        :param timeout: The maximum time to wait for the pump to stop running. If the timeout is exceeded,
                        an error is raised.
        """
        starttime = time.monotonic()
        while True:
            if not self.get_is_running():
                # ok, we are not running, so we can exit now
                break

            elapsedtime = time.monotonic() - starttime
            if elapsedtime > timeout:
                raise TimeoutWhileWaitingForRunningPumpToFinishException(
                    "Timed out while waiting for the pump to finish running! pump:\n%s" % (
                        self.as_json(),))
            time.sleep(0.5)

    @property
    def last_message(self):
        return self._raw_jsondata["runtime"]["last-message"]

    @property
    def last_seen(self):
        return self._raw_jsondata["runtime"]["last-seen"]

    def unset_last_seen(self):
        self.update_last_seen(None)

    def update_last_seen(self, last_seen):
        self_link = self._connection.get_pipe_pump_url(self.pipe_id)

        post_response = self._connection.do_post_request(self_link, data={"operation": "update-last-seen",
                                                                          "last-seen": last_seen})

        # check that we get a 200-response with a representation of the updated pump.
        validate_response_is_ok(post_response)
        validate_equal_case_insensitive(post_response.headers["Content-Type"], "application/json")
        self.update_raw_jsondata(post_response.text)

        # Check that the "is-disabled"-attribute has been updated
        actual_last_seen = self.last_seen
        if actual_last_seen != last_seen:
            if (last_seen is None and actual_last_seen == "") or (last_seen == "" and actual_last_seen is None):
                # None and an empty string means the same here.
                pass
            else:
                raise AssertionError(
                    "Failed to update the 'last-seen'-value of the pump '%s'! expected value: '%s'  actual value: '%s'" % (
                        self.id, last_seen, actual_last_seen))

    @property
    def is_disabled(self):
        return self._raw_jsondata["runtime"]["is-disabled"]

    @property
    def is_valid_config(self):
        return self._raw_jsondata["runtime"]["is-valid-config"]

    @property
    def last_run(self):
        return parse_datetime(self._raw_jsondata["runtime"]["last-run"])

    @property
    def next_run(self):
        return parse_datetime(self._raw_jsondata["runtime"]["next-run"])

    def disable(self):
        """Disable this pump. This prevents the pump from being automatically run by the task scheduler"""
        self._set_disabled_state(True)

    def enable(self):
        """Enable this pump."""
        self._set_disabled_state(False)

    def _set_disabled_state(self, is_disabled):
        # Send a put-request to disable the pump
        if self.is_disabled != is_disabled:
            if is_disabled:
                postdata = {"operation": "disable"}
            else:
                postdata = {"operation": "enable"}

            self_link = self._connection.get_pipe_pump_url(self.pipe_id)

            post_response = self._connection.do_post_request(self_link, data=postdata)

            # check that we get a 200-response with a representation of the updated pump.
            validate_response_is_ok(post_response)
            validate_equal_case_insensitive(post_response.headers["Content-Type"], "application/json")
            self.update_raw_jsondata(post_response.text)

            # Check that the "is-disabled"-attribute has been updated
            actual_is_disabled = self.is_disabled
            if actual_is_disabled != is_disabled:
                raise AssertionError("Failed to update the 'is-disabled' setting on the pump '"
                                     "'%s'! Expected value: '%s'  Actual value: '%s'" % (self.id, is_disabled,
                                                                                         actual_is_disabled))

    def start(self, dont_wait_for_pump_to_start=False, allow_already_running_pump=True):
        """
        Starts the pump.

        :param dont_wait_for_pump_to_start: If this flag is set to True, the method will return without waiting for the
                                           pump to start running.
        :param allow_already_running_pump: If this  flag is set to False, this method will fail with a
                                           "PumpIsAlreadyRunning"-exception if if the pump was already
                                           running.
        """
        url = self._connection.get_pipe_pump_url(self.pipe_id)
        postdata = {"operation": "start"}
        if dont_wait_for_pump_to_start:
            postdata["dont-wait-for-pump-to-start"] = "true"
        response = self._connection.do_post_request(url, data=postdata)

        if response.status_code == 409:
            self.update_raw_jsondata(response.text)
            if allow_already_running_pump:
                return False
            else:
                raise PumpIsAlreadyRunning(self)

        validate_response_is_ok(response, 200)
        self.update_raw_jsondata(response.text)
        return True

    def stop(self):
        """
        Stops the pump.
        """
        self.run_operation("stop")

    def run_operation(self,
                      operation,
                      operation_parameters=None,
                      allowable_response_status_codes=frozenset([200])):
        """Runs the specified operation on the pump.
        :param operation: The operation to run.
        :param operation_parameters: A dict with operation parameters.
        :param allowable_response_status_codes: The http request status code(s) to accept (defaults to 200).
        """
        url = self._connection.get_pipe_pump_url(self.pipe_id)
        postdata = {"operation": operation}
        if operation_parameters is not None:
            postdata.update(operation_parameters)
        response = self._connection.do_post_request(url, data=postdata)
        validate_response_is_ok(response, allowable_response_status_codes=allowable_response_status_codes)
        self.update_raw_jsondata(response.text)
        return True
