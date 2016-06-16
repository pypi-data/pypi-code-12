#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import os
import shutil
import jinja2

try:
    from .packages.member import Package, Module
    from .template import template_collection as tc
except:
    from docfly.packages.member import Package, Module
    from docfly.template import template_collection as tc


class ApiReferenceDoc(object):
    """A class used to generate sphinx-doc api reference part.

    :param package_name: the importable package name
    :type package_name: string

    :param dst: default "_source", the directory you want to put doc files 
    :type dst: string

    :param ignore: default empty list, package, module prefix you want to ignored
    :type ignore: list of string

    **中文文档**

    如果你需要忽略一个包: 请使用 ``docfly.packages``
    如果你需要忽略一个模块: 请使用 ``docfly.zzz_manual_install`` 或 
    ``docfly.zzz_manual_install.py``
    """

    def __init__(self, package_name, dst="_source", ignore=[]):
        if "." in package_name:
            raise Exception("package_name has to be a root package.")

        self.package_name = package_name
        self.package = Package(package_name)
        self.dst = dst
        self.ignore = [i.replace(".py", "") for i in ignore]

    def fly(self):
        """Generate doc tree.
        """
        dst = self.dst  # create an temp alias

        try:
            os.mkdir(dst)
        except:
            pass

        # delete everything already exists
        package_dir = os.path.join(os.path.abspath(dst), self.package_name)
        try:
            shutil.rmtree(package_dir)
        except Exception as e:
            print("'%s' can't be removed! Error: %s" % (package_dir, e))

        # create .rst files
        for pkg, parent, fullname, sub_packages, sub_modules in self.package.walk():

            if not self.isignored(pkg):
                dir_path = os.path.join(*(
                    [dst, ] + fullname.split(".")
                ))
                init_path = os.path.join(dir_path, "__init__.rst")

                self.make_dir(dir_path)
                self.make_file(init_path, self.generate_package_content(pkg))

                for mod in sub_modules:
                    if not self.isignored(mod):
                        module_path = os.path.join(dir_path, mod.name + ".rst")
                        self.make_file(
                            module_path, self.generate_module_content(mod))

    def isignored(self, mod_or_pkg):
        """Find whether if we need include a :class:`docfly.packages.member.Package` or
        :class:`docfly.packages.member.Module`.

        **中文文档**

        根据全名判断一个包或者模块是否需要被ignore.
        """
        for pattern in self.ignore:
            if mod_or_pkg.fullname.startswith(pattern):
                return True
        return False

    def make_dir(self, abspath):
        """Make an empty directory.
        """
        try:
            os.mkdir(abspath)
            print("Made: %s" % abspath)
        except:
            pass

    def make_file(self, abspath, text):
        """Make a file with utf-8 text.
        """
        try:
            with open(abspath, "wb") as f:
                f.write(text.encode("utf-8"))
            print("Made: %s" % abspath)
        except:
            pass

    def generate_package_content(self, package):
        """Generate package.rst text content.

        ::

            {{ package_name }}
            ==================

            .. automodule:: {{ package_name }}
                :members:

            sub packages and modules
            ------------------------

            .. toctree::
               :maxdepth: 1

                {{ sub_package_name1 }} <{{ sub_package_name1 }}/__init__>
                {{ sub_package_name2 }} <{{ sub_package_name2 }}/__init__>
                {{ sub_module_name1}} <{{ sub_module_name1}}>
                {{ sub_module_name2}} <{{ sub_module_name2}}>

        """
        if isinstance(package, Package):
            return jinja2.Template(tc.package).render(package=package, isignored=self.isignored)
        else:
            raise Exception("%r is not a Package object" % package)

    def generate_module_content(self, module):
        """Generate module.rst text content.

        ::

            {{ module_name }}
            =================

            .. automodule:: {{ module_fullname }}
                :members:
        """
        if isinstance(module, Module):
            return jinja2.Template(tc.module).render(module=module)
        else:
            raise Exception("%r is not a Module object" % module)


if __name__ == "__main__":
    doc = ApiReferenceDoc("toppackage", dst="_source",
                          ignore=[
                              "toppackage.subpackage1",
                              "toppackage.module2.py",
                              "toppackage.subpackage2.module22.py",
                          ],
                          )
    doc.fly()
