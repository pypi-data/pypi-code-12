#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

"""
Core class bridging between chirp.audio and chirp.api components.
A ChirpSDK object can take arbitrary dictionaries (of any JSON-serialisable data)
and generate a Chirp "shortcode" identifier to play as audio.
"""

from .api import API
from .audio import AudioSession, AudioGenerator
from .chirp import Chirp


class ChirpSDK(object):
    def __init__(self, app_key, app_secret, api_host=None):
        self.api = API(app_key, app_secret, api_host)
        self.audio_session = AudioSession()
        self.audio_generator = AudioGenerator()

    def create_chirp(self, payload):
        """ Creates a Chirp object that encapsulates the given payload.

        If payload is a 10-character string, creates an audio-only chirp;
        if it is a dict, generates an identifier that encapsulates the data."""
        if isinstance(payload, dict):
            data = self.api.create_chirp(payload)
            return Chirp(chirpsdk=self, **data)
        return Chirp(chirpsdk=self, shortcode=payload)

    def get_chirp(self, shortcode):
        """ Queries the Chirp API server for a given shortcode, and returns
        the Chirp object associated."""
        data = self.api.get_chirp(shortcode)
        return Chirp(chirpsdk=self, **data)

    def chirp(self, chirp):
        """ Takes a shortcode or Chirp object, and plays it via audio hardware
        (if supported). Requires pyaudio for playback."""
        if not isinstance(chirp, Chirp):
            chirp = self.create_chirp(chirp)
        self.audio_session.play(chirp.longcode)

    def save_wav(self, chirp, filename=None, offline=False):
        """ Takes a Chirp object, translates it into audio,
        and saves the output as a .wav file."""
        if not filename:
            filename = '{}.wav'.format(chirp.shortcode)

        if not offline:
            self.api.save_wav(chirp.shortcode, filename)
        else:
            self.audio_generator.save_wav(chirp.longcode, filename)
        return filename

    def encode(self, shortcode):
        """ Encodes a shortcode to a longcode by adding error-correction bits."""
        return self.api.encode(shortcode)['longcode']

    def decode(self, longcode):
        """ Decodes a longcode to shortcode."""
        return self.api.decode(longcode)['shortcode']
