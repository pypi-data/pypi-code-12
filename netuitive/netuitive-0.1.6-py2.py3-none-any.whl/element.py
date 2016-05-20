from .attribute import Attribute
from .metric import Metric
from .sample import Sample
from .tag import Tag
from .relation import Relation


class Element(object):

    """
    An entity that represents the host that the agent runs on

        :param ElementType: Type of the Element
        :type ElementType: string

    """

    def __init__(self, ElementType='SERVER', location=None):
        self.type = ElementType
        self.tags = []
        self.attributes = []
        self.relations = []
        self.metrics = []
        self.samples = []
        self.id = None
        self.name = None

        if location is not None:
            self.location = location

    def add_attribute(self, name, value):
        """
            :param name: Name of the attribute
            :type name: string
            :param value: Value of the attribute
            :type value: string
        """

        self.attributes.append(Attribute(name, value))

    def add_relation(self, fqn):
        """
            :param fqn: FQN of the other Element
            :type name: string
        """

        self.relations.append(Relation(fqn))

    def add_tag(self, name, value):
        """
            :param name: Name of the tag
            :type name: string
            :param value: Value of the tag
            :type value: string
        """

        self.tags.append(Tag(name, value))

    def add_sample(self,
                   metricId,
                   timestamp,
                   value,
                   metricType=None,
                   host=None,
                   sparseDataStrategy='None',
                   unit='',
                   tags=None,
                   min=None,
                   max=None,
                   avg=None,
                   sum=None,
                   cnt=None):
        """
            :param metricId: Metric FQN
            :type metricId: string
            :param timestamp: Timestamp for the sample
            :type timestamp: int
            :param value: Value of the sample
            :type value: float
            :param metricType: Metric Type
            :type metricType: string
            :param host: Element FQN
            :type host: string
            :param sparseDataStrategy: Sparse data strategy
            :type sparseDataStrategy: string
            :param unit: Metric Unit type
            :type unit: string
            :param tags: List of dicts
            :type tags: list
            :param min: Minimum of the sample
            :type min: float
            :param max: Maximum of the sample
            :type max: float
            :param avg: Average of the sample
            :type avg: float
            :param sum: Sum of the sample
            :type sum: float
            :param cnt: Count of the sample
            :type cnt: float



        """

        if self.id is None and host is not None:
            self.id = host

        if self.name is None and host is not None:
            self.name = host

        if tags is not None:
            Tags = []
            for i in tags:
                for k in i:
                    Tags.append(Tag(k, i[k]))

        else:
            Tags = None

        if len(self.metrics) > 0:
            t = list(self.metrics)

            if metricId not in t:
                self.metrics.append(
                    Metric(metricId,
                           metricType,
                           sparseDataStrategy,
                           unit,
                           Tags))
        else:
            self.metrics.append(
                Metric(metricId,
                       metricType,
                       sparseDataStrategy,
                       unit,
                       Tags))

        self.samples.append(Sample(metricId,
                                   timestamp *
                                   1000,
                                   value,
                                   min,
                                   max,
                                   avg,
                                   sum,
                                   cnt))

    def clear_samples(self):
        self.metrics = []
        self.samples = []
