import os
from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
install_reqs = parse_requirements(req_path, session=False)

req_path = os.path.join(os.path.dirname(__file__), 'test-requirements.txt')
test_reqs = parse_requirements(req_path, session=False)

reqs = [str(ir.req) for ir in install_reqs]
treqs = [str(ir.req) for ir in test_reqs]


setup(
    name='pydiecalc',
    version='0.1.1',
    author='Justin Hammond',
    author_email='justin@roaet.com',
    description='python RPG Dice Parser and calculator',
    url='https://github.com/roaet/pydiecalc',
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'pydiecalc = pydiecalc.client:main'
        ],
    }
)
