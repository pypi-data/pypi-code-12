import threading
from collections import OrderedDict

from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

from ievv_opensource.utils.logmixin import LogMixin


class WatchConfig(object):
    """
    Used by plugins to configure watching.

    See :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.watch`.
    """
    def __init__(self, watchfolders, watchregexes, runnable):
        """
        Args:
            watchfolders: List of folders to watch.
            watchregexes: List of regexes to watch.
            runnable: A runnable (an object with a run()-method), such as a plugin.
        """
        self.folders = watchfolders
        self.regexes = watchregexes
        self.runnable = runnable

    def run(self):
        self.runnable.run()


class WatchConfigPool(LogMixin):
    def __init__(self):
        self._watchconfigs = []

    def extend(self, watchconfigs):
        self._watchconfigs.extend(watchconfigs)

    def get_logger_name(self):
        return 'watcherpool'

    def __watch_folder(self, folderpath, runnables, regexes):
        event_handler = EventHandler(
            runnables=runnables,
            regexes=regexes
        )
        observer = Observer()
        observer.schedule(event_handler, folderpath, recursive=True)
        self.get_logger().info(
            'Starting watcher for folder {!r} with regexes {!r}. '
            'Runnables notified of changes: {}.'.format(
                folderpath, regexes, ', '.join(str(runnable) for runnable in runnables)))
        observer.start()
        return observer

    def __build_foldermap(self):
        # Note: We use OrderedDict here, and a list (instead of set) for
        #       runnables below to maintain the order of apps when building.
        #       This should not matter, but it is nice to have the apps
        #       build in the same order as they are listed in settings.
        foldermap = OrderedDict()
        for watchconfig in self._watchconfigs:
            for folderpath in watchconfig.folders:
                if folderpath not in foldermap:
                    foldermap[folderpath] = {
                        'regexes': set(),
                        'runnables': []
                    }
                foldermap[folderpath]['regexes'].update(watchconfig.regexes)
                if watchconfig.runnable not in foldermap[folderpath]['runnables']:
                    foldermap[folderpath]['runnables'].append(watchconfig.runnable)
        return foldermap

    def watch(self):
        foldermap = self.__build_foldermap()
        observers = []
        for folderpath, folderkwargs in foldermap.items():
            observer = self.__watch_folder(folderpath=folderpath, **folderkwargs)
            observers.append(observer)
        return observers


class EventHandler(RegexMatchingEventHandler):
    """
    Event handler for watchdog --- this is used by each watcher
    thread to react to changes in the filesystem.

    This is instantiated by :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.watch`
    to watch for changes in files matching
    :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_regexes`
    in the folders specified in
    :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_folders`.
    """
    def __init__(self, *args, **kwargs):
        self.runnables = kwargs.pop('runnables')
        self.runtimer = None
        self.is_running = False
        super(EventHandler, self).__init__(*args, **kwargs)

    def handle_plugin_run(self):
        if self.is_running:
            return
        self.is_running = True
        for runnable in self.runnables:
            runnable.run()
        self.is_running = False

    def on_any_event(self, event):
        if self.runtimer:
            self.runtimer.cancel()
        self.runtimer = threading.Timer(0.5, self.handle_plugin_run)
        self.runtimer.start()
