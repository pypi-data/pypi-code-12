import argparse
import os
import typing
import logging

import requests
import subprocess

import sys

"""The Github cloner"""

API_GITHUB_COM = 'https://api.github.com'

from statsbiblioteket.github_cloner.myTypes import *


class BraceMessage(object):
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.fmt.format(*self.args, **self.kwargs)


class DollarMessage(object):
    def __init__(self, fmt, **kwargs):
        self.fmt = fmt
        self.kwargs = kwargs

    def __str__(self):
        from string import Template
        return Template(self.fmt).substitute(**self.kwargs)


M = BraceMessage


def get_github_repositories(githubName: str,
                            user_type: UserType,
                            repo_type: RepoType,
                            batch_size: int = 100) -> typing.List[Repository]:
    """
    Format of the JSON is documented at
     http://developer.github.com/v3/repos/#list-organization-repositories

    Supports batching (which Github indicates by the presence of a Link header,
    e.g. ::

        Link: <https://api.github.com/resource?page=2>; rel="next",
              <https://api.github.com/resource?page=5>; rel="last"

    """
    # API documented at http://developer.github.com/v3/#pagination
    githubUrl = '{github}/{userType}/{name}/{repoType}'.format(
        github=API_GITHUB_COM, userType=user_type.value, name=githubName,
        repoType=repo_type.value)

    r = requests.get(githubUrl, params={"per_page": batch_size})
    repositories = r.json()
    logging.debug(M('Found {0} repositories on github', len(repositories)))

    page = 1
    while 'rel="next"' in r.headers.get('Link', ''):
        logging.debug(M('More repositories to be had'))
        page += 1
        r = requests.get(githubUrl, params={"page": page, "per_page":
            batch_size})
        repositories += r.json()
        logging.debug(M('We now have {0} repositories', len(repositories)))
    result = parse_github_repositories(repositories, repo_type)

    return result


def parse_github_repositories(repositories: dict, repo_type: RepoType) -> \
        typing.List[Repository]:
    """
    Parse the github repositories into our Repository objects

    :param repositories: a dict of the github json for repositories
    :param repo_type: enum denoting real Repos or Gists
    :return: A list of Repository objects
    """

    def _get_repository_url(repository: dict):
        if repo_type is RepoType.GIST:
            return repository['git_pull_url']
        else:
            return repository['ssh_url']

    def _get_repository_name(repository: dict):
        if repo_type is RepoType.GIST:
            return repository['id']
        else:
            return repository['name']

    result = [Repository(name=_get_repository_name(repository),
                         description=repository[
                                         'description'] or "(no description)",
                         url=_get_repository_url(repository)) for
              repository in repositories]
    return result


def fetchOrClone(git_url: Url, repository_path: Path):
    """
    If the repository already exists, perform a fetch. Otherwise perform a
    clone.
    The repository is cloned 'bare' i.e. with the --mirror flag

    :param git_url: The git url to clone/fetch from
    :param repository_path: The path to clone the repository to
    :returns: None
    :raises subprocess.CalledProcessError: If any of the git processes failed
    """
    abspath = os.path.abspath(repository_path)

    should_fetch = os.path.isdir(repository_path)

    if should_fetch:
        logging.info(M('Fetching updates to repository {0}', repository_path))
        remote = 'git -C {abspath} remote set-url origin {git_url}'.format(
            abspath=abspath, git_url=git_url)
        output = subprocess.check_output(remote.split(),
                                         stderr=subprocess.STDOUT)
        logging.debug(
            M('Running command "{0}"', remote))

        fetch = 'git -C {abspath} --bare fetch --all'.format(
            abspath=abspath)
        output = subprocess.check_output(fetch.split(),
                                         stderr=subprocess.STDOUT)
        logging.debug(
            M('Running command "{0}"\n{1}', fetch, output.decode("utf-8")))
    else:
        logging.info(M('Cloning repository {0}', repository_path))
        os.makedirs(abspath, exist_ok=True)

        clone = 'git -C {abspath} clone --mirror {git_url} .'.format(
            abspath=abspath, git_url=git_url)
        output = subprocess.check_output(clone.split(),
                                         stderr=subprocess.STDOUT)
        logging.debug(
            M('Running command "{0}"\n{1}', clone, output.decode("utf-8")))


def githubBackup(githubName: str,
                 user_type: UserType = UserType.USER,
                 repo_type: RepoType = RepoType.REPO):
    """
    Backup all repositories from a specific user/org on github to current
    working dir

    :param githubName: The name of the organisation/user on github
    :param user_type: enum USER or ORG
    :param repo_type: enum REPO or GIST
    :return: None
    :raises CalledProcessError: If any of the git processes failed
    """
    repositories = get_github_repositories(githubName, user_type, repo_type)
    for repository in repositories:
        fetchOrClone(repository.url, repository.name + '.git')



def create_parser():
    parser = argparse.ArgumentParser(
        description='Clones github repositories and github gists')
    parser.add_argument('--org', action='append',
                        help='The github organisation to backup', dest='orgs')
    parser.add_argument('--user', action='append',
                        help='The github user to backup', dest='users')
    parser.add_argument('--logLevel', default='DEBUG',
                        help='the log level', dest='loglevel')
    parser.add_argument('--logFile', default='log.log',
                        help='the log file', dest='logfile')
    return parser


def main():
    """
    Parse command line args and backup the github repos

    :param argv: the command line arguments
    :return: None
    """
    parser = create_parser()

    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.logfile, level=getattr(logging,
                                                             args.loglevel.upper()))

    for org in args.orgs or []:
        for repoType in RepoType:
            githubBackup(githubName=org, user_type=UserType.ORG,
                         repo_type=repoType)
    for user in args.users or []:
        for repoType in RepoType:
            githubBackup(githubName=user, user_type=UserType.USER,
                         repo_type=repoType)

    logging.shutdown()

# action
if __name__ == '__main__':
    main()
