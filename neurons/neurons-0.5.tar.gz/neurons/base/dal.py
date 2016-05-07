
from spyne.util import six

from twisted.internet import reactor
from twisted.internet.threads import deferToThreadPool
from twisted.python.threadpool import ThreadPool


def _user_callables(d):
    for k,v in d.items():
        if callable(v) and not k in ('__init__', '__metaclass__'):
            yield k,v


class DBThreadPool(ThreadPool):
    def __init__(self, engine, verbose=False):
        if engine.dialect.name == 'sqlite':
            pool_size = 1

            ThreadPool.__init__(self, minthreads=1, maxthreads=1)
        else:
            ThreadPool.__init__(self)

        self.engine = engine
        reactor.callWhenRunning(self.start)

    def start(self):
        reactor.addSystemEventTrigger('during', 'shutdown', self.stop)
        ThreadPool.start(self)


class DalMeta(type(object)):
    def __new__(cls, cls_name, cls_bases, cls_dict):
        for k, v in _user_callables(cls_dict):
            def _w2(_user_callable):
                def _wrap(*args, **kwargs):
                    return deferToThreadPool(reactor, retval._pool,
                                            _et(_user_callable), *args, **kwargs)
                return _wrap
            cls_dict[k] = _w2(v)

        retval = type(object).__new__(cls, cls_name, cls_bases, cls_dict)
        return retval

    @property
    def bind(self):
        return self._db

    @bind.setter
    def bind(self, what):
        self._db = what
        self._pool = DBThreadPool(what)


@six.add_metaclass(DalMeta)
class DalBase(object):
    _db = None
    _pool = None

    def __init__(self, ctx):
        self.ctx = ctx
        self.session = ctx.udc.session
        if ctx.udc.session is None:
            self.session = ctx.udc.session = ctx.udc.Session()
