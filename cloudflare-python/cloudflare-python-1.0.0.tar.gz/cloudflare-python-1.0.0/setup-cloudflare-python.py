#!/usr/bin/env python
"""CloudFlare API code - setup.py file"""

from setuptools import setup, find_packages

def main():
    """CloudFlare API code - setup.py file"""

    with open('README.rst') as read_me:
        long_description = read_me.read()

    setup(
        name='cloudflare-python',
        version='1.0.0',
        description='Python wrapper for the CloudFlare v4 API',
        long_description=long_description,
        author='Martin J. Levy',
        author_email='martin@cloudflare.com',
        # maintainer='Martin J. Levy',
        # maintainer_email='martin@cloudflare.com',
        url='https://github.com/cloudflare/python-cloudflare',
        license='MIT',
        packages=find_packages(),
        install_requires=['cloudflare', 'requests', 'future', 'pyyaml'],
        keywords='cloudflare',
        entry_points={},
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ]
    )

if __name__ == '__main__':
    main()
