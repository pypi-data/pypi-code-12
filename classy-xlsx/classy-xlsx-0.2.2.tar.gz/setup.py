import os

from setuptools import setup


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='classy-xlsx',
    version='0.2.2',
    packages=['classy_xlsx'],
    license='BSD License',
    description='The package allows you to create xlsx files in style models Django ORM.',
    long_description=README,
    url='https://github.com/suguby/classy_xlsx',
    author='Shandrinov Vadim',
    author_email='suguby@gmail.com',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'XlsxWriter==0.8.7',
        # 'bunch==1.0.1',
    ]
)
