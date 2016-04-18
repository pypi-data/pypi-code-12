# -*- coding: utf-8 -*-
__author__ = 'tangke'
import logging


class MyLog:
    MyLogging = None

    @classmethod
    def log(cls):
        '''
        获取一个日志对象，属于单例
        '''
        if cls.MyLogging is None:
            cls.MyLogging = logging
            cls.MyLogging.basicConfig(level=logging.DEBUG,
                                      format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                      datefmt='%a, %d %b %Y %H:%M:%S',
                                      filename='auto_build.log',
                                      filemode='w')

            console = cls.MyLogging.StreamHandler()
            console.setLevel(cls.MyLogging.DEBUG)
            formatter = cls.MyLogging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            cls.MyLogging.getLogger('').addHandler(console)
        return cls.MyLogging
