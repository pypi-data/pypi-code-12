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
        name = 'karellen-testing',
        version = '0.0.1.dev20160416005023',
        description = '''Karellen Testing Library''',
        long_description = '''Please visit https://github.com/karellen/karellen-testing for more information!''',
        author = "Karellen, Inc",
        author_email = "supervisor@karellen.co",
        license = 'Apache License, Version 2.0',
        url = 'https://github.com/karellen/karellen-testing',
        scripts = [],
        packages = ['karellen.testing.mock'],
        py_modules = [],
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Testing'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
