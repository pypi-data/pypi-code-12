from distutils.core import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst', format='md')
except ImportError:
    #print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='ksmtp',
    version='0.2.7',
    author='Kenneth Burgener',
    author_email='kenneth@oeey.com',
    scripts=['bin/ksmtp'],
    packages=['ksmtp'],
    data_files=[('/etc/', ['config/ksmtp.conf'])],
    url='http://pypi.python.org/pypi/ksmtp/',
    license='LICENSE.txt',
    description='Simple Python SMTP relay replacement for sendmail with SSL authentication',
    long_description=read_md('README'),
)
