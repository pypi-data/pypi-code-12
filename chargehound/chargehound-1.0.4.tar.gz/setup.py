try:
    from setuptools import setup
except ImportError:
    from disutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='chargehound',
    version='1.0.4',
    author='Chargehound',
    author_email='support@chargehound.com',
    packages=['chargehound'],
    description='Chargehound Python Bindings',
    long_description=long_description,
    url='https://www.chargehound.com',
    license='MIT',
    test_suite='test.all',
    install_requires=[
        'requests'
        ],
    )
