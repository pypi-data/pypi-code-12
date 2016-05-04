from .command import Command
from matador.session import Session
import win32serviceutil as win32


class ActionService(Command):

    def _is_running(self, label, name, with_logging=False):
        if win32.QueryServiceStatus(name, machine=self.server)[1] == 4:
            message = ('%s - Running on %s' % (label, self.args.environment))
            running = True
        else:
            message = (
                '%s - Not Running on %s' % (label, self.args.environment))
            running = False

        if with_logging:
            self._logger.info(message)

        return running

    def _add_arguments(self, parser):
        parser.prog = 'matador start/stop-services'
        parser.add_argument(
            '-e', '--environment',
            type=str,
            required=True,
            help='Agresso environment name')

        parser.add_argument(
            '-s', '--service',
            type=str,
            default='all',
            help='Agresso service label')

    def _execute(self):
        self.server = Session.environments[self.args.environment]['abwServer']
        self.services = Session.environments[self.args.environment]['services']


class StartService(ActionService):

    def _start(self, label, name):
        if not self._is_running(label, name):
            win32.StartService(name, machine=self.server)
            self._is_running(
                self.args.service,
                self.services[self.args.service],
                True)
        else:
            self._logger.info(
                'Cannot start %s on %s - It is already running' %
                (label, self.args.environment))

    def _execute(self):
        super(StartService, self)._execute()
        if self.args.service == 'all':
            for label, name in self.services.items():
                self._start(label, name)
        else:
            self._start(self.args.service, self.services[self.args.service])


class StopService(ActionService):

    def _stop(self, label, name):
        if self._is_running(label, name):
            win32.StopService(name, machine=self.server)
            self._is_running(
                self.args.service,
                self.services[self.args.service],
                True)
        else:
            self._logger.info(
                'Cannot stop %s on %s - It is not currently running' %
                (label, self.args.environment))

    def _execute(self):
        super(StopService, self)._execute()
        if self.args.service == 'all':
            for label, name in self.services.items():
                self._stop(label, name)
        else:
            self._stop(self.args.service, self.services[self.args.service])


class RestartService(ActionService):

    def _restart(self, label, name):
        if self._is_running(label, name):
            win32.RestartService(name, machine=self.server)
            self._is_running(
                self.args.service,
                self.services[self.args.service],
                True)
        else:
            self._logger.info(
                'Cannot restart %s on %s - It is not currently running' %
                (label, self.args.environment))

    def _execute(self):
        super(RestartService, self)._execute()
        if self.args.service == 'all':
            for label, name in self.services.items():
                self._restart(label, name)
        else:
            self._restart(self.args.service, self.services[self.args.service])


class ServiceStatus(ActionService):

    def _execute(self):
        super(ServiceStatus, self)._execute()
        if self.args.service == 'all':
            for label, name in self.services.items():
                self._is_running(label, name, True)
        else:
            self._is_running(
                self.args.service,
                self.services[self.args.service],
                True)
