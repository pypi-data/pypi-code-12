# -*- coding: utf-8 -*-

# This module contains the 'live' reports about Jaobi usage.

import datetime
from tornado import gen
from jaobi.models import ContentConsumption


def _format_result(result):
    results = result['result']
    rdict = {}
    for r in results:
        rdict[r['_id']] = r['total']
    return rdict


class RealTimeConsumption:

    """ A class responsible for real time reports about consumption.

    Here 'real time' means all the ContentConsumption that was
    included in the last 5 minutes and don't have an unload_date."""

    base_collection = ContentConsumption

    @classmethod
    @gen.coroutine
    def get_themes_report(cls, **kwargs):
        """ Returns report for realtime theme consumption.

        :param kwargs: Arguments to filter the queryset before
          aggregating it. Note that ``inclusion_date__gte`` will
          always be five minutes ago and ``unload_date`` will always
          be None."""

        now = datetime.datetime.now()
        five_min_ago = now - datetime.timedelta(minutes=5)
        kwargs['inclusion_date__gte'] = five_min_ago
        kwargs['unload_date'] = None

        unwind = {'$unwind': '$themes'}
        group = {'$group':
                 {'_id': '$themes',
                  'total': {'$sum': 1}}}
        sort = {'$sort': {'total': -1}}

        pipeline = [unwind, group, sort]
        qs = cls.base_collection.objects.filter(**kwargs)
        r = yield qs.aggregate(*pipeline)
        return _format_result(r)
