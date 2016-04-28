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
    def __init__(self, rf_host='0.0.0.0', rf_port=8100, sip_host='0.0.0.0', sip_port=5060):
        self.library = CallerKeywords(host=sip_host, port=sip_port)
        RobotRemoteServer(library=self.library, host=rf_host, port=rf_port)
