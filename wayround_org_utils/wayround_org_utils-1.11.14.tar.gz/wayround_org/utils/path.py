
import copy
import os.path

import wayround_org.utils.types

S_SEP = os.path.sep
D_SEP = S_SEP * 2

S_SEP_BYTES = bytes(S_SEP, 'ascii')
D_SEP_BYTES = bytes(D_SEP, 'ascii')

# TODO: documentation for all functions
# TODO: make all functions support bytes as well as str


def select_seps(str_in):
    if not isinstance(str_in, (str, bytes)):
        raise ValueError("str_in must be str or bytes")

    ret = S_SEP, D_SEP
    if isinstance(str_in, bytes):
        ret = S_SEP_BYTES, D_SEP_BYTES
    return ret


def select_s_sep(str_in):
    ret = S_SEP
    if isinstance(str_in, bytes):
        ret = S_SEP_BYTES
    return ret


def _remove_double_sep(str_in):

    if not isinstance(str_in, (str, bytes)):
        raise ValueError("str_in must be str or bytes")

    if isinstance(str_in, str):
        while D_SEP in str_in:
            str_in = str_in.replace(D_SEP, S_SEP)

    elif isinstance(str_in, bytes):
        while D_SEP_BYTES in str_in:
            str_in = str_in.replace(D_SEP_BYTES, S_SEP_BYTES)

    return str_in


def _remove_trailing_slash(str_in):

    if not isinstance(str_in, (str, bytes)):
        raise ValueError("str_in must be str or bytes")

    s_sep = select_s_sep(str_in)

    ret = str_in

    ret = ret.rstrip(s_sep)

    # while ret.endswith(s_sep):
    #    ret = ret[:-1]

    # TODO: what is it? commented out 2014-08-30
    # if len(ret) == 0:
    #     ret = s_sep

    return ret


def join(
        *args,
        must_be=str,
        keep_end_empty=False
        ):
    """
    keep_end_empty - if True and *args ends on '' or b'', then result will
    end with trailing slash
    """

    if not must_be in [str, bytes]:
        raise ValueError("`must_be' must be in [str, bytes]")

    s_sep = S_SEP
    if must_be == bytes:
        s_sep = S_SEP_BYTES

    for i in args:
        if not isinstance(i, (str, bytes, list,)):
            raise ValueError("arguments must be str, bytes or lists")

    res, res_t = wayround_org.utils.types.is_all_rec_bytes_str(
        args,
        must_be=must_be
        )
    if not res:
        raise ValueError(
            "arguments must all be of same type: str, bytes or lists of them"
            )

    if len(args) == 0:
        ret = s_sep[0:0]

    else:

        abso = False
        if len(args) != 0 and len(args[0]) != 0:
            abso = args[0][0] == s_sep

        ret_l = []

        for i in args:

            if isinstance(i, list):

                joined = join(
                    *i,
                    must_be=must_be,
                    keep_end_empty=keep_end_empty
                    )

                ret_l += joined.split(s_sep)

            else:

                ret_l += i.split(s_sep)

        if len(ret_l) != 0:

            for i in range(len(ret_l) - 2, -1, -1):

                if ret_l[i] in ['', b'']:
                    del ret_l[i]

        if len(ret_l) != 0:
            if not keep_end_empty:
                if ret_l[-1] in ['', b'']:
                    del ret_l[-1]

        # if len(ret_l) != 0:

            # NOTE: I know what this removes all empty lines from list,
            #       including the last ones, meaning adding slash to string.
            #       This is difference to os.path.join() and is intensional.
            # NOTE: This behavior changes at 2 apr of 2016. see parameters.

            # while '' in ret_l:
            #     ret_l.remove('')

            # while b'' in ret_l:
            #     ret_l.remove(b'')

        ret = s_sep.join(ret_l)

        if abso:
            ret = s_sep + ret

    return ret


def split(path, end_slash='eat'):
    """
    end_slash - 'eat' - removes trailing slash and any it's meaning
                'append' - if path ends on slash - append slash as separate
                        item into result
                'append_to_last_item' - like 'append', but adds slash to list
                        item in result list
                'append_to_last_item_force' - like 'append_to_last_item', but
                        if result list is empty - adds new item into it

    """

    if end_slash not in [
            'eat',
            'append',
            'append_to_last_item',
            'append_to_last_item_force'
            ]:
        raise ValueError("invalid value for `on_ending_slash'")

    if not isinstance(path, (str, bytes)):
        raise ValueError("path must be str or bytes")

    s_sep = select_s_sep(path)

    absp = path.startswith(s_sep)
    htsp = path.endswith(s_sep)

    path = _remove_double_sep(path)
    path = _remove_trailing_slash(path)

    ret = path.split(s_sep)

    while '' in ret:
        ret.remove('')

    while b'' in ret:
        ret.remove(b'')

    if absp:
        ret.insert(0, s_sep)

    if htsp:
        if end_slash == 'eat':
            # do nothing
            pass
        elif end_slash == 'append':
            ret.append(s_sep)
        elif end_slash in ['append_to_last_item', 'append_to_last_item_force']:
            if len(ret) == 0 and end_slash == 'append_to_last_item_force':
                if isinstance(path, str):
                    ret.append('')
                elif isinstance(path, bytes):
                    ret.append(b'')
                else:
                    raise Exception("programming error")
            if len(ret) != 0 and not ret[-1].startswith(s_sep):
                ret[-1] = ret[-1] + s_sep
        else:
            raise Exception("programming error")

    return ret


def normpath(path):
    if not isinstance(path, (str, bytes)):
        raise ValueError("path must be str or bytes")
    return _remove_double_sep(os.path.normpath(path))


def abspath(path):
    if not isinstance(path, (str, bytes)):
        raise ValueError("path must be str or bytes")
    return _remove_double_sep(os.path.abspath(path))


def relpath(path, start):
    if not isinstance(path, (str, bytes)):
        raise ValueError("path must be str or bytes")
    if not isinstance(start, (str, bytes)):
        raise ValueError("start must be str or bytes")
    return _remove_double_sep(os.path.relpath(path, start))


def realpath(path):
    if not isinstance(path, (str, bytes)):
        raise ValueError("path must be str or bytes")
    return _remove_double_sep(os.path.realpath(path))


def abspaths(lst):

    ret = list()

    for i in lst:
        ret.append(abspath(i))

    return ret


def realpaths(lst):

    ret = list()

    for i in lst:
        ret.append(realpath(i))

    return ret


# NOTE: does not work
# def eval_abs_paths(lst, g, l):
#
#    """
#    Ensure(make) listed variables are(be) absolute path
#    """
#
#    for i in lst:
#        if i in l:
#            l[i] = abspath(l[i])
#
#    return


def prepend_path(lst, base):
    """
    Removes any trailing sep from base, and inserts it in the start of every
    lst item. if item not starts with separator, inserts it between base and
    item
    """

    lst = copy.copy(lst)

    while base.endswith(S_SEP):
        base = base[:-1]

    for i in range(len(lst)):
        sep = ''

        if lst[i][0] != S_SEP:
            sep = S_SEP

        lst[i] = base + sep + lst[i]

    return lst


def unprepend_path(lst, base):
    """
    Removes any trailing sep from base, and removes it from the start of every
    lst item.
    """

    if not isinstance(lst, list):
        raise TypeError("lst must be list")

    while base.endswith(S_SEP):
        base = base[:-1]

    for i in lst:
        if not (i + S_SEP).startswith(base + S_SEP):
            raise ValueError(
                "Not all items in lst have base `{}'".format(base)
                )

    lst = copy.copy(lst)

    base_l = len(base)

    for i in range(len(lst)):

        lst[i] = lst[i][base_l:]

    return lst


def insert_base(path, base):
    if not isinstance(path, str):
        raise ValueError("path must be str")
    return prepend_path([path], base)[0]


def remove_base(path, base):
    if not isinstance(path, str):
        raise ValueError("path must be str")
    return unprepend_path([path], base)[0]


def bases(lst):
    """
    Removes dirnames from paths
    """

    if not isinstance(lst, list):
        raise TypeError("lst must be list")

    ret = []

    for i in lst:
        ret.append(os.path.basename(i))

    return ret


def exclude_files_not_in_dirs(files, dirs):

    if not isinstance(files, list):
        raise TypeError("files must be list")

    if not isinstance(dirs, list):
        raise TypeError("dirs must be list")

    ret = []

    for i in files:

        d = os.path.dirname(i)

        if d in dirs:
            ret.append(i)

    return ret


def path_length(string, end_slash='eat'):
    return len(split(string, end_slash=end_slash))


def _is_subpath_range_error(p1, p2):
    error = False
    for i in range(len(p1)):
        # TODO: check this
        if len(p1) < i + 1:
            error = True
            break

        # TODO: check this
        if len(p2) < i + 1:
            error = True
            break

        if p1[i] != p2[i]:
            error = True
            break

    return error


def get_subpath(basepath, fullpath, end_slash='eat'):

    if not isinstance(basepath, str):
        raise ValueError("path must be str")

    if not isinstance(fullpath, str):
        raise ValueError("path_to_check must be str")

    p1 = split(abspath(basepath), end_slash=end_slash)
    p2 = split(abspath(fullpath), end_slash=end_slash)

    ret = None

    error = _is_subpath_range_error(p1, p2)

    if not error:
        ret = join(p2[len(p1):])

    return ret


def is_subpath(path_to_check, path):

    if not isinstance(path, str):
        raise ValueError("path must be str")

    if not isinstance(path_to_check, str):
        raise ValueError("path_to_check must be str")

    p1 = split(abspath(path))
    p2 = split(abspath(path_to_check))

    error = _is_subpath_range_error(p1, p2)

    ret = not error

    return ret


def is_subpath_real(path_to_check, path):

    if not isinstance(path, str):
        raise ValueError("path must be str")

    if not isinstance(path_to_check, str):
        raise ValueError("path_to_check must be str")

    p1 = split(realpath(path))
    p2 = split(realpath(path_to_check))

    error = _is_subpath_range_error(p1, p2)

    ret = not error

    return ret


def select_by_prefered_extension(lst, ext_lst):

    ret = None

    if len(lst) > 0:
        found = None
        for i in ext_lst:
            for j in lst:
                if j.endswith(i):
                    found = j
                    break
            if found is not None:
                break

        if found:
            ret = found
        else:
            ret = lst[0]

    return ret


def file_paths(filename):

    abs_full = abspath(filename)
    abs_dir = os.path.dirname(abs_full)
    abs_dir_real = realpath(abs_dir)
    abs_base = os.path.basename(abs_full)
    abs_dir_real_full = join(abs_dir_real, abs_base)

    real_full = realpath(abs_full)
    real_dir = os.path.dirname(real_full)
    real_base = os.path.basename(real_full)

    ret = {
        'abs_full': abs_full,
        'abs_dir': abs_dir,
        'abs_base': abs_base,

        'abs_dir_real': abs_dir_real,
        'abs_dir_real_full': abs_dir_real_full,

        'real_full': real_full,
        'real_dir': real_dir,
        'real_base': real_base
        }

    return ret
