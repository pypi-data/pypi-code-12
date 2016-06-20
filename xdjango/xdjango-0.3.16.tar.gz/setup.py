import os

from setuptools import setup, find_packages


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


EXCLUDE_FROM_PACKAGES = []

REQUIRES = ["sdklib >= 1.0", "Django>=1.8.4", "djangorestframework>=3.3.3"]

setup(
    name = 'xdjango',
    version = '0.3.16',
    description = 'Xtra-django library',
    author='Ivan Martin',
    author_email='ivanmar_91@hotmail.com',
    url='https://bitbucket.org/projectx-team/xdjango',
    install_requires=REQUIRES,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    package_data=get_package_data('xdjango'),
)