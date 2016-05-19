# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import sys

import click

from .main import hatcher
from .utils import add_arguments, pass_organization, pass_team


def team_arguments(fn):
    return add_arguments(fn, 'organization', 'team')


@hatcher.group('teams', api_versions=[0, 1])
def teams():
    """Perform operations on a team.
    """


@teams.group('repositories', api_versions=[0, 1])
def repositories():
    """Perform operations on repositories to which a team has access.
    """


@teams.group('members', api_versions=[0, 1])
def members():
    """Perform operations on members of a team.
    """


@teams.command('list', api_versions=[0, 1])
@click.argument('organization')
@pass_organization
def list_teams(organization):
    """List all teams in an organization.
    """
    for team in sorted(organization.list_teams(), key=lambda t: t['name']):
        print(team['name'])


@teams.command('create', api_versions=[0, 1])
@team_arguments
@click.argument('group')
@pass_organization
def create_team(organization, team, group):
    """Create a new team.
    """
    organization.create_team(team, group)


@teams.command('delete', api_versions=[0, 1])
@team_arguments
@pass_team
def delete_team(team):
    """Delete a team.
    """
    team.delete()


@teams.command('metadata', api_versions=[0, 1])
@team_arguments
@pass_team
def team_metadata(team):
    """Get a team's metadata.
    """
    print(team.metadata())


@repositories.command('list', api_versions=[0, 1])
@team_arguments
@pass_team
def list_team_repositories(team):
    """List all repositories to which this team has access.
    """
    for repository in team.list_repositories():
        print(repository)


@repositories.command('add', api_versions=[0, 1])
@team_arguments
@click.argument('repository')
@pass_organization
def add_repository_to_team(organization, team, repository):
    """Add access to a repository from a team.
    """
    team = organization.team(team)
    repository = organization.repository(repository)
    team.add_repository(repository)


@repositories.command('remove', api_versions=[0, 1])
@team_arguments
@click.argument('repository')
@pass_organization
def remove_repository_from_team(organization, team, repository):
    """Remove access to a repository from a team.
    """
    team = organization.team(team)
    repository = organization.repository(repository)
    team.remove_repository(repository)


@repositories.command('query', api_versions=[0, 1])
@team_arguments
@click.argument('repository')
@pass_organization
def query_team_repository_access(organization, team, repository):
    """Query if a team has access to a repository.
    """
    team = organization.team(team)
    repository = organization.repository(repository)
    has_access = team.query_repository_access(repository)
    if has_access:
        print('{0!r} has access to {1!r}'.format(team.name, repository.name))
    else:
        print('{0!r} does not have access to {1!r}'.format(
            team.name, repository.name))
        sys.exit(1)


@members.command('list', api_versions=[0, 1])
@team_arguments
@pass_team
def list_team_members(team):
    """List members of a team.
    """
    for user in team.list_users():
        print(user)


@members.command('add', api_versions=[0, 1])
@team_arguments
@click.argument('email')
@pass_organization
def add_user_to_team(organization, team, email):
    """Add a user to a team.
    """
    team = organization.team(team)
    user = organization.user(email)
    team.add_user(user)


@members.command('remove', api_versions=[0, 1])
@team_arguments
@click.argument('email')
@pass_organization
def remove_user_from_team(organization, team, email):
    """Remove a user to a team.
    """
    team = organization.team(team)
    user = organization.user(email)
    team.remove_user(user)


@members.command('query', api_versions=[0, 1])
@team_arguments
@click.argument('email')
@pass_organization
def query_team_user_access(organization, team, email):
    """Query if a user is a member of a team.
    """
    team = organization.team(team)
    user = organization.user(email)
    has_access = team.query_user_access(user)
    if has_access:
        print('{0!r} has access to {1!r}'.format(user.email, team.name))
    else:
        print('{0!r} does not have access to {1!r}'.format(
            user.email, team.name))
        sys.exit(1)
