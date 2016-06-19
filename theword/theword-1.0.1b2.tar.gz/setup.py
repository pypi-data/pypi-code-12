from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='theword',
    author='Jim Haughwout',
    author_email='haughwout@alum.mit.edu',
    description='Humor inspired by `import this` and _The Trashmen_',
    url='https://github.com/JimHaughwout/theword',
    download_url = 'https://github.com/JimHaughwout/theword/tarball/1.0.1b2', 
    version='1.0.1b2',
    packages=['theword', ],
    package_dir={'theword':'theword'},
    license='MIT',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment'
    ],
)