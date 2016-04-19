# -*- coding:utf-8 -*-
import abc
import logging

_log = logging.getLogger(__name__)

__all__ = ['PipelineEntity', 'PipelineUnsupportedOperation']


class PipelineEntity:
    """
    Test
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.env = {}
        self.priority = None
        self.type = 'node'
        self.input_channels = []
        self.output_channels = []
        self.external_dependencies = []

    @abc.abstractmethod
    def register(self, pipeline):
        """
        Test
        :param pipeline:
        :return:
        """
        pass


class PipelineUnsupportedOperation(Exception):
    """
    Test
    """
    pass
