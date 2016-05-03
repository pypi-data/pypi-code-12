#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

import struct
import math
import wave

import pyaudio

from .constants import *
from .util import char_to_frequency


class AudioSession(object):
    """ Plays audio to sound hardware from an AudioGenerator object. """

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.generator = AudioGenerator()
        self.stream = self.pyaudio.open(format=pyaudio.paInt16,
                                        rate=int(CHIRP_SAMPLERATE),
                                        channels=1,
                                        output=True)

    def play(self, longcode):
        """ Play a longcode. Prepends frontdoor. """
        frames = self.generator.generate(CHIRP_FRONTDOOR + longcode)
        self.stream.write(frames)

    def close(self):
        """ End this audio session. """
        self.stream.close()
        self.pyaudio.terminate()


class AudioWavetable(object):
    """ Generates a fixed-size table of sinosoidal samples and steps through
    it based on a given frequency, with linear interpolation.
    """

    def __init__(self, wavetable_length = 4096):
        # Array of raw floats comprising a sinusoidal waveform
        self.wavetable_length = wavetable_length
        self.wavetable = [math.sin(2.0 * math.pi * n / wavetable_length)
                          for n in range(wavetable_length)]
        self.wavetable.append(self.wavetable[0])
        self.wavetable.append(self.wavetable[1])

        # Wavetable phase
        self.phase = 0.0
        self.phase_inc = 0.0

    def set_frequency(self, frequency):
        self.phase_inc = frequency * self.wavetable_length / CHIRP_SAMPLERATE

    def next(self):
        phase_round = int(self.phase)
        phase_fraction = self.phase - phase_round

        # Update wavetable phase
        self.phase += self.phase_inc;
        if self.phase > self.wavetable_length:
            self.phase -= self.wavetable_length
        if self.phase < 0:
            self.phase += self.wavetable_length

        # Calculate return value via linear interpolation
        return (self.wavetable[phase_round] + phase_fraction *
                (self.wavetable[phase_round + 1] - self.wavetable[phase_round]))


class AudioGenerator(object):
    """ Class to generate audio samples for a chirp. """

    def __init__(self):
        self.wavetable = AudioWavetable()
        self.base_frequency = CHIRP_BASE_FREQUENCY
        self.interval = CHIRP_INTERVAL

    def generate(self, code):
        data = b''
        freq = None
        freq_target = None
        freq_change_per_sample = 0.0
        amp = 0.0
        sample_cnt = 0

        for letter in code:
            try:
                freq_target = char_to_frequency(letter, self.base_frequency, self.interval)

                if freq is None:
                    freq = freq_target
                if porta > 0:
                    freq_change_per_sample = (freq_target - freq) / float (porta_samples)
                else:
                    freq_change_per_sample = 0
                    freq = freq_target

            except ValueError as e:
                print('Warning: character "%s" not found in CHIRP_ALPHABET, skipping' % letter)
                for n in range(note_length_samples):
                    data = data + struct.pack('h', 0)
                    sample_cnt += 1
                continue

            for n in range(note_length_samples):
                if n < env_attack_samples :
                    amp = env_sustain * n / float(env_attack_samples)
                elif n < note_length_samples - env_release_samples:
                    amp = env_sustain
                else:
                    amp = (env_sustain * (1.0 - ((n - (
                        float(note_length_samples - env_release_samples))
                    ) / float(env_release_samples))))

                if n < porta_samples:
                    freq += freq_change_per_sample

                # Update internal phase increment based on desired frequency
                self.wavetable.set_frequency(freq)

                sample = self.wavetable.next() * master_vol * amp * FLOAT_TO_SHORT
                data = data + struct.pack('h', int(sample))

        return data

    def save_wav(self, code, filename):
        wav = wave.open(filename, 'wb')
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(self.generate(code))
        wav.close()
