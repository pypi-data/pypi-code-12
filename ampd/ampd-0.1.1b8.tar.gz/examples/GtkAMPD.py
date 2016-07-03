import gi
import signal
import ampd

gi.require_version('Gtk', '3.0')

from gi.repository import GLib, Gtk


class App(Gtk.Application):
    def __init__(self):
        super(App, self).__init__()
        self.connect('startup', self.startup_cb)
        self.connect('shutdown', self.shutdown_cb)
        self.connect('activate', lambda *args: None)

        self.register(None)

    @staticmethod
    def startup_cb(self):
        self.client = ampd.ClientGLib()
        self.client.connect_to_server()
        self.ampd_worker_group = self.client.new_worker_group()

        self.win = Gtk.ApplicationWindow(application=self)
        self.box = Gtk.VBox()
        self.win.add(self.box)

        self.label = Gtk.Label(max_width_chars=50, wrap=True)
        self.box.pack_start(self.label, True, True, 0)

        self.entry = Gtk.Entry()
        self.entry.connect('activate', self.entry_activate_cb)
        self.box.pack_end(self.entry, False, False, 0)

        self.sigint_source = GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, lambda: self.win.destroy() or True)

        self.win.show_all()

    @staticmethod
    def shutdown_cb(self):
        GLib.source_remove(self.sigint_source)
        self.client.close()
        self.disconnect_by_func(self.startup_cb)
        self.disconnect_by_func(self.shutdown_cb)

    @ampd.worker
    def entry_activate_cb(self, entry):
        command = eval(entry.get_text(), vars(ampd))
        reply = yield command
        self.label.set_label(str(reply))


App().run()
