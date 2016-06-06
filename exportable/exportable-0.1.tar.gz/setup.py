import os

from distutils.core import setup


def get_requirements():
    """Get requirements from requirements.txt. Lines starting with a # are skipped."""
    here = os.path.dirname(__file__)
    req = os.path.join(here, "requirements.txt")
    for line in open(req, "r", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        yield line.strip()


setup(
    name='exportable',
    version='0.1',
    packages=[
        'exportable',
        'exportable.exporters',
        'exportable.exporters.tests'
    ],
    url='https://github.com/amcat/exportable',
    license='AGPL',
    author='AmCAT Developers',
    author_email='',
    description='',
    install_requires=list(get_requirements())
)
