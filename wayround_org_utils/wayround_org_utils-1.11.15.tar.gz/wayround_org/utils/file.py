
import fnmatch
import logging
import os
import select
import shutil
import threading
import time
import copy

import wayround_org.utils.path
import wayround_org.utils.terminal
import wayround_org.utils.text


POLL_CONSTS = {}

_l = dir(select)
for _i in [
        'POLLIN',
        'POLLPRI',
        'POLLOUT',
        'POLLERR',
        'POLLHUP',
        'POLLNVAL'
        ]:
    POLL_CONSTS[_i] = eval('select.{}'.format(_i))

del _i
del _l


def copy_file(src, dst, overwrite_dst=False, verbose=True):

    ret = 0

    if os.path.isfile(dst) and not overwrite_dst:
        if verbose:
            logging.info("Skipping overwriting file `{}'".format(dst))
    else:

        if verbose:
            logging.info("copying `{}'".format(os.path.relpath(src)))

        try:
            shutil.copy2(src, dst)
        except:
            if verbose:
                logging.error(
                    "Can't overwrite file `{}'".format(dst)
                    )
            ret = 1

    return ret


def copy_symlink(src, dst, overwrite_dst=False, verbose=True):

    ret = 0

    link_value = os.readlink(src)

    if ((os.path.isfile(dst)
         or os.path.islink(dst))
            and overwrite_dst):

        os.unlink(dst)

    elif os.path.isdir(dst):
        if verbose:
            logging.error(
                "Can't create link. It's a directory `{}'".format(dst))
        ret = 1

    try:
        os.symlink(link_value, dst)
    except:
        if verbose:
            logging.error(
                "Can't create link. File exists `{}'".format(dst)
                )
        ret = 2

    return ret


def _copytree_sub(
        src_dir,
        dst_dir,
        overwrite_files=False,
        stop_on_overwrite_error=True,
        verbose=True
        ):

    # TODO: make verbose parameter

    ret = 0

    full_src_dir = wayround_org.utils.path.abspath(src_dir)
    full_dst_dir = wayround_org.utils.path.abspath(dst_dir)

    if not os.path.isdir(full_src_dir):
        if verbose:
            logging.error("Source dir not exists `{}'".format(src_dir))
        ret = 1
    else:
        if create_if_not_exists_dir(full_dst_dir) != 0:
            if verbose:
                logging.error(
                    "Error creating destination dir `{}'".format(full_dst_dir)
                    )
            ret = 2
        else:

            for path, dirs, files in os.walk(
                    src_dir,
                    topdown=True,
                    onerror=_copytree_on_error,
                    followlinks=False
                    ):

                path_dst = wayround_org.utils.path.join(
                    full_dst_dir,
                    wayround_org.utils.path.relpath(
                        path,
                        full_src_dir
                        )
                    )

                dirs.sort()
                files.sort()

                for i in dirs:

                    joined = wayround_org.utils.path.join(path, i)
                    joined_dst = wayround_org.utils.path.join(path_dst, i)

                    if os.path.islink(joined):

                        if copy_symlink(
                                joined,
                                joined_dst,
                                overwrite_files,
                                verbose=verbose
                                ) != 0:
                            ret = 3
                            # TODO: break?

                    else:
                        if create_if_not_exists_dir(joined_dst) != 0:
                            if verbose:
                                logging.error(
                                    "Can't create directory `{}'".format(
                                        joined_dst
                                        )
                                    )
                            ret = 5
                            # TODO: break?

                # TODO: if ret == 0?
                for i in files:

                    joined = wayround_org.utils.path.join(path, i)
                    joined_dst = wayround_org.utils.path.join(path_dst, i)

                    if os.path.islink(joined):

                        if copy_symlink(
                                joined,
                                joined_dst,
                                overwrite_files,
                                verbose=verbose
                                ) != 0:
                            ret = 3
                            break

                    elif os.path.isfile(joined):

                        if copy_file(
                                joined,
                                joined_dst,
                                overwrite_files,
                                verbose=verbose
                                ) != 0:
                            ret = 4
                            break

                if ret != 0:
                    break

    return ret


def _copytree_on_error(err):
    try:
        raise err
    except:
        logging.exception("Can't copy file:\n{}".format(err))
    return


def copytree(
        src_dir,
        dst_dir,
        overwrite_files=False,
        clear_before_copy=False,
        dst_must_be_empty=True,
        verbose=True
        ):

    # TODO: think of hardlinks too..

    src_dir = wayround_org.utils.path.abspath(src_dir)
    dst_dir = wayround_org.utils.path.abspath(dst_dir)

    ret = 0

    if verbose:
        logging.info("copying `{}'\n    to\n    `{}'".format(src_dir, dst_dir))

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)

    if dst_must_be_empty:
        if not isdirempty(dst_dir):
            if verbose:
                logging.error("Destination dir `{}' not empty".format(dst_dir))
            ret = 1

    if ret == 0:

        if clear_before_copy:
            if verbose:
                logging.info("Cleaning dir `{}'".format(dst_dir))
            cleanup_dir(dst_dir, verbose=verbose)

        if create_if_not_exists_dir(dst_dir, verbose=verbose) != 0:
            if verbose:
                logging.error("Error creating dir `{}'".format(dst_dir))
            ret = 2
        else:
            if (_copytree_sub(
                    src_dir,
                    dst_dir,
                    overwrite_files=overwrite_files,
                    verbose=verbose
                    )
                    != 0):
                if verbose:
                    logging.error(
                        "Some errors occurred"
                        " while copying `{}' to `{}'".format(
                            src_dir,
                            dst_dir
                            )
                        )
                ret = 3

    return ret


def copy_file_or_directory(
        src_path,
        dst_dir,
        overwrite_files=False,
        clear_before_copy=False,
        dst_must_be_empty=True,
        verbose=True
        ):

    ret = 0

    if os.path.islink(src_path):
        ret = copy_symlink(
            src_path,
            dst_dir,
            # wayround_org.utils.path.join(dst_dir, os.path.basename(src_path)),
            overwrite_dst=overwrite_files,
            verbose=verbose
            )
    elif os.path.isfile(src_path):
        ret = copy_file(
            src_path,
            dst_dir,
            # wayround_org.utils.path.join(dst_dir, os.path.basename(src_path)),
            overwrite_dst=overwrite_files,
            verbose=verbose
            )
    else:
        if os.path.isdir(src_path):
            ret = copytree(
                src_path,
                dst_dir,
                overwrite_files=overwrite_files,
                clear_before_copy=clear_before_copy,
                dst_must_be_empty=dst_must_be_empty,
                verbose=verbose
                )

        else:
            if verbose:
                logging.error(
                    "Don't know what to do with: {}".format(src_path))
            ret = 1

    return ret


def isdirempty(dirname):
    return len(os.listdir(dirname)) == 0

is_dir_empty = isdirempty


def remove_if_exists(file_or_dir, remove_dead_lymlinks=False, verbose=True):

    ret = 0

    file_or_dir = wayround_org.utils.path.abspath(file_or_dir)

    if os.path.islink(file_or_dir):
        try:
            os.unlink(file_or_dir)
        except:
            if verbose:
                logging.exception(
                    "      can't remove link {}".format(file_or_dir)
                    )
            ret = 1

    if ret == 0 and os.path.exists(file_or_dir):

        if not os.path.islink(file_or_dir):

            if os.path.isdir(file_or_dir):
                try:
                    shutil.rmtree(file_or_dir)
                except:
                    if verbose:
                        logging.exception(
                            "Can't remove dir {}".format(file_or_dir)
                            )
                    ret = 1
            else:
                try:
                    os.unlink(file_or_dir)
                except:
                    if verbose:
                        logging.exception(
                            "      can't remove file {}".format(file_or_dir)
                            )
                    ret = 1

    return 0


def create_if_not_exists_dir(dirname, verbose=True):
    ret = 0
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            if verbose:
                logging.error(
                    "Destination dir not exists and cant's be created")
            ret = 1
        else:
            ret = 0
    else:
        if os.path.isfile(dirname):
            if verbose:
                logging.error("Destination exists but is file")
            ret = 2
        elif os.path.islink(dirname):
            if verbose:
                logging.error("Destination exists but is link")
            ret = 3
        elif not os.path.isdir(dirname):
            if verbose:
                logging.error("Destination exists but is not dir")
            ret = 4
        else:
            ret = 0
    return ret


def cleanup_dir(dirname, verbose=True):

    ret = 0

    files = os.listdir(dirname)

    for i in range(len(files)):
        files[i] = wayround_org.utils.path.abspath(
            wayround_org.utils.path.join(dirname, files[i])
            )

    for i in files:
        if remove_if_exists(i, verbose=verbose) != 0:
            ret = 1

    return ret


def inderictory_copy_file(directory, file1, file2, verbose=True):

    file1 = os.path.basename(file1)
    file2 = os.path.basename(file2)

    f1 = os.path.join(directory, file1)
    f2 = os.path.join(directory, file2)

    if os.path.isfile(f1):
        if os.path.exists(f2):
            if verbose:
                logging.error("destination file or dir already exists")
        else:
            logging.info("copying {} to {}".format(f1, f2))
            try:
                shutil.copy(f1, f2)
            except:
                if verbose:
                    logging.exception("Error copying file")
    else:
        if verbose:
            logging.error("source file not exists")

    return


def files_recurcive_list(
        dirname,
        onerror=None,
        followlinks=False,
        exclude_paths=None,
        relative_to=None,
        mute=True,
        sort=False,
        acceptable_endings=None,
        print_found=False,
        list_symlincs=True,
        maxdepth=None,
        include_dirs=False
        ):

    s_sep = wayround_org.utils.path.select_s_sep(dirname)

    if relative_to and not isinstance(relative_to, str):
        raise ValueError("relative_to must be str or None")

    if maxdepth:

        if not isinstance(maxdepth, int):
            raise ValueError("maxdepth must be int or None")

        else:
            if maxdepth < 0:
                raise ValueError("maxdepth can't be lesser than zero")

    dirname = wayround_org.utils.path.normpath(dirname)

    absp = dirname.startswith(s_sep)
    dirname = wayround_org.utils.path.abspath(dirname)

    lst = []

    if not mute:
        logging.info(
            "Setting list of files in `{}' and it's subdirs".format(dirname)
            )

    if isinstance(exclude_paths, list):
        exclude_paths2 = list()

        for i in exclude_paths:

            f_path = None

            if i.startswith(s_sep):
                f_path = wayround_org.utils.path.abspath(i)
            else:
                f_path = wayround_org.utils.path.abspath(
                    wayround_org.utils.path.join(
                        dirname, i
                        )
                    )

            if ((dirname == os.path.sep and f_path.startswith(os.path.sep)) or
                    (f_path + os.path.sep).startswith(dirname + os.path.sep)):
                exclude_paths2.append(f_path)

        exclude_paths = exclude_paths2

    if not mute:
        logging.info("Walking...")

    dirname_path_length = wayround_org.utils.path.path_length(dirname)

    for dire, dirs, files in os.walk(
            dirname,
            onerror=onerror,
            followlinks=followlinks
            ):

        current_path_length = (
            wayround_org.utils.path.path_length(dire) - dirname_path_length
            ) + 1

        if maxdepth:
            if current_path_length == maxdepth:
                while len(dirs) != 0:
                    del(dirs[0])

        if sort:
            dirs.sort()
            files.sort()

        if isinstance(exclude_paths, list):

            for i in dirs[:]:

                f_path = wayround_org.utils.path.abspath(
                    wayround_org.utils.path.join(
                        dire, i
                        )
                    )

                if f_path in exclude_paths:
                    while i in dirs:
                        dirs.remove(i)

        for f in files:

            f_path = wayround_org.utils.path.join(dire, f)

            append = True

            if not list_symlincs and os.path.islink(f_path):
                append = False

            if append:
                if acceptable_endings:

                    found = False

                    for i in acceptable_endings:
                        if f.endswith(i):
                            found = True
                            break

                    if not found:
                        append = False

            if append:
                if print_found and not mute:
                    print("    {}".format(f_path))
                lst.append(f_path)

        if include_dirs:
            for f in dirs:

                f_path = wayround_org.utils.path.join(dire, f)

                append = True

                if not list_symlincs and os.path.islink(f_path):
                    append = False

                if append:
                    if print_found and not mute:
                        print("    {}".format(f_path))
                    lst.append(f_path)

        if not mute:
            pp = None
            if not relative_to:
                pp = dire
            else:
                pp = wayround_org.utils.path.relpath(dire, relative_to)

            wayround_org.utils.terminal.progress_write(
                "    ({} files): {}".format(len(lst), pp)
                )

    if not mute:
        wayround_org.utils.terminal.progress_write_finish()

    ret = lst

    if not relative_to:

        if not absp:

            p_path_s_l = len(dirname) + 1

            for i in range(len(ret)):
                ret[i] = ret[i][p_path_s_l:]

    else:

        for i in range(len(ret)):
            ret[i] = wayround_org.utils.path.relpath(ret[i], relative_to)

    return ret


def null_file(filename):
    ret = 0
    try:
        f = open(filename, 'w')
    except:
        ret = 1
    else:
        f.close()
    return ret


def get_dir_size(name):
    name = wayround_org.utils.path.abspath(name)
    if not os.path.isdir(name):
        raise OSError("Not a dir `{}'".format(name))

    size = 0

    lst = os.listdir(name)
    for i in ['.', '..']:
        if i in lst:
            lst.remove(i)

    lst.sort()

    for i in lst:
        f_pth = wayround_org.utils.path.abspath(name + os.path.sep + i)
        if not os.path.islink(f_pth):
            if os.path.isfile(f_pth):
                s = os.stat(f_pth)
                size += s.st_size
            elif os.path.isdir(f_pth):
                size += get_dir_size(f_pth)

    return size


def get_file_size(name):

    ret = None

    if not os.path.exists(name):
        ret = None
    else:
        if os.path.isfile(name):
            s = os.stat(name)
            ret = s.st_size
        elif os.path.isdir(name):
            ret = get_dir_size(name)

    return ret


def convert_symlink_to_file(path):

    ret = 0

    if os.path.islink(path):

        r_path = os.path.realpath(path)

        if os.path.isfile(r_path):
            os.unlink(path)
            shutil.copy2(r_path, path)
            ret = 0

        else:
            ret = 1

    return ret


def dereference_file(filename):

    ret = 0

    filename = wayround_org.utils.path.abspath(filename)

    if not os.path.exists(filename):
        ret = 1

    else:
        if os.path.isdir(filename):
            ret = 0
        else:
            if not os.path.islink(filename):
                ret = 0
            else:
                lnk = None
                dir_name = wayround_org.utils.path.abspath(
                    os.path.dirname(filename)
                    )

                try:
                    lnk = os.readlink(filename)
                except:
                    ret = 2
                else:
                    if lnk[0] != '/':
                        lnk = wayround_org.utils.path.abspath(
                            wayround_org.utils.path.join(dir_name, lnk)
                            )

                    os.unlink(filename)
                    shutil.copy2(lnk, filename)

    return ret


def dereference_files_in_dir(dirname):

    ret = 0

    dirname = wayround_org.utils.path.abspath(dirname)

    try:
        for dirpath, dirnames, filenames in os.walk(dirname):
            filenames.sort()
            dirnames.sort()
            dirpath = wayround_org.utils.path.abspath(dirpath)

            for i in filenames:
                if dereference_file(os.path.join(dirpath, i)) != 0:
                    logging.error(
                        "Could not dereference `{}'".format(
                            wayround_org.utils.path.relpath(
                                dirname,
                                os.getcwd()
                                )
                            )
                        )

                    ret = 1
    except:
        logging.exception("Dir files dereferencing exception")
        ret = 2

    return ret


def files_by_mask_copy_to_dir(in_dir, out_dir, mask='*.h'):

    in_dir = wayround_org.utils.path.abspath(in_dir)
    out_dir = wayround_org.utils.path.abspath(out_dir)

    ret = 0
    try:
        for dirpath, dirnames, filenames in os.walk(in_dir):
            filenames.sort()
            dirnames.sort()
            dirpath = wayround_org.utils.path.abspath(dirpath)

            for i in filenames:
                if fnmatch.fnmatch(i, mask):
                    shutil.copy2(
                        dirpath + os.path.sep + i,
                        out_dir + os.path.sep + i,
                        follow_symlinks=True
                        )

    except:
        logging.exception("Files by mask copy to dir exception")
        ret = 1

    return ret


class FDStatusWatcher:

    def __init__(self, on_status_changed=None):

        self._clear(init=True)

        self._on_status_changed = on_status_changed

    def __del__(self):
        self.stop()

    def _clear(self, init=False):

        if not init:
            if self.stat() != 'stopped':
                raise RuntimeError("Working. Cleaning restricted")

        if not init:
            if self._fd and self._poll:
                self._poll.unregister(self._fd)

        self._poll = None

        self._fd = None

        self._watching_thread = None

        self._stop_flag = False

        self.fd_status = None

        self._starting = False
        self._stopping = False

    def set_fd(self, fd):

        if not isinstance(fd, int):
            raise TypeError("`fd' must be int")

        logging.debug(
            "{}: Switching monitoring to new fd {}, previaus was {}".format(
                type(self).__name__,
                fd, self._fd
                )
            )

        worked = False
        if self.stat() == 'working':
            worked = True

            self.stop()

        self._fd = fd

        if worked:
            self.start()

    def get_fd(self):

        return self._fd

    def stop(self):

        if not self._starting and not self._stopping:

            self._stopping = True
            self._stop_flag = True
            self.wait('stopped')
            self._clear()
            self._stopping = False

    def start(self):

        threading.Thread(
            name="Thread Starting Socket Watcher",
            target=self._start
            ).start()

    def _start(self):

        if not isinstance(self._fd, int):
            raise TypeError("file descriptor must be given before start")

        if (not self._starting
                and not self._stopping
                and self.stat() == 'stopped'):

            self._starting = True

            self._poll = select.poll()
            self._poll.register(
                self._fd,
                select.POLLIN | select.POLLPRI | select.POLLOUT |
                select.POLLERR | select.POLLHUP | select.POLLNVAL
                )

            self._watching_thread = threading.Thread(
                name="Thread watching FD {}".format(self._fd),
                target=self._watching_method
                )

            self._watching_thread.start()

            self._starting = False

    def stat(self):

        ret = 'stopped'

        if bool(self._watching_thread):
            ret = 'working'
        else:
            ret = 'stopped'

        return ret

    def wait(self, what='stopped'):

        allowed_what = ['stopped', 'working']

        if not what in allowed_what:
            raise ValueError("`what' must be in {}".format(allowed_what))

        while True:
            time.sleep(0.1)
            if self.stat() == what:
                break

        return

    def _watching_method(self):

        while True:

            if self._stop_flag:
                break

            new_stat_lst = self._poll.poll(100)

            if len(new_stat_lst) > 0:

                new_stat_event = new_stat_lst[0][1]

                if new_stat_event != self.fd_status:
                    threading.Thread(
                        name="FD {} status changed to [{}]".format(
                            self._fd,
                            '|'.join(poll_stat_namer(new_stat_event))
                            ),
                        target=self._on_status_changed,
                        args=(self._fd, poll_stat_namer(new_stat_event),)
                        ).start()

                self.fd_status = new_stat_event

        self._watching_thread = None


def poll_stat_namer(event):

    if not isinstance(event, int):
        raise TypeError("`event' must be int, but it is `{}'".format(event))

    devided = poll_stat_devider(event)
    names = set()

    for i in POLL_CONSTS.keys():

        for j in devided:

            if POLL_CONSTS[i] == j:
                names.add(i)

    return list(names)


def poll_stat_devider(event):

    if not isinstance(event, int):
        raise TypeError("`event' must be int, but it is `{}'".format(event))

    devided = []

    for i in POLL_CONSTS:

        int_val = eval("select.{}".format(i))

        if int_val & event != 0:
            devided.append(int_val)

    return devided


def print_status_change(sock, stats):
    logging.info("File descriptor {} status changed to {}".format(sock, stats))


def which(name, under=None, exception_if_not_found=True):
    """
    define 'under' to exclude not acceptable PATH components
    """

    ret = None

    splitted_PATH = os.environ['PATH'].split(':')

    if isinstance(under, str):
        under = [under]

    if under is None:
        under = copy.copy(splitted_PATH)

    for i in range(len(under) - 1, -1, -1):
        ui = under[i]

        if not ui.endswith('/bin') and not ui.endswith('/sbin'):
            under.append(
                wayround_org.utils.path.join(
                    ui,
                    'bin'
                    )
                )
            under.append(
                wayround_org.utils.path.join(
                    ui,
                    'sbin'
                    )
                )

    for i in range(len(under) - 1, -1, -1):
        if not os.path.isdir(under[i]):
            del under[i]

    for i in under:

        n_f_n = wayround_org.utils.path.join(i, name)

        # print("checking: {}".format(n_f_n))

        if os.path.isfile(n_f_n):
            ret = n_f_n
            break

    if ret is None and exception_if_not_found:
        raise FileNotFoundError("`{}' executable not found".format(name))

    return ret


def checksumed_dir_redue(reducing_dir, reducable_dir, method='sha512'):

    reducing_dir_filelist = wayround_org.utils.file.files_recurcive_list(
        reducing_dir,
        onerror=None,
        followlinks=False,
        exclude_paths=None,
        relative_to=None,
        mute=False,
        sort=True,
        acceptable_endings=None,
        print_found=False,
        list_symlincs=False,
        maxdepth=None
        )

    reducing_dir_sums = wayround_org.utils.checksum.checksums_by_list(
        reducing_dir_filelist, method
        )

    reducable_dir_filelist = wayround_org.utils.file.files_recurcive_list(
        reducable_dir,
        onerror=None,
        followlinks=False,
        exclude_paths=None,
        relative_to=None,
        mute=False,
        sort=True,
        acceptable_endings=None,
        print_found=False,
        list_symlincs=False,
        maxdepth=None
        )

    reducable_dir_sums = wayround_org.utils.checksum.checksums_by_list(
        reducable_dir_filelist, method
        )

    for i in reducable_dir_filelist:

        for j in reducing_dir_filelist:

            if reducing_dir_sums[j] == reducable_dir_sums[i]:

                rel_path = \
                    wayround_org.utils.path.relpath(j, os.path.dirname(i))

                if os.path.isfile(i) or os.path.islink(i):
                    os.unlink(i)

                os.symlink(rel_path, i)

                break

    return 0
