from setuptools import setup, find_packages

setup(
    name='hsq',
    version='1.0.2',
    packages=find_packages(),
    package_data={'': ['carddefs.xq', 'hs.xq', 'hsq.xq']},
    author='Ed Kellett',
    zip_safe=False,
    install_requires=[
        'blessings',
        'clize',
        'hearthstone',
        'tabulate'
    ],
    entry_points={
        'console_scripts': ['hsq = hsq.hsq:_main']
    }
)
