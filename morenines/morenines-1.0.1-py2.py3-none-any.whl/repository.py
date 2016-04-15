import os

from morenines import output
from morenines import util

from morenines.index import Index
from morenines.ignores import Ignores


NAMES = {
    'mn_dir': '.morenines',
    'index': 'index',
    'ignore': 'ignore',
}

DEFAULT_IGNORE_PATTERNS = [
    NAMES['mn_dir'],
]

class Repository(object):
    # Since click will try to instantiate this class for us with no args, we
    # put the __init__ code here instead
    def init(self, path):
        self.path = path
        self.index = Index(path)
        self.ignore = Ignores(DEFAULT_IGNORE_PATTERNS)

        # Other paths
        self.mn_dir_path = os.path.join(self.path, NAMES['mn_dir'])
        self.index_path = os.path.join(self.mn_dir_path, NAMES['index'])
        self.ignore_path = os.path.join(self.mn_dir_path, NAMES['ignore'])


    def create(self, path):
        repo_path = find_repo(path)

        if repo_path:
            output.error("Repository already exists: {}".format(repo_path))
            util.abort()

        self.init(path)

        os.mkdir(self.mn_dir_path)


    def open(self, path):
        if not os.path.exists(path):
            output.error("Repository path does not exist: {}".format(path))
            util.abort()
        elif not os.path.isdir(path):
            output.error("Repository path is not a directory: {}".format(path))
            util.abort()

        repo_path = find_repo(path)

        if not repo_path:
            output.error("Cannot find repository in '{}' or any parent dir".format(path))
            util.abort()

        self.init(repo_path)

        if os.path.isfile(self.index_path):
            self.index.read(self.index_path)

        if os.path.isfile(self.ignore_path):
            self.ignore.read(self.ignore_path)


def find_repo(start_path):
    if start_path == '/':
        return None

    mn_dir_path = os.path.join(start_path, NAMES['mn_dir'])

    if os.path.isdir(mn_dir_path):
        return start_path

    parent = os.path.split(start_path)[0]

    return find_repo(parent)
