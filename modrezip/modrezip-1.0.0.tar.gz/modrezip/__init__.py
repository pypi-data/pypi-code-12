"""modrezip: call repackage_zip() to make a modified copy of a zipfile."""

from copy import copy
from zipfile import ZipFile


def _repackage_zip_item(src_zip, src_info, dst_zip, callback):
    """Repackage one zipped item into the destination zip."""

    # Copy the ZipInfo, then allow the user callback to modify it
    dst_info = copy(src_info)
    dst_info = callback(src_zip, dst_info)

    # If the callback returns None then the item is skipped. Otherwise
    # write it to the output zipfile.
    if dst_info is not None:
        item_file = src_zip.open(src_info)
        dst_zip.writestr(dst_info, item_file.read())


def repackage_zip(src_file, dst_file, callback):
    """Create a modified copy of a zip file.

    The source zip file is copied into a new zip file. For each item
    in the source zip the |callback| is called to (optionally) modify
    the file's attributes, including its path within the archive.

    src_file: a path or file-like object passed to zipfile.ZipFile in
              read mode

    dst_file: a path or file-like object passed to zipfile.ZipFile in
              write mode

    callback: a callable that takes two arguments, the source ZipFile
              and a ZipInfo object for an item in the ZipFile. The
              callback should return a ZipInfo object, usually by
              returning the one it was called with. The callback can
              freely modify the ZipInfo object it was called with, for
              example to change the items path. The callback can
              return None instead of a ZipInfo object, in which case
              the item will not be written to the destination ZipFile.

    """
    with ZipFile(src_file, 'r') as src_zip:
        with ZipFile(dst_file, 'w') as dst_zip:
            for src_info in src_zip.infolist():
                _repackage_zip_item(src_zip, src_info, dst_zip, callback)
