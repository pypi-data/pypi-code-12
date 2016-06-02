from django.contrib.auth.models import User
from django.test import Client
from ldb.django.test import SeleniumTestCase
from django.conf import settings

import urlparse

class UserTestMixin(object):
    """
    Mixin that handles test that require a user.
    
    Does the following:
        * Creates a django.test.Client and stores it in cls.client.
        * Creates a user, stores user in cls.user
        * Logs in said user to cls.client
    """
    username = 'test_user'
    password = 'silly_pass'

    def _pre_setup(self):
        super(UserTestMixin, self)._pre_setup()
        self.client = Client()
        self.user = User.objects.create_user(self.username, 'test@user.com',
                                             self.password)
        self.user.save()
        self.client.login(username=self.username, password=self.password)


class SeleniumUserTestCase(UserTestMixin, SeleniumTestCase):
    # TODO: Handle exceptions, especially if login fails
    def _pre_setup(self):
        super(SeleniumUserTestCase, self)._pre_setup()
        settings.DEBUG = True
        self.selenium_get(settings.LOGIN_URL)
        self.selenium.find_element_by_name('username').send_keys(self.username)
        password_field = self.selenium.find_element_by_name('password')
        password_field.send_keys(self.password)
        password_field.submit()

        expected_url = self.make_url(settings.LOGIN_REDIRECT_URL)
        if self.selenium.current_url != expected_url:
            super(SeleniumUserTestCase, self)._post_teardown()
            assert False, "Login failed"
