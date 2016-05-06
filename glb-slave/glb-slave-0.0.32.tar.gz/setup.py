from setuptools import setup, find_packages


setup(
    name='glb-slave',
    description='GLB slave client.',
    version='0.0.32',
    author='Lain',
    author_email='softliunaisen@gmail.com',
    url='https://pypi.python.org/pypi/glb-slave/',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'glb_slave=glb_slave:process'
        ]
    },
    install_requires=['click', 'websocket-client', 'Jinja2'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
