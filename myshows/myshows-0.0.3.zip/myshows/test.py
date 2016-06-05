import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import myshows
from myshows.exceptions import *
from unittest import TestCase, main

USER = ''
PASSWORD = ''
INCORRECT_PASSWORD = ''
from test_config import USER, PASSWORD, INCORRECT_PASSWORD

class MyShowsTestCase(TestCase):
    def setUp(self):
        self.api = myshows.session()

    # good_login
    def test_login_one(self):
        response = self.api.login(USER, PASSWORD)
        self.assertEqual(response.status_code, 200)

    # bad login
    def test_login_two(self):
        self.assertRaises(MyShowsAuthentificationFailedException, lambda: self.api.login(USER, INCORRECT_PASSWORD))

    # profile with login
    def test_profle(self):
        response = self.api.login(USER, PASSWORD)
        response = self.api.profile()
        self.assertEqual(response['gender'], 'm')

    # user_profile without username
    def test_user_profile(self):
        response = self.api.user_profile('')
        self.assertEqual(response, None)

    # user_profile without username
    def test_user_profile(self):
        response = self.api.user_profile(USER)
        self.assertEqual(response['gender'], 'm')

    # good
    def test_shows_one(self):
        response = self.api.shows(1)['title']
        self.assertEqual(response, 'House')

    def test_shows_status_later(self):
        response = self.api.login(USER, PASSWORD)
        response = self.api.profile_shows_status(37473, 'later')
        self.assertEqual(response.status_code, 200)

    def test_shows_status_remove(self):
        response = self.api.login(USER, PASSWORD)
        response = self.api.profile_shows_status(37473, 'remove')
        self.assertEqual(response.status_code, 200)

    def test_shows_status_without_login(self):
        self.assertRaises(MyShowsAuthentificationRequiredException, lambda: self.api.profile_shows_status(37473, 'later'))

    def test_profile_news(self):
        response = self.api.login(USER, PASSWORD)
        response = self.api.profile_news()
        self.assertEqual(isinstance(response, dict), True)

if __name__ == '__main__':
    main(warnings='ignore')
