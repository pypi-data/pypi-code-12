#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'python-printer-escpos',
        version = '0.0.3',
        description = '''Python interface for ESCPOS Printers''',
        long_description = '''Please visit https://github.com/shantanubhadoria/python-printer-escpos for more information!''',
        author = "Shantanu Bhadoria",
        author_email = "shantanu@cpan.org",
        license = 'Apache License, Version 2.0',
        url = 'https://github.com/shantanubhadoria/python-printer-escpos',
        scripts = [],
        packages = [
            'escpos',
            'escpos.commandset'
        ],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'Pillow',
            'pyserial',
            'pyusb',
            'qrcode'
        ],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
