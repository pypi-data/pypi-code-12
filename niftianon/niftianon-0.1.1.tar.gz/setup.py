from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='niftianon',
    version='0.1.1',
    packages=['niftianon'],
    zip_safe=True,
    author='Jon Stutters',
    author_email='j.stutters@ucl.ac.uk',
    description='Anonymiser for NIFTI images',
    long_description=readme(),
    url='https://github.com/jstutters/niftianon',
    include_package_data=True,
    install_requires=[
        'Click',
        'nibabel'
    ],
    entry_points='''
        [console_scripts]
        niftianon=niftianon.cli:anonymise
    ''',
    license='MIT',
    classifiers=[
    ]
)
