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

import json

import logging

import jira.client

log = logging.getLogger(__name__)


jira_cache = {}
def get_existing_jira_issues(downstream, config):
    key = json.dumps(downstream)
    if not key in jira_cache:
        client = jira.client.JIRA(**config['sync2jira']['jira'])
        query = " AND ".join([
            "=".join([k, v]) for k, v in downstream.items()
        ]) + " AND resolution is null"
        results = client.search_issues(query, maxResults=500)
        # TODO -- handle pagination here...
        jira_cache[key] = results
    return jira_cache[key]


def create_jira_issue(issue, config):
    log.info("Creating %r issue for %r" % (issue.downstream, issue))
    if config['sync2jira']['testing']:
        log.info("Testing flag is true.  Skipping actual creation.")
    else:
        client = jira.client.JIRA(**config['sync2jira']['jira'])
        return client.create_issue(
            summary=issue.title,
            description=issue.url,
            project=issue.downstream['project'],
            component=issue.downstream['component'],
        )


def sync_with_jira(issue, config):
    existing_issues = get_existing_jira_issues(issue.downstream, config)
    if issue.title not in [i.fields.summary for i in existing_issues]:
        create_jira_issue(issue, config)
