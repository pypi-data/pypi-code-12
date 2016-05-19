# -*- coding: utf-8 -*-

import tempfile
import shutil

from os.path import dirname


class tempdir(object):
    """
    Context manager to create and handle temp dir, expose utility methods,
    and cleanup on exit.
    """
    def __init__(self, base_path=None, cleanup=True):
        self.__base_path = base_path
        self.__cleanup = cleanup

    @property
    def base_path(self):
        """
        Base path for temp files

        :return:
        """
        return self.__base_path

    @property
    def path(self):
        return self.__path

    def cleanup(self):
        try:
            shutil.rmtree(self.path)
        except AttributeError:
            pass  # Never `enter`ed, no path to delete

    def __enter__(self):
        self.__path = tempfile.mkdtemp(dir=self.__base_path)
        if self.__base_path is None:
            self.__base_path = dirname(self.__path)
        return self

    def __exit__(self, *_):
        if self.__cleanup:
            self.cleanup()
