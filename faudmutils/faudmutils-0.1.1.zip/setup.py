from distutils.core import setup

setup(
    name='faudmutils',
    version='0.1.1',
    author='Michael Crawford',
    author_email='michaelcrawf2014@fau.edu',
    packages=['faudmutils'],
    url='http://pypi.python.org/pypi/FAUDMUtils/',
    license='LICENSE.txt',
    description='Collection of FAUs DM Utils',
    long_description=open('README.txt').read(),
    install_requires=[
        "scikit-learn >= 0.17",
        "pandas >= 0.17",
        'numpy',
    ],
)