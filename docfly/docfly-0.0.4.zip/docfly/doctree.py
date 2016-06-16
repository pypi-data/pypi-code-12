#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function
import os
import jinja2
try:
    from .packages.dataIO import textfile
    from .template import template_collection as tc
except:
    from docfly.packages.dataIO import textfile
    from docfly.template import template_collection as tc


class Article(object):
    def __init__(self, title, path):
        self.title = title
        self.path = path


class DocTree(object):
    """A DocTree structure following
    :ref:`Sanhe Sphinx standard <Sanhe_sphinx_doc_project_style_guide>`.
    """
    def __init__(self, dir_path):
        if self.is_doc_dir(dir_path) is False:
            raise Exception
        self.dir_path = dir_path

    @staticmethod
    def is_doc_dir(dir_path):
        """
        
        **中文文档**
        
        检测该目录是否符合 :ref:`Sanhe Sphinx 文档标准 <Sanhe_sphinx_doc_project_style_guide>`:
        
        - 文件目录下是否有一个 ``content.rst`` 文件。
        """
        if os.path.exists(os.path.join(dir_path, "content.rst")):
            return True
        else:
            return False

    @staticmethod
    def get_doc_dir_list(dir_path):
        """
        
        **中文文档**
        
        获得文件夹中的所有子文档文件夹, 使用 :meth:`DocTree.is_doc_dir` 中的
        判断准则。
        """
        dir_list = list()
        for path in os.listdir(dir_path):
            abspath = os.path.join(dir_path, path)
            if DocTree.is_doc_dir(abspath):
                dir_list.append(abspath)
        return dir_list

    @staticmethod
    def get_title(abspath):
        """
        
        **中文文档**
        
        从一个.rst文件中, 找到顶级标题。也就是第一个 ``====`` 上面一行。如果没有
        ``====``, 那么 ``----`` 也行。
        """
        lastline = None
        for line in textfile.readlines(abspath, strip="both"):
            if (line == "=" * len(line)) and (len(line) >= 1):
                return lastline.strip()
            else:
                lastline = line
        
        lastline = None
        for line in textfile.readlines(abspath, strip="both"):
            if (line == "-" * len(line)) and (len(line) >= 1):
                print("Warning, this document doesn't have '======' header, "
                      "But having a `------` header!")
                return lastline.strip()
            else:
                lastline = line

        return None
        
    @staticmethod
    def process(dir_path, table_of_content_header):
        """
        
        **中文文档**
        
        处理一个文件夹。
        """
        article_list = list()

        for sub_dir_path in DocTree.get_doc_dir_list(dir_path):
            abspath = os.path.join(sub_dir_path, "content.rst")
            title = DocTree.get_title(abspath)
            path = os.path.basename(sub_dir_path) + "/index.rst"
            article = Article(title=title, path=path)
            article_list.append(article)

        content = jinja2.Template(tc.index).\
            render(
                article_list=article_list, 
                has_toc=len(article_list) >= 1,
                table_of_content_header=table_of_content_header)
        
        abspath = os.path.join(dir_path, "index.rst")
        textfile.write(content, abspath)
        print("Made: %s" % abspath)
        
    def fly(self, table_of_content_header="Table of Content (目录)"):
        for current_dir, dir_list, file_list in os.walk(self.dir_path):
            if self.is_doc_dir(current_dir):
                self.process(current_dir, table_of_content_header)