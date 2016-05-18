import os
from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='hidash',
    version='0.1.8',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A Django app to generate google charts, excel and pdf straight from the database.',
    long_description=README,
    author='Devashish Sharma , Swapnil Tiwari',
    author_email='devashishsharma2302@gmail.com , swapniltiwari43@gmail.com',
    keywords = ['Chart', 'reports', 'Export', 'django', 'dashboard' , 'google charts' , 'excel' , 'pdf'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
install_requires=[
          'xlwt'
]
)
