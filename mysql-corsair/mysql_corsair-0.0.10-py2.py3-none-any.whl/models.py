import logging
from abc import ABCMeta, abstractmethod, abstractproperty
from threading import Thread


logger = logging.getLogger(__name__)


class Recipe(object):
    __metaclass__ = ABCMeta

    def __init__(self, source_db_conn_dict, target_db_conn_dict, async):
        self.async = async
        self.source_db_conn_dict = source_db_conn_dict
        self.target_db_conn_dict = target_db_conn_dict

    def execute(self):
        self.preprocess()

        db_args = (self.source_db_conn_dict, self.target_db_conn_dict)
        if self.async:
            threads = []
            for step in self.steps():
                threads.append(Thread(target=step.execute, args=db_args))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        else:
            for step in self.steps():
                step.execute(*db_args)

        self.postprocess()

    @abstractproperty
    def steps(self):
        pass

    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def postprocess(self):
        pass


class Step(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, source_db_conn_dict, target_db_conn_dict):
        pass
