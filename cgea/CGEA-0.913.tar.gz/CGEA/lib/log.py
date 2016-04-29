# logging utlities

import logging

# logs on shell
def slogger (name):
    log = logging.getLogger (name)
    log.setLevel (logging.INFO)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', "%d-%m-%Y %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


# logs on file
def logger (name, basepath):
    log = logging.getLogger(name)
    log.setLevel (logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', "%d-%m-%Y %H:%M:%S")

    # info
    hfile_info = logging.FileHandler(basepath+"info.log")
    hfile_info.setFormatter(formatter)
    hfile_info.setLevel(logging.INFO)
    log.addHandler(hfile_info)

    # error
    hfile_error = logging.FileHandler(basepath+"error.log")
    hfile_error.setFormatter(formatter)
    hfile_error.setLevel(logging.ERROR)
    log.addHandler(hfile_error)
    
    # debug
    hfile_debug = logging.FileHandler(basepath+"debug.log")
    hfile_debug.setFormatter(formatter)
    hfile_debug.setLevel(logging.DEBUG)
    log.addHandler(hfile_debug)
    
    
    # return
    return log


