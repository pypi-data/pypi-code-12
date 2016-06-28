import logging
import json
import math
import os
import re
import subprocess
import urllib2

import numpy
import utm

import settings

class BuoyDataError(Exception):
    """ Exception for lack of buoy data in the expected file. """
    def __init__(self, msg):
        self.msg=msg

    def __str__(self):
        return repr(self.msg)

def find_datasets(cc):
    """
    Get list of possible datasets. 

    Args:
        cc: Calibration contoller instance, for metadata

    Returns:
        datasets, coordinates, depths: lists of buoy ids, their coordinates, and their depths

    Notes:
        The station_table.txt file is hugely inconsistent and not really computer-friendly.
        Changed to a json file holding only what is necesary.
    """

    ur_lat = cc.metadata['CORNER_UR_LAT_PRODUCT']
    ur_lon = cc.metadata['CORNER_UR_LON_PRODUCT']
    ll_lat = cc.metadata['CORNER_LL_LAT_PRODUCT']
    ll_lon = cc.metadata['CORNER_LL_LON_PRODUCT']

    filename = os.path.join(settings.PACKAGE_BASE, 'data', 'station_table.json')

    stations = []
    with open(filename, 'r') as f:
        stations = json.load(f)

    datasets = []
    coordinates = []
    depths = []

    for i in range(len(stations['stations'])):
        buoy_lat = stations['lat'][i]
        buoy_lon = stations['lon'][i]

        if buoy_lat > ll_lat and buoy_lat < ur_lat:
            if buoy_lon > ll_lon and buoy_lon < ur_lon:
                datasets.append(stations['stations'][i])
                coordinates.append([stations['lat'][i], stations['lon'][i]])
                depths.append(stations['depth'][i])

    return datasets, coordinates, depths

def get_buoy_data(filename, url):
    """
    Download/ unzip appripriate buoy data from url.

    Args:
        filename: path/file to save buoy data file
        url: url to download data from

    Returns:
        True or False: depending on whether or not it has been downloaded 

    """

    try:
        # open url
        f = urllib2.urlopen(url)

        # write data to file

        with open(filename, "wb") as local_file:
            local_file.write(f.read())

        # unzip if it is still zipped 
        # TODO replace with python unzip method
        if '.gz' in filename:
            subprocess.check_call('gzip -d -f '+filename, shell=True)
            # subprocess.Popen('rm '+filename, shell=True)

    except urllib2.HTTPError, e:
        return False
    except urllib2.URLError, e:
        logging.error("URL Error:", e.reason, url)
        return False
    except OSError, e:
        logging.error('OSError: ', e.reason, filename)
        return False

    return True


def find_skin_temp(cc, filename, depth):
    """
    Convert bulk temp -> skin temperature.

    Args:
        cc: calibrationcontroller object, for data and time information
        filename: filename to get data from
        depth: depth of thermometer on buoy

    Returns:
        skin_temp, pres, atemp, dewp: all parameters of the buoy

    Raises:
        BuoyDataError: if no data, date range wrong, etc.

    Notes:
        source: https://www.cis.rit.edu/~cnspci/references/theses/masters/miller2010.pdf
    """

    hour = cc.scenedatetime.hour
    
    date = cc.date.strftime('%Y %m %d')
    data = []

    with open(filename, 'r') as f:
        for line in f:
            if date in line:
                data.append(line.strip('\n').split())

    if data == []:
        raise BuoyDataError('No data in file? %s.'% filename)
        
    data = numpy.asarray(data, dtype=float)
    #print data

    # compute 24hr wind speed and temperature
    avg_wspd = data[:,6].mean()   # [m s-1]
    avg_wtmp = data[:,14].mean()   # [C]
    
    pres = data[:,12].mean()
    atemp = data[:,13].mean()
    dewp = data[:,15].mean()

    # calculate skin temperature
    # part 1
    a = 0.05 - (0.6 / avg_wspd) + (0.03 * math.log(avg_wspd))
    z = depth   # depth in meters
    
    avg_skin_temp = avg_wtmp - (a * z) - 0.17

    # part 2
    b = 0.35 + (0.018 * math.exp(0.4 * avg_wspd))
    c = 1.32 - (0.64 * math.log(avg_wspd))
    
    t = int(hour - (c * z))
    T_zt = float(data[t][14])    # temperature data from closest hour
    f_cz = (T_zt - avg_skin_temp) / math.exp(b*z)

    # combine
    skin_temp = avg_skin_temp + f_cz + 273.15

    if skin_temp >= 600:
        raise BuoyDataError('No water temp data for selected date range in the data set %s.'% filename)

    return skin_temp, pres, atemp, dewp
