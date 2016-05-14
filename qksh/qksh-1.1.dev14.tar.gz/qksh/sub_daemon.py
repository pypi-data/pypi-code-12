"""
    qksh.sub_daemon
    ~~~~~~~~~

    Implements a daemon to cache credential in memory and maintain the
    session cookie as needed.

    :copyright: (c) 2016 by Qiang He.
    :license: MIT, see LICENSE for more details.
"""

from daemon.runner import DaemonRunner, DaemonRunnerStopFailureError
from pidsearch import find_pid
from getenv import HTTPS_PROXY
import BaseHTTPServer
import StringIO
import thread
import time
import cPickle
import requests
import ihealth_api
import logging
import sys
import os
import signal
import setproctitle
import subprocess

session_cookie = StringIO.StringIO()
session_cookie.write(None)

# save cookie validation result in poker
poker = StringIO.StringIO()
poker.write(None)

# username/password
secret = StringIO.StringIO()
secret.write(None)


logger = logging.getLogger("sub_daemon")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("/var/log/qksh/qksh.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    # fmt='%(asctime)s %(levelname)s %(module)s: %(message)s',
    fmt='%(asctime)s %(levelname)s %(module)s[%(process)s]'
        ': %(message)s',
    # fmt='%(asctime)s %(levelname)s %(module)s[%(process)s]'
    #     ' line:%(lineno)d: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)

# set process name
file_path=subprocess.check_output(['which','qksh']).rstrip('\n')
setproctitle.setproctitle(file_path)

# unpickle credential cache, and dump session cookie in memory
def _update_cookie():
    user_pass_list = cPickle.loads(secret.getvalue())
    username, password = user_pass_list[0:2]
    logger.info('updating cookie in cache. running get_cookie()')
    # logger.info('username: %s, password; %s', username, password)
    cookie = ihealth_api.RetrieveCookie().get_cookie(username, password)
    session_cookie.truncate(0)
    cPickle.dump([requests.utils.dict_from_cookiejar(cookie[0]),
                 cookie[1]], session_cookie)
    logger.info('session cookie cache updated.')


def wrapper_request_handler():
    """
    :return: ``HttpRequestHandler class``
    
    Implement decorator of HttpRequestHandler here, handling GET / POST request
    """
    class HttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            self.send_response(200)
            if self.path == '/auth.do':
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(secret.getvalue())
                logger.info('sending cached credential')
                return

            if self.path == '/poke':
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(poker.getvalue())
                logger.info('sending poke response.')
                return

            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if session_cookie.getvalue() != '':
                logger.debug('sending session cookie {0}'.format(
                             session_cookie.getvalue()))
                self.wfile.write(session_cookie.getvalue())
            else:
                self.wfile.write("No session cookie found!")
                logger.info('No session cookie found!')

        # read hlen bytes of data and write to file-like string buffer. flush
        # session_cookie every time received a POST request and break the loop
        def do_POST(self):
            if self.path == '/auth.do':
                logger.info('receiving credential.')
                hlen = self.headers.get('Content-Length')
                secret.truncate(0)
                secret.write(
                    self.rfile.read(int(hlen)))
                logger.info('credential updated.')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # logger.info('update credential in cache. %s',
                #             self.rfile.read(int(hlen)))
                # logger.info('credential updated.')
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # look for content-length header, saving hlen bytes into memory
                # and update poker with 'valid' value.
                for i in self.headers:
                    if i == 'content-length':
                        hlen = self.headers.get('Content-Length')
                        ret = self.rfile.read(int(hlen))
                        session_cookie.truncate(0)
                        session_cookie.write(ret)
                        poker.write('valid')
                        logger.info('saving session cookie in memory cache.')
                        logger.debug('session cookie value: {0}'.format(
                                     session_cookie.getvalue()))
    return HttpRequestHandler


class Credential(object):
    """
    :return: ``None``
    
    Create a RESTful web server, maintaining username/password/session cookie
    in cache, and periodically validate session cookie
    """
    def __init__(self):
        requests.packages.urllib3.disable_warnings()

        self.logger = logging.getLogger("sub_daemon")
        # TODO: temporary disable stdout/stderr, not sure how to redirect
        # stdout when called by subprocess and logging to qksh.log file.
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/qksh.pid'
        self.pidfile_timeout = 5

    def _restful_loopback_server(
            self,
            server_class=BaseHTTPServer.HTTPServer,
            handler_class=BaseHTTPServer.BaseHTTPRequestHandler):

        # Restful server socket will handle GET/POST request from qksh.
        # Lookback server is hardcoded running on port 63333. Each HTTP request
        # will be dispatched to handler_class
        host, port = "127.0.0.1", 63333
        server_address = (host, port)
        self.logger.info('binding restful_loopback_server to 127.0.0.1:63333.')
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

    # periodically validate session cookie at an interval of 10 mins,
    # if approaching deadline, refresh cookie as needed.
    def _timeout_checker(self):
        file_link = 'https://ihealth.f5.com/qkview-analyzer/'
        while 1:
            counter = 0
            while counter <= 4:
                if session_cookie.getvalue() is not '':
                    cookie = cPickle.loads(session_cookie.getvalue())

                    self.logger.info('downloading test page.')
                    ret = requests.get(file_link, proxies=HTTPS_PROXY,
                                       verify=False,
                                       cookies=cookie[0])
                    # if Location header is in the response, invoke
                    # update_cookie function, otherwise, touch poker with
                    # 'valid' value
                    if 'Location' in ret.headers.keys():
                        self.logger.info(
                            'Location header found in response,'
                            'invoke _update_cookie()')
                        _update_cookie()
                    else:
                        self.logger.info('no Location header found in '
                                         'response.')
                        # convert epoch time to system time for easy reading.
                        t_epoch = cookie[1].split(':')[1].strip('}')
                        expr_time = time.strftime(
                            '%Y-%m-%d %H:%M:%S',
                            time.localtime(float(t_epoch)))
                        poker.truncate(0)
                        poker.write('valid')
                        self.logger.info('session cookie expire at {0}, '
                                         'status: valid'.format(expr_time))
                counter += 1
                time.sleep(600)

            # session cookie need to be updated every 50 mins.
            self.logger.info(
                'session cookie about to expire, calling _update_cookie()')
            _update_cookie()

    def run(self):

        # daemonize the loopback server
        thread.start_new_thread(self._timeout_checker, ())
        handler_class = wrapper_request_handler()
        self._restful_loopback_server(handler_class=handler_class)


class StartDaemonRunner(DaemonRunner):
    """
    :return: ``None``

    Subclass the Daemon Runner to kick off sub daemon without feeding CLI args.
    """
    def parse_args(self, argv=None):
        DaemonRunner.parse_args(self, argv=['class', 'start'])


class StopDaemonRunner(DaemonRunner):
    """
    :return: ``None``

    Subclass the Daemon Runner to stop sub daemon without feeding CLI args.
    """
    def parse_args(self, argv=None):
        DaemonRunner.parse_args(self, argv=['class', 'stop'])


class DaemonControl(object):
    """
    :return: ``None``

    class to Start/Stop sub_daemon.

    * Raise exceptions when failing to start or stop as needed.
    """
    def __init__(self):
        self.credential = Credential()
        self.daemon_runner = None

    def daemon_start(self):
        logger.info('sub_daemon initializing...')
        self.daemon_runner = StartDaemonRunner(self.credential)
        try:
            # This ensures that the logger file handle does not get closed
            # during daemonization
            self.daemon_runner.daemon_context.files_preserve = [
                fh.stream]
            self.daemon_runner.do_action()
            logger.info('sub_daemon started.')
        except Exception as e:
            if self.daemon_status() is None:
                logger.exception(e)
                print 'sub_daemon stopped.'

    def daemon_stop(self):
        daemon_runner = StopDaemonRunner(self.credential)
        try:
            daemon_runner.do_action()
            logger.info('Terminating on signal 15, sub_daemon stopped.')
        except DaemonRunnerStopFailureError:
            logger.exception(DaemonRunnerStopFailureError.message)
            pid = find_pid()
            if pid is not None:
                os.kill(int(pid), signal.SIGTERM)

    def daemon_restart(self):
        self.daemon_stop()
        self.daemon_start()

    @staticmethod
    def daemon_status():
        """
        :return ret: returning a tuple of sub_daemon running status and pid
            number, if exists.

            e.g.
            (1, None): daemon is not running
            (0, '12345'): daemon is running and pid is 12345

        it also cleans up the lagecy pid file when found the sub_daemon is
        not running.

        * raise an exception if pid file is missing whilst the sub_daemon
        is running.
        """
        pid_value = find_pid()
        logger.debug('pid_value: {0}'.format(pid_value))

        try:
            # if sub_daemon is not running, clean up the pid file and return 1
            if pid_value is None:
                if os.path.isfile('/var/run/qksh.pid'):
                    os.remove('/var/run/qksh.pid')
                ret = (1, None)
            else:
                with open('/var/run/qksh.pid') as f:
                    qksh_pid = f.readline()
                ret = (0, qksh_pid.strip('\n'))
        except IOError as e:
            print 'sub_daemon is running, pid file missing, ' \
                  'PID: {0}'.format(pid_value)
            logger.exception(e)
            raise e
        return ret

if __name__ == '__main__':

    g = DaemonControl()

    action_item = {
        'start': g.daemon_start,
        'stop': g.daemon_stop,
        'restart': g.daemon_restart,
        'status': g.daemon_status
    }

    if sys.argv[1] in action_item.keys():
        print action_item[sys.argv[1]]()
    else:
        sys.exit('argument {0} is not supported.\n'
                 'Supported argv list: start|stop|restart|status'.format(
                    sys.argv[1]))
