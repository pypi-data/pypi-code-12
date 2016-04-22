#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exvocabulary import ExVocabulary
import unittest
import sys
try:
    import simplejson as json
except ImportError:
    import json


class TestModule(unittest.TestCase):
    """Checks for the sanity of all module methods"""

    def test_synonym_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.synonym("repudiate")
        result = '{"verb": ["renounce", "decline", "deny", "refuse", "reject"]}'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_synonym_not_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.synonym("sxsw")
        self.assertFalse(current_result)

    def test_antonym_valid_phrase_1(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.antonym("love")
        result = '{"verb": ["hate"], "noun": ["hate"]}'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_antonym_valid_phrase_2(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.antonym("respect")
        result = '{"verb": ["disesteem", "disrespect"], "noun": ["disesteem", "disrespect"]}'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_antonym_not_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.antonym("sxsw")
        self.assertFalse(current_result)

    def test_partOfSpeech_valid_phrase_1(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.part_of_speech("hello")
        result = '[{"text": "interjection", "example:": "Used to greet someone, answer the telephone, or express surprise.", "seq": 0}]'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_partOfSpeech_valid_phrase_2(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.part_of_speech("rapidly")
        result = '[{"text": "adverb", "example:": "With speed; in a rapid manner.", "seq": 0}]'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_partOfSpeech_not_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.part_of_speech("sxsw")
        self.assertFalse(current_result)

    def test_usageExamples_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.vocabulary_example("hillock")
        result = '[{"corpus": "New York Times", "seq": 0, "sentence": "The most immediately captivating of Mr. Sachs\u2019s works is a small, cylindrical fish pond surrounded by a sloping plywood construction, like a flagstone-covered hillock."}, {"corpus": "BBC", "seq": 1, "sentence": "Wakass Haruf taught at Birmingham\'s Golden Hillock Academy - one of the schools caught up in the so-called Trojan Horse affair."}, {"corpus": "BBC", "seq": 2, "sentence": "Nansen Primary and Golden Hillock were also put into special measures."}]'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_usageExamples_not_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.usage_example("lksj")
        self.assertFalse(current_result)

    def test_hyphenation_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.hyphenation("hippopotamus")
        result = '[{"seq": 0, "text": "hip", "type": "secondary stress"}, {"seq": 1, "text": "po"}, {"seq": 2, "text": "pot", "type": "stress"}, {"seq": 3, "text": "a"}, {"seq": 4, "text": "mus"}]'
        middle_val = json.loads(result)
        expected_result = json.dumps(middle_val)
        if sys.version_info[:2] <= (2, 7):
            self.assertItemsEqual(current_result, expected_result)
        else:
            self.assertCountEqual(current_result, expected_result)

    def test_hyphenation_not_valid_phrase(self):
        vb = ExVocabulary("tests/api_key.json")
        current_result = vb.hyphenation("sxsw")
        self.assertFalse(current_result)


if __name__ == "__main__":
    unittest.main()
