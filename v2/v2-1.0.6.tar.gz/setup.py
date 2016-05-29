#!/usr/bin/env python
from setuptools import find_packages, setup


conf = dict(name='v2',
            version='1.0.6',
            install_requires=['magiclog'],
            author='Jason Dusek',
            author_email='jason.dusek@gmail.com',
            url='https://github.com/solidsnack/v2',
            setup_requires=['pytest-runner', 'setuptools'],
            tests_require=['flake8', 'pytest', 'tox'],
            description='Intelligent auto-versioning.',
            packages=find_packages(),
            package_data={'v2': ['MANIFEST.in']},
            entry_points={'console_scripts': ['v2 = v2.__main__:main']},
            classifiers=['Environment :: Console',
                         'Intended Audience :: Developers',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: Unix',
                         'Operating System :: POSIX',
                         'Programming Language :: Python',
                         'Programming Language :: Python :: 2.7',
                         'Programming Language :: Python :: 3.5',
                         'Topic :: Software Development',
                         'Development Status :: 4 - Beta'])


if __name__ == '__main__':
    setup(**conf)
