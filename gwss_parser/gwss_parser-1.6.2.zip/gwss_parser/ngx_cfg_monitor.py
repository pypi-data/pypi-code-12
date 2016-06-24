import psutil
import os
import datetime
import time
import subprocess
import threading
from ngx_cfg_utils import detect_all_config_file

class ConfigMonitor(object):
	'''monitor nginx configuration file changing automaticly'''

	def __init__(self, cfg_files, update_time, log=True):
		self._nginx_pids = self._get_nginx_pids()
		self._files = cfg_files
		self._update_time = update_time
		self._log = log
		self._changed = False


	def _get_nginx_pids(self):
		ngx_lst = []
		for p in psutil.process_iter():
			try:
				if p.name() == 'nginx' and p.status() in ['running', 'sleeping']:
					ngx_lst.append(p.pid)
			except (psutil.NoSuchProcess, psutil.ZombieProcess):
				pass
		return set(ngx_lst)

	def _test_nginx_config(self):
		'''calling nginx to test whether its configuration files are well-formed'''
		proc = subprocess.Popen(["service nginx configtest" if os.path.exists('/etc/init.d/nginx') else "nginx -t"], shell=True,
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		result = (len(stdout) > 3 and stdout.find("fail") == -1) or (stderr.find("fail") == -1)
		if not result and self._log:
			from common.logger import log
			log.debug("nginx|state=test_config_failed")
		return result

	def has_file_changed(self):
		current_time = int(time.mktime(datetime.datetime.now().timetuple()))
		for item in self._files:
			last_modified_time = int(os.stat(item).st_mtime)
			if (current_time - last_modified_time) < self._update_time * 2:
				return True
		old_config_file = set(self._files)
		new_config_file = set(detect_all_config_file())
		return old_config_file.symmetric_difference(new_config_file)

	def has_nginx_reloaded(self):
		if self._changed:
			return True
		old_pids = self._nginx_pids
		new_pids = self._get_nginx_pids()

		if old_pids.symmetric_difference(new_pids) and self.has_file_changed() and self._test_nginx_config():
			self._nginx_pids = new_pids
			self._changed = True
			if self._log:
				from common.logger import log
				log.debug("nginx|state=conf_is_changed")
			return True
		return False

	def has_changed(self):
		return self._changed

	def reset(self, update_pids=False):
		if update_pids:
			self._nginx_pids = self._get_nginx_pids()
		self._changed = False

	def run(self):
		while not self.has_nginx_reloaded():
			time.sleep(self._update_time)
		if self._log:
			from common.logger import log
			log.debug("nginx|state=parser_need_restart_soon")

	def start(self):
		t=threading.Thread(target=self.run)
		t.daemon = True
		t.start()
