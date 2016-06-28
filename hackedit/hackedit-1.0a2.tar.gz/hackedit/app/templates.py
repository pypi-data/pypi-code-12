"""
This module contains the top level API for managing the project/file templates.
"""
import json
import logging
import os
import re

from binaryornot.check import is_binary

from hackedit.app import settings


def create(template, dest_dir, answers):
    """
    Creates a file/project from the specified template, at the specified directory.

    :param template: Template data.
    :param dest_dir: Destination directory where to create the file/project
    :param answers: Dict of answers for substitution variables
    """
    def get_paths(root, path, src_dir, dest_dir):
        src_path = os.path.join(root, path)
        rel_path = os.path.relpath(src_path, src_dir)
        dst_path = os.path.join(dest_dir, rel_path)
        return src_path, dst_path

    def get_file_encoding(path):
        if is_binary(path):
            return 'binary'
        try:
            encodings = template['encodings']
        except KeyError:
            encodings = ['utf-8', 'cp1252']

        for encoding in encodings:
            try:
                with open(path, encoding=encoding) as f:
                    f.read()
            except UnicodeDecodeError:
                continue
            else:
                return encoding

    def open_file(path, encoding, to_write=None):
        if encoding == 'binary':
            if to_write is None:
                mode = 'rb'
            else:
                mode = 'wb'
            encoding = None
        else:
            if to_write is None:
                mode = 'r'
            else:
                mode = 'w'
        content = None
        with open(path, mode, encoding=encoding) as f:
            if to_write is not None:
                f.write(to_write)
            else:
                content = f.read()
        return content

    def subsitute_vars(string):
        for var, value in answers.items():
            string = re.sub('@%s@' % var, value, string)
        return string

    ret_val = []

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    src_dir = template['path']
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file == 'template.json' or file.endswith('.pyc'):
                continue
            src, dst = get_paths(root, file, src_dir, dest_dir)
            dst = subsitute_vars(dst)
            encoding = get_file_encoding(src)
            try:
                content = open_file(src, encoding)
            except OSError:
                _logger().exception('failed to open file: %r', src)
            if encoding != 'binary':
                content = subsitute_vars(content)
            if file == 'btpad_btn_img_0.png':
                print(len(content), encoding)
            try:
                open_file(dst, encoding, to_write=content)
            except PermissionError:
                _logger().exception('failed to write file: %r', dst)
            else:
                ret_val.append(dst)

            assert open_file(dst, encoding) == content

        for directory in dirs:
            src, dst = get_paths(root, directory, src_dir, dest_dir)
            dst = subsitute_vars(dst)
            try:
                os.mkdir(dst)
            except PermissionError:
                _logger().exception('failed to create directory: %r', dst)
    return ret_val


def get_sources():
    """
    Returns the template sources (directory associated with a label).
    """
    s = settings.load()
    tmpl_sources = s.value('_templates/sources', '[]')
    tmpl_sources = json.loads(tmpl_sources)
    return sorted(tmpl_sources, key=lambda x: x['label'])


def add_source(label, path):
    """
    Adds a template source

    :param label: Name of the template source.
    :param path: Path of the template source.
    """
    tmpl_sources = get_sources()
    tmpl_sources.append({'label': label, 'path': path})
    s = settings.load()
    s.setValue('_templates/sources', json.dumps(tmpl_sources))


def rm_source(label):
    """
    Removes the specified template source.

    :param label: Name of the template source to remove.
    """
    tmpl_sources = get_sources()
    for src in tmpl_sources:
        if src['label'] == label:
            tmpl_sources.remove(src)
    s = settings.load()
    s.setValue('_templates/sources', json.dumps(tmpl_sources))


def clear_sources():
    """
    Clear template sources.
    """
    s = settings.load()
    s.setValue('_templates/sources', json.dumps([]))


def get_templates(category='', source_filter=''):
    """
    Gets the list of templates.

    :param category: Template category to retrieve.
        - use "Project" to get project templates
        - use "File" to get file templates
        - use an empty string to retrieve them all (default).

    :param source: Label of the source of the templates to retrieve. Use an empty string to retrieve
        templates from all sources.
    """
    def filtered_sources():
        """
        Filter list of sources based on the ``source`` parameter.
        """
        tmpl_sources = get_sources()
        filtered = []
        if source_filter:
            # only keep the requested template source
            for src in tmpl_sources:
                if src['label'] == source_filter:
                    filtered.append(src)
                    break
        else:
            filtered = tmpl_sources
        return filtered

    def get_template(tdir):
        """
        Returns template data for the given template directory.

        Returns None if the template is invalid.

        :param tdir: Template directory to get data from.
        """
        tmpl = None
        template_json = os.path.join(tdir, 'template.json')
        if not os.path.exists(template_json):
            # no template.json -> invalid template
            _logger().warn('"template.json" not found in template directory: %r', tdir)
        else:
            try:
                with open(template_json) as f:
                    tmpl = json.loads(f.read())
            except (OSError, json.JSONDecodeError):
                # unreadable template.json -> invalid template
                _logger().exception('failed to read %r', template_json)
                tmpl = None
            else:
                try:
                    tmpl_cat = tmpl['category']
                except KeyError:
                    # no metadata or no category in template.json -> invalid template
                    _logger().exception('failed to read category from template metadata, '
                                        'incomplete template.json?')
                    tmpl = None
                else:
                    # valid template (finally).
                    tmpl['source'] = src
                    if category and category != tmpl_cat:
                        _logger().debug('rejecting template directory: %r, invalid category', tdir)
                        tmpl = None
        return tmpl

    def listdir(directory):
        """
        Securely list subdirectories of ``directory``.

        Returns an empty list of an OSError occurred.
        """
        try:
            return os.listdir(directory)
        except OSError:
            return []

    for src in filtered_sources():
        for tdir in listdir(src['path']):
            tdir = os.path.join(src['path'], tdir)
            if os.path.isfile(tdir):
                continue
            tmpl = get_template(tdir)
            if tmpl:
                tmpl['path'] = tdir
                yield tmpl


def get_template(source, template):
    """
    Returns the specified template data.
    """
    for t in get_templates(source_filter=source):
        if t['name'] == template:
            return t
    return None


def _logger():
    return logging.getLogger(__name__)


if __name__ == '__main__':
    clear_sources()
    add_source('COBOL',  '/home/colin/Documents/hackedit-cobol/hackedit_cobol/templates')
    add_source('Python', '/home/colin/Documents/hackedit-python/hackedit_python/templates')
    for tmpl in get_templates():
        print(json.dumps(tmpl, indent=4, sort_keys=True))
