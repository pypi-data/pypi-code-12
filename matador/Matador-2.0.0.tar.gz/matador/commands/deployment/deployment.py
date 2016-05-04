import logging


class DeploymentCommand(object):

    def __init__(self, *args):
        self._logger = logging.getLogger(__name__)
        self.args = args
        self._execute()

    def _execute(self):
        raise NotImplementedError
