import traceback

from abc import abstractmethod
from cloudshell.core.action_result import ActionResult
from cloudshell.core.driver_response import DriverResponse
from cloudshell.core.driver_response_root import DriverResponseRoot
from cloudshell.networking.core.connectivity_request_helper import ConnectivityRequestDeserializer
from cloudshell.networking.operations.interfaces.connectivity_operations_interface import \
    ConnectivityOperationsInterface
import jsonpickle


class ConnectivityOperations(ConnectivityOperationsInterface):
    APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST = ['type', 'actionId',
                                                                 ('connectionParams', 'mode'),
                                                                 ('actionTarget', 'fullAddress')]

    def __init__(self):
        pass

    @property
    @abstractmethod
    def logger(self):
        pass

    def apply_connectivity_changes(self, request):
        """Handle apply connectivity changes request json, trigger add or remove vlan methods,
        get responce from them and create json response

        :param request: json with all required action to configure or remove vlans from certain port
        :return Serialized DriverResponseRoot to json
        :rtype json
        """

        if request is None or request == '':
            raise Exception('ConnectivityOperations', 'request is None or empty')

        holder = ConnectivityRequestDeserializer(jsonpickle.decode(request))

        if not holder or not hasattr(holder, 'driverRequest'):
            raise Exception('ConnectivityOperations', 'Deserialized request is None or empty')

        driver_response = DriverResponse()
        results = []
        driver_response_root = DriverResponseRoot()

        for action in holder.driverRequest.actions:
            self.logger.info('Action: ', action.__dict__)
            self._validate_request_action(action)
            action_result = ActionResult()
            action_result.type = action.type
            action_result.actionId = action.actionId
            action_result.errorMessage = None
            action_result.infoMessage = None
            action_result.updatedInterface = action.actionTarget.fullName
            if action.type == 'setVlan':
                qnq = False
                ctag = ''
                for attribute in action.connectionParams.vlanServiceAttributes:
                    if attribute.attributeName.lower() == 'qnq':
                        request_qnq = attribute.attributeValue
                        if request_qnq.lower() == 'true':
                            qnq = True
                    elif attribute.attributeName.lower() == 'ctag':
                        ctag = attribute.attributeValue
                try:
                    action_result.infoMessage = self.add_vlan(action.connectionParams.vlanId,
                                                              action.actionTarget.fullAddress,
                                                              action.connectionParams.mode.lower(),
                                                              qnq,
                                                              ctag)
                except Exception as e:
                    self.logger.error('Add vlan failed: {0}'.format(traceback.format_exc()))
                    action_result.errorMessage = ', '.join(map(str, e.args))
                    action_result.success = False
            elif action.type == 'removeVlan':
                try:
                    action_result.infoMessage = self.remove_vlan(action.connectionParams.vlanId,
                                                                 action.actionTarget.fullAddress,
                                                                 action.connectionParams.mode.lower())
                except Exception as e:
                    self.logger.error('Remove vlan failed: {0}'.format(traceback.format_exc()))
                    action_result.errorMessage = ', '.join(map(str, e.args))
                    action_result.success = False
            else:
                continue
            results.append(action_result)

        driver_response.actionResults = results
        driver_response_root.driverResponse = driver_response
        return self.set_command_result(driver_response_root).replace('[true]', 'true')

    def _validate_request_action(self, action):
        """Validate action from the request json, according to APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST

        """
        is_fail = False
        fail_attribute = ''
        for class_attribute in self.APPLY_CONNECTIVITY_CHANGES_ACTION_REQUIRED_ATTRIBUTE_LIST:
            if type(class_attribute) is tuple:
                if not hasattr(action, class_attribute[0]):
                    is_fail = True
                    fail_attribute = class_attribute[0]
                if not hasattr(getattr(action, class_attribute[0]), class_attribute[1]):
                    is_fail = True
                    fail_attribute = class_attribute[1]
            else:
                if not hasattr(action, class_attribute):
                    is_fail = True
                    fail_attribute = class_attribute

        if is_fail:
            raise Exception('ConnectivityOperations',
                            'Mandatory field {0} is missing in ApplyConnectivityChanges request json'.format(
                                fail_attribute))

    def set_command_result(self, result, unpicklable=False):
        """Serializes output as JSON and writes it to console output wrapped with special prefix and suffix

        :param result: Result to return
        :param unpicklable: If True adds JSON can be deserialized as real object.
                            When False will be deserialized as dictionary
        """

        json = jsonpickle.encode(result, unpicklable=unpicklable)
        result_for_output = str(json)
        return result_for_output

    @abstractmethod
    def add_vlan(self, vlan_range, port_list, port_mode, qnq, ctag):
        pass

    @abstractmethod
    def remove_vlan(self, vlan_range, port_list, port_mode):
        pass
