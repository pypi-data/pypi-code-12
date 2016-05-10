"""A collection of juju-core environment watchers."""

from __future__ import absolute_import
from jujuclient import WatchWrapper

from ..utils import ErrorExit

# _status_map provides a translation of Juju 2 status codes to the closest
# Juju 1 equivalent. Only defines codes that need translation.
_status_map = {'idle': 'started'}


class WaitForMachineTermination(WatchWrapper):
    """Wait until the given machines are terminated."""

    def __init__(self, watch, machines):
        super(WaitForMachineTermination, self).__init__(watch)
        self.machines = set(machines)
        self.known = set()

    def process(self, entity_type, change, data):
        if entity_type != 'machine':
            return
        if change == 'remove' and data['Id'] in self.machines:
            self.machines.remove(data['Id'])
        else:
            self.known.add(data['Id'])

    def complete(self):
        for m in self.machines:
            if m in self.known:
                return False
        return True


class WaitForUnits(WatchWrapper):
    """Wait for units of the environment to reach a particular goal state.

    If services are provided, only consider the units belonging to the given
    services.
    If the on_errors callable is provided, call the given function each time a
    change set is processed and a new unit is found in an error state. The
    callable is called passing a list of units' data corresponding to the units
    in an error state.
    """
    def __init__(
            self, watch, goal_state='started', services=None, on_errors=None):
        super(WaitForUnits, self).__init__(watch)
        self.goal_state = goal_state
        self.services = services
        self.on_errors = on_errors
        # The units dict maps unit names to units data.
        self.units = {}
        # The units_in_error list contains the names of the units in error.
        self.units_in_error = []

    def process(self, entity, action, data):
        if entity != 'unit':
            return
        if (self.services is None) or (data['Service'] in self.services):
            unit_name = data['Name']
            if action == 'remove' and unit_name in self.units:
                del self.units[unit_name]
            else:
                self.units[unit_name] = data

    def complete(self):
        ready = True
        new_errors = []
        goal_state = self.goal_state
        on_errors = self.on_errors
        units_in_error = self.units_in_error
        for unit_name, data in self.units.items():
            try:
                status = data['Status']
            except KeyError:
                # 'Status' has been removed from newer versions of Juju.
                # Respond with the closest status parameter, translating it
                # through the _status_map. If the status value is not in
                # _status_map, just use the original value.
                status = data['JujuStatus']['Current']
                status = _status_map.get(status, status)
            if status == 'error':
                if unit_name not in units_in_error:
                    units_in_error.append(unit_name)
                    new_errors.append(data)
            elif status != goal_state:
                ready = False
        if new_errors and goal_state != 'removed' and callable(on_errors):
            on_errors(new_errors)
        return ready


def log_on_errors(env):
    """Return a function receiving errors and logging them.

    The resulting function is suitable to be used as the on_errors callback
    for WaitForUnits (see above).
    """
    return env.log_errors


def exit_on_errors(env):
    """Return a function receiving errors, logging them and exiting the app.

    The resulting function is suitable to be used as the on_errors callback
    for WaitForUnits (see above).
    """
    def callback(errors):
        log_on_errors(env)(errors)
        raise ErrorExit()
    return callback


def raise_on_errors(exception):
    """Return a function receiving errors and raising the given exception.

    The resulting function is suitable to be used as the on_errors callback
    for WaitForUnits (see above).
    """
    def callback(errors):
        raise exception(errors)
    return callback
