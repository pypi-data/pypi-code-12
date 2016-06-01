import logging




def emit_colored_ansi(fn):
    def new(*args):
        levelno = args[1].levelno
        if(levelno >= 50):
            color = '\x1b[31m'  # red
        elif(levelno >= 40):
            color = '\x1b[31m'  # red
        elif(levelno >= 30):
            color = '\x1b[33m'  # yellow
        elif(levelno >= 20):
            color = '\x1b[32m'  # green
        elif(levelno >= 10):
            color = '\x1b[35m'  # pink
        else:
            color = '\x1b[0m'  # normal
        args[1].levelname = color + args[1].levelname + '\x1b[0m'  # normal
        return fn(*args)
    return new


def init_logger(name, directory=".", log_level=logging.DEBUG,
                log_to_file=True, log_to_screen=True, color=True,**kwargs):
    """Set up a logging system

    Parameters
    ----------

    name : str
        The name of the log file
    directory : str
        The path where the log file is to be stored
    log_level : logging.LOG_LEVEL
        A logging loglevel object. Controlling which messages are to be 
        displayed.

    Returns
    -------

    log : a logging.getLogger object.

    Examples
    --------

    The returned object can be used to for log messages::

        >>> log.info("MESSAGE")
        >>> log.log("MESSAGE")
        >>> log.debug("MESSAGE")
        >>> log.warning("MESSAGE")
        >>> log.error("MESSAGE")
        >>> log.critical("MESSAGE")
"""

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    # The handler should only be set once for matching logger_names
    if not getattr(log, 'handler_set', None):
        formatter = logging.Formatter('%(asctime)s  %(levelname)s: '\
                                      '(%(module)s %(funcName)s) '
                                      '%(message)s', "%Y-%m-%dT%H:%M:%S")
        if log_to_file:
            log_file = logging.FileHandler("{}/{}.log".format(directory,
                                                          name))
            log_file.setFormatter(formatter)
            log_file.setLevel(logging.DEBUG)
            log.addHandler(log_file)
        if log_to_screen:
            prt_screen = logging.StreamHandler()
            prt_screen.setLevel(logging.DEBUG)
            prt_screen.setFormatter(formatter)
            log.addHandler(prt_screen)
            if color:
               logging.StreamHandler.emit = emit_colored_ansi(logging.StreamHandler.emit)
        log.handler_set = True
    return log
