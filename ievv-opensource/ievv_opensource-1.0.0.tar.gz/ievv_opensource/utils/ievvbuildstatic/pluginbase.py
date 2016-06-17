from future.utils import python_2_unicode_compatible

from ievv_opensource.utils.ievvbuildstatic.watcher import WatchConfig
from ievv_opensource.utils.logmixin import LogMixin


@python_2_unicode_compatible
class Plugin(LogMixin):
    """
    Base class for all plugins in ``ievvbuildstatic``.
    """

    #: The name of the plugin.
    name = None

    def __init__(self):
        self.app = None

    def install(self):
        """
        Install any packages required for this plugin.

        Should use :meth:`ievv_opensource.utils.ievvbuild.config.App.get_installer`.

        Examples:

            Install an npm package::

                def install(self):
                    self.app.get_installer(NpmInstaller).install(
                        'somepackage')
                    self.app.get_installer(NpmInstaller).install(
                        'otherpackage', version='~1.0.0')
        """

    def run(self):
        """
        Run the plugin. Put the code executed by the plugin each time files
        change here.
        """
        pass

    def watch(self):
        """
        Configure watching for this plugin.

        You normally do not override this method, instead you override
        :meth:`.get_watch_folders` and :meth:`.get_watch_regexes`.

        Returns:
            WatchConfig: A :class:`ievv_opensource.utils.ievvbuildstatic.watcher.WatchConfig`
                object if you want to watch for changes in this plugin, or ``None`` if you do not
                want to watch for changes.
        """
        watchfolders = self.get_watch_folders()
        if watchfolders:
            watchregexes = self.get_watch_regexes()
            return WatchConfig(
                watchfolders=watchfolders,
                watchregexes=watchregexes,
                runnable=self)
        else:
            return None

    def get_watch_regexes(self):
        """
        Get the regex used when watching for changes to files.

        Defaults to a regex matching any files.
        """
        return [r'^.*$']

    def get_watch_folders(self):
        """
        Get folders to watch for changes when using ``ievv buildstatic --watch``.

        Defaults to an empty list, which means that no watching thread is started
        for the plugin.

        The folder paths must be absolute, so in most cases you should
        use ``self.app.get_source_path()`` (see
        :meth:`ievv_opensource.utils.ievvbuildstatic.config.App#get_source_path`)
        to turn user provided relative folder names into absolute paths.
        """
        return []

    def get_logger_name(self):
        return '{}.{}'.format(self.app.get_logger_name(), self.name)

    def __str__(self):
        return self.get_logger_name()
