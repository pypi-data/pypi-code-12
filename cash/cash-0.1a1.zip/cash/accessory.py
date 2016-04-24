# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from errno import EACCES, ENOTDIR
from os import getcwd, makedirs, remove, strerror
from time import timezone

def create_directory(dir_abs_path, mode=0o770, messages=None):
    """Recursive directory creation function
    os.chmod work only for last directory

    """

    try:
        makedirs(dir_abs_path, mode)
    except Exception as exception:
        error_code = exception.errno
        if error_code == EACCES: # 13 (Python 3 PermissionError)
            if messages != None:
                raise Exception(messages["_critical_NoRoot"])
            else:
                raise
        elif error_code == ENOTDIR: # 20 (Python 3 NotADirectoryError)
            path = dir_abs_path
            while path != '/':
                if isfile(path):
                    try:
                        remove(path)
                    except Exception as exception: # Python 3 PermissionError
                         error_code = exception.errno
                         if error_code == EACCES: # 13
                             if messages != None:
                                 raise Exception(messages["_critical_NoRoot"])
                             else:
                                 raise
                         else:
                             if messages != None:
                                 raise Exception(
                                         messages["_critical_Oops"] %
                                         strerror(error_code))
                             else:
                                 raise
                path = dirname(path)
            try:
                makedirs(Directoey_name, mode)
            except Exception as exception: # Python 3 PermissionError
                error_code = exception.errno
                if error_code == EACCES: # 13
                    if messages != None:
                        raise Exception(messages["_critical_NoRoot"])
                    else:
                        raise
                else:
                    if messages != None:
                        raise Exception(
                                messages["_critical_Oops"] %
                                strerror(error_code))
                    else:
                        raise
        else:
            if messages != None:
                raise Exception(
                        messages["_critical_Oops"] %
                        strerror(error_code))
            else:
                raise

def get_date_time():
    """Get yyyy-mm-ddThh:mm:ss±hh:mm"""

    def normalize(element):
        """Add '0' from front"""

        if len(element) == 1:
            element = '0' + element
        return element

    tz = ""

    now = datetime.now()
    year = str(now.year)
    month = normalize(str(now.month))
    day = normalize(str(now.day))
    hour = normalize(str(now.hour))
    minute = normalize(str(now.minute))
    second = normalize(str(now.second))
    date = year + '-' + month + '-' + day
    time = hour + ':' + minute + ':' + second
    time_zone = timezone
    if time_zone <= 0:
        tz += '+'
    else:
        tz += '-'
    time_zone = abs(time_zone)
    if time_zone == 0:
        tz += "00:00"
    else:
        tz_list = str(timedelta(seconds=time_zone)).split(':')
        tz += normalize(tz_list[0]) + ':' + normalize(tz_list[1])
    date_time =  date + 'T' + time + tz
    return date_time
