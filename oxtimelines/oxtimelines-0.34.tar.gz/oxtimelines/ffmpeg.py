# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2014
from __future__ import division, with_statement, print_function

import fractions
import subprocess

import Image
import numpy as np
import ox


FFMPEG = None
for cmd in ('ffmpeg', 'avconv'):
    cmd = ox.file.cmd(cmd)
    if subprocess.call(['which', cmd], stdout=subprocess.PIPE) == 0:
        FFMPEG = cmd
        break
if not FFMPEG:
    print("could not find ffmpeg, make sure its installed and available in PATH")
FPS = 25

class Video(object):

    framerate = FPS
    samplerate = 48000

    def __init__(self, path, height, audio, video_callback, done_callback):
        self.height = height
        self.video = self.height > 0
        self.audio = audio

        self.video_callback = video_callback
        self.done_callback = done_callback
        self.path = path

        self.info = info = ox.avinfo(self.path)
        self.duration = info['duration']
        self.audio = self.audio and info['audio'] != []
        self.video = self.video and info['video'] != []
        if self.video:
            ratio = info['video'][0]['width'] / info['video'][0]['height']
            self.width = int(round(self.height * ratio))
            if self.width % 4:
                self.width += 4 - self.width % 4

        if self.audio:
            self.volume = []
            self.channels = 2

    def decode(self, points=None):
        if points:
            self.in_time = points[0]
            self.out_time = points[1]
        else:
            self.in_time = 0
            self.out_time = self.duration
        if self.video:
            timestamp = 0
            for frame in video(self.path, height=self.height, info=self.info, framerate=self.framerate):
                if self._is_between_in_and_out(timestamp):
                    self.video_callback(frame, timestamp)
                timestamp += 1/self.framerate
        if self.audio:
            timestamp = 0
            for frame in audio(self.path, info=self.info, samplerate=self.samplerate, framerate=self.framerate):
                if self._is_between_in_and_out(timestamp):
                    frame = rms(frame, 0) / self.samplerate
                    self.volume.append(frame)
                timestamp += 1/self.framerate
            # m = max(max(self.volume, key=lambda v: max(v)))
            # self.volume = [(v[0]/m, v[1]/m) for v in self.volume]
        self.done_callback(self.volume if self.audio else [])

    def get_duration(self):
        return self.duration

    def get_size(self):
        return (self.width, self.height)

    def _is_between_in_and_out(self, timestamp):
        return timestamp >= self.in_time and timestamp < self.out_time

def video(path, height=96, info=None, framerate=FPS):
    depth = 3

    if not info:
        info = ox.avinfo(path)
    dar = AspectRatio(info['video'][0]['display_aspect_ratio'])
    width = int(dar * height)
    width += width % 2
    nbytes= depth * width * height
    bufsize = nbytes + 100

    cmd = [
        FFMPEG,
        '-loglevel', 'error',
        '-i', path,
        '-threads', '4',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-vcodec', 'rawvideo',
        '-vf', 'scale=%d:%d' % (width, height),
        '-aspect', '%d:%d' % (width, height),
        '-r', str(framerate),
        '-'
    ]
    #print(' '.join(cmd))
    p = subprocess.Popen(cmd,
        bufsize=bufsize,
        stdout=subprocess.PIPE,
        stderr=open('/dev/null', 'w'),
        close_fds=True)

    first = True
    while True:
        data = p.stdout.read(nbytes)
        if len(data) != nbytes:
            if first:
                raise IOError("ERROR: could not open file %s" % path)
            else:
                return
        else:
            first = False
            yield Image.frombytes('RGB', (width, height), data)

def audio(path, info=None, samplerate=48000, framerate=FPS):
    depth = 2
    channels = 2

    if not info:
        info = ox.avinfo(path)

    nbytes = depth * samplerate * channels
    bufsize = nbytes + 100

    #'-loglevel', 'error'
    cmd = [
        FFMPEG,
        '-i', path,
        '-vn',
        '-ar', str(samplerate),
        '-ac', str(channels),
        '-acodec', 'pcm_s16le',
        '-f', 'wav',
        '-'
    ]
    # print(' '.join(cmd))
    p = subprocess.Popen(cmd,
                         bufsize=bufsize,
                         stdout=subprocess.PIPE,
                         stderr=open('/dev/null', 'w'),
                         close_fds=True)
    chunk = int(nbytes / framerate)
    first = True
    while True:
        data = p.stdout.read(chunk)
        if len(data) != chunk:
            if first:
                raise IOError("ERROR: frame data has wrong size")
            else:
                return
        else:
            first = False
            audio = np.fromstring(data, dtype="int16")
            audio = audio.reshape((int(len(audio)/channels), channels)).astype('float')
            yield audio

def rms(x, axis=None):
    return np.sqrt(np.mean(x**2, axis=axis))

class AspectRatio(fractions.Fraction):

    def __new__(cls, numerator, denominator=None):
        if not denominator:
            ratio = map(int, numerator.split(':'))
            if len(ratio) == 1:
                ratio.append(1)
            numerator = ratio[0]
            denominator = ratio[1]
            # if its close enough to the common aspect ratios rather use that
            if abs(numerator/denominator - 4/3) < 0.03:
                numerator = 4
                denominator = 3
            elif abs(numerator/denominator - 16/9) < 0.02:
                numerator = 16
                denominator = 9
        return super(AspectRatio, cls).__new__(cls, numerator, denominator)

    @property
    def ratio(self):
        return "%d:%d" % (self.numerator, self.denominator)

