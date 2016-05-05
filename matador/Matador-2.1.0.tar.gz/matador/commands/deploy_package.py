#!/usr/bin/env python
from .command import Command
from .deploy_ticket import execute_ticket
from matador.session import Session
from matador import git
from pathlib import Path
import shutil
import yaml
from importlib.machinery import SourceFileLoader


class ActionPackage(Command):

    def _add_arguments(self, parser):
        parser.prog = 'matador deploy-package'
        parser.add_argument(
            '-e', '--environment',
            type=str,
            required=True,
            help='Agresso environment name')

        parser.add_argument(
            '-p', '--package',
            type=str,
            required=True,
            help='Package name')

        parser.add_argument(
            '-c', '--commit',
            type=str,
            default='none',
            help='Commit or tag ID')

    @staticmethod
    def _checkout_package(package, commit):
        repo_folder = Session.matador_repository_folder
        package_folder = Path(
            Session.matador_packages_folder, package)

        shutil.rmtree(str(package_folder), ignore_errors=True)

        Session.update_repository()

        git.checkout(Session.matador_repo, commit)

        src = Path(repo_folder, 'deploy', 'packages', package)
        shutil.copytree(str(src), str(package_folder))

    def _execute(self):
        Session.set_environment(self.args.environment)
        if self.args.commit == 'none':
            commit = None
        else:
            commit = self.args.commit
        self._checkout_package(self.args.package, commit)


class DeployPackage(ActionPackage):

    def _execute(self):
        super(DeployPackage, self)._execute()
        if self.args.commit == 'none':
            commit = None
        else:
            commit = self.args.commit
        package_folder = Path(
            Session.matador_packages_folder, self.args.package)
        Session.deployment_folder = package_folder
        ticketsFile = Path(package_folder, 'tickets.yml')

        file = ticketsFile.open('r')
        tickets = yaml.load(file)
        for ticket in tickets:
            self._logger.info('*' * 25)
            self._logger.info('Deploying ticket %s' % ticket)
            self._logger.info('*' * 25)
            execute_ticket(str(ticket), 'deploy', commit, True)


class RemovePackage(ActionPackage):

    def _execute(self):
        super(RemovePackage, self)._execute()
        package_folder = Path(
            Session.matador_packages_folder, self.args.package)
        Session.deployment_folder = package_folder
        sourceFile = Path(package_folder, 'remove.py')

        SourceFileLoader('remove', str(sourceFile)).load_module()
