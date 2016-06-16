from setuptools import setup

with open('README.rst') as f:
     readme = f.read()

try:
    from PIL import Image
    requirements = ['numpy']
except:
    requirements = ['numpy', 'Pillow']


setup(
    name="image2pyarray",
    version="0.0.6",
    packages=['image2pyarray'],
    description='load image',
    long_description=readme,
    url='https://github.com/',
    author='me',
    author_email='me@etwings.com',
    license='MIT',
    install_requires=requirements,
)
