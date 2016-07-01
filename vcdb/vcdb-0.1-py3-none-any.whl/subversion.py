"""
Utility functions to work with Subversion.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.
import datetime
import io
import logging
import os
import subprocess
import tempfile
from xml.etree import ElementTree

import vcdb.common as common

STRFTIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

_SUBVERSION_KIND_TO_PATH_KIND_MAP = {
    'dir': 'd',
    'file': 'f',
}
_SUBVERSION_ACTION_TO_PATH_ACTION_MAP = {
    'A': 'a',  # added
    'D': 'd',  # deleted
    'M': 'e',  # modified (source and/or properties)
    'R': 'e',  # replaced (using "svn remove" and "svn add" on the same file without any commit in between)
}
_log = logging.getLogger('vcdb.subversion')


def path_from_path_element(change, path_element):
    assert change is not None
    assert path_element is not None

    path = path_element.text
    svn_kind = path_element.attrib['kind']
    try:
        kind = _SUBVERSION_KIND_TO_PATH_KIND_MAP[svn_kind]
    except KeyError:
        assert False, 'kind=%r must be added to _SUBVERSION_KIND_TO_PATH_KIND_MAP' % svn_kind
    svn_action = path_element.attrib['action']
    try:
        action = _SUBVERSION_ACTION_TO_PATH_ACTION_MAP[svn_action]
    except KeyError:
        assert False, 'action=%r must be added to _SUBVERSION_ACTION_TO_PATH_ACTION_MAP' % svn_action

    base_commit_id = path_element.attrib.get('copyfrom-rev')
    base_path = path_element.attrib.get('copyfrom-path')
    if base_commit_id is not None:
        action = 'c'
        base_change_id = common.change_id_for(change.repository_id, base_commit_id)
    else:
        if base_path is not None:
            raise common.VcdbError('on base_commit_id=None, base_path must be None but is: %r' % base_path)
        base_change_id = None
    result = common.Path(
        action=action,
        base_change_id=base_change_id,
        base_path=base_path,
        change_id=change.change_id,
        kind=kind, path=path,
        repository_id=change.repository_id)
    return result


def change_from_logentry_element(session, repository, logentry_element):
        assert logentry_element.tag == 'logentry'
        author = logentry_element.find('author').text
        commit_id = logentry_element.attrib['revision']
        commit_message = logentry_element.find('msg').text
        commit_time_text = logentry_element.find('date').text
        # HACK: Strip the trailing 'Z' which seems to be there for reasons unknown.
        commit_time_text = commit_time_text[:-1]
        commit_time = datetime.datetime.strptime(commit_time_text, STRFTIME_FORMAT)
        change_id = common.change_id_for(repository.repository_id, commit_id)
        result = common.Change(
            author=author,
            change_id=change_id,
            commit_id=commit_id,
            commit_time=commit_time,
            commit_message=commit_message,
            repository_id=repository.repository_id
        )
        return result


def run_svn(command, *options):
    """
    Run a subversion command using the svn command line client.
    """
    command_parts = [
        'svn',
        command,
        '--no-auth-cache',
        '--non-interactive',
        '--quiet',
    ]
    command_parts.extend(list(options))
    _log.debug('  %s', ' '.join(command_parts))
    subprocess.check_call(command_parts)


def write_svn_log_xml(svn_log_xml_path, uri, revision=None):
    command_parts = [
        'svn',
        'log',
        '--no-auth-cache',
        '--non-interactive',
        '--verbose',
        '--xml',
        uri,
    ]
    if revision is not None:
        command_parts.extend([
            '--revision',
            revision
        ])
    _log.info('export subversion log for revision %s', revision)
    _log.debug('  %s', ' '.join(command_parts))
    with open(svn_log_xml_path, 'wb') as target_xml_file:
        xml_data = subprocess.check_output(command_parts)
        target_xml_file.write(xml_data)


def svn_info_elements(uri):
    command_parts = [
        'svn',
        'info',
        '--no-auth-cache',
        '--non-interactive',
        '--xml',
        uri,
    ]
    svn_info_bytes = subprocess.check_output(command_parts)
    with io.BytesIO(svn_info_bytes) as svn_info_io:
        result = ElementTree.parse(svn_info_io)
    return result


def svn_info_revision(repository_uri):
    entry_xpath = 'entry[@revision]'
    svn_info_root = svn_info_elements(repository_uri)
    try:
        entry_element = svn_info_root.findall(entry_xpath)[0]
    except IndexError:
        raise common.VcdbError('XML from "svn info" must contain an element matching XPath %s' % 'entry[@revision]')
    return entry_element.attrib['revision']


def repository_for(session, repository_uri):
    assert session is not None
    assert repository_uri is not None

    existing_repositories = session.query(common.Repository).filter_by(uri=repository_uri).all()
    existing_repository_count = len(existing_repositories)
    if existing_repository_count == 0:
        _log.info('add new repository: %r', repository_uri)
        result = common.Repository(uri=repository_uri)
        session.add(result)
        session.commit()
    else:
        assert existing_repository_count == 1, "Repository.UniqueConstraint('uri') must avoid duplicates"
        result = existing_repositories[0]
    return result


def update_repository(session, repository_uri):
    assert session is not None
    assert repository_uri is not None

    repository = repository_for(session, repository_uri)
    revision = '0:HEAD' # TODO: Update starting revision from last change.
    svn_log_xml_file = tempfile.NamedTemporaryFile(suffix='.xml', prefix='vcdb_svn_log_')
    svn_log_xml_path = svn_log_xml_file.name
    svn_log_xml_file.close()  # Close the temp file, we just need its name.

    # Extract and log parse it.
    write_svn_log_xml(svn_log_xml_path, repository_uri, revision)
    _log.info('read subversion log from %s', svn_log_xml_path)
    log_root = ElementTree.parse(svn_log_xml_path)

    # Process log and add changes and paths.
    for logentry_element in log_root.findall('logentry[@revision]'):
        change = change_from_logentry_element(session, repository, logentry_element)
        _log.debug('  add change: %s', change)
        session.merge(change)
        for path_element in logentry_element.findall('paths/path'):
            path = path_from_path_element(change, path_element)
            _log.debug('    add path: %s', path)
            session.merge(path)
        copied_paths = session.query(common.Path).filter(
            common.Path.change_id == change.change_id,
            common.Path.action == 'c'
        ).all()
        # Change action of copied paths with base_path removed to 'm' (moved).
        for copied_path in copied_paths:
            deleted_path_count = session.query(common.Path).filter(
                common.Path.change_id == change.change_id,
                common.Path.action == 'd',
                common.Path.path == copied_path.base_path
            ).delete()
            if deleted_path_count == 1:
                copied_path.action = 'm'
            else:
                assert deleted_path_count == 0
    session.commit()

