import sys
from setuptools import setup, find_packages

if sys.version_info < (3,):
    import codecs
    open = codecs.open

setup(
    name='django-mauveinternet',
    version='1.0.1',
    description="A collection of extensions for Django developed by Mauve Internet",
    long_description=open('README.rst', encoding='utf8').read(),
    author='Daniel Pope',
    author_email='dan@mauveinternet.co.uk',
    url='http://pypi.python.org/pypi/django-mauveinternet',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Pillow>=2.3,<2.4',
        'Markdown>=2.6,<2.7'
    ],
)
