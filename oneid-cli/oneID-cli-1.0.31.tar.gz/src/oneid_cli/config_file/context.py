import os

from . import base_loader as loader


def oneid_config_dir():
    """
    Find the configuration path where the credentials and configuration
    files are stored

    :return: path to user's oneID CLI configuration
    """
    user_directory = os.path.expanduser('~')
    oneid_directory = '.oneid'
    return os.path.join(user_directory, oneid_directory)


def oneid_credentials_file_loader(create=False):
    """
    Get a Loader for the credentials file

    Will look for YAML, JSON and legacy versions of the
    file in that order
    :return: Loader for the found file
    :rtype: Loader
    """
    return loader.find(os.path.join(oneid_config_dir(), 'credentials'), create=create)


def load(project_id=None):
    """
    Context manager for reading the stored configuration file
    """
    return oneid_credentials_file_loader().load(project_id)


def update(project_id=None):
    """
    Context manager for creating or updating the stored configuration file
    """
    return oneid_credentials_file_loader(create=True).update(project_id)
