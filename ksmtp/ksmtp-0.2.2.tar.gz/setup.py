from distutils.core import setup

setup(
    name='ksmtp',
    version='0.2.2',
    author='Kenneth Burgener',
    author_email='kenneth@oeey.com',
    scripts=['bin/ksmtp'],
    packages=['ksmtp'],
    data_files=[('/etc/', ['config/ksmtp.conf'])],
    url='http://pypi.python.org/pypi/ksmtp/',
    license='LICENSE.txt',
    description='Simple Python SMTP relay replacement for sendmail with SSL authentication',
    long_description=open('README').read(),
)
