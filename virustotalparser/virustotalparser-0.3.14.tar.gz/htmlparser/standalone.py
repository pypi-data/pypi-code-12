import json
import sys

from pathlib import Path

from .finder import Finder
from .parser import Parser


class JsonNotListError(Exception):
    pass


class IncorrectNumberOfArguments(Exception):
    pass


class Standalone:
    def __init__(self, html_path, json_path=None):
        self.parser = Parser()
        self.html_path = html_path
        self.json_path = json_path

    def parse_and_find(self):
        element_list = self.parser.parse(self.read_html())
        finder = Finder(element_list)
        if self.json_path is None:
            elements_found = finder.find_first_page_attributes()
        else:
            elements_found = finder.find_attributes_from_list(self.read_json())
        return elements_found

    def read_html(self):
        with self.html_path.open() as html_file:
            html_string = html_file.read()
        return html_string

    def read_json(self):
        with self.json_path.open() as json_file:
            json_string = json_file.read()
        json_list = json.loads(json_string)
        if isinstance(json_list, list):
            return json_list
        else:
            raise JsonNotListError

    def print_results(self, elements_found):
        results_path = self.html_path.parent / 'result.json'
        result_string = json.dumps(elements_found, indent=4)
        with results_path.open('w+') as results_file:
            results_file.write(result_string)
        print(result_string)


def init_standalone(args):
    if len(args) == 2:
        html_path = Path(args[0])
        json_path = Path(args[1])
        return Standalone(html_path, json_path)
    elif len(args) == 1:
        html_path = Path(args[0])
        return Standalone(html_path)
    else:
        raise IncorrectNumberOfArguments


def main(args):
    try:
        standalone = init_standalone(args)
        elements_found = standalone.parse_and_find()
        standalone.print_results(elements_found)
        return elements_found
    except FileNotFoundError as error:
        print(str(error))
    except ValueError as error:
        print("Bad json format.\n" + str(error))
    except JsonNotListError as error:
        print("Provided json doesn't represent list")
    except IncorrectNumberOfArguments as error:
        print ("Incorrect number of arguments, one or two shoud be provided.")


