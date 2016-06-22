
SETUP_INFO = dict(
    name = 'infi.reboot',
    version = '0.2.13',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.reboot',
    license = 'PSF',
    description = """A cross-platform module for handling reboot-pending operations.""",
    long_description = """A cross-platform module for handling reboot-pending operations.""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': [
'_posix_uptime.c'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    from setuptools import Extension
    import platform
    SETUP_INFO['packages'] = find_packages('src')
    if platform.system() in ["AIX", "SunOS"]:
        aix_extension = Extension('infi.reboot._posix_uptime',
            sources=['src/infi/reboot/_posix_uptime.c'])
        SETUP_INFO['ext_modules'] = [aix_extension]
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

