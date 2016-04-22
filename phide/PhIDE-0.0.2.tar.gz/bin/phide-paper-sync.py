#!/usr/bin/env python

import os
import sys
import shutil


IGNORED_DIRS = {'.ipynb_checkpoints', '.git', '.', '..'}
ACCEPTED_EXTS = {'pdf', 'doc', 'docx'}


def _sync(phide_dir, sync_dir, file_name, verbose=True):
    if not os.path.exists(sync_dir):
        os.makedirs(sync_dir)

    phide_path = os.path.join(phide_dir, file_name)
    sync_path = os.path.join(sync_dir, file_name)

    phide_exists = os.path.exists(phide_path)
    sync_exists = os.path.exists(sync_path)

    src, dst = None, None

    if phide_exists and sync_exists:
        phide_t = os.path.getmtime(phide_path)
        sync_t = os.path.getmtime(sync_exists)

        if phide_t > sync_t:
            src, dst = phide_dir, sync_path
        elif phide_t < sync_t:
            src, dst = sync_path, phide_dir
    elif phide_exists and not sync_exists:
        src, dst = phide_dir, sync_path

    if src is not None:
        if verbose: print("{} -> {}", src, dst)
        shutil.copy2(src, dst)


def mirror(phide_dir, sync_dir, sync=False, verbose=True):
    for file_name in os.listdir(phide_dir):
        if file_name == "." or file_name == "..":
            continue

        phide_path = os.path.join(phide_dir, file_name)

        if file_name == '_cited_docs':
            child_syncs, sync_path = True, sync_dir
        else:
            child_syncs, sync_path = False, os.path.join(sync_dir, file_name)

        if os.path.isdir(phide_path):
            if file_name not in IGNORED_DIRS:
                mirror(phide_path, sync_path, child_syncs, verbose)
        elif sync:
            extension = os.path.splitext(file_name)[-1].lower()[1:]
            if extension in ACCEPTED_EXTS:
                _sync(phide_dir, sync_dir, file_name, verbose)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: phide-paper-sync sync-dir")
        sys.exit(1)

    mirror(os.getcwd(), os.path.abspath(sys.argv[0]))
