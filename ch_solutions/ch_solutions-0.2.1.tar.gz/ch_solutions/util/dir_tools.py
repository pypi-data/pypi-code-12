import os


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, mode=0o755, exist_ok=True)
