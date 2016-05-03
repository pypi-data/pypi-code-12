
import copy
import fnmatch
import logging
import re
import os.path


def is_lists_of_strings_equal(lst, lst2):
    ret = False

    l = len(lst)
    if l == len(lst2):
        ret = True
        for i in range(l):
            if lst[i] != lst2[i]:
                ret = False
                break

    return ret


def remove_all_values(lst, lst2):
    """
    Removes all values of list lst2 from list lst
    """
    for i in lst2:
        while i in lst:
            lst.remove(i)
    return


def list_lstrip(lst, lst2):
    lst = copy.copy(lst)
    while (len(lst) > 0
           and lst[0] in lst2):
        del lst[0]
    return lst


def list_rstrip(lst, lst2):
    lst = copy.copy(lst)
    while (len(lst) > 0
           and lst[-1] in lst2):
        del lst[-1]
    return lst


def list_strip(lst, lst2):
    return list_lstrip(list_rstrip(copy.copy(lst), lst2), lst2)


def list_lower(lst):
    lst2 = []
    for i in lst:
        lst2.append(i.lower())
    return lst2


def list_upper(lst):
    lst2 = []
    for i in lst:
        lst2.append(i.upper())
    return lst2


def list_sort(lst, cmp=None):

    lst_l = len(lst)

    i = -1
    j = -1
    x = None

    if lst_l > 1:
        while True:
            if i == lst_l - 2:
                break
            i += 1
            j = i
            while True:

                if j == lst_l - 1:
                    break
                j += 1

                if cmp is None:
                    if lst[i] > lst[j]:
                        x = lst[i]
                        lst[i] = lst[j]
                        lst[j] = x
                else:
                    cmp_r = cmp(lst[i], lst[j])
                    if cmp_r == +1:
                        x = lst[i]
                        lst[i] = lst[j]
                        lst[j] = x

    return


def list_remove_empty_lines(lst):
    ret = []
    for i in lst:
        if i != '':
            ret.append(i)
    return ret


def list_remove_duplicated_lines(lst):
    _s = set()
    _l = list()
    for i in lst:
        if not i in _s:
            _s.add(i)
            _l.append(i)
    ret = _l
    return ret


def list_strip_lines(lst):
    ret = []
    for i in lst:
        ret.append(i.strip())
    return ret


def list_strip_filelines(lst):
    ret = []
    for i in lst:
        ret.append(i.strip('\n'))
    return ret


def list_strip_remove_empty_remove_duplicated_lines(lst):
    """
    Do some actions with list of lines

    Do not use this function for file lists,
    use filelist_strip_remove_empty_remove_duplicated_lines
    """
    ret = list_strip_lines(lst)
    ret = list_remove_empty_lines(ret)
    ret = list_remove_duplicated_lines(ret)
    return ret


def filelist_strip_remove_empty_remove_duplicated_lines(lst):
    """
    Does not strips spaces from file names.

    Use this function for file lists,
    not list_strip_remove_empty_remove_duplicated_lines
    """
    ret = list_strip_filelines(lst)
    ret = list_remove_empty_lines(ret)
    ret = list_remove_duplicated_lines(ret)
    return ret


def list_filter_list_white_or_black(
        in_str_list, in_filters_lst, white=True
        ):

    ret = []

    for i in in_str_list:
        i = str(i)

        for j in in_filters_lst:

            if white:
                if re.match(j, i):
                    ret.append(i)
                    break
            else:
                if not re.match(j, i):
                    ret.append(i)
                    break

    return ret


def filter_text_parse(filter_text, show_errors=False):
    """
    Returns list of command structures

    ret = [
        dict(
            action   = '-' or '+',
            function = <depends on subject> (no spaces allowed),
            data     = <depends on subject> (can contain spaces)
            )
        ]

    """
    ret = []

    lines = filter_text.splitlines()

    for i in lines:
        if i != '' and not i.isspace() and not i.startswith('#'):
            struct = i.split(' ', maxsplit=2)
            if not len(struct) == 3:
                if show_errors:
                    logging.error("Wrong filter line: `{}'".format(i))
                ret = None
                break
            else:
                struct = dict(
                    action=struct[0],
                    function=struct[1],
                    data=struct[2]
                    )
                ret.append(struct)

    return ret


def filter_list(input_list, filter_text):
    """
    Filters supplied list with supplied filter

    subjects not in check_for_subjects will always be positive (but can be
    filtered out by proper leading rules)
    """

    ret = []

    inp_list = set(copy.copy(input_list))
    out_list = copy.copy(inp_list)

    filters = filter_text_parse(filter_text)

    for f in filters:

        action = f['action']
        function = f['function']
        no = False
        cs = True
        data = f['data']

        if not action in ['+', '-']:
            logging.error("Wrong action: `{}'".format(action))
            ret = 10
            break

        if function.startswith('!'):
            no = True
            function = function[1:]

        if function.endswith('!'):
            cs = False
            function = function[:-1]

        if not function in [
                'begins', 'contains', 'ends',
                'fm', 'bfm', 're', 'bre'
                ]:
            logging.error(
                "Wrong function : `{}'".format(function)
                )
            ret = 3
            break

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

                if not cs:
                    working_item = working_item.lower()

                matched = False

                if function == 'begins':
                    working_data = data
                    if not cs:
                        working_data = working_data.lower()
                    matched = working_item.startswith(working_data)

                elif function == 'contains':
                    working_data = data
                    if not cs:
                        working_data = working_data.lower()
                    matched = working_item.find(working_data) != -1

                elif function == 'end':
                    working_data = data
                    if not cs:
                        working_data = working_data.lower()
                    matched = working_item.endswith(working_data)

                elif function == 're':
                    working_data = data
                    flags = 0
                    if not cs:
                        flags |= re.IGNORECASE
                    matched = \
                        re.match(working_data, working_item, flags) is not None

                elif function == 'bre':
                    working_data = data
                    flags = 0
                    if not cs:
                        flags |= re.IGNORECASE
                    matched = \
                        re.match(
                            working_data,
                            os.path.basename(working_item),
                            flags) is not None

                elif function == 'fm':
                    working_data = data
                    if not cs:
                        working_data = working_data.lower()
                    matched = fnmatch.fnmatch(working_item, working_data)

                elif function == 'bfm':
                    working_data = data
                    if not cs:
                        working_data = working_data.lower()
                    matched = fnmatch.fnmatch(
                        os.path.basename(working_item),
                        working_data
                        )

                else:
                    raise Exception("Programming error")

                if no:
                    matched = not matched

                if matched:

                    if action == '+':
                        out_list.add(item)

                    elif action == '-':
                        if item in out_list:
                            out_list.remove(item)

                    else:
                        raise Exception("Programming error")

                else:
                    pass

    if not isinstance(ret, int):
        ret = out_list

    if isinstance(ret, set):
        ret = list(ret)

    return ret
