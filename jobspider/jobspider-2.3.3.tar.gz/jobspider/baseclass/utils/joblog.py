#!/usr/bin/python

"""
Level	    Numeric value
CRITICAL	50
ERROR	    40
WARNING 	30
INFO	    20
DEBUG	    10
NOTSET	    0

"""





import logging
import os



class MyLogger():

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self._set_handlers()

    def _set_handlers(self):
        self.logger.addHandler(self.sta_handler)
        self.logger.addHandler(self.file_handler)

    @property
    def sta_handler(self):
        formater = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s in %(filename)s %(levelno)s'
        )
        com_handler = logging.StreamHandler()
        com_handler.setLevel(logging.ERROR)
        com_handler.setFormatter(formater)
        return com_handler

    @property
    def file_handler(self):
        formater = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s in %(filename)s %(levelno)s'
        )
        com_handler = logging.FileHandler('s.log')
        com_handler.setLevel(logging.ERROR)
        com_handler.setFormatter(formater)
        return com_handler



if __name__ == "__main__":
    l = MyLogger('haibo').logger
    l.error('test error')
    l.warn('test warn')

    sl = logging.getLogger('haibo.c')
    sl.warn('test inherit')

