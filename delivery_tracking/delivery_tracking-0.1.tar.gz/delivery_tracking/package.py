
import re

from cp import CP
from sp import SP


class Package(object):
    """
    TODO
    tracknum_regexes
    """
    all_couriers = {'cp': CP,
                    'sp': SP}

    email = "jack@jack.cz"  # XXX
    cache_prefix = "cp_tracker_"
    deadline_seconds = 40
    
    def __init__(self, courier, tracknum):
        if courier not in self.all_couriers.keys():
            raise ValueError('{0} is not valid courier code ({1})'.format(
                courier, ', '.join(self.all_couriers.keys())))

        self.courier = self.all_couriers[courier](tracknum)

    @staticmethod
    def guess_courier(tracknum):
        for courier_key, courier_class in Package.all_couriers.items():
            if any([re.match(regex, tracknum) for regex in courier_class.tracknum_regexes]):
                return courier_key

        return None



