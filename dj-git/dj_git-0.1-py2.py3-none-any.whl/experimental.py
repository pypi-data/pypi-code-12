# -*- coding: utf-8 -*-

"""
experimental

Some experimentations.

:copyright: (c) 2016 by Taurus Olson <taurusolson@gmail.com>
:license: MIT

"""

from django.db.models import Count
from git.models import Project

# Count the number of commits by committer
p = Project.objects.get(name='agate')

total_commits_by_committer = p.commit_set.values('committer') \
    .annotate(total_commits=Count('sha')) \
    .order_by('-total_commits')


