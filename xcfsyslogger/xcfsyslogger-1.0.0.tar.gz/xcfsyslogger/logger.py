# coding: utf-8
import logging
import logging.config
import logging.handlers
import os
import simplejson


def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
):
    """Setup logging configuration

    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = simplejson.loads(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


class SysLogHandler(logging.handlers.SysLogHandler):

    def emit(self, record):
        if isinstance(record.msg, str):
            # RFC says we should prefix with BOM, but rsyslog will log the BOM
            record.msg = record.msg.decode('utf-8')
        return super(SysLogHandler, self).emit(record)


def syslogger(logname, loglevel=logging.INFO, path=None):
    logger = logging.getLogger(logname)
    for handler in logger.handlers:
        if isinstance(handler, SysLogHandler):
            return logger

    if not path:
        path = logname.strip(' /').replace('.', '/')
    handler = syslogger_handler(path, loglevel)
    logger.setLevel(loglevel)
    logger.propagate = False
    logger.addHandler(handler)
    return logger


def syslogger_handler(path, loglevel=logging.INFO):
    formatter = logging.Formatter('{} %(levelname)s %(message)s'.format(path))
    syslog = SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_LOCAL0)
    syslog.setFormatter(formatter)
    syslog.setLevel(loglevel)

    return syslog
