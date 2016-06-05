#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import logging
import mechanize
import os

class MechanizeCache(object):

    def __init__(self, cookie_jar,
                 login_url,
                 username, password,
                 username_form_label, password_form_label,
                 validation_url, validation_text,
                 form_select=None,
                 debug=False):

        # Logging and debugging
        self.debug = debug
        self.logger = self._setup_logs(debug)

        # Cookie jar text file
        self.br = mechanize.Browser()
        self.cookie_jar = cookie_jar

        # Login checks
        self.login_url = login_url
        self.validation_url = validation_url
        self.validation_text = validation_text

        # Username and password
        self.username = username
        self.username_form_label = username_form_label
        self.password = password
        self.password_form_label = password_form_label

        # Form selection management
        self.form_select = form_select

    def _setup_logs(self, debug):
        """Set up the logger for debugging output"""
        FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger('tcpserver')
        logger.setLevel(logging.INFO)

        if debug:
            logger.setLevel(logging.DEBUG)

        return logger

    def __repr__(self):
        quiet_mode = " (D)" if self.debug else ""
        return "<MC %s%s>" % (self.username, quiet_mode)

    def login(self, invalidate_cookies=False, headers=None):
        br = self.br
        br.set_handle_robots(False)

        if headers:
            br.addheaders = headers
        else:
            # user agent updated 2016-03-11
            br.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')]

        # Cookie Jar
        policy = mechanize.DefaultCookiePolicy(rfc2965=True)
        cj = mechanize.LWPCookieJar(policy=policy)
        br.set_cookiejar(cj)

        if os.path.isfile(self.cookie_jar) and not invalidate_cookies:
            self.logger.debug("Found %s" % self.cookie_jar)
            cj.load(self.cookie_jar, ignore_discard=True, ignore_expires=True)
            validation_url = self.validation_url
            self.logger.debug("Opening url...%s" % validation_url)
            resp = br.open(validation_url)
            #-if "login.php" in resp.geturl():
            if self.validation_text not in resp.read():
                self.logger.debug("Bad url.  Invalidating cookies...")
                self.login(invalidate_cookies=True)
        else:
            # Check if existing cookies work
            resp = br.open(self.login_url)

            if not self.form_select:
                br.select_form(nr=0) # select second form in page (0 indexed)
            else:
                formcount=0
                for frm in br.forms():
                    if str(frm.attrs["id"]) == self.form_select:
                        break
                    formcount=formcount+1
                br.select_form(nr=formcount)

            br[self.username_form_label] = self.username
            br[self.password_form_label] = self.password
            response = br.submit()

            self.logger.debug("Saving cookies after login form")
            cj.save(self.cookie_jar, ignore_discard=True, ignore_expires=True)
            self.logger.debug("Logged in to %s" % response.geturl())

        self.logged_in = True
        return self.logged_in

    def open(self, location):
        """Returns the browser that opens the location and returns the response"""
        resp = self.br.open(location)
        return resp
