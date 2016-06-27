import os

__author__ = 'hiepsimu'


class chdir(object):
    def __init__(self, path):
        self.path = path
        self.last_dir = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.last_dir)

