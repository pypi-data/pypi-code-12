#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------


class Chirp(object):
    """ Chirp: Represents a chirp object, featuring:

    shortcode -- a 10-character identifier from the chirp alphabet
    payload -- a dict of key-value pairs
    created_at -- a datetime representing the chirp's creation date
    """
    def __init__(self, chirpsdk, data=None, shortcode=None, created_at=None,
                 longcode=None, public=True):
        self.chirpsdk = chirpsdk
        self.data = data
        self.created_at = created_at
        self.shortcode = shortcode
        self.longcode = longcode or self.chirpsdk.encode(shortcode)
        self.public = public

    def chirp(self):
        self.chirpsdk.chirp(self)

    def save_wav(self, filename=None, offline=False):
        self.chirpsdk.save_wav(self, filename, offline)
