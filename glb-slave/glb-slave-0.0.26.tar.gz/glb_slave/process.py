# -*- coding: utf-8 -*-
import re
import sys
import time
import json
import codecs
import socket
import subprocess
import threading
from websocket import create_connection, WebSocketConnectionClosedException
from subprocess import Popen, PIPE
from os import makedirs
from os.path import exists, dirname
from jinja2 import Environment, PackageLoader

from .daemon import Daemon


def write(dist, content):
    dir_ = dirname(dist)
    if not exists(dir_):
        makedirs(dir_)
    with codecs.open(dist, 'w', 'utf-8') as f:
        f.write(content)


def read(dist, read_all=False):
    if not exists(dist):
        return
    with codecs.open(dist, 'r', 'utf-8') as f:
        if read_all:
            return f.read()
        return f.readlines()


def write_files(dir_name, vals):
    for k, v in vals.iteritems():
        write("%s%s" % (dir_name, k), v)


def get_local_address():
    return re.search('\d+\.\d+\.\d+\.\d+',
                     Popen('ifconfig', stdout=PIPE).stdout.read()).group(0)


def exec_service(service_command):
    subprocess.call(service_command, shell=True)


def get_connection(websocket_uri):
    try:
        return create_connection(websocket_uri)
    except socket.error as e:
        print 'Connect GLB Server failed: %r' % e
        sys.exit(1)


def render_template(template_name, **kwargs):
    JENV = Environment(loader=PackageLoader('glb_slave', 'templates'))
    return (JENV
            .get_template(template_name)
            .render(**kwargs))


def deal_default_conf(conf_dist, f_name):
    file_path = "%sglb_cluster.conf" % conf_dist
    _default_conf = render_template('nginx.conf.jinja2',
                                    file_paths=[file_path])
    write("%s%s" % (conf_dist, f_name), _default_conf)


class Process(Daemon):

    def __init__(self, websocket_uri, s_type, pid_dist,
                 s_command, conf_dist, ssl_dist):
        super(Process, self).__init__(
            '%s%s' % (pid_dist, 'daemon-glb-slave.pid'))
        self.s_type = s_type
        self.pid_dist = pid_dist
        self.s_command = s_command
        self.conf_dist = conf_dist
        self.ssl_dist = ssl_dist
        self.conn = get_connection(websocket_uri)

    def write_config_files(self, vals):
        write_files(self.conf_dist, vals.get("conf_files", {}))
        write_files(self.ssl_dist, vals.get("ssl_files", {}))

    def run_with_service(self, vals):
        self.write_config_files(vals)
        exec_service(self.s_command)

    def rev_data(self, lock):
        while True:
            try:
                rev_data = self.conn.recv()
                if rev_data:
                    data = json.loads(rev_data)
                    if data:
                        lock.acquire()
                        self.data[0] = data
                        lock.notify()
                        lock.release()
            except WebSocketConnectionClosedException as e:
                print 'Connect GLB Server failed: %r' % e
                sys.exit(1)

    def run_data(self, lock):
        while True:
            data = self.data[0]
            if lock.acquire():
                if not data:
                    lock.wait()
                else:
                    self.data[0] = {}
                lock.release()
            slave_version = data.get('slave_version', None)
            config_files = data.get('config_files', None)
            if config_files:
                if (self.s_type == 'nginx' and self.conf_dist != self.slave_old_conf_d):
                    deal_default_conf(self.conf_dist, 'nginx.conf')
                self.run_with_service(config_files)
            if slave_version is not None:
                if self.s_type == 'nginx':
                    self.slave_old_conf_d = self.conf_dist
                write('%s%s' % (self.pid_dist, 'slave_version'),
                      "\n".join([slave_version, self.slave_old_conf_d]))
            # time.sleep(0.5)

    def _run(self):
        lock = threading.Condition()
        self.slave_version = ""
        self.slave_old_conf_d = ""
        self.data = [{}]
        slave_info = read('%s%s' % (self.pid_dist, 'slave_info'))
        if slave_info:
            self.slave_version = slave_info[0]
            self.slave_old_conf_d = slave_info[1]
        data = json.dumps(dict(addr=get_local_address(),
                               slave_version=self.slave_version,
                               service_type=self.s_type))
        self.conn.send(data)
        rever = threading.Thread(target=self.rev_data, args=(lock,))
        runner = threading.Thread(target=self.run_data, args=(lock,))
        rever.start()
        runner.start()
        rever.join()
        runner.join()

    def stop(self):
        self.conn.close()
        super(Process, self).stop()
