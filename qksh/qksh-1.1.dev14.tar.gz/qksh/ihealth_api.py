"""
    qksh.ihealth_api
    ~~~~~~~~~

    Implements the API to get f5 session cookie, upload qkview, download
    file, command output etc...

    :copyright: (c) 2016 by Qiang He.
    :license: MIT, see LICENSE for more details.
"""

import requests
import requests.utils
import cPickle
import logging
import sys
from getenv import HTTPS_PROXY
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from clint.textui.progress import Bar as ProgressBar



# TODO: need to add notice level log.
# TODO: need to add log rorate


class RetrieveCookie:

    logger = logging.getLogger("ihealth_api")

    # TODO: need to create a function to handle the situation where fail to
    # get the file, command or upload qkview to ihealth
    def __init__(self):

        requests.packages.urllib3.disable_warnings()
        # HTTPConnection.debuglevel = 0
        # you need to initialize logging, otherwise you will not see anything
        # from requests
        # TODO: need to add parameter to turn on debug
        # logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
        #                     datefmt='%Y-%m-%d %H:%M:%S')
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = False

    def retrieve_cookie(self):
        pickled_cookie = requests.get('http://127.0.0.1:63333')
        self.logger.info('returning pickled_cookie.')
        self.logger.debug('value: %s', cPickle.loads(pickled_cookie.content))
        return requests.utils.cookiejar_from_dict(
            cPickle.loads(pickled_cookie.content)[0])

    def get_cookie(self, username, password):

        # form data need to be passed as string such that the order will be
        # honored.
        payload = '{"user_id": "' + username + '", "user_secret": "' +\
                  password + '"}'

        ret = requests.post(
            'https://api.f5.com/auth/pub/sso/login/ihealth-api',
            data=payload, verify=False, timeout=10, allow_redirects=False
        )
        self.logger.info('sending authentication request to f5 api.')
        # iHealth will return json data indicate that the cookie will
        # expire in 1 hour in the format of epoch time.

        if ret.status_code != 200:
            print 'Server Status Code: {0}'.format(ret.status_code)
            print "Login failure! Please check username and password by" \
                  " login directly to login.f5.com."
            return ret.status_code
        else:
            # return session cookie and expire time in http response as a list
            return [ret.cookies, ret.content]

    def get_file(self, file_link, file_name=None):

        # load cookie from local daemon
        cookie = self.retrieve_cookie()

        self.logger.info('downloading file.')
        ret = requests.get(file_link,proxies=HTTPS_PROXY, verify=False,
                           cookies=cookie)
        # TODO: if file name is exist, write to it and prompt progress
        if file_name is None:
            for i in ret.iter_content(1024):
                sys.stdout.write(i)
            self.logger.info('file downloaded.')
        else:
            k = open(file_name, 'wb')
            for i in ret.iter_content(1024):
                k.write(i)
            k.close()
            print 'File downloaded: {0}'.format(file_name)

    def get_commands(self, command_link):

        # load cookie from local daemon
        cookie = self.retrieve_cookie()

        self.logger.info('downloading command output.')
        # call convert_url here to get the desired url pattern before passing
        # it to iHealth API
        ret = requests.get(command_link, verify=False, cookies=cookie)
        for i in ret.iter_content(1024):
            sys.stdout.write(i)
        self.logger.info('commnand output downloaded.')

    @staticmethod
    def create_callback(encoder):
        encoder_len = encoder.len
        bar = ProgressBar(expected_size=encoder_len, filled_char='=')

        def callback(monitor):
            bar.show(monitor.bytes_read)
        return callback

    def uploadqkview(self, case_num, qkview_path):

        # load cookie from local daemon
        cookie = self.retrieve_cookie()

        # create call back function and display progress bar when uploading
        # qkview to iHealth
        # see
        #
        #   https://toolbelt.readthedocs.org/en/latest/uploading-data.html
        #
        # and
        #
        #   https://gitlab.com/sigmavirus24/toolbelt/blob/master/examples/
        #   monitor/progress_bar.py
        m = MultipartEncoder(
                fields={
                    'f5_support_case': case_num, 'visible_in_gui': 'True',
                    'qkview': (
                        qkview_path.split('/')[-1], open(qkview_path, 'rb')
                    )
                }
            )
        callback = self.create_callback(m)
        monitor = MultipartEncoderMonitor(m, callback)
        self.logger.info('uploading qkview.')
        post = requests.post(
            'https://ihealth-api.f5.com/qkview-analyzer/api/qkviews',
            headers={'Content-Type': m.content_type,
                     'Accept': 'application/vnd.f5.ihealth.api'},
            cookies=cookie, allow_redirects=False, data=monitor, verify=False,
            proxies=HTTPS_PROXY)
        ret = post

        # yield qkview link on CLI, if success
        if ret.status_code == 303 and "Location" in ret.headers:
            hash_id = ret.headers['Location'].split('/')[-1]
            print \
                'qkview uploaded, Link: ' \
                'https://ihealth.f5.com/qkview-analyzer/qv/{0}'.format(hash_id)
            self.logger.info('qkview uploaded.')
        else:
            print 'qkview uploading failed. Server status code: {0}'.format(
                ret.status_code)
        return ret.content
