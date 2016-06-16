#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module analysis internal structure of any Python Package.
"""

from __future__ import print_function, unicode_literals
import os
from collections import OrderedDict
from docfly.packages.crosys import SP_PATH

TAB = "    "


class SubModuleNotFound(Exception):
    """Raise when sub module/package not found.
    """


class InValidModuleName(Exception):
    """Raise when module name is invalid.
    """


class InValidPackageName(Exception):
    """Raise when package name is invalid.
    """
    
    
class Module(object):
    """Represent a module object in Python. Typically it's ``module_name.py``.

    :param name: module base name, can't have "." in it.
    :type name: str

    :param parent: default None, parent package name, list of package
    :type parent: str
    """

    def __init__(self, name, parent=None):
        if "." in name:
            raise InValidModuleName
        self.name = name
        self.parent = parent

    @property
    def fullname(self):
        """Return full name with parent packages information.

        fullname = package_name1.package_name2. ... .module_name
        """
        if self.parent:
            return "%s.%s" % (self.parent, self.name)
        else:
            return self.name

    def __str__(self):
        tpl = "Module(name=%r, parent=%r, fullname=%r)"
        return tpl % (self.name, self.parent, self.fullname)

    def __repr__(self):
        return "Module(name=%r, parent=%r)" % (self.name, self.parent)


class Package(object):
    """Represent a package object in Python. It is a directory having a 
    ``__init__.py`` file.

	**中文文档**
	
    代表了Python中 ``package(包)`` 的抽象类。

    Package必须可以被import命令所导入, 换言之, 就是已经被成功安装了。

    Package的属性的解释:

    - name: 包名称
    - parent: 母包的名称
    - fullname: 包的全名, 带母包
    - sub_packages: 有序字典, {子包的名称: Package对象}
    - sub_modules: 有序字典, {子模块的名称: Module对象}
    """

    def __init__(self, name, parent=None):
        if "." in name:
            raise InValidPackageName
        self.name = name
        self.parent = parent
        self.sub_packages = OrderedDict()
        self.sub_modules = OrderedDict()
        
        # Find package directory full path
        if self.parent:
            package_dir = os.path.join(
                *([SP_PATH, ] + self.parent.split(".") + self.name.split("."))
            )
        else:
            package_dir = os.path.join(
                *([SP_PATH, ] + self.name.split("."))
            )
            if os.path.isfile(package_dir + ".py"):
                return
        
        # Walk through all sub packages and sub modules
        for basename in os.listdir(package_dir):
            abspath = os.path.join(package_dir, basename)

            # If it's a directory, see if there is a __init__.py file
            if os.path.isdir(abspath):

                # If it is a sub package, then analyze it
                if os.path.exists(os.path.join(abspath, "__init__.py")):
                    self.sub_packages[basename] = Package(
                        name=basename, parent=self.fullname)

            # If it's a file, see if it's a .py file
            else:
                fname, ext = os.path.splitext(basename)

                # If it is a sub module, then analyze it
                if (ext == ".py") and (fname != "__init__"):
                    self.sub_modules[fname] = Module(
                        name=fname, parent=self.fullname)

    @property
    def fullname(self):
        """Return full name with parent packages information.

        fullname = package_name1.package_name2. ... .package_name
        """
        if self.parent:
            return "%s.%s" % (self.parent, self.name)
        else:
            return self.name

    def __str__(self):
        tpl = "Package(\n{tab}name=%r, \n{tab}parent=%r, \n{tab}fullname=%r, \n{tab}sub_packages=%r, \n{tab}sub_modules=%r, \n)".format(
            tab=TAB)
        return tpl % (
            self.name, self.parent, self.fullname,
            list(self.sub_packages), list(self.sub_modules),
        )

    def __repr__(self):
        tpl = "Package(name=%r, parent=%r}"
        return tpl % (self.name, self.parent)

    def __getitem__(self, key):
        try:
            return self.sub_packages[key]
        except KeyError:
            try:
                return self.sub_modules[key]
            except KeyError:
                raise SubModuleNotFound(
                    "%r doesn't has sub module %r" % (self.fullname, key))

    def _tree_view_builder(self, indent=0, is_root=True):
        """Build a text to represent the package structure.
        """
        def pad_text(indent):
            return "    " * indent + "|---"

        lines = list()

        if is_root:
            lines.append(SP_PATH)

        lines.append("%s%s (%s)" %
                     (pad_text(indent), self.name, self.fullname))

        indent += 1

        # sub packages
        for pkg in self.sub_packages.values():
            lines.append(pkg._tree_view_builder(indent=indent, is_root=False))

        # __init__.py
        lines.append("%s%s (%s)" %
                     (pad_text(indent), "__init__.py", self.fullname))

        # sub modules
        for mod in self.sub_modules.values():
            lines.append("%s%s (%s)" %
                         (pad_text(indent), mod.name + ".py", mod.fullname))

        return "\n".join(lines)

    def show(self):
        """Pretty print the package structure.
        """
        print(self._tree_view_builder(0))

    def walk(self):
        """A generator that walking through all sub packages and sub modules.

        1. current package object (包对象)
        2. current package's name (当前包对象的名字)
        3. current package' fullname (当前包对象的全名)
        4. list of sub packages (所有子包)
        5. list of sub modules (所有模块)
        """
        yield (
            self,
            self.parent,
            self.fullname,
            list(self.sub_packages.values()),
            list(self.sub_modules.values()),
        )

        for pkg in self.sub_packages.values():
            for things in pkg.walk():
                yield things


#--- Unittest ---
if __name__ == "__main__":
    mod = Module("member", parent="docfly")
    pkg = Package("docfly")

    def test_Module():
        print(mod)
        print(repr(mod))

#     test_Module()

    def test_Package():
        print(pkg)
        print(repr(pkg))
        
        print(pkg["packages"])
        print(pkg["fly"])
        
#     test_Package()

    def test_Package_show():
        pkg.show()

#     test_Package_show()

    def test_Package_walk():
        for i in pkg.walk():
            print(i)

#     test_Package_walk()

    def test_module_like_package():
        pkg = Package("six")
        print(pkg)

#     test_module_like_package()