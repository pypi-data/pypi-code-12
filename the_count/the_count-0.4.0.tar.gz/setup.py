from setuptools import setup, find_packages

setup(
    name = 'the_count',
    version = '0.4.0',
    description = 'Handy class for counting things',
    author = 'Brian Lauber',
    author_email = 'constructible.truth@gmail.com',
    packages = find_packages(exclude = ["tests"]),
    install_requires = [],
    test_suite = 'tests',
    tests_require = ["pytest>=2.8.2"]
)
