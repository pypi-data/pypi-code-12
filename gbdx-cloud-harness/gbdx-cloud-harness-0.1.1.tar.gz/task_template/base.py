"""
cloud-harness Application Template
"""
import json
import os
from gbdx_task_interface import GbdxTaskInterface


class TaskTemplate(GbdxTaskInterface):
    """ Base Class for custom tasks written for GBDX CLI.
    """
    task = None
    __verbose_stdout = False

    def __init__(self, **arguments):

        self.__task_def_json = ''

        self.__verbose_stdout = arguments.get('verbose')

        remote_work_path = os.environ.get('REMOTE_WORK_PATH', None)
        if remote_work_path is not None:
            self.__work_path = remote_work_path
            self.__remote_run = True
        else:
            self.__work_path = os.getcwd()
            self.__remote_run = False

        self.__src_path = None

        super(TaskTemplate, self).__init__(self.__work_path)

    @property
    def src_path(self):
        return self.__src_path

    @property
    def task_json(self):
        return self.__task_def_json

    def finalize(self, success_or_fail, message=''):
        """
        :param success_or_fail: string that is 'success' or 'fail'
        :param message:
        """
        if not self.__remote_run:
            return json.dumps({'status': success_or_fail, 'reason': message}, indent=4)
        else:
            super(TaskTemplate, self).finalize(success_or_fail, message)

    def __enter__(self):

        self.__src_path = self.task.src_path

        # Store json in memory
        self.__task_def_json = self.task.json()

        if self.__verbose_stdout:
            print self.__task_def_json

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print self.finalize('failed', str(exc_val))
        else:
            # Write output ports to ports.json
            input_ports, output_ports = self.task.ports
            for port in output_ports:
                if port.port_type == 'string':
                    self.set_output_string_port(port.name, port.value)

            print self.finalize('success', self._reason)
