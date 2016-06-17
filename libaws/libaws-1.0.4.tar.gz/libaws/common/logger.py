#coding:utf-8
import os
import logging
import logging.config
import config
import utils
import libaws.base.utils as baseutils
from libaws.common import mylogger


def init_log_path():
    try:
        app_data_path = utils.get_app_data_path()
        log_path = os.path.join(app_data_path,'logs')
        baseutils.mkdirs(log_path)
    except Exception,e:
        print e
        log_path = "./.libaws/logs"
        baseutils.mkdirs(log_path)
    return log_path

log_path = init_log_path()
logname = "libaws"
LOGGING = {
      #版本,总是1
      'version': 1,
      'disable_existing_loggers': True,
      'formatters': {
          'detail': {'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
              'datefmt' : '%Y-%m-%d %H:%M:%S'
            },
          'simple': {'format': '%(message)s'},
          'default':{'format' : '[%(levelname)s]%(asctime)s %(message)s',
              'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
      'handlers': {
          'null': {
              'level':'DEBUG',
              'class':'logging.NullHandler',
            },
        'rotate_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path ,"%s.log" % logname),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'default',
            },
        },

      'loggers' : {
        # 定义了一个logger
        'root' : {
            'level' : 'DEBUG',
            'handlers' : ['rotate_file'],
            'propagate' : True
        }
    } 
}

#获取root日志
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('root')

debug_stream_handler = mylogger.loghandler.ConsoleColorHandler()
debug_stream_handler.setLevel(logging.DEBUG)
default_logging_formater = LOGGING['formatters']['default']
default_formatter = logging.Formatter(default_logging_formater['format'],default_logging_formater['datefmt'])
debug_stream_handler.setFormatter(default_formatter)

stream_handler = mylogger.loghandler.ConsoleColorHandler()
stream_handler.setLevel(logging.WARN)
simple_formatter = logging.Formatter(LOGGING['formatters']['simple']['format'])
stream_handler.setFormatter(simple_formatter)

#是否禁止日志
logger.disabled = config.LOGGER_DISABLED

def enable_debug_log(enabled=True):

    global logger

    if enabled:
        logger.handlers[0].setLevel(logging.DEBUG)
        logger.addHandler(debug_stream_handler)
    else:
        logger.addHandler(stream_handler)

