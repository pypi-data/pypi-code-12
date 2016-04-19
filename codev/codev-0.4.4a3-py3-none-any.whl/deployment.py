from logging import getLogger
from .provisioner import Provisioner
from .performer import BaseProxyExecutor, CommandError

logger = getLogger(__name__)


class Deployment(BaseProxyExecutor):
    def __init__(self, performer, settings):
        super().__init__(performer)
        self.provisioner = Provisioner(settings.provider, performer, settings_data=settings.specific)
        self.scripts = settings.scripts

    def _onerror(self, arguments, error):
        logger.error(error)
        arguments.update(
            dict(
                command=error.command,
                exit_code=error.exit_code,
                error=error.error
            )
        )
        self.run_scripts(self.scripts.onerror, arguments)

    def deploy(self, infrastructure, script_info):
        self.run_scripts(self.scripts.onstart, script_info)
        try:
            logger.info('Installing provisioner...')
            self.provisioner.install()

            logger.info('Creating machines...')
            infrastructure.create()

            logger.info('Configuration...')
            self.provisioner.run(infrastructure, script_info)
        except CommandError as e:
            self._onerror(script_info, e)
            return False
        else:
            try:
                arguments = {}
                arguments.update(script_info)
                arguments.update(infrastructure.machines_info())
                self.run_scripts(self.scripts.onsuccess, arguments)
                return True
            except CommandError as e:
                self._onerror(script_info, e)
                return False