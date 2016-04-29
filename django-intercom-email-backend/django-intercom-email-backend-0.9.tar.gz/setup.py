
from setuptools import setup, find_packages


setup(
    name='django-intercom-email-backend',
    version='0.9',
    url='https://github.com/cravefood/django-intercom-email-backend',
    author='Sergio Oliveira',
    author_email='seocam@seocam.com',
    description='Intercom email backend for Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['django',
                      'python-intercom'],
)
