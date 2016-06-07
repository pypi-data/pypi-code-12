# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import pprint


class PumpIsAlreadyRunning(Exception):
    def __init__(self, running_task):
        self.running_task = running_task


class PipeAlreadyExists(Exception):
    pass


class SystemAlreadyExists(Exception):
    pass


class TimeoutWhileWaitingForRunningPumpToFinishException(Exception):
    pass


class InternalServerError(Exception):
    """This is raised when the server has responded with a 5xx statuscode"""
    pass


class BadRequestException(Exception):
    """This is raised when the server has responded with a 400 statuscode"""
    pass


class ConfigUploadFailed(BadRequestException):
    """This is raised when the server has responded with a 400 statuscode on a configuration upload request. The
    reponse object is stored in the 'response' attribute. The json payload of the response is stored in the
    'parsed_response' attribute."""
    def __init__(self, response, parsed_response):
        self.response = response
        self.parsed_response = parsed_response
        super().__init__("Config upload failed! response:\n%s" % (pprint.pformat(self.parsed_response),))

