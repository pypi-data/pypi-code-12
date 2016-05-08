"""
Utility functions for dealing with files
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import magic


def is_text_file(filepath):
    """
    Check if a file is a text file using libmagic.

    Args:
        filepath: A string. The path to the file being inspected.

    Returns:
        True if the file is a text file.
    """
    f = magic.from_file(filepath)
    return "text" in f
