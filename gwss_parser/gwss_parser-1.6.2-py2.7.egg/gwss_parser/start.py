import time
import sys
import os
import signal
import platform
import atexit
import traceback

import psutil
from ngx_log_parser import NginxLogParser
from ngx_cfg_utils import get_config_info
from common.logger import log


class Daemon:
	"""
	A generic daemon class.	
	Usage: subclass the Daemon class and override the run() method
	"""
	def __init__(self, handler, pidfile, output='/dev/null'):
		self.handler = handler
		self.pidfile = pidfile
		self.output = output

	def kill_proc_tree(self, pid, including_parent=True):  
		parent = psutil.Process(int(pid))
		children = parent.children(recursive=True)
		for child in children:
			child.kill()
		psutil.wait_procs(children, timeout=5)
		if including_parent:
			parent.kill()
			parent.wait(5)

	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		#judge platform
		if platform.system().lower() == 'windows':
			atexit.register(self.delpid)
			pid = str(os.getpid())
			file(self.pidfile,'w+').write("%s\n" % pid)
			return
		
		#do first fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError as e:
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		#os.chdir("/") 
		os.setsid() 
		os.umask(0)
		
		#ignore signal
		try:
			signal.signal(signal.SIGINT, signal.SIG_IGN)
			signal.signal(signal.SIGHUP, signal.SIG_IGN)
			signal.signal(signal.SIGQUIT, signal.SIG_IGN)
			signal.signal(signal.SIGPIPE, signal.SIG_IGN)
			signal.signal(signal.SIGTTOU, signal.SIG_IGN)
			signal.signal(signal.SIGTTIN, signal.SIG_IGN)
			#signal.signal(signal.SIGCHLD, signal.SIG_IGN)	#Can't ignore this signal, otherwise popen may be abnormal
		except Exception as ex:
			sys.stderr.write("ignore signal fail: %s\n" % ex)
			
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except OSError as e:
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# redirect standard file descriptors
		output_dir = os.path.dirname(self.output)
		if output_dir and not os.path.exists(output_dir):
			os.makedirs(output_dir, 0777);
		sys.stdout.flush()
		sys.stderr.flush()
		try:
			si = file('/dev/null', 'r')
			so = file(self.output, 'a+')
			os.dup2(si.fileno(), sys.stdin.fileno())
			os.dup2(so.fileno(), sys.stdout.fileno())
			os.dup2(so.fileno(), sys.stderr.fileno())
			# write pidfile
			atexit.register(self.delpid)
			pid = str(os.getpid())
			with open(self.pidfile,'w') as fi:
				fi.write("%s\n" % pid)
		except:
			print "Daemon Error: ", sys.exc_info()
			traceback.print_exc()

	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			
			pid = None

		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			self.kill_proc_tree(int(pid))
			if os.path.exists(self.pidfile):
				os.remove(self.pidfile)
		except Exception as err:
			print "Stop error:", str(err)
			sys.exit(1)
			traceback.print_exc()

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def run(self):
		"""
		Call handler. It will be called after the process has been
		daemonized by start() or restart().
		"""
		if self.handler is not None:
			self.handler()
		
	def main(self):
		if len(sys.argv) == 2:
			action = sys.argv[1].lower()
			if 'start' == action:
				self.start()
			elif 'stop' == action:
				self.stop()
			elif 'restart' == action:
				self.restart()
			else:
				print "Unknown Command"
				print "Usage: %s start|stop|restart" % sys.argv[0]
				sys.exit(2)
			sys.exit(0)
		else:
			print "Usage: %s start|stop|restart" % sys.argv[0]
			sys.exit(2)


def main():
	"""Main entry point"""

	# small try except block
	try:
		while 1: 
			# parser will restart if parser_main reports a update in nginx conf
			machine_id, access_logs, log_patterns, config_files = get_config_info()
			ngx_log_parser = NginxLogParser(machine_id, access_logs, log_patterns, config_files)
			ngx_log_parser.execute()
			log.info("nginx_config_change")
			time.sleep(1)

	except Exception, e:
		log.error(e.message)

def entry():
	from config import PID_FOLDER, LOG_FOLDER
	Daemon(main, PID_FOLDER + "/gwss_parser.pid", LOG_FOLDER + '/log/daemon.log').main()

# entry point
if __name__ == "__main__":
	# main()
	entry()
