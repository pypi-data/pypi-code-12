
import rinocloud
import os


def set_local_path(directory, create_dir=False):
    """
        sets path for local saving of information
        if create is true we will create the folder even if it doesnt exist
    """
    if not os.path.exists(directory) and create_dir is True:
        os.makedirs(directory)

    if os.path.isdir(directory):
        rinocloud.path = directory
