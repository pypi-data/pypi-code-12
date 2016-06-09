#!/usr/bin/env python3

from __future__ import print_function

import requests
import subprocess
import json
import re
try:
    from urllib.parse import urljoin
except ImportError:  # python2
    from urlparse import urljoin
from autoauth import Authenticate

OPEN = 'OPEN'
LOGFRMT = '%s'


def execute(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    return p.stdout.read().decode('utf-8').strip('\n')


def config(key):
    return execute(['git', 'config', '--get', key])


def find_url():
    g = re.search('git@([^:]*):', config('remote.origin.url'))
    return 'https://' + g.group(1)


def find_repository():
    return config('remote.origin.url').split('/')[-1].rsplit('.', 1)[0]


def find_branch():
    return execute(['git', 'symbolic-ref', 'HEAD'])


def find_username():
    return config('user.email').split('@')[0]


def find_description(frm, to):
    return to


def find_project():
    return config('remote.origin.url').split('/')[-2]


class PullRequest(object):
    def __init__(self, project, repository, onto, branch, state,
                 title=None, description=None, reviewers=None):
        self.project = project
        self.repository = repository
        self.onto = onto
        self.branch = branch
        self.state = state
        self.title = title or re.sub('^refs/heads/', '', branch)
        self.description = description or find_description(onto, branch)
        self.reviewers = reviewers or []


def submit_pull_request(url, auth, request, debug=False):
    def mkref(name):
        return {
            'id': name if '/' in name else 'refs/heads/%s' % name,
            'repository': {
                'slug': request.repository,
                'name': request.repository,
                'project': {'key': request.project}
            }
        }

    data = {
        'title': request.title,
        'description': request.description,
        'state': request.state,
        'open': request.state == OPEN,
        'closed': request.state != OPEN,
        'fromRef': mkref(request.branch),
        'toRef': mkref(request.onto),
        'reviewers': [{'user': {'name': name}} for name in request.reviewers]
    }

    frmt = '/rest/api/1.0/projects/%s/repos/%s/pull-requests'
    api = urljoin(url, frmt % (request.project, request.repository))

    if debug:
        print(json.dumps(data, indent=4, sort_keys=True))

    r = requests.post(api,
                      auth=auth.credentials,
                      headers={
                          'content-type': 'application/json',
                          'accept': 'application/json'
                      },
                      data=json.dumps(data),
                      verify=False)
    return r.json()


def main():
    import argparse
    parser = argparse.ArgumentParser('pull-request')
    parser.add_argument('branch', nargs='?')
    parser.add_argument('--on-to', default='master')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--update')
    parser.add_argument('--title')
    parser.add_argument('--description')
    parser.add_argument('--project')
    parser.add_argument('--repository')
    parser.add_argument('--url')
    parser.add_argument('--username',
                        metavar='USERNAME',
                        help='stash username')
    parser.add_argument('--password',
                        metavar='PASSWORD',
                        help='stash password')

    reviewers_group = parser.add_mutually_exclusive_group()
    reviewers_group.add_argument('--reviewer', action='append')
    reviewers_group.add_argument('--reviewers', type=lambda s: s.split(','))

    args = parser.parse_args()

    url = args.url or find_url()
    repository = args.repository or find_repository()
    project = args.project or find_project()
    branch = args.branch or find_branch()
    reviewers = args.reviewer or args.reviewers

    pr = PullRequest(project=project,
                     repository=repository,
                     onto=args.on_to,
                     branch=branch,
                     state=OPEN,
                     title=args.title,
                     description=args.description,
                     reviewers=reviewers)

    username = args.username or find_username()
    auth = Authenticate('stash-pull-request', username, args.password)
    auth.get_credentials()

    data = submit_pull_request(url, auth, pr, args.debug)

    if args.debug:
        print(json.dumps(data, indent=4, sort_keys=True))

    if 'errors' in data:
        for err in data['errors']:
            print(err['message'])
            try:
                epr = err['existingPullRequest']
            except KeyError:
                pass
            else:
                try:
                    link = epr['link']
                except KeyError:
                    print(epr['links']['self'][0]['href'])
                else:
                    print(urljoin(url, link['url']))

    if 'links' in data:
        print(data['links']['self'][0]['href'])

    if 'link' in data:
        print(urljoin(url, data['link']['url']))

if __name__ == '__main__':
    main()
