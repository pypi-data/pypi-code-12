from setuptools import setup
import pywebgettext

setup(
    name='pywebgettext',
    version=pywebgettext.__version__,
    packages = ['pywebgettext'],
    author="Vincent MAILLOL",
    author_email="pywebgettext@gmail.com",
    description="Extract gettext strings from python template",
    long_description=open('README.rst').read(),
    url='http://github.com/maillol/pywebgettext',
 
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Internationalization"
    ],
 
    entry_points = {
        'console_scripts': [
            'pywebgettext = pywebgettext.__main__:main',
        ],
    },
    license="WTFPL"
)
