from fabric.api import lcd
from fabric.api import settings
import sys
import yaml

from loktar.cmd import exe
from loktar.environment import ROOT_PATH
from loktar.exceptions import CITestFail
from loktar.exceptions import ForbiddenTimelineKey
from loktar.exceptions import SimplePluginErrorConfiguration
from loktar.log import Log


class SimplePlugin(object):
    def __init__(self, package_info, config):
        """Constructor for the SimplePlugin

        Args:
            package_info (dict): represent all informations for the target package in the config.json
            config (dict): this is the configuration plugin. It contains 2 keys 'run' & 'clean'.

        Raise:
            SimplePluginErrorConfiguration: An error occurred when a key is missing in the configuration
        """
        self.plugin_name = sys.modules[self.__class__.__module__].__file__.split('/')[-1].split('.')[0]
        self.logger = Log()
        self.config = config

        self.path = "{0}/{1}/{2}".format(ROOT_PATH["container"],
                                         package_info["pkg_dir"],
                                         package_info["pkg_name"]) \
                    if "pkg_dir" in package_info else \
                    "{0}/{1}".format(ROOT_PATH["container"],
                                     package_info["pkg_name"])

        try:
            self.cmd = self.config["command"]
        except KeyError:
            raise SimplePluginErrorConfiguration()

    def __command(self, cmd):
        """Run the command indicated in the yaml file in the package directory

        Raise:
            CITestFail: An error occurred when the test failed
        """
        with lcd(self.path):
            with settings(warn_only=True):
                if not exe(cmd, remote=False):
                    raise CITestFail("Test failed")

    def _base_run(self):
        self.__command(self.cmd["run"])

    def _base_clean(self):
        self.__command(self.cmd["clean"])


class ComplexPlugin(SimplePlugin):
    def __init__(self, package_info, config):
        """Constructor for the ComplexPlugin, child of SimplePlugin

        Args:
            package_info (dict): represent all informations for the target package in the config.json
            config (dict): this is the configuration plugin. It contains 2 keys 'run' & 'clean'.

        Raise:
            SimplePluginErrorConfiguration: An error occurred when a key is missing in the configuration
        """
        SimplePlugin.__init__(self, package_info, config)
        self.timeline = dict()
        self.share_memory = dict()
        self.__origin = {
            50: self._base_run,
            95: self._base_clean
        }

    def _run(self, timeline):
        """Run the timeline
        Args:
            timeline (dict): represent the user timeline, it will be merged with the origin timeline

        Raise:
            ForbiddenTimelineKey: An error occurred when the plugin try to used a reserved key
        """
        try:
            assert not (set(self.__origin.keys()) & set(timeline))
        except AssertionError:
            raise ForbiddenTimelineKey("Timeline key: 50 & 95 are reserved")

        timeline.update(self.__origin)

        for ref in sorted(timeline):
            timeline[ref]()
