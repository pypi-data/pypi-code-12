#!/usr/bin/env python
# -*- coding:utf-8 -*-

import getopt
import getpass
import signal
import sys

import mlog
from mtailfer import MTailf


def show_usage():
    mlog.debug("-h 要查看日志的机器ip，格式为ip1:port1,ip2:port2,ip3:port3, (port可以省略，默认32200)")
    mlog.debug("-u 用户名,可以不填，默认取当前登陆的用户名")
    mlog.debug("-f 要查看的日志路径, 如 /home/wwwroot/www.log")


def main():
    opts, args = getopt.getopt(sys.argv[1:], "h:f:u:", ["help"])
    host_str, fn, user = None, None, getpass.getuser()
    for opt, arg in opts:
        if opt == "--help":
            show_usage()
            sys.exit(0)
        if "-h" == opt:
            host_str = arg
        if "-f" == opt:
            fn = arg
        if "-u" == opt:
            user = arg

    if host_str and fn and user:
        hosts_str = host_str.split(",")
        mtailfer = MTailf(hosts_str, user=user, fn=fn)
        signal.signal(signal.SIGINT, mtailfer.stop)
        for line in mtailfer.mtailf():
            mlog.debug_inline("【%s】" % line[0])
            mlog.info(line[1])

    else:
        mlog.error("参数错误")
        show_usage()
        sys.exit(0)

if __name__ == '__main__':
    main()
