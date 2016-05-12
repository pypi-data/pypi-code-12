#!/bin/env python
#-*- encoding=utf8 -*-
#
# Copyright 2013 beager
#
# 作者：zone
#
# 功能：该模块提供日志相关功能
#
# 版本：V1.0.0
import logging
import logging.handlers
import util


class GlobalLogger:
    def __init__(self, config=None):
        logger = logging.getLogger('globallog')
        logger.propagate = False
        self.logger = logger
        if logger and logger.handlers:
            # 初始化过的
            pass
        elif config:
            self._init_config(config)
        else:
            # 未配置
            raise Exception("Invalid Logger Config")
        self.warn = self.logger.warn
        self.info = self.logger.info
        self.error = self.logger.error
        self.debug = self.logger.debug
        self.critical = self.logger.critical

    def write(self, msg, ex=None):
        """
        msg: 日志内容
        ex:  是否是因为发生了异常而记录日志, 若是,则ex为当前的异常. 默认为 None
        """
        if not ex:
            self.logger.info(msg)
        else:
            self.logger.error('%s Error: %s' % (msg, str(ex)))

    def _parse_level(self, level_str):
        if level_str == 'error':
            parsed_level = logging.ERROR
        elif level_str == 'debug':
            parsed_level = logging.DEBUG
        else:
            parsed_level = logging.INFO
        return parsed_level

    def _add_syslog_handler(self, syslog_config):
        handler = logging.handlers.SysLogHandler(address=(syslog_config['ip'], syslog_config['port']))
        f = logging.Formatter(syslog_config['name'] + '-[%(levelname)s] %(message)s')
        handler.setFormatter(f)
        handler.setLevel(self._parse_level(syslog_config['level']))
        self.logger.addHandler(handler)
        

    def _add_filelog_handler(self, filelog_config):
        file_path = filelog_config['path']
        if file_path.find('%') >= 0:
            file_path = util.now().strftime(file_path)
        handler = logging.FileHandler(file_path)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(self._parse_level(filelog_config['level']))
        self.logger.addHandler(handler)

    def _init_config(self, config):
        """ 初始化并解析配置
        """
        self.config = config
        if 'ip' in self.config and 'port' in self.config:
            # 旧版本配置
            if 'syslog' not in self.config:
                self.config['syslog'] = {}
            self.config['syslog']['ip'] = self.config['ip']
            self.config['syslog']['port'] = self.config['port']

        if 'syslog' in self.config:
            if 'level' not in self.config['syslog']:
                self.config['syslog']['level'] = self.config.get('level')
            if 'name' not in self.config['syslog']:
                self.config['syslog']['name'] = self.config.get('name')
            self._add_syslog_handler(self.config['syslog'])
        if 'textlog' in self.config:
            self._add_filelog_handler(self.config['textlog'])
        self.logger.setLevel(self._parse_level('debug'))
        if not self.logger.handlers:
            raise Exception("Invalid Logger Config")


class SysLog:
    """
    系统日志的封装
    使用方法
        from beager_utils import logger
        syslog = logger.SysLog({ 'ip':'192.168.1.12', 'port':514, 'level':'info', 'name':'apps' })

        写日志
        syslog.write('some message')

    """
    def __init__(self, config):
        logger = logging.getLogger()
        if logger and logger.handlers:
            self.logger = logger
        else:
            ip    = config['ip']
            port  = config['port']
            name  = config['name']
            level = self._parse_level(config['level'])
            
            handler = logging.handlers.SysLogHandler(address=(ip, port))
            f = logging.Formatter(name + '-[%(levelname)s] %(message)s')
            handler.setFormatter(f)

            logger.addHandler(handler)
            logger.setLevel(level)

            self.logger = logger
        self.warn = self.logger.warn
        self.info = self.logger.info
        self.error = self.logger.error
        self.debug = self.logger.debug
        self.critical = self.logger.critical

    def _parse_level(self, level_str):
        if level_str == 'error':
            parsed_level = logging.ERROR
        elif level_str == 'debug':
            parsed_level = logging.DEBUG
        else:
            parsed_level = logging.INFO
        return parsed_level

    def write(self, msg, ex=None):
        """
        msg: 日志内容
        ex:  是否是因为发生了异常而记录日志, 若是,则ex为当前的异常. 默认为 None
        """
        if not ex:
            self.logger.info(msg)
        else:
            self.logger.error('%s Error: %s' % (msg, str(ex)))


CommonLog = None
"""弃用
"""

def initial_log(config):
    """ 初始化CommonLog（用以utils里的其它模块的写日志功能）
    """
    global CommonLog
    if not CommonLog:
        CommonLog = SysLog(config)
