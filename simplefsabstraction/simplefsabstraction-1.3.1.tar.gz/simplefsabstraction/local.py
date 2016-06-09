import os
from shutil import copyfile

import shutil

from simplefsabstraction.interface import SimpleFS


class LocalFS(SimpleFS):
    """
    The local file system
    """

    def __init__(self, allowed_extensions=None, base_path=''):
        """
        :param base_path: a path prefix that will be appended to the file names
        """
        self.base_path = base_path
        self.allowed_extensions = allowed_extensions

    def exists(self, file_name):
        return os.path.isfile(self.base_path + file_name)

    def _save(self, source_file, filename):
        """
        Save the file
        :param source_file:
        :param filename:
        :return:
        """
        # If the source file is a filename
        if type(source_file) is str:
            copyfile(source_file, filename)
        # If the file is a "real" file, we copy it another way
        else:
            source_file.seek(0)
            with open(filename, "wb") as dest:
                shutil.copyfileobj(source_file, dest)

    def save(self, source_file, dest_name, randomize=False):
        if self.allowed_extensions and not self._check_extension(dest_name, self.allowed_extensions):
            raise SimpleFS.BadExtensionError()
        filename = self.base_path + (self._random_filename() if randomize else dest_name)
        self._save(source_file, filename)
        return filename
