from setuptools import setup

setup(
    name='dash.ly',
    version='0.11.4',
    author='chris p',
    author_email='chris@plot.ly',
    packages=['dash'],
    license='MIT',
    description='',
    long_description=open('README.md').read(),
    install_requires=['flask', 'plotly', 'flask-cors']
)
