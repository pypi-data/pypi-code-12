from setuptools import setup, find_packages

VERSION = '0.0.1'

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

setup(
    name="mkdocs-cluster",
    version=VERSION,
    classifiers=CLASSIFIERS,
    url='https://gitlab.com/kaliko/mkdocs-cluster',
    license='BSD',
    description='Another bootstrap theme for MkDocs',
    author='kaliko jack',
    author_email='kaliko@azylum.org',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'cluster = mkdocs_cluster',
        ]
    },
    zip_safe=False
)
