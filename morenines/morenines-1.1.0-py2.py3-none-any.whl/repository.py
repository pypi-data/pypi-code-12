import os
import errno

from morenines.index import Index
from morenines.ignores import Ignores

from morenines.exceptions import PathError, RepositoryError, NoEffectWarning


NAMES = {
    'mn_dir': '.morenines',
    'index': 'index',
    'ignore': 'ignore',
    'new_index': 'new_index',
    'index_archive_dir': 'indexes',
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
        self.new_index_path = os.path.join(self.mn_dir_path, NAMES['new_index'])
        self.index_archive_dir = os.path.join(self.mn_dir_path, NAMES['index_archive_dir'])


    def create(self, path):
        repo_path = find_repo(path)

        if repo_path:
            raise PathError("Repository already exists at path: {}".format(repo_path), repo_path)

        self.init(path)

        os.mkdir(self.mn_dir_path)

        # Write an empty index file as a starter
        with open(self.index_path, 'w') as stream:
            self.index.write(stream)


    def open(self, path):
        if os.path.exists(path) == False or os.path.isdir(path) == False:
            raise PathError("Invalid repository path: {}".format(path), path)

        repo_path = find_repo(path)

        if not repo_path:
            raise PathError("Not a morenines repository (or any of its parent dirs): {}".format(path), path)

        self.init(repo_path)

        if os.path.isfile(self.index_path):
            self.index.read(self.index_path)

        if os.path.isfile(self.ignore_path):
            self.ignore.read(self.ignore_path)


    def normalize_paths(self, paths):
        """Make paths relative to the repo root.

        If a path is not a descendant of the repo root, raise an exception.
        """
        rel_paths = []

        for path in paths:
            # Remove any relative path weirdness
            path = os.path.abspath(path)

            if not path.startswith(self.path):
                raise PathError("Path not in repository: {}".format(path), path)

            rel_paths.append(os.path.relpath(path, self.path))

        return rel_paths


    def _walk_tree(self, root):
        """Walk the directory tree starting with root, returning all non-ignored paths below.

        Internal method; input is not validated. Call self.normalize_paths() on
        `root` param first.
        """
        paths = []

        root = os.path.abspath(root)

        for dir_path, dir_names, file_names in os.walk(root):
            ignored_dirs = [d for d in dir_names if self.ignore.match(d)]
            ignored_files = [f for f in file_names if self.ignore.match(f)]

            # Assign dir_names in place with [:] so that os.walk doesn't traverse ignored dirs
            dir_names[:] = [d for d in dir_names if d not in ignored_dirs]

            file_names = [f for f in file_names if f not in ignored_files]
            file_paths = [os.path.join(dir_path, f) for f in file_names]
            file_paths = self.normalize_paths(file_paths)

            paths.extend(file_paths)

        return paths


    def add(self, paths):
        """Append untracked files to the index with their hashes and write it.

        Returns the list of paths that were added to the repository.
        """

        # We need to differentiate paths that are definitely files
        file_paths = []

        # Make paths relative to repo root
        paths = self.normalize_paths(paths)

        for path in paths:
            # if existing path is a dir, walk its subdirs to collect paths in dir
            if os.path.isdir(path):
                subpaths = self._walk_tree(path)
                if subpaths:
                    file_paths.extend(subpaths)
                else:
                    # We should log the fact that the param the user supplied
                    # did nothing, but NoEffectWarning is an Exception and
                    # would break control flow
                    pass
            elif not os.path.exists:
                raise PathError("Path does not exist: {}".format(path), path)
            else:
                file_paths.append(path)

        # If dirs were the only supplied paths, and walking them produced no valid files
        # TODO this could really benefit from a --verbose option, to see what is ignored
        if not file_paths:
            raise NoEffectWarning("No files in the supplied directory path(s) were able to be added. (Are they ignored?)")

        # add paths to index
        self.index.add(file_paths)

        return file_paths


    def remove(self, paths):
        """Remove paths and hashes from the index and write it.

        Returns the list of paths that were removed from the repository.
        """

        # We need to differentiate paths that are definitely files in the index
        file_paths = []

        # make paths relative to repo root
        paths = self.normalize_paths(paths)

        for path in paths:
            if path in self.index.files:
                file_paths.append(path)
            else:
                subpaths = [p for p in self.index.files.keys() if p.startswith(path)]

                if subpaths:
                    file_paths.extend(subpaths)
                else:
                    raise PathError("Path does not exist in repository: {}".format(path), path)

        # If dirs were the only supplied paths, and walking them produced no valid files
        # TODO this could really benefit from a --verbose option, to see what is ignored
        if not file_paths:
            raise NoEffectWarning("No files in the supplied directory path(s) were able to be added. (Are they ignored?)")

        # remove paths from index
        self.index.remove(file_paths)

        return file_paths

    def write_index(self):
        """Rename the old index file and write the new one
        """
        self.check_index_sanity()

        # Figure out what we're going to rename the current index file to
        # We need to put this in the 'parent' header of the new index, so we
        # figure this out before we do anything
        archived_parent_name = self.get_archived_parent_name()

        self.index.parent = archived_parent_name

        # Write the new index
        with open(self.new_index_path, 'w') as new_index_stream:
            self.index.write(new_index_stream)

        self.archive_current_index(archived_parent_name)

        # Rename the new index file to be the current index
        try:
            os.rename(self.new_index_path, self.index_path)
        except OSError as e:
            # TODO (py3 only): chain the errors
            raise RepositoryError("Could not move the new index file into place")


    def check_index_sanity(self):
        """Try to ensure that the current repository state is expected and sensible.
        """

        if not os.path.isfile(self.index_path) and os.path.isfile(self.new_index_path):
            message = "No current index file exists: {}\n".format(self.index_path)
            message += "A new temporary index file exists, however: {}\n".format(self.new_index_path)
            message += "To fix this problem, rename the newest valid index file (possibly the one listed above) to {}\n".format(self.index_path)
            message += "(You may have to reattempt the last add or remove command)"

            raise RepositoryError(error_message)

        if os.path.isfile(self.new_index_path):
            message = "A new temporary index file already exists: {}\n".format(self.new_index_path)

            message += "To fix this problem, move this temporary index file out of its directory\n"
            message += "(You may have to reattempt the last add or remove command)"

            raise RepositoryError(message)


    def archive_current_index(self, archived_name):
        # Get the path we're renaming the current index to
        archived_path = os.path.join(self.index_archive_dir, archived_name)

        # Create the index archive dir if possible - EAFP
        try:
            os.mkdir(self.index_archive_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                # NOT AN ERROR: The archive dir will almost always exist
                pass
            else:
                raise

        # Archive the current index by renaming it into the archive dir
        try:
            os.rename(self.index_path, archived_path)
        except OSError as e:
            # TODO (py3 only): chain the errors
            raise RepositoryError("Could not archive the current index file")


    def get_archived_parent_name(self):
        old_index = Index(self.path)

        old_index.read(self.index_path)

        return "{}-{}".format(NAMES['index'], old_index.date)


def find_repo(start_path):
    if start_path == '/':
        return None

    mn_dir_path = os.path.join(start_path, NAMES['mn_dir'])

    if os.path.isdir(mn_dir_path):
        return start_path

    parent = os.path.split(start_path)[0]

    return find_repo(parent)
