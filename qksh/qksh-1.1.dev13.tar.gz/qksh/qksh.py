#!/bin/bash/env python
from ihealth_api import RetrieveCookie
# from logging_wrapper import Logger
import re
import os
import requests
import StringIO
import cPickle
import getpass
import logging
import sys
from logger import create_logger
from handle_exception import AuthenticateError, ArgumentError
from sub_daemon import DaemonControl
from multiprocessing import Process
import requests.utils


# logger = Logger('ihealth_api.qksh')
create_logger()
dctl = DaemonControl()

logger = logging.getLogger('ihealth_api.qksh')


def _warpper_daemon_start():
    """
    :parameter None:
    :return None:

    Warpper of daemon_start(), do the UNIX double-fork magic, see Stevens'
    "Advanced Programming in the UNIX Environment" for details
    (ISBN 0201563177)
    """
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        sys.exit('sys.stderr, "fork #1 failed: {errno} ({strerror})'.format(
            errno=e.errno, strerror=e.strerror))
    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)
    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            sys.exit(0)
    except OSError, e:
        sys.exit('sys.stderr, "fork #1 failed: {errno} ({strerror})'.format(
            errno=e.errno, strerror=e.strerror))
    # start the daemon loop
    dctl.daemon_start()


def _parse_arg(arg_list=None, ):
    ptn_case = re.compile(r'^(c\d{7}|1-\d{8,10})$', re.IGNORECASE)
    ptn_url = re.compile(r"""^https://ihealth\.f5\.com/qkview-analyzer/qv
                                 (/\d{7}) # regex match qkview id
                                 (/commands|/files) # reg match commands/files
                                 (/view|/download) # reg match view/download
                                 (/\w*) #regex match hash value""",
                         re.IGNORECASE | re.X)
    # if no argv supplied to qksh, call usage, or split the first argument
    # and do regex check
    logger.info('Checking arguments, argument list: {0}'.format(
                str(arg_list[1:]).strip('[]')))
    if len(arg_list) > 1:
        logger.info('start parsing arguments list.')
        if arg_list[1] == 'status':
            if dctl.daemon_status()[0] == 1:
                sys.exit('sub_daemon is not running.')
            else:
                sys.exit('sub_daemon is running, PID: {0}'.format(
                    dctl.daemon_status()[1]))

        if arg_list[1] == 'start':
            session_obj = RetrieveCookie()
            g = dctl.daemon_status()
            if g[0] == 1:
                p = Process(target=_warpper_daemon_start)
                p.start()
                p.join()
                _auth_with_f5site(session_obj)
                sys.exit('sub_daemon started.')
            elif g[0] == 0:
                sys.exit('sub_daemon already running, PID: {0}'.format(g[1]))
            # toggle.start_daemon()
            # sys.exit('sub_daemon started.')

        if arg_list[1] == 'stop':
            dctl.daemon_stop()
            sys.exit('sub_daemon stopped.')

        # TODO: currently the sys.exit takes no effect.
        # need to warp the daemon_start function and spawn process.
        if arg_list[1] == 'restart':
            dctl.daemon_restart()
            sys.exit('sub_daemon {0}'.format(arg_list[1]))

        # explanation as below:
        # return 1:
        #     first arg is case number
        # return 2:
        #     first arg is url and it's a file downloading link
        # return 3:
        #     first arg is url and it's a commands downloading link
        sliced_url = arg_list[1].split('/')
        case_num_match = ptn_case.match(arg_list[1])
        url_match = ptn_url.match(arg_list[1])
        if case_num_match is not None:
            return 1
        elif url_match is not None:
            if sliced_url[6] == 'files':
                return 2
            if sliced_url[6] == 'commands':
                return 3
        else:
            usage()
            raise ArgumentError
    else:
        sys.exit(usage())


# put below code in a separate function so that it can be easily mocked in
# pytest
def _get_username_password():
    print "Authenticate with F5..."
    try:
        return raw_input('Enter username: '),\
               getpass.getpass('Enter password: ')
    except KeyboardInterrupt as e:
        logger.exception(e)
        raise


def _auth_with_f5site(obj):
    """
    :parameter obj: requests library object.
    :return None:

    Authenticate against with F5 web site, and update username/password,
    session cookie in the sub_daemon.

    * Raise an error if found response code is 401. see:
        https://devcentral.f5.com/wiki/iHealth.Authentication.ashx
    """

    username, password = _get_username_password()
    temp = StringIO.StringIO()
    cPickle.dump([username, password], temp)
    requests.post('http://127.0.0.1:63333/auth.do', data=temp.getvalue())

    # TODO: handle specific requests exception respectively.
    try:
        auth_cookie = obj.get_cookie(username, password)
        logger.debug('returning value of get_cookie(): {0}'.format(auth_cookie))
        if auth_cookie == 401:
            raise AuthenticateError
    except AuthenticateError as e:
        dctl.daemon_stop()
        logger.warning(
            'authentication fail, stop sub_daemon, {0}'.format(e.dump_error())
        )
        raise

    # get cookie value: temp.getvalue() and update session cookie,
    # expire time to local sub_daemon
    # TODO: no need to use StringIO, can use cPickle dumps and loads instead
    temp = StringIO.StringIO()
    cPickle.dump(
        [requests.utils.dict_from_cookiejar(auth_cookie[0]), auth_cookie[1]],
        temp
    )
    requests.post('http://127.0.0.1:63333', data=temp.getvalue())
    # return username, password


def usage():
    print \
        "Qkview Shell(1.1.dev13)\n"\
        "Upload multiple qkviews to a single case or download log file/" \
        "config file/tmsh command output from ihealth.\n" \
        "    Usage: qksh [[case number] [qkview file]]\n" \
        "                [url of qkview files]\n" \
        "                [url of qkview command output]\n" \
        "    Example:\n" \
        "        qksh.py <case number> <qkview file list>\n" \
        "        qksh.py 1-12345678 test-1.qkview test-2.qkview\n" \
        "        qksh.py <file/command url of iHealth>\n" \
        "        qksh.py https://ihealth.f5.com/qkview-analyzer/qv/4081581" \
        "/files/download/Y29uZmlnL2JpZ2lwLmNvbmY"
    logger.info('Invalid arguments.')


def poke_cookie(obj):
    logger.info('daemon is running, step into poke_cookie().')
    poke_res = requests.get('http://127.0.0.1:63333/poke')
    if poke_res.content == "valid":
        logger.info('session cookie is valid. step out poke_cookie()')
        return
    else:
        # even though pid file exists, cookie appears to be invalid, therefore
        # try to restart the sub_daemon, and re-auth against f5 web site.
        # TODO: need to get sub_daemon stdout to qksh.log file, currently
        # the stdout is suspended.
        logger.info('session cookie is not valid, updating credential.')
        _auth_with_f5site(obj)


# check if sub_daemon pid exists or not, if not exists, re-initiate a new
# process.
def pid_check(session_obj):
    logger.info('step into pid_check(), checking sub_daemon status.')
    ret = dctl.daemon_status()
    logger.debug('print ret value: {0}'.format(ret))
    if ret[0] == 1:
        logger.info('daemon is not running, kick off sub_daemon.')
        p = Process(target=_warpper_daemon_start)
        p.start()
        p.join()
        _auth_with_f5site(session_obj)
    else:
        poke_cookie(session_obj)


def main():
    ret = _parse_arg(sys.argv)
    session_obj = RetrieveCookie()

    pid_check(session_obj)

    logger.debug('case match? {0}'.format(ret))
    if ret == 1:
        # TODO: create multiple threads for uploding concurrently
        for i in sys.argv[2:]:
            session_obj.uploadqkview(sys.argv[1], i)
    elif ret == 2:
        session_obj.get_file(sys.argv[1].replace('/view/', '/download/'))
    elif ret == 3:
        session_obj.get_commands(sys.argv[1].replace('/view/', '/download/'))
    else:
        try:
            usage()
        except AuthenticateError as e:
            print e.dump_error()


if __name__ == "__main__":
    main()
