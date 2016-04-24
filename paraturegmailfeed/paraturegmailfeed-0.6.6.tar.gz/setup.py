from setuptools import setup


setup(
    name='paraturegmailfeed',
    version='0.6.6',
    description='ETL for Parature emails routed to Gmail account',
    url='https://github.com/joelcolucci/paraturegmailfeed',
    author='Joel Colucci',
    author_email='joelcolucci@gmail.com',
    license='MIT',
    packages=['paraturegmailfeed', 'paraturegmailfeed.paratureaction'],
    install_requires=[
        'google-api-python-client',
        'gmailresthandler',
        'pymongo'
    ],
    zip_safe=False
)
