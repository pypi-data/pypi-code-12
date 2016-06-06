import os
from shutil import copyfile

from simplefsabstraction.interface import SimpleFS


class LocalFS(SimpleFS):
    """
    The local file system
    """

    def __init__(self, base_path=''):
        """
        :param base_path: a path prefix that will be appended to the file names
        """
        self.base_path = base_path

    def exists(self, file_name):
        return os.path.isfile(self.base_path + file_name)

    def _save(self, source_file, filename):
        return copyfile(source_file, filename)

    def save(self, source_file, dest_name, randomize=False, extensions=None):
        if extensions and not self._check_extension(dest_name, extensions):
            raise SimpleFS.BadExtensionError()
        filename = self.base_path + (self._random_filename() if randomize else dest_name)
        self._save(source_file, filename)
        return filename
