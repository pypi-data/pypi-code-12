
"""
This module is for creating variable-like objects for storring size python
objects
"""

import os.path
import yaml

import wayround_org.utils.path


class PersistentMemoryDriver:
    pass


class PersistentMemoryDriverFileSystem(PersistentMemoryDriver):

    def __init__(self, directory):
        self.directory = directory
        self.counter = 0
        return

    def init(self):
        os.makedirs(self.directory, exist_ok=True)
        files = os.listdir(self.directory)
        for i in files:

            if not i.endswith('.yaml'):
                continue

            descriptor = int(i[0:i.find('.')])
            os.unlink(self.gen_descriptor_filepath(descriptor))
        return

    def gen_descriptor_filepath(self, descriptor):
        if not isinstance(descriptor, int):
            raise TypeError("`descriptor' must be int")
        if descriptor < 0:
            raise ValueError("`descriptor' must be >= 0")
        ret = wayround_org.utils.path.join(
            self.directory,
            '{}.yaml'.format(str(descriptor))
            )
        return ret

    def new(self):
        ret = self.counter
        self.counter += 1
        return ret

    def delete(self, descriptor):
        f_path = self.gen_descriptor_filepath(descriptor)
        if os.path.isfile(f_path):
            os.unlink(f_path)
        return

    def get_value(self, descriptor):
        ret = None
        f_path = self.gen_descriptor_filepath(descriptor)
        if os.path.isfile(f_path):
            with open(f_path) as f:
                ret = yaml.load(f.read())
        return ret

    def set_value(self, descriptor, value):
        f_path = self.gen_descriptor_filepath(descriptor)
        with open(f_path, 'w') as f:
            f.write(yaml.dump(value))
        return

    def open(self, descriptor, flags):
        f_path = self.gen_descriptor_filepath(descriptor)
        ret = open(f_path, flags)
        return ret

    def get_size(self):
        return os.stat(self.gen_descriptor_filepath(descriptor)).st_size

    def get_bytes(self, descriptor, size_limit=1024, bs=500):
        ret = None

        f_path = self.gen_descriptor_filepath(descriptor)

        if self.get_size(descriptor) <= size_limit:
            if os.path.isfile(f_path):
                ret = b''
                with open(f_path, 'br') as f:
                    while True:
                        b = f.read(bs)
                        if len(b) == 0:
                            break
                        ret += b

        return ret


class PersistentMemory:

    @classmethod
    def new_fs_memory(cls, path):
        return cls(PersistentMemoryDriverFileSystem(path))

    def __init__(self, driver):
        if not isinstance(driver, PersistentMemoryDriver):
            raise TypeError(
                "invalid `driver' instance type"
                )
        self.driver = driver
        return

    def new(self, value=None):
        return PersistentVariable(self.driver, value)

    def init(self):
        return self.driver.init()


class PersistentVariable:

    def __init__(self, driver, initial):
        if not isinstance(driver, PersistentMemoryDriver):
            raise TypeError(
                "invalid `driver' instance type"
                )
        self.driver = driver
        self.descriptor = self.driver.new()
        self.set(initial)
        return

    def get(self):
        return self.driver.get_value(self.descriptor)

    def set(self, value):
        return self.driver.set_value(self.descriptor, value)

    def __del__(self):
        self.driver.delete(self.descriptor)
        return

    def open(self, flags='r'):
        return self.driver.open(self.descriptor, flags)

    def get_size(self):
        return self.driver.get_size(self.descriptor)

    def get_bytes(self, size_limit=1024, bs=500):
        return self.driver.get_bytes(
            self,
            self.descriptor,
            size_limit=size_limit,
            bs=bs
            )
