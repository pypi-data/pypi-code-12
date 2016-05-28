
import hashlib
import logging
import os
import re

import wayround_org.utils.path
import wayround_org.utils.stream
import wayround_org.utils.terminal


def make_dir_checksums(
        dirname,
        output_filename,
        rel_to=None,
        conv_to_rooted=True,
        exclude=None,
        verbose=True
        ):

    ret = 0

    dirname = wayround_org.utils.path.abspath(dirname)

    if not os.path.isdir(dirname):
        logging.error("Not is dir {}".format(dirname))
        ret = 1

    else:

        try:
            sums_fd = open(output_filename, 'w')
        except:
            logging.exception("Error opening output file")
            ret = 2
        else:
            try:
                ret = make_dir_checksums_fo(
                    dirname,
                    sums_fd,
                    rel_to,
                    conv_to_rooted,
                    exclude,
                    verbose=verbose
                    )
            except:
                logging.exception("Error")
                ret = 2
            finally:
                sums_fd.close()

    return ret


def make_dir_checksums_fo(
        dirname,
        output_fileobj,
        rel_to=None,
        conv_to_rooted=True,
        exclude=None,
        verbose=True
        ):

    if exclude is not None and not isinstance(exclude, list):
        raise ValueError("`exclude' must be list or None")

    if not isinstance(rel_to, str):
        rel_to = dirname

    ret = 0

    dirname = wayround_org.utils.path.abspath(dirname)

    if rel_to is None:
        rel_to = dirname

    rel_to = wayround_org.utils.path.abspath(rel_to)

    if not os.path.isdir(dirname):
        logging.error("Not a dir {}".format(dirname))
        ret = 1

    else:

        if not hasattr(output_fileobj, 'write'):
            logging.error("Wrong output file object")
            ret = 2
        else:

            for wres in os.walk(dirname):

                wres[1].sort()
                wres[2].sort()

                root = wres[0]
                files = wres[2]

                for f in files:
                    root_f = wayround_org.utils.path.join(root, f)

                    if exclude is not None and root_f in exclude:
                        continue

                    rel_path = wayround_org.utils.path.relpath(
                        root_f, rel_to
                        )

                    if verbose:
                        wayround_org.utils.terminal.progress_write(
                            "    {}".format(rel_path)
                            )
                    if (os.path.isfile(root_f)
                        and
                        not os.path.islink(root_f)
                        ):
                        m = hashlib.sha512()
                        fd = None
                        try:
                            fd = open(root_f, 'rb')
                        except:
                            logging.exception(
                                "Can't open file `{}'".format(
                                    root_f
                                    )
                                )
                            ret = 3
                        else:
                            try:
                                while True:

                                    buf = fd.read()
                                    if len(buf) == 0:
                                        break

                                    m.update(buf)

                                wfn = rel_path

                                if (conv_to_rooted
                                        and not wfn.startswith(os.path.sep)):

                                    wfn = os.path.sep + wfn

                                output_fileobj.write(
                                    "{digest} *{pkg_file_name}\n".format_map(
                                        {
                                            'digest': m.hexdigest(),
                                            'pkg_file_name': wfn
                                            }
                                        )
                                    )
                            except:
                                logging.exception("Some error")
                            finally:
                                fd.close()

                        del(m)

    if verbose:
        wayround_org.utils.terminal.progress_write_finish()
    return ret


def is_dir_changed(dirname, checksum_file, method='sha512', verbose=False):

    ret = False

    checksum_file_tmp = checksum_file + '.tmp'

    wayround_org.utils.checksum.make_dir_checksums(
        dirname,
        checksum_file_tmp,
        rel_to='/',
        exclude=[
            checksum_file,
            checksum_file_tmp
            ],
        verbose=verbose
        )

    if not os.path.isfile(checksum_file):
        ret = True

    else:

        summ1 = wayround_org.utils.checksum.make_file_checksum(
            checksum_file
            )
        summ2 = wayround_org.utils.checksum.make_file_checksum(
            checksum_file_tmp
            )

        ret = summ1 != summ2

        os.unlink(checksum_file)

    os.rename(checksum_file_tmp, checksum_file)

    return ret


def make_file_checksum(filename, method='sha512'):
    ret = 0

    if not method.isidentifier() or not hasattr(hashlib, method):
        raise ValueError("hashlib doesn't have `{}'".format(method))

    try:
        f = open(filename, 'rb')
    except:
        logging.exception("Can't open file `{}'".format(filename))
        ret = 1
    else:
        summ = make_fileobj_checksum(f, method)
        if not isinstance(summ, str):
            logging.error("Can't get checksum for file `{}'".format(filename))
            ret = 2
        else:
            ret = summ

        f.close()

    return ret


def make_fileobj_checksum(fileobj, method='sha512'):
    ret = None
    hash_method_name = None

    if not method.isidentifier() or not hasattr(hashlib, method):
        raise ValueError("hashlib doesn't have `{}'".format(method))

    try:
        hash_method_name = getattr(hashlib, method)()
    except:
        logging.exception(
            "Error calling for hashlib method `{}'".format(method)
            )
        ret = 1
    else:
        wayround_org.utils.stream.cat(
            fileobj,
            hash_method_name,
            write_method_name='update',
            standard_write_method_result=False
            )
        ret = hash_method_name.hexdigest()
        del(hash_method_name)
    return ret


def parse_checksums_file_text(filename):
    ret = 0
    try:
        f = open(filename, 'rb')
    except:
        logging.exception("Can't open file `{}'".format(filename))
        ret = 1
    else:
        txt = f.read()
        f.close()
        sums = parse_checksums_text(txt)
        if not isinstance(sums, dict):
            logging.error(
                "Can't get checksums from file `{}'".format(filename)
                )
            ret = 2
        else:
            ret = sums

    return ret


def parse_checksums_text(text):
    ret = 0
    if isinstance(text, bytes):
        text = text.decode('utf-8')

    lines = text.splitlines()
    sums = {}
    for i in lines:
        ist = i.strip(' \n\t\0')
        if ist != '':
            re_res = re.match(r'(.*?) \*(.*)', ist)

            if re_res is None:
                ret = 1
                break
            else:
                sums[re_res.group(2)] = re_res.group(1)

    if ret == 0:
        ret = sums

    return ret


def checksums_by_list(file_lst, method):

    if not method.isidentifier() or not hasattr(hashlib, method):
        raise ValueError("hashlib doesn't have `{}'".format(method))

    ret = {}

    for i in file_lst:
        ret[i] = make_file_checksum(i, method=method)

    return ret


def render_checksum_dict_to_txt(sums_dict, sort=False):

    keys = list(sums_dict.keys())

    if sort:
        keys.sort()

    ret = ''

    for i in keys:
        ret += '{summ} *{path}\n'.format(summ=str(sums_dict[i]), path=str(i))

    return ret


def is_data_error(method, value, data):

    ret = True

    value = value.lower()

    if not method.isidentifier() or not hasattr(hashlib, method):
        raise ValueError("hashlib doesn't have `{}'".format(method))

    hash_method_name = eval("hashlib.{}()".format(method))

    hash_method_name.update(data)

    hd = hash_method_name.hexdigest().lower()

    return hd == value
