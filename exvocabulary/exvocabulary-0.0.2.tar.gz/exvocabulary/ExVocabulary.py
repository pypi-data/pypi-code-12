"""
The MIT License (MIT)

Copyright (c) 2016 Davis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import requests
import contextlib
import sys

__author__ = "Cheni Shang-Kuei"

"""
Copy most functionality from github project prodicus/vocabulary, and modify
and add some function
"""


@contextlib.contextmanager
def try_URL(message='Connection Lost'):
    try:
        yield
    except requests.exceptions.ConnectionError:
        sys.stdout.write(message)


class ExVocabulary(object):
    """
    Use web api to retrive definition of phrase and return as JSON data or data
    structure
    """
    """
    | Private variable | Private mathod       | Public Method        |
    |------------------+----------------------+----------------------|
    | __api_key        | __load_api_link()    | hyphenation()        |
    |                  | __get_api_link()     | usage_example()      |
    |                  | __return_json()      | vocabulary_example() |
    |                  | __return_structure() | part_of_speech()     |
    |                  |                      | synonym()            |
    |                  |                      | antonym()            |
    |                  |                      | phrase_definition()  |
    |                  |                      |                      |
    |------------------+----------------------+----------------------|
    """
    def __init__(self):
        pass

    def __get_api_link(self, api):
        """
        Returns API links

        Args:
            api: Possible values are "wordnik", "urbandict", "bighugelabs",
            "vocabulary"

        Returns:
            Returns API links to urbandictionary, wordnik, glosbe, bighugelabs,
            vocabulary
        """
        api_request_links = {
            "example":
            "http://api.wordnik.com:80/v4/word.json/{word}/examples?limit={limit}&includeDuplicates=false&useCanonical=true&skip=0&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5",
            "definition":
            "http://api.wordnik.com:80/v4/word.json/{word}/definitions?limit={limit}&includeRelated=true&sourceDictionaries=all&useCanonical=true&includeTags=false&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5",
            "related":
            "http://api.wordnik.com:80/v4/word.json/{word}/relatedWords?limitPerRelationshipType={limit}&useCanonical=false&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5",
            "hyphenation":
            "http://api.wordnik.com:80/v4/word.json/{word}/hyphenation?limit={limit}&useCanonical=false&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5",
            "vocabulary":
            "https://corpus.vocabulary.com/api/1.0/examples.json?query={word}&maxResults={max_num}&startOffset=0&filter=0",
        }

        if api in api_request_links.keys():
            return api_request_links[api]
        else:
            return False

    def __return_json(self, url):
        """
        Returns JSON data which is returned by querying the API service

        Args:
            url: The complete formatted url which is then queried using requests

        Returns:
            JSON data be fed by the API, if API send error signal then return
            dict that contains error as key, else return False
        """
        with try_URL():
            response = requests.get(url)
            if response.status_code == 200:
                json_obj = response.json()
                return json_obj
            else:
                return {"error": response.status_code}

    def __return_structure(self, json_str):
        """
        Returns structure insead of JSON data

        Args:
            json_str: JSON data to be parsed structure

        Returns:
            Returns the structure of JSON data if not a JSON data then returns
            data
        """
        try:
            return json.loads(json_str)
        except:
            return json_str

    def hyphenation(self, phrase):
        """
        Returns back the stress points in the "phrase" passed

        Args:
            phrase: Word for which hyphenation is to be found

        Returns:
            Returns a JSON object as string, False if invalid phrase
        """
        url = self.__get_api_link("hyphenation").format(word=phrase, action="hyphenation", limit="10")
        hyphenation = {}
        json_obj = self.__return_json(url)
        if isinstance(json_obj, list):
            if len(json_obj) == 0:
                return False
            return json.dumps(json_obj)
        elif isinstance(json_obj, dict):
            if "error" in json_obj:
                return False

    def usage_example(self, phrase):
        """
        Takes the source phrase and queries it to the urbandictionary API

        Args:
            phrase: Word for which usage_example is to be found

        Returns:
            Returns a JSON object as string, False if invalid phrase



            corpus": "New York Times", "seq": 0, "sentence"
        """
        url = self.__get_api_link("example").format(word=phrase, limit="10")
        word_examples = []
        json_obj = self.__return_json(url)
        if isinstance(json_obj, dict):
            for index, content in enumerate(json_obj["examples"]):
                example = {}
                example["corpus"] = content["provider"]["name"]
                example["seq"] = index
                example["sentence"] = content["text"].replace("\r", "").replace("\n", "")
                word_examples.append(example)
            return json.dumps(word_examples)
        else:
            return False

    def vocabulary_example(self, phrase, max_results=3):
        """
        Queries the vocabulary.com API for exta examples.

        Args:
            phrase: Word for which example is to be found

        Returns:
            Returns a JSON data if no example exist then returns False
        """
        # api url for vocabulary.com to request sentence example
        url = self.__get_api_link("vocabulary").format(word=phrase,
                                                       max_num=max_results)
        page = requests.get(url).text
        json_obj = json.loads(page)
        try:
            # get wanted result from json structure
            sentences = []
            for i in range(max_results):
                sentence = {}
                sentence["seq"] = i
                sentence["corpus"] = json_obj["result"]["sentences"][i][
                    "volume"]["corpus"]["name"]
                sentence["sentence"] = json_obj["result"]["sentences"][i][
                    "sentence"]

                sentences.append(sentence)
            return json.dumps(sentences)
        except:
            return False

    def part_of_speech(self, phrase):
        """
        Querrying Wordnik's API for knowing whether the word is a noun,
        adjective and the like

        Args:
            phrase: Word for which part_of_speech is to be found

        Returns:
            Returns a JSON object as string, False if invalid phrase
        """
        url = self.__get_api_link("definition").format(word=phrase, limit="10")
        json_obj = self.__return_json(url)

        final_list = []
        if isinstance(json_obj, list):
            part_of_speech = {}
            for content in json_obj:
                key = content["partOfSpeech"]
                value = content["text"]
                part_of_speech[key] = value
                if part_of_speech:
                    index = 0
                    for key, value in part_of_speech.items():
                        final_list.append({"seq": index,
                                           "text": key,
                                           "example:": value})
                        index += 1
                    return json.dumps(final_list)
                    # return final_list
        elif isinstance(json_obj, dict):
            if "error" in json_obj:
                return False

    def synonym(self, phrase):
        """
        Queries the bighugelabs API for the synonym. The results include
         - "syn" (synonym)
         - "ant" (antonym)
         - "rel" (related terms)
         - "sim" (similar terms)
         - "usr" (user suggestions)

        Args:
            phrase: Word for which synonym is to be found

        Returns:
            returns a JSON object, if no antonyms are found then return False
        """
        url = self.__get_api_link("related").format(word=phrase, limit="10")
        json_obj = self.__return_json(url)
        if isinstance(json_obj, dict):
            if error in json_obj:
                return False
        elif isinstance(json_obj, list):
            for content in json_obj:
                key = content["relationshipType"]
                value = content["words"]

                related = {}
                if key != "synonym":
                    continue
                else:
                    related["synonym"] = value

                if len(related) == 0:
                    return False
                else:
                    return json.dumps(related)

    def antonym(self, phrase):
        """
        Queries the bighugelabs API for the synonym. The results include
         - "syn" (synonym)
         - "ant" (antonym)
         - "rel" (related terms)
         - "sim" (similar terms)
         - "usr" (user suggestions)

        Args:
            phrase: Word for which synonym is to be found

        Returns:
            returns a JSON object, if no antonyms are found then return False
        """
        url = self.__get_api_link("related").format(word=phrase, limit="10")
        json_obj = self.__return_json(url)
        if isinstance(json_obj, dict):
            if error in json_obj:
                return False
        elif isinstance(json_obj, list):
            for content in json_obj:
                key = content["relationshipType"]
                value = content["words"]

                related = {}
                if key != "antonym":
                    continue
                else:
                    related["antonym"] = value

                if len(related) == 0:
                    return False
                else:
                    return json.dumps(related)

    def phrase_definition(self, phrase):
        """
        Returns the information that one phrase should prossible contended.

        Args:
            phrase: Word for which example is to be found

        Returns:
            Returns a dict which contends word information like, hyphenation,
            part_of_speech, synonym, antonym, example
        """
        definition = {}
        definition["phrase"] = phrase

        hyphenation = self.__return_structure(self.hyphenation(phrase))
        if hyphenation:
            definition["hyphenation"] = hyphenation
        else:
            definition["hyphenation"] = False
        part_of_speech = self.__return_structure(self.part_of_speech(phrase))
        if part_of_speech:
            definition["part_of_speech"] = part_of_speech
        else:
            definition["part_of_speech"] = False
        synonym = self.__return_structure(self.synonym(phrase))
        if synonym:
            definition["synonym"] = synonym
        else:
            definition["synonym"] = False
        antonym = self.__return_structure(self.antonym(phrase))
        if antonym:
            definition["antonym"] = antonym
        else:
            definition["antonym"] = False
        example = self.__return_structure(self.usage_example(phrase))
        if example:
            definition["example"] = example
        else:
            definition["example"] = False

        return definition
