from xbus.monitor.models.monitor import User

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'user'


@view_decorators.list(_MODEL)
def user_list(request):
    return get_list(User, request.GET)


@view_decorators.read(_MODEL)
def user_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()
