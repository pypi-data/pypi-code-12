from types import FunctionType
from argparse import ArgumentParser
import inspect
import sys


class AutoArgumentParser(object):
    def __init__(self, type_to_parse):
        self.parser = ArgumentParser()
        self.type = type_to_parse

    def parse_args(self):
        actions = self._get_actions()
        parser = ArgumentParser()
        parser.add_argument('action', type=str, help='Action to perform', choices=actions)

        # no arguments provided
        if len(sys.argv) == 1:
            # will display available actions
            parser.parse_args()
            return

        package_manager = self.type()
        if len(sys.argv) > 1:
            action = sys.argv[1]
            if action not in actions:
                raise ValueError('Action {0} is not supported'.format(action))
            method = getattr(package_manager, action)
            arguments = AutoArgumentParser._get_method_arguments(method)
            for argument in arguments:
                parser.add_argument('--' + argument, type=str, required=True)
            args = parser.parse_args()
            method_params = {arg: getattr(args, arg) for arg in arguments}
            method(**method_params)

    @staticmethod
    def _get_method_arguments(method):
        return [a for a in inspect.getargspec(method).args if a != 'self']

    def _get_actions(self):
        return [x for x, y in self.type.__dict__.items() if type(y) == FunctionType and not str(x).startswith('_')]


