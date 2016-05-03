
"""
Module for organizing persistent supporting flags for files

This can be used to create any sort of flags

YAML is used for storing data in flags

flags can be also used as simple raw files
"""

import copy
import os.path

import yaml

import wayround_org.utils.path
import wayround_org.utils.threading
import wayround_org.utils.types_presets


def verify_flag_name(flagged_file, flag_name):
    """
    function for checking whatever user supplied flag name supported by
    FlaggedFile class instance
    """
    if not isinstance(flagged_file, FlaggedFile):
        raise TypeError("`flagged_object' must be inst of FlaggedFile")

    if not isinstance(flag_name, str):
        raise TypeError("flag name must be str")

    if flag_name not in flagged_file.possible_flags:
        raise ValueError("invalid flag name")
    return


def check_formatted_access_to_raw_flag(flagged_file, flag_name):

    verify_flag_name(flagged_file, flag_name)

    if flag_name in flagged_file.raw_flags:
        raise ValueError(
            "trying to use formatted access to raw flag `{}'".format(
                flag_name
                )
            )
    return


class FlaggedFile:
    """
    Use this class for creating flags
    """

    def __init__(
            self,
            path,
            basename,
            possible_flags,
            raw_flags=None,
            object_locker=None
            ):
        """
        path - directory in which to store flags
        basename - base name to which flag extensions will be appended
        possible_flags - list (or set) of flags which supported by  instance of
            this class
        raw_flags - list (or set) of flags, internal structure of which should
            not be considered in YAML markup. so trying to use on them YAML
            methods of this class will raise exception.
        object_locker - instance of ObjectLocker to use for sefe access to
            flag files. use None for automatic ceation of this
        """

        self._path = None
        self._basename = None

        if raw_flags is None:
            raw_flags = set()

        if not isinstance(possible_flags, (list, set)):
            raise TypeError("`possible_flags' must be list or set")

        if not isinstance(raw_flags, (list, set)):
            raise TypeError("`raw_flags' must be list, set or None")

        self.path = path
        self.basename = basename
        self.possible_flags = set(possible_flags)
        self.raw_flags = set(raw_flags)

        for i in self.raw_flags:
            if i not in self.possible_flags:
                print(
                    "warning (FlaggedFile):"
                    " {} not in possible_flags".format(i)
                    )

        self.possible_flags |= self.raw_flags

        if object_locker is None:
            object_locker = wayround_org.utils.threading.ObjectLocker()

        self.object_locker = object_locker

        for i in possible_flags:
            setattr(self, '{}_path'.format(i), self.gen_flag_path(i))

        return

    def get_flags_list(self):
        return copy.copy(self.possible_flags)

    @property
    def path(self):
        """
        returns directory path with which this instance is working now.
        this is wrapped in property to ensure correct value is passed to it
        """
        return self._path

    @path.setter
    def path(self, value):
        """
        change path parameter
        """
        if not isinstance(value, str):
            raise TypeError("`path' must be str")
        self._path = value
        return

    @property
    def basename(self):
        return self._basename

    @basename.setter
    def basename(self, value):
        if not isinstance(value, str):
            raise TypeError("`basename' must be str")
        self._basename = value
        return

    def unset_all_flags(self):
        for i in self.possible_flags:
            self.unset_flag(i)
        return

    def gen_flag_path(self, name):
        verify_flag_name(self, name)
        ret = wayround_org.utils.path.join(
            self.path,
            '{}.{}'.format(self.basename, name)
            )
        return ret

    def get_flag_path(self, name):
        verify_flag_name(self, name)
        ret = getattr(self, '{}_path'.format(name))
        return ret

    def get_flag_lock(self, name):
        ret = self.object_locker.get_lock(self.get_flag_path(name))
        return ret

    def get_is_flag_locked(self, name):
        ret = self.object_locker.get_is_locked(self.get_flag_path(name))
        return ret

    def get_is_flag_set(self, name):
        ret = os.path.isfile(self.get_flag_path(name))
        return ret

    def open_flag(self, name, flags='r'):
        ret = open(self.get_flag_path(name), flags)
        return ret

    def write_flag_from_persistent_variable(
            self,
            name,
            pv,
            stop_event=None,
            bs=2 * 1024**2
            ):
        """
        ret: True - success, None - stopped
        """

        if not isinstance(
                pv,
                wayround_org.utils.pm.PersistentVariable
                ):
            raise TypeError(
                "must be inst of "
                "wayround_org.utils.pm.PersistentVariable"
                )

        ret = None

        with self.get_flag_lock(name):
            with self.open_flag(name, 'bw') as f1:
                with pv.open('br') as f2:
                    while True:
                        if stop_event is not None and stop_event.is_set():
                            ret = None
                            break
                        b = f2.read(bs)
                        if len(b) == 0:
                            ret = True
                            break
                        f1.write(b)
        return ret

    def set_flag(self, name):
        verify_flag_name(self, name)
        if name in self.raw_flags:
            f_path = self.get_flag_path(name)
            if not self.get_is_flag_set(name):
                with self.get_flag_lock(name):
                    with self.open_flag(name, 'wb'):
                        pass
        else:
            data = self.get_flag_data(name)
            self.set_flag_data(name, data)
        return

    def set_flag_data(self, name, data):

        check_formatted_access_to_raw_flag(self, name)

        with self.get_flag_lock(name):
            with self.open_flag(name, 'w') as f:
                f.write(yaml.dump(data))

        return

    def get_flag_data(self, name):

        check_formatted_access_to_raw_flag(self, name)

        ret = None

        if self.get_is_flag_set(name):
            with self.get_flag_lock(name):
                with self.open_flag(name, 'r') as f:
                    ret = yaml.load(f.read())

        return ret

    def get_flag_size(self, name):
        verify_flag_name(self, name)
        ret = os.stat(self.get_flag_path(name)).st_size
        return ret

    def unset_flag(self, name):
        with self.get_flag_lock(name):
            if self.get_is_flag_set(name):
                os.unlink(self.get_flag_path(name))
        return

    def get_bool(self, name):
        ret = self.get_flag_data(name) is True
        return ret

    def set_bool(self, name, value=True):
        if not isinstance(value, bool):
            raise TypeError("`{}' value must be bool".format(name))
        self.set_flag_data(name, value)
        return

    def get_str(self, name):
        ret = self.get_flag_data(name)
        if not isinstance(ret, str):
            ret = None
        return ret

    def set_str(self, name, value):
        if not isinstance(value, str):
            raise TypeError("`{}' value must be str".format(name))
        self.set_flag_data(name, value)
        return

    def set_str_n(self, name, value):
        """
        Same as set_str, but allows None as value
        """
        if value is not None and not isinstance(value, str):
            raise TypeError("`{}' value must be str or None".format(name))
        self.set_flag_data(name, value)
        return

    def get_int(self, name):
        ret = self.get_flag_data(name)
        if not isinstance(ret, int):
            ret = None
        return ret

    def set_int(self, name, value):
        if not isinstance(value, int):
            raise TypeError("`{}' value must be int".format(name))
        self.set_flag_data(name, value)
        return

    def set_int_n(self, name, value):
        """
        Same as set_int, but allows None as value
        """
        if value is not None and not isinstance(value, int):
            raise TypeError("`{}' value must be int or None".format(name))
        self.set_flag_data(name, value)
        return

    def get_str_list(self, name):
        ret = self.get_flag_data(name)
        if not wayround_org.utils.types_presets.is_list_of_str(ret):
            ret = []
        return ret

    def set_str_list(self, name, value):
        if not wayround_org.utils.types_presets.is_list_of_str(value):
            raise TypeError("`{}' value must be list of str".format(name))
        self.set_flag_data(name, value)
        return

    def add_str_list(self, name, value):
        self.set_str_list(name, self.get_str_list(name) + [value])
        return

    def get_str_set(self, name):
        ret = self.get_flag_data(name)
        if not wayround_org.utils.types_presets.is_set_of_str(ret):
            ret = set()
        return ret

    def set_str_set(self, name, value):
        if not wayround_org.utils.types_presets.is_set_of_str(value):
            raise TypeError("`{}' value must be set of str".format(name))
        self.set_flag_data(name, value)
        return

    def add_str_set(self, name, value):
        self.set_str_list(
            name,
            self.get_str_list(name) + [value]
            )
        return

    def get_int_list(self, name):
        ret = self.get_flag_data(name)
        if not wayround_org.utils.types_presets.is_list_of_int(ret):
            ret = []
        return ret

    def set_int_list(self, name, value):
        if not wayround_org.utils.types_presets.is_list_of_int(value):
            raise TypeError("`{}' value must be list of int".format(name))
        self.set_flag_data(name, value)
        return

    def set_int_list_n(self, name, value):
        if (value is not None
            and not wayround_org.utils.types_presets.is_list_of_int(value)
            ):
            raise TypeError(
                "`{}' value must be None or list of int".format(name)
                )
        self.set_flag_data(name, value)
        return
