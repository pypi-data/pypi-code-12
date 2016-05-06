from setuptools import setup

setup(
    name='eureka_template',
    version='0.0.4',
    description='Eureka Templating Library',
    author='Jorge Dias',
    author_email='jorge@mrdias.com',
    packages=['eureka_template'],
    scripts=['bin/eureka-template'],
    install_requires=[
        'eureka-client>=0.6.2',
        'jinja2'
    ]
)
