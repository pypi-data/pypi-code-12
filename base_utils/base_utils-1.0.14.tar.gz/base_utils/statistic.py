#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
#使用方法:
    from beager_utils import statistic as stat
    stat.comm_stat.setLogger(mylogger)


    格式化
    stat.comm_stat.record(data1)
    stat.comm_stat.record(data2)

"""

import datetime
import logger
import logging
import logging.handlers

def _format_stat(params_data):
    """ 旧版
    """
    str_result ="%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" %(
        params_data.get('logno', 0l), # new add
        params_data.get('actiontime',str(datetime.datetime.now())).replace(' ', '+'),
        params_data.get('ui', 0) or params_data.get('uid', 0), 
        params_data.get('roleid', 0),
        params_data.get('ei', '').replace(' ', '+'),
        params_data.get('ai', '').replace(' ', '+'),
        params_data.get('wm', '').replace(' ', '+'),
        params_data.get('si', '').replace(' ', '+'),
        params_data.get('mf', '').replace(' ', '+'),
        params_data.get('bd', '').replace(' ', '+'),
        params_data.get('md', '').replace(' ', '+'),
        params_data.get('pv', '').replace(' ', '+'),
        params_data.get('pl', 0), 
        params_data.get('sw', 0),
        params_data.get('sh', 0), 
        params_data.get('nt', 0),
        params_data.get('la', '').replace(' ', '+'),
        params_data.get('clientid', 0),
        params_data.get('clientver', '').replace(' ', '+'),
        params_data.get('clientpos', 0),
        params_data.get('restype', 0),                    # new add
        str(params_data.get('resid', '')).replace(' ', '+'),   # modify
        str(params_data.get('resid2', '')).replace(' ', '+'),  # modify
        str(params_data.get('statid', '')).replace(' ', '+'),  # modify
        str(params_data.get('statid2', '')).replace(' ', '+'), # modify
        params_data.get('chnno', 0),
        params_data.get('chnpos', 0),
        params_data.get('ip', '').replace(' ', '+'),
        params_data.get('reqno', 0),
        params_data.get('reqactno', 0),                     # new add
        params_data.get('reqaction', '').replace(' ', '+'), # new add
        params_data.get('resaction', '').replace(' ', '+'), # new add
        str(params_data.get('rescode', '')).replace(' ', '+'),   # new add
        str(params_data.get('ext1', '')).replace(' ', '+'),
        str(params_data.get('ext2', '')).replace(' ', '+'),
        str(params_data.get('ext3', '')).replace(' ', '+'),
        str(params_data.get('ext4', '')).replace(' ', '+'),
        str(params_data.get('ext5', '')).replace(' ', '+'))
    return str_result


def _format_data(log_param):
    """格式化统计参数
    """
    if 'actiontime' not in log_param:
        log_param['actiontime'] = str(datetime.datetime.now())
    log_param_list = ['logno', 'actiontime', 'ui', 'roleid', 'ei', 'ai', 'wm', 'si', 'mf', 'bd', 'md', 'pv', 'pl', 'sw', 'sh', 'nt', 'la', 'clientid', 'clientver', 'clientpos', 'restype', 'resid', 'resid2', 'statid', 'statid2', 'chnno', 'chnpos', 'ip', 'reqno', 'reqactno', 'reqaction', 'resaction', 'rescode', 'ext1', 'ext2', 'ext3', 'ext4', 'ext5', 'de', 'oi', 'svcid']
    # log_solid_list = [str(log_param.get(each_key, '')).replace(' ', '+') for each_key in log_param_list]
    log_solid_list = []
    for each_key in log_param_list:
        each_value = log_param.get(each_key, '')
        if not isinstance(each_value, basestring):
            each_value = str(each_value)
        log_solid_list.append(each_value.replace(' ', '+'))
    return ' '.join(log_solid_list)


def _format_stat_v1(data):
    return '[STAT]-[V1.0]' + _format_stat(data)


def _format_stat_v11(data):
    return '[STAT]-[V1.1]' + _format_data(data)


def _get_stat_logger(config):
    stat_logger = logging.getLogger('stat')
    if stat_logger and stat_logger.handlers:
        return stat_logger
    elif config['syslog']:
        syslog_config = config['syslog']
        handler = logging.handlers.SysLogHandler(address=(syslog_config['ip'], syslog_config['port']))
        f = logging.Formatter('stat-[%(levelname)s] %(message)s')
        handler.setFormatter(f)
        handler.setLevel(logging.INFO)

        stat_logger.addHandler(handler)
        stat_logger.setLevel(logging.DEBUG)
        return stat_logger


class _CommonStat:
    def __init__(self, config=None, version='V1.0', svcid=''):
        """config为空时默认使用V1.0的日志格式
        config不为空时，使用V1.1的日志格式
        """
        self.logger = None
        self.config = config
        self.version = version
        self.svcid = svcid

    def setLogger(self, logger):
        """（弃用）设置一个默认日志. 该日志必须要有一个 write 方法
        """
        if logger is None or getattr(logger, 'write', None) is None:
            raise Exception('Logger is invalid! a valid logger must have a write method. ')
        self.logger = logger

    def record(self, data):
        """记录数据(V1.0)
        """
        try:
            if self.version == 'V1.0':
                if self.logger is None:
                    self.logger = logger.CommonLog
                self.logger.write(_format_stat_v1(data))
            elif self.version == 'V1.1':
                if self.config:
                    stat_logger = _get_stat_logger(self.config)
                    data['svcid'] = self.svcid
                    stat_logger.info(_format_stat_v11(data))
                else:
                    raise Exception("Stat Config is invalid!")
        except Exception, ex:
            # self.logger.write('comm_stat_record', ex)
            pass


comm_stat = _CommonStat()
CommonStat = _CommonStat
