from setuptools import setup, find_packages


setup(
    name='glb',
    description='Guokr load balancing.',
    version='0.0.51',
    author='Aliao',
    author_email='aliao0019@gmail.com',
    url='https://pypi.python.org/pypi/glb/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'glb=glb:manage'
        ]
    },
    install_requires=['Flask', 'click', 'Jinja2',
                      'Flask-RESTFUL', 'jsonschema',
                      'gevent-websocket', 'Flask-Redis',
                      'functools32'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
