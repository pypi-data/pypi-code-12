import click
import socket

from splinter import Browser
from unipath import Path
from fabric.api import env
from functools import wraps
from urlparse import urljoin
from mh_pages.pages import LoginPage
from click.exceptions import UsageError
from fabric.contrib.files import exists as remote_exists


class ClickState(object):

    def __init__(self):
        self.username = None
        self.password = None
        self.host = None
        self.ssh_user = None
        self.driver = 'firefox'
        self.inbox_path = '/var/matterhorn/inbox'
        self.working_dir = None

    @property
    def base_url(self):
        return 'http://' + self.host + '/'

    @property
    def inbox_dest(self):
        return Path(self.inbox_path) \
            .parent.child('files', 'collection', 'inbox')


pass_state = click.make_pass_decorator(ClickState, ensure=True)


def state_callback(ctx, option, value):
    state = ctx.ensure_object(ClickState)
    if value is not None:
        setattr(state, option.name, value)


def host_callback(ctx, option, value):
    state = ctx.ensure_object(ClickState)
    if value is not None:
        setattr(state, 'host', socket.gethostbyaddr(value)[0])
    return value


def password_option(f, required=True):
    return click.option('-p', '--password',
                        expose_value=False,
                        required=required,
                        help='MH admin login password',
                        envvar='MHUIT_PASSWORD',
                        callback=state_callback)(f)


def username_option(f, required=True):
    return click.option('-u', '--username',
                        expose_value=False,
                        required=required,
                        help='MH admin login username',
                        envvar='MHUIT_USERNAME',
                        callback=state_callback)(f)


def user_option(f):
    return click.option('--ssh_user',
                        expose_value=False,
                        help='The user to execute remote tasks as',
                        envvar='MHUIT_SSH_USER',
                        callback=state_callback)(f)


def host_option(f, required=True):
    return click.option('-H', '--host',
                        expose_value=False,
                        required=required,
                        help='host/ip of remote admin node',
                        envvar='MHUIT_HOST',
                        callback=host_callback)(f)


def driver_option(f):
    return click.option('-D', '--driver',
                        expose_value=False,
                        help='Selenium driver to use: firefox|chrome',
                        envvar='MHUIT_DRIVER',
                        callback=state_callback)(f)


def inbox_path_option(f):
    return click.option('-I', '--inbox_path',
                        expose_value=False,
                        help='alternate path to recording inbox',
                        envvar='MHUIT_INBOX_PATH',
                        callback=state_callback)(f)


def selenium_options(f):
    f = password_option(f)
    f = username_option(f)
    f = host_option(f)
    f = driver_option(f)
    return f


def inbox_options(f):
    f = host_option(f)
    f = user_option(f)
    f = inbox_path_option(f)
    return f


def init_fabric(click_cmd):
    @wraps(click_cmd)
    def wrapped(state, *args, **kwargs):

        # set up the fabric env
        env.host_string = state.host
        if state.ssh_user:
            env.user = state.ssh_user

        if not remote_exists(state.inbox_path):
            raise UsageError(
                "Invalid remote inbox path: %s" % state.inbox_path)

        return click_cmd(state, *args, **kwargs)
    return wrapped


def init_browser(init_path=''):
    def decorator(click_cmd):
        @wraps(click_cmd)
        def _wrapped_cmd(state, *args, **kwargs):

            try:
                state.browser = Browser(state.driver)
                state.browser.visit(urljoin(state.base_url, init_path))

                if 'Login' in state.browser.title:
                    page = LoginPage(state.browser)
                    with page.wait_for_page_change():
                        page.login(state.username, state.password)
                        if 'Login' in state.browser.title:
                            raise RuntimeError(
                                "Login failed. Check your user/pass.")
                    state.browser.visit(urljoin(state.base_url, init_path))

                result = click_cmd(state, *args, **kwargs)
                return result
            finally:
                state.browser.quit()

        return _wrapped_cmd
    return decorator
