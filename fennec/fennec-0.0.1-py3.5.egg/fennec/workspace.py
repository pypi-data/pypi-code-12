import logging
import os
from datetime import datetime

from pytz import timezone


class Workspace(object):
    """Workspace manager.

    Args:
        name (str): Workspace name. (it is used for directory naming)
        root (str): Root of results. (default value is "./results"

    Attributes:
        name (str): Workspace name.
        category (str): Workspace category.
    """

    zone = timezone("Asia/Tokyo")
    date_fmt = "%Y%m%d_%H%M%S"

    def __init__(self, name, root="./results"):
        category_, name_ = os.path.split(name)

        self.name = name_ if name_ else "experiment"
        self.category = category_
        self.root = root
        self.created = datetime.now(Workspace.zone)

        self.path = os.path.join(self.root,
                                 self.category,
                                 "{}_{}".format(self.created.strftime(Workspace.date_fmt), self.name))

        self._logger = None

    def log(self, message):
        """Logging"""
        if self._logger is None:
            self._init_logger()

        self._logger.info(message)

    def _init_logger(self):
        logging.basicConfig(filename=self.abspath("result.log"),
                            format="[%(asctime)s %(name)s] %(message)s",
                            datefmt="%Y/%m/%d %I:%M:%S",
                            level=logging.DEBUG)
        self._logger = logging.getLogger(self.name)

    def abspath(self, path):
        """Convert relative path to absolute path based on workspace directory."""
        abspath = os.path.abspath(os.path.join(self.path, path))
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        return abspath

    def __call__(self, path=""):
        return self.abspath(path)
