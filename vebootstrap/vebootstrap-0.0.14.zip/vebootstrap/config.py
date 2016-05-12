# -*- coding: utf-8 -*-
import os
import sys
import codecs
import json


try:
    str = unicode
except:
    pass


class Config(object):
    FILENAME = os.path.join(os.path.expanduser("~"), ".vebootstrap")
    DEFAULT_SETTINGS = {
            "default_packages": ["ipython"],
            "default_windows_packages": []
            }

    def __init__(self):
        self.init()
        self.load()

    def save(self):
        pass

    def init(self):
        if not os.access(self.FILENAME, os.F_OK) or os.stat(self.FILENAME).st_size == 0:
            with codecs.open(self.FILENAME, "wb", encoding="utf-8") as fp:
                fp.write(json.dumps(self.DEFAULT_SETTINGS, indent=4))

    def assert_value(self, json_value):
        assert_type("config json", json_value, dict)

        default_packages = json_value.get('default_packages', [])
        assert_type("default_packages", default_packages, list)
        assert_sequence("default_packages", default_packages, str)

        default_windows_packages = json_value.get('default_windows_packages', [])
        assert_type("default_windows_packages", default_windows_packages, list)
        assert_sequence("default_windows_packages", default_windows_packages, str)

    def load(self):
        try:
            j = json.loads(codecs.open(self.FILENAME, "rb", encoding="utf-8").read())
        except ValueError as e:
            sys.stderr.write(u"Loading config failed: {0}\n".format(self.FILENAME))
            raise e

        self.assert_value(j)
        self.default_packages = j.get('default_packages', [])
        self.default_windows_packages = j.get('default_windows_packages', [])


def assert_type(name, value, type_assertion):
    if not isinstance(value, type_assertion):
        raise TypeError("{0} must be {1} (found: {2})".format(name, type_assertion, value))


def assert_sequence(sequence_name, sequence, type_assertion):
    for element in sequence:
        assert_type("item in {0}".format(sequence_name), element, type_assertion)


def assert_dict(dictionary_name, dictionary, key_type_assertion, value_type_assertion):
    for key, value in dictionary:
        key_type_assertion and assert_type("key in {0}".format(dictionary_name), key, key_type_assertion)
        value_type_assertion and assert_type("value in {0}".format(dictionary_name), value, value_type_assertion)

