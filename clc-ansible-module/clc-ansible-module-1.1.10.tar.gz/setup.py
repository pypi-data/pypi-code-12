#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'clc-ansible-module',
          version = '1.1.10',
          description = '''Centurylink Cloud Ansible Modules''',
          long_description = '''Ansible extension modules which allow users to interact with Centurylink Cloud to define and manage cloud components.''',
          author = "CenturyLink Cloud",
          author_email = "WFAAS-LLFT@centurylink.com",
          license = 'CTL Corporate License',
          url = 'http://www.centurylinkcloud.com',
          scripts = ['scripts/clc_inv.py', 'scripts/clc_inv.pyc'],
          packages = ['clc_ansible_module'],
          py_modules = ['clc_inv'],
          classifiers = ['Development Status :: 3 - Alpha', 'Programming Language :: Python'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "clc-sdk==2.45" ],
          
          zip_safe=True
    )
