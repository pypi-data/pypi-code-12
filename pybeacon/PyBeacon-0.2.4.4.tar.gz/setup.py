from setuptools import setup

setup(
    name = 'PyBeacon',
    version = '0.2.4.4',
    packages = ['PyBeacon'],
    entry_points = {
        "console_scripts": ['PyBeacon = PyBeacon.PyBeacon:main']
    },
    install_requires = [
        'bluez',
        'bluez-hcidump'
    ],

    summary = 'Python script for scanning and advertising urls over Eddystone-URL.',

    description = 'Python script for scanning and advertising urls over Eddystone-URL.',

    url = 'https://github.com/nirmankarta/PyBeacon',

    download_url = 'https://github.com/nirmankarta/PyBeacon/archive/master.zip',

    author = 'Nirmankarta',

    author_email = 'we@nirmankarta.com',

    maintainer = 'Prabhanshu Attri',

    maintainer_email = 'contact@prabhanshu.com',

    license = 'Apache License 2.0',

    keywords = ['Eddystone', 'Eddystone URL', 'Beacon', 'Raspberry Pi'],

    classifiers = [
       
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)