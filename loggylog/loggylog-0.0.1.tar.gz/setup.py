import os
from setuptools import setup

# loggylog
# Complex logging, simple API


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="loggylog",
    version="0.0.1",
    description="Complex logging, simple API",
    author="Johan Nestaas",
    author_email="johannestaas@gmail.com",
    license="GPLv3+",
    keywords="",
    url="https://www.bitbucket.org/johannestaas/loggylog",
    packages=['loggylog'],
    package_dir={'loggylog': 'loggylog'},
    long_description=read('README.rst'),
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[],
    # entry_points={
    #     'console_scripts': [
    #         'loggylog=loggylog:main',
    #     ],
    # },
    # If you get errors running setup.py install:
    # zip_safe=False,
    #
    # For including non-python files:
    # package_data={
    #     'loggylog': ['templates/*.html'],
    # },
    # include_package_data=True,
)
