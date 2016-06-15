from distutils.core import setup

# try:
    # import pypandoc
    # long_description = pypandoc.convert('README.md', 'rst')
# except(IOError, ImportError):
    # long_description = open('README.md').read()

long_description = open('README.md').read()
print(long_description)

setup(
    name='pyshellout',
    packages=['pyshellout'],  # this must be the same as the name above
    version='0.2.5',
    description='Thin convenience wrappers for shelling out commands easily from python',
    long_description=long_description,
    author='Chiel ten Brinke',
    author_email='ctenbrinke@gmail.com',
    url='https://github.com/Chiel92/python-shellout',  # use the URL to the github repo
    keywords=['pyshellout', 'shellout', 'shell', 'CLI'],  # arbitrary keywords
    classifiers=[],
)
