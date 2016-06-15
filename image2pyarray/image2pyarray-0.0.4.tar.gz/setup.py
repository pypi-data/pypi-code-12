from setuptools import setup

with open('README.rst') as f:
     readme = f.read()

setup(
    name="image2pyarray",
    version="0.0.4",
    packages=['image2pyarray'],
    description='load image',
    long_description=readme,
    url='https://github.com/',
    author='me',
    author_email='me@etwings.com',
    license='MIT',
    install_requires=[
        'Pillow','numpy'
    ],
)
