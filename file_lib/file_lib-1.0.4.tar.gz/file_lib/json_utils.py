# -*- coding: utf-8 -*-
import json
import codecs


def read_json_file(file_path, encoding='utf-8'):
    with codecs.open(file_path, 'r', encoding) as json_file:
        return json.load(json_file)


def write_json_file(file_path, data, encoding='utf-8'):
    with codecs.open(file_path, 'w', encoding) as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
