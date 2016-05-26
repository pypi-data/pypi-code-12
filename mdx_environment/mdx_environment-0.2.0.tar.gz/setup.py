##
# BSD 3-clause licence
#
# Copyright (c) 2015, Andrew Robinson
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the names of python-md-showable AND/OR mdx_showable nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

## Following line updated by util/set-version script, DO NOT EDIT
version='0.2.0'

from distutils.core import setup
setup(
  name = 'mdx_environment',
  packages = ['mdx_environment'],
  version = version,
  description = 'Python Markdown plugin to insert content and show hide sections based on environment variables',
  author = 'Andrew Robinson',
  author_email = 'andrewjrobinson+pypi@gmail.com',
  url = 'https://github.com/andrewjrobinson/python-md-environment',
  download_url = 'https://github.com/andrewjrobinson/python-md-environment/tarball/v%s'%version,
  install_requires=[
    'markdown',
    ],
  keywords = ['markdown', 'extension', 'environment', 'variable', 'showable', 'sections'],
  classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 2.7",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Topic :: Text Processing :: Markup",
    "Topic :: Text Processing :: Markup :: HTML",
    "Topic :: Software Development :: Documentation",
    ],
)
