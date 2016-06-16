from setuptools import setup

setup(
    name="workqueue",
    packages=['workqueue'],
    version='0.1.0',
    description='Master/Worker implementation of a Task Queue',
    author='Jesus Martinez',
    author_email='jesus.a.martinez.v@gmail.com',
    classifiers=[],
    download_url='https://github.com/adminMesfix/workqueue/tarball/0.1.0',
    url='https://github.com/adminMesfix/workqueue',
    keywords=['task', 'queue', 'master', 'worker', 'async', 'asynchronous'],
    install_requires=['pika']
)

