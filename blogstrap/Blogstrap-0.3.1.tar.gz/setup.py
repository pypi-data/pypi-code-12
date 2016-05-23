# Copyright 2015 Joe H. Rahme <joehakimrahme@gmail.com>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""A dumb blogging platform based on Strapdown.js
"""

from setuptools import setup

repo_url = "http://github.com/joehakimrahme/blogstrap"

setup(
    name='Blogstrap',
    author="Joe H. Rahme",
    author_email="joehakimrahme@gmail.com",
    version='0.3.1',
    description="A dumb blogging platform based on Strapdown.js",
    url=repo_url,
    download_url=repo_url + "/tarball/0.3.1",
    long_description=__doc__,
    packages=['blogstrap'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'six'],

    entry_points={
        'console_scripts': [
            'blogstrap = blogstrap.blogstrap:main',
        ]
    }
)
