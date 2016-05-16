#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-member

import pkgutil
import importlib
import sys
import unittest

def unitdox(args):
    package_name = args[1]
    testcase_classes = import_unit_test_case(package_name)
    for class_item in testcase_classes: # type: class
        if class_item.__module__.startswith(package_name):
            print('{0} ({1})'.format(class_item.__name__, class_item.__module__))
            test_methods = [methods for methods in dir(class_item) if methods.startswith('test_')]
            for test_method in test_methods:
                print('\t{0}'.format(test_method.replace('_', ' ')))
            print('')

def import_unit_test_case(package_name):
    package_name = package_name
    package = importlib.import_module(package_name)

    for _, modname, _ in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + '.'):
        importlib.import_module(modname, __package__)

    return [cls for cls in unittest.TestCase.__subclasses__()]

def main():
    unitdox(sys.argv)

if __name__ == "__main__":
    main()
