# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Dataflow SDK for Python setup configuration.

The Apache Beam Python SDK code can be found at:
https://github.com/apache/incubator-beam/tree/python-sdk/sdks/python
"""

import os
import platform
import setuptools


# Currently all compiled modules are optional  (for performance only).
# Cython is available on the workers, but we don't require it for development.
if platform.system() == 'Windows':
  # Windows doesn't always provide int64_t.
  cythonize = lambda *args, **kwargs: []
else:
  try:
    # pylint: disable=g-statement-before-imports,g-import-not-at-top
    from Cython.Build import cythonize
  except ImportError:
    cythonize = lambda *args, **kwargs: []


def get_apache_beam_sdk_version():
  global_names = {}
  execfile(os.path.normpath('./apache_beam/version.py'),
           global_names)
  return global_names['__version__']


# The versions for the Google package wrapping the Apache Beam SDK
# and the expected version of the Apache bundled code.
# The version strings are independent of each other and do not have to be equal.
# The version strings use PEP 440 (https://www.python.org/dev/peps/pep-0440/).
GOOGLE_CLOUD_DATAFLOW_VERSION = '0.3.0rc2'
APACHE_BEAM_SDK_VERSION = '0.3.0'


BUNDLED_SDK_CODE_VERSION = get_apache_beam_sdk_version()
if APACHE_BEAM_SDK_VERSION != BUNDLED_SDK_CODE_VERSION:
  raise RuntimeError(
      'The expected Apache Beam SDK version (%s) is different from '
      'the version of the bundled code from the apache_beam/ folder (%s). ' % (
          APACHE_BEAM_SDK_VERSION, BUNDLED_SDK_CODE_VERSION))


REQUIRED_PACKAGES = [
    'avro>=1.7.7',
    'dill>=0.2.5',
    'google-apitools>=0.5.2',
    'httplib2>=0.8',
    'mock>=1.0.1',
    'oauth2client>=2.0.1',
    'protorpc>=0.9.1',
    'python-gflags>=2.0',
    'pyyaml>=3.10',
    ]


LONG_DESCRIPTION = '''
Google distribution of Apache Beam SDK.

The Apache Beam Python SDK code can be found at:
https://github.com/apache/incubator-beam/tree/python-sdk/sdks/python
'''

setuptools.setup(
    name='google-cloud-dataflow',
    version=GOOGLE_CLOUD_DATAFLOW_VERSION,
    description='Google Cloud Dataflow SDK for Python',
    long_description=LONG_DESCRIPTION,
    url='https://cloud.google.com/dataflow/',
    author='Google, Inc.',
    author_email='dataflow-sdk@google.com',
    packages=setuptools.find_packages(),
    ext_modules=cythonize([
        '**/*.pyx',
        'apache_beam/coders/coder_impl.py',
        'apache_beam/runners/common.py',
        'apache_beam/utils/counters.py',
    ]),
    setup_requires=['nose>=1.0'],
    install_requires=REQUIRED_PACKAGES,
    test_suite='nose.collector',
    zip_safe=False,
    # PyPI package information.
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    license='Apache 2.0',
    keywords='google cloud dataflow apache beam',
    )
