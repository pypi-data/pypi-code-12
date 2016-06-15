import os


def ensure_path_exists(path):
    path = str(path)

    if not os.path.exists(path):
        os.makedirs(path)
