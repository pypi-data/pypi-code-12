


import urllib2
import urllib
import re
import json
from datetime import date

from courier import Courier, Statuses


class SP(Courier):
    tracking_url = 'http://api.posta.sk/private/search?q={tracknum}&m=tnt'
    extendable = False

    def __init__(self, tracknum, force_reload=False):
        super(SP, self).__init__(tracknum)
        self.sp_data = json.loads(self.tracking_page)

    def is_tracknum_valid(self):
        """Is self.tracknum valid?"""
        return not self.sp_data['parcels']

    def is_extended(self):
        raise NotImplementedError()

    def get_status(self):
        last_state = None
        for event in self.sp_data['parcels'][0]['events'][::-1]:
            if 'state' in event:
                last_state = event['state']
                break
            return Statuses.DELIVERED
        
        # TODO: this translation of statuses is (most probably) wrong

        if last_state == 'received':
            return Statuses.SENT
        elif last_state == 'notified':  # Item retained at post office {post}
            return Statuses.DELIVERING
        elif last_state == 'delivered':
            return Statuses.DELIVERED
        
        logger.warning(u"Unknown shipping state : '" + last_state + "' for '" + self.tracknum + "'")

        return Statuses.UNKNOWN

    def get_expiration_date(self):
        raise NotImplementedError()
