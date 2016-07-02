#!/usr/bin/env python2
#coding:utf-8
"""
  Author:  yafeile --<yafeile@163.com>
  Purpose: memcached命令行版本
  Created: Saturday, July 02, 2016
"""

from pymemcache.client.base import Client
from cmd import Cmd

__version__ = '0.1'

class MemcachedCLI(Cmd, object):
    def __init__(self, host, port):
        super(MemcachedCLI, self).__init__()
        self.client = Client((host, port))
        self.prompt = '{0}:{1}>'.format(host, port)
        self.get_action(self.client)
    
    def get_action(self, client):
        for name in dir(client):
            if not name.startswith('_'):
                attr = getattr(client, name)
                if callable(attr):
                    setattr(self.__class__, 'do_' + name, self._make_cmd(name))
                    doc = (getattr(attr, '__doc__', '') or '').strip()
                    if doc:
                        setattr(self.__class__, 'help_' + name, self._make_help(doc))                    
    
    def _make_cmd(self, name):
        def handler(self, line):
            parts = line.split()
            try:
                print(getattr(self.client, name)( *parts))
            except Exception as e:
                print('Error:{0}'.format(e))
        return handler
    
    def _make_help(self, doc):
        def help(self):
            print(' ' * 80)
            print(doc)
        return help

    def do_exit(self, arg):
        """退出CLI"""
        return True
    
    def default(self, line):
        print("The Memcached Server did not implement this command.")
    do_EOF = do_exit

def main():
    from argparse import ArgumentParser
    args = ArgumentParser(description= 'Memcached命令行版本')
    args.add_argument('-b', '--host', help = 'Memcached监听的地址')
    args.add_argument('-p', '--port',type = int, help = '指定的Memcached端口')
    arg = args.parse_args()
    host = arg.host or '127.0.0.1'
    port = arg.port or 11211
    try:
        MemcachedCLI(host, port).cmdloop()
    except KeyboardInterrupt:
        print('\n')
        SystemExit

if __name__ == '__main__':
    main()