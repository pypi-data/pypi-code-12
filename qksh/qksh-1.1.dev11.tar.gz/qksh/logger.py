import logging


def create_logger(level='INFO'):
    """
    :parameter level: set log level

    Creates a logger for the given application.  This logger works
    similar to a regular Python logger but changes the effective logging
    level based on the application's debug flag.
    """

    logger = logging.getLogger('ihealth_api')
    logger.setLevel(logging.DEBUG)

    # TODO: create log foleder, also adding log rotate
    # currently it requires root permission in order to write log under
    # /var/log folder, to workaround that, need to create a subfolder with
    # user permission and put log under that subfolder, however, it still
    # requires root permission the first time to setup the program.

    fh = logging.FileHandler("/var/log/qksh/qksh.log")
    if level == 'DEBUG':
        fh.setLevel(logging.DEBUG)
    else:
        fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        # fmt='%(asctime)s %(levelname)s %(module)s[%(process)s]'
        #     ': %(message)s',
        fmt='%(asctime)s %(levelname)s %(module)s[%(process)s]'
            ' line:%(lineno)d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
