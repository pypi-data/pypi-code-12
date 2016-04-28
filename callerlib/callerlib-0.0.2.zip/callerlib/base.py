import settings
from .report import Report

from robotremoteserver import RobotRemoteServer


class CallerKeywords(object):
    def __init__(self, host='0.0.0.0', port=5060):
        self.report = Report()
        self.host = host
        self.port = port

    def init_call(self):
        self.report.info('Init Call')


class CallerLib(object):
    def __init__(self):
        self.library = CallerKeywords(settings.SIP_HOST, settings.SIP_PORT)
        RobotRemoteServer(library=self.library, host=settings.RF_HOST, port=settings.RF_PORT)
