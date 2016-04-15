# The MIT License (MIT)
#
# Copyright (c) 2016 CNRS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


import os.path as op
import pyannote.parser


class Etape(object):
    """ODESSA-ETAPE speaker diarizaiont

    Parameters
    ----------
    wav_dir : string
        Path to ETAPE audio files.

    Usage
    -----
    >>> etape = Etape(wav_dir="/path/to/wav_dir/")
    >>> for wav, annotated, annotation in etape.train_iter():
    ...     pass

    """

    def __init__(self, wav_dir):
        super(Etape, self).__init__()
        self.wav_dir = wav_dir

    def _subset_iter(self, subset):

        # load training file
        mdtm_path = op.join(
            op.dirname(op.realpath(__file__)),
            'data/mdtm/{subset}.mdtm'.format(subset=subset))

        # load evaluation maps
        path = op.join(
            op.dirname(op.realpath(__file__)),
            'data/uem/{subset}.uem'.format(subset=subset))
        uems = pyannote.parser.UEMParser().read(path)

        # load reference
        path = op.join(
            op.dirname(op.realpath(__file__)),
            'data/mdtm/{subset}.mdtm'.format(subset=subset))
        mdtms = pyannote.parser.MDTMParser().read(path)

        for uri in uems.uris:
            annotated = uems(uri)
            annotation = mdtms(uri)
            wav = op.join(self.wav_dir, '{uri}.wav'.format(uri=uri))
            yield wav, annotated, annotation

    def train_iter(self):
        return self._subset_iter('elda-trn')

    def dev_iter(self):
        return self._subset_iter('elda-dev')

    def test_iter(self):
        return self._subset_iter('eval')
