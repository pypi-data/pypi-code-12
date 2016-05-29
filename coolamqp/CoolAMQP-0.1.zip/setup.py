#!/usr/bin/env python
#coding=UTF-8
from distutils.core import setup

setup(name='CoolAMQP',
      version='0.1',
      description='The AMQP client library',
      author=u'Piotr Maślanka',
      author_email='piotrm@smok.co',
      url='https://github.com/piotrmaslanka/coolamqp',
      download_url='https://github.com/piotrmaslanka/coolamqp/archive/master.zip',
      keywords=['amqp', 'pyamqp', 'rabbitmq', 'client', 'network', 'ha', 'high availability'],
      packages=['coolamqp', 'coolamqp.backends'],
      install_requires=[
            "amqp"
      ]
     )