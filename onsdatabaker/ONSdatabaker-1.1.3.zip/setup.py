from setuptools import setup, find_packages

long_desc = """
Transform Excel spreadsheets
"""
# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for classifiers

conf = dict(
    name='ONSdatabaker',
    version='1.1.3',
    description="Excel Output Transformation",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
    keywords='',
    author='Office for National Statistics',
    author_email='michael.adams@ons.gsi.gov.uk',
    url='http://github.com/ONS-OpenData/ONSdatabaker/',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=['docopt', 'xypath>=1.0.12', 'xlutils', 'pyhamcrest'],
    tests_require=[],
    entry_points={
        'console_scripts': [
            'bake = ONSdatabaker.bake:main',
            'sortcsv = ONSdatabaker.sortcsv:main'
        ]
    })

if __name__ == '__main__':
    setup(**conf)
