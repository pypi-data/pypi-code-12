from setuptools import setup, find_packages

setup(
    name='datapub',
    version='0.0.1',
    description='Python bindings for datapub.io web API',
    author='Jeff Workman',
    author_email='jeff.workman@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='datapub',
    install_requires=['requests'],
    packages=['datapub'],
    zip_safe=False
)
