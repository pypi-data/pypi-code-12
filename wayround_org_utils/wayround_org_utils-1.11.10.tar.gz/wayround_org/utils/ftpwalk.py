
import ftplib
import logging
import os.path
import re
import threading


LIST_ANSWER_RE = (
    r'(?P<mode>.*?)\s+'
    r'(?P<blocks>.*?)\s+'
    r'(?P<uid>.*?)\s+'
    r'(?P<gid>.*?)\s+'
    r'(?P<size>.*?)\s+'
    r'(?P<date1>.*?)\s+'
    r'(?P<date2>.*?)\s+'
    r'(?P<date3>.*?)\s+'
    r'(?P<name>.*)'
    )

LIST_ANSWER_RE_C = re.compile(LIST_ANSWER_RE)


class FTPWalk:

    def __init__(self, ftp_connection):
        self._ftp_connection = ftp_connection
        self._dir_cache = {}
        self._fstats_cb_errors = None
        self._fstats_cb_dir = None
        self._get_dir_cache_lock = threading.Lock()
        return

    def _fstats_cb(self, string):

        # print("_fstats_cb string: {}".format(string))

        if string.startswith('total'):
            # if not self._fstats_cb_dir in self._dir_cache:
            #    self._dir_cache[self._fstats_cb_dir] = {}
            return

        if not isinstance(string, str):
            raise TypeError("type error")

        if string == '':
            raise ValueError("value error")

        r_re = LIST_ANSWER_RE_C.match(string)

        if r_re is not None:

            self._dir_cache[self._fstats_cb_dir][r_re.group('name')] = {
                'mode': r_re.group('mode'),
                'blocks': r_re.group('blocks'),
                'uid': r_re.group('uid'),
                'gid': r_re.group('gid'),
                'size': r_re.group('size'),
                'date1': r_re.group('date1'),
                'date2': r_re.group('date2'),
                'date3': r_re.group('date3')
                }
        else:
            raise Exception("couldn't parse: {}".format(string))
            self._fstats_cb_errors = True

        return

    def get_dir_cache(self, path):
        """
        return: dict - ok, None - error, False - not a dir
        """

        # print("get_dir_cache, path: {}".format(path))

        if path == '':
            path = '/'

        ret = False

        with self._get_dir_cache_lock:

            # print("self._dir_cache: {}".format(self._dir_cache))

            if path in self._dir_cache:
                ret = self._dir_cache[path]
            else:
                pwd = self._ftp_connection.pwd()

                try:
                    self._ftp_connection.cwd(path)
                except ftplib.error_perm:
                    logging.exception("error")
                    ret = None
                else:
                    self._fstats_cb_dir = path
                    self._fstats_cb_errors = False
                    if not self._fstats_cb_dir in self._dir_cache:
                        self._dir_cache[self._fstats_cb_dir] = {}
                    # pwd = self._ftp_connection.pwd()
                    self._ftp_connection.cwd(path)
                    try:
                        self._ftp_connection.dir(self._fstats_cb)
                    except:
                        logging.exception("error")
                        self._fstats_cb_errors = True

                    if self._fstats_cb_errors:
                        if path in self._dir_cache:
                            del self._dir_cache[path]
                        ret = None
                    else:
                        ret = self._dir_cache[path]

        # print("get_dir_cache, ret: {}".format(ret))

        return ret

    def listdir(self, path):
        dir_cache = self.get_dir_cache(path)
        ret = list(dir_cache.keys())
        return ret

    def fstat_d_n(self, dirname, name):

        # print('fstat_d_n: {}, {}'.format(dirname, name))

        ret = None
        dir_cache = self.get_dir_cache(dirname)
        if dir_cache is not None and name in dir_cache:
            ret = dir_cache[name]

        # print('fstat_d_n ret: {}'.format(ret))

        return ret

    def fstat(self, name):
        
        # print('fstat: {}'.format(name))

        fdir = os.path.dirname(name)
        name = os.path.basename(name)

        ret = self.fstat_d_n(fdir, name)

        # print('fstat ret: {}'.format(ret))

        return ret

    def _is(self, name, c='-', no=False):
        
        # print("_is: {}, {}, {}".format(name, c, no))

        ret = None

        stat = self.fstat(name)
        
        # print('    stat: {}'.format(stat))

        if stat is not None:
            ret = stat['mode'][0] == c
            if no:
                ret = not ret

        return ret

    def is_dir(self, name):
        return self._is(name, c='d')

    def is_file(self, name):
        return self._is(name, c='-')

    def is_link(self, name):
        return self._is(name, c='l')

    def exists(self, name):
        ret = self.fstat(name) is not None
        return ret

    def get(self, path, c='d', no=False):

        ret = None

        dir_cache = self.get_dir_cache(path)

        if dir_cache is not None:
            ret = []
            for i in dir_cache.keys():
                res = dir_cache[i]['mode'][0] == c
                if no:
                    res = not res
                if res:
                    ret.append(i)

        return ret

    def get_files(self, path):
        return self.get(path, '-')

    def get_dirs(self, path):
        return self.get(path, 'd')

    def get_links(self, path):
        return self.get(path, 'l')

    def get_not_dirs(self, path):
        return self.get(path, 'd', True)
