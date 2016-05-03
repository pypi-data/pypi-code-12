#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

# Chirp
CHIRP_ALPHABET = "0123456789abcdefghijklmnopqrstuv"
CHIRP_FRONTDOOR = "hj"
CHIRP_LENGTH = 10
CHIRP_REED_SOLOMON_LENGTH = 8
CHIRP_LONGCODE_LENGTH = CHIRP_LENGTH + CHIRP_REED_SOLOMON_LENGTH
CHIRP_SHORTCODE_PATTERN = '^[%s]{%d}$' % (CHIRP_ALPHABET, CHIRP_LENGTH)
CHIRP_LONGCODE_PATTERN = '^[%s]{%d}$' % (CHIRP_ALPHABET, CHIRP_LONGCODE_LENGTH)

# API
API_HOST = "api.chirp.io"
API_ENDPOINT_ROOT = "/v1"
API_ENDPOINT_AUTHENTICATE = "/authenticate"
API_ENDPOINT_CHIRP = "/chirps"
API_ENDPOINT_CHIRP_ENCODE = "/chirps/encode"
API_ENDPOINT_CHIRP_DECODE = "/chirps/decode"

# Audio
CHIRP_BASE_FREQUENCY = 1760.0
CHIRP_INTERVAL = 0
CHIRP_SAMPLERATE = 44100.0
MIDI_NOTE_RATIO = 1.0594630943591

# Envelope specs (seconds)
master_vol = 0.4
note_length = 0.0872

# Portamento time (seconds)
porta = 0.008

# Attack and release as a percent of total note length
env_attack = 0.05 * note_length
env_release = 0.05 * note_length
env_sustain = 1.0

# Values in samples
note_length_samples = int(note_length * CHIRP_SAMPLERATE)
env_attack_samples = int(env_attack * CHIRP_SAMPLERATE)
env_release_samples = int(env_release * CHIRP_SAMPLERATE)
porta_samples = int(porta * CHIRP_SAMPLERATE)

FLOAT_TO_SHORT = 32768.0
