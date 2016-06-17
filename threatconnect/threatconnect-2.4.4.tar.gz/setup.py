from setuptools import setup, find_packages

# 
# PATCH 1
#

setup(
    name='threatconnect',
    version='2.4.4',
    description='Python SDK for ThreatConnect API',
    author='ThreatConnect',
    author_email='support@threatconnect.com',
    # package_dir = {'': 'src'},
    packages=find_packages(),
    url='https://github.com/ThreatConnect-Inc/threatconnect-python',
    download_url='https://github.com/ThreatConnect-Inc/threatconnect-python/tarball/2.4',
    license='ASL',
    install_requires=['requests', 'python-dateutil'],
    extras_require={
        ':python_version=="2.7"': ['enum34']
    },
    use_2to3=True,
    # convert_2to3_doctests = [''],
    # use_2to3_fixers = [''],
    use_2to3_exclude_fixers=['lib2to3.fixes.fix_print'],
    entry_points={
        'console_scripts': [
            'stanchion=bin.stanchion:main'
        ],
    },
)
