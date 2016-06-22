# -*- coding: utf-8 -*-

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Methods
from statsbiblioteket.github_cloner.github_cloner \
    import \
    githubBackup, \
    fetchOrClone, \
    get_github_repositories, \
    parse_github_repositories, \
    create_parser #This import is important for the sphinx-argparse docs


# Types
from statsbiblioteket.github_cloner.github_cloner import \
    RepoType, \
    UserType, \
    Repository, \
    Url, \
    Path

__author__ = 'Asger Askov Blekinge'
__email__ = 'asger.askov.blekinge@gmail.com'
__version__ = '0.2.0'