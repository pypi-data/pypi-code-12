
import os.path
import hashlib

import yaml

import wayround_org.utils.path
import wayround_org.utils.data_cache_miscs


class DataCache:

    def __init__(
            self,
            storage_directory,
            cache_name,
            cache_check_refresh_required_callback,
            cache_check_refresh_required_cb_args,
            cache_check_refresh_required_cb_kwargs,
            refresh_callback,
            refresh_cb_args,
            refresh_cb_kwargs,
            checksum_method
            ):
        """
        storage_directory - directory where cache is stored
        cache_name - name to whcih .cache extension added
        cache_check_refresh_required_callback - callable with two parameters,
            by which DataCache object and complete cache file name is passed.
            this callable should return:
                None - on error, True - if refresh is required, False - if
                refresh is not needed
        refresh_callback - callcble to call whan refresh is needed.
            refresh_callback must accept atleast two parameters: DataCach
            object and complete cache filename. also additional parameters may
            be passed passed by refresh_cb_args and refresh_cb_kwargs. this
            callable should write fresh data into file pointed by first
            parameter
        """

        if not isinstance(storage_directory, str):
            raise TypeError("`storage_directory' must be str")

        if not isinstance(cache_name, str):
            raise TypeError("`cache_name' must be str")

        if not callable(cache_check_refresh_required_callback):
            raise TypeError(
                "`cache_check_refresh_required_callback' must be callable"
                )

        if not callable(refresh_callback):
            raise TypeError("`refresh_callback' must be callable")

        if checksum_method not in ['md5', 'sha1', 'sha256', 'sha512']:
            raise ValueError("invalid `checksum_method' value")

        self.checksum_method = checksum_method

        self.storage_directory = storage_directory

        if not os.path.isdir(storage_directory):
            os.makedirs(storage_directory, exist_ok=True)

        self.cache_name = cache_name

        self.cache_check_refresh_required_callback = \
            cache_check_refresh_required_callback

        self.cache_check_refresh_required_cb_args = \
            cache_check_refresh_required_cb_args

        self.cache_check_refresh_required_cb_kwargs = \
            cache_check_refresh_required_cb_kwargs

        self.refresh_callback = refresh_callback

        self.refresh_cb_args = refresh_cb_args

        self.refresh_cb_kwargs = refresh_cb_kwargs
        return

    def get_complete_filename(self):
        ret = wayround_org.utils.path.join(
            self.storage_directory,
            self.cache_name + '.cache'
            )
        return ret

    def get_complete_filename_cs(self):
        ret = '{}.{}'.format(
            self.get_complete_filename(),
            self.checksum_method
            )
        return ret

    def calc_data_checksum(self):

        ret = None

        filename = self.get_complete_filename()

        if os.path.isfile(filename):

            dig = getattr(hashlib, self.checksum_method)()

            with open(filename, 'br') as f:
                while True:
                    b = f.read(2 * 1024**2)
                    if len(b) == 0:
                        break
                    dig.update(b)
            ret = dig.hexdigest().lower()

        return ret

    def rewrite_actual_checksum(self):
        cs = self.calc_data_checksum()
        cs_fn = self.get_complete_filename_cs()
        if cs is None:
            if os.path.isfile(cs_fn):
                os.unlink(cs_fn)
        else:
            with open(cs_fn, 'w') as f:
                f.write(cs)
        return

    def cache_data_integrity_check(self):
        """
        return:
            True - integrity check passed,
            False - integrity check not passed,
            None - some error
        """

        ret = False

        filename_sum_name = self.get_complete_filename_cs()

        d_c_sum = self.calc_data_checksum()

        if d_c_sum is not None:

            if os.path.isfile(filename_sum_name):
                with open(filename_sum_name) as f:
                    f_sum = f.read()

                f_sum = f_sum.strip().lower()

                if d_c_sum == f_sum:
                    ret = True

        return ret

    def open_cache(self):
        """
        return: None - on error, file opened in 'r' mode - on success
        """
        ret = None
        complete_filename = self.get_complete_filename()
        ct_cb_res = self.cache_check_refresh_required_callback(
            self,
            complete_filename,
            *self.cache_check_refresh_required_cb_args,
            **self.cache_check_refresh_required_cb_kwargs
            )
        if ct_cb_res is None:
            ret = None
        else:
            ct_cb_res = bool(ct_cb_res)
            if ct_cb_res is True:
                self.refresh_callback(
                    self,
                    complete_filename,
                    *self.refresh_cb_args,
                    **self.refresh_cb_kwargs
                    )
            ret = open(complete_filename, 'r')
        return ret


class ShortCSTimeoutYamlCacheHandler:

    def __init__(
            self,
            storage_directory,
            cache_name,
            timeout_delta,
            csmethod,
            freshdata_callback,
            freshdata_callback_args=None,
            freshdata_callback_kwargs=None
            ):
        
        if freshdata_callback_args is None:
            freshdata_callback_args = tuple()

        if freshdata_callback_kwargs is None:
            freshdata_callback_kwargs = dict()

        self.storage_directory = storage_directory
        self.cache_name = cache_name
        self.timeout_delta = timeout_delta
        self.csmethod = csmethod
        self.freshdata_callback = freshdata_callback
        self.freshdata_callback_args = freshdata_callback_args
        self.freshdata_callback_kwargs = freshdata_callback_kwargs

        self.dc = DataCache(
            self.storage_directory,
            self.cache_name,
            self._get_data_cache_check_refresh_required_cb,
            tuple(),
            dict(),
            self._get_data_cache_refresh_cb,
            tuple(),
            dict(),
            self.csmethod
            )
        return

    def _get_data_cache_check_refresh_required_cb(self, cache_mgr, path):

        ret = (
            wayround_org.utils.data_cache_miscs.check_data_cache_timeout(
                path,
                self.timeout_delta
                )
            or not cache_mgr.cache_data_integrity_check()
            )

        return ret

    def _get_data_cache_refresh_cb(self, cache_mgr, path):
        # print("args: {}".format(self.freshdata_callback_args))
        # print("kwargs: {}".format(self.freshdata_callback_kwargs))
        data = self.freshdata_callback(
            *self.freshdata_callback_args,
            **self.freshdata_callback_kwargs
            )
        with open(path, 'w') as f:
            f.write(yaml.dump(data))
        cache_mgr.rewrite_actual_checksum()
        return

    def get_data_cache(self):
        ret = None
        cache = self.dc.open_cache()
        if cache is not None:
            ret = yaml.load(cache.read())
            cache.close()
        return ret
