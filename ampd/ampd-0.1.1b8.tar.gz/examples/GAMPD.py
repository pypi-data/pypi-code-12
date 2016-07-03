from gi.repository import Gio
import pprint
import sys
import ampd


class App(Gio.Application):
    def __init__(self):
        super(App, self).__init__()
        self.connect('startup', self.startup_cb)
        self.connect('shutdown', self.shutdown_cb)
        self.connect('activate', self.prompt)

    @staticmethod
    def startup_cb(self):
        self.client = ampd.ClientGLib()
        self.client.connect_to_server()
        self.ampd_worker_group = self.client.new_worker_group()
        self.hold()

    @staticmethod
    def shutdown_cb(self):
        self.client.close()
        self.disconnect_by_func(self.startup_cb)
        self.disconnect_by_func(self.shutdown_cb)
        self.disconnect_by_func(self.prompt)

    @staticmethod
    @ampd.worker
    def prompt(self):
        PROMPT = 'ampd: '
        yield ampd.CONNECT
        print('Connected')
        while True:
            try:
                try:
                    command = input(PROMPT) if sys.version_info >= (3, 0) else raw_input(PROMPT)
                except EOFError:
                    command = None
                if not command:
                    self.release()
                    return
                command = eval(command, vars(ampd))
            except:
                sys.excepthook(*sys.exc_info())
                continue
            try:
                try:
                    reply = yield command
                except DeprecationWarning as reply:
                    print('Warning: \"%s\" is deprecated' % command.split(' ')[0])
                    reply = reply.message
                MyPrettyPrinter().pprint(reply)
            except GeneratorExit:
                print('Disconnected')
                break
            except Exception as e:
                print('ERROR:', e)
                self.release()
                raise


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, obj, context, maxlevels, level):
        if isinstance(obj, str):
            return (obj, True, False)
        return pprint.PrettyPrinter.format(self, obj, context, maxlevels, level)


App().run()
