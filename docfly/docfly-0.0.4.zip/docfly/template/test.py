#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2
from dataIO import textfile
from docfly.packages.member import Module, Package
from docfly.doctree import Article

pkg = Package("docfly")
print(jinja2.Template(textfile.read("package.tpl")).render(package=pkg))
print(jinja2.Template(textfile.read("module.tpl")).render(module=pkg["zzz_manual_install"]))

article=Article(title="Hello World", path="hello-world/index.rst")
print(jinja2.Template(textfile.read("index.tpl")).render(article_list=[article,], has_toc=True))
