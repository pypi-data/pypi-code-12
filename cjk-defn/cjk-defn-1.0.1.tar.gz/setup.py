#!/usr/bin/env python3

""" Setup script for packaging and installation. """

from distutils.core import setup

with open('README.rst', 'r', encoding='utf-8') as fin:
    LONG_DESCRIPTION = fin.read()

setup(
    #
    # Basic information
    #
    name='cjk-defn',
    version='1.0.1',
    author='yaoguai',
    author_email='lapislazulitexts@gmail.com',
    url='https://github.com/yaoguai/cjk-defn',
    license='MIT',
    #
    # Descriptions & classifiers
    #
    description='Console CJK dictionary program.',
    long_description=LONG_DESCRIPTION,
    keywords='chinese japanese korean cjk asia language dictionary',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Religion',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'],
    #
    # Included Python files
    #
    scripts=['cjk-defn'],
    py_modules=['cjk_defn'],
    data_files=[
        ('share/doc/cjk-defn', [
            'LICENSE.rst',
            'README.rst']),
        ('share/man/man1', [
            'cjk-defn.1']),
        ('var/lib/cjk-defn', [
            'var/lib/cjk-defn/dump-database',
            'var/lib/cjk-defn/make-database',
            'var/lib/cjk-defn/vacuum-database'])]
)
