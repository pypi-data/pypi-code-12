# -*- encoding: utf-8 -*-
import hashlib
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import User


@view_config(
    route_name='login_info',
    request_method='GET',
    permission=NO_PERMISSION_REQUIRED,
    renderer='json',
    http_cache=0,
)
def login_info(request):
    """Get information about the connected user.
    """

    login = request.authenticated_userid
    if not login:
        return {'login': login}

    # Get information about the user from the database.
    db_session = DBSession()
    user = db_session.query(User).filter(User.user_name == login).first()
    if not user:
        return {'login': login}

    email = user.email_address

    # The default avatar URL uses Gravatar <www.gravatar.com>:
    # http://www.gravatar.com/avatar/[md5 hex digest of the email]
    avatar_url = 'http://www.gravatar.com/avatar/%s' % (
        hashlib.md5(email.encode('utf-8')).hexdigest()
    )

    return {
        'avatar_url': avatar_url,
        'display_name': user.display_name,
        'email': email,
        'login': login,
    }
