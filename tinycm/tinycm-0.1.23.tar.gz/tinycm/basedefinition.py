from tinycm import DefinitionConflictError
import json


class BaseDefinition(object):
    def __init__(self, identifier, parameters, source, after, context):
        self.identifier = identifier
        self.parameters = parameters
        self.source = source
        self.after = after
        self.context = context
        self.name = parameters['name']

        if hasattr(self, 'init'):
            parameters_pass = {}
            for key in parameters:
                new_key = key.replace('-', '_')
                if key != 'name':
                    parameters_pass[new_key] = parameters[key]
            self.init(**parameters_pass)

    def __repr__(self):
        return '<{}>'.format(self.identifier)

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def get_unique_data(self):
        return self.identifier + json.dumps(self.parameters)

    def merge_if_same(self, key, other, none_value=None):
        self_val = getattr(self, key)
        other_val = getattr(other, key)
        if self_val == other_val:
            return key
        if self_val == none_value and other_val == none_value:
            return none_value
        if self_val == none_value:
            return other_val
        if other_val == none_value:
            return self_val
        raise DefinitionConflictError('Duplicate definition "{}" for {}'.format(key, self.identifier))
