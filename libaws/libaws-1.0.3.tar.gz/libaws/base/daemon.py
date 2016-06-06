#coding:utf-8
import os
import sys

DEFAULT_DEV_NULL = "/dev/null"

def daemonize(default_stdout=DEFAULT_DEV_NULL,default_stderr=DEFAULT_DEV_NULL):
    '''
        使进程后台运行
    '''

    if not hasattr(os,'fork'):
        raise ValueError("Daemonizing is not available on this platform.")
        
     # fork进程        
    try:
        if os.fork() > 0: os._exit(0)
    except OSError, error:
        print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)    
    os.chdir('/')
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError, error:
        print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

    #重定向标准IO
    sys.stdout.flush()
    sys.stderr.flush()
    stdinput = file(DEFAULT_DEV_NULL, 'r')
    redirect_stdout = file(default_stdout, 'a+')
    redirect_stderror = file(default_stderr, 'a+', 0)
    os.dup2(stdinput.fileno(), sys.stdin.fileno())
    os.dup2(redirect_stdout.fileno(), sys.stdout.fileno())
    os.dup2(redirect_stderror.fileno(), sys.stderr.fileno())
