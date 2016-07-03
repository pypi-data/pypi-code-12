
"""
Version comparison utilities
"""

import logging
import os.path
import functools
import copy
import re

import wayround_org.utils.tarball
import wayround_org.utils.path
import wayround_org.utils.directory


def source_version_comparator_keyed():
    return functools.cmp_to_key(source_version_comparator)


def source_version_comparator(
        name1, name2,
        acceptable_source_name_extensions
        ):

    ret = 0

    if isinstance(acceptable_source_name_extensions, str):
        acceptable_source_name_extensions = \
            acceptable_source_name_extensions.split(' ')

    name1 = os.path.basename(name1)
    name2 = os.path.basename(name2)

    d1 = wayround_org.utils.tarball.parse_tarball_name(
        name1,
        True,
        acceptable_source_name_extensions
        )

    d2 = wayround_org.utils.tarball.parse_tarball_name(
        name2,
        True,
        acceptable_source_name_extensions
        )

    if d1 is None:
        raise Exception("Can't parse filename: {}".format(name1))

    if d2 is None:
        raise Exception("Can't parse filename: {}".format(name2))

    if d1['groups']['name'] != d2['groups']['name']:
        raise ValueError(
            "Files has different names: `{}' ({}) and `{}' ({})".format(
                d1['groups']['name'], name1,
                d2['groups']['name'], name2
                )
            )

    else:
        com_res = standard_comparison(
            d1['groups']['version_list'], d1['groups']['status_list'],
            d2['groups']['version_list'], d2['groups']['status_list']
            )

        if com_res != 0:
            ret = com_res
        else:
            ret = 0

    if ret == -1:
        logging.debug(name1 + ' < ' + name2)
    elif ret == 1:
        logging.debug(name1 + ' > ' + name2)
    else:
        logging.debug(name1 + ' = ' + name2)

    return ret


def standard_comparator(
        version1,
        version2
        ):

    logging.debug("standard_comparator: `{}', `{}'".format(version1, version2))

    int_v1 = version1
    int_v2 = version2

    i1_error = False
    i2_error = False

    if isinstance(version1, str):
        int_v1 = version1.split('.')

    if isinstance(version2, str):
        int_v2 = version2.split('.')

    if not isinstance(int_v1, list):
        i1_error = True
    else:
        for i in int_v1:
            if not isinstance(i, (int, str)):
                i1_error = True

    if not isinstance(int_v2, list):
        i2_error = True
    else:
        for i in int_v2:
            if not isinstance(i, (int, str)):
                i2_error = True

    if i1_error:
        raise ValueError(
            "standart_comparison parameters must be [lists of [str or int]]"
            " or [strings], not {}".format(int_v1)
            )

    if i2_error:
        raise ValueError(
            "standart_comparison parameters must be [lists of [str or int]]"
            " or [strings], not {}".format(int_v2)
            )

    ret = standard_comparison(int_v1, None, int_v2, None)
    logging.debug("standard_comparator ret: `{}'".format(ret))
    return ret


def standard_comparison(
        version_list1, status_list1,
        version_list2, status_list2
        ):

    vers_comp_res = None
    stat_comp_res = None

    vers1 = version_list1
    vers2 = version_list2

    longer = None

    v1l = len(vers1)
    v2l = len(vers2)

    #  length used in first comparison part
    el_1 = v1l

    if v1l == v2l:
        longer = None
        el_1 = v1l

    elif v1l > v2l:
        longer = 'vers1'
        el_1 = v2l

    else:
        longer = 'vers2'
        el_1 = v1l

    # first comparison part

    for i in range(el_1):

        if int(vers1[i]) > int(vers2[i]):
            logging.debug(vers1[i] + ' > ' + vers2[i])
            vers_comp_res = +1
            break
        elif int(vers1[i]) < int(vers2[i]):
            logging.debug(vers1[i] + ' < ' + vers2[i])
            vers_comp_res = -1
            break
        else:
            continue

    # second comparison part
    if vers_comp_res is None:
        if longer is not None:
            if longer == 'vers1':
                logging.debug(str(vers1) + ' > ' + str(vers2))
                vers_comp_res = +1
            else:
                logging.debug(str(vers1) + ' > ' + str(vers2))
                vers_comp_res = -1

    if vers_comp_res is None:
        vers_comp_res = 0

    if vers_comp_res == 0:
        if status_list1 is not None and status_list2 is not None:
            s1 = '.'.join(status_list1)
            s2 = '.'.join(status_list2)
            if s1 > s2:
                stat_comp_res = +1
            elif s1 < s2:
                stat_comp_res = -1
            else:
                stat_comp_res = 0

            vers_comp_res = stat_comp_res

    ret = vers_comp_res

    return ret


def same_base_structurize_by_version(bases):
    """
    return example:
    {
        0: ['b-0.tar', 'b-0.0.tar', 'b-0.0.0.tar'],
        1: 'b-1.tar',
        2: {
            0: 'b-2.0.tar',
            1: 'b-2.1.tar'
            2: {
                0: ['b-2.2.0.tar', 'b-2.2.tar', 'b-2.2.0.tar.xz'],
                1: 'b-2.2.1.tar',
                2: 'b-2.2.2.tar'
                },
            3: 'b-2.3.tar'
        }
    }
    """

    ver_tree = wayround_org.utils.directory.Directory()

    for i in bases:
        ver_tree_add_base(ver_tree, i)

    return ver_tree


def restore_base(directory, value, as_name=0):
    if not as_name in directory:
        directory.mkfile(as_name, value)
    else:
        if directory[as_name].isfile():
            fv = directory[as_name].get_value()
            if isinstance(fv, str):
                directory[as_name].set_value([fv])
                fv = directory[as_name].get_value()
            if isinstance(value, list):
                for i in value:
                    fv.append(i)
            else:
                fv.append(value)
            directory[as_name].set_value(list(set(fv)))
        elif directory[as_name].isdir():
            directory = directory[as_name]
            restore_base(
                directory, value,
                as_name=0  # new subversions treated as zeros
                )
        else:
            raise Exception("programming error")
    return


def ver_tree_add_base(ver_tree, base):
    parse_result = wayround_org.utils.tarball.parse_tarball_name(base)

    version_list = parse_result['groups']['version_list']
    version_list_len = len(version_list)

    path_part = version_list[:-1]
    for i in range(len(path_part) - 1, -1, -1):
        path_part[i] = int(path_part[i])

    file_part = int(version_list[-1])

    directory = ver_tree

    if len(path_part) != 0:
        bases = []
        for i in range(len(path_part)):
            ii = path_part[i]
            if ii in directory:
                if directory[ii].isfile():
                    bases.append(directory[ii].get_value())
                    directory.delete(ii)
                    directory.mkdir(ii)
                directory = directory[ii]
            else:
                directory = directory.mkdir(ii)

        for i in bases:
            restore_base(directory, i, as_name=0)

    restore_base(directory, base, file_part)

    return


def truncate_ver_tree(directory, length):

    lst = directory.listdir()
    lst.sort()

    back_count = length

    for i in range(len(lst) - 1, -1, -1):

        if back_count > 0:
            if (len(directory.get_this_dir_path()) > 1
                    and re.match(r'^9\d+$', str(lst[i]))):
                pass
            else:
                back_count -= 1
        else:
            directory.delete(lst[i])
            del lst[i]

    del lst

    for i in directory.listdir():
        if directory[i].isdir():
            truncate_ver_tree(directory[i], length)

    return


def get_bases_from_ver_tree(directory, preferred_tarball_compressors):
    bases = []
    for path, dirs, files in directory.walk():
        for i in files:
            val = path[-1][i].get_value()
            if not isinstance(val, list):
                val = [val]

            res = wayround_org.utils.tarball.\
                tarball_names_list_subdivide_by_status(
                    val
                )

            for key in res.keys():
                res2 = wayround_org.utils.path.select_by_prefered_extension(
                    res[key],
                    preferred_tarball_compressors
                    )
                bases.append(res2)

            # res = wayround_org.utils.path.select_by_prefered_extension(
            #     val,
            #     preferred_tarball_compressors
            #     )
            # bases.append(res)
            # for j in val:
            #    bases.append(j)
    return bases


def test_same_base_structurize_by_version():

    test_bases = [
        'b-0.tar',
        'b-0.0.tar',
        'b-0.0.0.tar',
        'b-1.tar',
        'b-2.0.tar',
        'b-2.1.tar',
        'b-2.2.0.tar',
        'b-2.2.tar',
        'b-2.2.0.tar.xz',
        'b-2.2.1.tar',
        'b-2.2.2.tar',
        'b-2.3.tar'
        ]

    ver_tree = wayround_org.utils.directory.Directory()

    for i in test_bases:
        ver_tree_add_base(ver_tree, i)

    return ver_tree
