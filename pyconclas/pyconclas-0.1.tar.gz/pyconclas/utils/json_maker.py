#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import sys

from pyconclas.exceptions.client_exceptions import (
    ContentsKeyException, URLInvalidException, JsonKeysException, 
    ParameterTypeError, EmptyParameterException, DocMinException,
    DocMaxException)


REGEX = re.compile(
    r'(^(https?:\/\/(?:www\.|(?!www))|(www\.?))' # http(s)://(www) or www.
    r'[\w-]+\.[\w]+|' # domain
    r'(?!w)[\w-]+\.[\w]+)', # mywebsite.com
    re.IGNORECASE)


class JsonMaker(object):
    def __init__(self, dict_data):
        self._dict_data = dict_data

    def _validate_contents(self):
        """
            Definition:
                Checks that the key "contents" there is the key "doc" in
                "url" at the same time
        """
        keys_contents = self._dict_data["contents"]

        for item in keys_contents:
            if len(item) == 0:
                raise ContentsKeyException("It's dict has nothing")
            if "url" in item:
                if is_str_empty(item["url"]):
                    raise EmptyParameterException(
                        "The parameter 'url' needs a value")
            if "url" in item and "doc" in item:
                raise ContentsKeyException(
                    "There can be the key doc and url in the same dictionary")
            if "doc" in item:
                if len(item["doc"]) == 0:
                    raise ContentsKeyException("Key contents invalid")
                else:
                    self._validate_key_doc(item["doc"])
        return True

    def _validate_key_doc(self, key_doc):
        """
            Params:
                key_doc:: Key doc to be analyzed

            Definition:
                Verify nodes of node "doc" are valid.

            Returns:
                Return true if this node is valid.
        """
        for key, value in key_doc.items():
            condition = (
                key != "short_text" and 
                key != "long_text" and 
                key != "brands")
            if condition:
                raise ContentsKeyException('Invalid key "doc".')
            if type(value) is not str:
                raise ParameterTypeError(
                    'Node type error: "{0}":{1}'.format(key, value))
            if is_str_empty(value):
                raise EmptyParameterException(
                    "The parameter '{0}' needs a value".format(key))

        if "short_text" in key_doc and "long_text" in key_doc:
            doc_len = (len(key_doc["short_text"]) + 
                        len(key_doc["long_text"]))
            if doc_len < 25:
                raise DocMinException("The doc is not valid.")
        if "short_text" in key_doc:
            if len(key) > 1000:
                raise DocMaxException("The short_text doc is not valid.")
        if "long_text" in key_doc:
            if len(key) > 20000:
                raise DocMaxException("The long_text doc is not valid.")
        if "brands" in key_doc:
            if len(key) > 5000:
                raise DocMaxException("The brands doc is not valid.")

    def _check_urls(self):
        """
            Definition:
                Check if exists "callback" and "url" keys on dict and check
                if are valid

            Returns:
                Returns true if urls in keys of json is valide.
        """
        if "callback" in self._dict_data:
            if not re.match(REGEX, self._dict_data["callback"]):
                raise URLInvalidException("Invalid url callback")

        for item in self._dict_data["contents"]:
            if "url" in item:
                if not re.match(REGEX, item["url"]) or len(item["url"]) > 2083:
                    raise URLInvalidException(
                        "Invalid url {0}".format(item["url"]))
        return True

    def get_json(self):
        """
            Definition:
                Check if json is valid
            Returns:
                Retuns a string full json to do request
        """
        self._validate_contents()
        self._check_urls()
        return json.dumps(self._dict_data)

def is_str_empty(string):
    return string.isspace() or not string
