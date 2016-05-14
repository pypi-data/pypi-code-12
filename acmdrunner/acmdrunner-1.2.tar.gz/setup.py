from setuptools import setup


setup(
    name='acmdrunner',
    version='1.2',
    description='Ascetic command runner. The most ease way'
    ' to power your python app with custom management commands',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers'
    ],
    url='https://github.com/sergeyglazyrindev/asceticcmdrunner',
    author='Sergey Glazyrin',
    author_email='sergey.glazyrin.dev@gmail.com',
    license='MIT',
    packages=['acmdrunner', ],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': ['nose', 'mock'],
    },
    test_suite='tests',
    keywords=['command', 'dispatch'],
    download_url='https://github.com/sergeyglazyrindev/'
    'asceticcmdrunner/tarball/1.2'
)
