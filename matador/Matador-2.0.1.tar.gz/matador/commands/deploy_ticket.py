#!/usr/bin/env python
from .command import Command
from matador.commands.deployment import *
from matador.session import Session
from matador import git
from pathlib import Path
import shutil
from importlib.machinery import SourceFileLoader


def _checkout_ticket(ticket, repo, ticket_folder, commit):
    git.checkout(repo, commit)
    src = Path(repo.path, 'deploy', 'tickets', ticket)
    shutil.rmtree(str(ticket_folder), ignore_errors=True)
    shutil.copytree(str(src), str(ticket_folder))


def execute_ticket(ticket, action, commit, packaged=False):
    ticket_folder = Path(Session.matador_tickets_folder, ticket)
    Session.deployment_folder = ticket_folder

    shutil.rmtree(str(ticket_folder), ignore_errors=True)

    if not packaged:
        Session.update_repository()

    _checkout_ticket(ticket, Session.matador_repo, ticket_folder, commit)

    actionFile = Path(action + '.py')
    sourceFile = Path(ticket_folder, actionFile)
    SourceFileLoader(action, str(sourceFile)).load_module()


class ActionTicket(Command):
    action = 'None'

    def _add_arguments(self, parser):
        parser.prog = 'matador deploy-ticket'
        parser.add_argument(
            '-e', '--environment',
            type=str,
            required=True,
            help='Agresso environment name')

        parser.add_argument(
            '-t', '--ticket',
            type=str,
            required=True,
            help='Ticket name')

        parser.add_argument(
            '-c', '--commit',
            type=str,
            default='none',
            help='Commit or tag ID')

        parser.add_argument(
            '-p', '--packaged',
            type=bool,
            default=False,
            help='Whether this deployment is part of a package')

    def _execute(self):
        Session.set_environment(self.args.environment)
        if self.args.commit == 'none':
            commit = Session.project_repo.head().decode(encoding='ascii')
        else:
            commit = self.args.commit
        execute_ticket(self.args.ticket, self.action, commit, False)


class DeployTicket(ActionTicket):
    action = 'deploy'


class RemoveTicket(ActionTicket):
    action = 'remove'
