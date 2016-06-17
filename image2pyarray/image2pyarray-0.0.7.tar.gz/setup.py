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
    version="0.0.7",
    packages=['image2pyarray'],
    description='load image easily',
    long_description=readme,
    url='https://github.com/image2pyarray/image2pyarray',
    author='me',
    author_email='me@nsa.gov',
    license='MIT',
    install_requires=requirements,
)
