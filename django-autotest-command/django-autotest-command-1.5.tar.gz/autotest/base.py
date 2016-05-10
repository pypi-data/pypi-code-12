#
# Copyright 2016, Maren Hachmann <marenhachmann@yahoo.com>
#                 Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Some useful base test tools to help django testing.
"""

# FLAG: do not report failures from here in tracebacks
# pylint: disable=invalid-name
__unittest = True

import os
import types
import shutil
import inspect

from os.path import basename, dirname, join, abspath, isfile
from datetime import date
from importlib import import_module

from django.test import TestCase
from django.test.utils import override_settings

from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.core.files.base import File
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpRequest

try:
    import haystack
except ImportError:
    haystack = None

class HaystackMixin(object):
    """Access haystack as if it were indexed and ready for your test"""
    @classmethod
    def setUpClass(cls):
        super(HaystackMixin, cls).setUpClass()
        cls._hs_overridden = override_settings(
         HAYSTACK_CONNECTIONS={
          'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'STORAGE': 'ram'
          }
        })
        cls._hs_overridden.enable()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls._hs_overridden, 'wrapper'):
            cls._hs_overridden.disable()
        super(HaystackMixin, cls).tearDownClass()

    def setUp(self):
        super(HaystackMixin, self).setUp()
        haystack.connections.reload('default')
        call_command('rebuild_index', interactive=False, verbosity=0)

    def tearDown(self):
        super(HaystackMixin, self).tearDown()
        call_command('clear_index', interactive=False, verbosity=0)


class ExtraTestCase(TestCase):
    """
    Sets the MEDIA_ROOT location to a test location, copies in media files
    used in fixtures and provides an easy way to load files, objects and test
    GET and POST requests and their responses.
    """
    @classmethod
    def setUpClass(cls):
        super(ExtraTestCase, cls).setUpClass()
        cls.media_root = settings.MEDIA_ROOT.rstrip('/')
        if not cls.media_root.endswith('_test'):
            cls.media_root += '_test'
        if not os.path.isdir(cls.media_root):
            os.makedirs(media)
        cls._et_overridden = override_settings(
            MEDIA_ROOT=cls.media_root,
        )
        cls._et_overridden.enable()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls._et_overridden, 'wrapper'):
            cls._et_overridden.disable()
        super(ExtraTestCase, cls).tearDownClass()

    def setUp(self):
        "Creates a dictionary containing a default post request for resources"
        super(ExtraTestCase, self).setUp()
        if os.path.isdir(self.source_dir):
            for fname in os.listdir(self.source_dir):
                source = os.path.join(self.source_dir, 'test', fname)
                target = os.path.join(self.media_root, fname)
                if not isfile(target) and isfile(source):
                    shutil.copy(source, target)
        self.login(**getattr(self, 'credentials', {}))

    def login(self, **credentials):
        """Set session data regardless of being authenticated"""
        engine = import_module(settings.SESSION_ENGINE)
        client = import_module(getattr(settings, 'SESSION_CLIENT', 'django.test.client'))
 
        self.client = client.Client()

        # Save new session in database and add cookie referencing it
        request = HttpRequest()
        request.session = engine.SessionStore('Python/2.7', '127.0.0.1')
        request.session.save()

        self.user = None
        if credentials:
            self.user = authenticate(**credentials)
            login(request, self.user)
            request.session.save()

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie] = request.session.session_key
        self.client.cookies[session_cookie].update({
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
            'max-age': None,
        })

    @property
    def app_dir(self):
        """Returns the root directory of an app based on the test case location"""
        fn = dirname(inspect.getfile(type(self)))
        if basename(fn) == 'tests':
            return dirname(fn)
        return fn

    @property
    def source_dir(self):
        """Return a fixtures media directory where files might be found"""
        return os.path.join(self.app_dir, 'fixtures', 'media')

    def open(self, filename, *args, **kw):
        """Opens a file relative to this test script.

        *args go to open(), **kwargs go to File() e.g:
        
        self.open('foo.xml', 'rb', name='bar.xml')

        """
        fn = filename
        if not '/' in filename:
            filename = join(self.source_dir, fn)
            if not isfile(filename):
                filename = join(self.source_dir, 'test', fn)
        if not isfile(filename):
            raise IOError("Can't open file: %s (%s)" % (filename, fn))
        return File(open(filename, *args), **kw)

    def getObj(self, qs, **kw):
        """
        Get an object from django, assert it exists, return it.

        qs      - a QuerySet or Model class
        count   - number of objects to get (default: 1)
        **kw    - filter to run (default: None)

        Filters are combination of positive fields=value in kwargs
        and not_field=value for exclusion in the same dictionary.
        """
        count = kw.pop('count', 1)

        # Is the queryset a class? It's probably a model class
        if isinstance(qs, (types.TypeType, types.ClassType)):
            qs = qs.objects.all()

        for (field, value) in kw.items(): 
            if field[:4] != 'not_':
                qs = qs.filter(**{field: value})
            else:
                qs = qs.exclude(**{field[4:]: value})

        # Assert we have enough objects to return
        self.assertGreater(qs.count(), count - 1)

        # Return either one object or a list of objects limited to count
        return qs[0] if count == 1 else qs[:count]

    def assertGet(self, url_name, *arg, **kw):
        """Make a generic GET request with the best options"""
        data = kw.pop('data', {})
        method = kw.pop('method', self.client.get)
        follow = kw.pop('follow', True)
        status = kw.pop('status', None)
        get_param = kw.pop('get_param', None)

        if url_name[0] == '/':
            url = url_name
        else:
            url = reverse(url_name, kwargs=kw, args=arg)
        if get_param:
            url += '?' + get_param

        response = method(url, data, follow=follow)
        if status:
            self.assertEqual(response.status_code, status)
        return response

    def assertPost(self, *arg, **kw):
        """Make a generic POST request with the best options"""
        errs = kw.pop('form_errors', None)
        kw['method'] = self.client.post
        response = self.assertGet(*arg, **kw)

        if errs:
            for (field, msg) in errs.items():
                self.assertFormError(response, 'form', field, msg)
        elif response.context and 'form' in response.context:
            form = response.context['form']
            if 'status' in kw and kw['status'] == 200 and form:
                msg = ''
                for field in form.errors:
                    msg += "%s: %s\n" % (field, ','.join(form.errors[field]))
                self.assertFalse(bool(form.errors), msg)
        return response

    def assertBoth(self, *args, **kw):
        """
        Make a GET and POST request and expect the same status.
        
        Teturns (get, post) response tuple
        """
        post_kw = kw.copy()
        for key in ('form_errors', 'data'):
            kw.pop(key, None)
        return (self.assertGet(*args, **kw),
                self.assertPost(*args, **post_kw))

