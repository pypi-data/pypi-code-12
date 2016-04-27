#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=2 et sw=2 sts=2
#
# Copyright © 2016 Mohammad Amin Sameti <mamins1376@gmail.com>
#
# Distributed under terms of the GNU General Public License v3 LICENSE
# see LICENSE for details.

"""
PyBehnevis: a simple dependency-free wrapper for Behnevis API, which is
provided at http://www.behnevis.com/api.html as well.
"""

from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PyBehnevis(object):
  """
  main class, contains methods for communication with Behnevis API.

  example usage:
  behnevis = PyBehnevis()
  behnevis.convert('sedaye aab miayad, magar dar nahr tanhaei che mishooyand?')
  behnevis.convert('lebas lahzeha pak ast.')
  """

  API_URL = 'http://www.behnevis.com/php/convert.php'
  ENCODING = 'UTF-8'
  HEADERS = {
      "User-Agent":    "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
      "Content-Type":  "application/x-www-form-urlencoded"
      }

  def convert(self, text):
    """
    convert Finglish(or whatever you'd like to call) to Persian.
    gets and returns string.
    """

    url = self.API_URL
    encoding = self.ENCODING
    headers = self.HEADERS

    data = urlencode({
      'farsi': str(text)
      }).encode(encoding)

    request = Request(url=url,data=data,headers=headers)

    response = urlopen(request)

    result = response.read()

    response_encoding = response.headers['Content-Type']
    response_encoding = response_encoding[response_encoding.find('=')+1:]
    result = result.decode(response_encoding)

    # a simple fix
    result = result.replace('\ufeff','')[:-1]

    return result

