import time
import logging
from robotremoteserver import RobotRemoteServer

from .conf import settings

logger = logging.getLogger(__name__)


class Report(object):
    @staticmethod
    def fail(msg):
        print '*FAIL:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def warn(msg):
        print '*WARN:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def info(msg):
        print '*INFO:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def debug(msg):
        print '*DEBUG:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def html(msg):
        print '*HTML:{}* {}'.format(time.time()*1000, msg)


class CallerKeywords(object):
    def __init__(self, host='0.0.0.0', port=5060):
        logger.debug('Init CallerKeywords object')
        self.report = Report()
        self.host = host
        self.port = port

    def init_call(self):
        logger.debug('Start init call')
        self.report.info('Init Call')
        logger.debug('Stop init call')


class CallerLib(object):
    def __init__(self):
        self.library = CallerKeywords(host=settings.SIP_HOST, port=settings.SIP_PORT)
        RobotRemoteServer(library=self.library, host=settings.RF_HOST, port=settings.RF_PORT)
