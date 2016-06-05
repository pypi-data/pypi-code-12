import logging
from ch_solutions.util.dir_tools import make_dir
from ch_solutions.util.scripts import get_script_name


def get_logger(name=None, master=False, verbose=False, level=None, logname=None, path=None):
    # Set the following options only if we are the master logger
    if master:
        if name is None:
            logger = logging.getLogger(get_script_name())
        else:
            logger = logging.getLogger(name)
        # Make sure that a logfile name has been passed. We will store all logs in /var/log/scripts
        if logname is None:
            raise ValueError('"logname" must be specified for master logger.')

        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

        # Set the level if it is not defined
        if level not in log_levels or level is None:
            level = 'INFO'
        else:
            level = level.upper()

        # Define Static formats and paths
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_datefmt = '%Y-%m-%d %H:%M:%S'

        # Allowing path change for development purposes
        if path:
            log_path = str(path)
        else:
            log_path = '/var/log/scripts/'

        # Make sure log_path exists
        make_dir(log_path)

        # Set formatting for all loggers
        formatting = logging.Formatter(log_format, log_datefmt)

        # Setup the File logger
        fh = logging.FileHandler(log_path + logname)
        fh.setLevel(log_levels[level])
        fh.setFormatter(formatting)
        logger.addHandler(fh)

        # Make sure that we are adding a console logger if verbose is called
        if verbose:
            ch = logging.StreamHandler()
            ch.setLevel(log_levels[level])
            ch.setFormatter(formatting)
            logger.addHandler(ch)

        # Set the logging level overall as well.
        logger.setLevel(log_levels[level])
        return logger
    else:
        if name is None:
            raise ValueError('"name" must be specified for child loggers.')
        else:
            return logging.getLogger(get_script_name()).getChild(name)
