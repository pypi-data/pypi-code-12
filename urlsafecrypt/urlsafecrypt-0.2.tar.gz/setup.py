from setuptools import setup


setup(
    name='urlsafecrypt',
    packages=['urlsafecrypt'],
    version='0.2',
    description='Provides Fernet based symmetric encryption of data whose '
    'output is safe to be used in URLs.',
    author='Fabian Topfstedt',
    author_email='topfstedt@schneevonmorgen.com',
    url='https://bitbucket.org/fabian/urlsafecrypt',
    keywords=['urlsafe', 'cryptography'],
    classifiers=[],
    install_requires=[
        'cryptography',
    ]
)
