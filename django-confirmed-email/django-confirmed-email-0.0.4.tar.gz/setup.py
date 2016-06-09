from setuptools import setup
import os

package_path = os.path.normpath(os.path.join(os.path.abspath(__file__), os.path.pardir))
os.chdir(package_path)

with open('README.rst') as rm:
    README = rm.read()

confirmed_email_data = [
    'templates/confirmed_email/address_confirmed.html',
    'templates/confirmed_email/confirmation_email.txt',
    'templates/confirmed_email/confirmation_required.html'
]

setup(
    author="Jivan Amara",
    author_email='Development@JivanAmara.net',
    url='https://github.com/JivanAmara/confirmed-email',
    name='django-confirmed-email',
    version='0.0.4',
    packages=['confirmed_email'],
    package_data={'confirmed_email': confirmed_email_data},
    description='Provides an email sender that automatically confirms addresses.',
    long_description=README,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ]
)
