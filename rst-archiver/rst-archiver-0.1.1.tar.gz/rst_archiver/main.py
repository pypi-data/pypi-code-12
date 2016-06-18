from __future__ import print_function

import cgi
import os
import shutil
import tempfile
import urllib2

import pyperclip


def get_resource_dir_for_document(document_path):
    resource_path = os.path.join(
        os.path.dirname(document_path),
        'resources',
    )
    if not os.path.isdir(resource_path):
        os.mkdir(resource_path)

    return resource_path


def archive_file(document_path, asset_path):
    resource_dir = get_resource_dir_for_document(document_path)
    shutil.copy(asset_path, resource_dir)

    print("Archived {asset_name} to {resource_path}.".format(
        asset_name=os.path.basename(asset_path),
        resource_path=resource_dir,
    ))

    pyperclip.copy(os.path.join('resources/', os.path.basename(asset_path)))


def archive_url(document_path, asset_url):
    opener = urllib2.urlopen(asset_url)
    info = opener.info()
    _, metadata = cgi.parse_header(info.getheader('Content-Disposition'))
    filename = os.path.basename(metadata.get('filename'))
    if not filename:
        filename = os.path.basename(asset_url)
    data = opener.read()
    temporary_path = os.path.join(tempfile.gettempdir(), filename)

    with open(temporary_path, 'w') as out:
        out.write(data)

    archive_file(document_path, temporary_path)

    os.unlink(temporary_path)
