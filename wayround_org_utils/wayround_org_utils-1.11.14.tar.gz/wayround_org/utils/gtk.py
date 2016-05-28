
import logging
import os.path
import threading
import time

import wayround_org.utils.path


try:
    from gi.repository import Gtk
    from gi.repository import Gdk
    from gi.repository import GdkPixbuf
    from gi.repository import GLib
except:
    pass

else:

    class GtkIteratedLoop:

        # NOTE: this class is tending to be deprecated. we must obey to use
        # Gtk+ threading rules

        def __init__(self, sleep_fraction=0.01):
            self._exit_event = threading.Event()
            self._started = False
            self._sleep_fraction = sleep_fraction

        def wait(self, timeout=None):

            if self._started:
                self._exit_event.wait(timeout)
            else:
                self._started = True

                self._exit_event.clear()

                while not self._exit_event.is_set():
                    while Gtk.events_pending():
                        Gtk.main_iteration_do(False)

                    time.sleep(self._sleep_fraction)

                self._started = False

        def stop(self):
            self._exit_event.set()

    class TextView:

        def __init__(self):

            ui_file = os.path.join(
                os.path.dirname(__file__), 'ui', 'textview.glade'
                )

            ui = Gtk.Builder()
            ui.add_from_file(ui_file)

            self.ui = widget_dict(ui)

            self.ui['button1'].connect('clicked', self.onSaveAsActivated)

        def onSaveAsActivated(self, button):

            fc = Gtk.FileChooserDialog(
                "Select File To Save List",
                self.ui['window1'],
                Gtk.FileChooserAction.SAVE,
                (
                    Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
                    )
                )

            rc_resp = fc.run()

            path = fc.get_filename()

            fc.destroy()

            if rc_resp == Gtk.ResponseType.OK:

                dialog_resp = Gtk.ResponseType.YES

                if os.path.exists(path) and os.path.isdir(path):
                    dialog_resp = Gtk.ResponseType.NO

                    dia = Gtk.MessageDialog(
                        self.ui['window1'],
                        Gtk.DialogFlags.MODAL,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Directory not acceptable"
                        )

                    dia.run()
                    dia.destroy()

                elif os.path.exists(path) and os.path.isfile(path):

                    dialog_resp = Gtk.ResponseType.NO

                    dia = Gtk.MessageDialog(
                        self.ui['window1'],
                        Gtk.DialogFlags.MODAL,
                        Gtk.MessageType.QUESTION,
                        Gtk.ButtonsType.YES_NO,
                        "File exists. Rewrite?"
                        )

                    if dia.run() == Gtk.ResponseType.YES:
                        dialog_resp = Gtk.ResponseType.YES

                    dia.destroy()

                else:
                    pass

                if (
                        (os.path.exists(path)
                         and dialog_resp == Gtk.ResponseType.YES)
                        or
                        not os.path.exists(path)
                        ):

                    buff = self.ui['textview1'].get_buffer()
                    txt = buff.get_text(
                        buff.get_start_iter(), buff.get_end_iter(), False
                        )

                    try:
                        f = open(path, 'w')
                    except:
                        dia = Gtk.MessageDialog(
                            self.ui['window1'],
                            Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.OK,
                            "Couldn't rewrite file `{}'".format(path)
                            )

                        dia.run()
                        dia.destroy()
                    else:

                        f.write(txt)
                        f.close()

            return

    class MessageDialog(Gtk.MessageDialog):

        """
        Documentation same as for Gtk.MessageDialog
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.set_modal(True)
            self.set_transient_for(args[0])
            self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

            self.wayround_org_response = Gtk.ResponseType.NONE
            self.wayround_org_iteration_loop = GtkIteratedLoop()

        def run(self):

            self.show_all()

            self.connect('close', self.wayround_org_close_listener)
            self.connect('response', self.wayround_org_response_listener)

            self.wayround_org_iteration_loop.wait()

            return self.wayround_org_response

        def destroy(self, *args, **kwargs):
            self.wayround_org_iteration_loop.stop()
            return super().destroy(*args, **kwargs)

        def wayround_org_response_listener(self, dialog, response_id):
            self.wayround_org_response = response_id
            self.wayround_org_iteration_loop.stop()

        def wayround_org_close_listener(self, dialog):
            self.wayround_org_iteration_loop.stop()

    class Waiter:

        @classmethod
        def wait_thread(cls, thread):
            w = cls(thread.join, None, thread.is_alive)
            w.wait()
            return

        def __init__(
                self,
                wait_or_join_meth,
                ret_val_good_for_loop,
                is_alive_meth=None,
                timeout=0.2,
                waiter_sleep_time=0.01
                ):

            if not callable(wait_or_join_meth):
                raise TypeError("`wait_or_join_meth' must be callable")

            if is_alive_meth is not None and not callable(is_alive_meth):
                raise TypeError("`is_alivemeth' must be callable")

            if is_alive_meth is not None and waiter_sleep_time == 0:
                raise ValueError(
                    "if `is_alivemeth' is set,"
                    " `waiter_sleep_time' must not be 0"
                    )

            self._timeout = timeout
            self._is_alive_meth = is_alive_meth
            self._wait_or_join_meth = wait_or_join_meth
            self._waiter_sleep_time = waiter_sleep_time
            self._ret_val_good_for_loop = ret_val_good_for_loop
            self._thread = None
            self._stop_event = threading.Event()
            self._result = None
            self._iterated_loop = GtkIteratedLoop(
                sleep_fraction=waiter_sleep_time
                )

        def _start(self):

            if self._thread is None:

                self._thread = threading.Thread(
                    target=self._waiter,
                    )
                self._thread.start()

        def stop(self):
            self._iterated_loop.stop()
            self._stop_event.set()

        def wait(self, timeout=None):
            self._start()
            self._iterated_loop.wait(timeout)

        def _waiter(self):

            while True:

                if self._is_alive_meth is not None:
                    if not self._is_alive_meth():
                        break
                else:

                    if (self._wait_or_join_meth(self._timeout)
                            != self._ret_val_good_for_loop):
                        break

                time.sleep(self._waiter_sleep_time)

                if self._stop_event.is_set():
                    break

            self.stop()
            self._thread = None
            return

    class RelatedWindowCollector:

        def __init__(self):

            self._lock = threading.RLock()
            self.clear(init=True)

        def clear(self, init=False):

            self._constructor_cbs = {}

            self._singles = {}
            self._multiples = set()

            return

        def _window_methods_check(self, window):

            for i in ['run', 'show', 'destroy']:

                if not hasattr(window, i):
                    raise KeyError(
                        "{} has not attribute `{}'".format(window, i)
                        )

                if not callable(getattr(window, i)):
                    raise KeyError(
                        "`{}' not callable in {}".format(i, window)
                        )

            return

        def set_constructor_cb(self, name, cb, single=True):

            if not isinstance(name, str):
                raise ValueError("`name' must be str")

            if not isinstance(single, bool):
                raise ValueError("`single' must be bool")

            if not callable(cb):
                raise ValueError("`cb' must be callable")

            self._lock.acquire()

            if name in self._constructor_cbs:
                logging.warning("{}:Redefining `{}'".format(self, name))

            self._constructor_cbs[name] = {'cb': cb, 'single': single}

            self._lock.release()

            return

        def _check_name(self, name):

            if name not in self._constructor_cbs:
                raise KeyError(
                    "{}:Constructor for `{}' not registered".format(
                        self,
                        name
                        )
                    )

            return

        def get(self, name):

            self._check_name(name)

            ret = None

            self._lock.acquire()

            try:
                cdata = self._constructor_cbs[name]

                if cdata['single']:
                    if name in self._singles:
                        ret = self._singles[name]
                    else:
                        window = cdata['cb']()
                        self._window_methods_check(window)
                        self._singles[name] = window
                        ret = window

                else:
                    window = cdata['cb']()
                    self._window_methods_check(window)
                    self._multiples.add(window)
                    ret = window

            except:
                logging.exception("Exception")

            self._lock.release()

            return ret

        def destroy_window(self, name):

            self._lock.acquire()

            names = list(self._singles)
            if name in names:
                self._singles[name].destroy()
                del self._singles[name]

            self._lock.release()

            return

        def destroy_windows(self):

            self._lock.acquire()

            names = list(self._singles)
            for i in names:
                self.destroy_window(i)

            for i in list(self._multiples):
                i.destroy()
                self._multiples.remove(i)

            self._lock.release()

            return

        def destroy(self):
            self.destroy_windows()
            self.clear()

    def text_view(text, title='', size=None):

        if size is None:
            size = (700, 400)

        tw = TextView()

        tb = Gtk.TextBuffer()
        tb.set_text(str(text))

        tw.ui['textview1'].set_buffer(tb)

        tw.ui['window1'].set_default_size(*size)
        tw.ui['window1'].set_title(str(title))

        tw.ui['window1'].show_all()

        return

    def widget_dict(builder):

        ret = {}

        all_objects = builder.get_objects()

        for i in all_objects:
            if isinstance(i, Gtk.Buildable):
                ret[Gtk.Buildable.get_name(i)] = i

        return ret

    def list_view_select_and_scroll_to_name(treeview, name):

        sel = treeview.get_selection()
        model = treeview.get_model()
        ind = -1
        if model:
            for i in model:
                ind += 1
                if i[0] == name:
                    path = Gtk.TreePath.new_from_string(str(ind))
                    sel.select_path(path)
                    treeview.scroll_to_cell(path, None, True, 0.5, 0.5)
                    break

        return

    def process_events():
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        return

    class DirectoryTreeView(Gtk.TreeView):

        def __init__(self):
            super().__init__()

            self._root_dir = os.path.expanduser('~')

            self._show_hidden = False

            self._store = Gtk.TreeStore(str, str)

            self.set_headers_visible(False)
            self.set_search_column(1)

            _c = Gtk.TreeViewColumn()
            _r = Gtk.CellRendererPixbuf()
            _c.pack_start(_r, False)
            _c.add_attribute(_r, 'icon-name', 0)
            # _c.set_title('Icon')
            self.append_column(_c)

            _c = Gtk.TreeViewColumn()
            _r = Gtk.CellRendererText()
            _c.pack_start(_r, False)
            _c.add_attribute(_r, 'text', 1)
            # _c.set_title('Name')
            self.append_column(_c)

            self.set_model(self._store)

            self.connect('row-activated', self.on_item_acivated)

            return

        def set_root_directory(self, path):

            if os.path.isdir(path):
                self._root_dir = path

            self.reload()

            return

        def get_root_directory(self):
            return self._root_dir

        def set_directory(self, path):
            return

        def set_show_hidden(self, value):
            self._show_hidden = value

        def get_show_hidden(self):
            return self._show_hidden

        def _list_expanded2(self, model, itera, list_to_fill):

            while itera is not None:
                p = model.get_path(itera)
                if self.row_expanded(p):
                    list_to_fill.append(p)
                    childiter = model.iter_children(itera)
                    self._list_expanded2(model, childiter, list_to_fill)
                itera = model.iter_next(itera)

            return

        def _list_expanded(self):

            ret = []

            m = self.get_model()

            itera = m.get_iter_first()

            if iter is not None:

                self._list_expanded2(m, itera, ret)

            return

        def reload(self):

            # TODO: complete or remove
            # sel_rows = self.get_selection().get_selected_rows()
            # exp_rows = self._list_expanded()

            self.load_dir(None, self._root_dir)

            return

        def load_dir(self, itera, path):

            m = self.get_model()

            chi = m.iter_children(itera)
            res = True

            while chi is not None and res != False:
                res = m.remove(chi)

            lst = os.listdir(path)

            dirs = []
            files = []

            for i in lst:
                if os.path.isdir(
                        wayround_org.utils.path.join(path, i)
                        ):

                    dirs.append(i)
                else:
                    files.append(i)

            dirs.sort()
            files.sort()

            for i in dirs:
                m.append(itera, ['folder', i])

            for i in files:
                m.append(itera, ['txt', i])

            return

        def on_item_acivated(self, widget, path, column):

            m = self.get_model()

            pth = self.convert_indices_to_path(path.get_indices())

            fpth = wayround_org.utils.path.join(self._root_dir, pth)

            if os.path.isdir(fpth):

                self.load_dir(
                    m.get_iter(path),
                    fpth
                    )

                if m.iter_has_child(m.get_iter(path)):
                    self.expand_row(path, False)
                    self.scroll_to_cell(path, None, True, 0.5, 0.0)

            return

        def convert_indices_to_path(self, indices):

            lst = []

            m = self.get_model()
            for i in range(len(indices)):

                value = m.get_iter(Gtk.TreePath(indices[:i + 1]))

                lst.append(m[value][1])

            return os.path.sep.join(lst)

        def get_selected_path(self):

            sel = self.get_selection()

            model, itera = sel.get_selected()

            ret = self.get_root_directory()

            if itera:

                path = model.get_path(itera)

                pth = self.convert_indices_to_path(path.get_indices())

                ret = wayround_org.utils.path.join(self._root_dir, pth)

            return ret

        def get_selected_iter(self):

            sel = self.get_selection()

            model, itera = sel.get_selected()

            return itera

        def get_selected_iter_parent(self):

            sel = self.get_selection()

            model, itera = sel.get_selected()

            ret = gtk_tree_model_get_iter_parent(model, itera)

            return ret

    class ToIdle:

        """
        can be strange behavior with 'popup-menu' signal
        """

        @classmethod
        def new_from_callable(cls, action):
            return cls(action)

        def __init__(self, action):
            if not callable(action):
                raise ValueError("`action' must be callable")
            self._action = action
            return

        def __call__(self, *args, **kwargs):
            GLib.idle_add(self._action, *args, **kwargs)
            return

    def to_idle(action):
        """
        Read ToIdle class docs
        """
        return ToIdle.new_from_callable(action)

    def idle_add(*args, **kwargs):
        """
        shortcut
        """
        return GLib.idle_add(*args, **kwargs)

    def hide_on_delete(widget, event, *args):
        return Gtk.Widget.hide_on_delete(widget)

    def get_root_gtk_window(widget, limit=100):

        ret = None

        n = widget

        while not isinstance(n, Gtk.Window) and limit > 0:

            if not hasattr(n, 'get_parent') or not callable(n.get_parent):
                break

            n = n.get_parent()
            limit -= 1

        if isinstance(n, Gtk.Window):
            ret = n

        return ret

    def gtk_tree_model_get_iter_parent(treemodel, itera):

        path = treemodel.get_path(itera)

        indices = path.get_indices()

        ret = None

        len_indices = len(indices)

        if len_indices > 1:

            if len_indices == 1:
                path = Gtk.TreePath.new_first()
            else:
                path = Gtk.TreePath(indices[:-1])

            ret = treemodel.get_iter(path)

        return ret
