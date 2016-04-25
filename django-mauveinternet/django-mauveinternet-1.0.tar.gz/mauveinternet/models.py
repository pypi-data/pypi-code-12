import re
import operator
from django.db import models

class QuickSearchManager(models.Manager):
    def __init__(self, search=[]):
        """Construct a QuickSearchManager with a quick_search method that
        searches the fields listed in 'search'
        """
        super(QuickSearchManager, self).__init__()
        self.search = search

    def quick_search(self, query):
        """Returns a queryset that matches all instances where ALL of the words in query
        match in ANY of the fields provided in the constructor.
        """
        words = re.split(r'\s+', query)
        qs = self.all()
        for w in words:
            qlist = [models.Q(**{'%s__icontains' % k: w}) for k in self.search]
            qs = qs.filter(reduce(operator.or_, qlist))

        return qs
