import os

def get_path_of_current_file(current_file):
    """Returns the path of the __file__."""
    return os.path.dirname(os.path.realpath(current_file))

def path_join():
    return os.path.join
