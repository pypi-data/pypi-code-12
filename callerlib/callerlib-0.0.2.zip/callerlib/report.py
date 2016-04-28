import time


class Report(object):
    @staticmethod
    def fail(msg):
        print '*FAIL:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def warn(msg):
        print '*WARN:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def info(msg):
        print '*INFO:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def debug(msg):
        print '*DEBUG:{}* {}'.format(time.time()*1000, msg)

    @staticmethod
    def html(msg):
        print '*HTML:{}* {}'.format(time.time()*1000, msg)
