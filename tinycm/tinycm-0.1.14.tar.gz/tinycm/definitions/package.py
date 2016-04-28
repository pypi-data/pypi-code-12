from tinycm.basedefinition import BaseDefinition
import subprocess
import distro
import logging

logger = None


class PackageDefinition(BaseDefinition):
    def init(self, ensure, packagemanager='autodetect'):
        self.ensure = ensure
        self.packagemanager = packagemanager

        global logger
        logger = logging.getLogger('tinycm')

    def try_merge(self, other):
        self.ensure = self.merge_if_same('ensure', other)
        self.packagemanager = self.merge_if_same('packagemanager', other, 'autodetect')
        return self

    def get_system_state(self):
        result = {
            'installed': self._pm_check()
        }
        return result

    def get_config_state(self):
        return {
            'installed': self.ensure == 'installed'
        }

    def update_state(self, state_diff):
        if self.ensure == 'installed':
            self._pm_install()
        else:
            self._pm_remove()

    def _pm_check(self):
        if self.packagemanager == 'autodetect':
            current_distro = distro.identify()
            command_template = current_distro.command['package']['is-installed']
        elif self.packagemanager == 'apt':
            command_template = 'dpkg -s {}'
        elif self.packagemanager == 'pacman':
            command_template = 'pacman -Q {}'
        else:
            raise NotImplementedError()

        try:
            subprocess.check_output(command_template.format(self.name), shell=True, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def _pm_install(self):
        if self.packagemanager == 'autodetect':
            current_distro = distro.identify()
            command_template = current_distro.command['package']['install']
        elif self.packagemanager == 'apt':
            command_template = 'apt-get -y install --no-install-recommends {}'
        elif self.packagemanager == 'pacman':
            command_template = 'pacman -S --noconfirm {}'
        else:
            raise NotImplementedError()
        command = command_template.format(self.name)
        logger.info("Executing: {}".format(command))
        subprocess.check_call(command, shell=True, stderr=subprocess.STDOUT)

    def _pm_remove(self):
        if self.packagemanager == 'autodetect':
            current_distro = distro.identify()
            command_template = current_distro.command['package']['purge']
        elif self.packagemanager == 'apt':
            command_template = 'apt-get -y remove {}'
        elif self.packagemanager == 'pacman':
            command_template = 'pacman -Rs --noconfirm {}'
        else:
            raise NotImplementedError()

        command = command_template.format(self.name)
        logger.info("Executing: {}".format(command))
        subprocess.check_call(command, shell=True, stderr=subprocess.STDOUT)
