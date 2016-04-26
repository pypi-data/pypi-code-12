from setuptools import setup, find_packages

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.txt').read())

setup(
    name='more.forwarded',
    version='0.2',
    description="Forwarded header support for Morepath",
    long_description=long_description,
    author="Martijn Faassen",
    author_email="faassen@startifact.com",
    keywords='morepath forwarded',
    license="BSD",
    url="http://pypi.python.org/pypi/more.static",
    namespace_packages=['more'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'morepath > 0.13.2',
    ],
    extras_require=dict(
        test=[
            'pytest >= 2.0',
            'pytest-cov',
            'WebTest >= 2.0.14'
        ],
    ),
)
