from setuptools import setup

readme=open('README.rst').read()

setup(
    name='txtulip',
    version='0.1.0',
    description='',
    long_description=readme,
    author='Itamar Turner-Trauring',
    author_email='itamar@itamarst.org',
    maintainer='Thomas Grainger',
    maintainer_email='txtulip@graingert.co.uk',
    license="MIT",
    url='https://github.com/graingert/txtulip',
    packages=['txtulip', 'twisted.plugins'],
    namespace_packages=['twisted.plugins'],
    install_requires=[
        "twisted"
    ],
)
