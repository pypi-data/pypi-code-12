import logging
from abc import ABCMeta, abstractmethod, abstractproperty
from threading import Thread


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(ch)
logger.propagate = False


class Recipe(object):
    __metaclass__ = ABCMeta

    def __init__(self, source_db_conn_dict, target_db_conn_dict, async):
        self.async = async
        self.source_db_conn_dict = source_db_conn_dict
        self.target_db_conn_dict = target_db_conn_dict

    def execute(self):
        db_args = (self.source_db_conn_dict, self.target_db_conn_dict)
        for step in self.steps():
            logger.info('Starting step {0}'.format(step.__class__.__name__))
            if self.async:
                threads = []
                threads.append(Thread(target=step.execute, args=db_args))
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            else:
                step.execute(*db_args)
        self.postprocess()

    @abstractproperty
    def steps(self):
        pass

    @abstractmethod
    def postprocess(self):
        pass


class Step(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, source_db_conn_dict, target_db_conn_dict):
        pass
