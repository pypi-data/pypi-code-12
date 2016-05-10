# This file is part of sync2jira.
# Copyright (C) 2016 Red Hat, Inc.
#
# sync2jira is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# sync2jira is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with sync2jira; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110.15.0 USA
#
# Authors:  Ralph Bean <rbean@redhat.com>


import logging

import requests

import sync2jira.intermediary as i


log = logging.getLogger(__name__)


def handle_github_message(msg, config):
    owner = msg['msg']['repository']['owner']['login']
    repo = msg['msg']['repository']['name']
    upstream = '{owner}/{repo}'.format(owner=owner, repo=repo)
    mapped_repos = config['sync2jira']['map']['github']
    if upstream not in mapped_repos:
        log.info("%r not in github map: %r" % (upstream, mapped_repos.keys()))
        return None
    return i.Issue.from_github(upstream, msg['msg']['issue'], config)


def handle_pagure_message(msg, config):
    upstream = msg['msg']['project']['name']
    mapped_repos = config['sync2jira']['map']['pagure']
    if upstream not in mapped_repos:
        log.info("%r not in pagure map: %r" % (upstream, mapped_repos.keys()))
        return None
    return i.Issue.from_pagure(upstream, msg['msg']['issue'], config)


def pagure_issues(upstream, config):
    base = config['sync2jira'].get('pagure_url', 'https://pagure.io')
    url = base + '/api/0/' + upstream + '/issues'

    params = dict(status='Open')

    response = requests.get(url, params=params)
    data = response.json()['issues']
    issues = (i.Issue.from_pagure(upstream, issue, config) for issue in data)
    for issue in issues:
        yield issue


def github_issues(upstream, config):
    url = 'https://api.github.com/repos/%s/issues' % upstream

    headers = {}
    token = config['sync2jira'].get('github_token')
    if not token:
        log.warning('No github_token found.  We will be rate-limited...')
    else:
        headers['Authorization'] = 'token ' + token

    params = dict(per_page=100, state='open')

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    issues = (
        i.Issue.from_github(upstream, issue, config) for issue in data
        if not 'pull_request' in issue  # We don't want to copy these around
    )
    for issue in issues:
        yield issue
