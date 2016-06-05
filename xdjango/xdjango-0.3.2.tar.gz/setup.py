from setuptools import setup, find_packages


EXCLUDE_FROM_PACKAGES = []

REQUIRES = ["sdklib >= 1.0", "Django>=1.8.4", "djangorestframework>=3.3.3"]

setup(
    name = 'xdjango',
    version = '0.3.2',
    description = 'Xtra-django library',
    author='Ivan Martin',
    author_email='ivanmar_91@hotmail.com',
    url='https://bitbucket.org/projectx-team/xdjango',
    install_requires=REQUIRES,
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