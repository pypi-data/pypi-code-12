import glob
import importlib
import os
from .exceptions import ImportModuleErrorException


def load_commands_from_directory(project_path, package=None):
    """This is a function which loads all command files, so all
    needed files will be processed, and all commands will be loaded. The task
    of this function is to import all files with name acr_commands.py
    in project directory
    :param project_path: A path to the project
    :type project_path: string
    :param package_prefix: the prefix of the package, it needs for proper
    import_module function usage.
    An example: rit.core, that means all acr_commands.py files will be
    imported using such import path:
    rit.core.module.management.acr_commands
    :type package_prefix: string
    :returns: None
    :rtype: None
    :raises acmdrunner.exceptions.ImportModuleErrorException: in case of any
    unsuccessful import
    """
    _mod_name = 'acr_commands'
    for management_dir in glob.glob(os.path.join(
            project_path,
            '*/management')
    ):
        if not os.path.isdir(management_dir):
            continue
        management_dirs = management_dir.split(os.sep)
        module_name = '.'.join(management_dirs[-2:])
        if package:
            module_name = package + '.' + module_name + '.' + _mod_name
        else:
            module_name = module_name + '.' + _mod_name
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            raise ImportModuleErrorException(
                'Error while importing module: {}. Error: {}'.format(
                    module_name + '.' + _mod_name,
                    e
                )
            )


class Loader(object):

    @classmethod
    def load_from_directory(cls, project_path):
        """Loads tests from directory.

        :param project_path: Path to the project
        :type project_path: string
        :returns: None
        :rtype: None
        """
        load_commands_from_directory(project_path)

    @classmethod
    def load_from_package(cls, package_name):
        """Load commands from a given package

        :param package_name: A package name
        :type package_name: string
        :returns: None
        :rtype: None
        """
        package = importlib.import_module(package_name)
        project_path = os.path.dirname(package.__file__)
        load_commands_from_directory(project_path, package=package_name)
