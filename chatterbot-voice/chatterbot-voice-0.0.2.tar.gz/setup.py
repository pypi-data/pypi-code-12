#!/usr/bin/env python

from setuptools import setup


# Dynamically retrieve the version information from the chatterbot module
version = __import__('chatterbot_voice').__version__
author = __import__('chatterbot_voice').__author__
author_email = __import__('chatterbot_voice').__email__

req = open('requirements.txt')
requirements = req.readlines()
req.close()

setup(
    name='chatterbot-voice',
    version=version,
    url='https://github.com/gunthercox/chatterbot_voice',
    description='A voice interface adapter for ChatterBot.',
    author=author,
    author_email=author_email,
    packages=[
        'chatterbot_voice'
    ],
    package_dir={'chatterbot_voice': 'chatterbot_voice'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=True,
    platforms=['any'],
    keywords=['ChatterBot', 'chatbot', 'chat', 'bot', 'speech', 'voice'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=[]
)
