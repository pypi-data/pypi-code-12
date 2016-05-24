import logging
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from parrot.utils import traceback_in_one_line, get_domain, url_quote
from parrot.exceptions import (
    UrllibLoaderLoadException, SeleniumLoaderLoadException,
    SeleniumLoaderCookiesDifferentDomainsException
)

from .base import Loader


logger = logging.getLogger(__name__)


class UrllibLoader(Loader):
    def __init__(
        self, headers=None, timeout=10, *,
        attempts_limit=3, sleep_sec=10, silent=True
    ):
        super().__init__(
            attempts_limit=attempts_limit, sleep_sec=sleep_sec, silent=silent
        )
        self.headers = headers if headers is not None else {}
        self.timeout = timeout

    def _load(self, source):
        source = url_quote(source)
        request = Request(
            source,
            headers=self.headers
        )
        try:
            return urlopen(request, timeout=self.timeout).read()
        except Exception as exc:
            custom_exc = UrllibLoaderLoadException(
                source, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc, logger)
            logger.error(custom_exc)
            if isinstance(exc, HTTPError) and exc.code < 500:
                return exc
            return None


class SeleniumLoader(Loader):
    def __init__(
        self, browser_inst_or_cls, cookies=None, timeout=10, *,
        attempts_limit=3, sleep_sec=10, silent=True
    ):
        super().__init__(
            attempts_limit=attempts_limit, sleep_sec=sleep_sec, silent=silent
        )
        self.browser = None
        self.cookies = None
        self.timeout = timeout
        self._init_browser(browser_inst_or_cls, timeout)
        self._init_cookies(cookies)

    def _init_browser(self, browser_inst_or_cls, timeout):
        if isinstance(browser_inst_or_cls, type):
            browser = browser_inst_or_cls()
        else:
            browser = browser_inst_or_cls
        browser.set_page_load_timeout(timeout)
        self.browser = browser

    @staticmethod
    def _is_valid_cookies_domain(cookies):
        """
        Проверка того, что все cookies имеют одинаковый домен, или не имеют
        домен вообще

        :param cookies:
        :type cookies: list of dict
        :return:
        """
        if not cookies:
            return True
        domains = {
            cookie['domain'] for cookie in cookies if 'domain' in cookie
        }
        return len(domains) < 2

    @classmethod
    def _validate_cookies(cls, cookies):
        """
        В случае невалидных cookies вызывает
        SeleniumLoaderInvalidCookiesException

        :param cookies:
        :return:
        """
        if not cookies:
            return
        if not cls._is_valid_cookies_domain(cookies):
            raise SeleniumLoaderCookiesDifferentDomainsException(cookies)
        return

    @staticmethod
    def _get_domain_from_valid_cookies(cookies):
        if not cookies:
            return None
        for cookie in cookies:
            domain = cookie.get('domain')
            if domain is not None:
                return domain

    def _init_cookies(self, cookies):
        """
        Установить cookies

        :param cookies:
        :return:
        """
        if not cookies:
            return
        self._validate_cookies(cookies)
        self.cookies = cookies
        current_domain = get_domain(self.browser.current_url)
        cookies_domain = self._get_domain_from_valid_cookies(self.cookies)
        # Если для cookies указан домен, отличный от текущего, тогда нужно
        # текущий домен в браузере нужно заменить доменом из cookies
        if not (cookies_domain is None or current_domain == cookies_domain):
            # Переходим на страницу сайта, которая позволит сменить домен
            # браузера
            # https://selenium-python.readthedocs.org/en/latest/navigating.html#cookies
            self.browser.get(cookies_domain)
        for cookie in self.cookies:
            self.browser.delete_cookie(cookie['name'])
            self.browser.add_cookie(cookie)

    def _load(self, source):
        try:
            self.browser.get(source)
            # TODO: Продумать, как обрабатывать ошибки сервера (HTTP 500+)
            return self.browser.page_source
        except Exception as exc:
            custom_exc = SeleniumLoaderLoadException(
                source, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc, logger)
            logger.error(custom_exc)
            return None
