
SETUP_INFO = dict(
    name = 'infi.django_rest_utils',
    version = '0.11.3',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://git.infinidat.com/host-opensource/infi.django_rest_utils',
    license = 'PSF',
    description = """Enhancements to django-rest-framework""",
    long_description = """Enhancements to django-rest-framework""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'docopt',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': [
'*.html',
'*.js',
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [
'rest_utils = infi.django_rest_utils.rest_utils:rest_utils'
],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

