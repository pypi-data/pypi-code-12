# -*- coding: utf-8 -*-

# In this module is the consolidated data for reports about
# Jaobi usage.

import os
import re
from collections import defaultdict, OrderedDict
import datetime
import time
from bson.objectid import ObjectId
from mongomotor.document import Document, MapReduceDocument
from mongomotor.fields import StringField, DateTimeField
from pyrocumulus.conf import settings
from pyrocumulus.utils import fqualname
from tornado import gen
from tornado.concurrent import Future
from jaobi import models
from jaobi.utils import log
from jaobi.scheduler import scheduler

HERE = os.path.abspath(os.path.dirname(__file__))


class ReportMixin:

    """Base mixin for reports"""

    base_collection = models.ContentConsumption

    @classmethod
    def _format_kw(cls, **kwargs):
        kw = {}
        for k, v in kwargs.items():
            if not k.startswith('id__'):
                k = 'id__{}'.format(k)
            kw[k] = v
        return kw

    @classmethod
    def _format_result(cls, result):

        results = result['result']
        rdict = OrderedDict()
        for r in results:
            rdict[r['_id']] = r['total']
        return rdict

    @classmethod
    def _format_history_result(cls, key, result):
        rdict = defaultdict(list)
        for r in result['result']:
            rdict[r['_id'][key]].append({'date': r['_id']['date'],
                                         'total': r['total']})

        for k, v in rdict.items():
            rdict[k] = sorted(v, key=lambda d: d['date'], reverse=True)

        return rdict

    @classmethod
    def get_sort_pipeline(cls, sort):
        """Returns a pipeline (list) for sorting aggregation.
        If not ``sort`` returns an empty list.

        :param sort: Sort criteria."""

        pipeline = []
        if sort:
            pipeline.append({'$sort': sort})

        return pipeline

    @classmethod
    def get_skip_pipeline(cls, skip):
        """Returns a pipeline (list) for skipping aggregation.
        If not ``skip`` returns an empty list.

        :param skip: skip quantity."""

        pipeline = []
        if skip:
            pipeline.append({'$skip': skip})

        return pipeline

    @classmethod
    def get_limit_pipeline(cls, limit):
        """Returns a pipeline (list) for limiting aggregation.
        If not ``limit`` returns an empty list.

        :param limit: limit quantity."""

        pipeline = []
        if limit:
            pipeline.append({'$limit': limit})

        return pipeline

    @classmethod
    @gen.coroutine
    def get_report(cls, *pipeline, sort=None, skip=None, limit=None,
                   formatcall=None, **kwargs):
        """Returns reports based on ``pipeline``.

        :param pipeline: Base pipeline for aggregation.
        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param formatcall: Callable used to format the results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        kw = cls._format_kw(**kwargs)
        qs = cls.objects.filter(**kw)
        pipeline = list(pipeline)
        pipeline += cls.get_sort_pipeline(sort)
        pipeline += cls.get_skip_pipeline(skip)
        pipeline += cls.get_limit_pipeline(limit)
        r = yield qs.aggregate(*pipeline, allowDiskUse=True)

        if not formatcall:
            formatcall = cls._format_result

        r = formatcall(r)
        if isinstance(r, Future):
            r = yield r
        return r


class AggregatedReportMixin(ReportMixin):

    """Mixin for reports that use aggregation"""

    aggregation_fields = OrderedDict()
    mapf = None
    reducef = None
    _lock = None

    @classmethod
    def get_dated_project(cls, **aggregation_fields):
        """Returns a list representing the two first steps of a
        pipeline for grouping this by day.

        :param aggregation_fields: Fields to use in the dated projects
        """

        pipeline = [
            {'$project': dict(date='$inclusion_date',
                              h={'$hour': '$inclusion_date'},
                              m={'$minute': '$inclusion_date'},
                              s={'$second': '$inclusion_date'},
                              ms={'$millisecond': '$inclusion_date'},
                              **aggregation_fields)},
            {'$project': dict(date={'$subtract':
                                    ['$date',
                                     {'$add': ['$ms',
                                               {'$multiply': ['$s', 1000]},
                                               {'$multiply': ['$m', 60, 1000]},
                                               {'$multiply': ['$h',
                                                              3600, 1000]}]}]},
                              **aggregation_fields)}]
        return pipeline

    @classmethod
    def get_out_step(cls):
        """Returns the step for sending the result of an aggregation
        to a collection. It must be the last step in a pipeline."""

        return {'$out': cls._get_collection_name()}

    @classmethod
    def get_pipeline(cls):
        """Returns the pipeline for aggregation. Must be implemented in
        subclasses."""
        raise NotImplementedError

    @classmethod
    @gen.coroutine
    def do_aggregate(cls, **kwargs):
        """Aggregates ``cls.base_collection`` using the pipeline provided
        by ``cls.get_pipeline()``. It does an 'incremental' aggregation
        by sending the aggregation result to a temp collection and map
        reduce it to the final collection (read the code!).

        :param kwargs: Filter to queryset.
        """
        class_name = fqualname(cls)
        lock_name = '{}-lock'.format(class_name)

        if cls._lock is not None:
            log('cls {} already aggregating. Leaving...'.format(class_name))
            return

        log('Aggregating {}'.format(class_name))

        cls._lock = lock_name
        qs = cls.base_collection.objects.filter(**kwargs)
        pipeline = cls.get_pipeline()
        # The thing here is that the $out for aggregation in mongo
        # always overwrite the output collection, so I save it to a
        # temp collection and after that do a map reduce to the final
        # collection.
        out = pipeline[-1]['$out']
        tmp_out = '{}_{}'.format(out, str(time.time())[-7:].strip('.'))
        pipeline[-1]['$out'] = tmp_out
        r = yield qs.aggregate(*pipeline, allowDiskUse=True)
        # Here I have an instance of MotorCollection for the
        # temp collection so I can map reduce it to the final collection
        # and then drop it.
        coll = cls.base_collection._collection
        db = coll.database
        tmp_coll = coll.__class__(db, tmp_out)

        mapf = cls.mapf
        if not mapf:
            mapf = """function(){emit(this._id, this.value);}"""

        reducef = cls.reducef
        if not reducef:
            reducef = """function(key, values){return values;}"""

        opts = {'out': {'merge': out}}
        yield tmp_coll.map_reduce(mapf, reducef, **opts)
        yield tmp_coll.drop()
        cls._lock = None
        return r


class ConsumptionReportMixin(AggregatedReportMixin):

    """Mixin for reports related to consumption."""

    @classmethod
    def get_pipeline(cls):
        """Returns the pipeline for consumption aggregation."""

        pipeline = super().get_dated_project(**cls.aggregation_fields)

        d = cls.aggregation_fields.copy()
        d.update({'date': '$date'})
        group = {'$group': {'_id': d, 'value': {'$sum': 1}}}
        pipeline.append(group)
        pipeline.append(cls.get_out_step())
        return pipeline


class ConsumerReportMixin(AggregatedReportMixin):

    """Mixin for reports related to consumers."""

    @classmethod
    def get_pipeline(cls):
        """Returns the pipeline for consumers aggretation."""

        consumers_aggr = cls.aggregation_fields.copy()
        consumers_aggr.update({'consumer': '$consumer'})
        pipeline = super().get_dated_project(**consumers_aggr)

        d = cls.aggregation_fields.copy()
        d.update({'date': '$date'})

        # Here we group unique consumers by key/day
        group = {'$group': {'_id': d, 'consumers': {'$addToSet': '$consumer'}}}
        pipeline.append(group)
        # Here we have the count of consumers
        project = {'$project': {'_id': '$_id',
                                'value': {'$size': '$consumers'}}}
        pipeline.append(project)
        # And here we direct the output to a collection
        pipeline.append(cls.get_out_step())
        return pipeline


class ThemeReportMixin(ReportMixin):

    """A Mixin for reports related to themes"""

    @classmethod
    def get_pipeline(cls):
        """Returns a pipeline with themes unwinded."""

        pipeline = super().get_pipeline()
        # unwind themes before aggregation so we count
        # consumers by theme.
        pipeline.insert(2, {'$unwind': '$themes'})

        return pipeline

    @classmethod
    @gen.coroutine
    def get_themes_report(cls, sort=None, skip=None, limit=None, **kwargs):
        """Returns the consolidated data for themes reports.

        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        group = {"$group":
                 {'_id': '$_id.themes',
                  'total': {'$sum': '$value'}}}
        r = yield super().get_report(group, sort=sort, skip=skip,
                                     limit=limit, **kwargs)
        return r

    @classmethod
    @gen.coroutine
    def get_themes_report_history(cls, sort=None, skip=None, limit=None,
                                  **kwargs):
        """Returns the history data for themes reports.

        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        group = {'$group':
                 {'_id': {'theme': '$_id.themes',
                          'date': '$_id.date'},
                  'total': {'$sum': '$value'}}}

        fmt = lambda r: cls._format_history_result('theme', r)
        r = yield cls.get_report(group, sort=sort, skip=skip, limit=limit,
                                 formatcall=fmt, **kwargs)
        return r


class SiteReportMixin(ReportMixin):

    """A Mixin for reports related to sites."""

    @classmethod
    @gen.coroutine
    def get_sites_report(cls, sort=None, skip=None, limit=None, **kwargs):
        """Returns the consolidated data for sites reports.

        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        group = {"$group":
                 {'_id': '$_id.origin',
                  'total': {'$sum': '$value'}}}

        r = yield super().get_report(group, sort=sort, skip=skip,
                                     limit=limit, **kwargs)
        return r

    @classmethod
    @gen.coroutine
    def get_sites_report_history(cls, sort=None, skip=None, limit=None,
                                 **kwargs):
        """Returns the history data for sites reports.

        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        group = {'$group':
                 {'_id': {'origin': '$_id.origin',
                          'date': '$_id.date'},
                  'total': {'$sum': '$value'}}}

        fmt = lambda r: cls._format_history_result('origin', r)
        r = yield cls.get_report(group, sort=sort, skip=skip, limit=limit,
                                 formatcall=fmt, **kwargs)
        return r


class ReferrerReportMixin(ReportMixin):

    """Mixin for reports about referer."""

    @classmethod
    @gen.coroutine
    def get_referrer_report(cls, sort=None, skip=None, limit=None, **kwargs):
        """Returns the consolidated data for referrer reports.

        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        group = {"$group":
                 {'_id': '$_id.referrer',
                  'total': {'$sum': '$value'}}}

        r = yield super().get_report(group, sort=sort, skip=skip,
                                     limit=limit, **kwargs)

        count = {'$group': {'_id': ObjectId(), 'count': {'$sum': 1}}}
        fmt = lambda r: r['result'][0]['count']
        total = yield cls.get_report(group, count, formatcall=fmt, **kwargs)

        quantity = len(r)
        return {'total': total, 'quantity': quantity,
                'skip': skip, 'limit': limit, 'result': r}


class ContentReportMixin(ReportMixin):

    """ Mixin for reports related to content."""

    @classmethod
    @gen.coroutine
    def _format_result(cls, result):

        rdict = OrderedDict()
        ids = [r['_id'] for r in result['result']]
        contents = yield models.Content.objects.filter(id__in=ids).to_list()

        def get_total(rid):
            for c in result['result']:
                if c['_id'] == rid:
                    return c['total']

        def get_content(rid):
            for c in contents:
                if c.id == rid:
                    return c

        for rid in ids:
            rdict[get_content(rid)] = get_total(rid)

        return rdict

    @classmethod
    @gen.coroutine
    def do_aggregate(cls, **kwargs):
        """Does the usual aggregation and after that do an extra
        map-reduce to join info from content."""

        yield super().do_aggregate(**kwargs)

        class_name = fqualname(cls)
        if cls._lock is not None:
            log('cls {} already aggregating. Leaving...'.format(class_name))
            return

        log('Join content for {}'.format(class_name))
        lock_name = '{}-lock'.format(fqualname(cls))
        cls._lock = lock_name
        # Here I get the dates that need to be joined.
        r = yield cls.objects.filter(value__total=None).aggregate(
            {"$group": {'_id': '$_id.date'}})

        for doc in r['result']:
            date = doc['_id']
            # And here the map-reduce for each day needed.
            log('Join for date {} for {}'.format(
                date.strftime('%Y-%m-%d'), class_name))
            mapf = """
function(){
  emit({'content': this._id, 'date': ISODate('%s')},
       {total: 0, origin: this.origin, url:this.url});
};
""" % (date.strftime('%Y-%m-%d'))

            reducef = """
function(key, values){
  var result = {'total': 0};

  values.forEach(function(value){

    if (typeof(value) == 'number'){
      result['total'] += value;
    }
    else{
      if(value.origin){result['origin'] = value.origin;}
      if(value.url){result['url'] = value.url;}
    }
  });
  return result
};
"""
            pipeline = cls.get_pipeline()
            out = pipeline[-1]['$out']

            r = yield models.Content.objects.map_reduce(
                mapf, reducef, {'reduce': out}, get_out_docs=False)
        # here dropping content that was not visited
        yield cls.objects.filter(value__total=0).delete()
        cls._lock = None
        return r

    @classmethod
    @gen.coroutine
    def get_content_report(cls, sort=None, skip=None, limit=None, **kwargs):
        """Returns the consolidated data for content reports.

        :param sort: Order for aggretation results.
        :param skip: Offset for aggregation results.
        :param limit: Limit for aggregation results.
        :param kwargs: Arguments to filter the queryset before
          aggregating it."""

        group = {'$group':
                 {'_id': '$_id.content',
                  'total': {'$sum': '$value.total'}}}

        r = yield cls.get_report(group, sort=sort, skip=skip,
                                 limit=limit, **kwargs)

        count = {'$group': {'_id': ObjectId(), 'count': {'$sum': 1}}}
        fmt = lambda r: r['result'][0]['count']
        total = yield cls.get_report(group, count, formatcall=fmt, **kwargs)
        quantity = len(r)
        return {'total': total, 'quantity': quantity,
                'skip': skip, 'limit': limit, 'result': r}


class ThemeConsumption(MapReduceDocument, ThemeReportMixin,
                       ConsumptionReportMixin):

    """ This Document is the result of a map-reduce done in the
    content_consumption collection. It reduces the consumption to
    a consolidated consumption by theme/site/day.

    """

    aggregation_fields = OrderedDict({'origin': '$origin',
                                      'themes': '$themes'})


class SiteConsumption(MapReduceDocument, SiteReportMixin,
                      ConsumptionReportMixin):

    """ This Document is the result of an aggregation done in the
    content_consumption collection. It reduces the consumption to
    a consolidated consumption by site/day.
    """

    aggregation_fields = OrderedDict({'origin': '$origin'})


class ThemeConsumers(MapReduceDocument, ThemeReportMixin, ConsumerReportMixin):

    """ This Document is the result of an aggregation done in the
    content_consumption collection. It reduces the consumption to
    consolidated consumers by theme/day.
    """

    aggregation_fields = OrderedDict({'themes': '$themes'})


class SiteConsumers(MapReduceDocument, SiteReportMixin, ConsumerReportMixin):

    """ This Document is the result of an aggregation done in the
    content_consumption collection. It reduces the consumption to
    consolidated consumers by site/day.
    """

    aggregation_fields = OrderedDict({'origin': '$origin'})


class ContentConsumptionReport(MapReduceDocument, ContentReportMixin,
                               ConsumptionReportMixin):

    """ This Document is the result of an aggregation done in the
    content_consumption collection. It reduces the consumption to
    consolidated consumption by content/day."""

    aggregation_fields = OrderedDict({'content': '$content'})


class ContentConsumersReport(MapReduceDocument, ContentReportMixin,
                             ConsumerReportMixin):

    """ This Document is the result of an aggretation done in the
    content_consumption collection. It reduces the consumption to
    consolidated consumers by content/day."""

    aggregation_fields = OrderedDict({'content': '$content'})


class ReferrerConsumption(MapReduceDocument, ReferrerReportMixin,
                          ConsumptionReportMixin):

    """ This Document is the result of an aggretation done in the
    content_consumption collection. It reduces the consumption to
    consolidated consumers by referrer/day."""

    aggregation_fields = OrderedDict({'referrer': '$referrer',
                                      'origin': '$origin'})


class IncrementalMapReduce(Document):

    """This class takes care of incrementally execute the map
    reduce (or aggretation) for reports."""

    collection = StringField(unique=True, required=True)
    last_incr = DateTimeField()
    _reduced = []

    @classmethod
    @gen.coroutine
    def _get_since_for(cls, collection_name):
        try:
            col_incr = yield cls.objects.get(collection=collection_name)
        except cls.DoesNotExist:
            col_incr = cls(collection=collection_name)
            yield col_incr.save()

        begin_of_all_times = settings.BEGIN_OF_ALL_TIMES if hasattr(
            settings, 'BEGIN_OF_ALL_TIMES') else None

        since = col_incr.last_incr or begin_of_all_times
        return since

    @classmethod
    @gen.coroutine
    def _set_since_for(cls, collection_name):
        col_incr = yield cls.objects.get(collection=collection_name)
        col_incr.last_incr = datetime.datetime.now()
        yield col_incr.save()

    @classmethod
    def add(cls, reduced_cls):
        """Adds a reduced report to the map-reduce queue."""

        cls._reduced.append(reduced_cls)

    @classmethod
    @gen.coroutine
    def do_incremental_map_reduce(cls):
        """Do an incremental map reduce since the last time
        it was done."""

        futures = []
        for reduced_cls in cls._reduced:
            kw = {}
            coll_name = reduced_cls._get_collection_name()
            since = yield cls._get_since_for(coll_name)

            if since:
                kw = {'inclusion_date__gte': since}

            future = reduced_cls.do_aggregate(**kw)
            future.add_done_callback(cls._handle_aggregate_exception)
            futures.append(future)

            yield cls._set_since_for(coll_name)

        return futures

    @classmethod
    @gen.coroutine
    def do_today_map_reduce(cls):
        """Do map reduce for the current day."""

        futures = []
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        kw = {'inclusion_date__gte': today}
        for reduced_cls in cls._reduced:
            future = reduced_cls.do_aggregate(**kw)
            future.add_done_callback(cls._handle_aggregate_exception)
            futures.append(future)

        return futures

    @classmethod
    @gen.coroutine
    def do_yesterday_map_reduce(cls):
        """Do map reduce for the last day."""

        futures = []
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        yesterday = today - datetime.timedelta(days=1)

        kw = {'inclusion_date__gte': yesterday,
              'inclusion_date__lt': today}
        for reduced_cls in cls._reduced:
            future = reduced_cls.do_aggregate(**kw)
            future.add_done_callback(cls._handle_aggregate_exception)
            futures.append(future)

        return futures

    @classmethod
    def _handle_aggregate_exception(cls, future):
        """Releases the lock if some exception happend while aggregating."""
        if future.exception():
            cls._lock = None


@gen.coroutine
def _hack_clean_bad_collections():  # pragma no coverage for hacks!
    """There is a bug with the aggregate/map-reduce I use. Sometimes, I don't
    know why the tmp collection is not dropped. This shit here is to drop
    these collections."""

    log('hack to clean!!!', level='warning')
    coll = models.ContentConsumption._collection
    db = coll.database
    collections = yield db.collection_names()
    tmp_pat = re.compile('.+?_\d+?')
    tmp_colls = [c for c in collections if re.match(tmp_pat, c)]
    for tmp in tmp_colls:
        tmp_coll = coll.__class__(db, tmp)
        yield tmp_coll.drop()


if hasattr(settings, 'USE_REDUCED_REPORTS') and \
   settings.USE_REDUCED_REPORTS:  # pragma no coverage for hacks
    reduced_reports = [ThemeConsumption, SiteConsumption,
                       SiteConsumers, ThemeConsumers, ContentConsumersReport,
                       ContentConsumptionReport, ReferrerConsumption]
    for r in reduced_reports:
        IncrementalMapReduce.add(r)

    # 2 hours
    secs = 3600 * 2
    print('adding incremental map reduce to scheduler')
    scheduler.add(IncrementalMapReduce.do_incremental_map_reduce, secs)

    print('adding clean stuff')
    # 1 hour
    secs = 3600
    scheduler.add(_hack_clean_bad_collections, secs)
