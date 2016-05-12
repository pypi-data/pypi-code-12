#!/bin/env python
#-*- encoding=utf8 -*-
import nwbase_utils.logger as logger
import nwbase_utils.statistic as stats
config = {
    'syslog': {
        'ip':'192.168.1.61', 
        'port':514, 
        'level':'info',
        'name':'apps'
    },
    'textlog': {
        'path': 'test.txt',
        'level': 'debug'
    },
}


if __name__ == '__main__':
    log = logger.GlobalLogger(config)
    stats.CommonStat.record({'ai': 'test2'})