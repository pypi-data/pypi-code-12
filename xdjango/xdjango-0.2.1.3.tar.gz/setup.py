from setuptools import setup, find_packages


EXCLUDE_FROM_PACKAGES = []

setup(
    name = 'xdjango',
    version = '0.2.1.3',
    description = 'Xtra-django library',
    author='Ivan Martin',
    author_email='ivanmar_91@hotmail.com',
    url='https://bitbucket.org/projectx-team/xdjango',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
)