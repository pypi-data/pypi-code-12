from socket import gethostname
from datetime import datetime
from logging import getLogger

from celery import Task
from db_mutex import db_mutex, DBMutexError
from requests import post

from newrelic_plugin_agent.conf import settings
from newrelic_plugin_agent.constants import AGENT_MUTEX_ID_NAMESPACE
from newrelic_plugin_agent.models import NewRelicComponent
from newrelic_plugin_agent.version import __version__


LOG = getLogger(__name__)


class PushMetricTimeslicesTask(Task):

    def run(self, *args, **kwargs):
        for component in NewRelicComponent.objects.all():
            try:
                with db_mutex('{0}:{1}'.format(AGENT_MUTEX_ID_NAMESPACE, component.guid)):
                    last_pushed_time = component.last_pushed_time
                    metrics = self._get_component_metrics(component)
                    component.last_pushed_time = datetime.now()
                    component.save()
            except DBMutexError as exc:
                raise self.retry(exc=exc, countdown=settings.TIMESLICE_LOCK_RETRY_DELAY_MS)
            # note regarding failure to deliver (http) metrics:
            #       I considered merging the metrics back and resetting the last
            #       push time of the component, but couldn't easily solve the race
            #       condition observed when this component is repopulated and
            #       pushed in the time between releasing the lock and getting a
            #       bad http response from NR. The other obvious alternative is
            #       to lock until we receive a successful response, but I don't
            #       consider that an acceptable solution.  Considered this lost
            #       request an acceptable risk for the time being. No data is
            #       better than bad data imo
            self._push_component_metrics(component, metrics, last_pushed_time)

    def _push_component_metrics(self, component, metrics, last_pushed_time):
        # send values
        headers = {
            'X-License-Key': settings.NEWRELIC_LICENSE_KEY,
            'Content-Type': 'application/json',
        }
        duration = datetime.now() - last_pushed_time
        try:
            hostname = gethostname()
        except:  # pragma: no cover
            hostname = 'localhost'
        body = {
            'agent': {
                'host': hostname,
                'version': __version__,
            },
            'components': [{
                'name': component.name,
                'guid': component.guid,
                'duration': duration.seconds,
                'metrics': metrics,
            }]
        }
        response = post('{0}/platform/v1/metrics'.format(settings.NEWRELIC_BASE_URL), json=body, headers=headers)
        if response.status_code != 200:
            LOG.error('could not push metrics to New Relic')

    def _get_component_metrics(self, component):
        metrics = {}
        for timeslice in component.metric_timeslices.all():
            metrics[timeslice.guid] = timeslice.values
            timeslice.delete()
        return metrics


class PushMetricValueTask(Task):

    def run(self, component, guid, value, *args, **kwargs):
        try:
            with db_mutex('{0}:{1}'.format(AGENT_MUTEX_ID_NAMESPACE, component.guid)):
                # add value to timeslice
                component.push(guid, value)
        except DBMutexError as exc:
            raise self.retry(exc=exc, countdown=settings.TIMESLICE_LOCK_RETRY_DELAY_MS)
