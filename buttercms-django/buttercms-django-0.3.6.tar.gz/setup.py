import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst', 'r') as f:
    readme = f.read()

packages = [
    'buttercms-django'
]

install_requires = []
if sys.version_info < (2, 7, 9):
    raise Exception('ButterCMS uses the requests library to securely talk to https://buttercms.com '
        'which requires Python 2.7.9 or later.\n'
        'Please take a few seconds to upgrade to Python 2.7.9 and try again.\n'
        'https://www.python.org/downloads/')
    # TODO: Add support for < Python 2.7.9
    # install_requires.append('requests[security]')
else:
    install_requires.append('requests')


setup(name='buttercms-django',
        version='0.3.6',
        description='Company blogs as a service. Built for developers.',
        long_description=readme,
        url='https://buttercms.com',
        author='ButterCMS',
        author_email='jake@buttercms.com',
        license='MIT',
        packages=packages,
        install_requires=install_requires,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Environment :: Web Environment',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Framework :: Django',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
        ],
        keywords='django blog service',
        include_package_data=True,
        zip_safe=False)