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

    def save(self, source_file, dest_name):
        copyfile(source_file, self.base_path + dest_name)
