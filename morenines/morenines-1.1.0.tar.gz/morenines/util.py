import os
import sys
import hashlib
import datetime

def abort():
    """Stop exectution and return nonzero error code"""
    sys.exit(1)


def get_files(root_path, ignores, save_ignored_paths=False):
    paths = []
    ignored = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        ignored_dirs = [d for d in dirnames if ignores.match(d)]

        # Only walk ignored dirs if we're saving all ignored paths
        if save_ignored_paths:
            # Directories end in a slash
            ignored.extend([path + '/' for path in rel_paths_iter(ignored_dirs, dirpath, root_path)])

        # Prune ignored subdirs of current dir in-place
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]

        for path in rel_paths_iter(filenames, dirpath, root_path):
            if ignores.match(path):
                if save_ignored_paths:
                    ignored.append(path)
                continue
            else:
                paths.append(path)

    return paths, ignored


def rel_paths_iter(names, parent_dir_path, root_path):
    for name in names:
        # We want the full path of the file/dir, not its name
        path = os.path.join(parent_dir_path, name)

        # That path must be relative to the root, not absolute
        path = os.path.relpath(path, root_path)

        yield path


def get_hash(path):
    h = hashlib.sha1()

    with open(path, 'rb') as f:
        h.update(f.read())

    return h.hexdigest()


def get_new_and_missing(repo, include_ignored=False):
    current_files, ignored_files = get_files(repo.path, repo.ignore, include_ignored)

    new_files = [path for path in current_files if path not in repo.index.files]

    missing_files = [path for path in repo.index.files.keys() if path not in current_files]

    return new_files, missing_files, ignored_files


TIMESTAMP_FORMAT = "%Y-%m-%d" + "T" + "%H%M%S"

def timestamp_now():
    now = datetime.datetime.utcnow()

    return now.strftime(TIMESTAMP_FORMAT)
