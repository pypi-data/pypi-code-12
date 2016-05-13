

import copy
import logging
import os.path
import pprint
import re
import fnmatch

import wayround_org.utils.list
import wayround_org.utils.tag
import wayround_org.utils.text


# Difficult name examples:
DIFFICULT_NAMES = [
    'GeSHi-1.0.2-beta-1.tar.bz2',
    'Perl-Dist-Strawberry-BuildPerl-5101-2.11_10.tar.gz',
    'bind-9.9.1-P2.tar.gz',
    'boost_1_25_1.tar.bz2',
    'dahdi-linux-complete-2.1.0.3+2.1.0.2.tar.gz',
    'dhcp-4.1.2rc1.tar.gz',
    'dvd+rw-tools-5.5.4.3.4.tar.gz',
    'fontforge_full-20120731-b.tar.bz2',
    'gtk+-3.12.0.tar.xz',
    'lynx2.8.7rel.1.tar.bz2',
    'name.tar.gz',
    'ogre_src_v1-8-1.tar.bz2',
    'openjdk-8-src-b132-03_mar_2014.zip',
    'openssl-0.9.7a.tar.gz',
    'org.apache.felix.ipojo.manipulator-1.8.4-project.tar.gz',
    'pkcs11-helper-1.05.tar.bz2',
    'qca-pkcs11-0.1-20070425.tar.bz2',
    'tcl8.4.19-src.tar.gz',
    'wmirq-0.1-source.tar.gz',
    'xc-1.tar.gz',
    'xf86-input-acecad-1.5.0.tar.bz2',
    'xf86-input-elo2300-1.1.2.tar.bz2',
    'ziplock-1.7.3-source-release.zip',

    # delimiters missing between version numbers :-
    'unzip60.tar.gz',
    'zip30.tar.gz',
    'zip30c.tar.gz'
    ]
"""
Testing tarbal names
"""

ACCEPTABLE_SOURCE_NAME_EXTENSIONS = [
    '.tar.xz',
    '.tar.lzma',
    '.tar.bz2',
    '.tar.gz',
    '.txz',
    '.tlzma',
    '.tbz2',
    '.tbz',
    '.tgz',
    '.7z',
    '.zip',
    '.jar',
    '.tar'
    ]
"""
Acceptable source name extensions
"""

ACCEPTABLE_SOURCE_NAME_EXTENSIONS_REV_SORTED_BY_LENGTH = sorted(
    ACCEPTABLE_SOURCE_NAME_EXTENSIONS,
    key=lambda x: len(x),
    reverse=True
    )

KNOWN_SIGNING_EXTENSIONS = [
    '.sign', '.asc'
]
"""
Trying to list here all extensions by which tarballs can be signed.
This is needed by GetTheSource
"""

ALL_DELIMITERS = ['.', '_', '-', '~']
STATUS_DELIMITERS = ALL_DELIMITERS + ['+']


def _find_possible_chared_versions_and_singles(name_sliced, separator='.'):
    """
    From sliced package name, return all possible versions
    """

    versions = []
    logging.debug(
        "(internal1) versions delimitered by `{}': {}".format(
            separator,
            versions
            )
        )

    version_started = None
    version_ended = None

    index = -1

    for i in name_sliced:
        index += 1

        if i.isdecimal():

            if version_started is None:
                version_started = index

            version_ended = index

        else:

            if version_started is not None:
                if i != separator:
                    versions.append((version_started, version_ended + 1,))
                    version_started = None

    if version_started is not None:
        versions.append((version_started, version_ended + 1,))
        version_started = None

    logging.debug(
        "(internal2) versions delimitered by `{}': {}".format(
            separator,
            versions
            )
        )

    singles = []
    multiples = []

    for i in versions:
        if i[1] - i[0] == 1:
            singles.append(i)
        elif i[1] - i[0] > 1:
            multiples.append(i)
        else:
            raise Exception("Programming error")

    logging.debug(
        "(internal3) versions delimitered by `{}': {}".format(
            separator,
            versions
            )
        )

    return {'singles': singles, 'version': multiples}


def _find_all_versions_and_singles(name_sliced):
    """
    Find all versions using :func:`_find_possible_chared_versions_and_singles`
    function
    """
    ret = dict()
    for i in ALL_DELIMITERS:
        ret[i] = _find_possible_chared_versions_and_singles(name_sliced, i)
        logging.debug("versions delimitered by `{}': {}".format(i, ret[i]))
    return ret


def standard_version_finder(name_sliced, mute=False):
    """
    Find most possible version in sliced package name
    """

    ret = None

    possible_versions_and_singles_grouped_by_delimeter = \
        _find_all_versions_and_singles(name_sliced)

    logging.debug(
        "possible_versions_and_singles_grouped_by_delimeter: {}".format(
            repr(
                possible_versions_and_singles_grouped_by_delimeter
                )
            )
        )

    possible_versions_grouped_by_delimeter = {}
    possible_singles_grouped_by_delimeter = {}

    for i in ALL_DELIMITERS:

        possible_versions_grouped_by_delimeter[i] = \
            possible_versions_and_singles_grouped_by_delimeter[i]['version']

        possible_singles_grouped_by_delimeter[i] = \
            possible_versions_and_singles_grouped_by_delimeter[i]['singles']

    for i in ALL_DELIMITERS:

        if isinstance(ret, (tuple, int)):
            break

        l_possible_versions_grouped_by_delimeter_i = (
            len(possible_versions_grouped_by_delimeter[i])
            )

        if l_possible_versions_grouped_by_delimeter_i == 0:
            pass

        elif l_possible_versions_grouped_by_delimeter_i == 1:
            ret = possible_versions_grouped_by_delimeter[i][0]
            break
        else:

            current_delimiter_group = possible_versions_grouped_by_delimeter[i]

            maximum_length = 0

            for j in current_delimiter_group:
                l = j[1] - j[0]
                if l > maximum_length:
                    maximum_length = l

            if maximum_length == 0:
                s = "Version not found in group `{}'".format(i)
                if not mute:
                    logging.error(s)
                else:
                    logging.debug(s)
            else:

                lists_to_compare = []

                logging.debug(
                    "lists_to_compare: {}".format(repr(lists_to_compare))
                    )

                for j in current_delimiter_group:
                    l = j[1] - j[0]
                    if l == maximum_length:
                        lists_to_compare.append(j)

                l = len(lists_to_compare)
                if l == 0:
                    ret = None
                elif l == 1:
                    ret = lists_to_compare[0]
                else:

                    most_possible_version2 = lists_to_compare[0]

                    for j in lists_to_compare:
                        if j[0] < most_possible_version2[0]:
                            most_possible_version2 = j

                    logging.debug(
                        "most_possible_version2: {}".format(
                            repr(most_possible_version2)
                            )
                        )
                    ret = most_possible_version2
                    break

    if ret is None:
        for i in ALL_DELIMITERS:

            if isinstance(ret, (tuple, int)):
                break

            l_possible_singles_grouped_by_delimeter_i = (
                len(possible_singles_grouped_by_delimeter[i])
                )

            if l_possible_singles_grouped_by_delimeter_i == 0:
                pass

            elif l_possible_singles_grouped_by_delimeter_i == 1:
                ret = possible_singles_grouped_by_delimeter[i][0]
                break
            else:

                most_possible_version3 = \
                    possible_singles_grouped_by_delimeter[i][0]

                for j in possible_singles_grouped_by_delimeter[i]:
                    if j[0] < most_possible_version3[0]:
                        most_possible_version3 = j

                logging.debug(
                    "most_possible_version3: {}".format(
                        repr(most_possible_version3)
                        )
                    )
                ret = most_possible_version3
                break

    logging.debug("most_possible_version: {}".format(repr(ret)))

    return ret


def standard_version_splitter(name_sliced, most_possible_version):

    ret = dict(
        version=None,
        version_list_dirty=None,
        version_list=None,
        version_dirty=None
        )

    ret['version_list_dirty'] = \
        name_sliced[most_possible_version[0]:most_possible_version[1]]

    ret['version_list'] = \
        copy.copy(ret['version_list_dirty'])

    wayround_org.utils.list.remove_all_values(
        ret['version_list'],
        ALL_DELIMITERS
        )

    ret['version'] = '.'.join(ret['version_list'])

    ret['version_dirty'] = ''.join(ret['version_list_dirty'])

    return ret


def infozip_version_finder(name_sliced, mute=False):
    return 1, 2


def infozip_version_splitter(name_sliced, most_possible_version):

    ret = None

    if len(name_sliced) > 1:

        ret = dict(
            version=None,
            version_list_dirty=None,
            version_list=None,
            version_dirty=None
            )

        value = list(name_sliced[1])

        ret['version_list_dirty'] = value

        ret['version_list'] = \
            copy.copy(ret['version_list_dirty'])

        ret['version'] = '.'.join(ret['version_list'])

        ret['version_dirty'] = ''.join(ret['version_list_dirty'])

    return ret


def standard_version_functions_selector(filebn, subject):

    ret = None

    if not subject in ['finder', 'splitter']:
        raise ValueError("invalid `subject' value")

    if re.match(r'(un)?zip\d+', filebn):

        if subject == 'finder':
            ret = infozip_version_finder

        elif subject == 'splitter':
            ret = infozip_version_splitter

    else:

        if subject == 'finder':
            ret = standard_version_finder

        elif subject == 'splitter':
            ret = standard_version_splitter

    return ret


def parse_tarball_name(
        filename,
        mute=False,
        acceptable_source_name_extensions=None,
        version_functions_selector=None
        ):
    """
    Parse source tarball name

    If this function succeeded, dict is returned::

        {
            'name': None,
            'groups': {
                'name'              : None,
                'extension'         : None,

                'version'           : None,
                'version_list_dirty': None,
                'version_list'      : None,
                'version_dirty'     : None,

                'status'            : None,
                'status_list_dirty' : None,
                'status_dirty'      : None,
                'status_list'       : None,
                }
            }

    .. NOTE:: ret['group']['version'] numbers are always joined with point(s)

    see standard_version_finder for reference version finder

    see standard_version_splitter for reference version finder
    """

    if not isinstance(filename, str):
        raise TypeError("filename must be str")

    if acceptable_source_name_extensions is None:
        acceptable_source_name_extensions = ACCEPTABLE_SOURCE_NAME_EXTENSIONS

    if version_functions_selector is None:
        version_functions_selector = standard_version_functions_selector

    filename = os.path.basename(filename)

    logging.debug("Parsing source file name {}".format(filename))

    ret = None

    extension = None
    for i in acceptable_source_name_extensions:
        if filename.endswith(i):
            extension = i

    if extension is None:
        s = "Wrong extension"
        if not mute:
            logging.error(s)
        else:
            logging.debug(s)
        ret = 1
    else:
        without_extension = filename[:-len(extension)]

        # TODO: copy this parser to this module
        name_sliced = wayround_org.utils.text.slice_string_to_sections(
            without_extension
            )

        version_finder = version_functions_selector(filename, 'finder')

        most_possible_version = version_finder(name_sliced, mute)

        if not isinstance(most_possible_version, tuple):
            ret = None
        else:
            ret = {
                'name': None,
                'groups': {
                    'name': None,
                    'extension': None,

                    'version': None,
                    'version_list_dirty': None,
                    'version_list': None,
                    'version_dirty': None,

                    'status': None,
                    'status_list_dirty': None,
                    'status_dirty': None,
                    'status_list': None,
                    }
                }

            ret['name'] = filename

            ret['groups']['name'] = ''.join(
                name_sliced[:most_possible_version[0]]
                ).strip(''.join(ALL_DELIMITERS))

            # version operations

            version_splitter = version_functions_selector(filename, 'splitter')
            version_splitter_res = version_splitter(
                name_sliced,
                most_possible_version
                )

            if version_splitter_res is not None:

                ret['groups'].update(version_splitter_res)

                # status operations

                ret['groups']['status_list_dirty'] = (
                    name_sliced[most_possible_version[1]:]
                    )

                ret['groups']['status_list_dirty'] = (
                    wayround_org.utils.list.list_strip(
                        ret['groups']['status_list_dirty'],
                        STATUS_DELIMITERS
                        )
                    )

                ret['groups']['status_list'] = (
                    copy.copy(ret['groups']['status_list_dirty'])
                    )

                wayround_org.utils.list.remove_all_values(
                    ret['groups']['status_list'],
                    STATUS_DELIMITERS
                    )

                ret['groups']['status_list'] = (
                    wayround_org.utils.list.list_strip(
                        ret['groups']['status_list'],
                        STATUS_DELIMITERS
                        )
                    )

                ret['groups']['status'] = '.'.join(
                    ret['groups']['status_list']
                    )

                ret['groups']['status_dirty'] = \
                    ''.join(ret['groups']['status_list_dirty'])

            # extension

            ret['groups']['extension'] = extension

    if not isinstance(ret, dict):
        if not mute:
            logging.info("No match `{}'".format(filename))

        ret = None

    return ret


# TODO: adopt lists.filter_text_parse()
def filter_text_parse(filter_text):
    """
    Returns list of command structures

    ret = [
        dict(
            action   = '-' or '+',
            subject  = in ['path', 'filename', 'version', 'status'],
            function = <depends on subject> (no spaces allowed),
            data     = <depends on subject> (can contain spaces)
            )
        ]

    """
    ret = []

    lines = filter_text.splitlines()

    for i in lines:
        if i != '' and not i.isspace() and not i.startswith('#'):
            struct = i.split(' ', maxsplit=3)
            if not len(struct) == 4:
                logging.error("Wrong filter line: `{}'".format(i))
            else:
                struct = dict(
                    action=struct[0],
                    subject=struct[1],
                    function=struct[2],
                    data=struct[3]
                    )
                ret.append(struct)

    return ret


# TODO: adopt lists.filter_list()
def filter_tarball_list(input_list, filter_text):
    """
    Filter's supplied list with supplied filter text

    subjects not in check_for_subjects will always be positive (but can be
    filtered out by proper leading rules)
    """

    ret = []

    # TODO: do not use set function here as it is not sorted
    # NOTE: eventually I've had to use set() as it is faster
    inp_list = set(copy.copy(input_list))
    out_list = copy.copy(inp_list)

    filters = filter_text_parse(filter_text)

    for f in filters:

        action = f['action']
        subject = f['subject']
        function = f['function']
        no = False
        data = f['data']

        if not action in ['+', '-']:
            logging.error("Wrong action: `{}'".format(action))
            ret = 10
            break

        if function.startswith('!'):
            no = True
            function = function[1:]

        if not subject in ['filename', 'version', 'status']:
            logging.error("Wrong subject : `{}'".format(subject))
            ret = 1
            break

        if subject in ['filename', 'status']:

            if not function in [
                    'begins', 'contains', 'ends', 'fm', 'bfm', 're']:
                logging.error(
                    "Wrong `{}' function : `{}'".format(subject, function)
                    )
                ret = 3
                break

        elif subject == 'version':

            if not function in [
                    '<', '<=', '==', '>=', '>', 're', 'fm',
                    'begins', 'contains', 'ends'
                    ]:
                logging.error(
                    "Wrong `version' function : `{}'".format(function)
                    )
                ret = 4
                break

        else:
            raise Exception("Programming error")

        if not isinstance(ret, int):

            working_list = None

            if action == '+':
                working_list = copy.copy(inp_list)

            elif action == '-':
                working_list = copy.copy(out_list)
            else:
                raise Exception("Programming Error")

            for item in working_list:

                working_item = item

                if subject == 'filename':
                    working_item = os.path.basename(item)

                elif subject in ['version', 'status']:

                    working_item = None

                    parsed = wayround_org.utils.tarball.\
                        parse_tarball_name(
                            os.path.basename(item),
                            mute=True
                            )

                    if not isinstance(parsed, dict):
                        # TODO: it's not error, but may be it's need to do
                        # something than just a `pass'
                        pass
                    else:
                        if subject == 'version':
                            working_item = parsed['groups']['version']

                        elif subject == 'status':
                            working_item = parsed['groups']['status']

                        else:
                            raise Exception("Programming error")

                else:
                    raise Exception("Programming error")

                matched = False

                if function == 'begins':
                    matched = working_item.startswith(data)

                elif function == 'contains':
                    matched = working_item.find(data) != -1

                elif function == 'end':
                    matched = working_item.endswith(data)

                elif function == 're':
                    matched = re.match(data, working_item) is not None

                elif function == 'fm':
                    logging.debug(
                        "filter_tarball_list: "
                        "fm-matching `{}' and `{}'".format(
                            working_item,
                            data
                            )
                        )
                    matched = fnmatch.fnmatch(working_item, data)

                elif function == 'bfm':
                    logging.debug(
                        "filter_tarball_list: "
                        "base fm-matching `{}' and `{}'".format(
                            working_item,
                            data
                            )
                        )
                    matched = fnmatch.fnmatch(
                        os.path.basename(working_item),
                        data
                        )

                elif function in ['<', '<=', '==', '>=', '>']:
                    matched = (
                        wayround_org.aipsetup.version.lb_comparator(
                            working_item,
                            function + ' ' + data
                            )
                        )
                else:
                    raise Exception("Programming error")

                if no:
                    matched = not matched

                if matched:

                    logging.debug(
                        "filter_tarball_list: "
                        "match: `{}'\n       `{}'".format(item, f)
                        )

                    if action == '+':
                        logging.debug(
                            "filter_tarball_list: adding: {}".format(item)
                            )
                        out_list.add(item)

                    elif action == '-':
                        logging.debug(
                            "filter_tarball_list: removing: {}".format(
                                item
                                )
                            )
                        if item in out_list:
                            out_list.remove(item)

                    else:
                        raise Exception("Programming error")

                else:
                    logging.debug(
                        "filter_tarball_list: NOT "
                        "match: `{}'\n       `{}'".format(item, f)
                        )

    if not isinstance(ret, int):
        ret = out_list

    if isinstance(ret, set):
        ret = list(ret)

    return ret


def remove_invalid_tarball_names(names):
    names = copy.copy(names)

    for i in range(len(names) - 1, -1, -1):
        parse_result = parse_tarball_name(
            names[i]
            )
        if parse_result is None:
            del names[i]
        else:
            try:
                version_list = parse_result['groups']['version_list']
            except KeyError:
                version_list = None

            if (not isinstance(version_list, list)
                    or len(version_list) == 0):
                del names[i]
    return names


def tarball_names_list_subdivide_by_status(tarball_names_list):
    """
    this function usage assumes all supplied tarball names are same
    (versions too).

    result is dict, where keys  are statuses and values are lists of
    tarball names
    """

    # ACCEPTABLE_SOURCE_NAME_EXTENSIONS
    # ACCEPTABLE_SOURCE_NAME_EXTENSIONS_REV_SORTED_BY_LENGTH

    tarball_names_list = copy.copy(tarball_names_list)
    tarball_names_list_c2 = copy.copy(tarball_names_list)

    d = {}

    for i in tarball_names_list:
        parse_result = parse_tarball_name(
            i
            )
        if parse_result is not None:

            s = None

            if (parse_result['groups']['status'] is None
                    or parse_result['groups']['status'] == ''):
                s = None
            else:
                s = parse_result['groups']['status']

            if s not in d:
                d[s] = []

            d[s].append(i)

    ret = d

    return ret


def parse_test():
    """
    Run parser on all difficult names (:data:`DIFFICULT_NAMES`) in test
    purposes
    """

    for i in DIFFICULT_NAMES:
        logging.info("====== Testing parser on `{}' ======".format(i))
        res = parse_tarball_name(i)
        if not isinstance(res, dict):
            logging.error(
                "Error parsing file name `{}' - parser not matched".format(i)
                )
        else:
            pprint.pprint(res)
            print()

    return
