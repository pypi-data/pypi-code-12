# -*- encoding: utf-8 -*-
# TODO: upgrade to sha256!!!!!
from hashlib import sha1

from pyramid.security import NO_PERMISSION_REQUIRED

from pyramid.httpexceptions import HTTPFound

from pyramid.security import remember
from pyramid.security import forget

from pyramid.view import forbidden_view_config
from pyramid.response import Response

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import User

from xbus.monitor.i18n import req_l10n


def setup(config):
    """helper to call during app configuration phase
    ie:  xbus.monitor:core.main

    :param config: the config instance for the running pyramid
    :return: Nothing
    """

    # setup login
    config.add_route(
        'login', '/login',
        # permission=NO_PERMISSION_REQUIRED,
    )
    config.add_view(
        loginview,
        permission=NO_PERMISSION_REQUIRED,
        http_cache=0,
        renderer="xbus.monitor:templates/login.pt",
        route_name="login",
    )

    # setup logout
    config.add_route(
        'logout', '/logout',
        # permission=NO_PERMISSION_REQUIRED,
    )
    config.add_view(
        logoutview,
        permission=NO_PERMISSION_REQUIRED,
        http_cache=0,
        route_name="logout",
    )

    # Register the forbidden view.
    forbidden_view_config()(forbidden_view)


def loginview(request):
    """ this view is not decorated with the view_config decorator to avoid
    being always added because we only want it to be present when
    the configuration says we want http authentication using forms.

    The config.add_view is only added in the setup function which will be
    called from the application startup code, ie: xbus.monitor:core.main
    """
    _ = req_l10n(request)

    # find the url on which the login route is mounted
    login_url = request.route_url('login')

    referrer = request.url
    if referrer == login_url:
        # never use the login form itself as came_from
        referrer = '/'

    came_from = request.params.get('came_from', referrer)
    login = ''
    password = ''
    message = _('Please log in before using this application')

    result = dict(
        page_title=_("Login"),
        message=message,
        url=request.route_url('login'),
        came_from=came_from,
        login=login,
        password=password,
    )

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']

        if not login or not password:
            return result

        password = password.encode('utf-8')
        db_session = DBSession()

        # Ensure the user is in the DB and find its hashed password.
        user = db_session.query(User).filter(
            User.user_name == login
        ).first()

        if not user:
            return result

        user_pass = user.password.encode('utf-8')

        # Verify the provided password against the hashed one.
        hashed_pass = sha1()
        hashed_pass.update(password + user_pass[:40])
        if user_pass[40:] != hashed_pass.hexdigest().encode('utf-8'):
            return result

        headers = remember(request, login)
        return HTTPFound(location=came_from, headers=headers)

    else:
        return result


def logoutview(request):
    """same as for login, we do not decorate the view because we want to
    manually add the view if and only if the http authentication is enabled
    see the setup function and where it is called: ie core.main()
    """
    # forget the user
    headers = forget(request)
    # find the login url by its route name
    login_url = request.route_url('login')
    # and redirect the user to it because now
    # this is the only thing she can see
    return HTTPFound(location=login_url, headers=headers)


def forbidden_view(request):
    """this view will be used to redirect unlogged users to the login form
    and to display a real Forbidden to users that ARE logged but don't have
    access
    """
    _ = req_l10n(request)
    # do not allow a user to login if they are already logged in
    if request.authenticated_userid:
        return Response(_('You are not allowed'), status='401 Unauthorized')

    else:
        loc = request.route_url('login', _query=(('came_from', request.path),))
        return HTTPFound(location=loc)
