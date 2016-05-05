# -*- coding: utf-8 -*-
import platform
import signal
import sys


def set_exit_handler(func):
    if platform.system() == 'Windows':
        try:
            import win32api
            win32api.SetConsoleCtrlHandler(func, True)
        except ImportError:
            version = '.'.join(map(str, sys.version_info[:2]))
            raise Exception('pywin32 not installed for Python ' + version)
    else:
        signal.signal(signal.SIGTERM, func)


if __name__ == '__main__':
    def signal_handler(signal, func=None):
        print '**** processing exit handler ****'
        sys.exit(0)

    set_exit_handler(signal_handler)
    while True:
        pass
