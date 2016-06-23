from datetime import datetime
from Products.CMFCore.utils import getToolByName

from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList


def get_ip(request):
    if "HTTP_X_FORWARDED_FOR" in request.environ:
        # Virtual host
        ip = request.environ["HTTP_X_FORWARDED_FOR"]
    elif "REMOTE_ADDR" in request.environ:
        # Non-virtualhost
        ip = request.environ["REMOTE_ADDR"]
    else:
        ip = None

    return ip

def userLoggedIn(user, event):
    userip = get_ip(user.REQUEST)
    logintime = datetime.now()

    mtool = getToolByName(user, 'portal_membership')
    if not mtool:
        return

    member = mtool.getMemberById(user.getId())
    if not member:
        return

    anno = IAnnotations(member)
    data = anno.setdefault('login_history', PersistentList())
    data.append({'date': logintime, 'ip': userip})
