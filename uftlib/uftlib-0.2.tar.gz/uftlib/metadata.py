# -*- coding: utf-8 -*-
"""
Did you know that django.template cannot get an element from a dict by a key
which is another variable without using a custom defined filter?
Did you know that tornado.template reinvents some control loops and
other logical statements?
Did you know that mako templates are a completely new language?

Fear no more! You can use python code, python eval and string.Template to
create a fast and flexible templating engine.
"""

# The package name, which is also the "UNIX name" for the project.
package = 'uftlib'
project = "Ultra Fast Template Library"
project_no_spaces = project.replace(' ', '')
version = '0.2'
description = 'Uses python eval, string.Template to generate text very fast.'
authors = ['Tudor Aursulesei']
authors_string = ', '.join(authors)
emails = ['thestick613@gmail.com']
license = 'GPL'
copyright = '2015 ' + authors_string
url = 'https://github.com/thestick613/uftlib'
