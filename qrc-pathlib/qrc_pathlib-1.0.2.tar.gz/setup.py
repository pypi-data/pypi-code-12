import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'qrc_pathlib', 'version.py')) as f:
    VERSION = None
    code = compile(f.read(), 'version.py', 'exec')
    exec(code)
    assert VERSION


setup(
    name='qrc_pathlib',
    version=VERSION,
    packages=['qrc_pathlib'],
    url='https://github.com/GreatFruitOmsk/qrc_pathlib',
    license='MIT',
    author='Ilya Kulakov',
    author_email='kulakov.ilya@gmail.com',
    description="Extension for pathlib that implements Path and PurePath for Qt Resources System.",
    platforms=["Mac OS X 10.6+", "Windows XP+", "Linux 2.6+"],
    keywords='qt qrc pyqt pathlib',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Topic :: System :: Filesystems',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',

        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    test_suite='test'
)
