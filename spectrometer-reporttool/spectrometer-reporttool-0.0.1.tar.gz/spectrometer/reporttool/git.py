# -*- coding: utf-8 -*-

# @License EPL-1.0 <http://spdx.org/licenses/EPL-1.0>
##############################################################################
# Copyright (c) 2016 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

import datetime
from dateutil import tz
from collections import Counter
from collections import OrderedDict
import urllib

import requests
from tabulate import tabulate


class GitReport():
    def __init__(self, server_url, ref1, ref2):
        self.server_url = server_url
        self.ref1 = ref1
        self.ref2 = ref2
        self.fetch_data()

    def fetch_data(self):
        print('Fetching GitReport data...')
        url = urllib.parse.urljoin(self.server_url, 'gerrit/projects')
        projects = requests.get(url).json().get('projects')

        # Remove Gerrit special repos
        if 'All-Users' in projects:
            projects.remove('All-Users')

        self.commits = []
        project_data = {}
        self.tz_data = {}
        for project in projects:
            url = urllib.parse.urljoin(
                self.server_url,
                'git/commits_since_ref?project={0}&ref1={1}&ref2={2}'.format(
                    project, self.ref1, self.ref2)
            )
            data = requests.get(url).json()
            self.commits.extend(data.get('commits', []))
            project_data[project] = len(data.get('commits', []))

        for c in self.commits:
            _local = tz.tzoffset(None, c.get('author_tz_offset'))
            _date = datetime.datetime.now(tz=_local)
            _timezone = 'UTC{0}'.format(_date.strftime('%z'))
            self.tz_data[_timezone] = self.tz_data.get(_timezone, 0) + 1

        self.projects = Counter(project_data)
        self.top_projects = OrderedDict(self.projects.most_common(10))
        self.authors = Counter(commit['author'] for commit in self.commits)
        self.top_authors = OrderedDict(self.authors.most_common(10))
        self.organizations = Counter(commit['author_email'].split('@', 1)[-1] for commit in self.commits)
        self.top_organizations = OrderedDict(self.organizations.most_common(10))


    def print_report(self):
        print('\nOpenDaylight Project Statistics for {0} since {1}'.format(self.ref1, self.ref2))
        print('\nTotal OpenDaylight projects: {0}'.format(len(self.projects)))

        top_authors = ['{0} ({1})'.format(k, v) for k, v in self.top_authors.items()]
        top_organizations = ['{0} ({1})'.format(k, v) for k, v in self.top_organizations.items()]
        top_projects = ['{0} ({1})'.format(k, v) for k, v in self.top_projects.items()]
        table = OrderedDict()
        table['Top 10 Projects'] = top_projects
        table['Top 10 Contributors'] = top_authors
        table['Top 10 Organizations'] = top_organizations
        print('\n')
        print(tabulate(table, headers='keys'))

        all_authors = sorted(['{0} ({1})'.format(k, v) for k, v in self.authors.items()])
        all_organizations = sorted(['{0} ({1})'.format(k, v) for k, v in self.organizations.items()])
        all_projects = sorted(['{0} ({1})'.format(k, v) for k, v in self.projects.items()])
        all_timezones = sorted(['{0} ({1})'.format(k, v) for k, v in self.tz_data.items()])
        table = OrderedDict()
        table['All Projects'] = all_projects
        table['All Contributors'] = all_authors
        table['All Organizations'] = all_organizations
        table['Timezones'] = all_timezones
        print('\n')
        print(tabulate(table, headers='keys'))
