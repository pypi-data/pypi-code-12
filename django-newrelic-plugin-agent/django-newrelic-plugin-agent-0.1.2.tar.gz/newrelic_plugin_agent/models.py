from manager_utils import ManagerUtilsManager
from django.db import models
from jsonfield import JSONField


class NewRelicComponent(models.Model):
    # A "reverse domain name" styled identifier;
    # for example, com.newrelic.mysql.
    # This is a unique identity defined in the plugin's user interface,
    # which ties the component data to the corresponding plugin user interface
    # in New Relic Plugins.
    guid = models.CharField(max_length=64)
    # A name (<=32 characters) that uniquely identifies the monitored entity
    # and appears as the display name for this component.
    # Note: Metric names are case sensitive.
    name = models.CharField(max_length=32)
    # The time that the component last pushed all metrics
    last_pushed_time = models.DateTimeField()

    timeslice_schema = ('total', 'count', 'min', 'max', 'sum_of_squares')

    def push(self, guid, value):
        """
        Add new value to send to newrelic

        :type guid: str
        :param guid: The GUID of the newrelic metric

        :type value: int|float
        :param value: The value to send to newrelic

        :rtype: MetricTimeslice
        :return: current timeslice for given metric
        """
        model = self._get_metric_timeslice(guid)
        updated_timeslice = self._extend_timeslice(model.values, value)
        timeslice, created = NewRelicMetricTimeslice.objects.upsert(
            new_relic_component=self, guid=guid, updates={'values': updated_timeslice})
        return timeslice

    def merge(self, guid, values):
        """
        Merge values dict into existing metric timeslice

        :type guid: str
        :param guid: The GUID of the newrelic metric

        :type values: dict
        :param values: The values dict to merge

        :rtype: MetricTimeslice
        :return: current timeslice for given metric
        """
        model = self._get_metric_timeslice(guid)
        updated_timeslice = self._extend_timeslice(
            model.values, values['total'], min_value=values['min'], max_value=values['max'], **values)
        timeslice, created = NewRelicMetricTimeslice.objects.upsert(
            new_relic_component=self, guid=guid, updates={'values': updated_timeslice})
        return timeslice

    def _get_metric_timeslice(self, guid):
        model = NewRelicMetricTimeslice.objects.get_or_none(new_relic_component=self, guid=guid)
        if model is None:
            model = NewRelicMetricTimeslice(guid=guid, values={})
        return model

    def _extend_timeslice(self, current, value, count=1, max_value=None, min_value=None, sum_of_squares=None, **kwargs):
        """
        Recomputes all aggregate figures in timeslice with a newly introduced value or values of another timeslice

        :type current: dict
        :param current: The current timeslice

        :type value: int|float
        :param value: The single value to add to the timeslice or the sum total of the extending timeslice

        :type count: int
        :param count: The number of values pushed to an extending timeslice

        :type max_value: int|float
        :param max_value: The max value of an extending timeslice

        :type min_value: int|float
        :param min_value: The min value of an extending timeslice

        :type sum_of_squares: int|float
        :param sum_of_squares: The sum of squares of an extending timeslice

        :rtype: dict
        :return: The newly updated timeslice data

        .. code-block:: python

            >>> from newrelic_plugin_agent.models import NewRelicMetricTimeslice, NewRelicComponent
            >>> starting_values = {'min':2, 'max':3, 'count':2, 'total':5, 'sum_of_squares':13}
            >>> manager = NewRelicMetricTimeslice.objects
            >>> # extending the timeslice by one value
            >>> new_values = manager._extend_timeslice(starting_values, 4)
            >>> new_values
            {'min': 2, 'max': 4, 'count': 3, 'total': 9, 'sum_of_squares': 29}
            >>> # extending the timeslice by merging another timeslice
            >>> # destructing new_values in kwargs passes sum_of_squares and count
            >>> manager._extend_timeslice(
            ...     starting_values, new_values['total'], min_value=new_values['min'],
            ...     max_value=new_values['max'], **new_values)
            {'min': 2, 'max': '4', 'count': 5, 'total': 14, 'sum_of_squares': 42}
        """
        total = current.get('total', 0) + value
        count = current.get('count', 0) + count

        if max_value is None:
            max_value = value
        max_value = max(current.get('max', 0), max_value)
        if sum_of_squares is None:
            sum_of_squares = pow(value, 2)
        sum_of_squares = current.get('sum_of_squares', 0) + sum_of_squares

        if min_value is None:
            min_value = value
        if 'min' in current:
            min_value = min(current['min'], min_value)

        return_timeslice = {
            'total': total,
            'count': count,
            'min': min_value,
            'max': max_value,
            'sum_of_squares': sum_of_squares,
        }
        return return_timeslice


class NewRelicMetricTimeslice(models.Model):
    # fk to component configuration
    new_relic_component = models.ForeignKey(NewRelicComponent, related_name='metric_timeslices')
    # Unique name of the NR metric
    # examples
    guid = models.CharField(max_length=256)
    # the metric timeslice values
    # https://docs.newrelic.com/docs/plugins/plugin-developer-resources/developer-reference/metric-data-plugin-api#timeslice
    values = JSONField()

    class Meta:
        unique_together = ('new_relic_component', 'guid')

    objects = ManagerUtilsManager()
