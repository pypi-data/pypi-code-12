# -*- encoding: utf-8 -*-

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound

from pyramid.response import Response

from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.security import remember

from pyramid.view import forbidden_view_config

from xbus.monitor.utils.singleton import Singleton

from xbus.monitor.i18n import req_l10n

try:
    import lasso
    lasso_loaded = True
except ImportError:
    lasso = None
    lasso_loaded = False


class LassoSingle(object):
    __metaclass__ = Singleton

    def __init__(self, sp_meta, sp_key, idp_meta):
        """
        @param sp_meta: filename of the metadata file for the service provider
        @type sp_meta: string

        @param sp_key: filename of the service provider key
        @type sp_key: string

        @param idp_meta: filename of the Identity provider metadata.xml file
        @type idp_meta: string
        """
        self.reads, errors = self.__read_conf_file(sp_meta, sp_key, idp_meta)

        if errors:
            raise HTTPForbidden(detail=u"\n".join(errors))

        self.sp_meta_xml = self.reads[0]
        self.sp_key = self.reads[1]
        self.idp_meta_xml = self.reads[2]

        self.server = lasso.Server.newFromBuffers(
            self.sp_meta_xml,
            self.sp_key
        )

        self.server.addProviderFromBuffer(
            lasso.PROVIDER_ROLE_IDP,
            self.idp_meta_xml
        )

    @staticmethod
    def __read_conf_file(*args):
        res = []
        errs = []
        for arg in args:
            try:
                with open(arg, 'r') as f:
                    res.append(f.read())
            except IOError as e:
                errs.append(str(e))
        return res, errs

    def get_login(self):
        """create a new login instance for each request.
        """
        return lasso.Login(self.server)


def _login_referrer(request, params):
    """Extract a "came_from" parameter from the specified dictionary or
    just provide an URL to the home page.
    """
    return params.get('came_from', request.path)


def forbidden_view(exc, request):
    """Redirect unlogged users to the login view; answer with a "forbidden"
    message otherwise.
    """

    if not request.authenticated_userid:
        # Not authenticated; redirect to the login view.
        return HTTPFound(location=request.route_url(
            'login', _query=(('came_from', request.path),),
        ))

    _ = req_l10n(request)
    return Response(_('You are not allowed'), status='403 Forbidden')


def login_view(request):
    """Redirect to either the login page or the previous page.
    Request params:
        * came_from (optional): The page to redirect to when logged in.
    """

    login_referrer = _login_referrer(request, request.params)

    if authenticated_userid(request):
        return HTTPFound(location=login_referrer)

    # Save the previous page.
    request.session['came_from'] = login_referrer

    # Redirect to Authentic.

    sp_meta = request.registry.settings['saml2.sp_meta']
    sp_key = request.registry.settings['saml2.priv_key']
    idp_meta = request.registry.settings['saml2.idp_meta']

    login = LassoSingle(sp_meta, sp_key, idp_meta).get_login()

    login.initAuthnRequest()
    login.request.nameIdPolicy.format = None
    login.request.nameIdPolicy.allowCreate = True
    login.buildAuthnRequestMsg()

    return HTTPFound(location=login.msgUrl)


def login_metadata_view(request):
    with open(
        request.registry.settings['saml2.sp_meta'], 'r'
    ) as sp_meta_file:
        sp_meta = sp_meta_file.read()
    request.response.content_type = 'text/xml'
    return sp_meta


def login_success_view(request):
    """Called when the user has been redirected back to our site from the SAML2
    provider.
    Conclude the handshake, fetch some information (such as the user name,
    security groups...) and redirect to the home page.
    """
    _ = req_l10n(request)

    sp_meta = request.registry.settings['saml2.sp_meta']
    sp_key = request.registry.settings['saml2.priv_key']
    idp_meta = request.registry.settings['saml2.idp_meta']

    login = LassoSingle(sp_meta, sp_key, idp_meta).get_login()

    saml_response = request.params.get('SAMLResponse', None)
    if not saml_response:
        raise HTTPForbidden('%s: %s' % (
            _('Login error'), _('No "SAMLResponse" parameter')
        ))
    try:
        login.processAuthnResponseMsg(saml_response)
    except (lasso.DsError, lasso.ProfileCannotVerifySignatureError):
        raise HTTPForbidden('%s: %s' % (
            _('Login error'), _('Invalid signature')
        ))
    except lasso.Error as e:
        raise HTTPForbidden('%s: %s' % (_('Login error'), str(e)))
    try:
        login.acceptSso()
    except lasso.Error as e:
        raise HTTPForbidden('%s: %s' % (_('Login error'), str(e)))

    # Read authentic attributes to fetch the user role.
    attributes = {}
    for att_statement in login.assertion.attributeStatement:
        for at in att_statement.attribute:
            values = attributes.setdefault(at.name, [])
            for value in at.attributeValue:
                content = [v.exportToXml() for v in value.any]
                content = ''.join(content)
                values.append(content)
    roles = attributes.get('role')
    if not roles:
        raise HTTPForbidden('%s: %s' % (
            _('Login error'), _('The authentic login is not in a group')
        ))

    request.session['authentic_roles'] = roles

    login_referrer = _login_referrer(request, request.session)
    headers = remember(request, login.assertion.subject.nameId.content)

    return HTTPFound(location=login_referrer, headers=headers)


def logout_view(request):
    """Just empty the session and let the client handle this."""
    request.session.clear()
    request.response.headerlist.extend(forget(request))
    return {'auth_kind': request.registry.settings.auth_kind}


def setup(config):
    """Setup SAML2 auth - to be called when the app starts."""

    # Ensure python-lasso is available.
    if not lasso_loaded:
        raise Exception(
            'SAML2 enabled in settings but python-lasso could not be loaded.\n'
            'Download Lasso from <http://lasso.entrouvert.org/>.'
        )

    # Add routes for SAML2 views.
    config.add_route('login', '/login')
    config.add_route('login_metadata', '/login_metadata')
    config.add_route('login_success', '/login_success')
    config.add_route('logout', '/logout')

    # Register SAML2 views. Avoid using the "view_config" decorator as we don't
    # want the views to be added when SAML2 is disabled.
    def add_view(view, **kwargs):
        config.add_view(
            view,
            permission=NO_PERMISSION_REQUIRED,
            http_cache=0,
            **kwargs
        )
    add_view(login_view, route_name='login')
    add_view(login_metadata_view, route_name='login_metadata',
             renderer='string')
    add_view(login_success_view, route_name='login_success')
    add_view(logout_view, route_name='logout', renderer='json')

    # Register the forbidden view.
    forbidden_view_config()(forbidden_view)
