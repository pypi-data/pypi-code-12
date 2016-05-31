from setuptools import setup


setup(
    name='djangorestframework-expander',
    version='0.1.3',
    description=('A serializer mixin for Django REST Framework to expand object representations inline'),
    author='Ryan Pineo',
    author_email='ryanpineo@gmail.com',
    license='MIT',
    url='https://github.com/silverlogic/djangorestframework-expander',
    packages=['expander'],
    install_requires=['djangorestframework'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
