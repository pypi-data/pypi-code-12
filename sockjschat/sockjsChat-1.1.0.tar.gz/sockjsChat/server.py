import sys
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from urls import urls
from settings import settings

define("port", default=9090, help="run on the given port", type=int)

print '\n\ninvoking server.py'

class Application(tornado.web.Application):
    print '\n\ninvoked Application()\n'
    def __init__(self):
        print '\ninside Application __init__()'
        tornado.web.Application.__init__(self, urls, **settings)
        print 'Aapplication __init__ caleed with web.Application()'
        print 'returning from Application __init__'


def main():
    tornado.options.parse_command_line()
    print '\ncreating app=Applicatoin()'
    app = Application()
    print '\napp= Aapplication() created -> app : ',app
    app.listen(options.port)
    print "\nStarting server on http://127.0.0.1:%s" % options.port

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print "\nStopping server."






if __name__ == "__main__":
    main()