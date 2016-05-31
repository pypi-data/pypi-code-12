#! /usr/bin/env python
# -*- coding: utf-8 -*-


import select
import sys

import paramiko

import mlog


class MTailf(object):
    def __init__(self, hosts, user, fn):
        self.command = 'tail -f ' + fn
        self.user = user
        # self.port = port  # 默认跳板机使用 32200
        self.password = '1'  # 使用key认证 不用password
        self.hosts = hosts
        self.clients = []
        for sh in self.hosts:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(sh.split(':')[0], username=self.user, password=self.password, port=len(sh.split(':'))>1 and int(sh.split(':')[1]) or 32200)
            if not client:
                mlog.error("ssh连接错误,host:%s,user:%s" % (sh, self.user))
                sys.exit(-1)
            else:
                self.clients.append(client)
        if not self.clients:
            mlog.error("请至少连接一台服务器")
            sys.exit(-1)

    def mtailf(self):
        active_channels = []
        for client in self.clients:
            channel = client.get_transport().open_session()
            channel.exec_command(self.command)
            if not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
                active_channels.append(channel)
        while active_channels:
            read_list, _, __ = select.select(active_channels, [], [], 0.0)
            for r_read in read_list:
                if r_read.recv_ready():
                    for line in r_read.recv(len(r_read.in_buffer)).split("\n"):
                        if line and line.strip():
                            yield (r_read.getpeername()[0], line)

    def stop(self, signal, frame):
        mlog.debug("结束...")
        # 清理掉远程机器上的tail任务
        for client in self.clients:
            channel = client.get_transport().open_session()
            channel.exec_command("ps aux|grep '%s'|awk '{print $2}'|xargs kill -9" % self.command)
        sys.exit(0)
