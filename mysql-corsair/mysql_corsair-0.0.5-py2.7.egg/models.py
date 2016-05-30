from abc import ABCMeta, abstractmethod, abstractproperty
from threading import Thread


class Recipe(object):
    __metaclass__ = ABCMeta

    def __init__(self, source_db_conn_dict, target_db_conn_dict, async):
        self.async = async
        self.source_db_conn_dict = source_db_conn_dict
        self.target_db_conn_dict = target_db_conn_dict

    def execute(self):
        db_args = (self.source_db_conn_dict, self.target_db_conn_dict)
        for step in self.steps:
            if self.async:
                threads = []
                threads.append(Thread(target=step.execute, args=db_args))
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            else:
                step.execute(db_args)

    @abstractproperty
    def steps(self):
        pass

    @abstractmethod
    def postprocess(self):
        pass


class Step(object):
    __metaclass__ = ABCMeta

    def __init__(self, source_db_conn_dict, target_db_conn_dict):
        self.source_db_conn_dict = source_db_conn_dict
        self.target_db_conn_dict = target_db_conn_dict

    @abstractmethod
    def execute(self):
        pass
