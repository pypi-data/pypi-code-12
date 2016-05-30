import traceback

import datetime
import os
import logging
import numpy as np

# Python 2/3 compatibility
import six
try:
    from urllib.request import urlopen
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
    from urllib import urlopen

import auroraplot as ap
import auroraplot.magdata
import auroraplot.datasets.aurorawatchnet as awn
from auroraplot.magdata import MagData
from auroraplot.magdata import MagQDC
from auroraplot.temperaturedata import TemperatureData
from auroraplot.voltagedata import VoltageData

logger = logging.getLogger(__name__)

data_dir = '/data/sam'

def convert_date(s):
    dmy = map(int, s.split('.'))
    if dmy[2] >= 90:
        dmy[2] += 1900
    else:
        dmy[2] += 2000
    return np.datetime64(datetime.date(*list(reversed(dmy))))

def convert_time(s):
    hms = map(int, s.split(':')[0:3])
    return np.timedelta64(1000000 * (hms[0] * 3600 + hms[1] * 60 + hms[2]), 'us')
    
def convert_data(s):
    f = s.split(',')
    if len(f) != 7:
        raise('Bad format')
    return map(lambda n: float(n), f[1:6:2])
    # return map(float, s.split(',')[1:6:2])

def check_data(data):
    #data[0:2,np.logical_or(data[0:2] < -0.000003, data[0:2] > 0.000003)]
    data[0][np.logical_or(data[0] < -0.00003, data[0] > 0.00003)] = np.nan
    data[1][np.logical_or(data[1] < -0.00003, data[1] > 0.00003)] = np.nan
    data[2][np.logical_or(data[2] < -0.0001, data[1] > 0.0001)] = np.nan
    return data


def load_sam_data(file_name, archive_data, 
                  project, site, data_type, channels, start_time, 
                  end_time, **kwargs):
    '''Convert Mull mangetometer data to match standard data type

    data: MagData or other similar format data object
    archive: name of archive from which data was loaded
    archive_info: archive metadata
    '''
    data_type_info = {
        'MagData': {
            'class': MagData,
            'scaling': 1e-9,
            },
        'MagQDC': {
            'class': MagQDC,
            'scaling': 1e-9,
            },
        }

    assert data_type_info.has_key(data_type), 'Illegal data_type'
    chan_tup = tuple(archive_data['channels'])
    col_idx = []
    for c in channels:
        col_idx.append(chan_tup.index(c))

    try:
        if file_name.startswith('/'):
            uh = urlopen('file:' + file_name)
        else:
            uh = urlopen(file_name)
        try:
            lines = uh.readlines()
            sample_start_time = np.zeros([len(lines)], dtype='M8[us]')
            data = np.tile(np.nan, [3, len(lines)])

            n = 0
            for line in lines:
                try:
                    # Extract and parse everything in case of errors
                    dmy, hms, xyz, temperature, = line.split()
                    sample_start_time[n] = convert_date(dmy) + convert_time(hms)
                    data[:, n] = convert_data(xyz)
                    n += 1
                except:
                    print('Could not process "' + line + '"')
            if n != len(lines):
                # Some lines were bad
                data = data[:,0:n]
                sample_start_time = sample_start_time[0:n]

            # data = check_data(data)

            # Trim data to desired channels
            data = data[col_idx]
                       
            integration_interval = \
                np.tile(10000000, [len(channels), 
                                   len(sample_start_time)]).astype('m8[us]')

            sample_end_time = sample_start_time + \
                archive_data['nominal_cadence']

            if data_type_info[data_type].has_key('scaling'):
                data *= data_type_info[data_type]['scaling']
            
            try:
                r = data_type_info[data_type]['class']( \
                    project=project,
                    site=site,
                    channels=channels,
                    start_time=start_time,
                    end_time=end_time,
                    sample_start_time=sample_start_time, 
                    sample_end_time=sample_end_time,
                    integration_interval=integration_interval,
                    nominal_cadence=archive_data['nominal_cadence'],
                    data=data,
                    units=archive_data['units'],
                    sort=False)
            except Exception as e:
                print(traceback.format_exc())
                print(e)
            return r

        except Exception as e:
            logger.info('Could not read ' + file_name)
            logger.debug(str(e))

        finally:
            uh.close()
    except Exception as e:
        logger.info('Could not open ' + file_name)
        logger.debug(str(e))

    return None


sites = {
    'MULL': {
        'location': 'Mull, UK',
        'latitude': 56.3958,
        'longitude': -6.04167,
        'elevation': 3,
        'start_time': np.datetime64('2006-12-01T00:00Z'),
        'end_time': None, # Still operational
        'k_index_scale': 750e-9, # Estimated, based on BGS Eskdakemuir site
        'copyright': 'Roger Blackwell',
        'license': '',
        'attribution': 'Data provided by Roger Blackwell GM4PMK.', 
        'data_types': {
            'MagData': {
                'realtime': {
                    'channels': np.array(['X', 'Y', 'Z']),
                    'path': os.path.join(data_dir,
                                         'mull/%Y/%m/%Y%m%d.txt'),
                    'duration': np.timedelta64(24, 'h'),
                    'format': 'aurorawatchnet',
                    'load_converter': load_sam_data,
                    'nominal_cadence': np.timedelta64(10, 's'),
                    'units': 'T',
                    },
                },
            'MagQDC': {
                'qdc': {
                    'channels': np.array(['X', 'Y', 'Z']),
                    'path': os.path.join(data_dir, 
                                         'mull/qdc/%Y/mull_qdc_%Y%m.txt'),
                    'duration': np.timedelta64(24, 'h'),
                    'format': 'aurorawatchnet_qdc',
                    'load_converter': ap.magdata.load_qdc_data,
                    'nominal_cadence': np.timedelta64(5, 's'),
                    'units': 'T',
                    },
                },
            },
        }, # MULL
    }
        
# Set activity color/thresholds unless already set.
default_activity_thresholds = np.array([0.0, 50.0, 100.0, 200.0]) * 1e-9
default_activity_colors = np.array([[0.2, 1.0, 0.2],  # green  
                                    [1.0, 1.0, 0.0],  # yellow
                                    [1.0, 0.6, 0.0],  # amber
                                    [1.0, 0.0, 0.0]]) # red
for s in sites:
    if not sites[s].has_key('activity_thresholds'):
        sites[s]['activity_thresholds'] = default_activity_thresholds
    if not sites[s].has_key('activity_colors'):
        sites[s]['activity_colors'] = default_activity_colors
    
project = {
    'name': 'Simple Aurora Monitor',
    'abbreviation': 'SAM',
    'url': 'http://www.sam-magnetometer.net/',
    'sites': sites,
}

ap.add_project('SAM', sites)
