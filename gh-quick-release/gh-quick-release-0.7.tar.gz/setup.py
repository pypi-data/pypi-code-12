from setuptools import setup, find_packages

setup(
    name = 'gh-quick-release',
    packages = find_packages(),
    version = '0.7',
    description = 'Create a new release quickly',
    author = 'Jonathan Boudreau',
    author_email = 'jonathan.boudreau.92@gmail.com',
    url = 'https://github.com/AGhost-7/gh-quick-release',
    download_url = '',
    keywords = ['release', 'npm', 'github', 'nodejs'],
    classifiers = [],
    install_requires = [
        'requests',
        'simplejson'
    ],
    entry_points = { 
        'console_scripts': [
            'gh-quick-release=gh_quick_release:main'
        ]
    }
)
