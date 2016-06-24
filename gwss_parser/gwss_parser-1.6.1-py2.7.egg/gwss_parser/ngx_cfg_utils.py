"""
Nginx config parser and pattern builder.
Some of the code is adapted from ngxtop on github
"""
import sys
import os
import re
import subprocess
import time
import glob

from pyparsing import *

from common.logger import log



# start
all_access_log = []

REGEX_SPECIAL_CHARS = r'([\.\*\+\?\|\(\)\{\}\[\]])'
REGEX_LOG_FORMAT_VARIABLE = r'\$([a-zA-Z0-9\_]+)'

#default logformat
LOG_FORMAT_COMBINED = '$remote_addr - $remote_user [$time_local] ' \
                      '"$request" $status $body_bytes_sent ' \
                      '"$http_referer" "$http_user_agent"'
LOG_FORMAT_COMMON   = '$remote_addr - $remote_user [$time_local] ' \
                      '"$request" $status $body_bytes_sent ' \
                      '"$http_x_forwarded_for"'


# common parser element
semicolon = Literal(';').suppress()
# nginx string parameter can contain any character except: { ; " '
parameter = Word(''.join(c for c in printables if c not in set('{;"\'')))
# which can also be quoted
parameter = parameter | quotedString.setParseAction(removeQuotes)

startTime = 0

def timer(msg):
	currentTime = time.time()
	global startTime
	log.debug("%s%.5f", msg, currentTime - startTime)
	startTime = currentTime

def error_exit(msg, status = 1):
	sys.stderr.write('Error: %s\n' % msg)
	sys.exit(status)


def detect_config_path():
	"""
	Get nginx configuration file path based on `nginx -V` output
	There should be only one main nginx configuration file
	:return: detected nginx configuration file path
	"""
	try:
		proc = subprocess.Popen(['nginx', '-V'], stderr=subprocess.PIPE)
	except OSError:
		error_exit('Access log file or format was not set and nginx config file cannot be detected. ' +
                   'Perhaps nginx is not in your PATH?')

	stdout, stderr = proc.communicate()
	version_output = stderr.decode('utf-8')
	conf_path_match = re.search(r'--conf-path=(\S*)', version_output)
	if conf_path_match is not None:
		return conf_path_match.group(1)

	# if conf-path is not found, try another method
	prefix_match = re.search(r'--prefix=(\S*)', version_output)
	if prefix_match is not None:
		return prefix_match.group(1) + '/conf/nginx.conf'

	# attempt default if every other method fails
	return '/etc/nginx/nginx.conf'


def get_server_ip():
	"""
	Get the list of ip associated with the server
	:return: [ip1, ip2, ...]
	"""
	try:
		# this method only gets external IP
		proc = subprocess.Popen(['curl', 'icanhazip.com'], stdout=subprocess.PIPE)
	except OSError:
		print 'Cannot get server ip via icanhazip.com !!!!'
		server_ip = raw_input("Manually input server ip : ")
		return server_ip


	stdout, stderr = proc.communicate()
	server_ip = stdout.decode('utf-8').strip() # clear the \n at the end 
	#print "SERVER IP = ", server_ip
	return server_ip

def get_server_name_and_access_logs(config_str):
	"""
	Parse config_str for access_log and server_name directives
	Requirement: 
	- server name and access_log are defined
	- server_name must be followed by access_log
	- All access logs after last server_name will be chosen
	- use dict at the moment for convenience
	:return: {[server_name], [location], format} 
	"""
	
	"""	
	combine = Keyword("server_name") + OneOrMore(parameter) + semicolon + SkipTo("access_log").suppress() + Literal("access_log") + ZeroOrMore(parameter) + semicolon
	combine.ignore(pythonStyleComment)
	"""

	search_server_name = Keyword("server_name") + OneOrMore(parameter) + semicolon
	search_access_log = Keyword("access_log") + ZeroOrMore(parameter) + semicolon

	search_server_name.ignore(pythonStyleComment)
	search_access_log.ignore(pythonStyleComment)
	list_server_name = []
	list_access_log = []
	
	# search from the last occurrence of server_name directive till end of file
	config_str = config_str[config_str.rfind('server_name '):]
	result_server_name = search_server_name.searchString(config_str)
	result_access_log = search_access_log.searchString(config_str)
	
	# server_name not found !
	if not result_server_name:
		return

	# access_log not found
	if not result_access_log:
		return
	
	# extract list of server_name
	#print "@@@ Result server name", result_server_name
	list_server_name = result_server_name[0][1:]
	list_server_name = list(set(list_server_name))

	# extract list of all access_log location and respective format
	for directive in result_access_log.asList():
		path = directive[1]
		if path == 'off' or path.startswith('syslog:'):
			continue
		else:
			format_name = 'combined'
			if len(directive) > 2 and '=' not in directive[2]:
				format_name = directive[2]
			new_access_log = {}
			new_access_log['path'] = path
			new_access_log['format_name'] = format_name
			new_access_log['server_name'] = list_server_name
			list_access_log.append(new_access_log)
	
	# all access_log are off/can't reach
	if not list_access_log:
		return

	return list_access_log

def get_log_formats(config):
	"""
	Parse config for log_format directives
	:return: iterator over ('format name', 'format string') tuple of found directives
	"""
	# log_format name [params]
	log_format = Literal('log_format') + parameter + Group(OneOrMore(parameter)) + semicolon
	log_format.ignore(pythonStyleComment)

	LogFormatDict = {}
	for directive in log_format.searchString(config).asList():
		name = directive[1]
		format_string = ''.join(directive[2])
		LogFormatDict[name] = format_string

	return LogFormatDict

def get_all_log_formats(ListConfigFile):
	"""
	Get all the log_format variable in all found files before start parsing access_log
	:return: A log_format dict
	"""
	
	LogFormat = {}
	log.debug(  "------- Attempt to extract log_format information -------" )
	# add default log format
	LogFormat["combined"] = LOG_FORMAT_COMBINED
	LogFormat["common"] = LOG_FORMAT_COMMON

	for each_file in ListConfigFile:
		with open(each_file) as f:
			config_str = f.read()
		new_log_format = dict(get_log_formats(config_str))
		LogFormat.update(new_log_format)
		if new_log_format is not None:
			log.debug("------- Log format in %s -------" % each_file ) 
			log.debug("\t %s" % new_log_format)
	
	log.debug("------- All Log Formats -------")
	for k in LogFormat:
		log.debug("%s %s" % (k, LogFormat[k]))
	timer("Get all log format")
	return LogFormat

def detect_additional_config_path(config_str):
	"""
	Parse main config_str for include directives
	:return: additional include path
	"""
	access_log = Literal("include") + ZeroOrMore(parameter) + semicolon
	#access_log = Literal("include") + Regex(r"[.^;]*") 
	access_log.ignore(pythonStyleComment)

	list_config_path = []
	for directive in access_log.searchString(config_str).asList():
		#print directive[0],directive[1]
		path = directive[1]
		list_config_path.append(path)

	return list_config_path

def detect_additional_config_file(nginx_config, config_additional):
	"""
	For each additional path found in MAIN nginx file, match the path and find all files
	:return: all files paths
	"""

	list_file_name = []
	#attempt to match all additional files


	for additional_path in config_additional:
		#print  "Looking in path %s  "  % additional_path 
		current_path = additional_path
		if os.path.isabs(current_path) == False:
			# IMPORTANT: if path is relative, add basedir of nginx.conf	
			nginx_dirname = os.path.dirname(nginx_config)
			current_path = os.path.join(nginx_dirname, current_path)

		for name in glob.glob(current_path ):
			#print "\t", name
			"Ignore backup file"
			if not name.endswith("~"):
				list_file_name.append(name)

	return list_file_name

	
def detect_all_config_file():
	"""
	Detect access log config path of nginx
	Detect in main file + include in main file
	:return: list of config files of nginx.conf
	"""

	global startTime
	startTime = time.time()

	ListConfigFile = []
	# main config file
	config = detect_config_path()
	log.debug( "------- Find main nginx conf path : -------")
	log.debug('\t %s' % config)

	if not os.path.exists(config):
		error_exit('Nginx config file not found in %s' % config)

	ListConfigFile.append(config)

	# find addional include in main config file
	with open(config) as f:
		config_str = f.read()

	config_additional = set(detect_additional_config_path(config_str))
	log.debug("------- Attempt to find additional include -------")
	for each_path in config_additional:
		log.debug( '\t %s' % each_path)

	# find all config file in all path	
	config_additional_files = set(detect_additional_config_file(config, config_additional))
	log.debug("------- Attempt to find additional config files -------")
	for each_file in config_additional_files:
		log.debug( '\t %s' % each_file)
		ListConfigFile.append(each_file)

	timer("Detect all config")
	return ListConfigFile


def build_pattern(log_format):
	"""
	Build regular expression to parse given format.
	:param log_format: format string to parse
	:return: regular expression to parse given format
	"""

	if log_format == 'combined':
		log_format = LOG_FORMAT_COMBINED
	elif log_format == 'common':
		log_format = LOG_FORMAT_COMMON
	pattern = re.sub(REGEX_SPECIAL_CHARS, r'\\\1', log_format)
	pattern = re.sub(REGEX_LOG_FORMAT_VARIABLE, '(?P<\\1>.*?)', pattern)

	# Greedily match the last group
	li = pattern.rsplit("*?", 1)
	pattern = "*".join(li)

	log.debug(pattern)
	#print pattern

	return pattern


def get_all_access_logs(ListConfigFile):
	"""
	Get 1 access_log directive in EACH config file
	:return: List of access_log_info
	"""

	all_access_log = []

	for each_file in ListConfigFile:
		with open(each_file) as f:
			config_str = f.read()
		log.debug("------- Attempt to get server_name and access_log directives -------")
		log.debug("Location %s: " % each_file)
		list_access_log = []
		list_access_log = get_server_name_and_access_logs(config_str)
		#print "@@@ Received list access log", access_log
		
		if list_access_log is not None:
			all_access_log.extend(list_access_log)
		
	log.debug("------- ALL LOG FILES INFO -------")
	log.debug(all_access_log)	
	timer("Get all access log")
	return all_access_log


def map_server_name_alias(all_access_logs):
	"""
	In conf files there can be server_name xxxxxx yyyyyyy
	In log files there is no way to know without $host declarative which domain is requested
	Hence, to avoid double counting, map yyyyyy to xxxxxx and treat them as one
	:return: Mapping of server_name_alias to actual server_name used for counting
	"""

	server_name_alias = {}

	for access_log in all_access_logs:
		list_server = access_log['server_name']
		
		if len(list_server) == 1:
			server_name_alias[list_server[0]] = list_server[0]
		else:
			server_name_alias[list_server[0]] = list_server[0]
			for i in range(1, len(list_server)):
				server_name_alias[list_server[i]] = list_server[0]


	log.debug("Server name alias")
	log.debug(server_name_alias)

	return server_name_alias

def trim_access_log(all_access_logs):
	"""
	Trim server_name of all access_log to first item only
	:return: trimmed all_access_logs
	"""

	for access_log in all_access_logs:
		access_log['server_name'] = access_log['server_name'][0]

	return all_access_logs
		
	
def convert_all_format_to_regex(LogFormat):
	"""
	Convert all format to regex pattern"
	:return: LogPattern dict
	"""

	LogPattern = {}

	log.debug("-------- CONVERT ALL FORMAT TO REGEX PATTERN -------")
	# convert all available format to regex
	for each_format in LogFormat:
		#print "Pattern for %s" % each_format
		log.debug("Pattern for %s" % each_format)
		pattern = build_pattern(LogFormat[each_format])
		LogPattern[each_format] = pattern

	# convert specific format to regex
	timer("format to regex")

	return LogPattern

#######################################################
# Init debug functions
#######################################################
def printList(x):
	return "\n".join(str(y) for y in x)

def printDict(x):
	return "\n".join(str(y) + "\n" + str(x[y]) for y in x)

def get_config_info():
	try:
		config_files = detect_all_config_file()
		log_formats = get_all_log_formats(config_files)
		log_patterns = convert_all_format_to_regex(log_formats)
		access_logs = get_all_access_logs(config_files)
		machine_id = get_server_ip()

		#####################################
		log.debug("====== List Config File ======")
		log.debug(printList(config_files))

		log.debug("====== List Log Pattern ======")
		log.debug(printDict(log_patterns))

		log.debug("====== List Log Accesss ======")
		log.debug(printList(access_logs))

		log.debug("====== Server IP  ======")
		log.debug(machine_id)
		####################################

		return (machine_id, access_logs, log_patterns, config_files)
	except Exception, e:
		log.error(e, exc_info = True)

###################################################
# Test code
###################################################
if __name__ == "__main__":
	get_config_info()