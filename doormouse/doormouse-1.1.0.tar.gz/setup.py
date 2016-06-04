from setuptools import setup, find_packages
setup(
    name             = "doormouse",
    version          = "1.1.0",
    packages         = find_packages(exclude="tests"),
    test_suite       = 'tests',

    install_requires = [
                           'prettytable', 
                           'pyOpenSSL>=0.15.1', 
                           'pytz'
                       ],

    tests_require    = [
                           'mock', 
                           'pyOpenSSL>=0.15.1'
                       ],

    package_data     = {
                           '': [
                                   '*.txt', 
                                   '*.rst'
                               ]
                       },

    entry_points     = { 
                           'console_scripts': [
                               'doormouse = doormouse.cli:main'
                           ]
                       },

    author           = "BrainGu",
    author_email     = "doormouse@braingu.com",
    description      = "PKI without the PITA.",
    long_description = "Doormouse provides a library and CLI for managing your PKI. Currently "
                       "supports building x509 certificate infrastructure to track, "
                       "create/revoke and sign certificates.",
    license          = "Apache Software License",
    keywords         = "x509 ca certificate pki doormouse openssl",
    url              = "http://github.com/doormouseio/doormouse-core",
    classifiers      = [
                           'Development Status :: 5 - Production/Stable',
                           'Environment :: Console',
                           'Intended Audience :: Developers',
                           'Intended Audience :: Information Technology',
                           'Intended Audience :: System Administrators',
                           'License :: OSI Approved :: Apache Software License',
                           'Natural Language :: English',
                           'Operating System :: MacOS :: MacOS X',
                           'Operating System :: Microsoft :: Windows :: Windows 7',
                           'Operating System :: POSIX :: Linux',
                           'Programming Language :: Python :: 2.7',
                           'Topic :: Security',
                           'Topic :: Security :: Cryptography',
                           'Topic :: Software Development',
                           'Topic :: System :: Systems Administration'
                       ]
)
