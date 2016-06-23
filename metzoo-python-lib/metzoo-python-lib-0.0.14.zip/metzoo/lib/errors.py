# -*- coding: utf-8 -*-

class MetzooError(Exception):
    """Base class for metzoo errors"""

class AgentError(MetzooError):
    """Base class for agent errors"""

    def __init__(self, status, reason):
        self.__status = status
        self.__reason = reason

    def __str__(self):
        return "AgentError {}: {}".format(self.__status, self.__reason)


class AgentCreationError(AgentError):
    """Something went wrong creating an agent"""

class AgentDataError(AgentError):
    """Something went wrong sending data for an agent"""

class MetzooInvalidData(MetzooError):
    """Expected data with a structure, found another one"""

    def __init__(self, got, expected):
        self.__got = str(got)
        self.__expected = str(expected)

    def __str__(self):
        return "got {} but expected {}".format(self.__got, self.__expected)
