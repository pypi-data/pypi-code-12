
__author__ = 'shms'

import threading
from cisco_nxos_resource_driver import CiscoNXOSDriver
from cloudshell.shell.core.context.context import ResourceCommandContext, ResourceContextDetails, \
    ReservationContextDetails

class DriverCommandExecution(threading.Thread):
    def __init__(self, driver_instance, command_name, parameters_name_value_map):
        threading.Thread.__init__(self)

        self._parameters_name_value_map = parameters_name_value_map
        self._driver_instance = driver_instance
        self._command_name = command_name
        # self._cancellation_context = CancellationContext()

    def run(self):
        self._result = self._driver_instance.invoke_func(self._command_name,
                                                         self._parameters_name_value_map)

    def set_cancellation_context(self):
        # self._cancellation_context.is_cancelled = True
        pass

    def get_result(self):
        return self._result


class DriverWrapper:
    def __init__(self, obj):
        self.instance = obj

    def invoke_func(self, command_name, params):
        func = getattr(self.instance, command_name)

        return func(**params)

tt = CiscoNXOSDriver()

context = ResourceCommandContext()
context.resource = ResourceContextDetails()
context.resource.name = 'dsada'
context.reservation = ReservationContextDetails()
context.reservation.reservation_id = 'test_id'
context.resource.attributes = {}
context.resource.attributes['User'] = 'root'
context.resource.attributes['Password'] = 'Password1'
context.resource.address = '192.168.42.235'

threading.Thread(target=tt.send_custom_command, args=[context, 'kuku']).start()
# tt.send_custom_command(context, 'kuku')
# tt.get_inventory(context)