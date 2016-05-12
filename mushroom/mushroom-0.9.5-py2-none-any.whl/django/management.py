import sys

from django.core.management.base import BaseCommand, CommandError


class RunserverCommand(BaseCommand):
    '''
    Base class for creating management commands that start a mushroom server.
    In order to use this class the ``server_class`` attribute must be set.

    Example:

        ``myapp/management/commands/runmyserver.py``::

            import gevent.monkey
            from mushroom.django_support import RunserverCommand

            from myapp.server import MyServer

            class Command(RunserverCommand):
                server_class = MyServer

                def get_server(self, listener, **options):
                    gevent.monkey.patch_all()
                    return super(Command, self).get_server(listener, **options)

        ``myapp/server.py``::

            from mushroom.simple import SimpleServer

            class MyServer(SimpleServer):

                def rpc_ping(self, data):
                    return 'pong'

        Add ``myapp`` to ``settings.INSTALLED_APPS`` and do not forget
        to create the neccesary ``__init__.py`` files inside the directories
        so python can load the modules. The command can now be used like
        any other Django management command: ``manage.py runmyserver``
    '''
    args = '[optional port number, or ipaddr:port]'
    server_class = None
    server_name = 'mushroom server'
    default_host = '127.0.0.1'
    default_port = 39288 # picked by random.randint(1024, 65535)

    @property
    def help(cls):
        '''
        Property which creates a dynamic help text including the
        ``server_name`` and ``server_class``.
        '''
        return "Start %(server_name)s (server_class=%(server_module)s.%(server_class)s" % {
            'server_name': cls.server_name,
            'server_module': cls.server_class.__module__,
            'server_class': cls.server_class.__name__,
        }

    def handle(self, *args, **options):
        command_name = self.__class__.__module__.rsplit('.')[-1]
        if len(args) > 1:
            raise CommandError('Usage is %s [optional port number, or ipaddr:port]' % command_name)
        if len(args) == 0:
            listener = (self.default_host, self.default_port)
        else:
            try:
                if ':' in args[0]:
                    listener = args[0].split(':', 1)
                    listener = (listener[0], int(listener[1]))
                else:
                    listener = (self.default_host, int(args[0]))
            except ValueError:
                raise CommandError('%r is not a valid port number or address:port pair.' % args[0])
        self.stdout.write((
            'Starting %(server_name)s at %(url)s\n'
            'Quit the server with %(quit_command)s.\n'
        ) % {
            'url': 'http://%s:%d/' % listener,
            'server_name': self.server_name,
            'quit_command': 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'
        })
        server = self.get_server(listener, **options)
        server.run()

    def get_server(self, listener, **options):
        '''
        This method is creates the actual server object. It can be
        overwritten to monkey patch things using `gevent.monkey` or
        perform other setup tasks prior creating the server object.
        '''
        return self.server_class(listener)


