"""
Python API for SauceLabs Selenium testing.

https://wiki.saucelabs.com/display/DOCS/The+Sauce+Labs+REST+API
"""

import os
import datetime
import re
import requests
from sys import modules
from requests import Session
from urllib import parse
from bs4 import BeautifulSoup

__version__ = '0.1.12'


class PastaDecorator(object):
    """Multi-browser test decorator for SauceLabs."""

    @classmethod
    def on_platforms(cls, platforms):
        """
        Iterate over browser setups.

        Capability Options:
            app (string): app file loaded to SauceLabs storage
                'sauce-storage:<filename>'
            appiumVersion (string): Appium version
                '1.5.2', '1.5.1', '1.5.0', '1.4.16'
            browserName (string): web browser name
                'android', 'chrome', 'firefox', 'htmlunit',
                'internet explorer', 'iPhone', 'iPad', 'opera', 'safari'
            deviceOrientation (string): initial device orientation
                'LANDSCAPE', 'PORTRAIT'
            platform (string):
                Selenium: 'ANY', 'WINDOWS', 'XP', 'VISTA', 'MAC', 'LINUX',
                    'UNIX', 'ANDROID'
                SauceLabs: 'Windows 10', 'Windows 8.1', 'Windows 8',
                    'Windows 7', 'Windows XP', 'Linux', 'OS X 10.11',
                    'OS X 10.10', 'OS X 10.9', 'OS X 10.8'
            platformName (string): Appium mobile OS
                'iOS', 'Android', 'FirefoxOS'
            platformVersion (string): Appium mobile OS version
            screenResolution (string):
                '800x600', '1024x768', '1280x1024'
            recordScreenshots (bool): enable or disable screenshots
                True (default), False
            recordVideo (bool): enable or disable video recording
                True (default), False
            version (string): browser version number or 'latest'
        """
        def decorator(base_class):
            module = modules[base_class.__module__].__dict__
            for i, platform in enumerate(platforms):
                d = dict(base_class.__dict__)
                d['desired_capabilities'] = platform
                name = "%s_%s" % (base_class.__name__, i + 1)
                module[name] = type(name, (base_class,), d)
        return decorator


class PastaSauce(object):
    """SauceLabs access object for use by Python 3."""

    # obj HTTP communication strings
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    OPTIONS = 'OPTIONS'
    # access command options
    ALL = 'all'
    APPIUM = 'appium'
    WEBDRIVER = 'webdriver'
    SELENIUM = 'selenium-rc'
    # sub-account levels
    FREE = 'free'
    SMALL = 'small'
    TEAM = 'team'
    COM = 'com'
    COM_PLUS = 'complus'
    # test types
    QUNIT = 'qunit'
    JASMINE = 'jasmine'
    YUI = 'YUI Test'
    MOCHA = 'mocha'
    CUSTOM = 'custom'

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """
        Build a user account from (in order).

        1. passed values
        2. envrionment variables 'SAUCE_USERNAME' and
           'SAUCE_ACCESS_KEY'
        3. NoneType (only unauthenticated commands
           available to blank auth)
        """
        sauce_user = os.getenv('SAUCE_USERNAME') if not sauce_username \
            else sauce_username
        sauce_key = os.getenv('SAUCE_ACCESS_KEY') if not sauce_access_key \
            else sauce_access_key
        self.user = Account(sauce_user, sauce_key)
        self.comm = SauceComm(self.user)
        self.helper = PastaHelper()
        self.test_updates = {
            'name': None,
            'tags': None,
            'public': None,
            'passed': None,
            'build': None,
            'custom_data': None,
        }

    def get_user(self):
        """Return the current username."""
        return self.user.username

    def get_access_key(self):
        """Return the current user access key."""
        return self.user.access_key

    def get_headers(self):
        """Return the current HTTP headers."""
        return self.comm.get_headers()

    def get_sauce_labs_status(self):
        """Get the SauceLabs server status."""
        url = 'info/status'
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_supported_platforms(self, api):
        """Get a list of platforms available on SauceLabs."""
        url = 'info/platforms/%s' % api
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_user_info(self):
        """Get user information."""
        url = 'users/%s' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_current_job_activity(self):
        """Get current activity for a user."""
        url = '%s/activity' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_user_activity(self):
        """Get activity for a user."""
        url = 'users/%s/activity' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_account_usage(self, username=None, start=None, end=None):
        """Get account usage for a user."""
        user = username if username else self.comm.user.username
        url = 'users/%s/usage%s' % \
            (user, self.helper.get_date_encode_string(start, end))
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def create_sub_account(self, username, password, name, email, plan=None):
        """Create a sub-account."""
        url = 'users/%s' % self.user.username
        data = {}
        data['username'] = username
        data['password'] = password
        data['name'] = name
        data['email'] = email
        data['plan'] = plan if plan else 'free'
        return self.comm.send_request(PastaSauce.POST, url, data)

    def update_subaccount_plan(self, username, plan):
        """Change a sub-account user plan.

        Requires a partner account.
        """
        url = '%s/subscription' % username
        data = {'plan': plan, }
        return self.comm.send_request(PastaSauce.POST, url, data)

    def delete_subaccount_plan(self, username):
        """Delete a sub-account user plan.

        Requires a partner account.
        """
        url = '%s/subscription' % username
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def get_user_concurrency(self):
        """Get user concurrency limits."""
        url = 'users/%s/concurrency' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_jobs(self, username=None, number_of_jobs=100, get_full_data=False,
                 skip_jobs=0, jobs_from=None, jobs_to=None, output=None):
        """Get jobs run for a user."""
        user = username if not username else self.user.username
        url_args = {}
        if number_of_jobs != 100 and number_of_jobs > 0:
            url_args['limit'] = number_of_jobs
        if get_full_data:
            url_args['full'] = get_full_data
        if skip_jobs > 0:
            url_args['skip_jobs'] = skip_jobs
        if jobs_from:
            url_args['from'] = jobs_from
        if jobs_to:
            url_args['to'] = jobs_to
        if output:
            url_args['format'] = output
        url = '%s/jobs%s' % \
            (user, self.helper.get_jobs_encode_string(url_args))
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_full_job_info(self, job_id):
        """Get the full information for a particular job."""
        url = '%s/jobs/%s' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def update_job(self, job_id, name=None, tags=None, public=None,
                   passed=None, build=None, custom_data=None):
        """Update a user job."""
        url = '%s/jobs/%s' % (self.user.username, job_id)
        data = {}
        if name:
            data['name'] = name
        if tags:
            data['tags'] = tags
        if public:
            data['public'] = public
        if passed is not None:
            data['passed'] = passed
        if build:
            data['build'] = build
        if custom_data:
            data['custom_data'] = custom_data
        if not data:
            data = None
        return self.comm.send_request(PastaSauce.PUT, url, data)

    def delete_job(self, job_id):
        """Delete a user job."""
        url = '%s/jobs/%s' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def stop_job(self, job_id):
        """Stop an active job."""
        url = '%s/jobs/%s/stop' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.PUT, url, data)

    def get_job_asset_filenames(self, job_id):
        """Get asset filenames for a particular job."""
        url = '%s/jobs/%s/assets' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_job_asset_file(self, job_id, file_name):
        """Download an asset file."""
        url = '%s/jobs/%s/assets/%s' % (self.user.username, job_id, file_name)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def delete_job_asset_files(self, job_id):
        """Download asset files from a particular job."""
        url = '%s/jobs/%s/assets' % (self.user.username, job_id)
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def upload_file(self, file_name, file_type, file_path=None,
                    overwrite=False):
        """Upload a file to SauceStorage."""
        if not file_path:
            file_path = '.'
        if file_path.endswith('/'):
            file_path = file_path[:-1]
        if not os.path.isfile('%s/%s' % (file_path, file_name)):
            raise Exception.OSError.FileNotFoundError(
                '%s/%s not found' % (file_path, file_name))
        url = 'storage/%s/%s%s' % (
            self.user.username,
            file_name,
            '?overwrite=true' if overwrite else ''
        )
        data = None
        file_data = {'file': open('%s/%s' % (file_path, file_name), 'rb')}
        return self.comm.send_request(PastaSauce.POST, url, data, file_data)

    def get_storage_file_names(self):
        """Get the filenames for currently in SauceStorage."""
        url = 'storage/%s' % self.user.username
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_tunnel_ids(self, username=None):
        """Get the IDs for actice Sauce tunnels."""
        user = username if username else self.user.username
        url = '%s/tunnels' % user
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_tunnel_info(self, tunnel_id):
        """Get the information for a specific tunnel."""
        url = '%s/tunnels/%s' % (self.user.username, tunnel_id)
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def delete_tunnel(self, tunnel_id):
        """Delete a Sauce tunnel."""
        url = '%s/tunnels/%s' % (self.user.username, tunnel_id)
        data = None
        return self.comm.send_request(PastaSauce.DELETE, url, data)

    def start_js_unit_tests(self, platforms, test_url, framework,
                            tunnel_id=None, parent=None, test_max=None):
        """Start javascript unit tests."""
        url = '%s/js-tests' % self.user.username
        data = {}
        data['platforms'] = platforms
        data['url'] = test_url
        data['framework'] = framework
        if tunnel_id:
            data['tunnelIdentifier'] = tunnel_id
        elif parent:
            data['parentTunnel'] = parent
        if test_max:
            data['maxDuration'] = test_max
        return self.comm.send_request(PastaSauce.POST, url, data)

    def get_unit_test_status(self, test_ids):
        """Get the status for a group of tests."""
        url = '%s/js-tests/status' % self.user.username
        data = {}
        data['js tests'] = test_ids
        return self.comm.send_request(PastaSauce.POST, url, data)

    def get_bug_types(self):
        """Get the available bug types."""
        url = 'bugs/types'
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_bug_fields(self, bug_id):
        """Get the data fields for a type of bug."""
        url = 'bugs/types/%s' % bug_id
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def get_bug_details(self, bug_id):
        """Get details on a specific bug ID."""
        url = 'bugs/detail/%s' % bug_id
        data = None
        return self.comm.send_request(PastaSauce.GET, url, data)

    def update_bug(self, bug_id, title=None, description=None):
        """Update a bug."""
        url = 'bugs/update/%s' % bug_id
        data = {}
        if title:
            data['Title'] = title
        if description:
            data['Description'] = description
        return self.comm.send_request(PastaSauce.PUT, url, data)


class PastaHelper(object):
    """
    Internal helper functions for PastaSauce.

    Not intended for public use.
    """

    def date_type_base_valid(self, date):
        """Validate a date format."""
        if not isinstance(date, datetime.date) and not isinstance(date, str):
            return False
        return True

    def str_date_split(self, date_str):
        """Split a date string."""
        split = date_str.split('-')
        if len(split) != 3:
            raise ValueError('str date must be "YYYY-MM-DD"')
        try:
            s_year = int(split[0])
            s_month = int(split[1])
            s_day = int(split[2])
            return datetime.date(s_year, s_month, s_day)
        except Exception as e:
            raise ValueError(
                'str date must be "YYYY-MM-DD" -- %s : %s' % (e, e.args)
            )

    def check_dates(self, start, end):
        """Validate a pair of dates."""
        if not start and not end:
            return (None, None)
        begin_set = None
        end_set = None
        today = datetime.date.today()
        if start:
            self.date_type_base_valid(start)
            begin_set = self.str_date_split(start) \
                if isinstance(start, str) else start
            if today < begin_set:
                begin_set = today
        if end:
            self.date_type_base_valid(end)
            end_set = self.str_date_split(end) \
                if isinstance(end, str) else end
        if begin_set and end_set:
            return (begin_set, end_set) \
                if begin_set < end_set else (end_set, begin_set)
        if begin_set:
            return (begin_set, today)
        return (datetime.date.min, end_set)

    def get_date_encode_string(self, start, end):
        """Encode a date string."""
        url_data = {}
        start_date, end_date = self.check_dates(start, end)
        if start_date:
            url_data['start'] = start_date.isoformat()
        if end_date:
            url_data['end'] = end_date.isoformat()
        return ('?' + parse.urlencode(url_data)) if url_data != {} else ''

    def get_jobs_encode_string(self, url_data):
        """Get a job encode string if required."""
        return ('?' + parse.urlencode(url_data)) if url_data != {} else ''

    def get_job_visibility_options(self):
        """Return visibility options for a job."""
        return {
            'Public': {'public', 'public restricted', 'share', 'true'},
            'Private': {'team', 'false', 'private'},
        }

    def get_unit_frameworks(self):
        """Get available javascript unit test frameworks."""
        return ['qunit', 'jasmine', 'YUI Test', 'mocha', 'custom']


class Account(object):
    """Basic access account object for Sauce Labs."""

    def __init__(self, sauce_username=None, sauce_access_key=None):
        """Account initialization for SauceLabs.

        Setup an account with a user and access key or an empty call for
        unauthenticated requests.
        """
        if not sauce_username or not sauce_access_key:
            self.username = None
            self.access_key = None
        else:
            self.username = '%s' % sauce_username
            self.access_key = '%s' % sauce_access_key

    def set_username(self, user):
        """Change the SauceLabs username."""
        if not user:
            self.username = None
            self.access_key = None
            return False
        self.username = '%s' % user
        return True

    def set_access_key(self, access_key):
        """Change the SauceLabs user access key."""
        if not access_key:
            self.username = None
            self.access_key = None
            return False
        self.access_key = '%s' % access_key
        return True


class SauceComm(object):
    """
    Setup and control PastaSauce communication to SauceLabs.

    For unauthenticated commands, can setup with empty user
    SauceComm(Account())
    """

    # HTTP request options
    DELETE = PastaSauce.DELETE
    GET = PastaSauce.GET
    HEAD = PastaSauce.HEAD
    PATCH = PastaSauce.PATCH
    POST = PastaSauce.POST
    PUT = PastaSauce.PUT
    OPTIONS = PastaSauce.OPTIONS

    def __init__(self, user_account):
        """
        Initialize a SauceComm object for HTTP requests.

        Raise a TypeError if SauceComm is not given a PastaSauce Account.
        """
        if not isinstance(user_account, Account):
            raise TypeError('Expected %s, received %s' %
                            (Account, type(user_account)))
        self.user = user_account
        self.request = Session()
        # set user authentication; if an empty user is sent assume the requesst
        # does not require auth
        if self.user.username and self.user.access_key:
            self.request.auth = (self.user.username, self.user.access_key)
        self.request.headers.update({'Content-Type': 'application/json'})
        # no switch statement in Python; use lambda dict instead
        self.methods = {
            SauceComm.DELETE: (
                lambda url, data: self.request.delete(url=url, json=data)
            ),
            SauceComm.GET: (
                lambda url, data: self.request.get(url=url, json=data)
            ),
            SauceComm.HEAD: (
                lambda url, data: self.request.head(url=url, json=data)
            ),
            SauceComm.PATCH: (
                lambda url, data: self.request.delete(url=url, json=data)
            ),
            SauceComm.POST: (
                lambda url, data, files=None:
                    self.request.post(url=url, json=data, files=files)
            ),
            SauceComm.PUT: (
                lambda url, data: self.request.put(url=url, json=data)
            ),
            SauceComm.OPTIONS: (
                lambda url, data: self.request.options(url=url, json=data)
            ),
        }

    def send_request(self, method, url_append, extra_data=None, files=None):
        """Send the request with the data and files to Sauce Labs.

        Raise an InvalidProtocol exception if <method> is not in the class
        method list.
        """
        if method not in self.methods:
            raise InvalidProtocol('Unknown protocol "%s"' % method)
        full_url = 'https://saucelabs.com/rest/v1/%s' % url_append
        if files:
            return self.methods[SauceComm.POST](full_url, extra_data, files)
        return self.methods[method](full_url, extra_data)

    def get_protocols(self):
        """Return a sorted list of available protocols."""
        protocols = []
        for method in self.methods.keys():
            protocols.append(method)
        return protocols.sort()

    def get_headers(self):
        """Return request object headers."""
        return self.request.headers


class PastaConnect(object):
    """Manage SauceConnect.

    To Do:
    a) setup a tunnel
    b) manage tunnels
    c) tear down session tunnels when finished
    """

    def __init__(self, user_account):
        """Initialize a SauceConnect object.

        Incomplete
        """
        self.user = user_account

    def get_sauce_connect_links(self):
        """Return the SauceConnect URL links.

        Incomplete
        """
        r = requests.get('https://docs.saucelabs.com/reference/sauce-connect')
        soup = BeautifulSoup(r.text)
        return self.links(soup.body)

    def links(self, blob):
        """Parse blob looking for GZ, ZIP, DMG and EXE links.

        Incomplete
        """
        links = []
        regex = re.compile('''\"https:\/\/s[a-zA-Z\./\-]*[\d\.]{5,}
                           [a-zA-Z\./\-0-9]*[(gz|zip|dmg|exe)]\"''',
                           re.VERBOSE)
        pattern = regex.findall(blob)
        if not pattern:
            return links
        for match in pattern:
            if match[1:-1] not in links:
                links.append(match[1:-1])
        return links


class InvalidProtocol(Exception):
    """Protocol exception.

    Raised when an unknown protocol is attempted during a request submission
    """

    def __init__(self, message='', *args):
        """Initialize an exception."""
        self.message = message
        super(self).__init__(message, *args)

    def __str__(self):
        """Return string of the exception text."""
        return repr(self.message)
