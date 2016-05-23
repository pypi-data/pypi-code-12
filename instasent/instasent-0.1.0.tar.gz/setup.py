from setuptools import setup

setup(
    name='instasent',
    packages=['instasent'],
    version='0.1.0',
    description="Instasent's REST API",
    author='Instasent',
    author_email='support@instasent.com',
    url='https://github.com/instasent/instasent-python-lib',
    download_url='https://github.com/instasent/instasent-python-lib/archive/master.zip',
    keywords=['instasent', 'sms'],
    install_requires=['requests'],
)
