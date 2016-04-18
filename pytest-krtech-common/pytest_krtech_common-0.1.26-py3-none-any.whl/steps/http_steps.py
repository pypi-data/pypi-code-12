# coding=utf-8

import allure
import requests
from hamcrest import assert_that, equal_to


class HttpSteps(object):
    def __init__(self, config):
        self.driver = config.driver
        self.base_url = config.base_url

    class HttpSession:

        def __init__(self):
            self._params = {}
            self._headers = {}
            self._method = 'get'
            self._session = requests.Session()
            self._response = None
            self._url = None
            self._allow_redirects = True

        @property
        def response(self):
            return self._response

        @property
        def url(self):
            return self._url

        @property
        def params(self):
            return self._params

        def with_params(self, params):
            self._params = params
            return self

        def with_headers(self, headers):
            self._headers = headers
            return self

        def with_session(self, session):
            self._session = session
            return self

        def with_method(self, method):
            self._method = method
            return self

        def with_url(self, url):
            self._url = url
            return self

        def allow_redirects(self, allow_redirects):
            self._allow_redirects = allow_redirects
            return self

        def submit(self):
            if self._method == 'post':
                self._response = self._session.post(self._url, headers=self._headers, data=self._params,
                                                    allow_redirects=self._allow_redirects)
            else:
                self._response = self._session.get(self._url, headers=self._headers, params=self._params,
                                                   allow_redirects=self._allow_redirects)
            return self

        def __str__(self):
            return self.__repr__()

        def __repr__(self):
            return "<HttpSession(url='%s', method='%s', params='%s', allow_redirects='%s')>" \
                   % (self._url, self._method, self._params, self._allow_redirects)

    @allure.step("Открытвает страницу {1}")
    def opens(self, url):
        return self.HttpSession().with_url(url).submit()

    @allure.step("Авторизует пользователя '{1}' через http")
    def login(self, url, username, password):
        params = {'username': username, 'password': password}
        return self.HttpSession().with_method('post').with_params(params).with_url(url).submit()

    @allure.step("Статус соответствует '{2}' для ответа '{1}'")
    def should_see_response_status(self, response, status):
        assert_that(response.status_code, equal_to(status),
                    u'Статус ответа не соответствует ожидаемому')

    @allure.step("Значение заголовка '{2}' соответствует '{3}'")
    def should_see_header_value(self, response, header, value):
        assert_that(response.headers.get(header), equal_to(value),
                    u'Заголовок не соответствует ожидаемому значению ' + response.url)
