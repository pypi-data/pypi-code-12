# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.


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