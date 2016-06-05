try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="nectar",
    description="Helper Library for the Modern Propulsion ESCs",
    version=0.1,
    author="Brian Celenza",
    author_email="bcelenza@gmail.com",
    url="https://bitbucket.org/modernpropulsion/nectar",
    packages=['nectar'],
    license="MIT",
    long_description="",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals :: Serial',
    ],
    platforms='any',
    scripts=[],
	install_requires=[
		'pyserial',
	],
)
