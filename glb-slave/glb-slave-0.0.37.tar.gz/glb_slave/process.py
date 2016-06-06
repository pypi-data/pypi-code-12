# -*- coding: utf-8 -*-
import re
import sys
import json
import codecs
import socket
import subprocess
import threading
from websocket import (create_connection,
                       WebSocketConnectionClosedException)
from subprocess import Popen, PIPE
from os import makedirs
from os.path import exists, dirname
from jinja2 import Environment, PackageLoader


def mkdir(dir_):
    if not exists(dir_):
        makedirs(dir_)


def write(dist, content):
    dir_ = dirname(dist)
    mkdir(dir_)
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


def deal_default_with_nginx(conf_dist, old_conf_dist, cf_names):
    flag = False
    f_name = 'nginx.conf'
    template_name = 'nginx.conf.jinja2'
    conf_file_path = "%s%s" % (conf_dist, f_name)
    default_dir_names = ["glb"]
    for dir_name in default_dir_names:
        mkdir("%s%s" % (conf_dist, dir_name))
    content = read(conf_file_path, True)
    if content:
        for filename in cf_names.itervalues():
            if content.find(filename) == -1:
                flag = True
                break
    if not content or flag:
        for k, v in cf_names.iteritems():
            cf_names[k] = "%s%s" % (conf_dist, v)
        default_conf_content = render_template(template_name,
                                               **cf_names)
        write(conf_file_path, default_conf_content)

    default_path = "%ssites-enabled/default" % conf_dist
    default_flag = False
    default_content = read(default_path, True)
    if default_content:
            if content.find("health-check") == -1:
                default_flag = True
    if not default_content or default_flag:
        default_content = render_template("default.jinja2")
        write(default_path, default_content)


class Process:

    def __init__(self, websocket_uri, service_type, pid_dist,
                 nginx_command, nginx_conf_dist, nginx_ssl_dist,
                 nginx_ignore_protocol, haproxy_command, haproxy_conf_dist,
                 haproxy_ssl_dist, haproxy_ignore_protocol):
        self.s_type = service_type
        self.pid_dist = pid_dist
        self.n_command = nginx_command
        self.nc_dist = nginx_conf_dist
        self.ns_dist = nginx_ssl_dist
        self.ni_protocol = nginx_ignore_protocol
        self.h_command = haproxy_command
        self.hc_dist = haproxy_conf_dist
        self.hs_dist = haproxy_ssl_dist
        self.hi_protocol = haproxy_ignore_protocol
        self.conn = get_connection(websocket_uri)

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
                break
            finally:
                lock.acquire()
                lock.notify()
                lock.release()

    def run_data(self, lock, t):
        while t.isAlive():
            data = self.data[0]
            if lock.acquire():
                if not data:
                    lock.wait()
                else:
                    self.data[0] = {}
                lock.release()
            slave_version = data.get('slave_version', None)
            haproxy_config = data.get('haproxy_files', None)
            nginx_config = data.get('nginx_files', None)
            if haproxy_config:
                write_files(self.hc_dist, haproxy_config.get("conf_files", {}))
                write_files(self.hs_dist, haproxy_config.get("ssl_files", {}))
                exec_service(self.h_command)
            if nginx_config:
                cf_names = nginx_config.get('cf_names', {})
                deal_default_with_nginx(self.nc_dist,
                                        self.old_nginx_conf_d,
                                        cf_names)
                write_files("%ssites-enabled/" % self.nc_dist,
                            nginx_config.get("http_files", {}))
                write_files(self.nc_dist, nginx_config.get("tcp_files", {}))
                write_files(self.ns_dist, nginx_config.get("ssl_files", {}))
                exec_service(self.n_command)
            if slave_version is not None:
                self.old_nginx_conf_d = self.nc_dist
                write('%s%s' % (self.pid_dist, 'slave_version'),
                      "\n".join([slave_version, self.old_nginx_conf_d]))

    def run(self):
        lock = threading.Condition()
        self.slave_version = ""
        self.old_nginx_conf_d = ""
        self.data = [{}]
        slave_info = read('%s%s' % (self.pid_dist, 'slave_info'))
        if slave_info:
            self.slave_version = slave_info[0]
            self.old_nginx_conf_d = slave_info[1]
        data = json.dumps(dict(addr=get_local_address(),
                               slave_version=self.slave_version,
                               ni_protocol=self.ni_protocol,
                               hi_protocol=self.hi_protocol,
                               service_type=self.s_type))
        self.conn.send(data)
        rever = threading.Thread(target=self.rev_data, args=(lock,))
        runner = threading.Thread(target=self.run_data, args=(lock, rever))
        rever.start()
        runner.start()
