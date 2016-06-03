"""Setup tools for PastaSauce."""

from setuptools import setup, find_packages

setup(
    name='pastasauce',
    version='0.1.10',
    packages=find_packages(),
    scripts=[],
    # zip_safe=True,
    # eager_resources=[],
    install_requires=[],
    # dependency_links=[],
    # namespace_packages=[],
    include_package_data=True,
    # exclude_package_data=True,
    package_data={
        '': ['*.txt', '*.rst', '*.md'],
    },
    # entry_points={},
    # extras_require={},
    # setup_requires=[],
    # use_2to3=True,
    # convert_2to3_doctests=[],
    # use_2to3_fixers=[],
    author='OpenStax QA',
    author_email='greg@openstax.org',
    description='Sauce Labs interface for Python 3 exposing more of the SLAPI',
    license='Creative Commons Attribution 4.0 International Public License',
    keywords='',
    url='https://github.com/gregfitch/pastasauce',
    # long_description=open('./README.md').read(),
    # test_suite=''
    # tests_require=[],
    # test_loader='',
)
