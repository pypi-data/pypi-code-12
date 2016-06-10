import os
import re
import glob
from copy import copy

from six import iteritems


def sensors():
    """ Get list of sensors available """
    dirs = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*'))
    return sorted([os.path.basename(s) for s in dirs if os.path.isdir(s)])


class TestDataErrors(Exception):
    pass


class TestData(object):

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

    def __init__(self, sensor):
        """ Initialize testdata for a sensor """

        if sensor in sensors():
            self.sensor = sensor
        else:
            raise TestDataErrors('Sensor is not supported')

        sensor_path = glob.glob(os.path.join(self.path, sensor))

        examples = [f for f in os.listdir(sensor_path[0]) if os.path.isdir(os.path.join(sensor_path[0], f))]

        # load bandmap
        bands = {
            'landsat8': {
                'B1': 'coastal',
                'B2': 'blue',
                'B3': 'green',
                'B4': 'red',
                'B5': 'nir',
                'B6': 'swir1',
                'B7': 'swir2',
                'B8': 'pan',
                'B9': 'cirrus',
                'BQA': 'quality'
            },
            'sentinel2': {
                'B01': 'coastal',
                'B02': 'blue',
                'B03': 'green',
                'B04': 'red',
                'B08': 'nir',
                'B10': 'cirrus',
                'B11': 'swir1',
                'B12': 'swir2'
            }
        }

        fields = dict(zip(['band_name', 'band_type', 'filename', 'path'], [None, None, None, None]))

        # generate the sekeleton
        self.list = {}
        for k, v in iteritems(bands[sensor]):
            temp = copy(fields)
            temp['band_name'] = k
            temp['band_type'] = v
            self.list[k] = temp

        # generate examples skeleton
        self.examples = {}
        self.files_bands = {}
        self.files = {}
        self.bands = {}
        for example in examples:
            self.examples[example] = self.list
            self.files_bands[example] = {}
            self.files[example] = []
            self.bands[example] = []

            # fill in filenames and path
            files = glob.glob(os.path.join(self.path, sensor, example, '*.*'))
            for f in files:
                search = re.search('(B.{1,3})\.', f)
                if search:
                    band = search.group(0).replace('.', '')
                    if band in self.examples[example]:
                        self.examples[example][band]['path'] = f
                        self.examples[example][band]['filename'] = os.path.basename(f)
                        self.files_bands[example][f] = [self.examples[example][band]['band_type']]
                        self.files[example].append(f)
                        self.bands[example].append(self.examples[example][band]['band_type'])

        self.names = examples

    @classmethod
    def is_dir(cls, path):
        return os.path.isdir(os.path.join(cls.path, path))
