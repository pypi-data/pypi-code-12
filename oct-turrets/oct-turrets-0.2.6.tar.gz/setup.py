from setuptools import setup

from oct_turrets import __version__

setup(
    name='oct-turrets',
    version=__version__,
    author='Emmanuel Valette',
    packages=['oct_turrets'],
    include_package_data=True,
    description='Client tester part for oct',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
    ],
    install_requires=[
        'pyzmq',
        'six'
    ],
    entry_points={'console_scripts': [
        'oct-turrets-start = oct_turrets.start_turret:main'
    ]},
)
