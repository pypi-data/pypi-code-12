try:
    from setuptools import setup
except ImportError:
    from disutils.core import setup

setup(
    name='chargehound',
    version='1.0.3',
    author='Chargehound',
    author_email='support@chargehound.com',
    packages=['chargehound'],
    description='Chargehound Python Bindings',
    url='https://www.chargehound.com',
    license='MIT',
    test_suite='test.all',
    install_requires=[
        'requests'
        ],
    )
