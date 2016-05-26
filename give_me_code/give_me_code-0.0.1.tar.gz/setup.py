from setuptools import setup

setup(
    name='give_me_code',
    version='0.0.1',
    py_modules=['give_me_code'],
    install_requires=["flask"],
    url='https://github.com/winkidney/GiveMeCode',
    license='MIT',
    author='winkidney',
    author_email='winkidney@gmail.com',
    description='Return http response with any error code you want.'
)
