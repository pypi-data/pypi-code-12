import json
import re
import os
import threading
import datetime
import redis
import time

from config import *
from utils import jjoin
import ngx_log_field_parser as PARSER
from log_format import FIELD_LIST, FIELD_IGNORE_LIST
from common.logger import log
from ngx_cfg_monitor import ConfigMonitor

class NginxLogParser(object):
	REDIS_KEY = jjoin(PREFIX, MESSAGE_QUEUE)  # redis queue key

	def __init__(self, server_ip, access_logs, log_patterns, config_files):
		self.server_ip = server_ip
		self.regex_patterns = {}
		for key in log_patterns:
			regex_raw_pattern = log_patterns[key]
			self.regex_patterns[key] = re.compile(regex_raw_pattern)
		self.access_logs = access_logs
		self.config_files = config_files

	def parse_log(self, row, pattern, domain):
		"""
		USE PARSER.PARSER_LIST to parse keys in row
		If any parse function returns none, discard the row
		:return: Parsed row
		"""

		try:
			res = pattern.match(row).groupdict()
		except Exception, e:
			log.error(e, exc_info=True)
			log.error(row)
			return None

		# custom parsing row begins
		for key, parse_function in PARSER.PARSER_LIST.iteritems():
			if key not in res and key in FIELD_IGNORE_LIST:
				continue
			try:
				temp_res = parse_function(res[key])
				if temp_res is not None:
					res[key] = temp_res
				else:
					# parse function decides not to log this row
					return None
			except:
				# the row does not follow format expected by parser
				# or the parser is buggy. Ignore row at the moment
				return None

		# this part can't be changed at the moment
		res['domain'] = domain
		res['server_ip'] = self.server_ip

		return res

	def format_row(self, parsed_row):
		# return a formatted row according to the contract
		formatted_row = []
		for item in FIELD_LIST:
			if item in parsed_row:
				formatted_row.append(parsed_row[item])
		return formatted_row

	def follow(self):
		"""Follow/Tail all files found in access_logs"""
		last_ino = [os.stat(item['path']).st_ino if os.path.exists(item['path']) else None for item in self.access_logs]

		f = [open(item['path'], 'r') if os.path.exists(item['path']) else None for item in self.access_logs]
		for the_file in f:
			if the_file:
				the_file.seek(0, 2)

		n = len(f)

		'''
		Use a different method to tail multiple files
		*Source: https://bitbucket.org/rushman/multitail
		*Reason: The previous method will cause lagging behind when there are
		different traffic levels between access log files because it will sleep when
		ONE file has no traffic
		*This version will sleep when ALL FILES has no traffic. This version works ONLY if
		log rotation happens in short period of time, all happens on all file together (which
		is usually the case).
		'''
		while True:
			# read every files, use server_name as key
			got_line = False
			for i in range(0, n):
				if f[i]:
					the_file = f[i]
					info = self.access_logs[i]
					filePath = info['path']
					serverName = info['server_name']
					formatName = info['format_name']

					# print "DEBUG: "
					# print access_logs[i]
					# print serverName

					line = the_file.readline()
					if line:
						got_line = True
						#yield {'domain': serverName, 'format': formatName, 'line': line}
						yield {'raw': line, 'result': self.parse_log(line, self.regex_patterns[formatName], serverName)}
					else:
						continue
				else:
					info = self.access_logs[i]
					filePath = info['path']

					if os.path.exists(filePath):
						f[i] = open(filePath, 'r')
						last_ino[i] = os.stat(filePath).st_ino
					else:
						log.info("file_not_exists|file=%s" % filePath)
						continue

			if not got_line:
				time.sleep(SLEEP)  # IF THERE IS NO TRAFFIC FROM ALL FILES
				for i in range(0, n):
					if f[i]:
						the_file = f[i]
						info = self.access_logs[i]
						filePath = info['path']
						try:
							this_ino = os.stat(filePath).st_ino
						except:
							this_ino = 0
						if this_ino != last_ino[i]:
							the_file.close()
							while the_file.closed:
								try:
									f[i] = open(filePath, 'r')
									the_file = f[i]
								except:
									pass
							last_ino[i] = os.stat(filePath).st_ino
					else:
						info = self.access_logs[i]
						filePath = info['path']

						if os.path.exists(filePath):
							f[i] = open(filePath, 'r')
							last_ino[i] = os.stat(filePath).st_ino
						else:
							log.info("file_not_exists|file=%s" % (filePath))
							continue
							
	def prepare(self):
		self.redis = redis.StrictRedis(REDIS_HOSTNAME, socket_keepalive=True)
		self.pipe = self.redis.pipeline(transaction=False)  # no need for atomic
		self.last_call = datetime.datetime.now()
		self.redis_queue = []
							
	def execute(self):
		try:
			self.prepare()
			cfg_monitor = ConfigMonitor(self.config_files, PARSER_UPDATE)
			try:
				cfg_monitor.start()
			except Exception, e:
				log.error("cfg_monitor|msg=%s", e, exc_info=True)
			# short summary
			log.debug("welcome_msg|server_id=%s,access_log=%s,access_log_len=%u", self.server_ip, self.access_logs, len(self.access_logs))

			source = self.follow()
			log.debug("prepare|state=runnning")
			while not cfg_monitor.has_changed():
				# get next row and process, can be refactored more
				log.debug("prepare|state=before_get_line")
				row = source.next()
				log.debug("prepare|state=done")
				parsed_row = row['result']
				if parsed_row is None:
					# ignore this row
					continue
	
				formatted_row = None
				try:
					formatted_row = self.format_row(parsed_row)
				except Exception, e:
					log.error("invalid_row|row=%s,parsed_row=%s" % (row['raw'], parsed_row))
					continue
	
				if formatted_row is not None:
					self.redis_queue.append(json.dumps(formatted_row))
					# execute pipeline every second to save cpu
				self.update_db()
	
			log.info("execute|state=parser_stopped")
		except Exception, e:
			# try except in outermost block !
			log.error("unknown|msg=%s", e, exc_info=True)


	def update_db(self):

		current_time = datetime.datetime.now()
		if (current_time - self.last_call).seconds > 0:
			try:
				self.pipe.lpush(self.REDIS_KEY, *self.redis_queue)
				self.pipe.execute()
				log.info("execute|state=parse_success")
			except Exception, e:
				log.error("possible_redis_connection_problem|msg=%s", e, exc_info=True)
			finally:
				self.redis_queue[:] = []  # .clear function in python 3.3
				self.last_call = current_time


if __name__ == '__main__':
	from ngx_cfg_utils import get_config_info

	while True:
		print "parser start"
		machine_id, access_logs, log_patterns, config_files = get_config_info()
		ngx_log_parser = NginxLogParser(machine_id, access_logs, log_patterns, config_files)
		ngx_log_parser.execute()
		print "parser restart"
