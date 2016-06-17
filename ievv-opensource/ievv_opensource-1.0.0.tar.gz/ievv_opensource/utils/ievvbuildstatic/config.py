import logging
import os
import time

from django.apps import apps

from ievv_opensource.utils.ievvbuildstatic.watcher import WatchConfigPool
from ievv_opensource.utils.logmixin import LogMixin


class App(LogMixin):
    """
    Configures how ``ievv buildstatic`` should build the static files for a Django app.
    """
    def __init__(self, appname, version, plugins,
                 sourcefolder='staticsources',
                 destinationfolder='static'):
        """
        Parameters:
            appname: Django app label (I.E.: ``myproject.myapp``).
            plugins: Zero or more :class:`ievv_opensource.utils.ievvbuild.pluginbase.Plugin`
                objects.
            sourcefolder: The folder relative to the app root folder where
                static sources (I.E.: less, coffescript, ... sources) are located.
                Defaults to ``staticsources``.
        """
        self.apps = None
        self.version = version
        self.appname = appname
        self.sourcefolder = sourcefolder
        self.destinationfolder = destinationfolder
        self.installers = {}
        self.plugins = []
        for plugin in plugins:
            self.add_plugin(plugin)

    def add_plugin(self, plugin):
        """
        Add a :class:`ievv_opensource.utils.ievvbuildstatic.lessbuild.Plugin`.
        """
        plugin.app = self
        self.plugins.append(plugin)

    def run(self):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`
        for all plugins within the app.
        """
        for plugin in self.plugins:
            plugin.run()

    def install(self):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.install`
        for all plugins within the app.
        """
        for plugin in self.plugins:
            plugin.install()
        for installer in self.installers.values():
            installer.install()

    def get_app_config(self):
        """
        Get the AppConfig for the Django app.
        """
        if not hasattr(self, '_app_config'):
            self._app_config = apps.get_app_config(self.appname)
        return self._app_config

    def get_appfolder(self):
        """
        Get the absolute path to the Django app root folder.
        """
        return self.get_app_config().path

    def get_app_path(self, apprelative_path):
        """
        Returns the path to the directory joined with the
        given ``apprelative_path``.
        """
        return os.path.join(self.get_appfolder(), apprelative_path)

    def get_source_path(self, *sourcefolder_relative_path):
        """
        Returns the absolute path to a folder within the source
        folder.
        """
        sourcefolder = os.path.join(self.get_app_path(self.sourcefolder), self.appname)
        if sourcefolder_relative_path:
            return os.path.join(sourcefolder, *sourcefolder_relative_path)
        else:
            return sourcefolder

    def get_destination_path(self, *sourcefolder_relative_path, **kwargs):
        """
        Returns the absolute path to a folder within the destination
        folder.

        Parameters:
            sourcefolder_relative_path: Path relative to the source folder.
                Same format as ``os.path.join()``.
            new_extension: A new extension to give the destination path.
                See example below.


        Examples:

            Get the destination file for a coffeescript file - extension
            is changed from ``.coffee`` to ``.js``::

                get_destination_path('mylib', 'app.coffee', new_extension='.js')

        """
        new_extension = kwargs.get('new_extension', None)
        destinationfolder = os.path.join(
            self.get_app_path(self.destinationfolder), self.appname, self.version)
        if sourcefolder_relative_path:
            path = os.path.join(destinationfolder, *sourcefolder_relative_path)
            if new_extension:
                path, extension = os.path.splitext(path)
                path = path + new_extension
                return path
            else:
                return path
        else:
            return destinationfolder

    def watch(self):
        """
        Start a watcher thread for each plugin.
        """
        watchconfigs = []
        for plugin in self.plugins:
            watchconfig = plugin.watch()
            if watchconfig:
                watchconfigs.append(watchconfig)
        return watchconfigs

    def get_installer(self, installerclass):
        """
        Get an instance of the given ``installerclass``.

        Parameters:
            installerclass: A subclass of
                :class:`ievv_opensource.utils.ievvbuildstatic.installers.base.AbstractInstaller`.
        """
        if installerclass.name not in self.installers:
            installer = installerclass(app=self)
            self.installers[installerclass.name] = installer
        return self.installers[installerclass.name]

    def get_logger_name(self):
        return '{}.{}'.format(self.apps.get_logger_name(), self.appname)


class Apps(LogMixin):
    """
    Basically a list around :class:`.App` objects.
    """
    def __init__(self, *apps):
        """
        Parameters:
            apps: :class:`.App` objects to add initially. Uses :meth:`.add_app` to add the apps.
        """
        self.apps = []
        for app in apps:
            self.add_app(app)

    def add_app(self, app):
        """
        Add an :class:`.App`.
        """
        app.apps = self
        self.apps.append(app)

    def install(self):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.install`
        for all plugins within all :class:`apps <.App>`.
        """
        for app in self.apps:
            app.install()

    def run(self):
        """
        Run :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.run`
        for all plugins within all :class:`apps <.App>`.
        """
        for app in self.apps:
            app.run()

    def watch(self):
        """
        Start watcher threads for all folders that at least one
        :class:`plugin <ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin>`
        within any of the :class:`apps <.App>` has configured to be watched for changes.

        Blocks until ``CTRL-c`` is pressed.
        """
        watchconfigpool = WatchConfigPool()
        for app in self.apps:
            watchconfigpool.extend(app.watch())
        all_observers = watchconfigpool.watch()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in all_observers:
                observer.stop()

        for observer in all_observers:
            observer.join()

    def get_logger_name(self):
        return 'ievvbuildstatic'

    def __configure_shlogger(self, loglevel, handler):
        shlogger = logging.getLogger('sh.command')
        shlogger.setLevel(loglevel)
        shlogger.addHandler(handler)
        shlogger.propagate = False

    # def __configure_ievvbuild_logger(self, loglevel, handler):
    #     logger = self.get_logger()
    #     logger.setLevel(loglevel)
    #     logger.addHandler(handler)
    #     logger.propagate = False

    def configure_logging(self, loglevel=logging.INFO,
                          shlibrary_loglevel=logging.WARNING):
        # formatter = logging.Formatter('[%(name)s:%(levelname)s] %(message)s')
        handler = logging.StreamHandler()
        # handler.setFormatter(formatter)
        # handler.setLevel(loglevel)
        # self.__configure_ievvbuild_logger(loglevel=loglevel,
        #                                   handler=handler)
        self.__configure_shlogger(loglevel=shlibrary_loglevel,
                                  handler=handler)
