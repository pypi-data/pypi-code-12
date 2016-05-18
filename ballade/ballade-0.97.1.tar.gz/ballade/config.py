import sys
import os
import shutil
import logging
import base64
import socket

import yaml


class ConfigManager:
    def __init__(self, directory=None, file='config.yaml'):
        self.directory = self._get_directory(directory)
        self.file = file
        self.path = os.path.join(self.directory, self.file)
        self.config_dict = yaml.load(open(self.path, 'r'))
        self.is_ipv6_accessible = self._is_ipv6_accessible()
        self.filter_upstream = self._get_filter_upstream()
        self.regex_path = self._get_regex_path()
        self.proxy_auth = self._get_proxy_auth()
        self.bind = self._get_bind()
        self.china_ip_list = self._get_china_ip_list()

    def get_process_number(self, number):
        n = self.config_dict.get('process_num') if 'process_num' in self.config_dict.keys() else 0
        n = number if number else n  # Auto number process for logical cores
        if sys.platform == 'win32':
            # Windows does not support os.fork() which is indispensable for tornado
            logging.info("Only one process is supported for Windows")
            n = 1
        return n

    def _get_regex_path(self):
        regex_path = os.path.join(self.directory, 'regex')
        try:
            self._convert_to_regex(os.path.join(self.directory, self.config_dict['omega_file']), regex_path)
        except KeyError:
            logging.critical("There are some faults with your omega_file")
            exit(2)
        return regex_path

    def _get_proxy_auth(self):
        if 'auth' in self.config_dict.keys() and 'enable' in self.config_dict['auth'].keys() and self.config_dict['auth']['enable']:
            try:
                username = self.config_dict['auth']['username']
                password = self.config_dict['auth']['password']
            except KeyError:
                return None
            if username and password:
                return base64.encodebytes((username + ':' + password).encode()).strip()
        else:
            return None

    def _get_bind(self):
        try:
            return self.config_dict['bind']['address'], self.config_dict['bind']['port']
        except KeyError:
            logging.critical("Cannot find bind information in your config file!")
            exit(2)

    def _get_china_ip_list(self):
        result_list = []
        try:
            path = os.path.join(self.directory, self.config_dict['filter']['china_ip_list_file'])
        except KeyError:
            logging.warning("Cannot find china_ip_list_file")
            return result_list
        with open(path, 'r') as f:
            for line in f:
                line = line.replace('\n', '')
                result_list.append(line)
        return result_list

    def _get_filter_upstream(self):
        try:
            filter_profile = self.config_dict['filter']['filter_profile']
            for k, v in self.config_dict['proxy']['profile'].items():
                if k == filter_profile:
                    return v
            for k, v in self.config_dict['proxy']['virtual'].items():
                if k == filter_profile:
                    return self.config_dict['proxy']['profile'][v]
        except KeyError:
            logging.warning("Get filter profile fail, use direct")
            return 'direct://'

    def _is_ipv6_accessible(self):
        if 'ipv6_test' in self.config_dict.keys():
            try:
                force_family = self.config_dict['ipv6_test']['force_family']
                host = self.config_dict['ipv6_test']['host']
                port = self.config_dict['ipv6_test']['port']
            except KeyError:
                return False
            if force_family == 'ipv6':
                return True
            elif force_family == 'ipv4':
                return False
            else:
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                try:
                    s.connect((host, port))
                    s.close()
                    return True
                except socket.error:
                    return False
        else:
            return False

    def _convert_to_regex(self, source, destination):
        proxy_dict = self.config_dict['proxy']['profile']
        for k, v in self.config_dict['proxy']['virtual'].items():
            if v in proxy_dict.keys():
                proxy_dict[k] = proxy_dict[v]
        with open(source, 'r') as s:
            head, _ = os.path.split(destination)
            if not os.path.exists(head):
                os.makedirs(head)
            with open(destination, 'w') as d:
                for line in s:
                    line = line.replace('\n', '')
                    result = line.split(' +')
                    if len(result) == 2:
                        host, proxy = result
                        host = host.replace('.', r'\.')
                        host = host.replace('*', '.*')
                        # 因为Omega实际上是把 "*." 看作可出现零次或者一次处理的
                        if host[:4] == ".*\.":
                            host = "(.*\.)?" + host[4:]
                        proxy = proxy_dict[proxy]
                        d.write(host + ' ' + proxy + "\n")
        logging.debug("Regex convert complete")

    @staticmethod
    def _get_directory(directory):
        def get_homepath():
            try:
                if sys.platform == 'win32':
                    homepath = os.environ['HOMEPATH']
                else:
                    homepath = os.environ['HOME']
            except KeyError:
                print(
                    "Please define a config directory by -c, there is no $HOME or $HOMEPATH in your environment variables")
                exit(1)
            return homepath

        def copy_sample(target):
            sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample')
            # os.mkdir(config_dir) # copytree need the dst doesn't exist
            shutil.copytree(os.path.join(os.path.join(sample_path, '.config'), 'ballade'), target)

        if not directory:
            directory = os.path.join(os.path.join(get_homepath(), '.config'), 'ballade')
        if not os.path.exists(directory):
            print("Cannot find exist config directory, use %s" % directory)
            copy_sample(directory)
        print("If there are some config error, you can delete " + directory + " folder and restart")
        return directory
