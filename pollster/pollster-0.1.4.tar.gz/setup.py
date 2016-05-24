from distutils.core import setup
import pollster

setup(
    name='pollster',
    version = pollster.__version__,
    packages = ['pollster'],
    description = "A Python wrapper for the Pollster API",
    long_description = "A Python wrapper for the Pollster API",
    license = 'MIT',
    author = 'Aaron Bycoffe',
    author_email = 'bycoffe@huffingtonpost.com',
    url='https://github.com/huffpostdata/python-pollster',
    download_url = 'https://github.com/huffpostdata/python-pollster/tarball/' + pollster.__version__,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
