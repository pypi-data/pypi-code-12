import log_config
import loggerconfig

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import config

log = None

try:
	from django.utils.log import AdminEmailHandler
	
	class ErrorEmailHandler(AdminEmailHandler):
		def format_subject(self, subject):
			pos_list = filter(lambda x:x>0, [subject.find(c) for c in '|\r\n'])
			if pos_list:
					return subject[:min(pos_list)]
			else:
					return subject
except:
	pass

def _log_record_exception(func):
	def _func(self):
		try:
			return func(self)
		except:
			log.exception('log_exception|thread=%s:%s,file=%s:%s,func=%s:%s,log=%s',
				self.process, self.thread, self.filename, self.lineno, self.module, self.funcName, self.msg)
			raise
	return _func

def append_exc(func):
	def _append_exc(*args,**kwargs):
		if 'exc_info' not in kwargs:
			kwargs['exc_info'] = True
		return func(*args,**kwargs)
	return _append_exc

	
def init_logger(log_dir=None, sentry_dsn=None, rollover_when='MIDNIGHT', rollover_backup_count=30):
	
	if log_dir is None:
		log_dir = config.LOG_FOLDER + "/log"
	
	import os
	import sys
	if log_dir and not os.path.exists(log_dir):
		os.mkdir(log_dir, 0777)
		os.chmod(log_dir, 0777)
	logger_config = {
		'version': 1,
		'disable_existing_loggers': True,
		'formatters': {  
			'standard': {
				'format': '%(asctime)s.%(msecs)03d|%(levelname)s|%(process)d:%(thread)d|%(filename)s:%(lineno)d|%(module)s.%(funcName)s|%(message)s',
				'datefmt': '%Y-%m-%d %H:%M:%S',
			},
			'short' : {
				'format': '%(asctime)s.%(msecs)03d|%(levelname)s|%(message)s',
				'datefmt': '%Y-%m-%d %H:%M:%S',
			},
			'data' : {
				'format': '%(asctime)s.%(msecs)03d|%(message)s',
				'datefmt': '%Y-%m-%d %H:%M:%S',
			},
		},
		'handlers': {
			'file_fatal': {
				'level':'CRITICAL',
				'class':'common.loggingmp.MPTimedRotatingFileHandler',
				'filename': os.path.join(log_dir, 'fatal.log').replace('\\','/'),
				'when': rollover_when,
				'backupCount': rollover_backup_count,
				'formatter':'standard',
			},
			'file_error': {
				'level':'WARNING',
				'class':'common.loggingmp.MPTimedRotatingFileHandler',
				'filename': os.path.join(log_dir, 'error.log').replace('\\','/'),
				'when': rollover_when,
				'backupCount': rollover_backup_count,
				'formatter':'standard',
			},
			'file_info': {
				'level':'DEBUG',
				'class':'common.loggingmp.MPTimedRotatingFileHandler',
				'filename': os.path.join(log_dir, 'info.log').replace('\\','/'),
				'when': rollover_when,
				'backupCount': rollover_backup_count,
				'formatter':'short',
			},
			'file_data': {
				'level':'DEBUG',
				'class':'common.loggingmp.MPTimedRotatingFileHandler',
				'filename': os.path.join(log_dir, 'data.log').replace('\\','/'),
				'when': rollover_when,
				'backupCount': rollover_backup_count,
				'formatter':'data',
			},
		},
		'loggers': {
			'main': {
				'handlers': ['file_fatal', 'file_error', 'file_info'],
				'level': 'DEBUG',
				'propagate': True,
			},
			'data': {
				'handlers': ['file_data'],
				'level': 'DEBUG',
				'propagate': True,
			},
			'django.request': {
				'handlers': ['file_fatal', 'file_error', 'file_info'],
				'level': 'ERROR',
				'propagate': True,
			},
			'tornado.access': {
				'handlers': ['file_data'],
				'level': 'DEBUG',
				'propagate': True,
			},
			'tornado.application': {
				'handlers': ['file_fatal', 'file_error', 'file_info'],
				'level': 'DEBUG',
				'propagate': True,
			},
			'tornado.general': {
				'handlers': ['file_fatal', 'file_error', 'file_info'],
				'level': 'DEBUG',
				'propagate': True,
			},
		}
	}

	is_django_app = False
	is_debug = False
	is_test = False

	try:
		from django.conf import settings
		is_django_app = settings.configured
		if is_django_app:
			is_debug = settings.DEBUG
			is_test = 'TEST' in dir(settings) and settings.TEST
	except:
		pass
	if not is_django_app:
		import log_config

		is_debug = 'DEBUG' in dir(log_config) and log_config.DEBUG
		is_test = 'TEST' in dir(log_config) and log_config.TEST

	if is_debug:
		logger_config['handlers']['file_debug'] = {
			'level':'DEBUG',
			'class':'common.loggingmp.MPTimedRotatingFileHandler',
			'filename': os.path.join(log_dir, 'debug.log').replace('\\','/'),
			'when': rollover_when,
			'backupCount': rollover_backup_count,
			'formatter':'short',
		}
		logger_config['loggers']['django.db.backends'] = {
			'handlers': ['file_debug'],
			'level': 'DEBUG',
			'propagate': True,
		}
	elif not is_test:
		loggers = logger_config['loggers']
		for logger_item in loggers:
			if loggers[logger_item]['level'] == 'DEBUG':
				loggers[logger_item]['level'] = 'INFO'

	if not is_debug and sentry_dsn is not None:
		try:
			import raven
			if is_django_app:
				logger_config['handlers']['sentry'] = {
					'level':'WARNING',
					'class':'raven.contrib.django.raven_compat.handlers.SentryHandler',
					'formatter':'short',
				}
				settings.RAVEN_CONFIG = {'dsn': sentry_dsn}
			else:
				logger_config['handlers']['sentry'] = {
					'level':'WARNING',
					'class':'raven.handlers.logging.SentryHandler',
					'dsn': sentry_dsn,
					#'auto_log_stacks': True,
					'formatter':'short',
				}
			logger_config['loggers']['django.request']['handlers'].append('sentry')
			logger_config['loggers']['main']['handlers'].append('sentry')
		except:
			pass

	work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
	recover_path = False
	if work_dir not in sys.path:
		sys.path.append(work_dir)
		recover_path = True
	
	import logging
	try:
		import logging.config
		logging.config.dictConfig(logger_config)
	except Exception as err:
		import loggerconfig
		loggerconfig.dictConfig(logger_config)
		
	if recover_path:
		sys.path.remove(work_dir)
	global log
	log = logging.getLogger('main')
	log.exception = append_exc(log.error)
	log.assertion = log.critical
	log.data = logging.getLogger('data').info
	logging.LogRecord.getMessage = _log_record_exception(logging.LogRecord.getMessage)

#try init log
def try_init_logger():
	try:
		from django.conf import settings
	
		setting_keys = dir(settings)
		if 'LOGGER_CONFIG' in setting_keys:
			init_logger(**settings.LOGGER_CONFIG)
		elif 'LOGGING' in setting_keys and settings.LOGGING:
			import logging
			global log
			log = logging.getLogger('main')
			log.exception = append_exc(log.error)
			log.data = logging.getLogger('data')
		else:
			init_logger()
	except:
		try:
			import log_config
			init_logger(**log_config.LOGGER_CONFIG)
		except:
			try:
				init_logger()
			except Exception as err:
				print err.message
				pass

if log is None:
	try_init_logger()
