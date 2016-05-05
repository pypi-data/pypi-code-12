from setuptools import setup


install_requires = [
    'Jinja2==2.8',
    'MarkupSafe==0.23',
    'Twisted==16.1.1',
    'cffi==1.6.0',
    'cryptography==1.3.1',
    'enum34==1.1.4',
    'feedparser==5.2.1',
    'flake8==2.5.4',
    'idna==2.1',
    'ipaddress==1.0.16',
    'mccabe==0.4.0',
    'pep8==1.7.0',
    'pyOpenSSL==16.0.0',
    'pyasn1==0.1.9',
    'pycparser==2.14',
    'pyflakes==1.0.0',
    'requests==2.10.0',
    'six==1.10.0',
    'wsgiref==0.1.2',
    'zope.interface==4.1.3',
    'service-identity==16.0.0',
    'pyasn1-modules==0.0.8',
    'attr==0.1.0',
    'attrs==15.2.0'
]


version = '0.2'

setup(
    name='rssmailer',
    version=version,
    description="RSS Digest Emailer",
    author='Arun S',
    author_email='arun@indeliblestamp.com',
    url='https://tools.indeliblestamp.com',
    license='GPL',
    install_requires=install_requires,
    scripts=['rssmailer/rss_mailer.py'],
    packages=['rssmailer'],
    package_data={
        'sample': ['rssmailer/rssemailer.json.sample'],
        'reqs': ['requirements.txt'],
     },
)
#    include_package_data=True,
#    zip_safe=False,
