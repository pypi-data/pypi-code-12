""" standard """
from Config.ResourceType import ResourceType


def parse_metrics(metric):
    """ """

    #
    # standard values
    #
    
    omo = OwnerMetricsObject()
    
    omo.set_average_indicator_confidence(metric['averageIndicatorConfidence'])
    omo.set_average_indicator_rating(metric['averageIndicatorRating'])
    omo.set_metric_date(metric['metricDate'])
    omo.set_total_address(metric['totalAddress'])
    omo.set_total_adversary(metric['totalAdversary'])
    omo.set_total_document(metric['totalDocument'])
    omo.set_total_email(metric['totalEmail'])
    omo.set_total_emailaddress(metric['totalEmailAddress'])
    omo.set_total_enriched_indicator(metric['totalEnrichedIndicator'])
    omo.set_total_false_positive(metric['totalFalsePositive'])
    omo.set_total_false_positive_daily(metric['totalFalsePositiveDaily'])
    omo.set_total_file(metric['totalFile'])
    omo.set_total_group(metric['totalGroup'])
    omo.set_total_groupAttribute(metric['totalGroupAttribute'])
    omo.set_total_group_indicator(metric['totalGroupIndicator'])
    omo.set_total_host(metric['totalHost'])
    omo.set_total_incident(metric['totalIncident'])
    omo.set_total_indicator(metric['totalIndicator'])
    omo.set_total_indicatorAttribute(metric['totalIndicatorAttribute'])
    omo.set_total_observation_address(metric['totalObservationAddress'])
    omo.set_total_observation_daily(metric['totalObservationDaily'])
    omo.set_total_observation_emailaddress(metric['totalObservationEmailAddress'])
    omo.set_total_observation_file(metric['totalObservationFile'])
    omo.set_total_observation_host(metric['totalObservationHost'])
    omo.set_total_observation_indicator(metric['totalObservationIndicator'])
    omo.set_total_observation_url(metric['totalObservationUrl'])
    omo.set_total_result(metric['totalResult'])
    omo.set_total_signature(metric['totalSignature'])
    omo.set_total_tag(metric['totalTag'])
    omo.set_total_task(metric['totalTask'])
    omo.set_total_threat(metric['totalThreat'])
    omo.set_total_track(metric['totalTrack'])
    omo.set_total_url(metric['totalUrl'])
    
    return omo


class OwnerMetricsObject(object):
    __slots__ = (
        '_average_indicator_confidence',
        '_average_indicator_rating',
        '_metric_date',
        '_total_address',
        '_total_adversary',
        '_total_document',
        '_total_email',
        '_total_emailaddress',
        '_total_enriched_indicator',
        '_total_false_positive',
        '_total_false_positive_daily',
        '_total_file',
        '_total_group',
        '_total_groupAttribute',
        '_total_group_indicator',
        '_total_host',
        '_total_incident',
        '_total_indicator',
        '_total_indicatorAttribute',
        '_total_observation_address',
        '_total_observation_daily',
        '_total_observation_emailaddress',
        '_total_observation_file',
        '_total_observation_host',
        '_total_observation_indicator',
        '_total_observation_url',
        '_total_result',
        '_total_signature',
        '_total_tag',
        '_total_task',
        '_total_threat',
        '_total_track',
        '_total_url'
    )

    def __init__(self):
        """ """
        self._average_indicator_confidence = None
        self._average_indicator_rating = None
        self._metric_date = None
        self._total_address = None
        self._total_adversary = None
        self._total_document = None
        self._total_email = None
        self._total_emailaddress = None
        self._total_enriched_indicator = None
        self._total_false_positive = None
        self._total_false_positive_daily = None
        self._total_file = None
        self._total_group = None
        self._total_groupAttribute = None
        self._total_group_indicator = None
        self._total_host = None
        self._total_incident = None
        self._total_indicator = None
        self._total_indicatorAttribute = None
        self._total_observation_address = None
        self._total_observation_daily = None
        self._total_observation_emailaddress = None
        self._total_observation_file = None
        self._total_observation_host = None
        self._total_observation_indicator = None
        self._total_observation_url = None
        self._total_result = None
        self._total_signature = None
        self._total_tag = None
        self._total_task = None
        self._total_threat = None
        self._total_track = None
        self._total_url = None

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    """ shared metric resolution methods """
    #
    # average_indicator_confidence
    #
    @property
    def average_indicator_confidence(self):
        """ """
        return self._average_indicator_confidence
    
    def set_average_indicator_confidence(self, data):
        """ """
        self._average_indicator_confidence = data
    
    
    #
    # average_indicator_rating
    #
    @property
    def average_indicator_rating(self):
        """ """
        return self._average_indicator_rating
    
    def set_average_indicator_rating(self, data):
        """ """
        self._average_indicator_rating = data
    
    
    #
    # metric_date
    #
    @property
    def metric_date(self):
        """ """
        return self._metric_date
    
    def set_metric_date(self, data):
        """ """
        self._metric_date = data
    
    
    #
    # total_address
    #
    @property
    def total_address(self):
        """ """
        return self._total_address
    
    def set_total_address(self, data):
        """ """
        self._total_address = data
    
    
    #
    # total_adversary
    #
    @property
    def total_adversary(self):
        """ """
        return self._total_adversary
    
    def set_total_adversary(self, data):
        """ """
        self._total_adversary = data
    
    
    #
    # total_document
    #
    @property
    def total_document(self):
        """ """
        return self._total_document
    
    def set_total_document(self, data):
        """ """
        self._total_document = data
    
    
    #
    # total_email
    #
    @property
    def total_email(self):
        """ """
        return self._total_email
    
    def set_total_email(self, data):
        """ """
        self._total_email = data
    
    
    #
    # total_emailaddress
    #
    @property
    def total_emailaddress(self):
        """ """
        return self._total_emailaddress
    
    def set_total_emailaddress(self, data):
        """ """
        self._total_emailaddress = data
    
    
    #
    # total_enriched_indicator
    #
    @property
    def total_enriched_indicator(self):
        """ """
        return self._total_enriched_indicator
    
    def set_total_enriched_indicator(self, data):
        """ """
        self._total_enriched_indicator = data
    
    
    #
    # total_false_positive
    #
    @property
    def total_false_positive(self):
        """ """
        return self._total_false_positive
    
    def set_total_false_positive(self, data):
        """ """
        self._total_false_positive = data
    
    
    #
    # total_false_positive_daily
    #
    @property
    def total_false_positive_daily(self):
        """ """
        return self._total_false_positive_daily
    
    def set_total_false_positive_daily(self, data):
        """ """
        self._total_false_positive_daily = data
    
    
    #
    # total_file
    #
    @property
    def total_file(self):
        """ """
        return self._total_file
    
    def set_total_file(self, data):
        """ """
        self._total_file = data
    
    
    #
    # total_group
    #
    @property
    def total_group(self):
        """ """
        return self._total_group
    
    def set_total_group(self, data):
        """ """
        self._total_group = data
    
    
    #
    # total_groupAttribute
    #
    @property
    def total_groupAttribute(self):
        """ """
        return self._total_groupAttribute
    
    def set_total_groupAttribute(self, data):
        """ """
        self._total_groupAttribute = data
    
    
    #
    # total_group_indicator
    #
    @property
    def total_group_indicator(self):
        """ """
        return self._total_group_indicator
    
    def set_total_group_indicator(self, data):
        """ """
        self._total_group_indicator = data
    
    
    #
    # total_host
    #
    @property
    def total_host(self):
        """ """
        return self._total_host
    
    def set_total_host(self, data):
        """ """
        self._total_host = data
    
    
    #
    # total_incident
    #
    @property
    def total_incident(self):
        """ """
        return self._total_incident
    
    def set_total_incident(self, data):
        """ """
        self._total_incident = data
    
    
    #
    # total_indicator
    #
    @property
    def total_indicator(self):
        """ """
        return self._total_indicator
    
    def set_total_indicator(self, data):
        """ """
        self._total_indicator = data
    
    
    #
    # total_indicatorAttribute
    #
    @property
    def total_indicatorAttribute(self):
        """ """
        return self._total_indicatorAttribute
    
    def set_total_indicatorAttribute(self, data):
        """ """
        self._total_indicatorAttribute = data
    
    
    #
    # total_observation_address
    #
    @property
    def total_observation_address(self):
        """ """
        return self._total_observation_address
    
    def set_total_observation_address(self, data):
        """ """
        self._total_observation_address = data
    
    
    #
    # total_observation_daily
    #
    @property
    def total_observation_daily(self):
        """ """
        return self._total_observation_daily
    
    def set_total_observation_daily(self, data):
        """ """
        self._total_observation_daily = data
    
    
    #
    # total_observation_emailaddress
    #
    @property
    def total_observation_emailaddress(self):
        """ """
        return self._total_observation_emailaddress
    
    def set_total_observation_emailaddress(self, data):
        """ """
        self._total_observation_emailaddress = data
    
    
    #
    # total_observation_file
    #
    @property
    def total_observation_file(self):
        """ """
        return self._total_observation_file
    
    def set_total_observation_file(self, data):
        """ """
        self._total_observation_file = data
    
    
    #
    # total_observation_host
    #
    @property
    def total_observation_host(self):
        """ """
        return self._total_observation_host
    
    def set_total_observation_host(self, data):
        """ """
        self._total_observation_host = data
    
    
    #
    # total_observation_indicator
    #
    @property
    def total_observation_indicator(self):
        """ """
        return self._total_observation_indicator
    
    def set_total_observation_indicator(self, data):
        """ """
        self._total_observation_indicator = data
    
    
    #
    # total_observation_url
    #
    @property
    def total_observation_url(self):
        """ """
        return self._total_observation_url
    
    def set_total_observation_url(self, data):
        """ """
        self._total_observation_url = data
    
    
    #
    # total_result
    #
    @property
    def total_result(self):
        """ """
        return self._total_result
    
    def set_total_result(self, data):
        """ """
        self._total_result = data
    
    
    #
    # total_signature
    #
    @property
    def total_signature(self):
        """ """
        return self._total_signature
    
    def set_total_signature(self, data):
        """ """
        self._total_signature = data
    
    
    #
    # total_tag
    #
    @property
    def total_tag(self):
        """ """
        return self._total_tag
    
    def set_total_tag(self, data):
        """ """
        self._total_tag = data
    
    
    #
    # total_task
    #
    @property
    def total_task(self):
        """ """
        return self._total_task
    
    def set_total_task(self, data):
        """ """
        self._total_task = data
    
    
    #
    # total_threat
    #
    @property
    def total_threat(self):
        """ """
        return self._total_threat
    
    def set_total_threat(self, data):
        """ """
        self._total_threat = data
    
    
    #
    # total_track
    #
    @property
    def total_track(self):
        """ """
        return self._total_track
    
    def set_total_track(self, data):
        """ """
        self._total_track = data
    
    
    #
    # total_url
    #
    @property
    def total_url(self):
        """ """
        return self._total_url
    
    def set_total_url(self, data):
        """ """
        self._total_url = data

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Metric')

        #
        # retrievable methods
        #

        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('average_indicator_confidence', self.average_indicator_confidence))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('average_indicator_rating', self.average_indicator_rating))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('metric_date', self.metric_date))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_address', self.total_address))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_adversary', self.total_adversary))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_document', self.total_document))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_email', self.total_email))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_emailaddress', self.total_emailaddress))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_enriched_indicator', self.total_enriched_indicator))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_false_positive', self.total_false_positive))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_false_positive_daily', self.total_false_positive_daily))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_file', self.total_file))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_group', self.total_group))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_groupAttribute', self.total_groupAttribute))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_group_indicator', self.total_group_indicator))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_host', self.total_host))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_incident', self.total_incident))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_indicator', self.total_indicator))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_indicatorAttribute', self.total_indicatorAttribute))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_address', self.total_observation_address))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_daily', self.total_observation_daily))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_emailaddress', self.total_observation_emailaddress))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_file', self.total_observation_file))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_host', self.total_observation_host))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_indicator', self.total_observation_indicator))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_observation_url', self.total_observation_url))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_result', self.total_result))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_signature', self.total_signature))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_tag', self.total_tag))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_task', self.total_task))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_threat', self.total_threat))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_track', self.total_track))
        printable_string += ('  {0!s:<32}: {1!s:<50}\n'.format('total_url', self.total_url))

        return printable_string

"""
    "data": {
        "ownerMetric": [
            {
                "metricDate": "2016-03-14",
                "totalIndicator": 191362,
                "totalHost": 12373,
                "totalAddress": 145772,
                "totalEmailAddress": 1190,
                "totalFile": 4095,
                "totalUrl": 27932,
                "totalGroup": 110,
                "totalThreat": 1,
                "totalIncident": 107,
                "totalEmail": 0,
                "totalAdversary": 1,
                "totalSignature": 0,
                "totalTask": 4,
                "totalDocument": 1,
                "totalTag": 73,
                "totalTrack": 0,
                "totalResult": 0,
                "totalIndicatorAttribute": 508609,
                "totalGroupAttribute": 551,
                "averageIndicatorRating": 2.876296,
                "averageIndicatorConfidence": 47.8519,
                "totalEnrichedIndicator": 190996,
                "totalGroupIndicator": 107,
                "totalObservationDaily": 8,
                "totalObservationIndicator": 10,
                "totalObservationAddress": 16,
                "totalObservationEmailAddress": 0,
                "totalObservationFile": 0,
                "totalObservationHost": 0,
                "totalObservationUrl": 0,
                "totalFalsePositiveDaily": 2,
                "totalFalsePositive": 2
            },
            snipped
"""