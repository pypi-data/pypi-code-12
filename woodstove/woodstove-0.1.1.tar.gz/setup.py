from setuptools import setup, find_packages
import woodstove

requires=['bottle', 'six']

setup(
    name='woodstove',
    version=woodstove.__version__,
    description='A framework for writing HTTP service APIs',
    author=woodstove.__author__,
    author_email='richard.marshall@iacpub.com',
    url='https://github.com/richardmarshall/woodstove',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    requires=requires,
    install_requires=requires,
    extras_require={'db': ["peewee"]},
    packages=find_packages(),
)
